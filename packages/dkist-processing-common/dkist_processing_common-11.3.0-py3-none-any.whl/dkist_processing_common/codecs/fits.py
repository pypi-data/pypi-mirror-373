"""Encoders and decoders for writing and reading FITS files."""

from io import BytesIO
from pathlib import Path
from typing import Type

import numpy as np
from astropy.io import fits
from astropy.io.fits import Header

from dkist_processing_common.codecs.iobase import iobase_encoder
from dkist_processing_common.models.fits_access import FitsAccessBase


def fits_array_encoder(data: np.ndarray, header: Header | dict | None = None) -> bytes:
    """Convert an array to raw bytes representing a fits `HDUList`."""
    if not isinstance(data, np.ndarray):
        raise ValueError(f"Input type {type(data)} is not np.ndarray")
    if isinstance(header, dict):
        header = Header(header)
    hdu_list = fits.HDUList([fits.PrimaryHDU(data=data, header=header)])
    return fits_hdulist_encoder(hdu_list)


def fits_hdulist_encoder(hdu_list: fits.HDUList) -> bytes:
    """Convert an `HDUList` to raw bytes for writing to a file."""
    if not isinstance(hdu_list, fits.HDUList):
        raise ValueError(f"Input type {type(hdu_list)} is not fits.HDUList")
    file_obj = BytesIO()
    hdu_list.writeto(file_obj, checksum=True)
    return iobase_encoder(file_obj)


def fits_hdu_decoder(path: Path, hdu: int | None = None) -> fits.PrimaryHDU | fits.CompImageHDU:
    """Read a Path with `fits` to produce an `HDUList`."""
    hdu_list = fits.open(path, checksum=True)
    return _extract_hdu(hdu_list, hdu)


def fits_array_decoder(path: Path, hdu: int | None = None, auto_squeeze: bool = True) -> np.ndarray:
    """Read a Path with `fits` and return the `.data` property."""
    hdu = fits_hdu_decoder(path, hdu=hdu)
    data = hdu.data

    # This conditional is explicitly to catch summit data with a dummy first axis for WCS
    # purposes
    if auto_squeeze and len(data.shape) == 3 and data.shape[0] == 1:
        return np.squeeze(data)
    return data


def fits_access_decoder(
    path: Path, fits_access_class: Type[FitsAccessBase], **fits_access_kwargs
) -> FitsAccessBase:
    """Read a Path with `fits` and ingest into a `FitsAccessBase`-type object."""
    hdu = fits_hdu_decoder(path)
    return fits_access_class(hdu=hdu, name=str(path), **fits_access_kwargs)


def _extract_hdu(hdul: fits.HDUList, hdu: int | None = None) -> fits.PrimaryHDU | fits.CompImageHDU:
    """
    Return the fits hdu associated with the data in the hdu list.

    Only search down the hdu index for the data if the hdu index is not explicitly provided.
    """
    if hdu is not None:
        return hdul[hdu]
    if hdul[0].data is not None:
        return hdul[0]
    return hdul[1]
