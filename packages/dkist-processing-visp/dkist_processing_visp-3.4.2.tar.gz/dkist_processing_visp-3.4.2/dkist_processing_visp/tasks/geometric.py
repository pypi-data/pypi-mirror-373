"""
Visp geometric calibration task.

See :doc:`this page </geometric>` for more information.
"""

from typing import Generator

import numpy as np
import peakutils as pku
import scipy.ndimage as spnd
import scipy.optimize as spo
import skimage.exposure as skie
import skimage.metrics as skim
import skimage.morphology as skimo
import skimage.registration as skir
from astropy.modeling import fitting
from astropy.modeling import models
from astropy.stats import sigma_clip
from dkist_processing_common.codecs.fits import fits_access_decoder
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_processing_math.arithmetic import subtract_array_from_arrays
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_service_configuration.logging import logger
from scipy.fft import fftn
from scipy.optimize import minimize
from skimage.registration._phase_cross_correlation import _upsampled_dft

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.parsers.visp_l0_fits_access import VispL0FitsAccess
from dkist_processing_visp.tasks.mixin.beam_access import BeamAccessMixin
from dkist_processing_visp.tasks.mixin.corrections import CorrectionsMixin
from dkist_processing_visp.tasks.mixin.line_zones import LineZonesMixin
from dkist_processing_visp.tasks.visp_base import VispTaskBase

__all__ = ["GeometricCalibration"]


class GeometricCalibration(
    VispTaskBase,
    BeamAccessMixin,
    CorrectionsMixin,
    QualityMixin,
    LineZonesMixin,
):
    """
    Task class for computing the spectral geometry. Geometry is represented by three quantities.

      - Angle - The angle (in radians) between slit hairlines and pixel axes. A one dimensional array with two elements: one for each beam.

      - State_offset - The [x, y] shift between each modstate in each beam and a fiducial modstate. For each modstate and each beam two state offset values are computed.

      - Spectral_shift - The shift in the spectral dimension for each beam for every spatial position needed to "straighten" the spectra so a single wavelength is at the same pixel for all slit positions.

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

            - Gather dark corrected frames
            - Calculate spectral tilt (angle)
            - Remove spectral tilt
            - Using the angle corrected array, find the state offset
            - Write state offset
            - Calculate the spectral skew and curvature (spectral shifts)
            - Write the spectral skew and curvature

        Returns
        -------
        None
        """
        # This lives outside the run() loops and has its own internal loops because the angle calculation
        # only happens for a single modstate
        with self.apm_processing_step("Basic corrections"):
            self.do_basic_corrections()

        for beam in range(1, self.constants.num_beams + 1):
            with self.apm_task_step(f"Generating geometric calibrations for {beam = }"):
                with self.apm_processing_step(f"Computing and writing angle for {beam = }"):
                    angle = self.compute_beam_angle(beam=beam)
                    if beam == 2:
                        with self.apm_processing_step("Refining beam 2 angle"):
                            ang_corr = self.refine_beam2_angle(angle)
                        logger.info(f"Beam 2 angle refinement = {np.rad2deg(ang_corr)} deg")
                        angle += ang_corr
                        logger.info(f"Final beam 2 angle = {np.rad2deg(angle)} deg")
                    self.write_angle(angle=angle, beam=beam)

                for modstate in range(1, self.constants.num_modstates + 1):
                    with self.apm_processing_step(
                        f"Removing angle from {beam = } and {modstate = }"
                    ):
                        angle_corr_array = self.remove_beam_angle(
                            angle=angle, beam=beam, modstate=modstate
                        )

                    with self.apm_processing_step(
                        f"Computing state offset for {beam = } and {modstate = }"
                    ):
                        state_offset = self.compute_modstate_offset(
                            array=angle_corr_array, beam=beam, modstate=modstate
                        )
                        self.write_state_offset(offset=state_offset, beam=beam, modstate=modstate)

                    with self.apm_processing_step(
                        f"Removing state offset for {beam = } and {modstate = }"
                    ):
                        self.remove_state_offset(
                            array=angle_corr_array,
                            offset=state_offset,
                            beam=beam,
                            modstate=modstate,
                        )

                with self.apm_processing_step(f"Computing spectral shifts for {beam = }"):
                    spec_shifts = self.compute_spectral_shifts(beam=beam)

                with self.apm_writing_step(f"Writing spectral shifts for {beam = }"):
                    self.write_spectral_shifts(shifts=spec_shifts, beam=beam)

        with self.apm_processing_step("Computing and logging quality metrics"):
            no_of_raw_geo_frames: int = self.scratch.count_all(
                tags=[
                    VispTag.input(),
                    VispTag.frame(),
                    VispTag.task_solar_gain(),
                ],
            )

            self.quality_store_task_type_counts(
                task_type=TaskName.geometric.value, total_frames=no_of_raw_geo_frames
            )

    def pre_run(self) -> None:
        """Run before run() with Elastic APM span capturing."""
        super().pre_run()
        self._fiducial_array = None
        self._fiducial_mask = None

    def basic_corrected_solar_data(self, beam: int, modstate: int) -> np.ndarray:
        """
        Dark corrected solar gain array for a single beam and modstate.

        Parameters
        ----------
        beam : int
            The current beam being processed

        modstate : int
            The current modulator state

        Returns
        -------
        np.ndarray
            Dark corrected data array
        """
        tags = [
            VispTag.intermediate_frame(beam=beam, modstate=modstate),
            VispTag.task("GC_SOLAR_BASIC"),
        ]
        array_generator = self.read(tags=tags, decoder=fits_array_decoder)
        return next(array_generator)

    def basic_corrected_lamp_data(self, beam: int, modstate: int) -> np.ndarray:
        """
        Dark corrected lamp gain array for a single beam and modstate.

        Parameters
        ----------
        beam : int
            The current beam being processed

        modstate : int
            The current modulator state

        Returns
        -------
        np.ndarray
            Dark corrected data array
        """
        tags = [
            VispTag.intermediate_frame(beam=beam, modstate=modstate),
            VispTag.task("GC_LAMP_BASIC"),
        ]
        array_generator = self.read(tags=tags, decoder=fits_array_decoder)
        return next(array_generator)

    @property
    def fiducial_array(self) -> np.ndarray:
        """Target array used for determining state offsets."""
        if self._fiducial_array is None:
            raise ValueError("Fiducial array has not been set. This should never happen.")
        return self._fiducial_array

    @fiducial_array.setter
    def fiducial_array(self, array: np.ndarray) -> None:
        """
        Set the target array used for determining state offsets.

        Parameters
        ----------
        array : np.ndarray
            Fiducial array

        Returns
        -------
        None
        """
        self._fiducial_array = array

    @property
    def fiducial_mask(self) -> np.ndarray:
        """Mask on target array used for determining state offsets.

        Pixels NOT around strong lines are masked out.
        """
        if self._fiducial_mask is None:
            raise ValueError("Fiducial array has not been set. This should never happen.")
        return self._fiducial_mask

    @fiducial_mask.setter
    def fiducial_mask(self, array: np.ndarray) -> None:
        """
        Set the target mask used for determining state offsets.

        Parameters
        ----------
        array : np.ndarray
            Fiducial mask

        Returns
        -------
        None
        """
        self._fiducial_mask = array

    def offset_corrected_array_generator(self, beam: int) -> Generator[np.ndarray, None, None]:
        """
        All modstates for a single beam that have had their state offset applied.

        This is a generator because the arrays will be immediately averaged

        Parameters
        ----------
        beam : int
            The current beam being processed

        Returns
        -------
        Generator[np.ndarray, None, None]
            Generator of state offset corrected arrays

        """
        tags = [VispTag.intermediate_frame(beam=beam), VispTag.task("GC_OFFSET")]
        array_generator = self.read(tags=tags, decoder=fits_array_decoder)
        return array_generator

    def do_basic_corrections(self):
        """Apply dark correction to all data that will be used for Geometric Calibration."""
        self.prep_lamp_gain()
        self.prep_input_solar_gain()

    def prep_lamp_gain(self):
        """Apply dark corrections fo INPUT lamp frames."""
        for readout_exp_time in self.constants.lamp_readout_exp_times:
            for beam in range(1, self.constants.num_beams + 1):
                logger.info(
                    f"Starting basic lamp reductions for {readout_exp_time = } and {beam = }"
                )
                dark_array = next(
                    self.read(
                        tags=VispTag.intermediate_frame_dark(
                            beam=beam, readout_exp_time=readout_exp_time
                        ),
                        decoder=fits_array_decoder,
                    )
                )

                for modstate in range(1, self.constants.num_modstates + 1):
                    tags = [
                        VispTag.input(),
                        VispTag.frame(),
                        VispTag.task_lamp_gain(),
                        VispTag.modstate(modstate),
                        VispTag.readout_exp_time(readout_exp_time),
                    ]
                    input_lamp_gain_objs = self.read(
                        tags=tags, decoder=fits_access_decoder, fits_access_class=VispL0FitsAccess
                    )

                    readout_normalized_arrays = (
                        self.beam_access_get_beam(o.data, beam=beam) / o.num_raw_frames_per_fpa
                        for o in input_lamp_gain_objs
                    )

                    avg_lamp_array = average_numpy_arrays(readout_normalized_arrays)

                    dark_corrected_lamp_array = next(
                        subtract_array_from_arrays(
                            arrays=avg_lamp_array, array_to_subtract=dark_array
                        )
                    )

                    logger.info(f"Writing dark corrected lamp data for {beam=}, {modstate=}")
                    self.write(
                        data=dark_corrected_lamp_array,
                        tags=[
                            VispTag.intermediate_frame(beam=beam, modstate=modstate),
                            VispTag.task("GC_LAMP_BASIC"),
                        ],
                        encoder=fits_array_encoder,
                    )

    def prep_input_solar_gain(self):
        """
        Apply dark correction to INPUT solar gain images.

        Lamp correction is not applied because it was found to reduce contrast between the spectra and the hairlines.
        """
        for readout_exp_time in self.constants.solar_readout_exp_times:
            for beam in range(1, self.constants.num_beams + 1):
                logger.info(f"Starting basic reductions for {readout_exp_time = } and {beam = }")
                dark_array = next(
                    self.read(
                        tags=VispTag.intermediate_frame_dark(
                            beam=beam, readout_exp_time=readout_exp_time
                        ),
                        decoder=fits_array_decoder,
                    )
                )

                for modstate in range(1, self.constants.num_modstates + 1):

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

                    avg_solar_array = average_numpy_arrays(readout_normalized_arrays)

                    dark_corrected_solar_array = next(
                        subtract_array_from_arrays(
                            arrays=avg_solar_array, array_to_subtract=dark_array
                        )
                    )

                    logger.info(f"Writing dark corrected data for {beam=}, {modstate=}")
                    self.write(
                        data=dark_corrected_solar_array,
                        tags=[
                            VispTag.intermediate_frame(beam=beam, modstate=modstate),
                            VispTag.task("GC_SOLAR_BASIC"),
                        ],
                        encoder=fits_array_encoder,
                    )

    def compute_beam_angle(self, beam: int) -> float:
        """
        Find the angle between the slit hairlines and the pixel axes for a single beam.

        Generally, the algorithm is:

         1. Split each beam in half spatially to isolate the two hairlines
         2. Fit the spatial location of each hairline for every spectral pixel
         3. Fit a line to each hairline; the angle of each line is the arctan of the slope
         4. Average the two hairline angles
         5. Repeat 1 - 4 for all modstates and average the results

        Parameters
        ----------
        beam : int
            The current beam being processed

        Returns
        -------
        float
            Beam angle in radians
        """
        angle_list = []
        for modstate in range(1, self.constants.num_modstates + 1):
            data = self.basic_corrected_lamp_data(beam=beam, modstate=modstate)
            angle = self.compute_single_modstate_angles(data)
            logger.info(f"Angles for {beam = } and {modstate = } = {np.rad2deg(angle)} deg")
            angle_list.append(angle)

        # Flatten the list just in case we got different numbers of hairline regions for the different modstates
        # This can happen in data with more than 2 hairlines, which can be caused by dust on the slit or (less likely) ghosting.
        flat_angle_list = np.hstack(angle_list)

        theta = float(np.nanmedian(flat_angle_list))
        logger.info(f"Beam angle for {beam = }: {np.rad2deg(theta):0.4f} deg")
        return theta

    def identify_hairlines_and_bad_pixels(
        self, input_array: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Return pixel coordinates corresponding to hairlines and a map of non-hairline bad pixels.

        This is almost exactly the same algorithm as `dkist_processing_visp.tasks.mixin.corrections.find_hairline_pixels`,
        but it adds an extra step of doing a morphological opening prior to smoothing in the spatial dimension. This
        opening helps to remove small point/dot-like pixels that are not part of the hairline.

        The difference between the opened result and the original deviant pixel map shows the locations of non-hairline
        "bad" (i.e., deviant) pixels. This map is also returned.

        Parameters
        ----------
        input_array : np.ndarray
            Input array

        Returns
        -------
        tuple[np.ndarray, np.ndarray]
            Pixel coordinates of hairlines and map of non-hairline bad pixels

        """
        filtered_array = spnd.median_filter(
            input_array, size=(1, self.parameters.hairline_median_spatial_smoothing_width_px)
        )
        diff = (input_array - filtered_array) / filtered_array
        hairline_locations = np.abs(diff) > self.parameters.hairline_fraction

        # dtype kwarg necessary here to avoid endianness issues
        mask_array = np.zeros_like(input_array, dtype=int)
        mask_array[hairline_locations] = 1

        # These lines are what's different between this function and
        # `dkist_processing_visp.tasks.mixin.corrections.find_hairline_pixels`
        cleaned_mask_array = skimo.diameter_opening(
            mask_array, diameter_threshold=self.parameters.geo_binary_opening_diameter
        )
        bad_pixel_map = (mask_array - cleaned_mask_array).astype(bool)

        # Now smooth the hairline mask in the spatial dimension to capture the higher-flux wings
        smoothed_mask_array = spnd.gaussian_filter1d(
            cleaned_mask_array.astype(float),
            self.parameters.hairline_mask_spatial_smoothing_width_px,
            axis=1,
        )

        hairline_locations = np.where(
            smoothed_mask_array
            > smoothed_mask_array.max()
            * self.parameters.hairline_mask_gaussian_peak_cutoff_fraction
        )

        return hairline_locations, bad_pixel_map

    def make_hairline_binary_and_bad_pixel_map(
        self, array: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Return two maps showing hairline pixels and bad pixels, respectively.

        The hairline map is type `int` because it is treated as a binary image.
        The bad pixel map is type `bool` because it will be used to index the source array.

        Parameters
        ----------
        array : np.ndarray
            Input array

        Returns
        -------
        tuple[np.ndarray, np.ndarray]
            Map of hairline pixels and map of bad pixels

        """
        hairline_locations, bad_pixel_map = self.identify_hairlines_and_bad_pixels(array)
        map = np.zeros_like(array)
        map[hairline_locations] = 1

        return map, bad_pixel_map

    def compute_single_modstate_angles(self, array: np.ndarray) -> np.ndarray:
        """
        Compute the angles of a single array.

        The angles are computed by simply looking at the slope of the hairlines. The hairlines are identified by fitting
        a Gaussian to each spectral pixel based on an initial guess from the center of mass of a binarized image.

        Parameters
        ----------
        array : np.ndarray
            Input array

        Returns
        -------
        np.ndarray
            Angles of a single modstate

        """
        full_binary, bad_pixel_map = self.make_hairline_binary_and_bad_pixel_map(array)

        # Roughly remove any non-hairline bad pxiels. We don't need this to be perfect.
        array[bad_pixel_map.astype(bool)] = np.nanmedian(array)

        hairline_regions = self.find_hairline_regions(full_binary)

        angles = []
        for h, hairline_idx in enumerate(hairline_regions, start=1):
            data = array[:, hairline_idx]
            binary = full_binary[:, hairline_idx]
            wave_size, spatial_size = data.shape
            wave_x = np.arange(wave_size)
            spatial_x = np.arange(spatial_size)

            # Compute the median spatial pixel location of all non-zero pixels in the map. This gives use a rough
            # guess of where the hairline center is for each spectral pixel. (The [None, :] and axis=1 allow us to
            # compute the COM for all spectral pixels at once, so hailine_centers_init_guess will have shape (wave_size, )).
            # Set the 0s to NaN so a nanmedian will only consider non-zero pixels.
            binary[binary == 0] = np.nan
            hairline_centers_init_guess = np.nanmedian(spatial_x[None, :] * binary, axis=1)

            # Now refine hairline center with a gaussian fit at each spectral pixel
            #
            # Initialize gaussian fit centers with NaN so any bad pixels can easily be ignored during the line fit.
            hairline_fit_centers = np.zeros(wave_size) * np.nan
            for i in range(wave_size):
                if np.isnan(hairline_centers_init_guess[i]):
                    # NaNs happen when there's no identified hairline pixels at all for a particular spectral pixel.
                    logger.info(
                        f"Hairline region {h} and spectral pixel {i} has a NaN initial guess. Ignoring pixel in line fit."
                    )
                    continue

                x0 = int(hairline_centers_init_guess[i])
                fit_slice = slice(
                    x0 - self.parameters.geo_hairline_fit_width_px,
                    x0 + self.parameters.geo_hairline_fit_width_px,
                )
                hairline_profile = data[i, fit_slice]
                abscissa = spatial_x[fit_slice]

                # Initial guesses for gaussian fit. Remember that the hairlines are negative gaussians
                a0 = hairline_profile.min() - hairline_profile.max()
                sig0 = 1
                bg0 = hairline_profile.max()
                slope0 = 0

                try:
                    fit_pars = spo.curve_fit(
                        GeometricCalibration.gaussian_with_background,
                        abscissa,
                        hairline_profile,
                        p0=[a0, x0, sig0, bg0, slope0],
                    )[0]
                    fit_center = fit_pars[1]
                except RuntimeError:
                    logger.info(
                        f"Hairline fit in hairline region {h} and pixel {i} failed. Ignoring pixel in line fit."
                    )
                    continue

                hairline_fit_centers[i] = fit_center

            slope = self.fit_line_to_hairline_centers(wave_x, hairline_fit_centers)

            # The angle is just the arctan of the slope
            angles.append(np.arctan(slope))

        return np.array(angles)

    def find_hairline_regions(self, binary: np.ndarray) -> list[np.ndarray]:
        """
        Identify spatial regions around each hairline.

        This function exists because some ViSP frames show extra hairlines beyond the expected two. These extra hairlines
        are likely the result of dust on the slit, but may also be caused by ghosting or reflections.
        Rather than ignore these we can use them to further refine the beam angle.

        Regions are constrained to be within the bounds of the input array.

        Parameters
        ----------
        binary : np.ndarray
            Input array

        Returns
        -------
        list[np.ndarray]
            A list of indices corresponding to each hairline

        """
        collapsed_binary = np.nanmean(binary, axis=0)
        hairline_idx = pku.indexes(
            collapsed_binary, thres=self.parameters.geo_hairline_flat_id_threshold
        )
        logger.info(f"Hairline centers at {hairline_idx}")
        hairline_regions = []

        region_width = self.parameters.geo_hairline_fit_width_px * 4
        lower_limit = 0
        upper_limit = binary.shape[1]
        for idx in hairline_idx:
            region = np.arange(
                max(idx - region_width, lower_limit), min(idx + region_width, upper_limit)
            )
            hairline_regions.append(region)

        return hairline_regions

    def fit_line_to_hairline_centers(
        self, abscissa: np.ndarray, hairline_centers: np.ndarray
    ) -> float:
        """
        Fit a 1-degree polynomial (i.e., a line) to the hairline centers.

        Outliers are iteratively removed using a sigma clipping algorithm as detailed here:
        https://docs.astropy.org/en/stable/modeling/example-fitting-line.html#iterative-fitting-using-sigma-clipping

        Parameters
        ----------
        abscissa : np.ndarray
            Abscissae

        hairline_centers : np.ndarray
            Hairline centers

        Returns
        -------
        float
            The slope of the fit line

        """
        non_nan_idx = ~np.isnan(hairline_centers)

        line_fitter = fitting.LinearLSQFitter()
        outlier_rejection_fitter = fitting.FittingWithOutlierRemoval(
            fitter=line_fitter,
            outlier_func=sigma_clip,
            sigma=self.parameters.geo_hairline_angle_fit_sig_clip,
            niter=10,
            cenfunc="median",
            stdfunc="std",
        )
        linear_model = models.Linear1D()

        fit_line, _ = outlier_rejection_fitter(
            model=linear_model, x=abscissa[non_nan_idx], y=hairline_centers[non_nan_idx]
        )

        return fit_line.slope.value

    @staticmethod
    def gaussian_with_background(
        x: np.ndarray, a: float, x0: float, sigma: float, background_level: float, slope: float
    ) -> np.ndarray:
        r"""Compute a scaled gaussian with a baseline offset and slope.

        The function returned is

        .. math::

            a \, {\mathrm e}^{-\frac{(x - x_0)^2}{2 {\sigma}^2}} + b + m (x - x_0)

        where :math:`b` is the baseline offset and :math:`m` is the baseline slope.

        Parameters
        ----------
        x : np.ndarray
            Position

        a : float
            Gaussian scale

        x0 : float
            Gaussian center

        sigma : float
            Gaussian sigma

        background_level : float
            Background level offset at x0

        slope : float
            Linear slope of background

        Returns
        -------
        np.ndarray
            Scaled Gaussian with offset and linear slope at x

        """
        gaussian = a * np.exp(-((x - x0) ** 2) / (2 * sigma**2))
        return gaussian + background_level + slope * (x - x0)

    def refine_beam2_angle(self, beam_2_init_angle: float) -> float:
        """Find the angular adjustment needed to align beam 2's spectra with beam 1.

        Because this angle will apply to all modulation states the comparison is made between averages over all
        modulation states of beam 1 and beam 2. First, a rough, global, offset is computed and then a minimizer
        minimizes the difference between the beams after applying first a rotation, then an offset to beam 2.

        To reduce the influence of low-frequency differences between the beams (e.g., optical gain response) the beam
        averages are first put through a high-pass filter that preserves hairlines and spectral features (which are
        sharp).
        """
        beam_1_angle_array = next(
            self.read(
                tags=[VispTag.intermediate_frame(beam=1), VispTag.task_geometric_angle()],
                decoder=fits_array_decoder,
            )
        )
        beam_1_angle = beam_1_angle_array[0]
        beam_1_hpf, beam_1_mask = self.prep_refine_ang_input(beam=1, angle=beam_1_angle)
        beam_2_hpf, beam_2_mask = self.prep_refine_ang_input(beam=2, angle=beam_2_init_angle)

        logger.info("Computing rough-guess average beam offset")
        x_init, y_init = self.compute_single_state_offset(
            beam_1_hpf, beam_2_hpf, fiducial_mask=beam_1_mask, array_mask=beam_2_mask
        )

        logger.info("Fitting beam 2 angle refinement")
        res = spo.minimize(
            self.refine_ang_func,
            np.array(
                [
                    x_init,
                    y_init,
                    0.0,
                ]
            ),
            args=(beam_1_hpf, beam_2_hpf),
            method="nelder-mead",
        )

        angle = res.x[2]
        if abs(angle) > self.parameters.geo_max_beam_2_angle_refinement:
            logger.info(f"Refining angle is too large ({np.rad2deg(angle)} deg). Not using it.")
            return 0.0

        return angle

    def prep_refine_ang_input(self, beam: int, angle: float) -> tuple[np.ndarray, np.ndarray]:
        """Prepare an averaged, high-pass-filtered array for a single beam.

        Average is over all modulation states.
        """
        logger.info(f"Prepping beam {beam} data for angle refinement")
        solar_basic_tags = [VispTag.intermediate_frame(beam=beam), VispTag.task("GC_SOLAR_BASIC")]
        arrays = list(self.read(tags=solar_basic_tags, decoder=fits_array_decoder))
        # list needed here because np.stack is depreciating working with a generator
        angle_corr_arrays = list(self.corrections_correct_geometry(arrays, angle=angle))
        modstate_avg = np.mean(np.stack(angle_corr_arrays), axis=0)

        mask = self.compute_offset_mask(modstate_avg)
        high_pass_filtered_array = self.high_pass_filter_array(modstate_avg)
        rescaled_high_pass_filtered_array = skie.rescale_intensity(
            high_pass_filtered_array, out_range=(0.0, 1.0)
        )

        return rescaled_high_pass_filtered_array, mask

    @staticmethod
    def refine_ang_func(x, target, image) -> float:
        """Rotate and shift beam 2 then compare for similarity with beam 1."""
        xshift, yshift, ang = x
        rotated = next(GeometricCalibration.corrections_correct_geometry(image, angle=ang))
        shifted = next(
            GeometricCalibration.corrections_correct_geometry(
                rotated, shift=np.array([xshift, yshift])
            )
        )
        # data_range = 1. because we rescaled the input images to be (0., 1.0) above
        metric = 1 - skim.structural_similarity(target, shifted, data_range=1.0)
        return metric

    def remove_beam_angle(self, angle: float, beam: int, modstate: int) -> np.ndarray:
        """
        Rotate a single modstate and beam's data by the beam angle.

        Parameters
        ----------
        angle : float
            The beam angle (in radians) for the current modstate

        beam : int
            The current beam being processed

        modstate : int
            The current modstate

        Returns
        -------
        np.ndarray
            Array corrected for beam angle
        """
        beam_mod_array = self.basic_corrected_solar_data(beam=beam, modstate=modstate)
        corrected_array = next(self.corrections_correct_geometry(beam_mod_array, angle=angle))
        return corrected_array

    def compute_modstate_offset(self, array: np.ndarray, beam: int, modstate: int) -> np.ndarray:
        """
        Higher-level helper function to compute the (x, y) offset between modstates.

        Exists so the fiducial array can be set from the first beam and modstate.

        Parameters
        ----------
        array : np.ndarray
            Beam data

        beam : int
            The current beam being processed

        modstate : int
            The current modstate

        Returns
        -------
        np.ndarray
            (x, y) offset between modstates
        """
        if beam == 1 and modstate == 1:
            logger.info("Set fiducial array")
            self.fiducial_array = self.high_pass_filter_array(array)
            self.fiducial_mask = self.compute_offset_mask(array)
            return np.zeros(2)

        hpf_array = self.high_pass_filter_array(array)
        array_mask = self.compute_offset_mask(array)
        shift = self.compute_single_state_offset(
            fiducial_array=self.fiducial_array,
            array=hpf_array,
            upsample_factor=self.parameters.geo_upsample_factor,
            fiducial_mask=self.fiducial_mask,
            array_mask=array_mask,
        )
        logger.info(
            f"Offset for {beam = } and {modstate = } is {np.array2string(shift, precision=3)}"
        )

        return shift

    def remove_state_offset(
        self, array: np.ndarray, offset: np.ndarray, beam: int, modstate: int
    ) -> None:
        """
        Shift an array by some offset (to make it in line with the fiducial array).

        Parameters
        ----------
        array : np.ndarray
            Beam data

        offset : np.ndarray
            The state offset for the current modstate

        beam : int
            The current beam being processed

        modstate : int
            The current modstate

        Returns
        -------
        None

        """
        corrected_array = next(self.corrections_correct_geometry(array, shift=offset))
        self.write(
            data=corrected_array,
            tags=[
                VispTag.intermediate_frame(beam=beam, modstate=modstate),
                VispTag.task("GC_OFFSET"),
            ],
            encoder=fits_array_encoder,
        )

    def compute_spectral_shifts(self, beam: int) -> np.ndarray:
        """
        Compute the spectral 'curvature'.

        I.e., the spectral shift at each spatial pixel needed to have wavelength be constant across a single spectral
        pixel. Generally, the algorithm is:

         1. Identify the fiducial spectrum as the center of the slit
         2. For each spatial pixel, make an initial guess of the shift via correlation
         3. Take the initial guesses and use them in a chisq minimizer to refine the shifts
         4. Interpolate over those shifts identified as too large
         5. Remove the mean shift so the total shift amount is minimized

        Parameters
        ----------
        beam : int
            The current beam being processed

        Returns
        -------
        np.ndarray
            Spectral shift for a single beam
        """
        max_shift = self.parameters.geo_max_shift
        poly_fit_order = self.parameters.geo_poly_fit_order

        logger.info(f"Computing spectral shifts for beam {beam}")
        beam_generator = self.offset_corrected_array_generator(beam=beam)
        avg_beam_array = average_numpy_arrays(beam_generator)
        num_spec = avg_beam_array.shape[1]

        self.write(
            data=avg_beam_array,
            encoder=fits_array_encoder,
            tags=[VispTag.debug(), VispTag.frame()],
            relative_path=f"DEBUG_GC_AVG_OFFSET_BEAM_{beam}.dat",
            overwrite=True,
        )

        ref_spec = avg_beam_array[:, num_spec // 2]
        beam_shifts = np.empty(num_spec) * np.nan
        for j in range(num_spec):
            target_spec = avg_beam_array[:, j]

            ## Correlate the target and reference beams to get an initial guess
            corr = np.correlate(
                target_spec - np.nanmean(target_spec),
                ref_spec - np.nanmean(ref_spec),
                mode="same",
            )
            # This min_dist ensures we only find a single peak in each correlation signal
            pidx = pku.indexes(corr, min_dist=corr.size)
            initial_guess = 1 * (pidx - corr.size // 2)

            # These edge-cases are very rare, but do happen sometimes
            if initial_guess.size == 0:
                logger.info(
                    f"Spatial position {j} in {beam=} doesn't have a correlation peak. Initial guess set to 0"
                )
                initial_guess = 0.0

            elif initial_guess.size > 1:
                logger.info(
                    f"Spatial position {j} in {beam=} has more than one correlation peak ({initial_guess}). Initial guess set to mean ({np.nanmean(initial_guess)})"
                )
                initial_guess = np.nanmean(initial_guess)

            ## Then refine shift with a chisq minimization
            shift = minimize(
                self.shift_chisq,
                np.atleast_1d(initial_guess),
                args=(ref_spec, target_spec),
                method="nelder-mead",
            ).x[0]
            if np.abs(shift) > max_shift:
                # Didn't find a good peak, probably because of a hairline
                logger.info(
                    f"shift in {beam=} at spatial pixel {j} out of range ({shift} > {max_shift})"
                )
                continue

            beam_shifts[j] = shift

        ## Subtract the average so we shift my a minimal amount
        beam_shifts -= np.nanmean(beam_shifts)

        ## Finally, fit the shifts and return the resulting polynomial
        nan_idx = np.isnan(beam_shifts)
        poly = np.poly1d(
            np.polyfit(np.arange(num_spec)[~nan_idx], beam_shifts[~nan_idx], poly_fit_order)
        )

        return poly(np.arange(num_spec))

    @staticmethod
    def compute_single_state_offset(
        fiducial_array: np.ndarray,
        array: np.ndarray,
        upsample_factor: float = 1000.0,
        fiducial_mask: np.ndarray | None = None,
        array_mask: np.ndarray | None = None,
    ) -> np.ndarray:
        """
        Find the (x, y) shift between the current beam and the reference beam.

        The shift is found by fitting the peak of the correlation of the two beams

        Parameters
        ----------
        fiducial_array : np.ndarray
            Reference beam from mod state 1 data

        array : np.ndarray
            Beam data from current mod state

        Returns
        -------
        numpy.ndarray
            The (x, y) shift between the reference beam and the current beam at hand
        """
        shift = skir.phase_cross_correlation(
            fiducial_array,
            array,
            reference_mask=fiducial_mask,
            moving_mask=array_mask,
        )[0]

        if upsample_factor != 1.0:
            logger.info(f"Rough shift = {np.array2string(-1 * shift, precision=3)}")
            shift = GeometricCalibration.refine_modstate_shift(
                shift, fiducial_array, array, upsample_factor=upsample_factor
            )

        # Multiply by -1 so that the output is the shift needed to move from "perfect" to the current state.
        #  In other words, applying a shift equal to the negative of the output of this function will undo the measured
        #  shift.
        return -shift

    @staticmethod
    def refine_modstate_shift(
        shifts: np.ndarray,
        fiducial_array: np.ndarray,
        target_array: np.ndarray,
        upsample_factor: float = 10.0,
    ):
        """Refine a shift from `compute_single_state_offset` using an upsampling technique.

        This is taken directly from the un-masked version of `skimage.registration.phase_cross_correlation`.
        """
        # All comments below are copied from `skimage.registration.phase_cross_correlation`
        src_freq = fftn(fiducial_array)
        target_freq = fftn(target_array)
        image_product = src_freq * target_freq.conj()

        upsample_factor = np.array(upsample_factor, dtype=fiducial_array.dtype)
        shifts = np.round(shifts * upsample_factor) / upsample_factor
        upsampled_region_size = np.ceil(upsample_factor * 1.5)
        # Center of output array at dftshift + 1
        dftshift = np.fix(upsampled_region_size / 2.0)
        # Matrix multiply DFT around the current shift estimate
        sample_region_offset = dftshift - shifts * upsample_factor
        cross_correlation = _upsampled_dft(
            image_product.conj(), upsampled_region_size, upsample_factor, sample_region_offset
        ).conj()
        # Locate maximum and map back to original pixel grid
        maxima = np.unravel_index(np.argmax(np.abs(cross_correlation)), cross_correlation.shape)

        maxima = np.stack(maxima).astype(fiducial_array.dtype, copy=False)
        maxima -= dftshift

        shifts += maxima / upsample_factor

        return shifts

    def compute_offset_mask(self, array: np.ndarray) -> np.ndarray:
        """Generate a 2D mask that exclude non-line regions.

        These masks are then used to greatly improve the accuracy of the phase cross-correlation used in
        `compute_single_state_offset`.
        """
        zone_kwargs = {
            "prominence": self.parameters.solar_zone_prominence,
            "width": self.parameters.solar_zone_width,
            "bg_order": self.parameters.solar_zone_bg_order,
            "normalization_percentile": self.parameters.solar_zone_normalization_percentile,
            "rel_height": self.parameters.solar_zone_rel_height,
        }
        zones = self.compute_line_zones(array, **zone_kwargs)
        logger.info(f"Found {zones = }")
        mask = np.zeros(array.shape).astype(bool)
        for z in zones:
            mask[z[0] : z[1], :] = True

        return mask

    @staticmethod
    def high_pass_filter_array(array: np.ndarray) -> np.ndarray:
        """Perform a simple high-pass filter to accentuate narrow features (hairlines and spectra)."""
        return array / spnd.gaussian_filter(array, sigma=5)

    @staticmethod
    def shift_chisq(par: np.ndarray, ref_spec: np.ndarray, spec: np.ndarray) -> float:
        """
        Goodness of fit calculation for a simple shift. Uses simple chisq as goodness of fit.

        Less robust than SolarCalibration's `refine_shift`, but much faster.

        Parameters
        ----------
        par : np.ndarray
            Spectral shift being optimized

        ref_spec : np.ndarray
            Reference spectra (from first modstate)

        spec : np.ndarray
            Spectra being fitted

        Returns
        -------
        float
            Sum of chisquared fit

        """
        shift = par[0]
        shifted_spec = spnd.shift(spec, -shift, mode="constant", cval=np.nan)
        chisq = np.nansum((ref_spec - shifted_spec) ** 2 / ref_spec)
        return chisq

    def write_angle(self, angle: float, beam: int) -> None:
        """
        Write the angle component of the geometric calibration for a single beam.

        Parameters
        ----------
        angle : float
            The beam angle (radians) for the current modstate

        beam : int
            The current beam being processed

        Returns
        -------
        None
        """
        array = np.array([angle])
        self.write(
            data=array,
            tags=[VispTag.intermediate_frame(beam=beam), VispTag.task_geometric_angle()],
            encoder=fits_array_encoder,
        )

    def write_state_offset(self, offset: np.ndarray, beam: int, modstate: int) -> None:
        """
        Write the state offset component of the geometric calibration for a single modstate and beam.

        Parameters
        ----------
        offset : np.ndarray
            The state offset for the current modstate

        beam : int
            The current beam being processed

        modstate : int
            The current modstate

        Returns
        -------
        None

        """
        self.write(
            data=offset,
            tags=[
                VispTag.intermediate_frame(beam=beam, modstate=modstate),
                VispTag.task_geometric_offset(),
            ],
            encoder=fits_array_encoder,
        )

    def write_spectral_shifts(self, shifts: np.ndarray, beam: int) -> None:
        """
        Write the spectral shift component of the geometric calibration for a single beam.

        Parameters
        ----------
        shifts : np.ndarray
            The spectral shifts for the current beam

        beam : int
            The current beam being processed

        Returns
        -------
        None

        """
        self.write(
            data=shifts,
            tags=[VispTag.intermediate_frame(beam=beam), VispTag.task_geometric_spectral_shifts()],
            encoder=fits_array_encoder,
        )
