"""Bud that parses the name of the retarder used during POLCAL task observations."""

from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.parsers.unique_bud import TaskUniqueBud


class RetarderNameBud(TaskUniqueBud):
    """
    Bud for determining the name of the retarder used during a polcal Calibration Sequence (CS).

    This is *slightly* different than a simple `TaskUniqueBud` because we need to allow for CS steps when the retarder
    is out of the beam (i.g., "clear"). We do this by forcing the set of header values to be `{clear, RETARDER_NAME}`,
    where RETARDER_NAME is the value of this Bud.
    """

    # For type-hinting later
    key_to_petal_dict: dict[str, str]

    def __init__(self):
        super().__init__(
            constant_name=BudName.retarder_name.value,
            metadata_key="gos_retarder_status",
            ip_task_types=TaskName.polcal.value,
        )

    def getter(self, key) -> str:
        """Get the value for the retarder name and raise an Error if, ignoring "clear", that name is not unique."""
        value_set = set(self.key_to_petal_dict.values())
        value_set -= {"clear"}
        if len(value_set) > 1:
            raise ValueError(f"Multiple non-clear retarder names found. Names: {value_set}")

        raw_retarder_name = value_set.pop()
        return raw_retarder_name
