"""Pre-made flower that reads a single header key from all files and raises a ValueError if the values are not in a supplied range."""

from statistics import mean
from typing import Callable

from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess
from dkist_processing_common.parsers.task import passthrough_header_ip_task


class NearFloatBud(Stem):
    """
    Pre-made flower that reads a single header key from all files and raises a ValueError if the values are not within a given tolerance.

    This is intended for use with floats where the values may be slightly different, but should be the same.

    Parameters
    ----------
    constant_name
        The name for the constant to be defined

    metadata_key
        The metadata key associated with the constant

    tolerance
        The acceptable difference between the maximum and minimum values
    """

    def __init__(
        self,
        constant_name: str,
        metadata_key: str,
        tolerance: float,
    ):
        super().__init__(stem_name=constant_name)
        self.metadata_key = metadata_key
        self.tolerance = tolerance

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
        Get the value for this key and raise an error if the data spans more than the given tolerance.

        Parameters
        ----------
        key
            The input key
        Returns
        -------
        The mean value associated with this input key
        """
        value_set = list(self.key_to_petal_dict.values())
        biggest_value = max(value_set)
        smallest_value = min(value_set)
        if biggest_value - smallest_value > self.tolerance:
            raise ValueError(
                f"{self.stem_name} values are not close enough. Max: {biggest_value}, Min: {smallest_value}, Tolerance: {self.tolerance}"
            )
        return mean(value_set)


class TaskNearFloatBud(NearFloatBud):
    """
    Subclass of `NearFloatBud` that only considers objects that have specific task types.

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

    tolerance
        The acceptable difference between the maximum and minimum values
    """

    def __init__(
        self,
        constant_name: str,
        metadata_key: str,
        ip_task_types: str | list[str],
        tolerance: float,
        task_type_parsing_function: Callable = passthrough_header_ip_task,
    ):
        super().__init__(
            constant_name=constant_name, metadata_key=metadata_key, tolerance=tolerance
        )

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
