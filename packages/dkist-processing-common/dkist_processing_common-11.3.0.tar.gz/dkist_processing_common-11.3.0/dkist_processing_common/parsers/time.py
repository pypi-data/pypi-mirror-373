"""Time parser."""

from datetime import datetime
from datetime import timezone
from typing import Callable
from typing import Hashable
from typing import Type

import numpy as np

from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.models.tags import EXP_TIME_ROUND_DIGITS
from dkist_processing_common.models.tags import StemName
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess
from dkist_processing_common.parsers.single_value_single_key_flower import (
    SingleValueSingleKeyFlower,
)
from dkist_processing_common.parsers.task import passthrough_header_ip_task
from dkist_processing_common.parsers.unique_bud import TaskUniqueBud
from dkist_processing_common.parsers.unique_bud import UniqueBud


class ObsIpStartTimeBud(TaskUniqueBud):
    """A unique bud that yields the IP start time of the observe task."""

    def __init__(self):
        super().__init__(
            constant_name=BudName.obs_ip_start_time.value,
            metadata_key="ip_start_time",
            ip_task_types=TaskName.observe.value,
        )


class CadenceBudBase(UniqueBud):
    """Base class for all Cadence Buds."""

    def __init__(self, constant_name: str):
        super().__init__(constant_name, metadata_key="time_obs")

    def setter(self, fits_obj: L0FitsAccess) -> float | Type[SpilledDirt]:
        """
        If the file is an observe file, its DATE-OBS value is stored as unix seconds.

        Parameters
        ----------
        fits_obj
            The input fits object
        Returns
        -------
        The observe time in seconds
        """
        if fits_obj.ip_task_type.casefold() == TaskName.observe.value.casefold():
            return (
                datetime.fromisoformat(getattr(fits_obj, self.metadata_key))
                .replace(tzinfo=timezone.utc)
                .timestamp()
            )
        return SpilledDirt


class AverageCadenceBud(CadenceBudBase):
    """Class for the average cadence Bud."""

    def __init__(self):
        super().__init__(constant_name=BudName.average_cadence.value)

    def getter(self, key) -> np.float64:
        """
        Return the mean cadence between frames.

        Parameters
        ----------
        key
            The input key

        Returns
        -------
        The mean value of the cadences of the input frames
        """
        return np.mean(np.diff(sorted(list(self.key_to_petal_dict.values()))))


class MaximumCadenceBud(CadenceBudBase):
    """Class for the maximum cadence bud."""

    def __init__(self):
        super().__init__(constant_name=BudName.maximum_cadence.value)

    def getter(self, key) -> np.float64:
        """
        Return the maximum cadence between frames.

        Parameters
        ----------
        key
            The input key

        Returns
        -------
        The maximum cadence between frames
        """
        return np.max(np.diff(sorted(list(self.key_to_petal_dict.values()))))


class MinimumCadenceBud(CadenceBudBase):
    """Class for the minimum cadence bud."""

    def __init__(self):
        super().__init__(constant_name=BudName.minimum_cadence.value)

    def getter(self, key) -> np.float64:
        """
        Return the minimum cadence between frames.

        Parameters
        ----------
        key
            The input key

        Returns
        -------
        The minimum cadence between frames
        """
        return np.min(np.diff(sorted(list(self.key_to_petal_dict.values()))))


class VarianceCadenceBud(CadenceBudBase):
    """Class for the variance cadence Bud."""

    def __init__(self):
        super().__init__(constant_name=BudName.variance_cadence.value)

    def getter(self, key) -> np.float64:
        """
        Return the cadence variance between frames.

        Parameters
        ----------
        key
            The input key
        Returns
        -------
        Return the variance of the cadences over the input frames
        """
        return np.var(np.diff(sorted(list(self.key_to_petal_dict.values()))))


class TimeFlowerBase(SingleValueSingleKeyFlower):
    """Base task for SingleValueSingleKeyFlowers that need to round their values to avoid value jitter."""

    def setter(self, fits_obj: L0FitsAccess):
        """
        Set the exposure time for this flower.

        Parameters
        ----------
        fits_obj
            The input fits object
        Returns
        -------
        The value of the exposure time
        """
        raw_value = super().setter(fits_obj)
        return round(raw_value, EXP_TIME_ROUND_DIGITS)


class ExposureTimeFlower(TimeFlowerBase):
    """For tagging the frame FPA exposure time."""

    def __init__(self):
        super().__init__(
            tag_stem_name=StemName.exposure_time.value, metadata_key="fpa_exposure_time_ms"
        )


class ReadoutExpTimeFlower(TimeFlowerBase):
    """For tagging the exposure time of each readout that contributes to an FPA."""

    def __init__(self):
        super().__init__(
            tag_stem_name=StemName.readout_exp_time.value,
            metadata_key="sensor_readout_exposure_time_ms",
        )


class TaskTimeBudBase(Stem):
    """
    Base class for making time-related buds that are computed for specific task types.

    By "time-related" we mean values that generally need rounding when ingested into the database.

    Complicated parsing of the header into a task type can be achieved by passing in a different
    header task parsing function.

    Parameters
    ----------
    constant_name
        The name for the constant to be defined

    metadata_key
        The metadata key associated with the constant

    ip_task_types
        Only consider objects whose parsed header IP task type matches a string in this list

    header_task_parsing_func
        The function used to convert a header into an IP task type
    """

    def __init__(
        self,
        stem_name: str,
        metadata_key: str,
        ip_task_types: str | list[str],
        header_task_parsing_func: Callable = passthrough_header_ip_task,
    ):
        super().__init__(stem_name=stem_name)

        if isinstance(ip_task_types, str):
            ip_task_types = [ip_task_types]
        self.metadata_key = metadata_key
        self.ip_task_types = [task.casefold() for task in ip_task_types]
        self.header_parsing_function = header_task_parsing_func

    def setter(self, fits_obj: L0FitsAccess):
        """Return the desired metadata key only if the parsed task type matches the Bud's task type."""
        task = self.header_parsing_function(fits_obj)

        if task.casefold() in self.ip_task_types:
            raw_value = getattr(fits_obj, self.metadata_key)
            return round(raw_value, EXP_TIME_ROUND_DIGITS)

        return SpilledDirt

    def getter(self, key: Hashable) -> tuple[float, ...]:
        """Return a tuple of all the unique values found."""
        value_tuple = tuple(sorted(set(self.key_to_petal_dict.values())))
        return value_tuple


class TaskExposureTimesBud(TaskTimeBudBase):
    """Produce a tuple of all FPA exposure times present in the dataset for a specific ip task type."""

    def __init__(
        self,
        stem_name: str,
        ip_task_types: str | list[str],
        header_task_parsing_func: Callable = passthrough_header_ip_task,
    ):
        super().__init__(
            stem_name=stem_name,
            metadata_key="fpa_exposure_time_ms",
            ip_task_types=ip_task_types,
            header_task_parsing_func=header_task_parsing_func,
        )


class TaskReadoutExpTimesBud(TaskTimeBudBase):
    """Produce a tuple of all sensor readout exposure times present in the dataset for a specific task type."""

    def __init__(
        self,
        stem_name: str,
        ip_task_types: str | list[str],
        header_task_parsing_func: Callable = passthrough_header_ip_task,
    ):
        super().__init__(
            stem_name=stem_name,
            metadata_key="sensor_readout_exposure_time_ms",
            ip_task_types=ip_task_types,
            header_task_parsing_func=header_task_parsing_func,
        )
