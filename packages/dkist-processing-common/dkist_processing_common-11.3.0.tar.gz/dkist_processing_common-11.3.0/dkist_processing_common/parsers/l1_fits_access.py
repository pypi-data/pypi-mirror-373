"""By-frame 214 L1 only header keywords that are not instrument specific."""

from astropy.io import fits

from dkist_processing_common.models.fits_access import FitsAccessBase


class L1FitsAccess(FitsAccessBase):
    """
    Class defining a fits access object for processed L1 data.

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
        auto_squeeze: bool = False,  # Because L1 data should always have the right form, right?
    ):
        super().__init__(hdu=hdu, name=name, auto_squeeze=auto_squeeze)

        self.elevation: float = self.header["ELEV_ANG"]
        self.azimuth: float = self.header["TAZIMUTH"]
        self.table_angle: float = self.header["TTBLANGL"]
        self.gos_level3_status: str = self.header["LVL3STAT"]
        self.gos_level3_lamp_status: str = self.header["LAMPSTAT"]
        self.gos_polarizer_status: str = self.header["LVL2STAT"]
        self.gos_retarder_status: str = self.header["LVL1STAT"]
        self.gos_level0_status: str = self.header["LVL0STAT"]
        self.time_obs: str = self.header["DATE-BEG"]
        self.ip_id: str = self.header["IP_ID"]
        self.instrument: str = self.header["INSTRUME"]
        self.wavelength: float = self.header["LINEWAV"]
        self.proposal_id: str = self.header["PROP_ID"]
        self.experiment_id: str = self.header["EXPER_ID"]
        self.num_dsps_repeats: int = self.header["DSPSREPS"]
        self.current_dsps_repeat: int = self.header["DSPSNUM"]
        self.fpa_exposure_time_ms: float = self.header["XPOSURE"]
        self.sensor_readout_exposure_time_ms: float = self.header["TEXPOSUR"]
        self.num_raw_frames_per_fpa: int = self.header["NSUMEXP"]

    @property
    def gos_polarizer_angle(self) -> float:
        """Convert the polarizer angle to a float if possible before returning."""
        try:
            return float(self.header["POLANGLE"])
        except ValueError:
            return -999  # The angle is only used if the polarizer is in the beam

    @property
    def gos_retarder_angle(self) -> float:
        """Convert the retarder angle to a float if possible before returning."""
        try:
            return float(self.header["RETANGLE"])
        except ValueError:
            return -999  # The angle is only used if the retarder is in the beam
