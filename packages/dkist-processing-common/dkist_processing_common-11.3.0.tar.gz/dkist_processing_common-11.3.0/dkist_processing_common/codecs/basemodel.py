"""Encoder/decoder for writing and reading Pydantic BaseModel objects."""

from pathlib import Path
from typing import Type

from pydantic import BaseModel

from dkist_processing_common.codecs.bytes import bytes_decoder
from dkist_processing_common.codecs.str import str_encoder


def basemodel_encoder(data: BaseModel, **basemodel_kwargs) -> bytes:
    """Convert a Pydantic BaseModel object into bytes for writing to file."""
    data_dump = data.model_dump_json(**basemodel_kwargs)
    return str_encoder(data_dump)


def basemodel_decoder(path: Path, model: Type[BaseModel], **basemodel_kwargs) -> BaseModel:
    """Return the data in the file as a Pydantic BaseModel object."""
    data = bytes_decoder(path)
    model_validated = model.model_validate_json(data, **basemodel_kwargs)
    return model_validated
