import json
from uuid import uuid4

import pytest

from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks import SubmitDatasetMetadata
from dkist_processing_common.tasks.mixin import metadata_store


@pytest.fixture()
def scratch_with_processed_data(recipe_run_id, tmp_path) -> WorkflowFileSystem:
    """Scratch instance for a recipe run id with tagged dataset metadata."""
    scratch = WorkflowFileSystem(
        recipe_run_id=recipe_run_id,
        scratch_base_path=tmp_path,
    )

    # Write a debug frame
    debug_file_obj = uuid4().hex.encode("utf8")
    scratch.write(debug_file_obj, relative_path="debug.ext", tags=[Tag.debug(), Tag.frame()])

    # Write a dataset inventory file
    dataset_inv_file_obj: bytes = json.dumps({"key": uuid4().hex}).encode("utf8")
    scratch.write(
        dataset_inv_file_obj,
        relative_path="dataset_inv.json",
        tags=[Tag.output(), Tag.dataset_inventory()],
    )

    # Write an asdf file
    asdf_file_obj = uuid4().hex.encode("utf8")
    scratch.write(asdf_file_obj, relative_path="asdf.asdf", tags=[Tag.output(), Tag.asdf()])

    # Write quality data
    # quality data is not tagged as OUTPUT
    quality_data_obj = json.dumps([{"key": uuid4().hex, "metric_code": "NOT_NULL"}]).encode("utf8")

    scratch.write(
        quality_data_obj,
        relative_path="quality_data.json",
        tags=Tag.quality_data(),
    )

    # Write a quality report file
    quality_report_file_obj = uuid4().hex.encode("utf8")
    scratch.write(
        quality_report_file_obj,
        relative_path="quality_report.pdf",
        tags=[Tag.output(), Tag.quality_report()],
    )

    # Write a movie file
    movie_file_obj = uuid4().hex.encode("utf8")
    scratch.write(movie_file_obj, relative_path="movie.mp4", tags=[Tag.output(), Tag.movie()])

    # Write an intermediate frame
    intermediate_file_obj = uuid4().hex.encode("utf8")
    scratch.write(
        intermediate_file_obj,
        relative_path="intermediate.fits",
        tags=[Tag.intermediate(), Tag.frame(), Tag.task("FOO")],
    )

    return scratch


@pytest.fixture()
def submit_dataset_metadata_task(
    recipe_run_id, tmp_path, scratch_with_processed_data, fake_constants_db
) -> SubmitDatasetMetadata:
    """An instance of SubmitDatasetMetadata with tagged quality metrics."""
    task = SubmitDatasetMetadata(
        recipe_run_id=recipe_run_id,
        workflow_name="submit_dataset_metadata",
        workflow_version="submit_dataset_metadata_version",
    )
    task.scratch = scratch_with_processed_data
    task.constants._update(fake_constants_db)
    yield task
    task._purge()


def test_submit_dataset_metadata(
    submit_dataset_metadata_task,
    mocker,
    fake_gql_client,
):
    """
    :Given: An instance of SubmitDatasetMetadata with tagged processed data
    :When: SubmitDatasetMetadata is run
    :Then: Metadata files for the dataset are saved to the remote database
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    # intercept these two GraphQLClient calls so they can be confirmed
    mocked_metadata_store_add_dataset_receipt_account = mocker.patch.object(
        metadata_store.MetadataStoreMixin, "metadata_store_add_dataset_receipt_account"
    )
    mocked_metadata_store_add_quality_data = mocker.patch.object(
        metadata_store.MetadataStoreMixin, "metadata_store_add_quality_data"
    )
    task = submit_dataset_metadata_task

    # When
    task()

    # Then
    mocked_metadata_store_add_dataset_receipt_account.assert_called_once()
    mocked_metadata_store_add_quality_data.assert_called_once()
