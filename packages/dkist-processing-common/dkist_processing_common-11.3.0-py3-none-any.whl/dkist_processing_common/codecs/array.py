"""Encoder/decoder for writing/reading numpy arrays."""

import io
from pathlib import Path

import numpy as np

from dkist_processing_common.codecs.iobase import iobase_encoder


def array_encoder(data: np.ndarray, **np_kwargs) -> bytes:
    """Convert a numpy array to bytes compatible with np.load()."""
    buffer = io.BytesIO()
    np.save(buffer, data, **np_kwargs)
    return iobase_encoder(buffer)


def array_decoder(path: Path, **np_kwargs) -> np.ndarray:
    """Return the data in the file as a numpy array using np.load()."""
    return np.load(path, **np_kwargs)
