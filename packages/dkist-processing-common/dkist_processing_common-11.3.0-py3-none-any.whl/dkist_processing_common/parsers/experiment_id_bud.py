"""Experiment Id parser."""

from dkist_processing_common.models.constants import BudName
from dkist_processing_common.parsers.id_bud import ContributingIdsBud
from dkist_processing_common.parsers.id_bud import IdBud


class ExperimentIdBud(IdBud):
    """Class to create a Bud for the experiment_id."""

    def __init__(self):
        super().__init__(constant_name=BudName.experiment_id.value, metadata_key="experiment_id")


class ContributingExperimentIdsBud(ContributingIdsBud):
    """Class to create a Bud for the supporting experiment_ids."""

    def __init__(self):
        super().__init__(
            stem_name=BudName.contributing_experiment_ids.value, metadata_key="experiment_id"
        )
