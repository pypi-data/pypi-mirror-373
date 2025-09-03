"""VBI FITS access for L0 data."""

from astropy.io import fits
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess


class VbiL0FitsAccess(L0FitsAccess):
    """
    Class to provide easy access to L0 headers.

    i.e. instead of <VbiL0FitsAccess>.header['key'] this class lets us use <VbiL0FitsAccess>.key instead

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

        self.spatial_step_pattern: str = self.header["VBISTPAT"]
        self.number_of_spatial_steps: int = self.header.get("VBINSTP")
        self.current_spatial_step: int = self.header.get("VBISTP")
        self.number_of_exp_per_mosaic_step: int = self.header.get("VBINFRAM")
        self.current_mosaic_step_exp: int = self.header.get("VBICFRAM")
