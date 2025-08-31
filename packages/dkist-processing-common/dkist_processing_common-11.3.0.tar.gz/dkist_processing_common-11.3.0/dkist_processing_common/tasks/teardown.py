"""Task(s) for the clean up tasks at the conclusion of a processing pipeline."""

import logging
from abc import ABC
from abc import abstractmethod

from dkist_processing_common.tasks.base import WorkflowTaskBase

__all__ = ["Teardown", "TrialTeardown"]


logger = logging.getLogger(__name__)


class TeardownBase(WorkflowTaskBase, ABC):
    """
    Changes the status of the recipe run to a success status.

    Deletes the scratch directory containing all data from this pipeline run
    """

    @property
    def teardown_enabled(self) -> bool:
        """Recipe run configuration indicating if data should be removed at the end of a run."""
        return self.metadata_store_recipe_run.configuration.teardown_enabled

    def run(self) -> None:
        """Run method for Teardown class."""
        with self.apm_task_step("Change recipe run status"):
            self.change_recipe_run_status_to_success()

        if not self.teardown_enabled:
            with self.apm_task_step(f"Skip Teardown"):
                return

        logger.info(f"Removing data and tags for recipe run {self.recipe_run_id}")
        self.teardown()

    @abstractmethod
    def change_recipe_run_status_to_success(self):
        """Set the status of this recipe run to a version of success."""
        pass

    def teardown(self):
        """Purge all constants and files/tags in scratch."""
        with self.apm_task_step("Remove Data and Tags"):
            self.scratch.purge()

        with self.apm_task_step("Remove File Counters"):
            self.filename_counter.purge()

        with self.apm_task_step("Remove Constants"):
            self.constants._purge()


class Teardown(TeardownBase):
    """
    Teardown class for standard use.

    The success status is COMPLETEDSUCCESSFULLY and is considered complete.
    """

    def change_recipe_run_status_to_success(self):
        """Change the recipe run status to COMPLETEDSUCCESSFULLY."""
        self.metadata_store_change_recipe_run_to_completed_successfully()


class TrialTeardown(TeardownBase):
    """
    Teardown class for trial runs.

    The success status is TRIALSUCCESS and is NOT considered complete.
    """

    def change_recipe_run_status_to_success(self):
        """Change the recipe run status to TRIALSUCCESS."""
        self.metadata_store_change_recipe_run_to_trial_success()
