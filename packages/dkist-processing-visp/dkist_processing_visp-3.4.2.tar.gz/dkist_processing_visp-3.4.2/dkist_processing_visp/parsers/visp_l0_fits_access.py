"""ViSP FITS access for L0 data."""

from astropy.io import fits
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess


class VispL0FitsAccess(L0FitsAccess):
    """
    Class to provide easy access to L0 headers.

    i.e. instead of <VispL0FitsAccess>.header['key'] this class lets us use <VispL0FitsAccess>.key instead

    Parameters
    ----------
    hdu :
        Fits L0 header object

    name : str
        The name of the file that was loaded into this FitsAccess object

    auto_squeeze : bool
        When set to True, dimensions of length 1 will be removed from the array
    """

    def __init__(
        self,
        hdu: fits.ImageHDU | fits.PrimaryHDU | fits.CompImageHDU,
        name: str | None = None,
        auto_squeeze: bool = True,
    ):
        super().__init__(hdu=hdu, name=name, auto_squeeze=auto_squeeze)

        self.number_of_modulator_states: int = self.header["VSPNUMST"]
        self.raster_scan_step: int = self.header["VSPSTP"]
        self.total_raster_steps: int = self.header["VSPNSTP"]
        self.modulator_state: int = self.header["VSPSTNUM"]
        self.polarimeter_mode: str = self.header["VISP_006"]
        self.axis_1_type: str = self.header["CTYPE1"]
        self.axis_2_type: str = self.header["CTYPE2"]
        self.axis_3_type: str = self.header["CTYPE3"]
