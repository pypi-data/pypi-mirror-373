"""Wrapper for interactions with shared database that holds arbitrary data that persists across the entire recipe run."""

import json
from collections.abc import MutableMapping
from enum import Enum
from typing import Generator

from dkist_processing_common._util.tags import TagDB


class ConstantsDb(MutableMapping):
    """
    Base class defining the constants db.

    Initialize a connection to the shared database.

    Parameters
    ----------
    recipe_run_id
        The resipe_run_id
    task_name
        The task name
    """

    def __init__(self, recipe_run_id: int, task_name: str):
        self.store = TagDB(recipe_run_id, task_name, "constant")
        self._audit_db = TagDB(
            recipe_run_id=recipe_run_id, task_name=task_name, namespace="constants_audit"
        )
        self._audit_set_tag = f"SET_{task_name}"

    @staticmethod
    def extract_value(value: set) -> int | str | float:
        """
        Pop the first (and only) value from set and convert it from a json string.

        Parameters
        ----------
        value
            The set from which to pop the value

        Returns
        -------
        The value popped from the set.
        """
        return json.loads(value.pop())

    def __getitem__(self, key: str) -> int | str | float | tuple | list:
        """Return the constant stored at a specific key. Raise and error if the key doesn't exist."""
        if isinstance(key, Enum):
            key = key.value
        value = self.store.all(key)
        if not value:
            raise KeyError(f"Constant {key} does not exist")
        return self.extract_value(value)

    def __delitem__(self, key: str):
        """'delete' a key by making it map to an empty set."""
        self.store.clear_tag(key)

    def __setitem__(self, key: str, value: str | int | float | tuple | list):
        """Set a constant key with the specified value. Raise an error if the key already exists."""
        if self.store.all(key):
            raise ValueError(f"Constant {key} already exists")
        self.store.add(key, json.dumps(value))
        # audit which constant key had a value set
        self._audit_db.add(tag=self._audit_set_tag, value=key)

    def __iter__(self) -> Generator[str, None, None]:
        """Yield the currently defined constants as strings."""
        yield from self.store.tags

    def __len__(self):
        """Return the number of constants currently defined."""
        return len(self.store.tags)

    def close(self):
        """Close the db connection.  Call on __exit__ of a Task."""
        self.store.close()
        self._audit_db.close()

    def purge(self):
        """Remove all constants associated with the instance recipe run id."""
        self.store.purge()
        self._audit_db.purge()

    def rollback(self):
        """Remove all constants associated with the instance recipe run id and task name."""
        # remove constants
        for key in self._audit_db.all(tags=self._audit_set_tag):
            self.store.clear_tag(key)
        # remove audit
        self._audit_db.clear_tag(tag=self._audit_set_tag)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
