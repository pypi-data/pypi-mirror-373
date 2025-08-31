"""Wrappers for all workflow tasks."""

import json
import logging
import re
from abc import ABC
from importlib import metadata
from pathlib import Path
from typing import Any
from typing import Generator
from typing import Iterable
from typing import Type

from dkist_processing_core import TaskBase

from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common._util.tags import TagDB
from dkist_processing_common.codecs.bytes import bytes_encoder
from dkist_processing_common.codecs.path import path_decoder
from dkist_processing_common.config import common_configurations
from dkist_processing_common.models.constants import ConstantsBase
from dkist_processing_common.models.tags import StemName
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks.mixin.metadata_store import MetadataStoreMixin

__all__ = ["WorkflowTaskBase", "tag_type_hint"]

logger = logging.getLogger(__name__)

tag_type_hint = Iterable[str] | str


class WorkflowTaskBase(TaskBase, MetadataStoreMixin, ABC):
    """
    Wrapper for all tasks that need to access the persistent automated processing data stores.

    Adds capabilities for accessing:

    `scratch`
    `tags`
    `constants`

    Also includes ability to access the metadata store

    Parameters
    ----------
    recipe_run_id
        The recipe_run_id
    workflow_name
        The workflow name
    workflow_version
        The workflow version
    """

    is_task_manual: bool = False
    record_provenance: bool = False

    def __init__(
        self,
        recipe_run_id: int,
        workflow_name: str,
        workflow_version: str,
    ):
        super().__init__(
            recipe_run_id=recipe_run_id,
            workflow_name=workflow_name,
            workflow_version=workflow_version,
        )
        self.task_name = self.__class__.__name__
        self.scratch = WorkflowFileSystem(recipe_run_id=recipe_run_id, task_name=self.task_name)
        self.constants = self.constants_model_class(
            recipe_run_id=recipe_run_id, task_name=self.task_name
        )
        self.docs_base_url = common_configurations.docs_base_url
        self.filename_counter = TagDB(
            recipe_run_id=recipe_run_id, task_name=self.task_name, namespace="counter"
        )

    # These apm* functions provide tagged spans for APM bliss
    def apm_type_base(
        self,
        name: str,
        *args,
        arg_span_type: str = None,
        arg_labels: dict[str, str] = None,
        **kwargs,
    ):
        """Groom inputs to apm_step to handle various kwarg collisions."""
        if "span_type" in kwargs:
            raise RuntimeError(
                f"Cannot specify 'span_type' {kwargs['span_type']} in step that forces is it to be {arg_span_type}"
            )

        if "labels" in kwargs:
            arg_labels.update(kwargs["labels"])
            del kwargs["labels"]
        logger.info(
            f"Recording APM span: {name = }, {arg_span_type = }, {arg_labels = }, "
            f"recipe_run_id = {self.recipe_run_id}"
        )
        return self.apm_step(name, *args, span_type=arg_span_type, labels=arg_labels, **kwargs)

    def apm_task_step(self, name: str, *args, **kwargs):
        """Span for management/organizational/info type stuff."""
        return self.apm_type_base(
            name, *args, arg_span_type="code.task", arg_labels={"type": "task"}, **kwargs
        )

    def apm_processing_step(self, name: str, *args, **kwargs):
        """Span for computations."""
        return self.apm_type_base(
            name,
            *args,
            arg_span_type="code.processing",
            arg_labels={"type": "processing"},
            **kwargs,
        )

    def apm_writing_step(self, name: str, *args, **kwargs):
        """Span for writing to disk."""
        return self.apm_type_base(
            name, *args, arg_span_type="code.writing", arg_labels={"type": "writing"}, **kwargs
        )

    @property
    def constants_model_class(self) -> Type[ConstantsBase]:
        """Class containing the definitions of pipeline constants."""
        return ConstantsBase

    @property
    def library_versions(self) -> str:
        """Harvest the dependency names and versions from the environment for all packages beginning with 'dkist' or are a requirement for a package beginning with 'dkist'."""
        distributions = {
            d.name.lower().replace("_", "-"): d.version for d in metadata.distributions()
        }
        libraries = {}
        for pkg in metadata.distributions():
            if pkg.name.startswith("dkist"):
                libraries[pkg.name.lower().replace("_", "-")] = pkg.version
                for req in metadata.requires(pkg.name):
                    is_extra_requirement = "extra" in req
                    if not is_extra_requirement:
                        key = re.split(r"[ \[=<>~!]", req.lower())[
                            0
                        ]  # get the raw name of the package
                        libraries[key] = distributions[key]
        return json.dumps(libraries)

    def _record_provenance(self):
        logger.info(
            f"Recording provenance for {self.task_name}: "
            f"recipe_run_id={self.recipe_run_id}, "
            f"is_task_manual={self.is_task_manual}, "
            f"library_versions={self.library_versions}"
        )
        self.metadata_store_record_provenance(
            is_task_manual=self.is_task_manual, library_versions=self.library_versions
        )

    def pre_run(self) -> None:
        """Execute any pre-task setup required."""
        super().pre_run()
        if self.record_provenance or self.is_task_manual:
            with self.apm_task_step("Record Provenance"):
                self._record_provenance()

    def read(
        self, tags: tag_type_hint, decoder: callable = path_decoder, **decoder_kwargs
    ) -> Generator[Any, None, None]:
        """
        Return a generator corresponding to the files associated with the given tags.

        The type returned is dependent on the given `decoder`.

        Parameters
        ----------
        tags
            Tags to search for. Only files associated with ALL tags will be found.

        decoder
            Function to convert raw Paths into something more useful. Must accept `Path` as the input type.

        **decoder_kwargs
            Additional arguments to pass to the `decoder` function.
        """
        return (decoder(p, **decoder_kwargs) for p in self.scratch.find_all(tags=tags))

    def write(
        self,
        data: Any,
        tags: tag_type_hint,
        relative_path: Path | str | None = None,
        overwrite: bool = False,
        encoder: callable = bytes_encoder,
        **encoder_kwargs,
    ) -> Path:
        """
        Write data to a file and tag it using the given tags.

        Parameters
        ----------
        data
            The file to be written

        tags
            The tags to be associated with the file

        relative_path
            The relative path where the file is to be written

        overwrite
            Should the file be overwritten if it already exists?

        encoder
            Function that converts `data` into `bytes`

        **encoder_kwargs
            Additional arguments to pass to the `encoder` function.

        Returns
        -------
        The path for the written file
        """
        file_obj = encoder(data, **encoder_kwargs)
        if isinstance(tags, str):
            tags = [tags]
        else:
            tags = [t for t in tags]  # copy the input list so we don't modify it in place
        tags.append(Tag.workflow_task(self.__class__.__name__))

        relative_path = relative_path or self.build_generic_tag_filename(tags)
        relative_path = Path(relative_path)
        self.scratch.write(
            file_obj=file_obj, relative_path=relative_path, tags=tags, overwrite=overwrite
        )
        return relative_path

    @property
    def filename_tag_order(self) -> list[str]:
        """
        Order of tags to consider when constructing a filename.

        This list does NOT need to contain *all* possible tags, just the ones for which we care about the order.
        """
        return [
            StemName.debug.value,
            StemName.input.value,
            StemName.intermediate.value,
            StemName.calibrated.value,
            StemName.output.value,
            StemName.workflow_task.value,
            StemName.task.value,
            StemName.dsps_repeat.value,
            StemName.cs_step.value,
            StemName.modstate.value,
        ]

    def build_generic_tag_filename(self, tags: list) -> str:
        """
        Build a filename from a set of tags.

        The algorithm is:

         1. Any tag Stems that appear in `self.filename_tag_order` will be joined, in order, along with their values
            (if applicable).

         2. Any remaining tags not in `self.filename_tag_order` are sorted alphabetically and joined to the end of the
            filename.

         3. A counter value is appended to avoid any collisions on files that have the same set of tags.

         4. You can have any extension you want so long as it's ".dat".
        """
        # This call copies the input list so it doesn't get modified in place and flattens the list to allow
        # arbitrarily nested lists.
        copied_tags = self.scratch.parse_tags(tags)
        try:
            copied_tags.remove(StemName.frame.value)
        except ValueError:
            # Not a frame. This is fine.
            pass

        filename_parts = []
        for ordered_tag in self.filename_tag_order:
            tags_with_stem = filter(lambda t: ordered_tag in t, copied_tags)
            for tag in tags_with_stem:
                filename_parts.append(tag)
                copied_tags.remove(tag)

        sorted_remaining_tags = sorted(copied_tags)
        filename_parts += sorted_remaining_tags

        # replace spaces, underscores, and colons with dashes - dynamic part (e.g. polcal `Beam 1` label) may include spaces
        dash_separated_parts = [re.sub("[ _:]", "-", t) for t in filename_parts]

        base_filename = "_".join(dash_separated_parts)
        base_filename_counter = str(self.filename_counter.increment(base_filename))
        return base_filename + "_" + base_filename_counter + ".dat"

    def count(self, tags: tag_type_hint) -> int:
        """
        Return the number of objects tagged with the given tags.

        Parameters
        ----------
        tags
            The tags to be searched

        Returns
        -------
        The number of objects tagged with the given tags
        """
        return self.scratch.count_all(tags=tags)

    def tag(self, path: Path | str, tags: tag_type_hint) -> None:
        """
        Associate the given tags with the given path.

        Wrap the tag method in WorkflowFileSystem.

        Parameters
        ----------
        path
            The input path
        tags
            The tags to be associated with the given path

        Returns
        -------
        None
        """
        return self.scratch.tag(path=path, tags=tags)

    def tags(self, path: Path | str) -> list[str]:
        """
        Return list of tags that a path belongs to.

        Parameters
        ----------
        path
            The input path

        Returns
        -------
        A list of tags associated with the given path.
        """
        return self.scratch.tags(path=path)

    def remove_tags(self, path: Path | str, tags: tag_type_hint) -> None:
        """Remove the association between the given tag(s) and the given path."""
        self.scratch.remove_tags(path, tags)

    def _purge(self):
        """Purge the persistent stores associated with the workflow to which this task belongs e.g. when testing."""
        self.scratch.purge()
        self.constants._purge()
        self.filename_counter.purge()

    def rollback(self):
        """

        Remove changes made by this task from the persistent stores.

        This differs from _purge() in that it attempts to be more surgical.

        Finally, the recipe run is ensured to be in an Inprogress state.

        Scratch: Rolls back files written and tags newly added by this task

        Constants: Rolls back constants whose values were set by this task

        Filename Counter: not rolled back but its purpose of preventing file name collisions is not impacted
        """
        super().rollback()
        with self.apm_writing_step("Rollback Scratch"):
            self.scratch.rollback()
        with self.apm_writing_step("Rollback Constants"):
            self.constants._rollback()
        with self.apm_task_step("Change Recipe Run to Inprogress"):
            self.metadata_store_change_recipe_run_to_inprogress()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self.scratch.close()
        self.constants._close()
        self.filename_counter.close()
