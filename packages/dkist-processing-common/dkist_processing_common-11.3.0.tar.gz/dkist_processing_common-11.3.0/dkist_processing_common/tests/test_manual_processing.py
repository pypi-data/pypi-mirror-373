import pytest

from dkist_processing_common.manual import ManualProcessing
from dkist_processing_common.tasks import WorkflowTaskBase


class ProvenanceTask(WorkflowTaskBase):
    record_provenance = True

    def run(self): ...


@pytest.fixture(scope="function")
def manual_processing_run(tmp_path, recipe_run_id):
    with ManualProcessing(
        recipe_run_id=recipe_run_id,
        workflow_path=tmp_path,
        workflow_name="manual",
        workflow_version="manual",
    ) as manual_processing_run:
        yield manual_processing_run


def test_manual_record_provenance(tmp_path, recipe_run_id, manual_processing_run):
    """
    Given: A WorkflowTaskBase subclass with provenance recording turned on
    When: Running the task with the ManualProcessing wrapper
    Then: The provenance record exists on disk
    """
    manual_processing_run.run_task(task=ProvenanceTask)
    directory = tmp_path / str(recipe_run_id)
    provenance_file = directory / "ProvenanceTask_provenance.json"
    assert provenance_file.exists()
