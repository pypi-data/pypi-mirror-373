"""ViSP solar calibration task. See :doc:`this page </gain_correction>` for more information."""

import numpy as np
import scipy.ndimage as spnd
import scipy.optimize as spo
from dkist_processing_common.codecs.fits import fits_access_decoder
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_processing_math.arithmetic import divide_arrays_by_array
from dkist_processing_math.arithmetic import subtract_array_from_arrays
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_service_configuration.logging import logger

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.parsers.visp_l0_fits_access import VispL0FitsAccess
from dkist_processing_visp.tasks.mixin.beam_access import BeamAccessMixin
from dkist_processing_visp.tasks.mixin.corrections import CorrectionsMixin
from dkist_processing_visp.tasks.mixin.line_zones import LineZonesMixin
from dkist_processing_visp.tasks.visp_base import VispTaskBase

__all__ = ["SolarCalibration"]


class SolarCalibration(
    VispTaskBase,
    BeamAccessMixin,
    CorrectionsMixin,
    QualityMixin,
    LineZonesMixin,
):
    """
    Task class for generating Solar Gain images for each beam/modstate.

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
        For each beam.

            For each modstate:
                - Do dark, background, lamp, and geometric corrections
                - Compute the characteristic spectra
                - Re-apply the spectral curvature to the characteristic spectra
                - Re-apply angle and state offset distortions to the characteristic spectra
                - Remove the distorted characteristic solar spectra from the original spectra
                - Write master solar gain

        Returns
        -------
        None

        """
        for beam in range(1, self.constants.num_beams + 1):

            pre_equalized_gain_dict = dict()

            for modstate in range(1, self.constants.num_modstates + 1):
                apm_str = f"{beam = } and {modstate = }"
                with self.apm_processing_step(f"Initial corrections for {apm_str}"):
                    self.do_initial_corrections(beam=beam, modstate=modstate)

                with self.apm_processing_step(f"Computing characteristic spectra for {apm_str}"):
                    char_spec = self.compute_characteristic_spectra(beam=beam, modstate=modstate)
                    self.write(
                        data=char_spec,
                        encoder=fits_array_encoder,
                        tags=[VispTag.debug(), VispTag.frame()],
                        relative_path=f"DEBUG_SC_CHAR_SPEC_BEAM_{beam}_MODSTATE_{modstate}.dat",
                        overwrite=True,
                    )

                with self.apm_processing_step(
                    f"Re-distorting characteristic spectra for {apm_str}"
                ):
                    spec_shift = next(
                        self.read(
                            tags=[
                                VispTag.intermediate_frame(beam=beam),
                                VispTag.task_geometric_spectral_shifts(),
                            ],
                            decoder=fits_array_decoder,
                        )
                    )
                    redistorted_char_spec = next(
                        self.corrections_remove_spec_geometry(
                            arrays=char_spec, spec_shift=-1 * spec_shift
                        )
                    )
                    self.write(
                        data=redistorted_char_spec,
                        encoder=fits_array_encoder,
                        tags=[VispTag.debug(), VispTag.frame()],
                        relative_path=f"DEBUG_SC_CHAR_DISTORT_BEAM_{beam}_MODSTATE_{modstate}.dat",
                        overwrite=True,
                    )

                with self.apm_processing_step(f"Re-shifting characteristic spectra for {apm_str}"):
                    reshifted_char_spec = self.distort_characteristic_spectra(
                        char_spec=redistorted_char_spec, beam=beam, modstate=modstate
                    )
                    self.write(
                        data=reshifted_char_spec,
                        encoder=fits_array_encoder,
                        tags=[
                            VispTag.beam(beam),
                            VispTag.modstate(modstate),
                            VispTag.task("CHAR_SPEC_DISTORT_SHIFT"),
                        ],
                        relative_path=f"DEBUG_SC_CHAR_SPEC_DISTORT_SHIFT_BEAM_{beam}_MODSTATE_{modstate}.dat",
                        overwrite=True,
                    )

                with self.apm_processing_step(
                    f"Refining characteristic spectral shifts for {apm_str}"
                ):
                    refined_char_spec = self.refine_gain_shifts(
                        char_spec=reshifted_char_spec, beam=beam, modstate=modstate
                    )
                    self.write(
                        data=refined_char_spec,
                        encoder=fits_array_encoder,
                        tags=[VispTag.debug(), VispTag.frame()],
                        relative_path=f"DEBUG_SC_CHAR_SPEC_REFINE_BEAM_{beam}_MODSTATE_{modstate}.dat",
                        overwrite=True,
                    )

                with self.apm_processing_step(f"Removing solar signal from {apm_str}"):
                    gain = self.remove_solar_signal(
                        char_solar_spectra=refined_char_spec, beam=beam, modstate=modstate
                    )

                with self.apm_processing_step(f"Masking hairlines from {apm_str}"):
                    gain = self.corrections_mask_hairlines(gain)

                self.write(
                    data=gain,
                    encoder=fits_array_encoder,
                    tags=[
                        VispTag.debug(),
                        VispTag.frame(),
                    ],
                    relative_path=f"DEBUG_SC_PRE_EQ_SOLAR_GAIN_BEAM_{beam}_MODSTATE_{modstate}.dat",
                    overwrite=True,
                )

                pre_equalized_gain_dict[modstate] = gain

            with self.apm_processing_step(f"Equalizing modstates for {beam = }"):
                equalized_gain_dict = self.equalize_modstates(pre_equalized_gain_dict)

            for modstate in range(1, self.constants.num_modstates + 1):

                final_gain = equalized_gain_dict[modstate]

                with self.apm_writing_step(f"Writing solar gain for {beam = } and {modstate = }"):
                    self.write_solar_gain_calibration(
                        gain_array=final_gain, beam=beam, modstate=modstate
                    )

        with self.apm_processing_step("Computing and logging quality metrics"):
            no_of_raw_solar_frames: int = self.scratch.count_all(
                tags=[
                    VispTag.input(),
                    VispTag.frame(),
                    VispTag.task_solar_gain(),
                ],
            )

            self.quality_store_task_type_counts(
                task_type=TaskName.solar_gain.value, total_frames=no_of_raw_solar_frames
            )

    def unshifted_geo_corrected_modstate_data(self, beam: int, modstate: int) -> np.ndarray:
        """
        Array for a single beam/modstate that has dark, lamp, angle, and state offset corrections.

        Parameters
        ----------
        beam : int
            The beam number for this array

        modstate : int
            The modulator state for this array


        Returns
        -------
        np.ndarray
            Array with dark signal, lamp signal, angle and state offset removed

        """
        tags = [
            VispTag.intermediate_frame(beam=beam, modstate=modstate),
            VispTag.task("SC_GEO_NOSHIFT"),
        ]
        array_generator = self.read(tags=tags, decoder=fits_array_decoder)
        return next(array_generator)

    def geo_corrected_modstate_data(self, beam: int, modstate: int) -> np.ndarray:
        """
        Array for a single beam/modstate that has dark, lamp, and ALL of the geometric corrects.

        Parameters
        ----------
        beam : int
            The beam number for this array

        modstate : int
            The modulator state for this array


        Returns
        -------
        np.ndarray
            Array with dark signal, and lamp signal removed, and all geometric corrections made
        """
        tags = [
            VispTag.intermediate_frame(beam=beam, modstate=modstate),
            VispTag.task("SC_GEO_ALL"),
        ]
        array_generator = self.read(tags=tags, decoder=fits_array_decoder)
        return next(array_generator)

    def lamp_corrected_modstate_data(self, beam: int, modstate: int) -> np.ndarray:
        """
        Array for a single beam/modstate that has dark, background, and lamp gain applied.

        This is used to refine the final shifts in the re-distorted characteristic spectra. Having the lamp gain applied
        removes large optical features that would otherwise pollute the match to the characteristic spectra (which has
        no optical features).
        """
        tags = [
            VispTag.intermediate_frame(beam=beam, modstate=modstate),
            VispTag.task("SC_LAMP_CORR"),
        ]
        array_generator = self.read(tags=tags, decoder=fits_array_decoder)
        return next(array_generator)

    def bg_corrected_modstate_data(self, beam: int, modstate: int) -> np.ndarray:
        """
        Array for a single beam/modstate that has only has dark and background corrects applied.

        Parameters
        ----------
        beam : int
            The beam number for this array

        modstate : int
            The modulator state for this array


        Returns
        -------
        np.ndarray
            Array with dark and background signals removed
        """
        tags = [
            VispTag.intermediate_frame(beam=beam, modstate=modstate),
            VispTag.task("SC_BG_ONLY"),
        ]
        array_generator = self.read(tags=tags, decoder=fits_array_decoder)
        return next(array_generator)

    def do_initial_corrections(self, beam: int, modstate: int) -> None:
        """
        Do dark, lamp, and geometric corrections for all data that will be used.

        At two intermediate points the current arrays are saved because they'll be needed by various helpers:

        SC_BG_ONLY - The solar gain arrays with only a dark and background correction.

        SC_GEO_NOSHIFT - The solar gain arrays after dark, lamp, angle, and state offset correction. In other words,
                         they do not have spectral curvature removed. These are used to reshift the characteristic
                         spectra to the original spectral curvature.

        Parameters
        ----------
        beam : int
            The beam number for this array

        modstate : int
            The modulator state for this array


        Returns
        -------
        None
        """
        for readout_exp_time in self.constants.solar_readout_exp_times:
            dark_array = next(
                self.read(
                    tags=VispTag.intermediate_frame_dark(
                        beam=beam, readout_exp_time=readout_exp_time
                    ),
                    decoder=fits_array_decoder,
                )
            )

            background_array = np.zeros(dark_array.shape)
            if self.constants.correct_for_polarization and self.parameters.background_on:
                background_array = next(
                    self.read(
                        tags=[VispTag.intermediate_frame(beam=beam), VispTag.task_background()],
                        decoder=fits_array_decoder,
                    )
                )

            logger.info(
                f"Doing dark, background, lamp, and geo corrections for {beam=} and {modstate=}"
            )
            ## Load frames
            tags = [
                VispTag.input(),
                VispTag.frame(),
                VispTag.task_solar_gain(),
                VispTag.modstate(modstate),
                VispTag.readout_exp_time(readout_exp_time),
            ]
            input_solar_gain_objs = self.read(
                tags=tags, decoder=fits_access_decoder, fits_access_class=VispL0FitsAccess
            )

            readout_normalized_arrays = (
                self.beam_access_get_beam(o.data, beam=beam) / o.num_raw_frames_per_fpa
                for o in input_solar_gain_objs
            )

            ## Average
            avg_solar_array = average_numpy_arrays(readout_normalized_arrays)

            ## Dark correction
            dark_corrected_solar_array = subtract_array_from_arrays(
                arrays=avg_solar_array, array_to_subtract=dark_array
            )

            ## Residual background correction
            background_corrected_solar_array = next(
                subtract_array_from_arrays(dark_corrected_solar_array, background_array)
            )

            # Save the only-dark-corr because this will be used to make the final Solar Gain object
            self.write(
                data=background_corrected_solar_array,
                tags=[
                    VispTag.intermediate_frame(beam=beam, modstate=modstate),
                    VispTag.task("SC_BG_ONLY"),
                ],
                encoder=fits_array_encoder,
            )

            ## Lamp correction
            lamp_array = next(
                self.read(
                    tags=[
                        VispTag.intermediate_frame(beam=beam, modstate=modstate),
                        VispTag.task_lamp_gain(),
                    ],
                    decoder=fits_array_decoder,
                )
            )
            lamp_corrected_solar_array = next(
                divide_arrays_by_array(
                    arrays=background_corrected_solar_array, array_to_divide_by=lamp_array
                )
            )

            self.write(
                data=lamp_corrected_solar_array,
                tags=[
                    VispTag.intermediate_frame(beam=beam, modstate=modstate),
                    VispTag.task("SC_LAMP_CORR"),
                ],
                encoder=fits_array_encoder,
            )

            ## Geo correction
            angle_array = next(
                self.read(
                    tags=[VispTag.intermediate_frame(beam=beam), VispTag.task_geometric_angle()],
                    decoder=fits_array_decoder,
                )
            )
            angle = angle_array[0]
            state_offset = next(
                self.read(
                    tags=[
                        VispTag.intermediate_frame(beam=beam, modstate=modstate),
                        VispTag.task_geometric_offset(),
                    ],
                    decoder=fits_array_decoder,
                )
            )
            spec_shift = next(
                self.read(
                    tags=[
                        VispTag.intermediate_frame(beam=beam),
                        VispTag.task_geometric_spectral_shifts(),
                    ],
                    decoder=fits_array_decoder,
                )
            )

            geo_corrected_array = next(
                self.corrections_correct_geometry(lamp_corrected_solar_array, state_offset, angle)
            )
            # We need unshifted, but geo-corrected arrays for reshifting and normalization
            self.write(
                data=geo_corrected_array,
                tags=[
                    VispTag.intermediate_frame(beam=beam, modstate=modstate),
                    VispTag.task("SC_GEO_NOSHIFT"),
                ],
                encoder=fits_array_encoder,
            )

            # Now finish the spectral shift correction
            spectral_corrected_array = next(
                self.corrections_remove_spec_geometry(geo_corrected_array, spec_shift)
            )
            self.write(
                data=spectral_corrected_array,
                tags=[
                    VispTag.intermediate_frame(beam=beam, modstate=modstate),
                    VispTag.task("SC_GEO_ALL"),
                ],
                encoder=fits_array_encoder,
            )

    def compute_characteristic_spectra(self, beam: int, modstate: int) -> np.ndarray:
        """
        Compute the 2D characteristic spectra via a Gaussian smooth in the spatial dimension.

        A 2D characteristic spectra is needed because the line shape varys along the slit to the degree that a
        single, 1D characteristic spectrum will not fully remove the solar lines for all positions in the final gain.

        In this step we also normalize each spatial position to its median value. This removes low-order gradients in
        the spatial direction that are known to be caused by imperfect illumination of the Lamp gains (which were used
        to correct the data that will become the characteristic spectra).

        Parameters
        ----------
        beam : int
            The beam number for this array

        modstate : int
            The modulator state for this array


        Returns
        -------
        np.ndarray
            Characteristic spectra array
        """
        spectral_avg_window = self.parameters.solar_spectral_avg_window
        normalization_percentile = (
            self.parameters.solar_characteristic_spatial_normalization_percentile
        )
        logger.info(
            f"Computing characteristic spectra for {beam = } and {modstate = } with {spectral_avg_window = } and {normalization_percentile = }"
        )
        full_spectra = self.geo_corrected_modstate_data(beam=beam, modstate=modstate)

        full_spectra = self.corrections_mask_hairlines(full_spectra)
        # Normalize each spatial pixel by its own percentile. This removes large spatial gradients that are not solar
        # signal.
        normed_spectra = full_spectra / np.nanpercentile(
            full_spectra, normalization_percentile, axis=0
        )

        # size = (1, window) means don't smooth in the spectra dimension
        char_spec = spnd.median_filter(normed_spectra, size=(1, spectral_avg_window))

        return char_spec

    def refine_gain_shifts(self, char_spec: np.ndarray, beam: int, modstate: int) -> np.ndarray:
        """
        Refine the spectral shifts when matching characteristic spectra to the rectified input spectra.

        An important detail of this functino is that the goodness of fit metric is the final gain image (i.e., raw
        input with solar spectrum removed). We minimize the residuals in the gain image.

        Parameters
        ----------
        char_spec : np.ndarray
            Computed characteristic spectra

        beam : int
            The beam number for this array

        modstate : int
            The modulator state for this array


        Returns
        -------
        np.ndarray
            Characteristic spectra array with refined spectral shifts
        """
        # Grab rectified input spectra that will be the shift target
        target_spectra = self.lamp_corrected_modstate_data(beam=beam, modstate=modstate)
        num_spec = target_spectra.shape[1]

        logger.info(f"Computing line zones for {beam=} and {modstate=}")
        zone_kwargs = {
            "prominence": self.parameters.solar_zone_prominence,
            "width": self.parameters.solar_zone_width,
            "bg_order": self.parameters.solar_zone_bg_order,
            "normalization_percentile": self.parameters.solar_zone_normalization_percentile,
            "rel_height": self.parameters.solar_zone_rel_height,
        }
        zones = self.compute_line_zones(char_spec, **zone_kwargs)
        logger.info(f"Found {zones=} for {beam=} and {modstate=}")
        if len(zones) == 0:
            raise ValueError(f"No zones found for {beam=} and {modstate=}")

        reshift_char_spec = np.zeros(char_spec.shape)
        logger.info(f"Refining shifts for {beam=} and {modstate=}")
        for i in range(num_spec):
            ref_spec = target_spectra[:, i] / np.nanmedian(target_spectra[:, i])
            spec = char_spec[:, i] / np.nanmedian(char_spec[:, i])
            shift = SolarCalibration.refine_shift(spec, ref_spec, zones=zones, x_init=0.0)
            reshift_char_spec[:, i] = spnd.shift(char_spec[:, i], shift, mode="reflect")

        return reshift_char_spec

    def distort_characteristic_spectra(
        self, char_spec: np.ndarray, beam: int, modstate: int
    ) -> np.ndarray:
        """
        Re-apply angle and state offset distortions to the characteristic spectra.

        Parameters
        ----------
        char_spec : np.ndarray
            Computed characteristic spectra

        beam : int
            The beam number for this array

        modstate : int
            The modulator state for this array


        Returns
        -------
        np.ndarray
            Characteristic spectra array with angle and offset distortions re-applied
        """
        logger.info(f"Re-distorting characteristic spectra for {beam=} and {modstate=}")
        angle_array = next(
            self.read(
                tags=[VispTag.intermediate_frame(beam=beam), VispTag.task_geometric_angle()],
                decoder=fits_array_decoder,
            )
        )
        angle = angle_array[0]
        state_offset = next(
            self.read(
                tags=[
                    VispTag.intermediate_frame(beam=beam, modstate=modstate),
                    VispTag.task_geometric_offset(),
                ],
                decoder=fits_array_decoder,
            )
        )

        distorted_spec = next(
            self.corrections_correct_geometry(char_spec, -1 * state_offset, -1 * angle)
        )

        return distorted_spec

    def equalize_modstates(self, array_dict: dict[int, np.ndarray]) -> dict[int, np.ndarray]:
        """Adjust the flux of all modstates for a single beam so they all have the same median.

        That median is the global median over all modstates.
        """
        global_median_array = np.nanmedian(list(array_dict.values()), axis=0)
        output_dict = dict()

        for modstate, array in array_dict.items():
            correction = np.nanmedian(global_median_array / array)
            logger.info(f"Equalization correction for {modstate = } is {correction:.6f}")
            final_gain = array * correction
            output_dict[modstate] = final_gain

        return output_dict

    def remove_solar_signal(
        self, char_solar_spectra: np.ndarray, beam: int, modstate: int
    ) -> np.ndarray:
        """
        Remove the distorted characteristic solar spectra from the original spectra.

        Parameters
        ----------
        char_solar_spectra : np.ndarray
            Characteristic solar spectra

        beam : int
            The beam number for this array

        modstate : int
            The modulator state for this array


        Returns
        -------
        np.ndarray
            Original spectral array with characteristic solar spectra removed

        """
        logger.info(f"Removing characteristic solar spectra from {beam=} and {modstate=}")
        input_gain = self.bg_corrected_modstate_data(beam=beam, modstate=modstate)

        final_gain = input_gain / char_solar_spectra

        return final_gain

    def write_solar_gain_calibration(
        self, gain_array: np.ndarray, beam: int, modstate: int
    ) -> None:
        """
        Write a solar gain array for a single beam and modstate.

        Parameters
        ----------
        gain_array: np.ndarray
            Solar gain array

        beam : int
            The beam number for this array

        modstate : int
            The modulator state for this array


        Returns
        -------
        None
        """
        logger.info(f"Writing final SolarGain for {beam=} and {modstate=}")
        self.write(
            data=gain_array,
            tags=[
                VispTag.intermediate_frame(beam=beam, modstate=modstate),
                VispTag.task_solar_gain(),
            ],
            encoder=fits_array_encoder,
        )

    @staticmethod
    def refine_shift(
        spec: np.ndarray, target_spec: np.ndarray, zones: list[tuple[int, int]], x_init: float
    ) -> float:
        """
        Refine the shift for a single spatial position back to the rectified input spectra.

        Line zones are used to increase the SNR of the chisq and the final shift is the mean of the shifts computed
        for each zone.

        Parameters
        ----------
        spec : np.ndarray
            The 1D spectrum to shift back

        target_spec : np.ndarray
            The reference spectrum. This should be the un-shifted, raw spectrum at the same position as `spec`

        zones : List
            List of zone borders (in px coords)

        x_init: float
            Initial guess for the shift. This is used to shift the zones so it needs to be pretty good, but not perfect.

        Returns
        -------
        float
            The shift value
        """
        shifts = np.zeros(len(zones))
        for i, z in enumerate(zones):
            if z[1] + int(x_init) >= spec.size:
                logger.info(f"Ignoring zone {z} with init {x_init} because it's out of range")
                continue
            idx = np.arange(z[0], z[1]) + int(x_init)
            shift = spo.minimize(
                SolarCalibration.shift_func,
                np.array([x_init]),
                args=(target_spec, spec, idx),
                method="nelder-mead",
            ).x[0]
            shifts[i] = shift

        return np.nanmedian(shifts)

    @staticmethod
    def shift_func(
        par: list[float], ref_spec: np.ndarray, spec: np.ndarray, idx: np.ndarray
    ) -> float:
        """
        Non-chisq based goodness of fit calculator for computing spectral shifts.

        Instead of chisq, the metric approximates the final Gain image.

        Parameters
        ----------
        par : List
            List of parameters for minimization

        ref_spec : np.ndarray
            Reference spectra

        spec : np.ndarray
            Data

        idx : np.ndarray
            Range of wavelength pixels that will be compared in fit

        Returns
        -------
        float
            Goodness of fit metric

        """
        shift = par[0]
        shifted_spec = spnd.shift(spec, shift, mode="constant", cval=np.nan)
        final_gain = (ref_spec / shifted_spec)[idx]
        slope = (final_gain[-1] - final_gain[0]) / final_gain.size
        bg = slope * np.arange(final_gain.size) + final_gain[0]
        subbed_gain = np.abs((final_gain) - bg)
        fit_metric = np.nansum(subbed_gain[np.isfinite(subbed_gain)])
        return fit_metric
