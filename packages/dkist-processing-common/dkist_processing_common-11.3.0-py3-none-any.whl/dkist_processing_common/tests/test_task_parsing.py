import pytest
from astropy.io import fits

from dkist_processing_common.models.fits_access import FitsAccessBase
from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.parsers.task import parse_header_ip_task_with_gains
from dkist_processing_common.parsers.task import parse_polcal_task_type
from dkist_processing_common.parsers.task import passthrough_header_ip_task


class DummyFitsAccess(FitsAccessBase):
    def __init__(
        self,
        hdu: fits.ImageHDU | fits.PrimaryHDU | fits.CompImageHDU,
        name: str | None = None,
        auto_squeeze: bool = False,  # Because L1 data should always have the right form, right?
    ):
        super().__init__(hdu=hdu, name=name, auto_squeeze=auto_squeeze)

        self.ip_task_type: str = self.header["IPTASK"]
        self.gos_level3_status: str = self.header["GOSLVL3"]
        self.gos_level3_lamp_status: str = self.header["GOSLAMP"]
        self.gos_level0_status: str = self.header["GOSLVL0"]
        self.gos_retarder_status: str = self.header["GOSRET"]
        self.gos_polarizer_status: str = self.header["GOSPOL"]


@pytest.fixture
def full_header() -> dict:
    # Because the DummyFitsAccess needs all of these keys to be present even if they're not used.
    return {
        "IPTASK": "_",
        "GOSLVL3": "_",
        "GOSLAMP": "_",
        "GOSLVL0": "_",
        "GOSRET": "_",
        "GOSPOL": "_",
    }


@pytest.fixture
def fits_obj_with_task_type(full_header):
    task = "A_TASK"
    header = full_header | {"IPTASK": task}
    return DummyFitsAccess.from_header(header), task


@pytest.fixture
def lamp_gain_fits_object(full_header):
    header = full_header | {"IPTASK": "gain", "GOSLVL3": "lamp", "GOSLAMP": "on"}
    return DummyFitsAccess.from_header(header)


@pytest.fixture
def solar_gain_fits_object(full_header):
    header = full_header | {"IPTASK": "gain", "GOSLVL3": "clear"}
    return DummyFitsAccess.from_header(header)


@pytest.fixture
def polcal_dark_fits_object(full_header):
    header = full_header | {"GOSLVL0": "DarkShutter", "GOSRET": "clear", "GOSPOL": "clear"}
    return DummyFitsAccess.from_header(header)


@pytest.fixture
def polcal_gain_fits_object(full_header):
    header = full_header | {"GOSLVL0": "FieldStop", "GOSRET": "clear", "GOSPOL": "clear"}
    return DummyFitsAccess.from_header(header)


def test_passthrough_header_ip_task(fits_obj_with_task_type):
    """
    Given: A FitsAccess object with an ip task type property
    When: Parsing the object with the default parser
    Then: The raw task from the header is returned
    """
    fits_obj, task = fits_obj_with_task_type

    assert passthrough_header_ip_task(fits_obj) == task


def test_parse_header_ip_task_with_gains(
    fits_obj_with_task_type, lamp_gain_fits_object, solar_gain_fits_object
):
    """
    Given: FitsAccesss object with the combination of header values indicating lamp or solar gain
    When: Parsing the objects with the gain parser
    Then: The correct task type is returned
    """
    fits_obj, task = fits_obj_with_task_type
    assert parse_header_ip_task_with_gains(fits_obj) == task
    assert parse_header_ip_task_with_gains(lamp_gain_fits_object) == TaskName.lamp_gain.value
    assert parse_header_ip_task_with_gains(solar_gain_fits_object) == TaskName.solar_gain.value


def test_parse_polcal_task_type(
    fits_obj_with_task_type, polcal_dark_fits_object, polcal_gain_fits_object
):
    """
    Given: FitsAccess objects with the combination of header values indicating polcal darks or gains
    When: Parsing the objects with the polcal task parser
    Then: The correct task type (or SpilledDirt) is returned
    """
    fits_obj, _ = fits_obj_with_task_type
    assert parse_polcal_task_type(fits_obj) is SpilledDirt
    assert parse_polcal_task_type(polcal_dark_fits_object) == TaskName.polcal_dark.value
    assert parse_polcal_task_type(polcal_gain_fits_object) == TaskName.polcal_gain.value
