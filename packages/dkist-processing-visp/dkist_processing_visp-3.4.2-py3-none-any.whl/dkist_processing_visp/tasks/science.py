"""ViSP science calibration task. See :doc:`this page </science_calibration>` for more information."""

from collections import defaultdict
from dataclasses import dataclass
from functools import cached_property
from typing import Iterable

import numpy as np
from astropy.io import fits
from astropy.time import Time
from astropy.time import TimeDelta
from dkist_processing_common.codecs.fits import fits_access_decoder
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_processing_math.arithmetic import divide_arrays_by_array
from dkist_processing_math.arithmetic import subtract_array_from_arrays
from dkist_processing_math.linear_algebra import nd_left_matrix_multiply
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_processing_pac.optics.telescope import Telescope
from dkist_service_configuration.logging import logger

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.parsers.visp_l0_fits_access import VispL0FitsAccess
from dkist_processing_visp.tasks.mixin.beam_access import BeamAccessMixin
from dkist_processing_visp.tasks.mixin.corrections import CorrectionsMixin
from dkist_processing_visp.tasks.visp_base import VispTaskBase

__all__ = ["ScienceCalibration"]


@dataclass
class CalibrationCollection:
    """Dataclass to hold all calibration objects and allow for easy, property-based access."""

    dark: dict
    background: dict
    solar_gain: dict
    angle: dict
    state_offset: dict
    spec_shift: dict
    demod_matrices: dict | None

    @cached_property
    def beams_overlap_slice(self) -> tuple[slice, slice]:
        """
        Compute array slices that will extract the largest region with overlap from both beams.

        This is done by considering that state offset values computed by the GeometricCalibration task. Any sub-pixel
        overlaps are rounded to the next integer that still guarantees overlap.
        """
        logger.info("Computing beam overlap slices")
        # This will be a flat list of (x, y) pairs for all modstates and beams
        flat_offsets = sum([list(i.values()) for i in self.state_offset.values()], [])
        # Split out into an x list and a y list
        all_x_shifts, all_y_shifts = zip(*flat_offsets)
        all_x_shifts = np.array(all_x_shifts)
        all_y_shifts = np.array(all_y_shifts)

        logger.info(f"All x shifts: {all_x_shifts}")
        logger.info(f"All y shifts: {all_y_shifts}")

        # The amount we need to "slice in" from the front of the array is simply the maximum positive shift
        # The call to `np.ceil` ensures that the integer rounding doesn't allow non-overlap regions to leak in.
        max_x = int(np.ceil(np.max(all_x_shifts)))
        max_y = int(np.ceil(np.max(all_y_shifts)))

        # The amount we need to "chop off" the end of the array is the most negative negative shift.
        #
        # Here we rely on the fact that the fiducial array's shift is *always* (0, 0)
        #  (see `geometric.compute_modstate_offset`). Thus, if there are no negative shifts then the following lines
        #  will result in None. This is required for slicing because array[x:0] is no good. So if the min is 0 then we
        #  end up with array[x:None] which goes all the way to the end of the array.
        #
        # The call to `np.floor` ensures that the integer rounding doesn't allow non-overlap regions to leak in.
        #  (because more negative slices will cut out more data).
        min_x = int(np.floor(np.min(all_x_shifts))) or None
        min_y = int(np.floor(np.min(all_y_shifts))) or None

        x_slice = slice(max_x, min_x)
        y_slice = slice(max_y, min_y)

        return x_slice, y_slice


class ScienceCalibration(
    VispTaskBase,
    BeamAccessMixin,
    CorrectionsMixin,
    QualityMixin,
):
    """
    Task class for Visp science calibration of polarized and non-polarized data.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of

    workflow_name : str
        name of the workflow to which this instance of the task belongs

    workflow_version : str
        version of the workflow to which this instance of the task belongs

    Returns
    -------
    None

    """

    record_provenance = True

    def run(self):
        """
        Run Visp science calibration.

        - Collect all calibration objects
        - Process all frames
        - Record quality metrics


        Returns
        -------
        None

        """
        with self.apm_task_step("Loading calibration objects"):
            calibrations = self.collect_calibration_objects()

        with self.apm_task_step(
            f"Processing Science Frames for "
            f"{self.constants.num_map_scans} map scans and "
            f"{self.constants.num_raster_steps} raster steps"
        ):
            self.process_frames(calibrations=calibrations)

        with self.apm_processing_step("Computing and logging quality metrics"):
            no_of_raw_science_frames: int = self.scratch.count_all(
                tags=[
                    VispTag.input(),
                    VispTag.frame(),
                    VispTag.task_observe(),
                ],
            )

            self.quality_store_task_type_counts(
                task_type=TaskName.observe.value, total_frames=no_of_raw_science_frames
            )

    def collect_calibration_objects(self) -> CalibrationCollection:
        """
        Collect *all* calibration for all beams, modstates, and exposure times.

        Doing this once here prevents lots of reads as we reduce the science data.
        """
        dark_dict = defaultdict(dict)
        background_dict = dict()
        solar_dict = defaultdict(dict)
        angle_dict = dict()
        state_offset_dict = defaultdict(dict)
        spec_shift_dict = dict()
        demod_dict = dict() if self.constants.correct_for_polarization else None

        for beam in range(1, self.constants.num_beams + 1):
            for readout_exp_time in self.constants.observe_readout_exp_times:
                # Dark
                ######
                dark_array = next(
                    self.read(
                        tags=VispTag.intermediate_frame_dark(
                            beam=beam, readout_exp_time=readout_exp_time
                        ),
                        decoder=fits_array_decoder,
                    )
                )

                dark_dict[VispTag.beam(beam)][
                    VispTag.readout_exp_time(readout_exp_time)
                ] = dark_array

            # Residual background light
            ###########################
            background_dict[VispTag.beam(beam)] = np.zeros(dark_array.shape)
            if self.constants.correct_for_polarization and self.parameters.background_on:
                background_generator = self.read(
                    tags=[VispTag.intermediate_frame(beam=beam), VispTag.task_background()],
                    decoder=fits_array_decoder,
                )
                background_dict[VispTag.beam(beam)] = next(background_generator)

            # Angle
            #######
            angle_array = next(
                self.read(
                    tags=[VispTag.intermediate_frame(beam=beam), VispTag.task_geometric_angle()],
                    decoder=fits_array_decoder,
                )
            )
            angle_dict[VispTag.beam(beam)] = angle_array[0]

            # Spec shifts
            #############
            spec_shift_dict[VispTag.beam(beam)] = next(
                self.read(
                    tags=[
                        VispTag.intermediate_frame(beam=beam),
                        VispTag.task_geometric_spectral_shifts(),
                    ],
                    decoder=fits_array_decoder,
                )
            )

            # Demod
            #######
            if self.constants.correct_for_polarization:
                demod_dict[VispTag.beam(beam)] = next(
                    self.read(
                        tags=[
                            VispTag.intermediate_frame(beam=beam),
                            VispTag.task_demodulation_matrices(),
                        ],
                        decoder=fits_array_decoder,
                    )
                )

            for modstate in range(1, self.constants.num_modstates + 1):
                # Solar
                #######
                solar_dict[VispTag.beam(beam)][VispTag.modstate(modstate)] = next(
                    self.read(
                        tags=[
                            VispTag.intermediate_frame(beam=beam, modstate=modstate),
                            VispTag.task_solar_gain(),
                        ],
                        decoder=fits_array_decoder,
                    )
                )

                # State Offset
                ##############
                state_offset_dict[VispTag.beam(beam)][VispTag.modstate(modstate)] = next(
                    self.read(
                        tags=[
                            VispTag.intermediate_frame(beam=beam, modstate=modstate),
                            VispTag.task_geometric_offset(),
                        ],
                        decoder=fits_array_decoder,
                    )
                )

        return CalibrationCollection(
            dark=dark_dict,
            background=background_dict,
            solar_gain=solar_dict,
            angle=angle_dict,
            state_offset=state_offset_dict,
            spec_shift=spec_shift_dict,
            demod_matrices=demod_dict,
        )

    def process_frames(self, calibrations: CalibrationCollection):
        """
        Completely calibrate all science frames.

        - Apply all dark, background, gain, geometric corrections
        - Demodulate if needed
        - Combine beams
        - Apply telescope correction, if needed
        - Write calibrated arrays
        """
        for readout_exp_time in self.constants.observe_readout_exp_times:
            for map_scan in range(1, self.constants.num_map_scans + 1):
                for raster_step in range(0, self.constants.num_raster_steps):
                    beam_storage = dict()
                    header_storage = dict()
                    for beam in range(1, self.constants.num_beams + 1):
                        apm_str = f"{map_scan = }, {raster_step = }, and {beam = }"
                        with self.apm_processing_step(f"Basic corrections for {apm_str}"):
                            # Initialize array_stack and headers
                            if self.constants.correct_for_polarization:
                                logger.info(
                                    f"Processing polarimetric observe frames from {apm_str}"
                                )
                                (
                                    intermediate_array,
                                    intermediate_header,
                                ) = self.process_polarimetric_modstates(
                                    beam=beam,
                                    raster_step=raster_step,
                                    map_scan=map_scan,
                                    readout_exp_time=readout_exp_time,
                                    calibrations=calibrations,
                                )
                            else:
                                logger.info(
                                    f"Processing spectrographic observe frames from {apm_str}"
                                )
                                intermediate_array, intermediate_header = self.correct_single_frame(
                                    beam=beam,
                                    modstate=1,
                                    raster_step=raster_step,
                                    map_scan=map_scan,
                                    readout_exp_time=readout_exp_time,
                                    calibrations=calibrations,
                                )
                                intermediate_header = self.compute_date_keys(intermediate_header)
                            beam_storage[VispTag.beam(beam)] = intermediate_array
                            header_storage[VispTag.beam(beam)] = intermediate_header

                    with self.apm_processing_step("Combining beams"):
                        calibrated = self.combine_beams(beam_storage, header_storage, calibrations)

                    if self.constants.correct_for_polarization:
                        with self.apm_processing_step("Correcting telescope polarization"):
                            calibrated = self.telescope_polarization_correction(calibrated)

                    # Save the final output files
                    with self.apm_writing_step("Writing calibrated arrays"):
                        self.write_calibrated_array(
                            calibrated, map_scan=map_scan, calibrations=calibrations
                        )

    def process_polarimetric_modstates(
        self,
        beam: int,
        raster_step: int,
        map_scan: int,
        readout_exp_time: float,
        calibrations: CalibrationCollection,
    ) -> tuple[np.ndarray, fits.Header]:
        """
        Process a single polarimetric beam as much as is possible.

        This includes basic corrections and demodulation. Beam combination happens elsewhere.
        """
        # Create the 3D stack of corrected modulated arrays
        array_shape = calibrations.dark[VispTag.beam(1)][
            VispTag.readout_exp_time(readout_exp_time)
        ].shape
        array_stack = np.zeros(array_shape + (self.constants.num_modstates,))
        header_stack = []

        with self.apm_processing_step(f"Correcting {self.constants.num_modstates} modstates"):
            for modstate in range(1, self.constants.num_modstates + 1):
                # Correct the arrays
                corrected_array, corrected_header = self.correct_single_frame(
                    beam=beam,
                    modstate=modstate,
                    raster_step=raster_step,
                    map_scan=map_scan,
                    readout_exp_time=readout_exp_time,
                    calibrations=calibrations,
                )
                # Add this result to the 3D stack
                array_stack[:, :, modstate - 1] = corrected_array
                header_stack.append(corrected_header)

        with self.apm_processing_step("Applying instrument polarization correction"):
            intermediate_array = nd_left_matrix_multiply(
                vector_stack=array_stack,
                matrix_stack=calibrations.demod_matrices[VispTag.beam(beam)],
            )
            intermediate_header = self.compute_date_keys(header_stack)

        return intermediate_array, intermediate_header

    def combine_beams(
        self,
        array_dict: dict[str, np.ndarray],
        header_dict: dict[str, fits.Header],
        calibrations: CalibrationCollection,
    ) -> VispL0FitsAccess:
        """
        Average all beams together and chop the resulting frame to just the region of overlap.

        Also complain if the inputs are strange.
        """
        headers = list(header_dict.values())
        if len(headers) == 0:
            raise ValueError("No headers provided")
        for h in headers[1:]:
            if fits.HeaderDiff(headers[0], h):
                raise ValueError("Headers are different! This should NEVER happen!")

        if self.constants.correct_for_polarization:
            avg_array = self.combine_polarimetric_beams(array_dict)
        else:
            avg_array = self.combine_spectrographic_beams(array_dict)

        x_slice, y_slice = calibrations.beams_overlap_slice
        logger.info(f"Trimming non-overlapping beam edges by ({x_slice}, {y_slice})")
        cut_array = avg_array[x_slice, y_slice]

        hdu = fits.ImageHDU(data=cut_array, header=headers[0])
        obj = VispL0FitsAccess(hdu=hdu, auto_squeeze=False)

        return obj

    def combine_polarimetric_beams(self, array_dict: dict[str, np.ndarray]) -> np.ndarray:
        """
        Combine polarimetric beams so that polarization states are normalized by the intensity state (Stokes I).

        In other words:

        avg_I = (beam1_I + beam2_I) / 2
        avg_Q = (beam1_Q / beam1_I + beam2_Q / beam2_I) / 2. * avg_I

        ...and the same for U and V
        """
        beam1_data = array_dict[VispTag.beam(1)]
        beam2_data = array_dict[VispTag.beam(2)]

        avg_data = np.zeros_like(beam1_data)
        # Rely on the fact that the Stokes states are in order after demodulation
        avg_I = (beam1_data[:, :, 0] + beam2_data[:, :, 0]) / 2.0
        avg_data[:, :, 0] = avg_I

        for stokes in range(1, 4):
            beam1_norm = beam1_data[:, :, stokes] / beam1_data[:, :, 0]
            beam2_norm = beam2_data[:, :, stokes] / beam2_data[:, :, 0]
            avg_data[:, :, stokes] = avg_I * (beam1_norm + beam2_norm) / 2.0

        return avg_data

    def combine_spectrographic_beams(self, array_dict: dict[str, np.ndarray]) -> np.ndarray:
        """Simply average the two beams together."""
        array_list = []
        for beam in range(1, self.constants.num_beams + 1):
            array_list.append(array_dict[VispTag.beam(beam)])

        avg_array = average_numpy_arrays(array_list)
        return avg_array

    def write_calibrated_array(
        self,
        calibrated_object: VispL0FitsAccess,
        map_scan: int,
        calibrations: CalibrationCollection,
    ) -> None:
        """
        Write out calibrated science frames.

        For polarized data, write out calibrated science frames for all 4 Stokes parameters.
        For non-polarized data, write out calibrated science frames for Stokes I only.

        Parameters
        ----------
        calibrated_object
            Corrected frames object

        map_scan
            The current map scan. Needed because it's not a header key

        calibrations
            Calibration collection

        Returns
        -------
        None

        """
        # We only need to compute the header once
        #  (In fact we *need* to only compute it once because we update WCS values in place and running this function
        #   more than once would result in incorrect WCS info).
        final_header = self.update_calibrated_header(
            calibrated_object.header, map_scan=map_scan, calibrations=calibrations
        )
        if self.constants.correct_for_polarization:  # Write all 4 stokes params
            stokes_I_data = calibrated_object.data[:, :, 0]
            for i, stokes_param in enumerate(self.constants.stokes_params):
                stokes_data = calibrated_object.data[:, :, i]
                final_data = self.re_dummy_data(stokes_data)
                pol_header = self.add_L1_pol_headers(final_header, stokes_data, stokes_I_data)
                self.write_cal_array(
                    data=final_data,
                    header=pol_header,
                    stokes=stokes_param,
                    raster_step=calibrated_object.raster_scan_step,
                    map_scan=map_scan,
                )
        else:  # Only write stokes I
            final_data = self.re_dummy_data(calibrated_object.data)
            self.write_cal_array(
                data=final_data,
                header=final_header,
                stokes="I",
                raster_step=calibrated_object.raster_scan_step,
                map_scan=map_scan,
            )

    def correct_single_frame(
        self,
        beam: int,
        modstate: int,
        raster_step: int,
        map_scan: int,
        readout_exp_time: float,
        calibrations: CalibrationCollection,
    ) -> tuple[np.ndarray, fits.Header]:
        """
        Apply basic corrections to a single frame.

        Generally the algorithm is:
            1. Dark correct the array
            2. Background correct the array
            3. Solar Gain correct the array
            4. Geo correct the array
            5. Spectral correct array

        Parameters
        ----------
        beam
            The beam number for this single step

        modstate
            The modulator state for this single step

        raster_step
            The slit step for this single step

        map_scan
            The current map scan

        readout_exp_time
            The exposure time for this single step

        calibrations
            Collection of all calibration objects


        Returns
        -------
        tuple[np.ndarray, fits.Header]
            Corrected array, header
        """
        # Extract calibrations
        dark_array = calibrations.dark[VispTag.beam(beam)][
            VispTag.readout_exp_time(readout_exp_time)
        ]
        background_array = calibrations.background[VispTag.beam(beam)]
        solar_gain_array = calibrations.solar_gain[VispTag.beam(beam)][VispTag.modstate(modstate)]
        angle = calibrations.angle[VispTag.beam(beam)]
        spec_shift = calibrations.spec_shift[VispTag.beam(beam)]
        state_offset = calibrations.state_offset[VispTag.beam(beam)][VispTag.modstate(modstate)]

        # Grab the input observe frame
        tags = [
            VispTag.input(),
            VispTag.frame(),
            VispTag.task_observe(),
            VispTag.modstate(modstate),
            VispTag.map_scan(map_scan),
            VispTag.raster_step(raster_step),
            VispTag.readout_exp_time(readout_exp_time),
        ]
        observe_object_list = list(
            self.read(tags=tags, decoder=fits_access_decoder, fits_access_class=VispL0FitsAccess)
        )

        if len(observe_object_list) > 1:
            raise ValueError(
                f"Found more than one observe frame for {map_scan = }, {raster_step = }, {modstate = }, "
                f"and {readout_exp_time = }. This should NEVER have happened!"
            )
        observe_object = observe_object_list[0]

        # Split the beam we want
        readout_normalized_data = observe_object.data / observe_object.num_raw_frames_per_fpa
        observe_data = self.beam_access_get_beam(readout_normalized_data, beam=beam)

        # Dark correction
        dark_corrected_array = next(subtract_array_from_arrays(observe_data, dark_array))

        # Residual background correction
        background_corrected_array = next(
            subtract_array_from_arrays(dark_corrected_array, background_array)
        )

        # Solar gain correction
        solar_corrected_array = next(
            divide_arrays_by_array(background_corrected_array, solar_gain_array)
        )

        # Geo correction
        geo_corrected_array = next(
            self.corrections_correct_geometry(solar_corrected_array, state_offset, angle)
        )

        # Geo correction pt 2: spectral curvature
        spectral_corrected_array = next(
            self.corrections_remove_spec_geometry(geo_corrected_array, spec_shift)
        )

        return spectral_corrected_array, observe_object.header

    def telescope_polarization_correction(
        self,
        inst_demod_obj: VispL0FitsAccess,
    ) -> VispL0FitsAccess:
        """
        Apply a telescope polarization correction.

        Parameters
        ----------
        inst_demod_obj
            A demodulated, beam averaged frame

        Returns
        -------
        FitsAccess object with telescope corrections applied

        """
        tm = Telescope.from_fits_access(inst_demod_obj)
        mueller_matrix = tm.generate_inverse_telescope_model(
            M12=True, rotate_to_fixed_SDO_HINODE_polarized_frame=True, swap_UV_signs=True
        )
        inst_demod_obj.data = nd_left_matrix_multiply(
            vector_stack=inst_demod_obj.data, matrix_stack=mueller_matrix
        )
        return inst_demod_obj

    @staticmethod
    def compute_date_keys(headers: Iterable[fits.Header] | fits.Header) -> fits.Header:
        """
        Generate correct DATE-??? header keys from a set of input headers.

        Keys are computed thusly:
        * DATE-BEG - The (Spec-0122) DATE-OBS of the earliest input header
        * DATE-END - The (Spec-0122) DATE-OBS of the latest input header, plus the FPA exposure time

        Parameters
        ----------
        headers : Iterable[fits.Header] | fits.Header
            Headers

        Returns
        -------
        fits.Header
            A copy of the earliest header, but with correct DATE-??? keys
        """
        if isinstance(headers, fits.Header) or isinstance(
            headers, fits.hdu.compressed.CompImageHeader
        ):
            headers = [headers]

        sorted_obj_list = sorted(
            [VispL0FitsAccess.from_header(h) for h in headers], key=lambda x: Time(x.time_obs)
        )
        date_beg = sorted_obj_list[0].time_obs
        exp_time = TimeDelta(sorted_obj_list[-1].fpa_exposure_time_ms / 1000.0, format="sec")
        date_end = (Time(sorted_obj_list[-1].time_obs) + exp_time).isot

        header = sorted_obj_list[0].header
        header["DATE-BEG"] = date_beg
        header["DATE-END"] = date_end

        return header

    def re_dummy_data(self, data: np.ndarray):
        """
        Add the dummy dimension that we have been secretly squeezing out during processing.

        The dummy dimension is required because its corresponding WCS axis contains important information.

        Parameters
        ----------
        data : np.ndarray
            Corrected data

        Returns
        -------
        None

        """
        return data[None, :, :]

    def update_calibrated_header(
        self, header: fits.Header, map_scan: int, calibrations: CalibrationCollection
    ) -> fits.Header:
        """
        Update calibrated headers with any information gleaned during science calibration.

        Right now all this does is put map scan values in the header.

        Parameters
        ----------
        header : fits.Header
            The header to update

        map_scan : int
            Current map scan

        Returns
        -------
        fits.Header
            Updated header

        """
        # Update the map scan number
        header["VSPNMAPS"] = self.constants.num_map_scans
        header["VSPMAP"] = map_scan

        # Adjust the CRPIX values if the beam overlap slicing chopped from the start of the array
        x_slice, y_slice = calibrations.beams_overlap_slice

        # This if catches 0's and Nones
        if x_slice.start:
            # .start will only be non-None or 0 if the slice is from the start. In this case we need to update the WCS
            logger.info(
                f"Adjusting CRPIX2 from {header['CRPIX2']} to {header['CRPIX2'] - x_slice.start}"
            )
            header["CRPIX2"] = header["CRPIX2"] - x_slice.start
            logger.info(
                f"Adjusting CRPIX2A from {header['CRPIX2A']} to {header['CRPIX2A'] - x_slice.start}"
            )
            header["CRPIX2A"] = header["CRPIX2A"] - x_slice.start

        if y_slice.start:
            logger.info(
                f"Adjusting CRPIX1 from {header['CRPIX1']} to {header['CRPIX1'] - y_slice.start}"
            )
            header["CRPIX1"] = header["CRPIX1"] - y_slice.start
            logger.info(
                f"Adjusting CRPIX1A from {header['CRPIX1A']} to {header['CRPIX1A'] - y_slice.start}"
            )
            header["CRPIX1A"] = header["CRPIX1A"] - y_slice.start

        return header

    def add_L1_pol_headers(
        self, input_header: fits.Header, stokes_data: np.ndarray, stokes_I_data: np.ndarray
    ) -> fits.Header:
        """Compute and add 214 header values specific to polarimetric datasets."""
        # Probably not needed, but just to be safe
        output_header = input_header.copy()

        pol_noise = self.compute_polarimetric_noise(stokes_data, stokes_I_data)
        pol_sensitivity = self.compute_polarimetric_sensitivity(stokes_I_data)
        output_header["POL_NOIS"] = pol_noise
        output_header["POL_SENS"] = pol_sensitivity

        return output_header

    def compute_polarimetric_noise(
        self, stokes_data: np.ndarray, stokes_I_data: np.ndarray
    ) -> float:
        r"""
        Compute the polarimetric noise for a single frame.

        The polarimetric noise, :math:`N`, is defined as

        .. math::

            N = stddev(\frac{F_i}{F_I})

        where :math:`F_i` is a full array of values for Stokes parameter :math:`i` (I, Q, U, V), and :math:`F_I` is the
        full frame of Stokes-I. The stddev is computed across the entire frame.
        """
        return float(np.nanstd(stokes_data / stokes_I_data))

    def compute_polarimetric_sensitivity(self, stokes_I_data: np.ndarray) -> float:
        r"""
        Compute the polarimetric sensitivity for a single frame.

        The polarimetric sensitivity is the smallest signal that can be measured based on the values in the Stokes-I
        frame. The sensitivity, :math:`S`, is computed as

        .. math::

            S = \frac{1}{\sqrt{\mathrm{max}(F_I)}}

        where :math:`F_I` is the full frame of values for Stokes-I.
        """
        return float(1.0 / np.sqrt(np.nanmax(stokes_I_data)))

    def write_cal_array(
        self,
        data: np.ndarray,
        header: fits.Header,
        stokes: str,
        raster_step: int,
        map_scan: int,
    ) -> None:
        """
        Write out calibrated array.

        Parameters
        ----------
        data : np.ndarray
            calibrated data to write out

        header : fits.Header
            calibrated header to write out

        stokes : str
            Stokes parameter of this step. 'I', 'Q', 'U', or 'V'

        raster_step : int
            The slit step for this step

        map_scan : int
            The current map scan


        Returns
        -------
        None

        """
        tags = [
            VispTag.calibrated(),
            VispTag.frame(),
            VispTag.stokes(stokes),
            VispTag.raster_step(raster_step),
            VispTag.map_scan(map_scan),
        ]
        hdul = fits.HDUList([fits.PrimaryHDU(), fits.CompImageHDU(header=header, data=data)])
        self.write(data=hdul, tags=tags, encoder=fits_hdulist_encoder)

        filename = next(self.read(tags=tags))
        logger.info(f"Wrote intermediate file for {tags = } to {filename}")
