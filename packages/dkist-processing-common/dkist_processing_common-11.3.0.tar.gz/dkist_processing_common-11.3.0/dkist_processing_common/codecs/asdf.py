"""Encoders and decoders for writing and reading ASDF files."""

from io import BytesIO
from pathlib import Path

import asdf

from dkist_processing_common.codecs.iobase import iobase_encoder


def asdf_fileobj_encoder(asdf_obj: asdf.AsdfFile, custom_schema=None, **asdf_write_kwargs) -> bytes:
    """Save an `asdf.AsdfFile` object."""
    file_obj = BytesIO()
    asdf_obj.write_to(file_obj, **asdf_write_kwargs)
    return iobase_encoder(file_obj)


def asdf_encoder(tree: dict, custom_schema=None, **asdf_write_kwargs) -> bytes:
    """Convert a dict to raw bytes representing an ASDF file for writing to a file."""
    asdf_obj = asdf.AsdfFile(tree, custom_schema=custom_schema)
    return asdf_fileobj_encoder(asdf_obj, custom_schema=custom_schema, **asdf_write_kwargs)


def asdf_decoder(
    path: Path, lazy_load: bool = False, memmap: bool = False, **asdf_read_kwargs
) -> dict:
    """Read a Path with asdf and return the file's tree."""
    f = asdf.open(path, lazy_load=lazy_load, memmap=memmap, **asdf_read_kwargs)
    return f.tree
