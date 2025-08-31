"""Module for parsing IP task related things."""

from typing import Callable
from typing import Type

from dkist_processing_common.models.fits_access import FitsAccessBase
from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.tags import StemName
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.parsers.single_value_single_key_flower import (
    SingleValueSingleKeyFlower,
)


def passthrough_header_ip_task(fits_obj: Type[FitsAccessBase]) -> str:
    """
    Simply read the IP task directly from the header.

    AKA, default behavior.
    """
    return fits_obj.ip_task_type


def parse_header_ip_task_with_gains(fits_obj: FitsAccessBase) -> str:
    """
    Parse standard tasks from header while accounting for differences between solar and lamp gains.

    Parameters
    ----------
    fits_obj:
        A single FitsAccess object
    """
    # Distinguish between lamp and solar gains
    if (
        fits_obj.ip_task_type == "gain"
        and fits_obj.gos_level3_status == "lamp"
        and fits_obj.gos_level3_lamp_status == "on"
    ):
        return TaskName.lamp_gain.value
    if fits_obj.ip_task_type == "gain" and fits_obj.gos_level3_status == "clear":
        return TaskName.solar_gain.value

    # Everything else is unchanged
    return passthrough_header_ip_task(fits_obj)


def parse_polcal_task_type(fits_obj: Type[FitsAccessBase]) -> str | Type[SpilledDirt]:
    """
    Parse POLCAL task headers into polcal dark and clear labels.

    We don't check that the task type is POLCAL because we assume that has been done prior to passing a fits object
    to this function.

    In other words, this function does NOT produce the generic POLCAL task (which applies to *all* polcal frames); it
    only provides another level of parsing to POLCAL frames.
    """
    if (
        fits_obj.gos_level0_status == "DarkShutter"
        and fits_obj.gos_retarder_status == "clear"
        and fits_obj.gos_polarizer_status == "clear"
    ):
        return TaskName.polcal_dark.value

    elif (
        fits_obj.gos_level0_status.startswith("FieldStop")
        and fits_obj.gos_retarder_status == "clear"
        and fits_obj.gos_polarizer_status == "clear"
    ):
        return TaskName.polcal_gain.value

    # We don't care about a POLCAL frame that is neither dark nor clear
    return SpilledDirt


class TaskTypeFlower(SingleValueSingleKeyFlower):
    """Flower to tag by the IP task type."""

    def __init__(
        self, header_task_parsing_func: Callable[[FitsAccessBase], str] = passthrough_header_ip_task
    ):
        super().__init__(tag_stem_name=StemName.task.value, metadata_key="ip_task_type")
        self.header_parsing_function = header_task_parsing_func

    def setter(self, fits_obj: FitsAccessBase):
        """
        Set value of the flower.

        Parameters
        ----------
        fits_obj:
            A single FitsAccess object
        """
        return self.header_parsing_function(fits_obj)


class PolcalTaskFlower(SingleValueSingleKeyFlower):
    """
    Flower to find the polcal task type.

    This is separate from the "main" task-type flower because we still need all polcal frames to be tagged
    with just POLCAL (which is what the main task-type flower does); this flower adds an extra task tag for
    just POLCA_DARK and POLCAL_GAIN frames, but those frames are still POLCAL frames, too.
    """

    def __init__(self):
        super().__init__(tag_stem_name=StemName.task.value, metadata_key="ip_task_type")

    def setter(self, fits_obj: FitsAccessBase):
        """
        Set value of the flower.

        Parameters
        ----------
        fits_obj:
            A single FitsAccess object
        """
        if fits_obj.ip_task_type.casefold() != TaskName.polcal.casefold():
            return SpilledDirt

        return parse_polcal_task_type(fits_obj)
