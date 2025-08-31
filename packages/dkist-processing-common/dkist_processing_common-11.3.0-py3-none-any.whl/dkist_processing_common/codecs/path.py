"""Default decoder to pass through paths from `read`."""

from pathlib import Path


def path_decoder(path: Path) -> Path:
    """Passthrough for when the path is already a Path."""
    return path
