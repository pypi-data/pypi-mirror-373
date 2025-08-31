"""Tag cloud manager."""

from pathlib import Path
from typing import Iterable

from redis import Redis
from redis.backoff import FullJitterBackoff
from redis.exceptions import ConnectionError
from redis.retry import Retry

from dkist_processing_common.config import common_configurations


class TagDB:
    """
    Class for managing the tags database used to process and manage input data.

    Initialize a connection to a tag database whose instance is uniquely identified by the recipe_run_id and whose client connection is identified with the task_name.

    Parameters
    ----------
    recipe_run_id
        The recipe_run_id
    task_name
        The task_name
    namespace
        The namespace within the recipe_run_id
    """

    def __init__(self, recipe_run_id: int, task_name: str, namespace: str = "path"):
        self.recipe_run_id = recipe_run_id
        self.task_name = task_name
        self._db = self.recipe_run_id % common_configurations.scratch_inventory_max_db_index
        self.namespace = f"{self.recipe_run_id}:{namespace}:"
        connection_name = f"{self.namespace}{self.task_name}"
        scratch_inventory = common_configurations.scratch_inventory_mesh_service
        self.db_retry = Retry(
            backoff=FullJitterBackoff(), retries=3, supported_errors=(ConnectionError,)
        )
        self.db = Redis(
            db=self._db,
            host=scratch_inventory.host,
            port=scratch_inventory.port,
            client_name=connection_name,
            retry_on_error=[
                ConnectionError,
            ],
            retry=self.db_retry,
        )

    @staticmethod
    def _format_query_result(result: list[bytes]) -> set[str]:
        return {r.decode("utf8") for r in result}

    def _add_name_space(self, tags: Iterable[str] | str) -> Iterable[str] | str:
        if isinstance(tags, str):
            return self.namespace + tags
        return [f"{self.namespace}{t}" for t in tags]

    def _remove_name_space(self, raw_tags: Iterable[bytes] | bytes) -> list[str]:
        prefix_length = len(self.namespace)
        if isinstance(raw_tags, bytes):
            raw_tags = [raw_tags]
        return [str(k[prefix_length:], "UTF-8") for k in raw_tags]

    def add(self, tag: str, value: str):
        """
        Add values to a tag.

        Parameters
        ----------
        tag
            The tag
        value
            The value to be associated with the tag

        Returns
        -------
        None
        """
        tag = self._add_name_space(tag)
        self.db.sadd(tag, value)

    def increment(self, tag: str) -> int:
        """
        Increments the number stored in a tag by one.

        If the key does not exist, it is set to 0 before performing the operation.
        https://redis.io/commands/incr/

        Parameters
        ----------
        tag
            The tag to increment

        Returns
        -------
        Integer value of the tag
        """
        tag = self._add_name_space(tag)
        return self.db.incr(tag)

    def clear_tag(self, tag: str) -> None:
        """
        Remove a tag from the database.

        Parameters
        ----------
        tag
            The tag to be removed

        Returns
        -------
        None
        """
        tag = self._add_name_space(tag)
        self.db.delete(tag)

    def clear_value(self, value: Path | str) -> None:
        """
        Remove a value from all tags in the DB.

        Parameters
        ----------
        value
            The value to be removed

        Returns
        -------
        None
        """
        for tag in self.tags:
            self.remove(tag, value)

    def remove(self, tag: str, value: Path | str) -> None:
        """
        Remove a value from a specific tag.

        Parameters
        ----------
        tag
            The tag
        value
            The value to be removed

        Returns
        -------
        None
        """
        if isinstance(value, Path):
            value = str(value)
        self.db.srem(self._add_name_space(tag), value)

    def any(self, tags: Iterable[str] | str) -> set[str]:
        """
        Return a set of values that match any of the tags.

        Parameters
        ----------
        tags
            The input tags

        Returns
        -------
        A set of values matching any of the tags
        """
        tags = self._add_name_space(tags)
        r = self.db.sunion(tags)
        return self._format_query_result(r)

    def all(self, tags: Iterable[str] | str) -> set[str]:
        """
        Return a set of values that match all of the tags.

        Parameters
        ----------
        tags
            The tags to be matched
        Returns
        -------
        A set of values matching all of the tags
        """
        tags = self._add_name_space(tags)
        r = self.db.sinter(tags)
        return self._format_query_result(r)

    def tags_for_value(self, value: str) -> Iterable[str]:
        """
        Return list of tags assigned to a value.

        Parameters
        ----------
        value
            The value to be matched

        Returns
        -------
        A list of tags assigned to the value
        """
        value_tags = [t for t in self._namespace_keys if self.db.sismember(t, value)]
        return self._remove_name_space(value_tags)

    def close(self):
        """
        Close the connection to the tag db.

        For use at the end of a task
        """
        self.db.close()

    @property
    def _namespace_keys(self) -> list[bytes]:
        return self.db.keys(f"{self.namespace}*")

    @property
    def tags(self) -> list[str]:
        """Return a list of all tags in this namespace."""
        return self._remove_name_space(self._namespace_keys)

    def purge(self) -> None:
        """
        Remove the database of tags.

        For use at the end of a workflow.
        """
        if keys := self._namespace_keys:
            self.db.delete(*keys)

    def __repr__(self):
        return f"TagDB(recipe_run_id={self.recipe_run_id}, task_name={self.task_name})"

    def __str__(self):
        return f"{self!r} connected to {self.db}"
