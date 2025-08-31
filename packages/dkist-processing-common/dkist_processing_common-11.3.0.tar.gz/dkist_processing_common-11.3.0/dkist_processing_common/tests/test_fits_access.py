import numpy as np
import pytest
from astropy.io import fits

from dkist_processing_common.models.fits_access import FitsAccessBase
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess
from dkist_processing_common.parsers.l1_fits_access import L1FitsAccess


@pytest.fixture()
def hdu_with_complete_common_header(complete_common_header):
    """
    An HDU with data and a header with some common by-frame keywords and a single instrument
    specific one.
    """
    data = np.arange(9).reshape(3, 3)
    hdu = fits.PrimaryHDU(data, header=complete_common_header)
    return hdu


@pytest.fixture(params=["history", "comment", "continue"])
def hdu_with_special_keys(hdu_with_complete_common_header, request):
    """
    An HDU with data and a header that includes variations on the special keys that make headers
    different from dicts.

    The base complete_common_header already has history and comment cards so this fixture adds extras.
    """
    add_special = request.param
    hdu = hdu_with_complete_common_header
    if add_special == "history":
        hdu.header.add_history("test history")
        return hdu, request.param
    if add_special == "comment":
        hdu.header.add_comment("test comment")
        return hdu, request.param
    if add_special == "continue":
        hdu.header["LONG_VAL"] = " " * 100
        return hdu, request.param


@pytest.fixture()
def hdu_with_complete_l1_only_header(complete_l1_only_header):
    """
    An HDU with data and a header that contains ONLY 214 L1 keys
    """
    data = np.arange(9).reshape(3, 3)
    hdu = fits.CompImageHDU(data=data, header=complete_l1_only_header)

    return hdu


@pytest.fixture()
def extra_axis_hdu_with_complete_common_header(complete_common_header):
    """
    An HDU with data and a header with some common by-frame keywords and a single instrument
    specific one. Also contains an axis of length 1 in the data array
    """
    data = np.ones(shape=(1, 3, 3))
    hdu = fits.PrimaryHDU(data, header=complete_common_header)
    return hdu


@pytest.fixture()
def singleton_axis_hdu_with_complete_common_header(complete_common_header):
    """
    An HDU with data and a header with some common by-frame keywords and a single instrument
    specific one. Also contains an axis of length 1 in the data array
    """
    data = np.ones(shape=(1, 3))
    hdu = fits.PrimaryHDU(data, header=complete_common_header)
    return hdu


@pytest.fixture()
def three_singleton_axes_hdu(complete_common_header):
    """
    An HDU with data and a full header. The data has three dimensions but only a single value
    """
    data = np.ones(shape=(1, 1, 1))
    hdu = fits.PrimaryHDU(data, header=complete_common_header)
    return hdu


@pytest.fixture()
def hdu_with_no_data(complete_common_header):
    """
    An HDU with data and a header with some common by-frame keywords and a single instrument
    specific one.  No data is included in any HDUs.
    """
    hdu = fits.PrimaryHDU(header=complete_common_header)
    return hdu


@pytest.fixture()
def hdu_with_incomplete_common_header(tmp_path):
    """
    An HDU with data and a header missing one of the expected common by-frame keywords
    """
    data = np.arange(9).reshape(3, 3)
    hdu = fits.PrimaryHDU(data)
    hdu.header["TELEVATN"] = 6.28
    hdu.header["TAZIMUTH"] = 3.14
    return hdu


@pytest.fixture()
def fits_file_path(tmp_path, complete_common_header):
    file_path = tmp_path / "foo.fits"
    data = np.arange(9).reshape(3, 3)
    hdu = fits.PrimaryHDU(data, header=complete_common_header)
    hdu.header["INSTRUME"] = "foo"
    hdu.writeto(file_path)

    return file_path


@pytest.fixture()
def fits_file_path_with_data_in_imagehdu(tmp_path, complete_common_header):
    file_path = tmp_path / "foo.fits"
    data = np.arange(9).reshape(3, 3)
    hdu = fits.ImageHDU(data, header=complete_common_header)
    hdu.header["INSTRUME"] = "foo"
    hdul = fits.HDUList([fits.PrimaryHDU(), hdu])
    hdul.writeto(file_path)

    return file_path


class FitsAccessWithNaxisKeys(FitsAccessBase):
    def __init__(self, hdu, name):
        super().__init__(hdu, name)
        self.naxis = self.header["NAXIS"]
        self.naxis1 = self.header["NAXIS1"]
        self.naxis2 = self.header["NAXIS2"]


def test_from_single_hdu(hdu_with_complete_common_header):
    """
    Given: an HDU with expected, common by-frame keywords
    When: loading the HDU with the L0FitsAccess class
    Then: all values for common keywords are exposed as properties on the fits_obj class
    """
    fits_obj = L0FitsAccess(hdu_with_complete_common_header)
    assert fits_obj.elevation == 6.28
    assert fits_obj.azimuth == 3.14
    assert fits_obj.table_angle == 1.23
    assert fits_obj.time_obs == "2020-01-02T00:00:00.000000"
    assert fits_obj.name is None
    np.testing.assert_equal(fits_obj.data, np.arange(9).reshape(3, 3))


def test_l1_only_fits_access(hdu_with_complete_l1_only_header):
    """
    Given: an HDU with 214 L1-only headers
    When: loading the HDU with the L1FitsAccess class
    Then: no errors are raised and all values are exposed
    """
    fits_obj = L1FitsAccess(hdu_with_complete_l1_only_header)
    assert fits_obj.elevation == 6.28
    assert fits_obj.azimuth == 3.14
    assert fits_obj.table_angle == 1.23
    assert fits_obj.time_obs == "2020-01-02T00:00:00.000000"
    assert fits_obj.name is None
    np.testing.assert_equal(fits_obj.data, np.arange(9).reshape(3, 3))


def test_from_header(hdu_with_complete_common_header):
    """
    Given: an HDU with expected, common by-frame keywords
    When: constructing a L0FitsAccess object via the .from_header method
    Then: all values for common keywords are exposed as properties on the fits_obj class
    """
    fits_obj = L0FitsAccess.from_header(hdu_with_complete_common_header.header)
    assert fits_obj.elevation == 6.28
    assert fits_obj.azimuth == 3.14
    assert fits_obj.table_angle == 1.23
    assert fits_obj.time_obs == "2020-01-02T00:00:00.000000"
    assert fits_obj.name is None


def test_from_path(fits_file_path):
    """
    Give: a path that points to a valid fits file
    When: initializing a FitsAccess object with the path
    Then: a correct object is returned
    """
    fits_obj = L0FitsAccess.from_path(fits_file_path)
    np.testing.assert_equal(fits_obj.data, np.arange(9).reshape(3, 3))
    assert fits_obj.instrument == "foo"


def test_from_path_with_imagehdu(fits_file_path_with_data_in_imagehdu):
    """
    Give: a path that points to a valid fits file with data not in the PrimaryHDU
    When: initializing a FitsAccess object with the path
    Then: a correct object is returned
    """
    fits_obj = L0FitsAccess.from_path(fits_file_path_with_data_in_imagehdu)
    np.testing.assert_equal(fits_obj.data, np.arange(9).reshape(3, 3))
    assert fits_obj.instrument == "foo"


def test_no_header_value(hdu_with_incomplete_common_header):
    """
    Given: an HDU with a header with missing common by-frame keywords
    When: processing the HDU with the L0FitsAccess class
    Then: a KeyError is raised
    """
    with pytest.raises(KeyError):
        _ = L0FitsAccess(hdu_with_incomplete_common_header)


def test_as_subclass(hdu_with_complete_common_header):
    """
    Given: an instrument-specific fits_obj class that subclasses L0FitsAccess
    When: processing a HDU with instrument-specific keywords
    Then: both the common and instrument specific keywords values are available as properties in the
    derived class
    """

    class InstFitsAccess(L0FitsAccess):
        def __init__(self, hdu, name):
            super().__init__(hdu, name)
            self.foo: str = self.header["VISP_012"]

    fits_obj = InstFitsAccess(hdu_with_complete_common_header, name="foo")
    assert fits_obj.foo == "bar"
    assert fits_obj.elevation == 6.28
    assert fits_obj.azimuth == 3.14
    assert fits_obj.table_angle == 1.23
    assert fits_obj.time_obs == "2020-01-02T00:00:00.000000"
    assert fits_obj.name == "foo"
    np.testing.assert_equal(fits_obj.data, np.arange(9).reshape(3, 3))


def test_squeezing_array(extra_axis_hdu_with_complete_common_header):
    """
    Given: an HDU with a 3D array, where one axis has length 1
    When: loading the HDU with the L0FitsAccess class
    Then: the data element only contains two axes, the third axis being removed
    """
    fits_obj = L0FitsAccess(extra_axis_hdu_with_complete_common_header)
    assert len(fits_obj.data.shape) == 2


def test_squeezing_array_with_intentional_unitary_axis(
    singleton_axis_hdu_with_complete_common_header,
):
    """
    Given: an HDU with a 2D array, where one axis has length 1
    When: loading the HDU with the L0FitsAccess class
    Then: the data element only contains two axes, with the 'squeeze' not taking effect
    """
    fits_obj = L0FitsAccess(singleton_axis_hdu_with_complete_common_header)
    assert len(fits_obj.data.shape) == 2


def test_false_auto_squeeze(three_singleton_axes_hdu):
    """
    Given: an HDU with a 3D array where all axes have length 1
    When: loading the HDU with a FitsAccess class with auto_squeeze set to False
    Then: the full, 3D shape of the data is preserved
    """
    fits_obj = L0FitsAccess(three_singleton_axes_hdu, auto_squeeze=False)
    assert fits_obj.data.shape == (1, 1, 1)


def test_setting_data(hdu_with_complete_common_header):
    """
    Given: a L0FitsAccess object with data and a header
    When: setting the object's data property with a new array
    Then: the object's data and dynamic header keys are correctly updated
    """
    fits_obj = L0FitsAccess(hdu_with_complete_common_header)
    new_array = np.random.random((10, 4))  # Intentionally a different shape
    fits_obj.data = new_array
    np.testing.assert_equal(fits_obj.data, new_array)
    assert fits_obj.header["NAXIS1"] == 4
    assert fits_obj.header["NAXIS2"] == 10


def test_header_dict(hdu_with_special_keys):
    """
    Given: A FitsAccess object with data and a header including special header keys
    When: Accessing the header_dict method
    Then: The object's header is successfully exported as a dict of the same length as the header when accounting for multiple HISTORY or COMMENT cards
    """
    hdu, added_header_key = hdu_with_special_keys
    fits_obj = FitsAccessBase(hdu)
    assert isinstance(fits_obj.header_dict, dict)
    if added_header_key == "continue":
        assert len(fits_obj.header_dict) == len(fits_obj.header)
    if added_header_key in ["history", "comment"]:
        # HISTORY and COMMENT keys get "squeezed"
        assert len(fits_obj.header_dict) == len(fits_obj.header) - 1


@pytest.mark.parametrize(
    "header_type",
    [
        pytest.param(dict, id="Dict"),
        pytest.param(fits.header.Header, id="Header"),
        pytest.param(fits.hdu.compressed.CompImageHeader, id="CompHeader"),
    ],
)
def test_from_header_naxis_preserved(header_type):
    """
    Given: A header with NAXIS and NAXISn keys
    When: Ingesting that header with `FitsAccessBase.from_header`
    Then: The original NAXIS and NAXISn keys are preserved
    """
    raw_header = {"NAXIS": 2, "NAXIS1": 123, "NAXIS2": 456}
    header = header_type(raw_header)

    fits_obj = FitsAccessWithNaxisKeys.from_header(header)

    assert fits_obj.naxis == 2
    assert fits_obj.naxis1 == 123
    assert fits_obj.naxis2 == 456
