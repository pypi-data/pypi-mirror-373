"""Pre-made flower that reads a single header key from all files and raises a ValueError if it is not unique."""

from typing import Callable

from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess
from dkist_processing_common.parsers.task import passthrough_header_ip_task


class UniqueBud(Stem):
    """
    Pre-made flower that reads a single header key from all files and raises a ValueError if it is not unique.

    Parameters
    ----------
    constant_name
        The name for the constant to be defined

    metadata_key
        The metadata key associated with the constant
    """

    def __init__(
        self,
        constant_name: str,
        metadata_key: str,
    ):
        super().__init__(stem_name=constant_name)
        self.metadata_key = metadata_key

    def setter(self, fits_obj: L0FitsAccess):
        """
        Setter method used by parent stem class to set the value.

        Parameters
        ----------
        fits_obj
            The input fits object
        Returns
        -------
        The value associated with the metadata key for this object
        """
        return getattr(fits_obj, self.metadata_key)

    def getter(self, key):
        """
        Get the value for this key and raise an error if it is not unique.

        Parameters
        ----------
        key
            The input key
        Returns
        -------
        The value associated with this input key
        """
        value_set = set(self.key_to_petal_dict.values())
        if len(value_set) > 1:
            raise ValueError(
                f"Multiple {self.stem_name} values found for key {key}. Values: {value_set}"
            )
        return value_set.pop()


class TaskUniqueBud(UniqueBud):
    """
    Subclass of `UniqueBud` that only considers objects that have specific task types.

    Parameters
    ----------
    constant_name
        The name for the constant to be defined

    metadata_key
        The metadata key associated with the constant

    ip_task_types
        Only consider objects whose parsed header IP task type matches a string in this list

    task_type_parsing_function
        The function used to convert a header into an IP task type
    """

    def __init__(
        self,
        constant_name: str,
        metadata_key: str,
        ip_task_types: str | list[str],
        task_type_parsing_function: Callable = passthrough_header_ip_task,
    ):
        super().__init__(constant_name=constant_name, metadata_key=metadata_key)

        if isinstance(ip_task_types, str):
            ip_task_types = [ip_task_types]
        self.ip_task_types = [task.casefold() for task in ip_task_types]
        self.parsing_function = task_type_parsing_function

    def setter(self, fits_obj: L0FitsAccess):
        """Ingest an object only if its parsed IP task type matches what's desired."""
        task = self.parsing_function(fits_obj)

        if task.casefold() in self.ip_task_types:
            return super().setter(fits_obj)

        return SpilledDirt
