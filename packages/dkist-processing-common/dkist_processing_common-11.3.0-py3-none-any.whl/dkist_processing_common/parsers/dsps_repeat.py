"""Classes supporting the Data Set Parameters Set (DSPS) Repeat parameter."""

from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.tags import StemName
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess
from dkist_processing_common.parsers.single_value_single_key_flower import (
    SingleValueSingleKeyFlower,
)
from dkist_processing_common.parsers.unique_bud import TaskUniqueBud


class TotalDspsRepeatsBud(TaskUniqueBud):
    """The total number of DSPS Repeats."""

    def __init__(self):
        super().__init__(
            constant_name=BudName.num_dsps_repeats.value,
            metadata_key="num_dsps_repeats",
            ip_task_types=TaskName.observe.value,
        )


class DspsRepeatNumberFlower(SingleValueSingleKeyFlower):
    """The current DSPS Repeat step being executed."""

    def __init__(self):
        super().__init__(
            tag_stem_name=StemName.dsps_repeat.value, metadata_key="current_dsps_repeat"
        )

    def setter(self, fits_obj: L0FitsAccess):
        """
        Set the current DSPS Repeat number.

        Parameters
        ----------
        fits_obj
            The input fits object
        Returns
        -------
        The current DSPS repeat number
        """
        if fits_obj.ip_task_type.casefold() != TaskName.observe.value.casefold():
            return SpilledDirt
        return super().setter(fits_obj)
