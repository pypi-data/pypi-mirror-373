import json
from datetime import datetime
from typing import Any
from uuid import uuid4

import pytest

from dkist_processing_common.codecs.basemodel import basemodel_decoder
from dkist_processing_common.models.input_dataset import InputDatasetPartDocumentList
from dkist_processing_common.models.tags import Tag


def input_dataset_frames_part_factory(bucket_count: int = 1) -> list[dict]:
    return [
        {"bucket": uuid4().hex[:6], "object_keys": [uuid4().hex[:6] for _ in range(3)]}
        for _ in range(bucket_count)
    ]


def flatten_frame_parts(frame_parts: list[dict]) -> list[tuple[str, str]]:
    result = []
    for frame_set in frame_parts:
        for key in frame_set["object_keys"]:
            result.append((frame_set["bucket"], key))
    return result


def input_dataset_parameters_part_factory(
    parameter_count: int = 1,
    parameter_value_count: int = 1,
    has_date: bool = False,
    has_file: bool = False,
) -> list[dict]:
    result = [
        {
            "parameterName": uuid4().hex[:6],
            "parameterValues": [
                {"parameterValueId": i, "parameterValue": json.dumps(uuid4().hex)}
                for i in range(parameter_value_count)
            ],
        }
        for _ in range(parameter_count)
    ]
    if has_date:
        for data in result:
            param_list = data["parameterValues"]
            for item in param_list:
                item["parameterValueStartDate"] = datetime(2022, 9, 14).isoformat()
    if has_file:
        for data in result:
            param_list = data["parameterValues"]
            for item in param_list:
                item["parameterValue"] = json.dumps(
                    {
                        "__file__": {
                            "bucket": "data",
                            "objectKey": f"parameters/{data['parameterName']}/{uuid4().hex}.dat",
                        }
                    }
                )
    return result


@pytest.mark.parametrize(
    "input_dataset_parts",
    [
        pytest.param(
            (input_dataset_frames_part_factory(), Tag.input_dataset_observe_frames()),
            id="observe_single_bucket",
        ),
        pytest.param(
            (input_dataset_frames_part_factory(bucket_count=2), Tag.input_dataset_observe_frames()),
            id="observe_multi_bucket",
        ),
        pytest.param(
            (input_dataset_frames_part_factory(), Tag.input_dataset_calibration_frames()),
            id="calib_single_bucket",
        ),
        pytest.param(
            (
                input_dataset_frames_part_factory(bucket_count=2),
                Tag.input_dataset_calibration_frames(),
            ),
            id="calib_multi_bucket",
        ),
    ],
)
def test_input_dataset_frames_part_document(
    task_with_input_dataset, input_dataset_parts: tuple[Any, str]
):
    """
    Given: A task with an input dataset frames part document already written to file
    When: Reading the file into a validated model
    Then: The correct contents of the file are loaded
    """
    doc_part, tag = input_dataset_parts
    task = task_with_input_dataset
    doc_from_file = next(
        task.read(tags=tag, decoder=basemodel_decoder, model=InputDatasetPartDocumentList)
    )
    frames = [frames.model_dump() for frames in doc_from_file.doc_list]
    assert frames == doc_part


@pytest.mark.parametrize(
    "input_dataset_parts",
    [
        pytest.param(
            [
                (input_dataset_frames_part_factory(), Tag.input_dataset_observe_frames()),
                (input_dataset_frames_part_factory(), Tag.input_dataset_calibration_frames()),
            ],
            id="observe1_cal1_single_bucket",
        ),
        pytest.param(
            [
                (input_dataset_frames_part_factory(), Tag.input_dataset_observe_frames()),
            ],
            id="observe1_cal0_single_bucket",
        ),
        pytest.param(
            [
                (input_dataset_frames_part_factory(), Tag.input_dataset_calibration_frames()),
            ],
            id="observe0_cal1_single_bucket",
        ),
        pytest.param(
            [
                (
                    input_dataset_frames_part_factory(bucket_count=2),
                    Tag.input_dataset_observe_frames(),
                ),
                (
                    input_dataset_frames_part_factory(bucket_count=2),
                    Tag.input_dataset_calibration_frames(),
                ),
            ],
            id="observe1_cal1_multi_bucket",
        ),
        pytest.param(
            [
                (
                    input_dataset_frames_part_factory(bucket_count=2),
                    Tag.input_dataset_observe_frames(),
                ),
            ],
            id="observe1_cal0_multi_bucket",
        ),
        pytest.param(
            [
                (
                    input_dataset_frames_part_factory(bucket_count=2),
                    Tag.input_dataset_calibration_frames(),
                ),
            ],
            id="observe0_cal1_multi_bucket",
        ),
    ],
)
def test_input_dataset_frames_combination(
    task_with_input_dataset, input_dataset_parts: list[tuple[Any, str]]
):
    """
    Given: A task with both types of input dataset frame documents written to files
    When: Reading the file and validating into models
    Then: The correct files are returned by the input_dataset_objects method of InputDatasetFrames
    """
    # Given
    doc_parts = [part for part, _ in input_dataset_parts]
    task = task_with_input_dataset
    expected = []
    for part in doc_parts:
        if part:
            expected.extend(flatten_frame_parts(part))
    expected_set = set(expected)
    # When
    frames = []
    observe_frames = next(
        task.read(
            tags=Tag.input_dataset_observe_frames(),
            decoder=basemodel_decoder,
            model=InputDatasetPartDocumentList,
        ),
        None,
    )
    frames += observe_frames.doc_list if observe_frames else []
    calibration_frames = next(
        task.read(
            tags=Tag.input_dataset_calibration_frames(),
            decoder=basemodel_decoder,
            model=InputDatasetPartDocumentList,
        ),
        None,
    )
    frames += calibration_frames.doc_list if calibration_frames else []
    # Then
    frames_objects = sum([f.input_dataset_objects for f in frames], [])
    actual = [(frame.bucket, frame.object_key) for frame in frames_objects]
    actual_set = set(actual)
    assert len(actual) == len(actual_set)
    assert actual_set.difference(expected_set) == set()


@pytest.mark.parametrize(
    "input_dataset_parts",
    [
        pytest.param(
            (input_dataset_parameters_part_factory(), Tag.input_dataset_parameters()),
            id="single_param_no_date_no_file",
        ),
        pytest.param(
            (input_dataset_parameters_part_factory(has_file=True), Tag.input_dataset_parameters()),
            id="single_param_no_date_with_file",
        ),
        pytest.param(
            (input_dataset_parameters_part_factory(has_date=True), Tag.input_dataset_parameters()),
            id="single_param_with_date_no_file",
        ),
        pytest.param(
            (
                input_dataset_parameters_part_factory(has_date=True, has_file=True),
                Tag.input_dataset_parameters(),
            ),
            id="single_param_with_date_with_file",
        ),
        pytest.param(
            (
                input_dataset_parameters_part_factory(parameter_count=2),
                Tag.input_dataset_parameters(),
            ),
            id="multi_param_no_date_no_file",
        ),
        pytest.param(
            (
                input_dataset_parameters_part_factory(parameter_count=2, has_date=True),
                Tag.input_dataset_parameters(),
            ),
            id="multi_param_with_date_no_file",
        ),
        pytest.param(
            (
                input_dataset_parameters_part_factory(parameter_count=2, has_file=True),
                Tag.input_dataset_parameters(),
            ),
            id="multi_param_no_date_with_file",
        ),
        pytest.param(
            (
                input_dataset_parameters_part_factory(
                    parameter_count=2, has_date=True, has_file=True
                ),
                Tag.input_dataset_parameters(),
            ),
            id="multi_param_with_date_with_file",
        ),
    ],
)
def test_input_dataset_parameters(task_with_input_dataset, input_dataset_parts: tuple[Any, str]):
    """
    Given: A task with an input dataset parameters part document written to file
    When: Reading the file and validating into models
    Then: The correct contents of the file, including file parameters, are loaded
    """
    doc_part, tag = input_dataset_parts
    task = task_with_input_dataset
    doc_from_file = next(
        task.read(tags=tag, decoder=basemodel_decoder, model=InputDatasetPartDocumentList)
    )

    params = [params.model_dump() for params in doc_from_file.doc_list]
    assert params == doc_part
    expected_files = []
    for item in doc_part or []:
        for val in item["parameterValues"]:
            if "__file__" in val["parameterValue"]:
                file_dict = json.loads(val["parameterValue"])
                expected_files.append(file_dict["__file__"])
    file_objects = sum([d.input_dataset_objects for d in doc_from_file.doc_list], [])
    file_objects_dump = [f.model_dump() for f in file_objects]
    assert file_objects_dump == expected_files
