"""Scratch file system api."""

import logging
from contextlib import contextmanager
from os import umask
from pathlib import Path
from shutil import rmtree
from typing import Generator

from dkist_processing_common._util.tags import TagDB
from dkist_processing_common.config import common_configurations

logger = logging.getLogger(__name__)


class WorkflowFileSystem:
    """
    Wrapper for interactions with the shared file system "scratch" supporting recipe run id based namespaces and tagged data.

    Create a workflow file system object.

    Parameters
    ----------
    recipe_run_id
        The recipe_run_id
    task_name
        The task_name
    scratch_base_path
        The base path at which to create the file system

    """

    def __init__(
        self,
        recipe_run_id: int = 0,
        task_name: str = "dev_task",
        scratch_base_path: Path | str | None = None,
    ):
        self.recipe_run_id = recipe_run_id
        self.task_name = task_name
        if not scratch_base_path:
            scratch_base_path = common_configurations.scratch_base_path
        self.scratch_base_path = scratch_base_path
        self.workflow_base_path = Path(self.scratch_base_path) / str(recipe_run_id)
        with self._mask():
            self.workflow_base_path.mkdir(parents=True, exist_ok=True)
        self._tag_db = TagDB(recipe_run_id=self.recipe_run_id, task_name=self.task_name)
        self._audit_db = TagDB(
            recipe_run_id=self.recipe_run_id, task_name=self.task_name, namespace="scratch_audit"
        )
        self._audit_write_tag = f"WRITE_{self.task_name}"
        self._audit_tag_tag = f"TAG_{self.task_name}"
        self._audit_new_tag_cache = dict()

    @staticmethod
    @contextmanager
    def _mask():
        """Set a permissive umask to allow other users (e.g. globus) to modify resources created by the scratch library."""
        old_mask = umask(0)
        try:
            yield
        finally:
            umask(old_mask)

    def absolute_path(self, relative_path: Path | str) -> Path:
        """
        Convert a relative path to an absolute path with the base directories for the that workflow instance.

        Parameters
        ----------
        relative_path
            The relative_path input

        Returns
        -------
        The absolute path.
        """
        relative_path = Path(relative_path)
        if relative_path.is_absolute():
            raise ValueError("Relative path must be relative")

        return self.workflow_base_path / relative_path

    @staticmethod
    def parse_tags(tags: str | list | None) -> list:
        """Parse tags to support an individual tag in the form of a string or an arbitrarily nested list of strings."""
        if tags is None:
            return []
        if isinstance(tags, str):
            return [tags]
        return _flatten_list(tags)

    def write(
        self,
        file_obj: bytes,
        relative_path: Path | str,
        tags: str | list | None = None,
        overwrite: bool = False,
    ) -> None:
        """
        Write a file object to the path specified and tagged with any tags listed in tags.

        Parameters
        ----------
        file_obj
            The file object to be written
        relative_path
            The relative path at which to write the file
        tags
            The tags to be associated with the file object
        overwrite
            Should the file be overwritten if it already exists?

        Returns
        -------
        None
        """
        tags = self.parse_tags(tags)
        path = self.absolute_path(relative_path)
        # audit the path that was written to scratch
        self._audit_db.add(tag=self._audit_write_tag, value=str(path))
        with self._mask():
            path.parent.mkdir(parents=True, exist_ok=True)
            if overwrite:
                mode = "wb"
            else:
                mode = "xb"
            with path.open(mode=mode) as f:
                f.write(file_obj)
        self.tag(path, tags)

    def delete(self, path: Path | str):
        """
        Delete the file or path.

        Parameters
        ----------
        path
            The path to be deleted

        Returns
        -------
        None
        """
        path = Path(path)
        path.unlink(missing_ok=True)
        self._tag_db.clear_value(value=path)

    def tag(self, path: Path | str, tags: list | str) -> None:
        """
        Tag existing paths.

        The path must be relative to the WorkflowFileSystem base path and must exist.

        Parameters
        ----------
        path
            The path to tag
        tags
            The tags associated with the path.

        Returns
        -------
        None
        """
        tags = self.parse_tags(tags)
        path = Path(path)
        if not (self.workflow_base_path in path.parents):
            raise ValueError(
                f"Cannot tag paths which are not children of the base path {self.workflow_base_path}"
            )
        if not path.exists():
            raise FileNotFoundError(f"Cannot tag paths which do not exist. {path=}")

        for tag in tags:
            # audit the tag that was newly added to the scratch tag db
            if self._tag_is_new(tag=tag):
                self._audit_db.add(tag=self._audit_tag_tag, value=tag)
            self._tag_db.add(tag, str(path))

    def _tag_is_new(self, tag: str) -> bool:
        if self._audit_new_tag_cache.get(tag, None) is None:
            tag_is_new = not bool(self._tag_db.all(tags=tag))
            self._audit_new_tag_cache[tag] = tag_is_new
        return self._audit_new_tag_cache[tag]

    def tags(self, path: Path | str):
        """
        Return the tags associated with the given file object.

        Parameters
        ----------
        path
            The input file object
        Returns
        -------
        An iterable containing the tags associated with the file
        """
        value = str(path)
        return self._tag_db.tags_for_value(value=value)

    def remove_tags(self, path: Path | str, tags: list | str) -> None:
        """Remove a tag or tags from a given path."""
        tags = self.parse_tags(tags)
        for tag in tags:
            self._tag_db.remove(tag, str(path))

    def find_any(self, tags: str | list) -> Generator[Path, None, None]:
        """
        Return a generator of Path objects that are tagged by the union of the input tags.

        Parameters
        ----------
        tags
            The tags to be used in the search

        Returns
        -------
        A generator of path objects matching the union of the desired tags
        """
        tags = self.parse_tags(tags)
        paths = self._tag_db.any(tags)
        logger.debug(f"Found {len(paths)} files containing the set of {tags=}")
        for path in paths:
            yield Path(path)

    def find_all(self, tags: str | list) -> Generator[Path, None, None]:
        """
        Return a generator of Path objects that are tagged by the intersection of the input tags.

        Parameters
        ----------
        tags
            The tags to be used in the search

        Returns
        -------
        A generator of path objects matching the intersection of the desired tags
        """
        tags = self.parse_tags(tags)
        paths = self._tag_db.all(tags)
        logger.debug(f"Found {len(paths)} files containing the set of {tags=}")
        for path in paths:
            yield Path(path)

    def count_any(self, tags: str | list) -> int:
        """
        Return the number of objects that are tagged by the union of the input tags.

        Parameters
        ----------
        tags
            The tags to be used in the search

        Returns
        -------
        The number of objects tagged with the union of the input tags.
        """
        tags = self.parse_tags(tags)
        return len(self._tag_db.any(tags))

    def count_all(self, tags: str | list) -> int:
        """
        Return the number of objects that are tagged by the intersection of the input tags.

        Parameters
        ----------
        tags
            The tags to be used in the search

        Returns
        -------
        The number of objects tagged with the intersection of the input tags.

        """
        tags = self.parse_tags(tags)
        return len(self._tag_db.all(tags))

    def close(self):
        """Close the db connection.  Call on __exit__ of a Task."""
        self._tag_db.close()
        self._audit_db.close()

    def purge(self, ignore_errors: bool = False):
        """
        Remove all data (tags, files, and folders) for the instance.

        Call when tearing down a workflow

        Parameters
        ----------
        ignore_errors
            If set, errors will be ignored, otherwise stop at the first error
        Returns
        -------
        None
        """
        rmtree(self.workflow_base_path, ignore_errors=ignore_errors)
        self._tag_db.purge()
        self._audit_db.purge()

    def rollback(self):
        """Remove all files and new tags associated with the instance recipe run id and task name."""
        # remove files
        for path in self._audit_db.all(tags=self._audit_write_tag):
            path = Path(path)
            path.unlink(missing_ok=True)
            self._tag_db.clear_value(path)
        # remove tags
        for tag in self._audit_db.all(tags=self._audit_tag_tag):
            self._tag_db.clear_tag(tag=tag)
        # remove audit
        self._audit_db.clear_tag(tag=self._audit_write_tag)
        self._audit_db.clear_tag(tag=self._audit_tag_tag)

    def __repr__(self):
        return f"WorkflowFileSystem(recipe_run_id={self.recipe_run_id}, task_name={self.task_name}, scratch_base_path={self.scratch_base_path})"

    def __str__(self):
        return f"{self!r} connected to {self._tag_db}"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def _flatten_list(elements: list) -> list:
    """Flatten an arbitrarily nested list."""
    result = []
    for element in elements:
        if isinstance(element, list):
            result.extend(_flatten_list(element))
        else:
            result.append(element)
    return result
