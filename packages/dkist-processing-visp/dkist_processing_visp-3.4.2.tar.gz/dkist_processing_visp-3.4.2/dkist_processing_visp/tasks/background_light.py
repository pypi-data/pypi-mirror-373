"""ViSP background light calibration task."""

import gc
import time

import numpy as np
import scipy.optimize as spo
from astropy.io import fits
from dkist_processing_common.codecs.fits import fits_access_decoder
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_processing_math.arithmetic import subtract_array_from_arrays
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_processing_math.transform.binning import resize_arrays
from dkist_service_configuration.logging import logger

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.models.task_name import VispTaskName
from dkist_processing_visp.parsers.visp_l0_fits_access import VispL0FitsAccess
from dkist_processing_visp.tasks.mixin.beam_access import BeamAccessMixin
from dkist_processing_visp.tasks.mixin.corrections import CorrectionsMixin
from dkist_processing_visp.tasks.mixin.downsample import DownsampleMixin
from dkist_processing_visp.tasks.visp_base import VispTaskBase

__all__ = ["BackgroundLightCalibration"]


class BackgroundLightCalibration(
    VispTaskBase,
    BeamAccessMixin,
    DownsampleMixin,
    CorrectionsMixin,
    QualityMixin,
):
    """
    Task class for measuring additive background light that is not captured in the dark frames.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs

    """

    record_provenance = True

    def run(self) -> None:
        """
        Run the background light algorithm and save the results.

        For each beam:
            - Subtract the dark from all polcal frames
            - Compute the background light
            - Write the background light as an intermediate product
        """
        if not self.constants.correct_for_polarization:
            logger.info(
                "Background light calibration requires POLCAL frames and this is a Stokes-I dataset"
            )
            return

        if not self.parameters.background_on:
            logger.info("Background light correction is switched off")
            return

        self.check_exposure_times_match()

        num_bins = self.parameters.background_num_spatial_bins
        for beam in range(1, self.constants.num_beams + 1):

            logger.info(f"Dark-subtracting and spatially resampling raw polcals for {beam = }")
            full_num_wave, full_name_slit_pos, resampled_data = self.reduce_and_resample_polcals(
                beam=beam, num_bins=num_bins
            )

            self.write(
                data=resampled_data,
                encoder=fits_array_encoder,
                tags=[VispTag.debug(), VispTag.frame()],
                relative_path=f"DEBUG_BG_RESAMP_ARR_BEAM_{beam}.dat",
                overwrite=True,
            )

            logger.info(f"Computing background light for {beam = }")
            small_background_light = self.compute_background_light(resampled_data)

            self.write(
                data=small_background_light,
                encoder=fits_array_encoder,
                tags=[VispTag.debug(), VispTag.frame()],
                relative_path=f"DEBUG_BG_SMALL_ARR_BEAM_{beam}.dat",
                overwrite=True,
            )

            logger.info(f"Resampling background light to full-frame for {beam = }")
            full_background_light = self.upsample_background_light(
                small_background_light, full_shape=(full_num_wave, full_name_slit_pos)
            )

            self.write(
                data=full_background_light,
                tags=[VispTag.intermediate_frame(beam=beam), VispTag.task_background()],
                encoder=fits_array_encoder,
            )
            num_used_polcal_files = resampled_data.shape[0]

            # Note: This probably does nothing, but it *might* :shrug:
            del resampled_data
            del small_background_light
            del full_background_light
            gc.collect()

        with self.apm_processing_step("Computing and logging quality metrics"):
            self.quality_store_task_type_counts(
                task_type=VispTaskName.background.value,
                total_frames=num_used_polcal_files,
            )

    def check_exposure_times_match(self) -> None:
        """
        Make sure that the polcal exposure times are the same as solar gain and science exposure times.

        A fundamental assumption of the background algorithm is that the background light is additive and increases
        linearly with exp time (like a dark). We use polcal frames to compute the background light and thus if the exp
        time is not the same as the other tasks the derived correction will be incorrect.

        In the future we might scale the background light based on exposure time, but for now we'll just error if there's
        an issue.
        """
        if (
            len(
                set(
                    self.constants.polcal_exposure_times
                    + self.constants.solar_exposure_times
                    + self.constants.observe_exposure_times
                )
            )
            != 1
        ):
            raise ValueError(
                "Polcal, solar_gain, and observe frames do not all have the same FPA exposure time. Background light correction is not possible."
            )

        if len(self.constants.polcal_exposure_times) > 1:
            raise ValueError(
                f"Only a single polcal time is currently supported. Found {self.constants.polcal_exposure_times}"
            )

    def reduce_and_resample_polcals(self, beam: int, num_bins: int) -> tuple[int, int, np.ndarray]:
        """
        Remove dark signal from all polcal frames, resample their spatial dimension, and collect them in a big array stack.

        Polcal dark frames are ignored.

        Parameters
        ----------
        beam
            The ViSP beam to operate on

        num_bins
            The number of spatial bins to resample each array into

        Returns
        -------
        An ndarray of shape ((N - D) * M, x, y'), where N is the total number of Calibration Sequence steps, D is the
        number of dark CS steps, and M is the number of modulator states.
        """
        ## A note on resampling
        #
        # We don't resample the wavelength dimension right now because the full, unsampled wavelength range is crucial
        # to the goodness-of-fit parameter. Basically, the spatial dimension can be resampled prior to fitting because
        # the spatial pixels are completely independent. The wavelength pixels are not, though, and therefor the full
        # set of data along the wavelength axis is required at the time of fitting. The wavelength subsample factor
        # *only* reduces the number of fit variables.

        # Have to build this up dynamically because we don't want to hardcode the number of dark steps
        array_list = []
        logger.info(f"Using median filtering to resample spatial dimension to {num_bins} bins")

        for modstate in range(1, self.constants.num_modstates + 1):
            for cs_step in range(self.constants.num_cs_steps):
                cs_step_tags = [
                    VispTag.input(),
                    VispTag.frame(),
                    VispTag.task_polcal(),
                    VispTag.modstate(modstate),
                    VispTag.cs_step(cs_step),
                ]
                pol_cal_objs = list(
                    self.read(
                        tags=cs_step_tags,
                        decoder=fits_access_decoder,
                        fits_access_class=VispL0FitsAccess,
                    )
                )
                if pol_cal_objs[0].gos_level0_status == "DarkShutter":
                    logger.info(f"Skipping dark step {modstate = } and {cs_step = }")
                    continue

                logger.info(f"working on {modstate = } and {cs_step = }")
                all_readout_frames = []
                for readout_exp_time in self.constants.polcal_readout_exp_times:
                    dark_array = next(
                        self.read(
                            tags=VispTag.intermediate_frame_dark(
                                beam=beam, readout_exp_time=readout_exp_time
                            ),
                            decoder=fits_array_decoder,
                        )
                    )
                    num_wave, num_slit_pos = dark_array.shape

                    tags = cs_step_tags + [VispTag.readout_exp_time(readout_exp_time)]
                    pol_cal_objs = list(
                        self.read(
                            tags=tags,
                            decoder=fits_access_decoder,
                            fits_access_class=VispL0FitsAccess,
                        )
                    )

                    readout_normalized_arrays = [
                        self.beam_access_get_beam(obj.data, beam=beam) / obj.num_raw_frames_per_fpa
                        for obj in pol_cal_objs
                    ]
                    input_data = average_numpy_arrays(readout_normalized_arrays)
                    dark_subtracted_array = next(subtract_array_from_arrays(input_data, dark_array))
                    all_readout_frames.append(dark_subtracted_array)

                avg_readout_frames = average_numpy_arrays(all_readout_frames)

                resampled_array = self.downsample_spatial_dimension_local_median(
                    avg_readout_frames,
                    num_spatial_bins=self.parameters.background_num_spatial_bins,
                )

                array_list.append(resampled_array)

        output_array = np.stack(array_list)
        logger.info(
            f"Processed {len(array_list) // self.constants.num_modstates} CS steps with {self.constants.num_modstates} modstates."
        )
        return num_wave, num_slit_pos, output_array

    def compute_background_light(self, input_data: np.ndarray) -> np.ndarray:
        """
        Compute a full-frame background light image.

        For each spatial position in the (potentially) sub-sampled array a fit is performed to compute the background
        light at that pixel. These are then collected and re-sampled to the full frame size.

        Parameters
        ----------
        input_data
            An array with shape ((N - D) * M, x, y') (see `reduce_and_resample_polcals`) representing the stack of all
            polcal arrays.

        Returns
        -------
        Array of shape (x, y') containing the computed background light
        """
        num_arr, num_wave, num_bins = input_data.shape
        background_light = np.zeros((num_wave, num_bins), dtype=np.float64)

        continuum_idx = self.parameters.background_continuum_index
        t1 = time.time()
        for i in range(num_bins):
            logger.info(f"Fitting background light for bin {i + 1} of {num_bins}")
            single_pos_spectra = input_data[:, :, i]
            abscissa, init_guess, bounds = self.setup_fit(single_pos_spectra, continuum_idx)
            single_pos_background_light = self.fit_single_pos_background_light(
                single_pos_spectra, abscissa, init_guess, bounds, continuum_idx
            )
            background_light[:, i] = np.interp(
                np.arange(num_wave), abscissa, single_pos_background_light
            )

        logger.info(f"Full binned frame took {(time.time() - t1)/60.:.3f} minutes")
        return background_light

    @staticmethod
    def upsample_background_light(small_data: np.ndarray, full_shape: tuple) -> np.ndarray:
        """Resample a background light array to the full ViSP frame."""
        return next(resize_arrays(small_data, output_shape=full_shape, order=1))

    def setup_fit(
        self, spectra_stack: np.ndarray, continuum_idx: list[int]
    ) -> tuple[np.ndarray, np.ndarray, spo.Bounds]:
        """
        Subsample the wavelength axis, construct and initial guess, and define parameter bounds.

        Parameters
        ----------
        spectra_stack
            All polcal CS steps and modstates for a single spatial sample

        continuum_idx
            List of wavelength pixels to use when computing the normalization factor
        """
        min_spectrum = np.min(spectra_stack, axis=0)
        subsample_factor = self.parameters.background_wavelength_subsample_factor

        # Make the abscissa by subsampling arange
        x = np.arange(spectra_stack.shape[1])[::subsample_factor]

        # Make the initial guess
        ########################
        # Compute the normalization factors
        norms = np.mean(spectra_stack[:, continuum_idx], axis=1)

        # Normalize each spectrum
        normed_spec = spectra_stack / norms[:, None]

        # The initial guess has the shape of the stddev of the normalized spectra
        #  also subsample here
        init_guess = np.std(normed_spec, axis=0)[::subsample_factor]
        # Now convert that shape into the correct units (counts) by multiplying by a count value less
        #  than the minimum record spectrum
        init_guess *= np.mean(min_spectrum) / 2.0

        # Set bounds. The background light CANT'T be larger than the minimum recorded spectrum
        bounds = spo.Bounds(lb=0.0, ub=np.max(min_spectrum))

        logger.info(f"Sub-sampling wavelength axis by {subsample_factor} to {x.size} total samples")

        return x, init_guess, bounds

    def fit_single_pos_background_light(
        self,
        spectra_stack: np.ndarray,
        abscissa,
        init_guess: np.ndarray,
        bounds: spo.Bounds,
        continuum_idx: list,
    ) -> np.ndarray:
        """Run a fit to background light on a set of spectra from a single spatial position.

        The fit minimizes the standard deviation (over wavelength) of continuum-normalized CS steps, each of which are
        heavily modulated by the GOS optics.
        """
        fits.PrimaryHDU(init_guess).writeto("init_guess.dat", overwrite=True)

        t1 = time.time()
        res = spo.minimize(
            self.fitness_func,
            init_guess,
            method="SLSQP",
            bounds=bounds,
            args=(spectra_stack, abscissa, continuum_idx),
            # ftol is made very small so that the practical limit on the fit is the maxiter
            #  we find that this is a suitable way to constrain runtime in this specific fitting case
            options={"ftol": 1e-10, "maxiter": self.parameters.background_num_fit_iterations},
        )
        logger.info(
            f"Fit completed in {time.time() - t1:.2f} seconds with {res.nfev} evaluations for {res.nit} iterations"
        )

        background_light = res.x

        return background_light

    @staticmethod
    def fitness_func(
        background_light: np.ndarray, spectra: np.ndarray, abscissa: np.ndarray, continuum_idx: list
    ) -> np.ndarray:
        """Compute the standard deviation between normalized spectra of all modstates over all CS steps.

        The idea here is that modulation is a purely *multiplicative* operation and so normalizing all spectra by their
        continuum values should produce essentially identical spectra (i.e., low standard deviation). The presence of
        unaccounted for background light (which is additive) will make the spectra different and thus increase the
        standard deviation.
        """
        full_sl = np.interp(np.arange(spectra.shape[1]), abscissa, background_light)
        sl_corr_spectra = spectra - full_sl[None, :]
        normalizer_flux = np.mean(spectra[:, continuum_idx], axis=1)
        normed_spec = sl_corr_spectra / normalizer_flux[:, None]
        std = np.nanstd(normed_spec, axis=0)

        return np.nansum(std**2)
