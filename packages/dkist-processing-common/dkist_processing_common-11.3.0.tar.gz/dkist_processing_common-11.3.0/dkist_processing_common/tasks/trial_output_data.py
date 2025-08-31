"""Tasks to support transferring an arbitrary collection of files to a customizable post-run location."""

import logging
from functools import cached_property
from pathlib import Path

from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks.mixin.globus import GlobusMixin
from dkist_processing_common.tasks.mixin.globus import GlobusTransferItem
from dkist_processing_common.tasks.output_data_base import TransferDataBase

logger = logging.getLogger(__name__)

__all__ = ["TransferTrialData"]


class TransferTrialData(TransferDataBase, GlobusMixin):
    """
    Class for transferring data to a customizable post-run location.

    Provides the basic framework of locating and transferring data. Defaults to all product files, but a
    specific subset of files may be transferred by defining `trial_exclusive_transfer_tag_lists` in the
    recipe run configuration.

    Convenience properties provide common sets of tags:

    o `output_frame_tag_list` - List of tags list for output frames

    o `debug_frame_tag_list` - List of tags list for frames tagged with DEBUG

    o `intermediate_frame_tag_list` - List of tags list for frames tagged with INTERMEDIATE

    o `ancillaries_tag_list` - List of tags lists for ancillary products:
    dataset inventory, asdf, quality data, quality report, movie
    """

    def transfer_objects(self) -> None:
        """Collect transfer items and send them to Globus for transfer."""
        with self.apm_task_step("Build transfer list"):
            transfer_manifest = self.build_transfer_list()

        with self.apm_task_step("Send transfer manifest to globus"):
            self.transfer_all_trial_frames(transfer_manifest)

    @cached_property
    def destination_bucket(self) -> str:
        """Get the destination bucket."""
        return self.metadata_store_recipe_run.configuration.destination_bucket

    @property
    def destination_root_folder(self) -> Path:
        """Format the destination root folder with a value that can be set in the recipe run configuration."""
        root_name_from_config = (
            self.metadata_store_recipe_run.configuration.trial_root_directory_name
        )
        root_name = Path(root_name_from_config or super().destination_root_folder)
        return root_name

    @property
    def destination_folder(self) -> Path:
        """Format the destination folder with a parent that can be set by the recipe run configuration."""
        dir_name_from_config = self.metadata_store_recipe_run.configuration.trial_directory_name
        dir_name = dir_name_from_config or Path(self.constants.dataset_id)
        return self.destination_root_folder / dir_name

    @property
    def transfer_tag_lists(self) -> list[list[str]]:
        """Return list of tag lists that define specific files we want to transfer to the trial location.

        Defaults to transferring all product files.  Setting `trial_exclusive_transfer_tag_lists` in the
        recipe run configuration to a list of tag lists will override the default.
        """
        tag_list_from_config = (
            self.metadata_store_recipe_run.configuration.trial_exclusive_transfer_tag_lists
        )
        if tag_list_from_config is not None:
            return tag_list_from_config
        return self.default_transfer_tag_lists

    @property
    def output_frame_tag_list(self) -> list[list[str]]:
        """List of tag list for output frames."""
        return [self.output_frame_tags]

    @property
    def debug_frame_tag_list(self) -> list[list[str]]:
        """List of tag list for frames tagged with DEBUG."""
        tag_list = [[Tag.debug(), Tag.frame()]]
        return tag_list

    @property
    def intermediate_frame_tag_list(self) -> list[list[str]]:
        """List of tag list for frames tagged with INTERMEDIATE."""
        tag_list = [[Tag.intermediate(), Tag.frame()]]
        return tag_list

    @property
    def ancillaries_tag_list(self) -> list[list[str]]:
        """List of tag lists for the ancillaries: inventory, asdf, quality data, quality report, and movie."""
        tag_list = []
        tag_list += [[Tag.output(), Tag.dataset_inventory()]]
        tag_list += [[Tag.output(), Tag.asdf()]]
        tag_list += [[Tag.quality_data()]]  # quality data is not tagged as OUTPUT
        tag_list += [[Tag.output(), Tag.quality_report()]]
        tag_list += [[Tag.output(), Tag.movie()]]
        return tag_list

    @property
    def default_transfer_tag_lists(self) -> list[list[str]]:
        """Build the default list of all items to transfer to the trial locations."""
        transfer_tag_lists = self.output_frame_tag_list
        transfer_tag_lists += self.debug_frame_tag_list
        transfer_tag_lists += self.intermediate_frame_tag_list
        transfer_tag_lists += self.ancillaries_tag_list

        return transfer_tag_lists

    def build_transfer_list(self) -> list[GlobusTransferItem]:
        """
        Build a transfer list containing all files that are tagged with any of the sets of input tags.

        Unless specified otherwise in the recipe run configuration, the default is to transfer all product files.
        If specified in the recipe run configuration, `trial_exclusive_transfer_tag_lists` must be a list of tag set
        lists.  If the list is [[tag1, tag2]], then the resulting transfer list will contain all files that have both
        tag1 and tag2.  If the list is [[tag1], [tag2]], then the resulting transfer list will contain all files that
        have tag1 and/or tag2.  Combining both methods, if the list is [[tag1, tag2], [tag3, tag4]] then the
        resulting transfer list will contain:

        ALL(both tag1 and tag2) + ALL(both tag3 and tag4).
        """
        tag_lists = self.transfer_tag_lists

        transfer_items = []
        for tag_set in tag_lists:

            paths = self.read(tags=tag_set)
            for p in paths:
                destination_object_key = self.format_object_key(p)
                destination_path = Path(self.destination_bucket, destination_object_key)
                item = GlobusTransferItem(source_path=p, destination_path=destination_path)
                transfer_items.append(item)

        return list(set(transfer_items))

    def transfer_all_trial_frames(self, transfer_items: list[GlobusTransferItem]) -> None:
        """Send a list of transfer items to Globus for transfer."""
        logger.info(
            f"Preparing globus transfer {len(transfer_items)} items: "
            f"recipe_run_id={self.recipe_run_id}. "
            f"transfer_items={transfer_items[:3]}..."
        )

        self.globus_transfer_scratch_to_object_store(
            transfer_items=transfer_items,
            label=f"Transfer frames for trial run of recipe_run_id {self.recipe_run_id}",
        )
