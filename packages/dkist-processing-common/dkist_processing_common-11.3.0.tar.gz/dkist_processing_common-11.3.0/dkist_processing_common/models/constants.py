"""
Components of the Constant model.

Contains names of database entries and Base class for an object that simplifies
accessing the database (tab completion, etc.)
"""

from enum import Enum
from string import ascii_uppercase

from sqids import Sqids

from dkist_processing_common._util.constants import ConstantsDb


class BudName(str, Enum):
    """Controlled list of names for constant stems (buds)."""

    recipe_run_id = "RECIPE_RUN_ID"
    instrument = "INSTRUMENT"
    num_cs_steps = "NUM_CS_STEPS"
    num_modstates = "NUM_MODSTATES"
    proposal_id = "PROPOSAL_ID"
    contributing_proposal_ids = "CONTRIBUTING_PROPOSAL_IDS"
    experiment_id = "EXPERIMENT_ID"
    contributing_experiment_ids = "CONTRIBUTING_EXPERIMENT_IDS"
    obs_ip_start_time = "OBS_IP_START_TIME"
    average_cadence = "AVERAGE_CADENCE"
    maximum_cadence = "MAXIMUM_CADENCE"
    minimum_cadence = "MINIMUM_CADENCE"
    variance_cadence = "VARIANCE_CADENCE"
    num_dsps_repeats = "NUM_DSPS_REPEATS"
    dark_exposure_times = "DARK_EXPOSURE_TIMES"
    dark_readout_exp_times = "DARK_READOUT_EXP_TIMES"
    wavelength = "WAVELENGTH"
    retarder_name = "RETARDER_NAME"


class ConstantsBase:
    """
    Aggregate (from the constant buds flower pot) in a single property on task classes.

    It also provides some default constants, but is intended to be subclassed by instruments.

    To subclass:

    1. Create the actual subclass. All you need to do is add more @properties for the constants you want

    2. Update the instrument class's `constants_model_class` property to return the new subclass. For example::

         class NewConstants(ConstantsBase):
            @property
            def something(self):
                return 7

         class InstrumentWorkflowTask(WorkflowTaskBase):
            @property
            def constants_model_class:
                return NewConstants

            ...

    Parameters
    ----------
    recipe_run_id
        Thew recipe_run_id
    task_name
        The task_name
    """

    def __init__(self, recipe_run_id: int, task_name: str):
        self._db_dict = ConstantsDb(recipe_run_id=recipe_run_id, task_name=task_name)
        self._recipe_run_id = recipe_run_id

    # These management functions are all underscored because we want tab-complete to *only* show the available
    #  constants
    def _update(self, d: dict):
        self._db_dict.update(d)

    def _purge(self):
        self._db_dict.purge()

    def _close(self):
        self._db_dict.close()

    def _rollback(self):
        self._db_dict.rollback()

    @property
    def dataset_id(self) -> str:
        """Define the dataset_id constant."""
        return Sqids(min_length=6, alphabet=ascii_uppercase).encode([self._recipe_run_id])

    @property
    def proposal_id(self) -> str:
        """Get the proposal_id constant."""
        return self._db_dict[BudName.proposal_id]

    @property
    def contributing_proposal_ids(self) -> [str]:
        """Return the list of contributing proposal IDs."""
        proposal_ids = self._db_dict[BudName.contributing_proposal_ids]
        if isinstance(proposal_ids, str):
            return [proposal_ids]
        return proposal_ids

    @property
    def instrument(self) -> str:
        """Get the instrument name."""
        return self._db_dict[BudName.instrument]

    @property
    def obs_ip_start_time(self) -> str:
        """Return the start time of the observe IP."""
        return self._db_dict[BudName.obs_ip_start_time.value]

    @property
    def average_cadence(self) -> float:
        """Get the average_cadence constant."""
        return self._db_dict[BudName.average_cadence]

    @property
    def maximum_cadence(self) -> float:
        """Get the maximum cadence constant constant."""
        return self._db_dict[BudName.maximum_cadence]

    @property
    def minimum_cadence(self) -> float:
        """Get the minimum cadence constant constant."""
        return self._db_dict[BudName.minimum_cadence]

    @property
    def variance_cadence(self) -> float:
        """Get the variance of the cadence constant."""
        return self._db_dict[BudName.variance_cadence]

    @property
    def num_dsps_repeats(self) -> int:
        """Get the number of dsps repeats."""
        return self._db_dict[BudName.num_dsps_repeats]

    @property
    def dark_exposure_times(self) -> [float]:
        """Get a list of exposure times used in the dark calibration."""
        return self._db_dict[BudName.dark_exposure_times]

    @property
    def dark_readout_exp_times(self) -> [float]:
        """Get a list of readout exp times for all DARK frames."""
        return self._db_dict[BudName.dark_readout_exp_times]

    @property
    def stokes_params(self) -> [str]:
        """Return the list of stokes parameter names."""
        return ["I", "Q", "U", "V"]

    @property
    def experiment_id(self) -> str:
        """Get the experiment_id constant."""
        return self._db_dict[BudName.experiment_id]

    @property
    def contributing_experiment_ids(self) -> [str]:
        """Return the list of contributing experiment IDs."""
        experiment_ids = self._db_dict[BudName.contributing_experiment_ids]
        if isinstance(experiment_ids, str):
            return [experiment_ids]
        return experiment_ids

    @property
    def wavelength(self) -> float:
        """Wavelength."""
        return self._db_dict[BudName.wavelength.value]
