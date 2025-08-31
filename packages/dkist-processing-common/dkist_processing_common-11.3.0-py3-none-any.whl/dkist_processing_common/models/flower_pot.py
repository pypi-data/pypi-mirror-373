"""
Framework for grouping multiple keys and values with arbitrary logic.

Defines:
    Stem -> ABC for groupings that depend on both the key and (maybe) value. Subgroups (Petals) are implied but not enforced.

    FlowerPot -> Container for Stem children (Flowers)
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from collections import defaultdict
from collections.abc import Hashable
from typing import Any


class FlowerPot:
    """Base class to hold multiple sets (stems) of key, value pairs."""

    def __init__(self):
        self.stems: list[Stem] = list()

    def __iter__(self):
        return self.stems.__iter__()

    def __len__(self):
        return self.stems.__len__()

    def __getitem__(self, item):
        return self.stems.__getitem__(item)

    def add_dirt(self, key: Hashable, value: Any) -> None:
        """
        Send key and value through all Stems.

        Parameters
        ----------
        key
            The key
        value
            The value

        Returns
        -------
        None
        """
        if not isinstance(key, Hashable):
            raise TypeError(f"Type of key ({type(key)}) is not hashable")

        for stem in self.stems:
            stem.update(key, value)


class SpilledDirt:
    """
    A custom class for when a Flower wants the FlowerPot to skip that particular key/value.

    Exists because None, False, [], (), etc. etc. are all valid Flower return values
    """


class Thorn:
    """
    Custom class to indicate that a Bud's value should not be used.

    I.e., don't pick this Bud because it's thorny. This exists for "Picky" Buds that merely perform a check and Error
    on failure. If the check passes we don't need to do anything with the Bud's value and that value should be a Thorn.
    """


class Petal:
    """
    Base class to hold a single key, value pair.

    Parameters
    ----------
    item
        The key, value pair to be added
    """

    def __init__(self, item: tuple):
        self.value = item[0]
        self.keys = item[1]

    def __repr__(self):
        return f"Petal: {{{self.value}: {self.keys}}}"


class Stem(ABC):
    """
    Base group for grouping keys via arbitrary logic on the total collection of keys and values.

    Parameters
    ----------
    stem_name
        The name to be associated with the stem
    """

    def __init__(self, stem_name: Any):
        self.stem_name = stem_name
        self.key_to_petal_dict: dict[Hashable, Hashable] = dict()

        self._petal_cache: list[Petal] = []
        self._need_to_generate_petals: bool = True

    def update(self, key: Hashable, value: Any) -> None:
        """
        Ingest a single key/value pair.

        Parameters
        ----------
        key
            The key
        value
            The value

        Returns
        -------
        None
        """
        result = self.setter(value)
        if result is not SpilledDirt:
            self.key_to_petal_dict[key] = result
            self._need_to_generate_petals = True

    @property
    def petals(self) -> list[Petal]:
        """Return subgroups and associated keys."""
        if self._need_to_generate_petals:
            self._generate_petal_list()

        return self._petal_cache

    def _generate_petal_list(self) -> None:
        """
        Generate a list of petals.

        Generating a petal list can be expensive because it involves inverting the `key_to_petal_dict`. To avoid doing
        this every the `petals` property is accessed, this method produces a cached list of petals that is only
        re-generated when the `key_to_petal_dict` has been updated.

        Note: We can't make `petals` a `@cached_property` because that would make `petals` always tied to whatever the
        state of this `Stem` was when `petals` was first accessed. And we can't use `lru_cache` because the object that
        changes, `key_to_petal_dict`, is unhashable.
        """
        petal_to_key_dict = defaultdict(list)
        for key, petal in self.key_to_petal_dict.items():
            petal = self.getter(key)
            petal_to_key_dict[petal].append(key)

        self._petal_cache = [Petal(item) for item in petal_to_key_dict.items()]
        self._need_to_generate_petals = False

    @property
    def bud(self) -> Petal:
        """Just the first petal."""
        bud = self.petals[0]
        return bud

    @abstractmethod
    def setter(self, value: Any) -> Any:
        """
        Logic to apply to a single key/value pair on ingest.

        Implemented in derived class.

        Parameters
        ----------
        value
            The value to be added

        Returns
        -------
        Any
        """
        pass

    @abstractmethod
    def getter(self, key: Hashable) -> Hashable:
        """
        Logic to apply to all ingested values when picking the Flower.

        Implemented in derived class.

        Parameters
        ----------
        key
            The key to return the value of
        Returns
        -------
        The value
        """
        pass
