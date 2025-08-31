"""Abstraction layer for accessing fits data via class attributes."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from astropy.io import fits


class FitsAccessBase:
    """
    Abstraction layer for accessing fits data via class attributes.

    Parameters
    ----------
    hdu
        The fits object
    name
        An optional name that can be associated with the object
    auto_squeeze
        A boolean indicating whether to 'squeeze' out dimensions of size 1
    """

    def __init__(
        self,
        hdu: fits.ImageHDU | fits.PrimaryHDU | fits.CompImageHDU,
        name: str | Path | None = None,
        auto_squeeze: bool = True,
    ):
        self._hdu = hdu
        self.name = name
        self.auto_squeeze = auto_squeeze

    def __repr__(self):
        return f"{self.__class__.__name__}(hdu={self._hdu!r}, name={self.name!r}, auto_squeeze={self.auto_squeeze})"

    @property
    def data(self) -> np.ndarray:
        """
        Return the data array from the associated FITS object, with axes of length 1 removed if the array has three dimensions and the unit axis is the zeroth one.

        This is intended solely to remove the dummy dimension that is in raw data from the summit.

        Setting `auto_squeeze = False` when initializing this object will never squeeze out any dimensions

        Returns
        -------
        data array
        """
        # This conditional is explicitly to catch summit data with a dummy first axis for WCS
        # purposes
        if self.auto_squeeze and len(self._hdu.data.shape) == 3 and self._hdu.data.shape[0] == 1:
            return np.squeeze(self._hdu.data)
        return self._hdu.data

    @data.setter
    def data(self, array: np.ndarray) -> None:
        """
        Set the data array using an input data array.

        Parameters
        ----------
        array
            The input array

        Returns
        -------
        None
        """
        # There is no shape magic stuff going on here right now because the tasks/services that care about
        # it will deal with it themselves (I think (tm)).
        self._hdu.data = array

    @property
    def header(self) -> fits.Header:
        """Return the header for this fits object."""
        return self._hdu.header

    @property
    def header_dict(self) -> dict:
        """Return the header as a dict for this fits object with the special card values (HISTORY, COMMENT) as strings."""
        result = {}
        for card, value in self.header.items():
            if not isinstance(value, (int, float, str, bool)):
                result[card] = str(value)
            else:
                result[card] = value
        return result

    @property
    def size(self) -> float:
        """Return the size in bytes of the data portion of this fits object."""
        return self._hdu.size

    @classmethod
    def from_header(cls, header: fits.Header | dict, name: str | None = None) -> FitsAccessBase:
        """
        Convert a header to a FitsAccessBase (or child) object.

        Parameters
        ----------
        header
            A single `astropy.io.fits.header.Header` HDU object.
        name
            A unique name for the fits access instance
        """
        if isinstance(header, dict):
            header = fits.Header(header)
        hdu = fits.PrimaryHDU()

        # We need to update the header after `PrimaryHDU` instantiation because some of the FITS controlled keys
        # (e.g., NAXIS, NAXISn) would otherwise be changed by checks that occur during instantiation.
        hdu.header.update(header)
        return cls(hdu=hdu, name=name)

    @classmethod
    def from_path(cls, path: str | Path) -> FitsAccessBase:
        """
        Load the file at given path into a FitsAccess object.

        Parameters
        ----------
        path
            Location of fits file on disk
        """
        hdul = fits.open(path)
        if hdul[0].data is not None:
            hdu = hdul[0]
        else:
            hdu = hdul[1]
        return cls(hdu=hdu, name=path)
