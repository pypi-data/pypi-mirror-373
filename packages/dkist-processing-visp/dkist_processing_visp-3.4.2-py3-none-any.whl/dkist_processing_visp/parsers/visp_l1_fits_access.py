"""ViSP FITS access for L1 data."""

from astropy.io import fits
from dkist_processing_common.parsers.l1_fits_access import L1FitsAccess


class VispL1FitsAccess(L1FitsAccess):
    """
    Class to provide easy access to L1 headers.

    i.e. instead of <VispL1FitsAccess>.header['key'] this class lets us use <VispL1FitsAccess>.key instead

    Parameters
    ----------
    hdu :
        Fits L1 header object

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
