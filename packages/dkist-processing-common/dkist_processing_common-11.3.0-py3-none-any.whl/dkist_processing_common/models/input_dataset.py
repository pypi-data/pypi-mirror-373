"""Input dataset models for the inputDatasetPartDocument from the metadata store api."""

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import Json
from pydantic import PlainSerializer
from pydantic import field_serializer
from pydantic import field_validator
from pydantic.alias_generators import to_camel
from typing_extensions import Annotated


class InputDatasetBaseModel(BaseModel):
    """Custom BaseModel for input datasets."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
        validate_assignment=True,
    )

    def model_dump(self, **kwargs) -> dict:
        """Dump models as they were in the metadata store."""
        kwargs.setdefault("exclude_defaults", True)
        kwargs.setdefault("by_alias", True)  # will not be needed in Pydantic v3
        return super().model_dump(**kwargs)

    def model_dump_json(self, **kwargs) -> str:
        """Dump models as they were in the metadata store."""
        kwargs.setdefault("exclude_defaults", True)
        kwargs.setdefault("by_alias", True)  # will not be needed in Pydantic v3
        return super().model_dump_json(**kwargs)


class InputDatasetObject(InputDatasetBaseModel):
    """Input dataset object validator for a single file."""

    bucket: str
    object_key: str
    tag: str | None = None


class InputDatasetFilePointer(InputDatasetBaseModel):
    """Wrapper for InputDatasetObject files."""

    file_pointer: InputDatasetObject = Field(alias="__file__")


class InputDatasetParameterValue(InputDatasetBaseModel):
    """Input dataset parameter value validator."""

    parameter_value_id: int
    # parameter_value: Json[InputDatasetFilePointer] | Json[Any] # will work in gqlclient v2
    parameter_value: Json[Any]
    parameter_value_start_date: Annotated[
        datetime, Field(default=datetime(1, 1, 1)), PlainSerializer(lambda x: x.isoformat())
    ]

    @field_validator("parameter_value", mode="after")
    @classmethod
    def validate_parameter_value(cls, param_val):
        """Decode and provide additional validation for parameter_value types."""
        match param_val:
            case {"__file__": _}:
                return InputDatasetFilePointer.model_validate(param_val)
            case _:
                return param_val

    @field_serializer("parameter_value")
    def serialize_parameter_value(self, param_val):
        """Serialize the parameter_value types."""
        if isinstance(param_val, InputDatasetBaseModel):
            return json.dumps(param_val.model_dump())
        return json.dumps(param_val)


class InputDatasetParameter(InputDatasetBaseModel):
    """Parsing of the inputDatasetPartDocument that is relevant for parameters."""

    parameter_name: str
    parameter_values: list[InputDatasetParameterValue]

    @property
    def input_dataset_objects(self) -> list[InputDatasetObject]:
        """Find and return list of InputDatasetObjects."""
        object_list = []
        for param in self.parameter_values:
            if isinstance(param.parameter_value, InputDatasetFilePointer):
                object_list.append(param.parameter_value.file_pointer)
        return object_list


class InputDatasetFrames(InputDatasetBaseModel):
    """Parsing of the inputDatasetPartDocument that is relevant for frames."""

    bucket: str
    object_keys: list[str] = Field(alias="object_keys")  # not camel case in metadata store

    @property
    def input_dataset_objects(self) -> list[InputDatasetObject]:
        """Convert a single bucket and a list of object_keys list into a list of InputDatasetObjects."""
        object_list = []
        for frame in self.object_keys:
            object_list.append(InputDatasetObject(bucket=self.bucket, object_key=frame))
        return object_list


class InputDatasetPartDocumentList(InputDatasetBaseModel):
    """List of either InputDatasetFrames or InputDatasetParameter objects."""

    doc_list: list[InputDatasetFrames] | list[InputDatasetParameter] = Field(alias="doc_list")
