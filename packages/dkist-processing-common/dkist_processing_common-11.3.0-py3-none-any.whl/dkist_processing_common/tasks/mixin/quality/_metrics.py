"""Collection of Mixin classes supporting different types of quality metrics.

These classes should not be directly mixed in to anything. They are pre-mixed into the top-level QualityMixin
"""

import copy
import json
import logging
from collections import defaultdict
from datetime import datetime
from functools import partial
from typing import Any
from typing import Iterable
from typing import Literal

import astropy.units as u
import numpy as np
from astropy.wcs import WCS
from dkist_processing_pac.fitter.fitter_parameters import CU_PARAMS
from dkist_processing_pac.fitter.fitter_parameters import GLOBAL_PARAMS
from dkist_processing_pac.fitter.fitter_parameters import TELESCOPE_PARAMS
from dkist_processing_pac.fitter.fitting_core import compare_I
from dkist_processing_pac.fitter.polcal_fitter import PolcalFitter
from pandas import DataFrame
from solar_wavelength_calibration.fitter.wavelength_fitter import FitResult

from dkist_processing_common.codecs.json import json_decoder
from dkist_processing_common.models.fried_parameter import r0_valid
from dkist_processing_common.models.metric_code import MetricCode
from dkist_processing_common.models.quality import EfficiencyHistograms
from dkist_processing_common.models.quality import ModulationMatrixHistograms
from dkist_processing_common.models.quality import Plot2D
from dkist_processing_common.models.quality import PlotHistogram
from dkist_processing_common.models.quality import PlotRaincloud
from dkist_processing_common.models.quality import ReportMetric
from dkist_processing_common.models.quality import SimpleTable
from dkist_processing_common.models.quality import VerticalMultiPanePlot2D
from dkist_processing_common.models.tags import Tag

logger = logging.getLogger(__name__)


class _SimpleQualityMixin:
    @staticmethod
    def _create_statement_metric(
        name: str,
        description: str,
        metric_code: str,
        statement: str,
        warnings: str | None = None,
        facet: str | None = None,
    ) -> dict:
        metric = ReportMetric(
            name=name,
            description=description,
            metric_code=metric_code,
            facet=facet,
            statement=statement,
            warnings=warnings,
        )
        return metric.model_dump()

    def quality_store_range(self, name: str, warnings: list[str]):
        """
        Insert range checking warnings into the schema used to record quality info.

        Parameters
        ----------
        name: name of the parameter / measurement for which range was out of bounds
        warnings: list of warnings to be entered into the quality report
        """
        data = {"name": name, "warnings": warnings}
        self._record_values(values=data, tags=Tag.quality(MetricCode.range))

    def quality_build_range(self) -> dict:
        """Build range data schema from stored data."""
        warnings = []
        # Loop over files that contain data for this metric
        for path in self.read(tags=Tag.quality(MetricCode.range)):
            with path.open() as f:
                data = json.load(f)
                for warning in data["warnings"]:
                    warnings.append(warning)

        return ReportMetric(
            name="Range checks",
            description="This metric is checking that certain input and calculated parameters "
            "fall within a valid data range. If no parameters are listed here, all "
            "pipeline parameters were measured to be in range",
            metric_code=MetricCode.range,
            warnings=self._format_warnings(warnings),
        ).model_dump()


class _SimplePlotQualityMixin:
    """Mixin containing metrics that present as simple x/y plots."""

    @staticmethod
    def _create_2d_plot_with_datetime_metric(
        name: str,
        description: str,
        metric_code: str,
        xlabel: str,
        ylabel: str,
        series_data: dict[str, list[list[Any]]],
        series_name: str | None = None,
        ylabel_horizontal: bool = False,
        ylim: tuple[float, float] | None = None,
        statement: str | None = None,
        warnings: list[str] | None = None,
        facet: str | None = None,
    ) -> dict:
        for k, v in series_data.items():
            # Convert datetime strings to datetime objects
            series_data[k][0] = [datetime.fromisoformat(i) for i in v[0]]
            # Sort the lists to make sure they are in ascending time order
            series_data[k][0], series_data[k][1] = (list(t) for t in zip(*sorted(zip(v[0], v[1]))))
        plot_data = Plot2D(
            series_data=series_data,
            xlabel=xlabel,
            ylabel=ylabel,
            series_name=series_name,
            ylabel_horizontal=ylabel_horizontal,
            ylim=ylim,
        )
        metric = ReportMetric(
            name=name,
            description=description,
            metric_code=metric_code,
            facet=facet,
            statement=statement,
            plot_data=plot_data,
            warnings=warnings,
        )
        return metric.model_dump()

    def _record_2d_plot_values(
        self,
        x_values: list[str],
        y_values: list[float],
        tags: Iterable[str] | str,
        series_name: str = "",
        task_type: str | None = None,
    ):
        """
        Encode values for a 2d plot type metric and store as a file.

        Parameters
        ----------
        x_values: values to apply to the x axis of a 2d plot
        y_values: values to apply to the y axis of a 2d plot
        tags: list of tags relating to the specific quality parameter being stored
        series_name: name of the series if this is part of a multi series plot metric
        task_type: type of data to be used - dark, gain, etc
        """
        if isinstance(tags, str):
            tags = [tags]
        axis_are_different_lengths = len(x_values) != len(y_values)
        axis_are_zero_length = not x_values or not y_values
        if axis_are_different_lengths or axis_are_zero_length:
            raise ValueError(
                f"Cannot store 2D plot values with 0 length or different length axis. "
                f"{len(x_values)=}, {len(y_values)=}"
            )
        data = {"x_values": x_values, "y_values": y_values, "series_name": series_name}
        if task_type:
            tags.append(Tag.quality_task(quality_task_type=task_type))
        self._record_values(values=data, tags=tags)

    def _load_2d_plot_values(self, tags: str | list[str], task_type: str | None = None):
        """Load all quality files for a given tag and return the merged datetimes and values."""
        if isinstance(tags, str):
            tags = [tags]
        if task_type:
            tags.append(Tag.quality_task(quality_task_type=task_type))
        all_plot_data = defaultdict(list)
        for path in self.read(tags=tags):
            with path.open() as f:
                data = json.load(f)
                series_name = str(data["series_name"])
                if series_name in all_plot_data.keys():
                    all_plot_data[series_name][0].extend(data["x_values"])
                    all_plot_data[series_name][1].extend(data["y_values"])
                else:
                    all_plot_data[series_name] = [data["x_values"], data["y_values"]]
        return all_plot_data

    @staticmethod
    def _find_iqr_outliers(datetimes: list[str], values: list[float]) -> list[str]:
        """
        Given a list of values, find values that fall more than (1.5 * iqr) outside the quartiles of the data.

        Parameters
        ----------
        datetimes: list of datetime strings used to reference the files that are outliers
        values: values to use to determine outliers from the iqr
        """
        if len(values) == 0:
            raise ValueError("No values provided.")
        warnings = []
        q1 = np.quantile(values, 0.25)
        q3 = np.quantile(values, 0.75)
        iqr = q3 - q1
        for i, val in enumerate(values):
            if val < q1 - (iqr * 1.5) or val > q3 + (iqr * 1.5):
                warnings.append(
                    f"File with datetime {datetimes[i]} has a value considered to be an outlier "
                    f"for this metric"
                )
        return warnings

    def quality_store_ao_status_and_fried_parameter(
        self, datetimes: list[str], values: list[list[bool | float]]
    ):
        """
        Collect and store datetime / value pairs for the boolean AO status and Fried parameter.

        Store all non-None AO lock status values, but only store Fried parameter values if AO lock status is True.

        Because of how L1Metric.has_metric works, empty lists will not be passed to this method.
        However, because of how L1Metric.store_metric works, one or both values can be None.
        """
        ao_lock_values = [value[0] for value in values]
        ao_not_none = [ao for ao in ao_lock_values if ao is not None]
        if len(ao_not_none) != 0:
            self._record_values(values=ao_not_none, tags=Tag.quality(MetricCode.ao_status))
        fried_values = [value[1] for value in values]
        ao_oob_values = [value[2] for value in values]
        fried_values_to_plot = []
        datetimes_to_plot = []
        # For each set of input data, check if the r0 is considered valid based on all data
        for i in range(len(fried_values)):
            if r0_valid(
                r0=fried_values[i],
                ao_lock=ao_lock_values[i],
                num_out_of_bounds_ao_values=ao_oob_values[i],
            ):
                fried_values_to_plot.append(fried_values[i])
                datetimes_to_plot.append(datetimes[i])
        if len(fried_values_to_plot) != 0:
            self._record_2d_plot_values(
                x_values=datetimes_to_plot,
                y_values=fried_values_to_plot,
                tags=Tag.quality(MetricCode.fried_parameter),
            )

    def quality_build_ao_status(self) -> dict:
        """
        Build ao status schema from stored data.

        Because of how quality_task_independent_metrics in the QualityMixin works, this method is not called if no data is on disk.
        """
        ao_status = []
        # Loop over files that contain data for this metric
        for path in self.read(tags=Tag.quality(MetricCode.ao_status)):
            with path.open() as f:
                ao_status += json.load(f)
        percentage = round(100 * np.count_nonzero(ao_status) / len(ao_status), 1)
        return self._create_statement_metric(
            name="Adaptive Optics Status",
            description="This metric shows the percentage of frames in which the adaptive optics "
            "system was running and locked",
            metric_code=MetricCode.ao_status,
            statement=f"The adaptive optics system was running and locked for {percentage}% of the "
            f"observed frames",
            warnings=None,
        )

    def quality_build_fried_parameter(self) -> dict:
        """
        Build fried parameter schema from stored data.

        Because of how quality_task_independent_metrics in the QualityMixin works, this method is not called if no data is on disk.
        """
        # Merge all recorded quality values
        series_data = self._load_2d_plot_values(tags=Tag.quality(MetricCode.fried_parameter))
        values = list(series_data.values())[0][1]
        return self._create_2d_plot_with_datetime_metric(
            name="Fried Parameter",
            description="This metric quantifies the stability of the atmosphere during an "
            "observation and directly impacts the data quality through a phenomenon "
            "known as atmospheric seeing. One measurement is taken per L1 frame. "
            "Only measurements taken while the AO system is locked are valid.",
            metric_code=MetricCode.fried_parameter,
            xlabel="Time",
            ylabel="Fried Parameter (m)",
            ylim=(0.0, 0.2),
            series_data=series_data,
            statement=f"Average valid Fried Parameter measurements for L1 dataset: "
            f"{round(np.mean(values), 2)} ± {round(np.std(values), 2)} m",
            warnings=None,
        )

    def quality_store_light_level(self, datetimes: list[str], values: list[float]):
        """Collect and store datetime / value pairs for the light level."""
        self._record_2d_plot_values(
            x_values=datetimes, y_values=values, tags=Tag.quality(MetricCode.light_level)
        )

    def quality_build_light_level(self) -> dict:
        """Build light_level schema from stored data."""
        series_data = self._load_2d_plot_values(tags=Tag.quality(MetricCode.light_level))
        values = list(series_data.values())[0][1]
        return self._create_2d_plot_with_datetime_metric(
            name="Light Level",
            description="The telescope light level, as measured by the Telescope Acquisition Camera, at the start of "
            "data acquisition of each frame.",
            metric_code=MetricCode.light_level,
            xlabel="Time",
            ylabel="Light Level (adu)",
            series_data=series_data,
            statement=f"Average Light Level for L1 dataset: "
            f"{round(np.mean(values), 2)} ± {round(np.std(values), 2)} adu",
            warnings=None,
        )

    def quality_store_frame_average(
        self,
        datetimes: list[str],
        values: list[float],
        task_type: str,
        modstate: int | None = None,
    ):
        """Collect and store datetime / value pairs for the individual frame averages."""
        tags = [Tag.quality(MetricCode.frame_average)]
        if modstate:
            tags.append(Tag.modstate(modstate))
        self._record_2d_plot_values(
            x_values=datetimes,
            y_values=values,
            tags=tags,
            series_name=modstate or 1,
            task_type=task_type,
        )

    def quality_build_frame_average(self, task_type: str) -> dict:
        """Build frame average schema from stored data."""
        # This will load data for all modstates, if present
        series_data = self._load_2d_plot_values(
            tags=Tag.quality(MetricCode.frame_average), task_type=task_type
        )

        # Build metric dict
        if len(series_data) > 0:
            datetimes, values = list(series_data.values())[0]
            warnings = self._find_iqr_outliers(datetimes=datetimes, values=values)
            return self._create_2d_plot_with_datetime_metric(
                name=f"Average Across Frame - {task_type.upper()}",
                description=f"Average intensity value across frames of task type {task_type}. One measurement is taken per frame in each task type.",
                metric_code=MetricCode.frame_average,
                facet=task_type.upper(),
                xlabel="Time",
                ylabel="Average Value (adu / sec)",
                series_data=series_data,
                series_name="Modstate",
                warnings=self._format_warnings(warnings),
            )

    def quality_store_frame_rms(
        self,
        datetimes: list[str],
        values: list[float],
        task_type: str,
        modstate: int | None = None,
    ):
        """Collect and store datetime / value pairs for the individual frame rms."""
        tags = [Tag.quality(MetricCode.frame_rms)]
        if modstate:
            tags.append(Tag.modstate(modstate))
        self._record_2d_plot_values(
            x_values=datetimes,
            y_values=values,
            tags=tags,
            series_name=modstate or 1,
            task_type=task_type,
        )

    def quality_build_frame_rms(self, task_type: str) -> dict:
        """Build frame rms schema from stored data."""
        # This will load data for all modstates, if present
        series_data = self._load_2d_plot_values(
            tags=Tag.quality(MetricCode.frame_rms), task_type=task_type
        )

        # Build metric dict
        if len(series_data) > 0:
            datetimes, values = list(series_data.values())[0]
            warnings = self._find_iqr_outliers(datetimes=datetimes, values=values)
            return self._create_2d_plot_with_datetime_metric(
                name=f"Root Mean Square (RMS) Across Frame - {task_type.upper()}",
                description=f"RMS value across frames of task type {task_type}. One measurement is taken per frame in each task type.",
                metric_code=MetricCode.frame_rms,
                facet=task_type.upper(),
                xlabel="Time",
                ylabel="RMS (adu / sec)",
                series_data=series_data,
                series_name="Modstate",
                warnings=self._format_warnings(warnings),
            )

    def quality_store_noise(self, datetimes: list[str], values: list[float], stokes: str = "I"):
        """Collect and store datetime / value pairs for the noise data."""
        self._record_2d_plot_values(
            x_values=datetimes,
            y_values=values,
            series_name=stokes,
            tags=[Tag.quality(MetricCode.noise), Tag.stokes(stokes)],
        )

    def quality_build_noise(self) -> dict:
        """Build noise schema from stored data."""
        series_data = self._load_2d_plot_values(tags=[Tag.quality(MetricCode.noise)])
        return self._create_2d_plot_with_datetime_metric(
            name=f"Noise Estimation",
            description="Estimate of the noise in L1 frames. Noise is computed as the average of the stddev of "
            "boxes/cubes that extend 1/5 from the edge of the images on all sides. "
            "One measurement taken per L1 frame.",
            metric_code=MetricCode.noise,
            xlabel="Time",
            ylabel="Noise (adu)",
            series_data=series_data,
            warnings=None,
        )

    def quality_store_sensitivity(
        self, stokes: Literal["I", "Q", "U", "V"], datetimes: list[str], values: list[float]
    ):
        """Collect and store datetime / value pairs for the polarimetric noise data."""
        self._record_2d_plot_values(
            x_values=datetimes,
            y_values=values,
            series_name=stokes,
            tags=[Tag.quality(MetricCode.sensitivity), Tag.stokes(stokes)],
        )

    def quality_build_sensitivity(self) -> dict:
        """Build polarimetric noise schema from stored data."""
        series_data = self._load_2d_plot_values(tags=[Tag.quality(MetricCode.sensitivity)])
        return self._create_2d_plot_with_datetime_metric(
            name=f"Sensitivity",
            description=f"Sensitivity is defined as the stddev of a particular Stokes parameter divided by the signal in "
            f"Stokes I (computed as a median over the whole frame). One measurement is shown per map scan.",
            metric_code=MetricCode.sensitivity,
            xlabel="Time",
            ylabel=r"$\frac{\sigma_X}{\mathrm{med}(I)}$",
            ylabel_horizontal=True,
            series_data=series_data,
            series_name="Stokes Parameter",
            warnings=None,
        )


class _TableQualityMixin:
    """Mixing for metrics that present as tables."""

    @staticmethod
    def _create_table_metric(
        name: str,
        description: str,
        metric_code: str,
        rows: list[list[Any]],
        statement: str | None = None,
        warnings: list[str] | None = None,
        facet: str | None = None,
    ) -> dict:
        metric = ReportMetric(
            name=name,
            description=description,
            metric_code=metric_code,
            facet=facet,
            statement=statement,
            table_data=SimpleTable(rows=rows),
            warnings=warnings,
        )
        return metric.model_dump()

    def quality_store_health_status(self, values: list[str]):
        """
        Collect and store health status data.

        Parameters
        ----------
        values: statuses as listed in the headers
        """
        self._record_values(values=values, tags=Tag.quality(MetricCode.health_status))

    def quality_build_health_status(self) -> dict:
        """Build health status schema from stored data."""
        values = []
        for path in self.read(tags=Tag.quality(MetricCode.health_status)):
            with path.open() as f:
                data = json.load(f)
                values += data
        statuses, counts = np.unique(values, return_counts=True)
        statuses = [s.lower() for s in statuses]
        # JSON serialization does not work with numpy types
        counts = [int(c) for c in counts]
        warnings = []
        if any(s in statuses for s in ["bad", "ill", "unknown"]):
            warnings.append(
                "Data sourced from components with a health status of 'ill', 'bad', or 'unknown'."
            )
        table_data = [list(z) for z in zip(statuses, counts)]
        table_data.insert(0, ["Status", "Count"])
        return self._create_table_metric(
            name="Data Source Health",
            description="This metric contains the worst health status of the data source during "
            "data acquisition. One reading is taken per L1 frame.",
            metric_code=MetricCode.health_status,
            rows=table_data,
            warnings=self._format_warnings(warnings),
        )

    def quality_store_task_type_counts(
        self, task_type: str, total_frames: int, frames_not_used: int = 0
    ):
        """
        Collect and store task type data.

        Parameters
        ----------
        task_type: task type as listed in the headers
        total_frames: total number of frames supplied of the given task type
        frames_not_used: if some frames aren't used, how many
        """
        data = {
            "task_type": task_type.upper(),
            "total_frames": total_frames,
            "frames_not_used": frames_not_used,
        }
        self._record_values(values=data, tags=Tag.quality(MetricCode.task_types))

    def quality_build_task_type_counts(self) -> dict:
        """Build task type count schema from stored data."""
        # Raise warning if more than 5% of frames of a given type are not used
        warning_count_threshold = 0.05
        default_int_dict = partial(defaultdict, int)
        task_type_counts = defaultdict(default_int_dict)
        # Loop over files that contain data for this metric
        for path in self.read(tags=Tag.quality(MetricCode.task_types)):
            with path.open() as f:
                data = json.load(f)
                task_type_counts[data["task_type"]]["total_frames"] += data["total_frames"]
                task_type_counts[data["task_type"]]["frames_not_used"] += data["frames_not_used"]

        # Now, build metric from the counts dict
        table_data = [[i[0]] + list(i[1].values()) for i in task_type_counts.items()]
        warnings = []
        for row in table_data:
            if row[1] == 0:
                warnings.append(f"NO {row[0]} frames were used!")
            elif row[2] / row[1] > warning_count_threshold:
                warnings.append(
                    f"{round(100 * row[2] / row[1], 1)}% of frames were not used in the "
                    f"processing of task type {row[0]}"
                )
        # Add header row
        table_data.insert(0, ["Task Type", "Total Frames", "Unused Frames"])
        return self._create_table_metric(
            name="Frame Counts",
            description="This metric is a count of the number of frames used to produce a "
            "calibrated L1 dataset",
            metric_code=MetricCode.task_types,
            rows=table_data,
            warnings=self._format_warnings(warnings),
        )

    def quality_store_dataset_average(self, task_type: str, frame_averages: list[float]):
        """
        Collect and store dataset average.

        Parameters
        ----------
        task_type: task type as listed in the headers
        frame_averages: average value of all pixels in each frame of the given task type
        """
        data = {"task_type": task_type, "frame_averages": frame_averages}
        self._record_values(values=data, tags=Tag.quality(MetricCode.dataset_average))

    def quality_build_dataset_average(self) -> dict:
        """Build dataset average schema from stored data."""
        dataset_averages = defaultdict(list)
        # Loop over files that contain data for this metric
        for path in self.read(tags=Tag.quality(MetricCode.dataset_average)):
            with path.open() as f:
                data = json.load(f)
                # Add counts for the task type to its already existing counts
                dataset_averages[data["task_type"]] += data["frame_averages"]

        # Now, build metric from the counts dict
        table_data = [[i[0], round(np.mean(i[1]), 2)] for i in dataset_averages.items()]
        # Add header row
        table_data.insert(0, ["Task Type", "Dataset Average (adu / sec)"])
        return self._create_table_metric(
            name="Average Across Dataset",
            description="This metric is the calculated mean intensity value across data from an "
            "instrument program task type used in the creation of an entire L1 "
            "dataset.",
            metric_code=MetricCode.dataset_average,
            rows=table_data,
            warnings=None,
        )

    def quality_store_dataset_rms(self, task_type: str, frame_rms: list[float]):
        """
        Collect and store dataset average.

        Parameters
        ----------
        task_type: task type as listed in the headers
        frame_rms: rms value of all pixels in each frame of the given task type
        """
        data = {"task_type": task_type, "frame_rms": frame_rms}
        self._record_values(values=data, tags=Tag.quality(MetricCode.dataset_rms))

    def quality_build_dataset_rms(self) -> dict:
        """Build dataset rms schema from stored data."""
        dataset_rms = {}
        # Loop over files that contain data for this metric
        for path in self.read(tags=Tag.quality(MetricCode.dataset_rms)):
            with path.open() as f:
                data = json.load(f)
                # If the task type isn't in the dict, add it with counts set to zero
                if not data["task_type"] in dataset_rms.keys():
                    dataset_rms[data["task_type"]] = []
                # Add counts for the task type to its already existing counts
                dataset_rms[data["task_type"]] += data["frame_rms"]

        # Now, build metric from the counts dict
        table_data = [[i[0], round(np.mean(i[1]), 2)] for i in dataset_rms.items()]
        # Add header row
        table_data.insert(0, ["Task Type", "Dataset RMS (adu / sec)"])
        return self._create_table_metric(
            name="Dataset RMS",
            description="This metric is the calculated root mean square intensity value across data"
            " from an instrument program task type used in the creation of an entire "
            "L1 dataset.",
            metric_code=MetricCode.dataset_rms,
            rows=table_data,
            warnings=None,
        )

    def quality_store_historical(self, name: str, value: Any, warning: str | None = None):
        """
        Insert historical data into the schema used to record quality info.

        Parameters
        ----------
        name: name of the parameter / measurement to be recorded
        value: value of the parameter / measurement to be recorded
        warning: warning to be entered into the quality report
        """
        data = {"name": name, "value": value, "warnings": warning}
        self._record_values(values=data, tags=Tag.quality(MetricCode.historical))

    def quality_build_historical(self) -> dict:
        """Build historical data schema from stored data."""
        table_data = []
        warnings = []
        # Loop over files that contain data for this metric
        for path in self.read(tags=Tag.quality(MetricCode.historical)):
            with path.open() as f:
                data = json.load(f)
                table_data.append([data["name"], data["value"]])
                if data["warnings"] is not None:
                    warnings.append(data["warnings"])

        # Add header row
        table_data.insert(0, ["Metric", "Value"])
        return self._create_table_metric(
            name="Historical Comparisons",
            description="Over time, the data center will be comparing some of the above quality "
            "metrics and other parameters derived from file headers to see how the "
            "DKIST instruments and observations are changing.",
            metric_code=MetricCode.historical,
            rows=table_data,
            warnings=self._format_warnings(warnings),
        )


class _PolcalQualityMixin:
    """Mixin Class supporting the building of polcal-specific metrics."""

    def quality_store_polcal_results(
        self,
        *,
        polcal_fitter: PolcalFitter,
        label: str,
        bin_nums: list[int],
        bin_labels: list[str],
        skip_recording_constant_pars: bool = False,
        num_points_to_sample: int | None = None,
    ):
        """Compute and store all PolCal related metrics."""
        thinning_stride = self._compute_thinning_stride(polcal_fitter, num_points_to_sample)

        if not skip_recording_constant_pars:
            logger.info("Storing constant parameter values")
            self._store_polcal_constant_parameter_values(polcal_fitter=polcal_fitter, label=label)

        logger.info("Storing global parameter values")
        self._store_polcal_global_parameter_values(polcal_fitter=polcal_fitter, label=label)

        logger.info("Storing local parameter values")
        self._store_polcal_local_parameter_values(
            polcal_fitter=polcal_fitter,
            label=label,
            bin_nums=bin_nums,
            bin_labels=bin_labels,
            thinning_stride=thinning_stride,
        )

        logger.info("Storing fit residuals")
        self._store_polcal_fit_resdiuals(
            polcal_fitter=polcal_fitter,
            label=label,
            bin_nums=bin_nums,
            bin_labels=bin_labels,
            thinning_stride=thinning_stride,
        )

        logger.info("Storing modulation matrix efficiencies")
        self._store_polcal_modulation_efficiency(
            polcal_fitter=polcal_fitter,
            label=label,
            bin_nums=bin_nums,
            bin_labels=bin_labels,
            thinning_stride=thinning_stride,
        )

    @staticmethod
    def _format_facet(label: str | None) -> str | None:
        """Format the label as a typical key.  For example, `Beam 1` becomes `BEAM_1`."""
        if label is None or label == "":
            return None
        return str(label).replace(" ", "_").upper()

    @staticmethod
    def _compute_thinning_stride(
        polcal_fitter: PolcalFitter, num_points_to_sample: int
    ) -> int | None:
        """
        Compute the stride needed to collect the requested number of data samples.

        E.g., if there are 20,000 samples in the full `polcal_fitter` and the user wants to only save 200 then the
        stride will be 100.

        `None` is returned if no subsampling has been requested or if the number of requested samples is larger than
        then number of samples in the full `polcal_fitter`.
        """
        if num_points_to_sample is None:
            return None

        num_total_points = np.prod(polcal_fitter.local_objects.dresser.shape)
        if num_points_to_sample > num_total_points:
            return None

        remainder = num_total_points % num_points_to_sample
        if remainder:
            return num_total_points // (num_points_to_sample - 1)

        return num_total_points // num_points_to_sample

    def _store_polcal_constant_parameter_values(
        self, *, polcal_fitter: PolcalFitter, label: str
    ) -> None:
        """Store the global parameters that are held constant during the polcal fit.

        These are interesting and useful to anyone who wants to recreate the polcal models for themselves.
        """
        calibration_unit = polcal_fitter.global_objects.calibration_unit
        p_y = calibration_unit.py

        init_pars = polcal_fitter.global_objects.init_parameters.first_parameters
        vals_dict = init_pars.valuesdict()

        param_names = ["polarizer p_y"]
        param_vals = [p_y]

        for parname in TELESCOPE_PARAMS:
            param_names.append(parname)
            param_vals.append(vals_dict[parname])

        data = {"task_type": label, "param_names": param_names, "param_vals": param_vals}
        self._record_values(
            values=data,
            tags=[Tag.quality(MetricCode.polcal_constant_par_vals), Tag.quality_task(label)],
        )

    def quality_build_polcal_constant_parameter_values(self, label: str) -> dict:
        """Build Polcal constant parameter value table schema from stored data."""
        data_file = next(
            self.read(
                tags=[
                    Tag.quality(MetricCode.polcal_constant_par_vals),
                    Tag.quality_task(label),
                ]
            )
        )
        with data_file.open() as f:
            data = json.load(f)

        table_data = [["Parameter", "Value used during fit"]]
        for pn, pv in zip(data["param_names"], data["param_vals"]):
            try:
                pv_str = f"{pv: 9.6f}"
            except ValueError:
                # This should really *never* get triggered, but just in case we don't want the whole thing to blow up
                pv_str = str(pv)
            table_data.append([pn, pv_str])

        metric = ReportMetric(
            name=f"PolCal Constant Values in Calibration Unit Fit",
            description="These values are important aspects of the polcal model, but are held constant during Calibration "
            'Unit fits. p_y is the "transmission leakage" of the polarizer (see Appendix D of Harrington et '
            "al. 2021 for more information). The (x, t) pairs parameterize mirror Mueller matrices for "
            "three mirror groups; M12, M34, and M56.",
            metric_code=MetricCode.polcal_constant_par_vals,
            table_data=SimpleTable(rows=table_data),
        )
        return metric.model_dump()

    def _store_polcal_global_parameter_values(
        self,
        *,
        polcal_fitter: PolcalFitter,
        label: str,
    ) -> None:
        """Compute and store best-fit polcal parameter statistics.

        Namely, the fit value and its absolute and relative deviation from database metrology values.
        """
        init_pars = polcal_fitter.global_objects.init_parameters.first_parameters
        fit_pars = polcal_fitter.global_objects.fit_parameters.first_parameters

        # Record the values and diffs
        param_names = []
        param_vary = []
        param_init_vals = []
        param_fit_vals = []
        param_diffs = []
        param_ratios = []
        warnings = []
        for param, init_val in init_pars.valuesdict().items():
            # All parameter names are internally labeled with what Calibration Sequence (CS) they come from.
            #  Here we remove that label because we only care about the base name and these metrics only apply
            #  to data from single-CS fits.
            base_name = param.split("_CS")[0]
            if base_name not in GLOBAL_PARAMS and base_name not in CU_PARAMS:
                # Not a global parameter, so we don't need to analyze it.
                continue

            best_fit_val = fit_pars[param].value
            unit = ""
            if base_name in ["ret0h", "ret045", "ret0r"]:
                # One of the 3 elliptical retardance parameters.
                unit = " [deg]"
                init_val = np.rad2deg(init_val)  # Convert from radians
                best_fit_val = np.rad2deg(best_fit_val)

            if base_name in ["t_pol", "t_ret"]:
                # One of the optic transmissions. These are nicer as percents.
                unit = " [%]"
                init_val *= 100.0
                best_fit_val *= 100.0

            param_names.append(base_name + unit)
            param_vary.append(init_pars[param].vary)
            param_init_vals.append(init_val)
            param_fit_vals.append(best_fit_val)
            diff = init_val - best_fit_val
            if base_name in ["ret0h", "ret045", "ret0r"] and abs(diff) > 3.0:
                # Retardance values should be within 3 deg of the db value
                warnings.append(
                    f"{base_name.replace(' [deg]', '')} fit value deviates from the initial value by a large amount ({diff:.2f} degrees)"
                )

            if base_name in ["t_pol", "t_ret"] and abs(diff) > 5:
                # Optic transmission values should be within 5% of the db value
                warnings.append(
                    f"{base_name} fit value deviates from the initial value by a large amount ({abs(diff):.2f}%)"
                )
            param_diffs.append(diff)
            ratio = np.abs(diff) / init_val

            # NaN's look weird in a table. Replace with "-" instead.
            if np.isnan(ratio) or np.isinf(ratio):
                ratio = "-"
            param_ratios.append(ratio)

        data = {
            "task_type": label,
            "param_names": param_names,
            "param_vary": param_vary,
            "param_init_vals": param_init_vals,
            "param_fit_vals": param_fit_vals,
            "param_diffs": param_diffs,
            "param_ratios": param_ratios,
            "warnings": warnings,
        }
        self._record_values(
            values=data,
            tags=[Tag.quality(MetricCode.polcal_global_par_vals), Tag.quality_task(label)],
        )

    def quality_build_polcal_global_parameter_values(self, label: str) -> dict:
        """Build Polcal global parameter value table schema from stored data."""
        # This *could* exist in the _TableQualityMixin because it is just a simple table, but it's kept here because
        # it's corresponding store* method needs to be here for calling from the top-level quality_store_polcal_results
        data_file = next(
            self.read(
                tags=[Tag.quality(MetricCode.polcal_global_par_vals), Tag.quality_task(label)]
            )
        )
        with data_file.open() as f:
            data = json.load(f)

        table_data = [
            [
                "Parameter",
                "Free in Fit?",
                "Init Value",
                "Best Fit Value",
                "Difference",
                "Relative Diff.",
            ]
        ]
        for pn, pv, pi, pfv, pd, pr in zip(
            data["param_names"],
            data["param_vary"],
            data["param_init_vals"],
            data["param_fit_vals"],
            data["param_diffs"],
            data["param_ratios"],
        ):
            try:
                pi_str = f"{pi: 6.2f}"
            except ValueError:
                pi_str = str(pi)
            try:
                pfv_str = f"{pfv: 6.2f}"
            except ValueError:
                pfv_str = str(pfv)
            try:
                pd_str = f"{pd: .2e}"
            except ValueError:
                pd_str = str(pd)
            try:
                pr_str = f"{pr: .2e}"
            except ValueError:
                pr_str = str(pr)
            table_data.append([pn, pv, pi_str, pfv_str, pd_str, pr_str])

        metric = ReportMetric(
            name=f"PolCal Global Calibration Unit Fit - {label}",
            description="The deviation from database metrology values for Calibration Unit parameters used to compute "
            f"demodulation matrices. These parameters are fit the same across all polcal bins.",
            metric_code=MetricCode.polcal_global_par_vals,
            facet=self._format_facet(label),
            table_data=SimpleTable(rows=table_data),
            warnings=self._format_warnings(data["warnings"]),
        )
        return metric.model_dump()

    def _store_polcal_local_parameter_values(
        self,
        *,
        polcal_fitter: PolcalFitter,
        label: str,
        bin_nums: list[int],
        bin_labels: list[str],
        thinning_stride: int | None,
    ) -> None:
        """Store local polcal parameter fits.

        First, flatten FOV bins dimensions, compute modulation matrices, and record I_sys for all bins.

        Then convert to python lists for serialization and write to disk.
        """
        ## Modulation matrices
        fov_shape = polcal_fitter.local_objects.dresser.shape
        num_mod = polcal_fitter.local_objects.dresser.nummod
        flattened_demod = np.reshape(
            polcal_fitter.demodulation_matrices, (np.prod(fov_shape), 4, num_mod)
        )
        flattened_mod_list = []
        # Need to apply stride this was (instead of argument to `range` because `range` doesn't accept `None` for
        #  step argument.
        for i in range(flattened_demod.shape[0])[::thinning_stride]:
            try:
                flattened_mod_list.append(np.linalg.pinv(flattened_demod[i]))
            except:
                pass

        flattened_mod = np.stack(flattened_mod_list)
        # Move axis so numpoints is the last dimension, which will be easier to understand when
        # plotting
        flattened_mod = np.moveaxis(flattened_mod, 0, -1)

        # Because ndarrays can't be Json'd
        mod_list = flattened_mod.tolist()

        # Now get the rest of the free variables
        fit_params = polcal_fitter.local_objects.fit_parameters
        init_param = polcal_fitter.local_objects.init_parameters
        param_metadata = fit_params.first_parameters

        free_param_data = dict()
        num_varied_I_sys = 0
        for param in param_metadata.keys():
            # Don't grab modulation matrix values because we got those above.
            # Also don't grab any parameters that were fixed.
            if "modmat" in param or not param_metadata[param].vary:
                continue

            if param.startswith("I_sys"):
                num_varied_I_sys += 1

            fit_value_list = []
            for point_param in fit_params._all_parameters[::thinning_stride]:
                value = point_param[param].value
                if not np.isnan(value):
                    fit_value_list.append(value)

            init_value = init_param.first_parameters[param].value

            free_param_data[param] = {"fit_values": fit_value_list, "init_value": init_value}

        data = {
            "task_type": label,
            "bin_strs": [
                f"{num_bins} {bin_label}" for num_bins, bin_label in zip(bin_nums, bin_labels)
            ],
            "total_bins": int(np.prod(bin_nums)),
            "sampled_bins": flattened_mod.shape[-1],
            "num_varied_I_sys": num_varied_I_sys,
            "modmat_list": mod_list,
            "free_param_dict": free_param_data,
        }
        self._record_values(
            values=data,
            tags=[Tag.quality(MetricCode.polcal_local_par_vals), Tag.quality_task(label)],
        )

    def quality_build_polcal_local_parameter_values(self, label: str) -> dict:
        """Build a modulation matrix and I_sys histograms schema from stored data."""
        data_file = next(
            self.read(tags=[Tag.quality(MetricCode.polcal_local_par_vals), Tag.quality_task(label)])
        )
        with data_file.open() as f:
            data = json.load(f)

        modmat_hist = ModulationMatrixHistograms(modmat_list=data["modmat_list"])
        free_param_dict = data["free_param_dict"]
        I_sys_series_data = dict()
        I_sys_vertical_lines = dict()
        for step in range(data["num_varied_I_sys"]):
            I_sys_series_data[f"CS step {step}"] = free_param_dict[f"I_sys_CS00_step{step:02n}"][
                "fit_values"
            ]
            if step == 0:
                I_sys_vertical_lines["init value"] = free_param_dict[f"I_sys_CS00_step{step:02n}"][
                    "init_value"
                ]

        I_sys_hist = PlotHistogram(
            xlabel="I_sys", series_data=I_sys_series_data, vertical_lines=I_sys_vertical_lines
        )

        param_histograms = [I_sys_hist]
        for param, param_data in free_param_dict.items():
            if "I_sys" in param:
                # We already dealt with I_sys above
                continue

            plot_name = param.replace("_CS00", "")
            hist = PlotHistogram(
                xlabel=plot_name,
                series_data={plot_name: param_data["fit_values"]},
                vertical_lines={"init value": param_data["init_value"]},
            )
            param_histograms.append(hist)

        description = (
            "The first plot shows histograms of the individual modulation matrix elements. "
        )
        "Note that the first element is not shown because it is always fixed to 1 in fits. "
        "Subsequent plots show the distribution of all other free parameters in the fit, along with their initial "
        "values. For I_sys there is a separate fit value for each CS step."
        description += self._compute_bin_description(
            total_bins=data["total_bins"],
            bin_strs=data["bin_strs"],
            sampled_bins=data["sampled_bins"],
        )

        metric = ReportMetric(
            name=f"PolCal Local Bin Fits - {label}",
            description=description,
            metric_code=MetricCode.polcal_local_par_vals,
            facet=self._format_facet(label),
            modmat_data=modmat_hist,
            histogram_data=param_histograms,
        )
        return metric.model_dump()

    def _store_polcal_fit_resdiuals(
        self,
        *,
        polcal_fitter: PolcalFitter,
        label: str,
        bin_nums: list[int],
        bin_labels: list[str],
        thinning_stride: int | None,
    ):
        """Store flux residuals and chisq values for a local fit."""
        fit_container = polcal_fitter.local_objects
        fov_shape = fit_container.dresser.shape
        num_mod = fit_container.dresser.nummod
        num_steps = fit_container.dresser.numsteps
        num_points = np.prod(fov_shape)
        residual_array = np.zeros((num_mod, num_steps, num_points))
        red_chi_list = []
        for i in range(num_points)[::thinning_stride]:
            ## Fit residuals
            point_TM = copy.deepcopy(fit_container.telescope)
            point_CM = copy.deepcopy(fit_container.calibration_unit)

            idx = np.unravel_index(i, fov_shape)
            I_cal, I_unc = fit_container.dresser[idx]
            fit_params = fit_container.fit_parameters[idx]
            modmat = np.zeros((I_cal.shape[0], 4), dtype=np.float64)
            flat_residual = compare_I(
                params=fit_params,
                I_cal=I_cal,
                I_unc=I_unc,
                TM=point_TM,
                CM=point_CM,
                modmat=modmat,
                use_M12=True,
            )
            diff = np.reshape(flat_residual, (num_mod, num_steps))
            residual_array[:, :, i] = diff

            ## Red Chisq
            chisq = np.sum(flat_residual**2)
            num_free = sum([fit_params[p].vary for p in fit_params])
            red_chisq = chisq / num_free
            if not np.isnan(red_chisq):
                red_chi_list.append(red_chisq)

        # Convert residuals to panda DataFrame, which will greatly simplify plotting
        col_list = sum(
            [
                [[r, i + 1, j + 1] for r in residual_array[i, j, :]]
                for i in range(num_mod)
                for j in range(num_steps)
            ],
            [],
        )
        residual_dataframe = DataFrame(
            data=col_list, columns=["Flux residual", "Modstate", "CS Step"]
        )
        dataframe_str = residual_dataframe.to_json()

        data = {
            "task_type": label,
            "bin_strs": [
                f"{num_bins} {bin_label}" for num_bins, bin_label in zip(bin_nums, bin_labels)
            ],
            "total_bins": int(np.prod(bin_nums)),
            "sampled_bins": len(red_chi_list),
            "residual_json": dataframe_str,
            "red_chi_list": red_chi_list,
        }
        self._record_values(
            values=data,
            tags=[Tag.quality(MetricCode.polcal_fit_residuals), Tag.quality_task(label)],
        )

    def quality_build_polcal_fit_residuals(self, label: str) -> dict:
        """Build a metric containing flux residuals and reduced chisq values for all fits.

        The chisq values will turn into a histogram and the flux residuals will turn into a very fancy
        violin plot.
        """
        data_file = next(
            self.read(tags=[Tag.quality(MetricCode.polcal_fit_residuals), Tag.quality_task(label)])
        )
        with data_file.open() as f:
            data = json.load(f)

        chisq = data["red_chi_list"]
        avg_chisq = np.mean(chisq)
        chisq_hist = PlotHistogram(
            xlabel="Reduced Chisq",
            series_data={"Red chisq": chisq},
            vertical_lines={f"Mean = {avg_chisq:.2f}": avg_chisq},
        )
        residual_series = PlotRaincloud(
            xlabel="CS Step",
            ylabel=r"$\frac{I_{fit} - I_{obs}}{\sigma_I}$",
            ylabel_horizontal=True,
            categorical_column_name="CS Step",
            distribution_column_name="Flux residual",
            hue_column_name="Modstate",
            dataframe_json=data["residual_json"],
        )

        description = "The top plot shows relative flux residual distributions for all polcal Calibration Sequence steps. The bottom plot shows the reduced chi-squared distribution of all fits."
        description += self._compute_bin_description(
            total_bins=data["total_bins"],
            bin_strs=data["bin_strs"],
            sampled_bins=data["sampled_bins"],
        )

        metric = ReportMetric(
            name=f"PolCal Fit Residuals - {label}",
            description=description,
            metric_code=MetricCode.polcal_fit_residuals,
            facet=self._format_facet(label),
            histogram_data=chisq_hist,
            raincloud_data=residual_series,
        )
        return metric.model_dump()

    def _store_polcal_modulation_efficiency(
        self,
        *,
        polcal_fitter: PolcalFitter,
        label: str,
        bin_nums: list[int],
        bin_labels: list[str],
        thinning_stride: int | None,
    ):
        """Compute modulation efficiency for all fit bins and store in a file."""
        fov_shape = polcal_fitter.local_objects.dresser.shape
        num_mod = polcal_fitter.local_objects.dresser.nummod
        num_points = np.prod(fov_shape)
        flat_demod = np.reshape(polcal_fitter.demodulation_matrices, (num_points, 4, num_mod))
        thinned_demod = flat_demod[::thinning_stride, :, :]
        # This will have shape (num_points, 4)
        flat_efficiency = 1.0 / np.sqrt(num_mod * np.sum(thinned_demod**2, axis=2))

        nan_idx = np.sum(np.isnan(flat_efficiency), axis=1).astype(bool)
        flat_efficiency = flat_efficiency[~nan_idx, :]

        # Because ndarrays are not JSON-able
        # Also, transpose it so the Stokes parameters are the first dimension
        efficiency_list = flat_efficiency.T.tolist()

        warnings = []
        stokes_names = ["I", "Q", "U", "V"]
        efficiency_thresholds = [0.8, 0.4, 0.4, 0.4]
        means = np.mean(flat_efficiency, axis=0)
        for i, (stokes, thresh) in enumerate(zip(stokes_names, efficiency_thresholds)):
            if means[i] < thresh:
                warnings.append(
                    f"Stokes {stokes} has a low mean efficiency ({means[i] * 100:.1f} %)"
                )
        data = {
            "task_type": label,
            "bin_strs": [
                f"{num_bins} {bin_label}" for num_bins, bin_label in zip(bin_nums, bin_labels)
            ],
            "total_bins": int(np.prod(bin_nums)),
            "sampled_bins": flat_efficiency.shape[0],
            "efficiency_list": efficiency_list,
            "warnings": warnings,
        }
        self._record_values(
            values=data,
            tags=[Tag.quality(MetricCode.polcal_efficiency), Tag.quality_task(label)],
        )

    def quality_build_polcal_efficiency(self, label: str) -> dict:
        """Build a metric containing samples of the modulation efficiency for each stokes parameter."""
        data_file = next(
            self.read(tags=[Tag.quality(MetricCode.polcal_efficiency), Tag.quality_task(label)])
        )
        with data_file.open() as f:
            data = json.load(f)

        description = "The modulation efficiencies for all fit modulation matrices."
        description += self._compute_bin_description(
            total_bins=data["total_bins"],
            bin_strs=data["bin_strs"],
            sampled_bins=data["sampled_bins"],
        )

        metric = ReportMetric(
            name=f"PolCal Modulation Efficiency - {label}",
            description=description,
            metric_code=MetricCode.polcal_efficiency,
            facet=self._format_facet(label),
            efficiency_data=EfficiencyHistograms(efficiency_list=data["efficiency_list"]),
            warnings=self._format_warnings(data["warnings"]),
        )
        return metric.model_dump()

    @staticmethod
    def _compute_bin_description(
        total_bins: int, bin_strs: list[str], sampled_bins: int | None = None
    ) -> str:
        """
        Construct a grammatically correct string that describes the layout of bins present in polcal data.

        There are 3 cases:

        1. If only one bin-type is found we get "...spanning N TYPE bins."

        2. If two bin-types are found we get "...spanning N TYPE1 and M TYPE2 bins."

        3. For greater than two bin-types we get a list with commas and a final "and":
           "...spanning N TYPE1, M TYPE2, ..., and K TYPEK bins."
        """
        base_str = f" Data show"
        if sampled_bins is not None:
            base_str += f" {sampled_bins} uniformly sampled points from"

        base_str += f" {total_bins} total points spanning "

        if len(bin_strs) == 1:
            base_str += bin_strs[0]
        elif len(bin_strs) == 2:
            base_str += " and ".join(bin_strs)
        else:
            base_str += ", ".join(bin_strs[:-1])
            base_str += f", and {bin_strs[-1]}"

        base_str += " bins."

        return base_str


class _WavecalQualityMixin:
    """Mixin class supporting the recording and building of wavecal-related metrics."""

    def quality_store_wavecal_results(
        self,
        *,
        input_wavelength: u.Quantity,
        input_spectrum: np.ndarray,
        fit_result: FitResult,
        weights: None | np.ndarray = None,
    ):
        """
        Store the results of a wavelength solution fit.

        Namely, save the:

        * Input spectrum and wavelength
        * Best-fit combined atlas spectrum
        * Best-fit wavelength vector
        * Fit residuals

        Note that the residuals are the *unweighed* residuals.
        """
        weight_data = np.ones(input_wavelength.size) if weights is None else weights
        prepared_weights = np.sqrt(weight_data / np.sum(weight_data))
        residuals = fit_result.minimizer_result.residual / prepared_weights
        residuals[~np.isfinite(residuals)] = 0.0
        best_fit_atlas = input_spectrum - residuals
        normalized_residuals = residuals / input_spectrum

        best_fit_header = fit_result.wavelength_parameters.to_header(axis_num=1)
        wcs = WCS(best_fit_header)
        best_fit_wavelength = wcs.spectral.pixel_to_world(np.arange(input_spectrum.size))

        finite_idx = (
            np.isfinite(input_wavelength)
            * np.isfinite(input_spectrum)
            * np.isfinite(best_fit_wavelength)
            * np.isfinite(best_fit_atlas)
            * np.isfinite(normalized_residuals)
            * np.isfinite(weight_data)
        )

        data = {
            "input_wavelength_nm": input_wavelength.to_value(u.nm)[finite_idx].tolist(),
            "input_spectrum": input_spectrum[finite_idx].tolist(),
            "best_fit_wavelength_nm": best_fit_wavelength.to_value(u.nm)[finite_idx].tolist(),
            "best_fit_atlas": best_fit_atlas[finite_idx].tolist(),
            "normalized_residuals": normalized_residuals[finite_idx].tolist(),
            "weights": None if weights is None else weight_data[finite_idx].tolist(),
        }

        self._record_values(values=data, tags=[Tag.quality(MetricCode.wavecal_fit)])

    def quality_build_wavecal_results(self) -> dict:
        """Build a ReportMetric containing a multi-pane plot showing the fit spectra and residuals."""
        data = next(self.read(tags=[Tag.quality(MetricCode.wavecal_fit)], decoder=json_decoder))

        input_wave_list = data["input_wavelength_nm"]
        input_spectrum_list = data["input_spectrum"]
        best_fit_wave_list = data["best_fit_wavelength_nm"]
        best_fit_atlas_list = data["best_fit_atlas"]
        residuals_list = data["normalized_residuals"]
        weights = data["weights"]

        fit_series = {
            "Best Fit Observations": [best_fit_wave_list, input_spectrum_list],
            "Input Spectrum": [input_wave_list, input_spectrum_list],
            "Best Fit Atlas": [best_fit_wave_list, best_fit_atlas_list],
        }

        # Set the colors and zorder here manually because the JSON-ization of the quality data means we can't be sure of
        # the order these will be plotted in and thus can't rely on the default color-cycler in `dkist-quality`.
        fit_plot_kwargs = {
            "Best Fit Observations": {
                "ls": "-",
                "lw": 4,
                "alpha": 0.8,
                "ms": 0,
                "color": "#FAA61C",
                "zorder": 2,
            },
            "Input Spectrum": {"ls": "-", "alpha": 0.4, "ms": 0, "color": "#1E317A", "zorder": 2.1},
            "Best Fit Atlas": {"color": "k", "ls": "-", "ms": 0, "zorder": 2.2},
        }

        fit_plot = Plot2D(
            xlabel="Wavelength [nm]",
            ylabel="Signal",
            series_data=fit_series,
            plot_kwargs=fit_plot_kwargs,
            sort_series=False,
        )

        residuals_series = {"Residuals": [best_fit_wave_list, residuals_list]}
        residuals_plot_kwargs = {"Residuals": {"ls": "-", "color": "k", "ms": 0}}

        y_min = np.nanpercentile(residuals_list, 2)
        y_max = np.nanpercentile(residuals_list, 98)
        y_range = y_max - y_min
        y_min -= 0.1 * y_range
        y_max += 0.1 * y_range
        residuals_plot = Plot2D(
            xlabel="Wavelength [nm]",
            ylabel=r"$\frac{\mathrm{Obs - Atlas}}{\mathrm{Obs}}$",
            series_data=residuals_series,
            plot_kwargs=residuals_plot_kwargs,
            ylim=(y_min, y_max),
        )

        plot_list = [fit_plot, residuals_plot]
        height_ratios = [1.5, 1.0]
        if weights is not None:
            weight_series = {"Weights": [best_fit_wave_list, weights]}
            weight_plot_kwargs = {"Weights": {"ls": "-", "color": "k", "ms": 0}}
            weight_plot = Plot2D(
                xlabel="Wavelength [nm]",
                ylabel="Fit Weights",
                series_data=weight_series,
                plot_kwargs=weight_plot_kwargs,
            )
            plot_list.append(weight_plot)
            height_ratios.append(1.0)

        full_plot = VerticalMultiPanePlot2D(
            top_to_bottom_plot_list=plot_list,
            match_x_axes=True,
            no_gap=True,
            top_to_bottom_height_ratios=height_ratios,
        )

        metric = ReportMetric(
            name="Wavelength Calibration Results",
            description="These plots show the wavelength solution computed based on fits to a Solar FTS atlas. "
            "The top plot shows the input and best-fit spectra along with the best-fit atlas, which is "
            "a combination of Solar and Telluric spectra. The bottom plot shows the fit residuals.",
            metric_code=MetricCode.wavecal_fit,
            multi_plot_data=full_plot,
        )

        return metric.model_dump()
