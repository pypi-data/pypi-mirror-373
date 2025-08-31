"""Base QualityMixin class that contains machinery common to all metric types."""

from typing import Iterable

import numpy as np

from dkist_processing_common.codecs.json import json_encoder
from dkist_processing_common.codecs.quality import QualityValueEncoder
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tasks.mixin.quality._metrics import _PolcalQualityMixin
from dkist_processing_common.tasks.mixin.quality._metrics import _SimplePlotQualityMixin
from dkist_processing_common.tasks.mixin.quality._metrics import _SimpleQualityMixin
from dkist_processing_common.tasks.mixin.quality._metrics import _TableQualityMixin
from dkist_processing_common.tasks.mixin.quality._metrics import _WavecalQualityMixin


class QualityMixin(
    _SimpleQualityMixin,
    _SimplePlotQualityMixin,
    _TableQualityMixin,
    _PolcalQualityMixin,
    _WavecalQualityMixin,
):
    """Mixin class supporting the generation of the quality reports."""

    def quality_assemble_data(self, polcal_label_list: list[str] | None = None) -> list[dict]:
        """Assemble the quality data by checking for the existence of each metric."""
        report = []
        report += self.quality_task_independent_metrics()
        report += self.quality_task_dependent_metrics()

        polcal_labels = polcal_label_list or []
        report += self.quality_polcal_metrics(polcal_labels)

        return report

    def quality_task_independent_metrics(self) -> list[dict]:
        """Encapsulate task independent metric parsing."""
        result = []
        for metric_name, metric_func in self.quality_metrics_no_task_dependence.items():
            if self._quality_metric_exists(metric_name=metric_name):
                result.append(metric_func())
        return result

    def quality_task_dependent_metrics(self) -> list[dict]:
        """Encapsulate task dependent metric parsing."""
        result = []
        for metric_name, metric_func in self.quality_metrics_task_dependence.items():
            for task_type in self.quality_task_types:
                if self._quality_metric_exists(metric_name=metric_name, task_type=task_type):
                    result.append(metric_func(task_type=task_type))
        return result

    def quality_polcal_metrics(self, label_list: list) -> list[dict]:
        """Encapsulate polcal metric parsing."""
        result = []
        for metric_name, metric_func in self.quality_metrics_polcal.items():
            for label in label_list:
                if self._quality_metric_exists(metric_name=metric_name, task_type=label):
                    result.append(metric_func(label=label))

        return result

    @property
    def quality_task_types(self) -> list[str]:
        """Task types to use in generating metrics that work on several task types."""
        return [
            TaskName.dark.value,
            TaskName.gain.value,
            TaskName.lamp_gain.value,
            TaskName.solar_gain.value,
        ]

    @property
    def quality_metrics_no_task_dependence(self) -> dict:
        """Return a dict of the quality metrics with no task dependence."""
        return {
            "FRIED_PARAMETER": self.quality_build_fried_parameter,
            "LIGHT_LEVEL": self.quality_build_light_level,
            "NOISE": self.quality_build_noise,
            "SENSITIVITY": self.quality_build_sensitivity,
            "HEALTH_STATUS": self.quality_build_health_status,
            "TASK_TYPES": self.quality_build_task_type_counts,
            "DATASET_AVERAGE": self.quality_build_dataset_average,
            "DATASET_RMS": self.quality_build_dataset_rms,
            "HISTORICAL": self.quality_build_historical,
            "AO_STATUS": self.quality_build_ao_status,
            "RANGE": self.quality_build_range,
            "WAVECAL_FIT": self.quality_build_wavecal_results,
        }

    @property
    def quality_metrics_task_dependence(self) -> dict:
        """Return a dict of quality metrics which are dependent on the task."""
        return {
            "FRAME_AVERAGE": self.quality_build_frame_average,
            "FRAME_RMS": self.quality_build_frame_rms,
        }

    @property
    def quality_metrics_polcal(self) -> dict:
        """Return a dict of polcal quality metrics."""
        return {
            "POLCAL_CONSTANT_PAR_VALS": self.quality_build_polcal_constant_parameter_values,
            "POLCAL_GLOBAL_PAR_VALS": self.quality_build_polcal_global_parameter_values,
            "POLCAL_LOCAL_PAR_VALS": self.quality_build_polcal_local_parameter_values,
            "POLCAL_FIT_RESIDUALS": self.quality_build_polcal_fit_residuals,
            "POLCAL_EFFICIENCY": self.quality_build_polcal_efficiency,
        }

    def _quality_metric_exists(self, metric_name: str, task_type: str = None) -> bool:
        """Look for the existence of data on disk for a quality metric."""
        tags = [Tag.quality(quality_metric=metric_name)]
        if task_type:
            tags.append(Tag.quality_task(quality_task_type=task_type))
        try:
            next(self.read(tags=tags))
            return True
        except StopIteration:
            return False

    @staticmethod
    def _format_warnings(warnings: list[str] | None) -> list[str] | None:
        """If warnings is an empty list, change its value to None."""
        return warnings or None

    def _record_values(self, values, tags: Iterable[str] | str):
        """Serialize and store distributed quality report values for."""
        self.write(
            data=values, tags=tags, encoder=json_encoder, allow_nan=False, cls=QualityValueEncoder
        )

    @staticmethod
    def avg_noise(data) -> float:
        """Estimate the average noise in the image."""
        if len(data.shape) == 2:  # 2D data
            corner_square_length = int(data.shape[0] * 0.2)  # 1/5th of x dimension of array
            corner_square_height = int(data.shape[1] * 0.2)  # 1/5th of y dimension of array

            square_1 = data[0:corner_square_length, 0:corner_square_height]  # top left

            square_2 = data[-corner_square_length:, 0:corner_square_height]  # top right

            square_3 = data[0:corner_square_length, -corner_square_height:]  # bottom left

            square_4 = data[-corner_square_length:, -corner_square_height:]  # bottom right

            return np.nanmean(
                [
                    np.nanstd(square_1),
                    np.nanstd(square_2),
                    np.nanstd(square_3),
                    np.nanstd(square_4),
                ]
            )

        if len(data.shape) == 3:  # 3D data
            corner_cube_length = int(data.shape[0] * 0.2)  # 1/5th of x dimension of array
            corner_cube_height = int(data.shape[1] * 0.2)  # 1/5th of y dimension of array
            corner_cube_width = int(data.shape[2] * 0.2)  # 1/5th of z dimension of array

            cube_1 = data[
                0:corner_cube_length, 0:corner_cube_height, 0:corner_cube_width
            ]  # top left front

            cube_2 = data[
                0:corner_cube_length, 0:corner_cube_height, -corner_cube_width:
            ]  # top left back

            cube_3 = data[
                -corner_cube_length:, 0:corner_cube_height, 0:corner_cube_width
            ]  # top right front

            cube_4 = data[
                -corner_cube_length:, 0:corner_cube_height, -corner_cube_width:
            ]  # top right back

            cube_5 = data[
                0:corner_cube_length, -corner_cube_height:, 0:corner_cube_width
            ]  # bottom left front

            cube_6 = data[
                0:corner_cube_length, -corner_cube_height:, -corner_cube_width:
            ]  # bottom left back

            cube_7 = data[
                -corner_cube_length:, -corner_cube_height:, 0:corner_cube_width
            ]  # bottom right front

            cube_8 = data[
                -corner_cube_length:, -corner_cube_height:, -corner_cube_width:
            ]  # bottom right back

            return np.nanmean(
                [
                    np.nanstd(cube_1),
                    np.nanstd(cube_2),
                    np.nanstd(cube_3),
                    np.nanstd(cube_4),
                    np.nanstd(cube_5),
                    np.nanstd(cube_6),
                    np.nanstd(cube_7),
                    np.nanstd(cube_8),
                ]
            )
