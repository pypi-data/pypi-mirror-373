"""Controlled list of quality metric codes."""

from enum import StrEnum


class MetricCode(StrEnum):
    """Controlled list of quality metric codes."""

    ao_status = "AO_STATUS"
    dataset_average = "DATASET_AVERAGE"
    dataset_rms = "DATASET_RMS"
    frame_average = "FRAME_AVERAGE"
    frame_rms = "FRAME_RMS"
    fried_parameter = "FRIED_PARAMETER"
    health_status = "HEALTH_STATUS"
    historical = "HISTORICAL"
    light_level = "LIGHT_LEVEL"
    noise = "NOISE"
    polcal_constant_par_vals = "POLCAL_CONSTANT_PAR_VALS"
    polcal_efficiency = "POLCAL_EFFICIENCY"
    polcal_fit_residuals = "POLCAL_FIT_RESIDUALS"
    polcal_global_par_vals = "POLCAL_GLOBAL_PAR_VALS"
    polcal_local_par_vals = "POLCAL_LOCAL_PAR_VALS"
    range = "RANGE"
    sensitivity = "SENSITIVITY"
    task_types = "TASK_TYPES"
    wavecal_fit = "WAVECAL_FIT"
