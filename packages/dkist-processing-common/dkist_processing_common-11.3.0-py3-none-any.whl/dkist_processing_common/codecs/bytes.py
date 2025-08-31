"""Encoder/decoder for writing and reading bytes objects."""

from pathlib import Path


def bytes_encoder(data: bytes) -> bytes:
    """Passthrough for when the input are already bytes."""
    if not isinstance(data, bytes):
        raise ValueError(f"Input type {type(data)} is not bytes")
    return data


def bytes_decoder(path: Path) -> bytes:
    """Read a Path as a binary file and return its bytes."""
    with open(path, "rb") as f:
        file_bytes = f.read()

    return file_bytes
