import json
import os
from pathlib import Path

import pytest

from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.basemodel import basemodel_decoder
from dkist_processing_common.models.input_dataset import InputDatasetPartDocumentList
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_processing_common.tasks.transfer_input_data import TransferL0Data
from dkist_processing_common.tests.mock_metadata_store import InputDatasetRecipeRunResponseMapping
from dkist_processing_common.tests.mock_metadata_store import default_calibration_frames_doc
from dkist_processing_common.tests.mock_metadata_store import default_observe_frames_doc
from dkist_processing_common.tests.mock_metadata_store import default_parameters_doc
from dkist_processing_common.tests.mock_metadata_store import fake_gql_client_factory
from dkist_processing_common.tests.mock_metadata_store import (
    make_default_input_dataset_recipe_run_response,
)


def create_parameter_files(
    task: WorkflowTaskBase, parameters_doc: list[dict] = default_parameters_doc
):
    """
    Create the parameter files specified in the parameters document returned by the metadata store.

    This fixture assumes that the JSON parameters document has already been loaded into a python
    structure (a list of dicts), but the parameter values themselves are still JSON.
    """
    for parameter in parameters_doc:
        for value in parameter["parameterValues"]:
            if "__file__" not in value["parameterValue"]:
                continue
            parameter_value = json.loads(value["parameterValue"])
            param_path = parameter_value["__file__"]["objectKey"]
            file_path = task.scratch.workflow_base_path / Path(param_path)
            if not file_path.parent.exists():
                file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(data="")
            task.tag(path=file_path, tags=Tag.parameter(param_path))


def create_input_frames(
    task: WorkflowTaskBase,
    input_frame_docs: list[dict] = default_observe_frames_doc + default_calibration_frames_doc,
):
    """
    Create the observe and calibration frame files specified in the input dataset documents
    returned by the metadata store.
    """
    for frame in input_frame_docs:
        for object_key in frame["object_keys"]:
            file_path = task.scratch.workflow_base_path / Path(object_key)
            if not file_path.parent.exists():
                file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(data="")
            task.tag(path=file_path, tags=[Tag.frame(), Tag.input()])


class TransferL0DataTask(TransferL0Data):
    def run(self) -> None: ...


@pytest.fixture
def fake_gql_client_class_missing_calibration_part():
    input_dataset_recipe_run_response = make_default_input_dataset_recipe_run_response()
    dataset_parts = (
        input_dataset_recipe_run_response.recipeInstance.inputDataset.inputDatasetInputDatasetParts
    )
    for index, part in enumerate(dataset_parts):
        if (
            part.inputDatasetPart.inputDatasetPartType.inputDatasetPartTypeName
            == "calibration_frames"
        ):
            del dataset_parts[index]
    new_response_mapping = InputDatasetRecipeRunResponseMapping(
        response=input_dataset_recipe_run_response
    )
    FakeGQLClientMissingInputDatasetCalibrationPart = fake_gql_client_factory(
        response_mapping_override=new_response_mapping
    )

    return FakeGQLClientMissingInputDatasetCalibrationPart


def _transfer_l0_data_task_with_client(recipe_run_id, tmp_path, mocker, client_cls):
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient",
        new=client_cls,
    )
    with TransferL0DataTask(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(
            recipe_run_id=recipe_run_id,
            scratch_base_path=tmp_path,
        )
        yield task
        task._purge()


@pytest.fixture
def transfer_l0_data_task(recipe_run_id, tmp_path, mocker, fake_gql_client):
    yield from _transfer_l0_data_task_with_client(recipe_run_id, tmp_path, mocker, fake_gql_client)


@pytest.fixture
def transfer_l0_data_task_missing_calibration_part(
    recipe_run_id, tmp_path, mocker, fake_gql_client_class_missing_calibration_part
):
    yield from _transfer_l0_data_task_with_client(
        recipe_run_id, tmp_path, mocker, fake_gql_client_class_missing_calibration_part
    )


@pytest.mark.parametrize(
    "expected_doc, tag",
    [
        pytest.param(
            default_observe_frames_doc,
            Tag.input_dataset_observe_frames(),
            id="observe_frames",
        ),
        pytest.param(
            default_calibration_frames_doc,
            Tag.input_dataset_calibration_frames(),
            id="calibration_frames",
        ),
        pytest.param(
            default_parameters_doc,
            Tag.input_dataset_parameters(),
            id="parameters",
        ),
    ],
)
def test_download_dataset(transfer_l0_data_task, expected_doc, tag):
    """
    :Given: a TransferL0Data task with a valid input dataset
    :When: downloading the dataset documents from the metadata store
    :Then: the correct documents are written to disk, along with tags for file parameters
    """
    # Given
    task = transfer_l0_data_task
    # When
    task.download_input_dataset()
    # Then
    doc_from_file = next(
        task.read(tags=tag, decoder=basemodel_decoder, model=InputDatasetPartDocumentList)
    )
    doc_list_from_file = doc_from_file.model_dump()["doc_list"]
    if (
        tag == Tag.input_dataset_parameters()
    ):  # parameter doc gets written with tags for file objects
        for item in expected_doc:
            for val in item["parameterValues"]:
                if "__file__" in val["parameterValue"]:
                    file_dict = json.loads(val["parameterValue"])["__file__"]
                    file_dict["tag"] = Tag.parameter(Path(file_dict["objectKey"]).name)
                    val["parameterValue"] = json.dumps({"__file__": file_dict})
    assert doc_list_from_file == expected_doc


def test_download_dataset_missing_part(transfer_l0_data_task_missing_calibration_part):
    """
    :Given: a TransferL0Data task with a valid input dataset without calibration frames
    :When: downloading the dataset documents from the metadata store
    :Then: the correct number of documents are written to disk
    """
    # Given
    task = transfer_l0_data_task_missing_calibration_part
    # When
    task.download_input_dataset()
    # Then
    observe_doc_from_file = next(
        task.read(
            tags=Tag.input_dataset_observe_frames(),
            decoder=basemodel_decoder,
            model=InputDatasetPartDocumentList,
        )
    )
    parameters_doc_from_file = next(
        task.read(
            tags=Tag.input_dataset_parameters(),
            decoder=basemodel_decoder,
            model=InputDatasetPartDocumentList,
        )
    )
    with pytest.raises(StopIteration):
        calibration_doc_from_file = next(
            task.read(
                tags=Tag.input_dataset_calibration_frames(),
                decoder=basemodel_decoder,
                model=InputDatasetPartDocumentList,
            )
        )


@pytest.mark.parametrize(
    "task_name",
    [
        pytest.param(
            "transfer_l0_data_task",
            id="observe_and_calibration_frames",
        ),
        pytest.param(
            "transfer_l0_data_task_missing_calibration_part",
            id="calibration_frames_missing",
        ),
    ],
)
def test_build_frame_transfer_list_formatted(request, task_name):
    """
    :Given: a TransferL0Data task with downloaded input dataset docs
    :When: building a list of frames in the input dataset formatted for transfer
    :Then: the correct items are correctly loaded into GlobusTransferItem objects
    """
    # Given
    task = request.getfixturevalue(task_name)
    task.download_input_dataset()
    # When
    observe_transfer_objects = task.build_transfer_list(doc_tag=Tag.input_dataset_observe_frames())
    calibration_transfer_objects = task.build_transfer_list(
        doc_tag=Tag.input_dataset_calibration_frames()
    )
    transfer_objects = observe_transfer_objects + calibration_transfer_objects
    formatted_transfer_items = task.format_transfer_items(input_dataset_objects=transfer_objects)
    # Then
    source_filenames = []
    destination_filenames = []
    expected_frames = list(default_observe_frames_doc)
    if "missing_calibration_part" not in task_name:
        expected_frames += default_calibration_frames_doc
    for frame_set in expected_frames:
        for key in frame_set["object_keys"]:
            source_filenames.append(os.path.join("/", frame_set["bucket"], key))
            destination_filenames.append(Path(key).name)
    assert len(formatted_transfer_items) == len(source_filenames)
    for item in formatted_transfer_items:
        assert item.source_path.as_posix() in source_filenames
        assert item.destination_path.name in destination_filenames
        assert not item.recursive


def test_build_parameter_file_transfer_items(transfer_l0_data_task):
    """
    :Given: a TransferL0Data task with downloaded input dataset docs
    :When: building a list of parameter files formatted for transfer
    :Then: the correct items are correctly loaded into GlobusTransferItem objects
    """
    # Given
    task = transfer_l0_data_task
    task.download_input_dataset()
    # When
    transfer_objects = task.build_transfer_list(doc_tag=Tag.input_dataset_parameters())
    formatted_transfer_items = task.format_transfer_items(input_dataset_objects=transfer_objects)
    # Then
    source_filenames = []
    destination_filenames = []
    parameters = default_parameters_doc
    for param in parameters:
        for value in param["parameterValues"]:
            if "__file__" in value["parameterValue"]:
                value_dict = json.loads(value["parameterValue"])
                bucket = value_dict["__file__"]["bucket"]
                object_key = value_dict["__file__"]["objectKey"]
                source_filenames.append(os.path.join("/", bucket, object_key))
                destination_filenames.append(Path(object_key).name)
    assert len(formatted_transfer_items) == len(source_filenames)
    for transfer_item in formatted_transfer_items:
        assert transfer_item.source_path.as_posix() in source_filenames
        assert transfer_item.destination_path.name in destination_filenames
        assert str(transfer_item.destination_path).startswith(str(task.scratch.workflow_base_path))
        assert not transfer_item.recursive


def test_tag_transfer_items(transfer_l0_data_task):
    """
    :Given: a TransferL0Data task with downloaded input dataset frames and parameter files
    :When: tagging the downloaded files
    :Then: the downloaded items are correctly tagged
    """
    # Given
    task = transfer_l0_data_task
    task.download_input_dataset()
    observe_transfer_objects = task.build_transfer_list(doc_tag=Tag.input_dataset_observe_frames())
    calibration_transfer_objects = task.build_transfer_list(
        doc_tag=Tag.input_dataset_calibration_frames()
    )
    frame_transfer_objects = observe_transfer_objects + calibration_transfer_objects
    create_input_frames(task)
    parameter_transfer_objects = task.build_transfer_list(doc_tag=Tag.input_dataset_parameters())
    create_parameter_files(task)
    # When
    transfer_objects = frame_transfer_objects + parameter_transfer_objects
    task.tag_transfer_objects(input_dataset_objects=transfer_objects)
    # Then
    input_tags = [Tag.input(), Tag.frame()]
    input_frames_on_disk = list(task.scratch.find_all(tags=input_tags))
    for obj in frame_transfer_objects:
        destination_path = task.scratch.absolute_path(obj.object_key)
        assert destination_path in input_frames_on_disk
    assert len(input_frames_on_disk) == len(frame_transfer_objects)
    for obj in parameter_transfer_objects:
        destination_path = task.scratch.absolute_path(obj.object_key)
        param_tag = Tag.parameter(Path(obj.object_key))
        param_file_on_disk = list(task.scratch.find_all(tags=param_tag))
        assert destination_path in param_file_on_disk
        assert len(param_file_on_disk) == 1
