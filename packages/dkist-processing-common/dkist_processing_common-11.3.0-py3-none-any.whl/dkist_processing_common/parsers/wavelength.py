"""Bud to get the wavelength of observe frames."""

from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.parsers.unique_bud import TaskUniqueBud


class ObserveWavelengthBud(TaskUniqueBud):
    """Bud to find the wavelength of observe frames."""

    def __init__(self):
        super().__init__(
            constant_name=BudName.wavelength.value,
            metadata_key="wavelength",
            ip_task_types=TaskName.observe.value,
        )
