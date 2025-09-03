"""Visp write L1 task."""

from functools import cache
from typing import Literal

import astropy.units as u
from astropy.io import fits
from dkist_processing_common.tasks import WriteL1Frame
from dkist_processing_common.tasks.write_l1 import WavelengthRange
from dkist_service_configuration.logging import logger

from dkist_processing_visp.models.constants import VispConstants

cached_info_logger = cache(logger.info)
__all__ = ["VispWriteL1Frame"]


class VispWriteL1Frame(WriteL1Frame):
    """
    Task class for writing out calibrated l1 ViSP frames.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs
    """

    @property
    def constants_model_class(self):
        """Get Visp pipeline constants."""
        return VispConstants

    def add_dataset_headers(
        self, header: fits.Header, stokes: Literal["I", "Q", "U", "V"]
    ) -> fits.Header:
        """
        Add the VISP specific dataset headers to L1 FITS files.

        Parameters
        ----------
        header : fits.Header
            calibrated data header

        stokes :
            stokes parameter

        Returns
        -------
        fits.Header
            calibrated header with correctly written l1 headers
        """
        # Correct the headers for the number of map and scan steps per map due to potential observation aborts
        header["VSPNMAPS"] = self.constants.num_map_scans
        header["VSPNSTP"] = self.constants.num_raster_steps

        if stokes.upper() not in self.constants.stokes_params:
            raise ValueError("The stokes parameter must be one of I, Q, U, V")

        # Dynamically assign dataset axes based on CTYPEs in the L0 headers
        axis_types = [
            self.constants.axis_1_type,
            self.constants.axis_2_type,
            self.constants.axis_3_type,
        ]
        for i, axis_type in enumerate(axis_types, start=1):
            if axis_type == "HPLT-TAN":
                header[f"DNAXIS{i}"] = header[f"NAXIS{i}"]
                header[f"DTYPE{i}"] = "SPATIAL"
                header[f"DPNAME{i}"] = "spatial along slit"
                header[f"DWNAME{i}"] = "helioprojective latitude"
                if i < header["NAXIS"]:
                    header[f"CNAME{i}"] = "helioprojective latitude"
                header[f"DUNIT{i}"] = header[f"CUNIT{i}"]
            elif axis_type == "AWAV":
                header[f"DNAXIS{i}"] = header[f"NAXIS{i}"]
                header[f"DTYPE{i}"] = "SPECTRAL"
                header[f"DPNAME{i}"] = "dispersion axis"
                header[f"DWNAME{i}"] = "wavelength"
                if i < header["NAXIS"]:
                    header[f"CNAME{i}"] = "wavelength"
                header[f"DUNIT{i}"] = header[f"CUNIT{i}"]
            elif axis_type == "HPLN-TAN":
                header[f"DNAXIS{i}"] = self.constants.num_raster_steps
                header[f"DTYPE{i}"] = "SPATIAL"
                header[f"DPNAME{i}"] = "raster scan step number"
                header[f"DWNAME{i}"] = "helioprojective longitude"
                if i < header["NAXIS"]:
                    header[f"CNAME{i}"] = "helioprojective longitude"
                header[f"DUNIT{i}"] = header[f"CUNIT{i}"]
                # Current position in raster scan which counts from zero
                header[f"DINDEX{i}"] = header["VSPSTP"] + 1
            else:
                raise ValueError(
                    f"Unexpected axis type. Expected ['HPLT-TAN', 'AWAV', 'HPLN-TAN']. Got {axis_type}"
                )

        # Set the base number of dataset axes to 3
        num_axis = 3

        # ---Temporal---
        if self.constants.num_map_scans > 1:
            cached_info_logger("Adding map scan dataset axis")
            num_axis += 1
            header[f"DNAXIS{num_axis}"] = (
                self.constants.num_map_scans
            )  # total number of raster scans in the dataset
            header[f"DTYPE{num_axis}"] = "TEMPORAL"
            header[f"DPNAME{num_axis}"] = "raster map repeat number"
            header[f"DWNAME{num_axis}"] = "time"
            if num_axis < header["NAXIS"]:
                header[f"CNAME{num_axis}"] = "time"
            header[f"DUNIT{num_axis}"] = "s"
            # Temporal position in dataset
            header[f"DINDEX{num_axis}"] = header["VSPMAP"]  # Current raster scan

        # ---Stokes---
        if self.constants.correct_for_polarization:
            cached_info_logger("Adding Stokes dataset axis")
            num_axis += 1
            header[f"DNAXIS{num_axis}"] = 4  # I, Q, U, V
            header[f"DTYPE{num_axis}"] = "STOKES"
            header[f"DPNAME{num_axis}"] = "polarization state"
            header[f"DWNAME{num_axis}"] = "polarization state"
            if num_axis < header["NAXIS"]:
                header[f"CNAME{num_axis}"] = "polarization state"
            header[f"DUNIT{num_axis}"] = ""
            # Stokes position in dataset - stokes axis goes from 1-4
            header[f"DINDEX{num_axis}"] = self.constants.stokes_params.index(stokes.upper()) + 1

        header["DNAXIS"] = num_axis
        header["DAAXES"] = 2  # Spectral, spatial
        header["DEAXES"] = num_axis - 2  # Total - detector axes

        # VISP has a wavelength axis in the frame and so FRAMEWAV is hard to define. Use LINEWAV.
        header["LEVEL"] = 1
        header["WAVEUNIT"] = -9  # nanometers
        header["WAVEREF"] = "Air"

        # Binning headers
        header["NBIN1"] = 1
        header["NBIN2"] = 1
        header["NBIN3"] = 1
        header["NBIN"] = header["NBIN1"] * header["NBIN2"] * header["NBIN3"]

        # Values don't have any units because they are relative to disk center
        header["BUNIT"] = ("", "Values are relative to disk center. See calibration docs.")

        return header

    def calculate_date_end(self, header: fits.Header) -> str:
        """
        In VISP, the instrument specific DATE-END keyword is calculated during science calibration.

        Check that it exists.

        Parameters
        ----------
        header
            The input fits header
        """
        try:
            return header["DATE-END"]
        except KeyError:
            raise KeyError(
                f"The 'DATE-END' keyword was not found. "
                f"Was supposed to be inserted during science calibration."
            )

    def get_wavelength_range(self, header: fits.Header) -> WavelengthRange:
        """
        Return the wavelength range of this frame.

        Range is the wavelength values of the pixels at the ends of the wavelength axis.
        """
        axis_types = [
            self.constants.axis_1_type,
            self.constants.axis_2_type,
            self.constants.axis_3_type,
        ]
        wavelength_axis = axis_types.index("AWAV") + 1  # FITS axis numbering is 1-based, not 0
        wavelength_unit = header[f"CUNIT{wavelength_axis}"]
        minimum = header[f"CRVAL{wavelength_axis}"] - (
            header[f"CRPIX{wavelength_axis}"] * header[f"CDELT{wavelength_axis}"]
        )
        maximum = header[f"CRVAL{wavelength_axis}"] + (
            (header[f"NAXIS{wavelength_axis}"] - header[f"CRPIX{wavelength_axis}"])
            * header[f"CDELT{wavelength_axis}"]
        )
        return WavelengthRange(
            min=u.Quantity(minimum, unit=wavelength_unit),
            max=u.Quantity(maximum, unit=wavelength_unit),
        )

    def add_timing_headers(self, header: fits.Header) -> fits.Header:
        """
        Add timing headers to the FITS header.

        This method adds or updates headers related to frame timings.
        """
        # The source data is based on L0 data but L1 data takes L0 cadence * modstates to obtain.
        # This causes both the cadence and the full exposure time to be num_modstates times longer.
        header["CADENCE"] = self.constants.average_cadence * self.constants.num_modstates
        header["CADMIN"] = self.constants.minimum_cadence * self.constants.num_modstates
        header["CADMAX"] = self.constants.maximum_cadence * self.constants.num_modstates
        header["CADVAR"] = self.constants.variance_cadence * self.constants.num_modstates
        header["XPOSURE"] = header["XPOSURE"] * self.constants.num_modstates
        return header
