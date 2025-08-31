"""Encoder/decoders for writing and reading quality data."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

from dkist_processing_common.codecs.json import json_decoder
from dkist_processing_common.codecs.json import json_encoder

logger = logging.getLogger(__name__)


class QualityDataEncoder(json.JSONEncoder):
    """A JSON encoder for the quality data."""

    def __init__(self, **dumps_kwargs):
        # Raise a ValueError for NaN and Infinity.
        dumps_kwargs["allow_nan"] = False
        super().__init__(**dumps_kwargs)

    def default(self, obj) -> dict:
        """Encode datetime as dict of iso formatted strings.  JSONEncoder will later render the dict as a string."""
        if isinstance(obj, datetime):
            return {"iso_date": obj.isoformat("T")}
        return super().default(obj)


def quality_data_encoder(
    data: Any, encoding: str = "utf-8", errors="strict", **dumps_kwargs
) -> bytes:
    """Convert quality data to bytes by encoding as JSON."""
    # This encoder is for the QualityDataEncoder class
    if cls := dumps_kwargs.pop("cls", None):
        logger.info(
            f"Ignoring {cls=}.  Default JSONEncoder for quality_data_encoder is QualityDataEncoder."
        )
    # allow_nan is per QualityDataEncoder class
    if allow_nan := dumps_kwargs.pop("allow_nan", None):
        logger.info(f"Ignoring {allow_nan=} for quality_data_encoder.")

    return json_encoder(
        data, encoding=encoding, errors=errors, cls=QualityDataEncoder, **dumps_kwargs
    )


def quality_data_hook(obj: dict):
    """
    Decode iso date dict.

    Convert object being json decoded into a datetime object if in the format `{"iso_date":"<iso formatted string>"}`
    like those produced by QualityDataEncoder.
    This is the same as datetime_json_object_hook in dkist-quality.
    :param obj: dict of the object being json decoded
    :return: datetime object
    """
    # extract date string if present in the object dict
    iso_date = obj.get("iso_date")
    if iso_date is not None:
        return datetime.fromisoformat(iso_date)
    # iso_date not found - not covered by this hook
    return obj


def quality_data_decoder(
    path: Path, encoding: str = "utf-8", errors="strict", **loads_kwargs
) -> Any:
    """Read a file as JSON and return the decoded objects."""
    if object_hook := loads_kwargs.pop("object_hook", None):
        logger.info(f"Ignoring {object_hook=} for quality_data_decoder.")

    return json_decoder(
        path, encoding=encoding, errors=errors, object_hook=quality_data_hook, **loads_kwargs
    )


class QualityValueEncoder(json.JSONEncoder):
    """A JSON encoder applied to the quality metrics."""

    def default(self, obj: Any) -> Any:
        """Implement an encoder that correctly handles numpy float32 data."""
        # np.float32 is only for single values. Even an array of np.float32 objects is a np.ndarray
        if isinstance(obj, np.float32):
            return float(obj)
        return super().default(obj)
