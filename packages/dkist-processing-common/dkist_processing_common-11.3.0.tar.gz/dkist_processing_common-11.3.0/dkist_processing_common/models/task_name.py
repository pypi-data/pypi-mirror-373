"""Controlled list of common IP task tag names."""

from enum import Enum


class TaskName(str, Enum):
    """Controlled list of task tag names."""

    observe = "OBSERVE"
    polcal = "POLCAL"
    polcal_dark = "POLCAL_DARK"
    polcal_gain = "POLCAL_GAIN"
    dark = "DARK"
    gain = "GAIN"
    geometric = "GEOMETRIC"
    lamp_gain = "LAMP_GAIN"
    solar_gain = "SOLAR_GAIN"
    geometric_angle = "GEOMETRIC_ANGLE"
    geometric_offsets = "GEOMETRIC_OFFSETS"
    geometric_spectral_shifts = "GEOMETRIC_SPEC_SHIFTS"
    demodulation_matrices = "DEMOD_MATRICES"
