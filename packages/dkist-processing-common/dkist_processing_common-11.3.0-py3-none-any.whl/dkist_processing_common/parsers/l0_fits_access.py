"""By-frame 214 L0 header keywords that are not instrument specific."""

from astropy.io import fits

from dkist_processing_common.parsers.l1_fits_access import L1FitsAccess


class L0FitsAccess(L1FitsAccess):
    """
    Class defining a fits access object for L0 input data.

    Parameters
    ----------
    hdu
        The input fits hdu
    name
        An optional name to be associated with the hdu
    auto_squeeze
        A boolean indicating whether to 'squeeze' out dimensions of size 1
    """

    def __init__(
        self,
        hdu: fits.ImageHDU | fits.PrimaryHDU | fits.CompImageHDU,
        name: str | None = None,
        auto_squeeze: bool = True,
    ):
        super().__init__(hdu=hdu, name=name, auto_squeeze=auto_squeeze)
        self.ip_task_type: str = self.header["IPTASK"]
        self.ip_start_time: str = self.header["DKIST011"]
        self.ip_end_time: str = self.header["DKIST012"]
