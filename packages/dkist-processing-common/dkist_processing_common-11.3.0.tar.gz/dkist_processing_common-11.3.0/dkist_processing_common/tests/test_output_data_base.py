from pathlib import Path
from uuid import uuid4

import pytest

from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks.output_data_base import OutputDataBase
from dkist_processing_common.tasks.output_data_base import TransferDataBase


class OutputDataBaseTask(OutputDataBase):
    def run(self) -> None: ...


@pytest.fixture
def output_data_base_task(recipe_run_id, mocker, fake_gql_client):
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    proposal_id = "test_proposal_id"
    with OutputDataBaseTask(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.constants._update({"PROPOSAL_ID": proposal_id})
        yield task, proposal_id
        task.constants._purge()


class TransferDataTask(TransferDataBase):
    def transfer_objects(self):
        pass


@pytest.fixture
def transfer_data_task(recipe_run_id, tmp_path, mocker, fake_gql_client):
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    with TransferDataTask(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(
            recipe_run_id=recipe_run_id,
            scratch_base_path=tmp_path,
        )
        task.constants._update({"PROPOSAL_ID": "propID"})
        # Write an output frame
        output_file_obj = uuid4().hex.encode("utf8")
        task.write(output_file_obj, tags=[Tag.output(), Tag.frame()])

        # Write a frame that's not output
        unwanted_file_obj = uuid4().hex.encode("utf8")
        task.write(unwanted_file_obj, tags=[Tag.frame()])

        yield task, output_file_obj
        task._purge()


def test_format_object_key(output_data_base_task):
    """
    :Given: a task based on OutputDataBase with a proposal ID in its constants mapping
    :When: formatting a path into an object key
    :Then: the proposal ID and filename are in the object key
    """
    task, proposal_id = output_data_base_task
    filename = "test_filename.ext"
    path = Path(f"a/b/c/d/{filename}")
    assert proposal_id in task.format_object_key(path)
    assert filename in task.format_object_key(path)
    assert task.destination_bucket == "data"


def test_build_output_frame_transfer_list(transfer_data_task):
    """
    Given: A task based on TransferDataBase with some files, some of which are OUTPUT
    When: Building a transfer list of all OUTPUT frames
    Then: All OUTPUT frames are listed and no non-OUTPUT frames are listed
    """
    task, output_file_obj = transfer_data_task

    transfer_list = task.build_output_frame_transfer_list()

    assert len(transfer_list) == 1
    transfer_item = transfer_list[0]
    with transfer_item.source_path.open(mode="rb") as f:
        assert output_file_obj == f.read()
