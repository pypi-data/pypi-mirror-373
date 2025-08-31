"""Encoder/decoder for writing and reading IOBase binary (i.e., not Text) objects."""

from io import BytesIO
from io import IOBase
from io import TextIOBase
from pathlib import Path
from typing import Type


def iobase_encoder(data: Type[IOBase]) -> bytes:
    """Convert any binary `IOBase` subclass to `bytes` for writing to a file."""
    if not issubclass(data.__class__, IOBase):
        raise ValueError(f"Input type {type(data)} is not an IOBase subclass")
    if issubclass(data.__class__, TextIOBase):
        raise ValueError(
            f"Input type {type(data)} produces str data, which is currently not supported"
        )
    data.seek(0)  # ensure we are at the start of the buffer before read out
    return data.read()


def iobase_decoder(path: Path, io_class: Type[IOBase] = BytesIO) -> Type[IOBase]:
    """Read the contents of a file as any `IOBase` subclass."""
    with open(path, "rb") as f:
        file_obj = io_class(f.read())

    return file_obj
