from pathlib import Path

import pytest

from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks import TransferL1Data


def fake_list_objects(self, bucket, prefix=None):
    return list()


@pytest.fixture
def transfer_l1_data_task(recipe_run_id, tmp_path, fake_constants_db):
    with TransferL1Data(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(
            recipe_run_id=recipe_run_id,
            scratch_base_path=tmp_path,
        )
        task.constants._update(fake_constants_db)
        frame_path = task.scratch.workflow_base_path / Path("frame.fits")
        movie_path = task.scratch.workflow_base_path / Path("movie.mp4")
        with open(frame_path, "w") as f:
            f.write("Frame")
        task.tag(path=frame_path, tags=[Tag.frame(), Tag.output()])
        with open(movie_path, "w") as f:
            f.write("Movie")
        task.tag(path=movie_path, tags=[Tag.output(), Tag.movie()])

        yield task
        task._purge()


def test_transfer_l1_data(transfer_l1_data_task, mocker, fake_gql_client):
    """
    Given: A task with frames and movies tagged as output
    When: Transfering the L1 data
    Then: The task completes without errors
    """
    # Yeah, we mock a whole bunch of stuff here, but this test at least confirms that the setup to these calls is correct
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    mocker.patch(
        "dkist_processing_common.tasks.mixin.globus.GlobusMixin.globus_transfer_scratch_to_object_store"
    )
    mocker.patch("dkist_processing_common.tasks.mixin.object_store.ObjectClerk.upload_object")
    mocker.patch(
        "dkist_processing_common.tasks.mixin.object_store.ObjectClerk.list_objects",
        fake_list_objects,
    )
    transfer_l1_data_task()
    assert True
