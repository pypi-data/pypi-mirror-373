"""ViSP instrument polarization task. See :doc:`this page </polarization_calibration>` for more information."""

from collections import defaultdict

import numpy as np
import scipy.ndimage as spnd
from astropy.io import fits
from dkist_processing_common.codecs.fits import fits_access_decoder
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_processing_math.arithmetic import divide_arrays_by_array
from dkist_processing_math.arithmetic import subtract_array_from_arrays
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_processing_math.transform.binning import resize_arrays
from dkist_processing_pac.fitter.polcal_fitter import PolcalFitter
from dkist_processing_pac.input_data.drawer import Drawer
from dkist_processing_pac.input_data.dresser import Dresser
from dkist_service_configuration.logging import logger
from sklearn.linear_model import RANSACRegressor
from sklearn.pipeline import Pipeline
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.preprocessing import RobustScaler

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.parsers.visp_l0_fits_access import VispL0FitsAccess
from dkist_processing_visp.tasks.mixin.beam_access import BeamAccessMixin
from dkist_processing_visp.tasks.mixin.corrections import CorrectionsMixin
from dkist_processing_visp.tasks.mixin.downsample import DownsampleMixin
from dkist_processing_visp.tasks.visp_base import VispTaskBase

__all__ = ["InstrumentPolarizationCalibration"]


class InstrumentPolarizationCalibration(
    VispTaskBase,
    BeamAccessMixin,
    CorrectionsMixin,
    DownsampleMixin,
    QualityMixin,
):
    """
    Task class for instrument polarization for a VISP calibration run.

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

            - Reduce calibration sequence steps
            - Fit reduced data to PAC parameters
            - Compute and save demodulation matrices

        Returns
        -------
        None

        """
        if not self.constants.correct_for_polarization:
            return

        polcal_readout_exposure_times = self.constants.polcal_readout_exp_times
        if len(polcal_readout_exposure_times) > 1:
            logger.info(
                "WARNING: More than one polcal readout exposure time detected. "
                "Everything *should* still work, but this is a weird condition that may produce "
                "strange results."
            )
        logger.info(f"{polcal_readout_exposure_times = }")

        # Process the pol cal frames
        logger.info(
            f"Demodulation matrices will span FOV with shape 1 spectral bin "
            f"and median smoothing of {self.parameters.polcal_spatial_median_filter_width_px} px in the spatial dimension."
        )
        remove_I_trend = self.parameters.pac_remove_linear_I_trend
        for beam in range(1, self.constants.num_beams + 1):
            with self.apm_processing_step("Generate polcal DARK frame"):
                logger.info("Generating polcal dark frame")
                self.generate_polcal_dark_calibration(
                    readout_exp_times=polcal_readout_exposure_times, beam=beam
                )

            with self.apm_processing_step("Generate polcal GAIN frame"):
                logger.info("Generating polcal gain frame")
                self.generate_polcal_gain_calibration(
                    readout_exp_times=polcal_readout_exposure_times, beam=beam
                )

            with self.apm_processing_step(f"Reducing CS steps for {beam = }"):
                local_reduced_arrays, global_reduced_arrays = self.reduce_cs_steps(beam)

            with self.apm_processing_step(f"Fit CU parameters for {beam = }"):
                local_dresser = Dresser()
                local_dresser.add_drawer(
                    Drawer(local_reduced_arrays, remove_I_trend=remove_I_trend)
                )
                global_dresser = Dresser()
                global_dresser.add_drawer(
                    Drawer(global_reduced_arrays, remove_I_trend=remove_I_trend)
                )
                pac_fitter = PolcalFitter(
                    local_dresser=local_dresser,
                    global_dresser=global_dresser,
                    fit_mode=self.parameters.pac_fit_mode,
                    init_set=self.constants.pac_init_set,
                    inherit_global_vary_in_local_fit=True,
                    suppress_local_starting_values=True,
                    fit_TM=False,
                )

            with self.apm_processing_step(f"Resampling demodulation matrices for {beam = }"):
                demod_matrices = pac_fitter.demodulation_matrices

                self.write(
                    data=demod_matrices,
                    encoder=fits_array_encoder,
                    tags=[VispTag.debug(), VispTag.frame()],
                    relative_path=f"DEBUG_IPC_RAW_DEMOD_BEAM_{beam}.dat",
                    overwrite=True,
                )

                logger.info(f"Smoothing demodulation matrices for {beam = }")
                smoothed_demod = self.smooth_demod_matrices(demod_matrices)
                self.write(
                    data=smoothed_demod,
                    encoder=fits_array_encoder,
                    tags=[VispTag.debug(), VispTag.frame()],
                    relative_path=f"DEBUG_IPC_SMOOTH_DEMOD_BEAM_{beam}.dat",
                    overwrite=True,
                )

                # Reshaping the demodulation matrix to get rid of unit length dimensions
                logger.info(f"Resampling demodulation matrices for {beam = }")
                demod_matrices = self.reshape_demod_matrices(smoothed_demod)
                logger.info(f"Shape of resampled demodulation matrices: {demod_matrices.shape}")

            with self.apm_writing_step(f"Writing demodulation matrices for {beam = }"):
                # Save the demod matrices as intermediate products
                self.write(
                    data=demod_matrices,
                    tags=[
                        VispTag.intermediate_frame(beam=beam),
                        VispTag.task_demodulation_matrices(),
                    ],
                    encoder=fits_array_encoder,
                )

            with self.apm_processing_step("Computing and recording polcal quality metrics"):
                self.record_polcal_quality_metrics(beam, polcal_fitter=pac_fitter)

        with self.apm_processing_step("Computing and logging quality metrics"):
            no_of_raw_polcal_frames: int = self.scratch.count_all(
                tags=[
                    VispTag.input(),
                    VispTag.frame(),
                    VispTag.task_polcal(),
                ],
            )

            self.quality_store_task_type_counts(
                task_type=TaskName.polcal.value, total_frames=no_of_raw_polcal_frames
            )

    def reduce_cs_steps(
        self, beam: int
    ) -> tuple[dict[int, list[VispL0FitsAccess]], dict[int, list[VispL0FitsAccess]]]:
        """
        Reduce all the data for the cal sequence steps for this beam.

        Parameters
        ----------
        beam
            The current beam being processed

        Returns
        -------
        dict
            A Dict of calibrated and binned arrays for all the cs steps for this beam
        """
        # Create the dicts to hold the results
        local_reduced_array_dict = defaultdict(list)
        global_reduced_array_dict = defaultdict(list)

        background_array = None
        if self.parameters.background_on:
            background_array = next(
                self.read(
                    tags=[VispTag.intermediate_frame(beam=beam), VispTag.task_background()],
                    decoder=fits_array_decoder,
                )
            )

        logger.info(
            f"Data will be downsampled in the spatial dimension to {self.parameters.polcal_num_spatial_bins} pixels."
        )
        for modstate in range(1, self.constants.num_modstates + 1):
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

            for readout_exp_time in self.constants.polcal_readout_exp_times:
                # Put this loop here because the geometric objects will be constant across exposure times
                logger.info(f"Loading polcal dark for {beam = }")
                dark_array = next(
                    self.read(
                        tags=VispTag.intermediate_frame_polcal_dark(
                            beam=beam, readout_exp_time=readout_exp_time
                        ),
                        decoder=fits_array_decoder,
                    )
                )

                if background_array is None:
                    background_array = np.zeros(dark_array.shape)

                for cs_step in range(self.constants.num_cs_steps):
                    local_obj, global_obj = self.reduce_single_step(
                        beam,
                        dark_array,
                        background_array,
                        modstate,
                        cs_step,
                        readout_exp_time,
                        angle,
                        state_offset,
                        spec_shift,
                    )
                    local_reduced_array_dict[cs_step].append(local_obj)
                    global_reduced_array_dict[cs_step].append(global_obj)

        return local_reduced_array_dict, global_reduced_array_dict

    def reduce_single_step(
        self,
        beam: int,
        dark_array: np.ndarray,
        background_array: np.ndarray,
        modstate: int,
        cs_step: int,
        readout_exp_time: float,
        angle: float,
        state_offset: np.ndarray,
        spec_shift: np.ndarray,
    ) -> tuple[VispL0FitsAccess, VispL0FitsAccess]:
        """
        Reduce a single calibration step for this beam, cs step and modulator state.

        Parameters
        ----------
        beam : int
            The current beam being processed

        dark_array : np.ndarray
            The dark array for the current beam

        modstate : int
            The current modulator state

        cs_step : int
            The current cal sequence step

        readout_exp_time : float
            The per-readout exposure time

        angle : float
            The beam angle for the current modstate

        state_offset : np.ndarray
            The state offset for the current modstate

        spec_shift : np.ndarray
            The spectral shift for the current modstate

        Returns
        -------
        tuple
            FitsAccess objects with the final reduced result for this single step

        """
        apm_str = f"{beam = }, {modstate = }, {cs_step = }, and {readout_exp_time = }"
        logger.info(f"Reducing {apm_str}")
        # Get the iterable of objects for this beam, cal seq step and mod state

        # Get the headers and arrays as iterables
        tags = [
            VispTag.frame(),
            VispTag.input(),
            VispTag.task_polcal(),
            VispTag.modstate(modstate),
            VispTag.cs_step(cs_step),
            VispTag.readout_exp_time(readout_exp_time),
        ]
        polcal_objs = list(
            self.read(tags=tags, decoder=fits_access_decoder, fits_access_class=VispL0FitsAccess)
        )
        # Grab the 1st header
        avg_inst_pol_cal_header = polcal_objs[0].header

        # Average the arrays (this works for a single array as well)
        readout_normalized_arrays = (
            self.beam_access_get_beam(o.data, beam=beam) / o.num_raw_frames_per_fpa
            for o in polcal_objs
        )
        avg_inst_pol_cal_array = average_numpy_arrays(readout_normalized_arrays)

        with self.apm_processing_step(f"Apply basic corrections for {apm_str}"):
            dark_corrected_array = subtract_array_from_arrays(avg_inst_pol_cal_array, dark_array)

            background_corrected_array = subtract_array_from_arrays(
                dark_corrected_array, background_array
            )

            polcal_gain_array = next(
                self.read(
                    tags=[
                        VispTag.intermediate_frame_polcal_gain(
                            beam=beam, readout_exp_time=readout_exp_time
                        ),
                    ],
                    decoder=fits_array_decoder,
                )
            )
            gain_corrected_array = next(
                divide_arrays_by_array(background_corrected_array, polcal_gain_array)
            )

            geo_corrected_array = self.corrections_correct_geometry(
                gain_corrected_array, -state_offset, angle
            )

            spectral_corrected_array = next(
                self.corrections_remove_spec_geometry(geo_corrected_array, spec_shift)
            )

        with self.apm_processing_step(f"Extract macro pixels from {apm_str}"):
            self.set_original_beam_size(gain_corrected_array)
            filtered_array = self.corrections_mask_hairlines(spectral_corrected_array)

            # Add back in a dummy spectral dimension so things stay 2D, which helps thinking about it later on.
            spectral_binned_array = np.nanmedian(filtered_array, axis=0)[None, :]

            spatially_smoothed_array = spnd.median_filter(
                spectral_binned_array,
                # The 1 below means we don't smooth in the spectral dimension
                size=(1, self.parameters.polcal_spatial_median_filter_width_px),
            )

            local_array = self.downsample_spatial_dimension_local_median(
                spatially_smoothed_array, self.parameters.polcal_num_spatial_bins
            )

            # Add two dummy dimensions just to keep it 2D.
            global_binned_array = np.nanmedian(filtered_array)[None, None]

        with self.apm_processing_step(f"Create reduced VispL0FitsAccess for {apm_str}"):
            local_result = VispL0FitsAccess(
                fits.ImageHDU(local_array, avg_inst_pol_cal_header),
                auto_squeeze=False,
            )

            global_result = VispL0FitsAccess(
                fits.ImageHDU(global_binned_array, avg_inst_pol_cal_header),
                auto_squeeze=False,
            )

        return local_result, global_result

    def smooth_demod_matrices(self, demod_matrices: np.ndarray) -> np.ndarray:
        """
        Smooth demodulation matrices in the spatial dimension.

        The output will fully sample the spatial dimension so, as a side effect, this function also up-samples any data
        that were binned spatially.

        Smoothing is done using a RANSAC regression estimator to perform a polynomial fit with high resilience to outliers.
        """
        # We need to smooth the *modulation* (not DEmodulation) matrices to preserve the normalization of the Stokes-I
        # values. linalg.pinv makes this easy
        modulation_matrices = np.linalg.pinv(demod_matrices)

        num_wave, num_binned_slit_pos, num_mod, num_stokes = modulation_matrices.shape
        num_full_slit_pos = self.single_beam_shape[1]

        smoothed_mod = np.zeros((num_wave, num_full_slit_pos, num_mod, num_stokes))

        # The binned abscissa is the "x" locations of the bins along the full spatial range
        # The full abscissa is the "x" locations of all spatial pixels
        # Add dummy dimensions because sklearn requires it
        binned_abscissa = np.linspace(
            start=0, stop=num_full_slit_pos, num=num_binned_slit_pos, endpoint=False
        )[:, None]
        full_abscissa = np.arange(num_full_slit_pos)[:, None]

        model = self.build_RANSAC_model()
        for w in range(num_wave):
            for m in range(num_mod):
                for s in range(num_stokes):
                    curve = modulation_matrices[w, :, m, s]

                    # Clean weirdo pixels
                    fill_value = np.nanmedian(curve)
                    curve[~np.isfinite(curve)] = fill_value

                    model.fit(binned_abscissa, curve)
                    fit_curve = model.predict(full_abscissa)
                    smoothed_mod[w, :, m, s] = fit_curve

        # Now compute the inverse again to return the DEmodulation matrices
        smoothed_demod = np.linalg.pinv(smoothed_mod)

        return smoothed_demod

    def build_RANSAC_model(self) -> Pipeline:
        """Build a scikit-learn pipeline from a set of estimators."""
        # PolynomialFeatures casts the pipeline as a polynomial fit
        # see https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.PolynomialFeatures.html#sklearn.preprocessing.PolynomialFeatures
        poly_feature = PolynomialFeatures(
            degree=self.parameters.polcal_demod_spatial_smooth_fit_order
        )

        # RobustScaler is a scale factor that is robust to outliers
        # see https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.RobustScaler.html#sklearn.preprocessing.RobustScaler
        scaler = RobustScaler()

        # The RANSAC regressor iteratively sub-samples the input data and constructs a model with this sub-sample.
        # The method used allows it to be robust to outliers.
        # see https://scikit-learn.org/stable/modules/linear_model.html#ransac-regression
        RANSAC = RANSACRegressor(
            min_samples=self.parameters.polcal_demod_spatial_smooth_min_samples
        )

        return make_pipeline(poly_feature, scaler, RANSAC)

    def reshape_demod_matrices(self, demod_matrices: np.ndarray) -> np.ndarray:
        """Upsample demodulation matrices to match the full beam size.

        Given an input set of demodulation matrices with shape (X', Y', 4, M) resample the output to shape
        (X, Y, 4, M), where X' and Y' are the binned size of the beam FOV, X and Y are the full beam shape, and M is the
        number of modulator states.

        If only a single demodulation matrix was made then it is returned as a single array with shape (4, M).

        Parameters
        ----------
        demod_matrices
            A set of demodulation matrices with shape (X', Y', 4, M)

        Returns
        -------
        np.ndarray
            If X' or Y' > 1 then upsampled matrices that are the full beam size (X, Y, 4, M).
            If X' == Y' == 1 then a single matric for the whole FOV with shape (4, M)

        """
        if len(demod_matrices.shape) != 4:
            raise ValueError(
                f"Expected demodulation matrices to have 4 dimensions. Got shape {demod_matrices.shape}"
            )

        data_shape = demod_matrices.shape[
            :2
        ]  # The non-demodulation matrix part of the larger array
        demod_shape = demod_matrices.shape[-2:]  # The shape of a single demodulation matrix
        logger.info(f"Demodulation FOV sampling shape: {data_shape}")
        logger.info(f"Demodulation matrix shape: {demod_shape}")
        if data_shape == (1, 1):
            # A single modulation matrix can be used directly, so just return it after removing extraneous dimensions
            logger.info(f"Single demodulation matrix detected")
            return demod_matrices[0, 0, :, :]

        target_shape = self.single_beam_shape + demod_shape
        logger.info(f"Target full-frame demodulation shape: {target_shape}")
        return self.resize_polcal_array(demod_matrices, target_shape)

    def record_polcal_quality_metrics(self, beam: int, polcal_fitter: PolcalFitter):
        """Record various quality metrics from PolCal fits."""
        self.quality_store_polcal_results(
            polcal_fitter=polcal_fitter,
            label=f"Beam {beam}",
            # Yes, the first bin is actually hard-coded right now
            bin_nums=[1, self.parameters.polcal_num_spatial_bins],
            bin_labels=["spectral", "spatial"],
            ## This is a bit of a hack and thus needs some explanation
            # By using the ``skip_recording_constant_pars`` switch we DON'T record the "polcal constant parameters" metric
            # for beam 2. This is because both beam 1 and beam 2 will have the same table. The way `*-common` is built
            # it will look for all metrics for both beam 1 and beam 2 so if we did save that metric for beam 2 then the
            # table would show up twice in the quality report. The following line avoids that.
            skip_recording_constant_pars=beam != 1,
        )

    def set_original_beam_size(self, array: np.ndarray) -> None:
        """Record the shape of a single beam as a class property."""
        self.single_beam_shape = array.shape

    def resize_polcal_array(self, array: np.ndarray, output_shape: tuple[int, ...]) -> np.ndarray:
        """
        Resize PolCal array.

        Parameters
        ----------
        array : np.ndarray
            Input PolCal array

        output_shape : tuple
            Shape of output array

        Returns
        -------
        np.ndarray
            Reshaped PolCal array

        """
        return next(
            resize_arrays(array, output_shape, order=self.parameters.polcal_demod_upsample_order)
        )

    def generate_polcal_dark_calibration(
        self, readout_exp_times: list[float] | tuple[float], beam: int
    ) -> None:
        """Compute an average polcal dark array for all polcal exposure times."""
        for readout_exp_time in readout_exp_times:
            logger.info(f"Computing polcal dark for  {readout_exp_time = }")

            dark_arrays = self.read(
                tags=[
                    VispTag.input(),
                    VispTag.frame(),
                    VispTag.task_polcal_dark(),
                    VispTag.readout_exp_time(readout_exp_time),
                ],
                decoder=fits_access_decoder,
                fits_access_class=VispL0FitsAccess,
            )

            readout_normalized_arrays = (
                self.beam_access_get_beam(o.data, beam=beam) / o.num_raw_frames_per_fpa
                for o in dark_arrays
            )

            avg_array = average_numpy_arrays(readout_normalized_arrays)
            self.write(
                data=avg_array,
                tags=[
                    VispTag.intermediate_frame_polcal_dark(
                        beam=beam, readout_exp_time=readout_exp_time
                    ),
                ],
                encoder=fits_array_encoder,
            )

    def generate_polcal_gain_calibration(
        self, readout_exp_times: list[float] | tuple[float], beam: int
    ) -> None:
        """
        Average 'clear' polcal frames to produce a polcal gain calibration.

        The polcal dark calibration is applied prior to averaging.
        """
        for readout_exp_time in readout_exp_times:
            logger.info(f"Computing polcal gain for {readout_exp_time = }")

            dark_array = next(
                self.read(
                    tags=[
                        VispTag.intermediate_frame(beam=beam),
                        VispTag.task_polcal_dark(),
                        VispTag.readout_exp_time(readout_exp_time),
                    ],
                    decoder=fits_array_decoder,
                )
            )

            gain_arrays = self.read(
                tags=[
                    VispTag.input(),
                    VispTag.frame(),
                    VispTag.task_polcal_gain(),
                    VispTag.readout_exp_time(readout_exp_time),
                ],
                decoder=fits_access_decoder,
                fits_access_class=VispL0FitsAccess,
            )

            readout_normalized_arrays = (
                self.beam_access_get_beam(o.data, beam=beam) / o.num_raw_frames_per_fpa
                for o in gain_arrays
            )

            dark_corrected_arrays = subtract_array_from_arrays(
                arrays=readout_normalized_arrays, array_to_subtract=dark_array
            )

            avg_array = average_numpy_arrays(dark_corrected_arrays)
            self.write(
                data=avg_array,
                tags=[
                    VispTag.intermediate_frame_polcal_gain(
                        beam=beam, readout_exp_time=readout_exp_time
                    ),
                ],
                encoder=fits_array_encoder,
            )
