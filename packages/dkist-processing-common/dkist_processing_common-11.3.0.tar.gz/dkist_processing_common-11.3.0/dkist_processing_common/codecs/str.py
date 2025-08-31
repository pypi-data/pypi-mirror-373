"""Encoder/decoder for writing and reading str to files."""

from pathlib import Path

from dkist_processing_common.codecs.bytes import bytes_decoder


def str_encoder(string: str, encoding: str = "utf-8", errors="strict") -> bytes:
    """Convert a str to bytes using the given encoding."""
    if not isinstance(string, str):
        raise ValueError(f"Input type {type(string)} is not str")
    return string.encode(encoding=encoding, errors=errors)


def str_decoder(path: Path, encoding: str = "utf-8", errors="strict") -> str:
    """Read the data in a file as a string."""
    file_bytes = bytes_decoder(path)
    return file_bytes.decode(encoding=encoding, errors=errors)
