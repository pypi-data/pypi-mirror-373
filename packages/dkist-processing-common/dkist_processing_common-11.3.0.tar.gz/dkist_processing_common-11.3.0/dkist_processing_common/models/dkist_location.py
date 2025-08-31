"""Return hard-coded EarthLocation of the DKIST.

Cartesian geocentric coordinates of DKIST on Earth as retrieved from
https://github.com/astropy/astropy-data/blob/gh-pages/coordinates/sites.json#L838
"""

import astropy.units as u
from astropy.coordinates import EarthLocation

_dkist_site_info = {
    "aliases": ["DKIST", "ATST"],
    "name": "Daniel K. Inouye Solar Telescope",
    "elevation": 3067,
    "elevation_unit": "meter",
    "latitude": 20.7067,
    "latitude_unit": "degree",
    "longitude": 203.7436,
    "longitude_unit": "degree",
    "timezone": "US/Hawaii",
    "source": "DKIST website: https://www.nso.edu/telescopes/dki-solar-telescope/",
}

location_of_dkist: EarthLocation = EarthLocation.from_geodetic(
    _dkist_site_info["longitude"] * u.Unit(_dkist_site_info["longitude_unit"]),
    _dkist_site_info["latitude"] * u.Unit(_dkist_site_info["latitude_unit"]),
    _dkist_site_info["elevation"] * u.Unit(_dkist_site_info["elevation_unit"]),
)
