"""
Support functions and constants for customized FakeGQLClient
"""

import json
from abc import ABC
from abc import abstractmethod
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import BaseModel

from dkist_processing_common.models.graphql import InputDatasetInputDatasetPartResponse
from dkist_processing_common.models.graphql import InputDatasetPartResponse
from dkist_processing_common.models.graphql import InputDatasetPartTypeResponse
from dkist_processing_common.models.graphql import InputDatasetRecipeInstanceResponse
from dkist_processing_common.models.graphql import InputDatasetRecipeRunResponse
from dkist_processing_common.models.graphql import InputDatasetResponse
from dkist_processing_common.models.graphql import RecipeInstanceResponse
from dkist_processing_common.models.graphql import RecipeRunProvenanceResponse
from dkist_processing_common.models.graphql import RecipeRunResponse
from dkist_processing_common.models.graphql import RecipeRunStatusResponse

TILE_SIZE = 64

default_observe_frames_doc = [
    {
        "bucket": uuid4().hex[:6],
        "object_keys": [Path(uuid4().hex[:6]).as_posix() for _ in range(3)],
    }
]

default_calibration_frames_doc = [
    {
        "bucket": uuid4().hex[:6],
        "object_keys": [Path(uuid4().hex[:6]).as_posix() for _ in range(3)],
    },
    {
        "bucket": uuid4().hex[:6],
        "object_keys": [Path(uuid4().hex[:6]).as_posix() for _ in range(3)],
    },
]

default_parameters_doc = [
    {
        "parameterName": "param_name_1",
        "parameterValues": [
            {
                "parameterValueId": 1,
                "parameterValue": json.dumps([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
                "parameterValueStartDate": datetime(2000, 1, 1).isoformat(),
            }
        ],
    },
    {
        "parameterName": "param_name_2",
        "parameterValues": [
            {
                "parameterValueId": 2,
                "parameterValue": json.dumps(
                    {
                        "__file__": {
                            "bucket": "data",
                            "objectKey": f"parameters/param_name/{uuid4().hex}.dat",
                        }
                    }
                ),
                "parameterValueStartDate": datetime(2000, 1, 1).isoformat(),
            },
            {
                "parameterValueId": 3,
                "parameterValue": json.dumps(
                    {
                        "__file__": {
                            "bucket": "data",
                            "objectKey": f"parameters/param_name/{uuid4().hex}.dat",
                        }
                    }
                ),
                "parameterValueStartDate": datetime(2000, 1, 2).isoformat(),
            },
        ],
    },
    {
        "parameterName": "param_name_4",
        "parameterValues": [
            {
                "parameterValueId": 4,
                "parameterValue": json.dumps({"a": 1, "b": 3.14159, "c": "foo", "d": [1, 2, 3]}),
                "parameterValueStartDate": datetime(2000, 1, 1).isoformat(),
            }
        ],
    },
]

default_recipe_run_configuration = {"tile_size": TILE_SIZE}


class Unset:
    pass


class ResponseMapping(BaseModel, ABC):
    response: BaseModel

    @abstractmethod
    def match_query(self, query_base: str, query_response_cls: type):
        pass


class RecipeRunStatusResponseMapping(ResponseMapping):
    def match_query(self, query_base: str, query_response_cls: type):
        if query_base == "recipeRunStatuses":
            if query_response_cls == RecipeRunStatusResponse:
                return self.response
        return Unset


class RecipeRunResponseMapping(ResponseMapping):
    def match_query(self, query_base: str, query_response_cls: type):
        if query_base == "recipeRuns":
            if query_response_cls == RecipeRunResponse:
                return self.response
        return Unset


class InputDatasetRecipeRunResponseMapping(ResponseMapping):
    def match_query(self, query_base: str, query_response_cls: type):
        if query_base == "recipeRuns":
            if query_response_cls == InputDatasetRecipeRunResponse:
                return self.response
        return Unset


class QualityResponseMapping(ResponseMapping):
    pass  # TODO


def make_default_recipe_run_status_response() -> RecipeRunStatusResponse:
    return RecipeRunStatusResponse(recipeRunStatusId=1)


def make_default_recipe_run_response() -> RecipeRunResponse:
    return RecipeRunResponse(
        recipeInstanceId=1,
        recipeInstance=RecipeInstanceResponse(
            recipeId=1,
            inputDatasetId=1,
        ),
        configuration=json.dumps(default_recipe_run_configuration),
        recipeRunProvenances=[
            RecipeRunProvenanceResponse(recipeRunProvenanceId=1, isTaskManual=False),
        ],
    )


def make_default_input_dataset_recipe_run_response() -> InputDatasetRecipeRunResponse:
    return InputDatasetRecipeRunResponse(
        recipeInstance=InputDatasetRecipeInstanceResponse(
            inputDataset=InputDatasetResponse(
                inputDatasetId=1,
                isActive=True,
                inputDatasetInputDatasetParts=[
                    InputDatasetInputDatasetPartResponse(
                        inputDatasetPart=InputDatasetPartResponse(
                            inputDatasetPartId=1,
                            inputDatasetPartDocument=json.dumps(default_parameters_doc),
                            inputDatasetPartType=InputDatasetPartTypeResponse(
                                inputDatasetPartTypeName="parameters"
                            ),
                        )
                    ),
                    InputDatasetInputDatasetPartResponse(
                        inputDatasetPart=InputDatasetPartResponse(
                            inputDatasetPartId=2,
                            inputDatasetPartDocument=json.dumps(default_observe_frames_doc),
                            inputDatasetPartType=InputDatasetPartTypeResponse(
                                inputDatasetPartTypeName="observe_frames"
                            ),
                        )
                    ),
                    InputDatasetInputDatasetPartResponse(
                        inputDatasetPart=InputDatasetPartResponse(
                            inputDatasetPartId=3,
                            inputDatasetPartDocument=json.dumps(default_calibration_frames_doc),
                            inputDatasetPartType=InputDatasetPartTypeResponse(
                                inputDatasetPartTypeName="calibration_frames"
                            ),
                        )
                    ),
                ],
            ),
        ),
    )


default_response_mappings = (
    RecipeRunStatusResponseMapping(response=make_default_recipe_run_status_response()),
    RecipeRunResponseMapping(response=make_default_recipe_run_response()),
    InputDatasetRecipeRunResponseMapping(response=make_default_input_dataset_recipe_run_response()),
)


def fake_gql_client_factory(response_mapping_override: ResponseMapping | None = None):

    if response_mapping_override:
        response_mappings = (response_mapping_override,) + default_response_mappings
    else:
        response_mappings = default_response_mappings

    class FakeGQLClientClass:
        def __init__(self, *args, **kwargs):
            pass

        def execute_gql_query(self, query_base: str, query_response_cls: type, *args, **kwargs):
            # Overrides are prepended; first match is returned.
            for rm in response_mappings:
                response = rm.match_query(query_base, query_response_cls)
                if response is not Unset:
                    return [response]
            raise ValueError(f"Mocked response not found for {query_base=}, {query_response_cls=}")

        @staticmethod
        def execute_gql_mutation(**kwargs): ...

    return FakeGQLClientClass


@pytest.fixture()
def fake_gql_client():
    """
    Convenience fixture for default mock GQL client. To customize, use fake_gql_client_factory.
    """
    return fake_gql_client_factory()
