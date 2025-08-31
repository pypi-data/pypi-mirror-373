"""Tests for the tasks.trial_catalog module."""

from pathlib import Path
from string import ascii_uppercase
from uuid import uuid4

import astropy.units as u
import pytest
from astropy.io import fits
from dkist_data_simulator.spec214.vbi import SimpleVBIDataset
from sqids import Sqids

from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.asdf import asdf_decoder
from dkist_processing_common.codecs.bytes import bytes_decoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.codecs.json import json_decoder
from dkist_processing_common.codecs.quality import quality_data_encoder
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks import CreateTrialAsdf
from dkist_processing_common.tasks import CreateTrialDatasetInventory
from dkist_processing_common.tasks import CreateTrialQualityReport


@pytest.fixture()
def scratch_with_l1_frames(recipe_run_id, tmp_path) -> WorkflowFileSystem:
    """Scratch instance for a recipe run id with tagged L1 frames."""
    scratch = WorkflowFileSystem(
        recipe_run_id=recipe_run_id,
        scratch_base_path=tmp_path,
    )
    level_1_frames = SimpleVBIDataset(
        n_time=10,
        time_delta=1,
        linewave=550 * u.nm,
        detector_shape=(10, 10),
    )
    for frame in level_1_frames:
        hdul = fits.HDUList(hdus=[fits.PrimaryHDU(), frame.hdu(rice_compress=True)])
        file_obj = fits_hdulist_encoder(hdul)
        scratch.write(
            file_obj, tags=[Tag.output(), Tag.frame()], relative_path=f"{uuid4().hex}.dat"
        )
    return scratch


@pytest.fixture()
def create_trial_dataset_inventory_task(
    recipe_run_id,
    tmp_path,
    scratch_with_l1_frames,
    fake_constants_db,
    mocker,
    fake_gql_client,
) -> CreateTrialDatasetInventory:
    """An instance of CreateTrialDatasetInventory with L1 frames tagged in scratch."""
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient",
        new=fake_gql_client,
    )
    task = CreateTrialDatasetInventory(
        recipe_run_id=recipe_run_id,
        workflow_name="trial_dataset_inventory",
        workflow_version="trial_dataset_inventory_version",
    )
    task.scratch = scratch_with_l1_frames
    task.constants._update(fake_constants_db)
    yield task
    task._purge()


@pytest.fixture()
def create_trial_asdf_task(
    recipe_run_id, tmp_path, scratch_with_l1_frames, fake_constants_db
) -> CreateTrialAsdf:
    """An instance of CreateTrialAsdf with L1 frames tagged in scratch."""
    task = CreateTrialAsdf(
        recipe_run_id=recipe_run_id,
        workflow_name="trial_asdf",
        workflow_version="trial_asdf_version",
    )
    task.scratch = scratch_with_l1_frames
    task.constants._update(fake_constants_db)
    yield task
    task._purge()


@pytest.fixture()
def create_trial_quality_report_task(
    recipe_run_id, tmp_path, fake_constants_db
) -> CreateTrialQualityReport:
    """An instance of CreateTrialQualityReport with tagged quality data."""
    task = CreateTrialQualityReport(
        recipe_run_id=recipe_run_id,
        workflow_name="trial_quality_report",
        workflow_version="trial_quality_report_version",
    )
    task.constants._update(fake_constants_db)

    quality_data_warning_only = [
        {
            "name": "Range checks",
            "description": "This metric is checking that certain input and calculated parameters"
            " fall within a valid data range. If no parameters are listed here,"
            " all pipeline parameters were measured to be in range",
            "metric_code": "RANGE",
            "statement": "This is a test quality report with no data",
            "plot_data": None,
            "histogram_data": None,
            "table_data": None,
            "modmat_data": None,
            "efficiency_data": None,
            "raincloud_data": None,
            "warnings": ["warning 1", "warning 2"],
        }
    ]

    task.write(
        quality_data_warning_only,
        tags=Tag.quality_data(),
        encoder=quality_data_encoder,
        relative_path=f"{task.constants.dataset_id}_quality_data.json",
    )

    yield task
    task._purge()


def test_create_trial_dataset_inventory(create_trial_dataset_inventory_task):
    """
    :Given: An instance of CreateTrialDatasetInventory with L1 frames tagged in scratch
    :When: CreateTrialDatasetInventory is run
    :Then: A json file containing dataset inventory is tagged in scratch
    """
    task = create_trial_dataset_inventory_task
    # When
    task()
    # Then
    results = list(task.read(tags=[Tag.output(), Tag.dataset_inventory()], decoder=json_decoder))
    assert len(results) == 1
    inventory = results[0]
    assert isinstance(inventory, dict)
    assert len(inventory) > 20  # a bunch


def test_create_trial_asdf(create_trial_asdf_task, recipe_run_id):
    """
    :Given: An instance of CreateTrialAsdf with L1 frames tagged in scratch
    :When: CreateTrialAsdf is run
    :Then: An asdf file for the dataset is tagged in scratch
    """
    task = create_trial_asdf_task
    # When
    task()
    # Then
    asdf_tags = [Tag.output(), Tag.asdf()]
    filepaths = list(task.scratch.find_all(tags=asdf_tags))
    assert len(filepaths) == 1
    dataset_id = Sqids(min_length=6, alphabet=ascii_uppercase).encode([recipe_run_id])
    assert filepaths[0].name == f"INSTRUMENT_L1_20240416T160000_{dataset_id}_metadata.asdf"
    results = list(task.read(tags=asdf_tags, decoder=asdf_decoder))
    assert len(results) == 1
    tree = results[0]
    assert isinstance(tree, dict)
    for file_name in tree["dataset"].files.filenames:
        # This is a slightly better than check that `not Path(file_name).is_absolute()` because it confirms
        # we've correctly stripped the path of *all* parents (not just those that start at root).
        # E.g., this allows us to test the difference between `scratch.scratch_base_path` and
        # `scratch.workflow_base_path`
        assert Path(file_name).name == file_name


def test_create_trial_quality_report(create_trial_quality_report_task):
    """
    :Given: An instance of CreateTrialQualityReport with tagged quality data
    :When: CreateTrialQualityReport is run
    :Then: A quality report pdf file gets created and tagged
    """
    task = create_trial_quality_report_task
    # When
    task()
    # Then
    paths = list(task.read(tags=[Tag.output(), Tag.quality_report()]))
    assert len(paths) == 1
    quality_report = next(
        task.read(tags=[Tag.output(), Tag.quality_report()], decoder=bytes_decoder)
    )
    assert isinstance(quality_report, bytes)
    assert b"%PDF" == quality_report[:4]
