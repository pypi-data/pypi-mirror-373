"""Tests for the quality tasks."""

import json
from typing import Iterable

import numpy as np
import pytest
from astropy.io import fits
from astropy.wcs import WCS
from dkist_data_simulator.spec122 import Spec122Dataset
from dkist_data_simulator.spec214 import Spec214Dataset

from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tasks.quality_metrics import QualityL0Metrics
from dkist_processing_common.tasks.quality_metrics import QualityL1Metrics


class BaseSpec214l0Dataset(Spec122Dataset):
    def __init__(self, instrument="vbi"):
        super().__init__(
            dataset_shape=(3, 10, 10),
            array_shape=(1, 10, 10),
            time_delta=1,
            instrument=instrument,
            file_schema="level0_spec214",
        )

    @property
    def data(self):
        return np.ones(shape=self.array_shape)


class BaseSpec214Dataset(Spec214Dataset):
    def __init__(self, instrument="vbi"):
        self.array_shape = (10, 10)
        super().__init__(
            dataset_shape=(2, 10, 10),
            array_shape=self.array_shape,
            time_delta=1,
            instrument=instrument,
        )

    @property
    def fits_wcs(self):
        w = WCS(naxis=2)
        w.wcs.crpix = self.array_shape[1] / 2, self.array_shape[0] / 2
        w.wcs.crval = 0, 0
        w.wcs.cdelt = 1, 1
        w.wcs.cunit = "arcsec", "arcsec"
        w.wcs.ctype = "HPLN-TAN", "HPLT-TAN"
        w.wcs.pc = np.identity(self.array_ndim)
        return w


@pytest.fixture(scope="session")
def task_type_options() -> list[str]:
    # note that the length of this list and the dataset size affect how many occurrences there are
    return [
        TaskName.observe.value,
        TaskName.dark.value,
        TaskName.gain.value,
        TaskName.solar_gain.value,
    ]


@pytest.fixture(params=[TaskName.dark.value, TaskName.gain.value])
def quality_task_type(request) -> list[str]:
    # note that the length of this list and the dataset size affect how many occurrences there are
    return request.param


@pytest.fixture
def base_spec_214_l0_dataset_factory():
    def factory(task_types) -> list[fits.HDUList]:
        hduls = []
        for ds in BaseSpec214l0Dataset():
            hdu = ds.hdu()
            # overwritten here because you can't add an IPTASK @key_function to the dataset
            task_type_index = ds.index % len(task_types)
            hdu.header["IPTASK"] = task_types[task_type_index]
            hduls.append(fits.HDUList([hdu]))
        return hduls

    return factory


@pytest.fixture(
    params=[pytest.param([None], id="No_modstates"), pytest.param(range(1, 4), id="With_modstates")]
)
def modstate_option(request):
    return request.param


@pytest.fixture
def quality_l0_task_class(modstate_option):
    class QualityL0Task(QualityL0Metrics):
        @property
        def modstate_list(self) -> Iterable[int] | None:
            return modstate_option

    return QualityL0Task


@pytest.fixture
def quality_l0_task(recipe_run_id, tmp_path, quality_l0_task_class):
    with quality_l0_task_class(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        yield task
        task._purge()


@pytest.fixture
def quality_l0_task_with_quality_task_types(
    quality_l0_task, task_type_options, modstate_option, base_spec_214_l0_dataset_factory
):
    hduls = base_spec_214_l0_dataset_factory(task_type_options)
    for t in task_type_options:
        for m in modstate_option:
            tags = [Tag.input(), Tag.task(t)]
            if m is not None:
                tags.append(Tag.modstate(m))
            for hdul in hduls:
                quality_l0_task.write(data=hdul, tags=tags, encoder=fits_hdulist_encoder)

    return quality_l0_task


@pytest.fixture
def quality_l0_task_without_quality_task_types(
    quality_l0_task,
    request,
    recipe_run_id,
    task_type_options,
    base_spec_214_l0_dataset_factory,
    quality_task_type,
):
    task_types = [t for t in task_type_options if t != quality_task_type]
    hduls = base_spec_214_l0_dataset_factory(task_types)
    [
        quality_l0_task.write(
            data=hdul, tags=[Tag.input(), Tag.task(t)], encoder=fits_hdulist_encoder
        )
        for hdul in hduls
        for t in task_types
    ]
    return quality_l0_task


@pytest.mark.parametrize("metric_name", ["FRAME_RMS", "FRAME_AVERAGE"])
def test_l0_quality_metrics(
    quality_l0_task_with_quality_task_types, metric_name, quality_task_type, modstate_option
):
    """
    Given: a task with the QualityL0Metrics class
    When: checking that the task metric combination was created and stored correctly
    Then: the metric is encoded as a json object, which when opened contains a dictionary with the
      expected schema
    """
    # call task and assert that things were created (tagged files on disk with quality metric info in them)
    task = quality_l0_task_with_quality_task_types
    task()
    for modstate in modstate_option:
        tags = [Tag.quality(metric_name), Tag.quality_task(quality_task_type)]
        if modstate is not None:
            tags.append(Tag.modstate(modstate))
        files = list(task.read(tags=tags))
        assert files  # there are some
        for file in files:
            with file.open() as f:
                data = json.load(f)
                assert isinstance(data, dict)
                assert data["x_values"]
                assert data["y_values"]
                assert all(isinstance(item, str) for item in data["x_values"])
                assert all(isinstance(item, float) for item in data["y_values"])
                assert len(data["x_values"]) == len(data["y_values"])


@pytest.mark.parametrize("metric_name", ["FRAME_RMS", "FRAME_AVERAGE"])
def test_l0_quality_metrics_missing_quality_task_types(
    quality_l0_task_without_quality_task_types, metric_name, quality_task_type
):
    """
    Given: a task with the QualityL0Metrics class
    When: checking that the task metric combination was created and stored correctly
    Then: the metric is encoded as a json object, which when opened contains a dictionary with the
      expected schema
    """
    task = quality_l0_task_without_quality_task_types
    task()
    files = list(task.read(tags=[Tag.quality(metric_name), Tag.quality_task(quality_task_type)]))
    assert not files  # there are none


@pytest.fixture
def quality_L1_task(tmp_path, recipe_run_id):
    with QualityL1Metrics(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        for i in range(10):
            header_dict = [
                d.header(required_only=False, expected_only=False) for d in BaseSpec214Dataset()
            ][0]
            data = np.ones(shape=BaseSpec214Dataset().array_shape)
            hdu = fits.PrimaryHDU(data=data, header=fits.Header(header_dict))
            hdul = fits.HDUList([hdu])
            task.write(
                data=hdul, tags=[Tag.calibrated(), Tag.frame()], encoder=fits_hdulist_encoder
            )
        yield task
    task._purge()


def test_fried_parameter(quality_L1_task):
    """
    Given: a task with the QualityL1Metrics class
    When: checking that the fried parameter metric was created and stored correctly
    Then: the metric is encoded as a json object, which when opened contains a dictionary with the expected schema
    """
    task = quality_L1_task
    task()
    files = list(task.read(tags=Tag.quality("FRIED_PARAMETER")))
    assert files
    for file in files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert all(isinstance(item, str) for item in data["x_values"])
            assert all(isinstance(item, float) for item in data["y_values"])
            # assert data["task_type"] == "observe"


def test_light_level(quality_L1_task):
    """
    Given: a task with the QualityL1Metrics class
    When: checking that the light level metric was created and stored correctly
    Then: the metric is encoded as a json object, which when opened contains a dictionary with the expected schema
    """
    task = quality_L1_task
    task()
    files = list(task.read(tags=Tag.quality("LIGHT_LEVEL")))
    assert files
    for file in files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert all(isinstance(item, str) for item in data["x_values"])
            assert all(isinstance(item, float) for item in data["y_values"])
            # assert data["task_type"] == "observe"


def test_health_status(quality_L1_task):
    """
    Given: a task with the QualityL1Metrics class
    When: checking that the health status metric was created and stored correctly
    Then: the metric is encoded as a json object, which when opened contains a dictionary with the expected schema
    """
    task = quality_L1_task
    task()
    files = list(task.read(tags=Tag.quality("HEALTH_STATUS")))
    assert files
    for file in files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, list)


def test_ao_status(quality_L1_task):
    """
    Given: a task with the QualityL1Metrics class
    When: checking that the AO status metric was created and stored correctly
    Then: the metric is encoded as a json object, which when opened contains a dictionary with the expected schema
    """
    task = quality_L1_task
    task()
    files = list(task.read(tags=Tag.quality("AO_STATUS")))
    assert files
    for file in files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, list)
            assert all(isinstance(item, bool) for item in data)
