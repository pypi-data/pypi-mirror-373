import pytest
from astropy.coordinates import EarthLocation

from dkist_processing_common.models.dkist_location import location_of_dkist


@pytest.mark.flaky(max_reruns=10)
def test_location_of_dkist():
    """
    Given: function for retrieving the dkist location on earth
    When: Call function
    Then: result is the same as what is in the astropy online database
    """
    itrs = location_of_dkist
    assert itrs == EarthLocation.of_site("dkist")
