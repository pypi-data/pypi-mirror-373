"""Base class that supports common output data methods and paths."""

import logging
from abc import ABC
from abc import abstractmethod
from functools import cached_property
from pathlib import Path

from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_processing_common.tasks.mixin.globus import GlobusTransferItem
from dkist_processing_common.tasks.mixin.object_store import ObjectStoreMixin

logger = logging.getLogger(__name__)


class OutputDataBase(WorkflowTaskBase, ABC):
    """Subclass of WorkflowTaskBase which encapsulates common output data methods."""

    @cached_property
    def destination_bucket(self) -> str:
        """Get the destination bucket."""
        return self.metadata_store_recipe_run.configuration.destination_bucket

    def format_object_key(self, path: Path) -> str:
        """
        Convert output paths into object store keys.

        Parameters
        ----------
        path: the Path to convert

        Returns
        -------
        formatted path in the object store
        """
        object_key = self.destination_folder / Path(path.name)
        return str(object_key)

    @property
    def destination_folder(self) -> Path:
        """Format the destination folder."""
        return self.destination_root_folder / Path(self.constants.dataset_id)

    @property
    def destination_root_folder(self) -> Path:
        """Format the destination root folder."""
        return Path(self.constants.proposal_id)

    @property
    def output_frame_tags(self) -> list[str]:
        """Tags that uniquely identify L1 fits frames i.e. the dataset-inventory-able frames."""
        return [Tag.output(), Tag.frame()]


class TransferDataBase(OutputDataBase, ObjectStoreMixin, ABC):
    """Base class for transferring data from scratch to somewhere else."""

    def run(self) -> None:
        """Transfer the data and cleanup any folders."""
        with self.apm_task_step("Transfer objects"):
            self.transfer_objects()

        with self.apm_task_step("Remove folder objects"):
            self.remove_folder_objects()

    @abstractmethod
    def transfer_objects(self):
        """Collect objects and transfer them."""
        pass

    def build_output_frame_transfer_list(self) -> list[GlobusTransferItem]:
        """Build a list of GlobusTransfer items corresponding to all OUTPUT (i.e., L1) frames."""
        science_frame_paths: list[Path] = list(self.read(tags=self.output_frame_tags))

        transfer_items = []
        for p in science_frame_paths:
            object_key = self.format_object_key(p)
            destination_path = Path(self.destination_bucket, object_key)
            item = GlobusTransferItem(
                source_path=p,
                destination_path=destination_path,
            )
            transfer_items.append(item)

        return transfer_items

    def remove_folder_objects(self):
        """Remove folder objects that would have been added by the Globus transfer."""
        removed_object_keys = self.object_store_remove_folder_objects(
            bucket=self.destination_bucket, path=self.destination_root_folder
        )
        logger.info(
            f"Removed folder objects in {self.destination_bucket} bucket. {removed_object_keys=}"
        )

    def rollback(self):
        """

        Rollback a Transfer Task.

        Globus transfers are not dependent upon the task once they are submitted.  Rolling back this task may not be achievable action on the destination.
        """
        super().rollback()
        logger.warning(f"Transferred objects may still exist at the destination.")
