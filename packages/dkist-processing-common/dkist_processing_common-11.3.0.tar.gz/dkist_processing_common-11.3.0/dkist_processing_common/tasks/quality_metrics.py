"""Classes to support the generation of quality metrics for the calibrated data."""

import logging
from dataclasses import dataclass
from dataclasses import field
from inspect import signature
from pathlib import Path
from typing import Callable
from typing import Generator
from typing import Iterable
from typing import Type

import numpy as np

from dkist_processing_common.models.fits_access import FitsAccessBase
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess
from dkist_processing_common.parsers.quality import L1QualityFitsAccess
from dkist_processing_common.tasks.base import WorkflowTaskBase
from dkist_processing_common.tasks.mixin.quality import QualityMixin

__all__ = ["QualityL1Metrics", "QualityL0Metrics"]


logger = logging.getLogger(__name__)


@dataclass
class _QualityTaskTypeData:
    quality_task_type: str
    average_values: list[float] = field(default_factory=list)
    rms_values_across_frame: list[float] = field(default_factory=list)
    datetimes: list[str] = field(default_factory=list)
    modstate: int | None = None

    @property
    def has_values(self) -> bool:
        return bool(self.average_values)


class QualityL0Metrics(WorkflowTaskBase, QualityMixin):
    """
    Task class supporting the generation of quality metrics for the L0 data.

    Subclassing guide
    -----------------

    There are three important properties that an instrument subclass may want to change to make sure that the L0 metrics
    are computed for the correct files and organized in a meaningful way:

    `raw_frame_tag` (``str``)
        The top-level tag used to identify "raw" frames that will be considered when computing metrics. For visible
        instruments this can be left as the default `Tag.input()`, but IR cameras will probably want to set this to
        `Tag.linearized()` or similar.

    `~dkist_processing_common.tasks.mixin.quality.QualityMixin.quality_task_types` (`list[str]`)
        A list of IPTASK types. A separate set of L0 metrics will be reported for each task type listed here.
        See the definition of `~dkist_processing_common.tasks.mixin.quality.QualityMixin.quality_task_types` for the
        sensible defaults. If overloading, please use controlled `~dkist_processing_common.models.task_name.TaskName`
        values, if possible.

    `modstate_list` (`list[int] | None`)
        A list of modstates over which to separate each metric. Adding modstates does not create new metric entries, but
        does sub-divide each TASK's metric into modstate bins. If you want *all* files of a single TASK to be considered
        together return ``None`` here.

    **NOTE:** The `~dkist_processing_common.tasks.mixin.quality.QualityMixin.quality_task_types` on an instrument
    subclass of `~dkist_processing_common.tasks.l1_output_data.AssembleQualityData` should match whatever is set here
    (although in both cases the default is probably fine).
    """

    @property
    def modstate_list(self) -> Iterable[int] | None:
        """
        Define the list of modstates over which to compute quality metrics.

        If you want to compute metrics over *all* modstates at the same time return `None`.
        """
        return None

    @property
    def raw_frame_tag(self) -> str:
        """
        Define the tag that indicates L0 data.

        Usually this is `Tag.input()`, but for IR instruments it may be `Tag.linearized()`.
        """
        return Tag.input()

    @property
    def fits_access_class(self) -> Type[FitsAccessBase]:
        """Define the `FitsAccess`-type class used to parse the headers of L0 frames."""
        return L0FitsAccess

    def run(self) -> None:
        """
        Calculate L0 quality metrics for all TASK/MODSTATE combinations.

        Which (if any) modstates and task types to loop over can be set with the `modstate_list` and
        `quality_task_types` properties, respectively.
        """
        modstate_list = self.modstate_list if self.modstate_list is not None else [None]
        with self.apm_task_step("Computing L0 Quality Metrics"):
            quality_data_list = []
            for task_type in self.quality_task_types:
                with self.apm_processing_step(f"Working on {task_type = }"):
                    for modstate in modstate_list:
                        paths = self.get_paths_for_modstate_and_task(modstate, task_type)
                        quality_data = self.calculate_l0_metrics(
                            paths=paths, task_type=task_type, access_class=self.fits_access_class
                        )
                        quality_data.modstate = modstate
                        quality_data_list.append(quality_data)

        with self.apm_writing_step("Saving metrics to disk"):
            for quality_data in quality_data_list:
                if quality_data.has_values:
                    self.save_quality_data(quality_data, modstate=quality_data.modstate)

    def get_paths_for_modstate_and_task(
        self, modstate: int | None, task_type: str
    ) -> Generator[Path, None, None]:
        """
        Return Paths for all raw files that tagged with the given modstate and task type.

        The tag that defines "raw" can be changed in the `raw_frame_tag` property.
        """
        tags = [self.raw_frame_tag, Tag.task(task_type)]
        if modstate is not None:
            tags.append(Tag.modstate(modstate))

        return self.read(tags)

    def calculate_l0_metrics(
        self,
        paths: Generator[Path, None, None],
        task_type: str,
        access_class: Type[FitsAccessBase] = L0FitsAccess,
    ) -> _QualityTaskTypeData:
        """Calculate L0 quality metrics for a given task type and modstate."""
        quality_task_type_data = _QualityTaskTypeData(quality_task_type=task_type)

        for path in paths:
            frame = access_class.from_path(path)
            data = frame.data.astype(float)
            exposure_time_sec = frame.fpa_exposure_time_ms / 1000

            # Metrics
            normalized_rms = self.compute_normalized_rms(data, exposure_time_sec)
            normalized_mean = self.compute_normalized_mean(data, exposure_time_sec)

            quality_task_type_data.rms_values_across_frame.append(normalized_rms)
            quality_task_type_data.average_values.append(normalized_mean)
            quality_task_type_data.datetimes.append(frame.time_obs)

        return quality_task_type_data

    @staticmethod
    def compute_normalized_rms(data: np.ndarray, exposure_time_sec: float) -> float:
        r"""
        Compute the normalized rms of a single frame.

        Defined as

        .. math::

            RMS = \frac{\sqrt{\left<D^2\right>}}{t}

        where :math:`D` is the data array, :math:`t` is the exposure time, in seconds, and :math:`\left< \right>`
        denotes the average.
        """
        squared_mean = np.nanmean(data**2)
        return np.sqrt(squared_mean) / exposure_time_sec

    @staticmethod
    def compute_normalized_mean(data: np.ndarray, exposure_time_sec: float) -> float:
        r"""
        Compute the normalized mean of a single frame.

        Defined as

        .. math::

            \mathrm{M} = \left<D\right>/t

        where :math:`D` is the data array, :math:`t` is the exposure time, in seconds, and :math:`\left< \right>`
        denotes the average.
        """
        return np.nanmean(data) / exposure_time_sec

    def save_quality_data(
        self, quality_task_type_data: _QualityTaskTypeData, modstate: int | None = None
    ) -> None:
        """Write L0 metrics to disk."""
        self.quality_store_frame_average(
            datetimes=quality_task_type_data.datetimes,
            values=quality_task_type_data.average_values,
            task_type=quality_task_type_data.quality_task_type,
            modstate=modstate,
        )
        self.quality_store_frame_rms(
            datetimes=quality_task_type_data.datetimes,
            values=quality_task_type_data.rms_values_across_frame,
            task_type=quality_task_type_data.quality_task_type,
            modstate=modstate,
        )
        self.quality_store_dataset_average(
            task_type=quality_task_type_data.quality_task_type,
            frame_averages=quality_task_type_data.average_values,
        )
        self.quality_store_dataset_rms(
            task_type=quality_task_type_data.quality_task_type,
            frame_rms=quality_task_type_data.rms_values_across_frame,
        )


class L1Metric:
    """
    Class for collecting L1 quality metric data while frames are being opened before storing on disk.

    Parameters
    ----------
    storage_method
        The callable used to execute the storage
    value_source
        The source of the value being stored
    value_function
        The function to return the values
    """

    def __init__(
        self,
        storage_method: Callable,
        value_source: list[str] | str,
        value_function: Callable | None = None,
    ):
        self.storage_method = storage_method
        self.value_source = value_source
        self.values = []
        self.datetimes = []
        self.value_function = value_function

    def append_value(self, frame: L1QualityFitsAccess) -> None:
        """
        Append datetime from the frame to the list of datetimes.

        If a value_function was provided, apply it to the given source attribute and append to
        self.values. Otherwise, append the attribute value itself to self.values.  If multiple
        sources provided, append a list of the source attributes to self.values.

        Parameters
        ----------
        frame
            The input frame

        Returns
        -------
        None
        """
        self.datetimes.append(frame.time_obs)
        if self.value_function:
            self.values.append(self.value_function(getattr(frame, self.value_source)))
            return
        if isinstance(self.value_source, list):
            multiple_values = [getattr(frame, source, None) for source in self.value_source]
            self.values.append(multiple_values)
            return
        self.values.append(getattr(frame, self.value_source))

    @property
    def has_values(self):
        return len(self.values) > 0

    def store_metric(self):
        """Remove None values from a single-value values list (and also remove corresponding indices from datetimes) then send to the provided storage method."""
        # Get indices of non-None values and only use those.
        # Use multi-valued lists as is to be handled in the applicable storage_method.
        indices = [i for i, val in enumerate(self.values) if val is not None]
        d = [self.datetimes[i] for i in indices]
        v = [self.values[i] for i in indices]
        # Get signature of storage method and call with applicable args
        storage_method_sig = signature(self.storage_method)
        if storage_method_sig.parameters.get("datetimes", False):
            self.storage_method(datetimes=d, values=v)
            return
        self.storage_method(values=v)


class QualityL1Metrics(WorkflowTaskBase, QualityMixin):
    """Task class supporting the generation of quality metrics for the L0 data."""

    def run(self) -> None:
        """Run method for this task."""
        metrics = [
            L1Metric(storage_method=self.quality_store_light_level, value_source="light_level"),
            L1Metric(storage_method=self.quality_store_health_status, value_source="health_status"),
            L1Metric(
                storage_method=self.quality_store_ao_status_and_fried_parameter,
                value_source=["ao_status", "fried_parameter", "num_out_of_bounds_ao_values"],
            ),
        ]

        with self.apm_task_step("Reading L1 frames"):
            paths = list(self.read(tags=[Tag.calibrated(), Tag.frame()]))

        with self.apm_task_step("Calculating L1 quality metrics"):
            for metric in metrics:
                with self.apm_processing_step(f"Calculating L1 metric {metric.value_source}"):
                    for path in paths:
                        frame = L1QualityFitsAccess.from_path(path)
                        metric.append_value(frame=frame)

        with self.apm_task_step("Sending lists for storage"):
            for metric in metrics:
                if metric.has_values:
                    metric.store_metric()
