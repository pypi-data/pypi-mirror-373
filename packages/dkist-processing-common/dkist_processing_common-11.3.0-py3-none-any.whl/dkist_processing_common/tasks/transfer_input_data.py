"""Task(s) for the transfer in of data sources for a processing pipeline."""

import logging
from pathlib import Path

from dkist_processing_common.codecs.basemodel import basemodel_decoder
from dkist_processing_common.codecs.basemodel import basemodel_encoder
from dkist_processing_common.models.input_dataset import InputDatasetObject
from dkist_processing_common.models.input_dataset import InputDatasetPartDocumentList
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks.base import WorkflowTaskBase
from dkist_processing_common.tasks.mixin.globus import GlobusMixin
from dkist_processing_common.tasks.mixin.globus import GlobusTransferItem

__all__ = ["TransferL0Data"]

logger = logging.getLogger(__name__)


class TransferL0Data(WorkflowTaskBase, GlobusMixin):
    """Transfers Level 0 data and required parameter files to the scratch store."""

    def download_input_dataset(self):
        """Write the input dataset part documents to scratch with appropriate tags."""
        if observe_frames_part := self.metadata_store_input_dataset_observe_frames:
            doc = observe_frames_part.inputDatasetPartDocument
            self.write(data=doc, tags=Tag.input_dataset_observe_frames(), encoder=basemodel_encoder)
        if calibration_frames_part := self.metadata_store_input_dataset_calibration_frames:
            doc = calibration_frames_part.inputDatasetPartDocument
            self.write(
                data=doc, tags=Tag.input_dataset_calibration_frames(), encoder=basemodel_encoder
            )
        if parameters_part := self.metadata_store_input_dataset_parameters:
            doc = parameters_part.inputDatasetPartDocument
            self.add_file_tags_to_parameters_doc(param_doc=doc)
            self.write(data=doc, tags=Tag.input_dataset_parameters(), encoder=basemodel_encoder)

    def add_file_tags_to_parameters_doc(self, param_doc: InputDatasetPartDocumentList):
        """Update the input dataset document with the location of the file parameters."""
        for doc_item in param_doc.doc_list:
            for obj in doc_item.input_dataset_objects:
                obj.tag = Tag.parameter(Path(obj.object_key).name)

    def format_transfer_items(
        self, input_dataset_objects: list[InputDatasetObject]
    ) -> list[GlobusTransferItem]:
        """Format a list of InputDatasetObject(s) as GlobusTransferItem(s)."""
        transfer_items = []
        for obj in input_dataset_objects:
            source_path = Path("/", obj.bucket, obj.object_key)
            destination_path = self.scratch.absolute_path(obj.object_key)
            transfer_items.append(
                GlobusTransferItem(
                    source_path=source_path,
                    destination_path=destination_path,
                    recursive=False,
                )
            )
        return transfer_items

    def build_transfer_list(self, doc_tag: str) -> list[InputDatasetObject]:
        """Format the list of frames as transfer items to be used by globus."""
        doc = next(
            self.read(tags=doc_tag, decoder=basemodel_decoder, model=InputDatasetPartDocumentList),
            None,
        )
        doc_list = doc.doc_list if doc else []
        input_dataset_objects = []
        for doc_item in doc_list:
            input_dataset_objects += doc_item.input_dataset_objects
        return input_dataset_objects

    def tag_transfer_objects(self, input_dataset_objects: list[InputDatasetObject]) -> None:
        """Tag all the transferred input files."""
        for obj in input_dataset_objects:
            obj_path = self.scratch.absolute_path(obj.object_key)
            if obj.tag:
                self.tag(obj_path, tags=obj.tag)
            else:
                self.tag(obj_path, tags=[Tag.input(), Tag.frame()])

    def run(self) -> None:
        """Execute the data transfer."""
        with self.apm_task_step("Change Status to InProgress"):
            self.metadata_store_change_recipe_run_to_inprogress()

        with self.apm_task_step("Download Input Dataset Documents"):
            self.download_input_dataset()

        with self.apm_task_step("Build Input Dataset Transfer List"):
            observe_transfer_objects = self.build_transfer_list(
                doc_tag=Tag.input_dataset_observe_frames()
            )
            calibration_transfer_objects = self.build_transfer_list(
                doc_tag=Tag.input_dataset_calibration_frames()
            )
            parameter_transfer_objects = self.build_transfer_list(
                doc_tag=Tag.input_dataset_parameters()
            )
            transfer_objects = (
                observe_transfer_objects + calibration_transfer_objects + parameter_transfer_objects
            )
            if len(observe_transfer_objects + calibration_transfer_objects) == 0:
                raise ValueError("No input dataset frames found to transfer")

        with self.apm_task_step("Transfer Input Frames and Parameter Files via Globus"):
            self.globus_transfer_object_store_to_scratch(
                transfer_items=self.format_transfer_items(input_dataset_objects=transfer_objects),
                label=f"Transfer Input Objects for Recipe Run {self.recipe_run_id}",
            )

        with self.apm_processing_step("Tag Input Frames and Parameter Files"):
            self.tag_transfer_objects(input_dataset_objects=transfer_objects)

    def rollback(self):
        """Warn that depending on the progress of the task all data may not be removed because it hadn't been tagged."""
        super().rollback()
        logger.warning(
            f"Rolling back only removes data that has been tagged.  The data persisted by this task may not have been tagged prior to rollback."
        )
