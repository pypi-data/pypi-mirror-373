"""Task wrapper for manual execution outside the workflow engine."""

import json
import logging
import shutil
from pathlib import Path
from typing import Callable
from unittest.mock import patch

from dkist_processing_core.task import TaskBase

from dkist_processing_common.codecs.basemodel import basemodel_encoder
from dkist_processing_common.models.graphql import RecipeRunProvenanceMutation
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks.base import WorkflowTaskBase
from dkist_processing_common.tests.mock_metadata_store import fake_gql_client_factory

logger = logging.getLogger(__name__)


class ManualProcessing:
    """Task wrapper for manual execution outside the workflow engine."""

    def __init__(
        self,
        workflow_path: Path,
        recipe_run_id: int = 1,
        testing: bool = False,
        workflow_name: str = "manual",
        workflow_version: str = "manual",
    ):
        self.workflow_path = workflow_path
        self.recipe_run_id = recipe_run_id
        self.testing = testing
        self.workflow_name = workflow_name
        self.workflow_version = workflow_version

    def run_task(self, task: Callable) -> None:
        """
        Wrap the .run() method on a DKIST processing pipeline task.

        Parameters
        ----------
        task: Callable
            task object that subclasses TaskBase
        Returns
        -------
        None
        """
        if not issubclass(task, TaskBase):
            raise RuntimeError(
                "Task is not a valid DKIST processing task. "
                "Must be a subclass of dkist_processing_core.task.TaskBase"
            )
        with task(
            recipe_run_id=self.recipe_run_id,
            workflow_name=self.workflow_name,
            workflow_version=self.workflow_version,
        ) as t:
            t.scratch.scratch_base_path = self.workflow_path
            t.scratch.workflow_base_path = Path(t.scratch.scratch_base_path) / str(
                self.recipe_run_id
            )
            if self.testing:
                task.metadata_store_recipe_id = self.recipe_run_id + 1
                task.metadata_store_recipe_instance_id = self.recipe_run_id + 2

            with patch(
                "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient",
                new=fake_gql_client_factory(),
            ) as foo:
                # Run the task with a FakeGQLClient. This will handle pre_run(), run(), and post_run()
                with patch(
                    "dkist_processing_common.tasks.base.MetadataStoreMixin.metadata_store_record_provenance",
                    new=writing_metadata_store_record_provenance,
                ) as bar:
                    # Also run the task with a version of metadata_store_record_provenance that just writes the
                    #  records to disk
                    t()

        logger.info(f"Task {task.__name__} completed")

    def purge_tags_and_constants(self) -> None:
        """
        Remove all filepath tags and constants from the associated objects.

        Run at the end of a manual processing run.

        Returns
        -------
        None
        """

        class PurgeTagsAndConstants(WorkflowTaskBase):
            def run(self):
                pass

        t = PurgeTagsAndConstants(
            recipe_run_id=self.recipe_run_id, workflow_name="manual", workflow_version="manual"
        )
        t.scratch._tag_db.purge()
        t.constants._purge()
        logger.info(f"Constants and filepath tags purged for recipe run id {self.recipe_run_id}")

    def tag_inputs(self) -> None:
        """Tag the input fits files and json files."""

        class TagInputs(WorkflowTaskBase):
            def run(self):
                for file in self.scratch.workflow_base_path.glob("*.FITS"):
                    self.tag(path=file, tags=[Tag.input(), Tag.frame()])
                for file in self.scratch.workflow_base_path.glob("*observe.json"):
                    self.tag(path=file, tags=[Tag.input_dataset_observe_frames()])
                for file in self.scratch.workflow_base_path.glob("*calibration.json"):
                    self.tag(path=file, tags=[Tag.input_dataset_calibration_frames()])
                for file in self.scratch.workflow_base_path.glob("*parameters.json"):
                    self.tag(path=file, tags=[Tag.input_dataset_parameters()])

        with TagInputs(
            recipe_run_id=self.recipe_run_id, workflow_name="manual", workflow_version="manual"
        ) as t:
            t.scratch.workflow_base_path = Path(self.workflow_path) / str(self.recipe_run_id)
            t()

    def copy_input_files(self, source_dir: str):
        """Create a copy of the input files."""

        class CopyInputFiles(WorkflowTaskBase):
            def run(self):
                shutil.copytree(
                    source_dir, self.scratch.workflow_base_path.as_posix(), dirs_exist_ok=True
                )

        with CopyInputFiles(
            recipe_run_id=self.recipe_run_id, workflow_name="manual", workflow_version="manual"
        ) as t:
            t.scratch.workflow_base_path = Path(self.workflow_path) / str(self.recipe_run_id)
            t()

    def count_provenance(self) -> None:
        """
        Log an INFO message that enumerates the provenance records found in the database.

        This only works because we patch in a provenance recorder that writes the records to disk.
        See `run_task`
        """

        class CountProvenanceRecords(WorkflowTaskBase):
            def run(self):
                provenance_records = list(self.read(tags=["PROVENANCE_RECORD"]))
                logger.info(f"Found {len(provenance_records)} provenance records:")
                for r in provenance_records:
                    logger.info(f"\t{r}")

        with CountProvenanceRecords(
            recipe_run_id=self.recipe_run_id, workflow_name="manual", workflow_version="manual"
        ) as t:
            t.scratch.workflow_base_path = Path(self.workflow_path) / str(self.recipe_run_id)
            t()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.purge_tags_and_constants()


def writing_metadata_store_record_provenance(self, is_task_manual: bool, library_versions: str):
    """
    Write the provenance record to scratch.

    A copy of metadata_store_record_provenance that writes the record to scratch and tags with PROVENANCE RECORD.
    """
    params = RecipeRunProvenanceMutation(
        inputDatasetId=1234,
        isTaskManual=is_task_manual,
        recipeRunId=self.recipe_run_id,
        taskName=self.task_name,
        libraryVersions=library_versions,
        workflowVersion=self.workflow_version,
    )
    self.write(
        data=params,
        encoder=basemodel_encoder,
        tags=["PROVENANCE_RECORD"],
        relative_path=f"{self.task_name}_provenance.json",
        overwrite=True,
    )
