from dataclasses import asdict
from dataclasses import dataclass
from typing import Literal
from unittest.mock import Mock

import astropy.units as u
import numpy as np
import pytest
from astropy.coordinates import EarthLocation
from astropy.io import fits
from astropy.time import Time
from astropy.time import TimeDelta
from dkist_fits_specifications import __version__ as spec_version
from dkist_header_validator import spec214_validator

from dkist_processing_common import __version__ as common_version
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_hdu_decoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.models.graphql import RecipeRunProvenanceResponse
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.models.wavelength import WavelengthRange
from dkist_processing_common.tasks.write_l1 import WriteL1Frame
from dkist_processing_common.tests.mock_metadata_store import TILE_SIZE
from dkist_processing_common.tests.mock_metadata_store import InputDatasetRecipeRunResponseMapping
from dkist_processing_common.tests.mock_metadata_store import RecipeRunResponseMapping
from dkist_processing_common.tests.mock_metadata_store import fake_gql_client_factory
from dkist_processing_common.tests.mock_metadata_store import (
    make_default_input_dataset_recipe_run_response,
)
from dkist_processing_common.tests.mock_metadata_store import make_default_recipe_run_response


@pytest.fixture
def fake_gql_client_default_configuration():
    """Create GraphQL client Mock that returns result without recipe run configuration."""
    recipe_run_response = make_default_recipe_run_response()
    recipe_run_response.configuration = None
    new_response_mapping = RecipeRunResponseMapping(response=recipe_run_response)
    FakeGQLClientDefaultConfiguration = fake_gql_client_factory(
        response_mapping_override=new_response_mapping
    )

    return FakeGQLClientDefaultConfiguration


@pytest.fixture
def fake_gql_client_missing_calibration_part():
    """Create GraphQL client Mock that returns result without calibration part."""
    input_dataset_recipe_run_response = make_default_input_dataset_recipe_run_response()
    dataset_parts = (
        input_dataset_recipe_run_response.recipeInstance.inputDataset.inputDatasetInputDatasetParts
    )
    for index, part in enumerate(dataset_parts):
        if (
            part.inputDatasetPart.inputDatasetPartType.inputDatasetPartTypeName
            == "calibration_frames"
        ):
            del dataset_parts[index]
    new_response_mapping = InputDatasetRecipeRunResponseMapping(
        response=input_dataset_recipe_run_response
    )
    FakeGQLClientMissingInputDatasetCalibrationPart = fake_gql_client_factory(
        response_mapping_override=new_response_mapping
    )

    return FakeGQLClientMissingInputDatasetCalibrationPart


@pytest.fixture()
def make_fake_gql_client_with_provenance():
    """Create GraphQL client Mocks that will return customizable provenance records."""

    def class_generator(provenances: list[RecipeRunProvenanceResponse]):
        recipe_run_response = make_default_recipe_run_response()
        recipe_run_response.recipeRunProvenances = provenances
        new_response_mapping = RecipeRunResponseMapping(response=recipe_run_response)
        FakeGQLClientProvenances = fake_gql_client_factory(
            response_mapping_override=new_response_mapping
        )

        return FakeGQLClientProvenances

    return class_generator


class CompleteWriteL1Frame(WriteL1Frame):
    def add_dataset_headers(
        self, header: fits.Header, stokes: Literal["I", "Q", "U", "V"]
    ) -> fits.Header:
        # Because all these keys aren't part of SPEC-122
        header["DAAXES"] = 2
        header["DEAXES"] = 3
        header["DNAXIS"] = 5
        header["FRAMEWAV"] = 123.45
        header["LEVEL"] = 1
        header["WAVEREF"] = "Air"
        header["WAVEUNIT"] = -9
        header["DINDEX3"] = 3
        header["DINDEX4"] = 2
        header["DINDEX5"] = 1
        header["DNAXIS1"] = header["NAXIS1"]
        header["DNAXIS2"] = header["NAXIS2"]
        header["DNAXIS3"] = 10
        header["DNAXIS4"] = 1
        header["DNAXIS5"] = 4
        header["DPNAME1"] = ""
        header["DPNAME2"] = ""
        header["DPNAME3"] = ""
        header["DPNAME4"] = ""
        header["DPNAME5"] = ""
        header["DTYPE1"] = "SPATIAL"
        header["DTYPE2"] = "SPATIAL"
        header["DTYPE3"] = "TEMPORAL"
        header["DTYPE4"] = "SPECTRAL"
        header["DTYPE5"] = "STOKES"
        header["DUNIT1"] = ""
        header["DUNIT2"] = ""
        header["DUNIT3"] = ""
        header["DUNIT4"] = ""
        header["DUNIT5"] = ""
        header["DWNAME1"] = ""
        header["DWNAME2"] = ""
        header["DWNAME3"] = ""
        header["DWNAME4"] = ""
        header["DWNAME5"] = ""
        header["NBIN"] = 1
        for i in range(1, header["NAXIS"] + 1):
            header[f"NBIN{i}"] = 1

        header["VSPNMAPS"] = 1
        header["VSPMAP"] = 1
        header["POL_NOIS"] = 1.0
        header["POL_SENS"] = 1.0

        return header

    def calculate_date_end(self, header: fits.Header) -> str:
        start_time = Time(header["DATE-BEG"], format="isot", precision=6)
        exposure = TimeDelta(float(header["TEXPOSUR"]) / 1000, format="sec")
        return (start_time + exposure).to_value("isot")

    def get_wavelength_range(self, header: fits.Header) -> WavelengthRange:
        return WavelengthRange(min=1075.0 * u.nm, max=1085.0 * u.nm)


class CompleteWriteL1FrameWithEmptyWaveband(CompleteWriteL1Frame):
    def get_wavelength_range(self, header: fits.Header) -> WavelengthRange:
        # Return an empty range to test the empty waveband case
        return WavelengthRange(min=10000.0 * u.nm, max=10050.0 * u.nm)


@dataclass
class FakeConstantDb:
    INSTRUMENT: str = "TEST"
    DATASET_ID: str = "DATASETID"
    AVERAGE_CADENCE: float = 10.0
    MINIMUM_CADENCE: float = 10.0
    MAXIMUM_CADENCE: float = 10.0
    VARIANCE_CADENCE: float = 0.0
    STOKES_PARAMS: tuple = ("I", "Q", "U", "V")
    PROPOSAL_ID: str = ("PROPID1",)
    CONTRIBUTING_PROPOSAL_IDS: tuple = (("PROPID1"),)
    EXPERIMENT_ID: str = ("EXPERID1",)
    CONTRIBUTING_EXPERIMENT_IDS: tuple = ("EXPERID1", "EXPERID2", "EXPERID3")


@pytest.fixture(
    scope="function",
    params=[
        pytest.param((1, "complete_common_header"), id="Intensity"),
        pytest.param((4, "complete_polarimetric_header"), id="Polarimetric"),
    ],
)
def write_l1_task(request, recipe_run_id, tmp_path):
    with CompleteWriteL1Frame(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(recipe_run_id=recipe_run_id, scratch_base_path=tmp_path)
        num_of_stokes_params, header_fixture_name = request.param
        header = request.getfixturevalue(header_fixture_name)
        stokes_params = ["I", "Q", "U", "V"]
        used_stokes_params = []
        hdu = fits.PrimaryHDU(data=np.random.random(size=(1, 128, 128)) * 10, header=header)
        hdu.header["IPTASK"] = "level0_only key to be removed"
        hdul = fits.HDUList([hdu])
        for i in range(num_of_stokes_params):
            task.write(
                data=hdul,
                tags=[
                    Tag.calibrated(),
                    Tag.frame(),
                    Tag.stokes(stokes_params[i]),
                    Tag.dsps_repeat(i),
                ],
                encoder=fits_hdulist_encoder,
            )
            used_stokes_params.append(stokes_params[i])
        task.constants._update(asdict(FakeConstantDb()))
        yield task, used_stokes_params, header
        task._purge()


@pytest.fixture(
    scope="function",
    params=[
        pytest.param((1, "complete_common_header"), id="Intensity"),
        pytest.param((4, "complete_polarimetric_header"), id="Polarimetric"),
    ],
)
def write_l1_task_with_empty_waveband(recipe_run_id, tmp_path, request):
    with CompleteWriteL1FrameWithEmptyWaveband(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(recipe_run_id=recipe_run_id, scratch_base_path=tmp_path)
        num_of_stokes_params, header_fixture_name = request.param
        header = request.getfixturevalue(header_fixture_name)
        stokes_params = ["I", "Q", "U", "V"]
        used_stokes_params = []
        hdu = fits.PrimaryHDU(data=np.random.random(size=(1, 128, 128)) * 10, header=header)
        hdu.header["IPTASK"] = "level0_only key to be removed"
        hdul = fits.HDUList([hdu])
        for i in range(num_of_stokes_params):
            task.write(
                data=hdul,
                tags=[
                    Tag.calibrated(),
                    Tag.frame(),
                    Tag.stokes(stokes_params[i]),
                    Tag.dsps_repeat(i),
                ],
                encoder=fits_hdulist_encoder,
            )
            used_stokes_params.append(stokes_params[i])
        task.constants._update(asdict(FakeConstantDb()))
        yield task, used_stokes_params, header
        task._purge()


@pytest.fixture(
    scope="function",
    params=[
        pytest.param(
            {"AO_LOCK": True, "ATMOS_R0": 0.2, "OOBSHIFT": 17}, id="AO_LOCK_True_good_R0_good_oob"
        ),
        pytest.param(
            {"AO_LOCK": True, "ATMOS_R0": 1, "OOBSHIFT": 17}, id="AO_LOCK_True_bad_R0_good_oob"
        ),
        pytest.param(
            {"AO_LOCK": False, "ATMOS_R0": 0.2, "OOBSHIFT": 17}, id="AO_LOCK_False_good_R0_good_oob"
        ),
        pytest.param(
            {"AO_LOCK": False, "ATMOS_R0": 1, "OOBSHIFT": 17}, id="AO_LOCK_False_bad_R0_good_oob"
        ),
        pytest.param(
            {"AO_LOCK": True, "ATMOS_R0": 0.2, "OOBSHIFT": 150}, id="AO_LOCK_True_good_R0_bad_oob"
        ),
        pytest.param(
            {"AO_LOCK": True, "ATMOS_R0": 1, "OOBSHIFT": 150}, id="AO_LOCK_True_bad_R0_bad_oob"
        ),
        pytest.param(
            {"AO_LOCK": False, "ATMOS_R0": 0.2, "OOBSHIFT": 150}, id="AO_LOCK_False_good_R0_bad_oob"
        ),
        pytest.param(
            {"AO_LOCK": False, "ATMOS_R0": 1, "OOBSHIFT": 150}, id="AO_LOCK_False_bad_R0_bad_oob"
        ),
        pytest.param({"ATMOS_R0": 0.2, "OOBSHIFT": 17}, id="AO_LOCK_missing"),
        pytest.param({"ATMOS_R0": 0.2, "AO_LOCK": True}, id="OOBSHIFT_missing"),
    ],
)
def write_l1_task_no_data(request, recipe_run_id, tmp_path, complete_common_header):
    with CompleteWriteL1Frame(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(recipe_run_id=recipe_run_id, scratch_base_path=tmp_path)
        header = complete_common_header
        header.pop("AO_LOCK", None)
        header.pop("ATMOS_R0", None)
        header.pop("OOBSHIFT", None)
        header.update(request.param)
        hdu = fits.PrimaryHDU(data=np.random.random(size=(1, 1, 1)) * 1, header=header)
        hdul = fits.HDUList([hdu])
        task.write(
            data=hdul,
            tags=[
                Tag.calibrated(),
                Tag.frame(),
            ],
            encoder=fits_hdulist_encoder,
        )
        task.constants._update(asdict(FakeConstantDb()))
        fried_parameter = request.param["ATMOS_R0"]
        oob_shift = request.param.get("OOBSHIFT")
        yield task, header, fried_parameter, oob_shift
        task._purge()


@pytest.mark.parametrize(
    "provenances, is_manual",
    [
        pytest.param(
            [RecipeRunProvenanceResponse(recipeRunProvenanceId=1, isTaskManual=False)],
            False,
            id="auto_single",
        ),
        pytest.param(
            [
                RecipeRunProvenanceResponse(recipeRunProvenanceId=1, isTaskManual=False),
                RecipeRunProvenanceResponse(recipeRunProvenanceId=2, isTaskManual=False),
            ],
            False,
            id="auto_multiple",
        ),
        pytest.param(
            [RecipeRunProvenanceResponse(recipeRunProvenanceId=1, isTaskManual=True)],
            True,
            id="manual_single",
        ),
        pytest.param(
            [
                RecipeRunProvenanceResponse(recipeRunProvenanceId=1, isTaskManual=False),
                RecipeRunProvenanceResponse(recipeRunProvenanceId=2, isTaskManual=True),
            ],
            True,
            id="manual_multiple",
        ),
    ],
)
def test_write_l1_frame(
    write_l1_task,
    mocker,
    make_fake_gql_client_with_provenance,
    provenances: list[RecipeRunProvenanceResponse],
    is_manual,
):
    """
    :Given: a write L1 task
    :When: running the task
    :Then: no errors are raised and the MANPROC and FRAMEVOL headers are correct
    """
    WriteL1GQLClient = make_fake_gql_client_with_provenance(provenances=provenances)

    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=WriteL1GQLClient
    )
    mocker.patch(
        "dkist_processing_common.tasks.write_l1.WriteL1Frame.version_from_module_name",
        new_callable=Mock,
        return_value="fake_version_number",
    )

    task, used_stokes_params, _ = write_l1_task
    task()
    for stokes_param in used_stokes_params:
        files = list(task.read(tags=[Tag.frame(), Tag.output(), Tag.stokes(stokes_param)]))
        assert len(files) == 1
        for file in files:
            assert file.exists
            spec214_validator.validate(file, extra=False)
            hdu = fits_hdu_decoder(file)
            assert hdu.header["MANPROCD"] == is_manual

            # Test that FRAMEVOL is within 3% of the actual, on-disk size
            on_disk_size_mb = file.stat().st_size / 1024 / 1024
            np.testing.assert_allclose(hdu.header["FRAMEVOL"], on_disk_size_mb, rtol=0.03)

            # Test that FRAMEVOL still has its comment
            assert hdu.header.comments["FRAMEVOL"]

            # Test that 'level0_only' keys are being removed
            assert "IPTASK" not in hdu.header.keys()


def test_replace_header_values(write_l1_task):
    """
    :Given: an input header
    :When: replacing specific header values
    :Then: the header values have changed
    """
    task, _, header = write_l1_task
    original_file_id = header["FILE_ID"]
    original_date = header["DATE"]
    data = np.ones(shape=(1, 1))
    header = task.replace_header_values(header=header, data=data)
    assert header["FILE_ID"] != original_file_id
    assert header["DATE"] != original_date
    assert header["NAXIS"] == len(data.shape)
    assert header["DATE-END"] == "2020-01-02T00:00:00.100000"


def test_l1_filename(write_l1_task):
    """
    :Given: an input header
    :When: asking for the corresponding L1 filename
    :Then: the filename is formatted as expected
    """
    task, _, header = write_l1_task
    assert (
        task.l1_filename(header=header, stokes="Q")
        == f"VISP_2020_01_02T00_00_00_000000_01080000_Q_{task.constants.dataset_id}_L1.fits"
    )


def test_calculate_date_avg(write_l1_task):
    """
    :Given: an input header
    :When: finding the average date
    :Then: the correct datetime string is returned
    """
    task, _, header = write_l1_task
    assert task.calculate_date_avg(header=header) == "2020-01-02T12:00:00.000000"


def test_calculate_telapse(write_l1_task):
    """
    :Given: an input header
    :When: finding the time elapsed in an observation
    :Then: the correct time value is returned
    """
    task, _, header = write_l1_task
    assert task.calculate_telapse(header=header) == 86400


def test_solarnet_keys(write_l1_task, mocker, fake_gql_client):
    """
    :Given: files with headers converted to SPEC 214 L1
    :When: checking the solarnet extra headers
    :Then: the correct values are found
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    mocker.patch(
        "dkist_processing_common.tasks.write_l1.WriteL1Frame.version_from_module_name",
        new_callable=Mock,
        return_value="fake_version_number",
    )

    task, _, _ = write_l1_task
    task()
    files = list(task.read(tags=[Tag.frame(), Tag.output()]))
    for file in files:
        header = fits.open(file)[1].header
        assert header["DATEREF"] == header["DATE-BEG"]
        assert round(header["OBSGEO-X"]) == -5466045
        assert round(header["OBSGEO-Y"]) == -2404389
        assert round(header["OBSGEO-Z"]) == 2242134
        assert header["SOLARRAD"] == 975.58
        assert header["SPECSYS"] == "TOPOCENT"
        assert header["VELOSYS"] == 0.0
        assert header["WAVEBAND"] == "Fe XIII (1079.8 nm)"
        assert header["WAVEMIN"] == 1075.0
        assert header["WAVEMAX"] == 1085.0


def test_documentation_keys(write_l1_task, mocker, fake_gql_client):
    """
    :Given: files with headers converted to SPEC 214 L1
    :When: checking the documentation header URLs
    :Then: the correct values are found
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    mocker.patch(
        "dkist_processing_common.tasks.write_l1.WriteL1Frame.version_from_module_name",
        new_callable=Mock,
        return_value="fake_version_number",
    )

    task, _, _ = write_l1_task
    task()
    files = list(task.read(tags=[Tag.frame(), Tag.output()]))
    for file in files:
        header = fits.open(file)[1].header
        assert header["INFO_URL"] == task.docs_base_url
        assert header["HEADVERS"] == spec_version
        assert (
            header["HEAD_URL"] == f"{task.docs_base_url}/projects/data-products/en/v{spec_version}"
        )
        calvers = task.version_from_module_name()
        assert header["CALVERS"] == calvers
        assert (
            header["CAL_URL"]
            == f"{task.docs_base_url}/projects/{task.constants.instrument.lower()}/en/v{calvers}/{task.workflow_name}.html"
        )


def test_get_version_from_module(write_l1_task):
    task, _, _ = write_l1_task
    assert task.version_from_module_name() == common_version


def test_get_tile_size(write_l1_task, mocker, fake_gql_client):
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task, _, _ = write_l1_task
    test_array = np.zeros((1, TILE_SIZE // 2, TILE_SIZE * 2))
    tile_size = task.compute_tile_size_for_array(test_array)
    assert tile_size == [1, TILE_SIZE // 2, TILE_SIZE]


def test_rice_compression_with_specified_tile_size(write_l1_task, mocker, fake_gql_client):
    """
    :Given: a write_L1 task with a specified tile size in the recipe configuration
    :When: running the task
    :Then: data is written with the compression tile size specified in the recipe configuration
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task, _, _ = write_l1_task
    task()
    files = list(task.read(tags=[Tag.frame(), Tag.output()]))
    for file in files:
        hdul = fits.open(file)
        bintable = hdul[1]._get_bintable_without_data()
        comp_header = bintable.header
        data_shape = list(hdul[1].data.shape)
        data_shape.reverse()
        for i, dim in enumerate(data_shape):
            assert comp_header["ZTILE" + str(i + 1)] == min(dim, TILE_SIZE)


def test_rice_compression_with_default_tile_size(
    write_l1_task, mocker, fake_gql_client_default_configuration
):
    """
    :Given: a write_L1 task with no specified tile size in the recipe configuration
    :When: running the task
    :Then: data is written with astropy's default compression tile size

    Each tile size should be the length of the axis or 1 due to how astropy chooses default tiles.
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient",
        new=fake_gql_client_default_configuration,
    )
    task, _, _ = write_l1_task
    task()
    assert task.tile_size_param == None
    files = list(task.read(tags=[Tag.frame(), Tag.output()]))
    for file in files:
        hdul = fits.open(file)
        bintable = hdul[1]._get_bintable_without_data()
        comp_header = bintable.header
        data_shape = list(hdul[1].data.shape)
        data_shape.reverse()
        assert comp_header["ZTILE1"] == data_shape[0]
        assert comp_header["ZTILE2"] == 1
        assert comp_header["ZTILE3"] == 1


def test_reprocessing_keys(write_l1_task, mocker, fake_gql_client):
    """
    :Given: a write_L1 task with reprocessing keys present
    :When: running the task
    :Then: the reprocessing keys are correctly written
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient",
        new=fake_gql_client,
    )
    task, _, _ = write_l1_task
    task()
    files = list(task.read(tags=[Tag.frame(), Tag.output()]))
    for file in files:
        header = fits.open(file)[1].header
        assert header["IDSPARID"] == task.metadata_store_input_dataset_parameters.inputDatasetPartId
        assert (
            header["IDSOBSID"]
            == task.metadata_store_input_dataset_observe_frames.inputDatasetPartId
        )
        assert (
            header["IDSCALID"]
            == task.metadata_store_input_dataset_calibration_frames.inputDatasetPartId
        )
        assert header["WKFLNAME"] == task.workflow_name
        assert header["WKFLVERS"] == task.workflow_version
        assert header["PROCTYPE"] == "L1"
        assert header["PRODUCT"] == task.compute_product_id(header["IDSOBSID"], header["PROCTYPE"])


def test_missing_input_dataset_part(
    write_l1_task, mocker, fake_gql_client_missing_calibration_part
):
    """
    :Given: a Write_L1 task with a missing calibration frames part
    :When: running the task
    :Then: the input dataset part keys are correctly written without throwing an exception
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient",
        new=fake_gql_client_missing_calibration_part,
    )
    task, _, _ = write_l1_task
    task()
    files = list(task.read(tags=[Tag.frame(), Tag.output()]))
    for file in files:
        header = fits.open(file)[1].header
        assert header["IDSPARID"] == task.metadata_store_input_dataset_parameters.inputDatasetPartId
        assert (
            header["IDSOBSID"]
            == task.metadata_store_input_dataset_observe_frames.inputDatasetPartId
        )
        assert "IDSCALID" not in header


@pytest.mark.parametrize(
    "ids_obs_id, proc_type",
    [
        pytest.param(42, "alpha", id="42"),
        pytest.param(1_000, "beta", id="thousand"),
        pytest.param(1_000_000, "gamma", id="million"),
    ],
)
def test_product_id_calculation(ids_obs_id: int, proc_type: str):
    """
    Given: integer IDSOBSID and string PROCTYPE
    When: calculating the productId
    Then: the productId is computed properly
    """
    product_id = WriteL1Frame.compute_product_id(ids_obs_id, proc_type)
    assert isinstance(product_id, str)
    assert product_id.startswith(f"{proc_type}-")
    assert len(product_id) >= len(proc_type) + 6
    # same result the second time around
    assert product_id == WriteL1Frame.compute_product_id(ids_obs_id, proc_type)


def test_calculate_date_end(write_l1_task):
    """
    :Given: a write_L1 task with the DATE-END keyword
    :When: running the task
    :Then: the DATE-END keyword is inserted as expected
    """
    task, _, header = write_l1_task
    assert task.calculate_date_end(header=header) == "2020-01-02T00:00:00.100000"


def test_add_contributing_id_headers(write_l1_task):
    """
    :Given: a header and proposal id / experiment id constants
    :When: adding ids to the headers
    :Then: the correct ids are added
    """
    task, _, header = write_l1_task
    header = task.add_contributing_id_headers(header=header)
    # Ensure there is one contributing proposal ID
    assert header["PROPID01"] == "PROPID1"
    # Ensure that there are contributing experiment IDs
    assert header["EXPRID01"] == "EXPERID1"
    assert header["EXPRID02"] == "EXPERID2"
    assert header["EXPRID03"] == "EXPERID3"
    # Check total numbers
    assert header["NPROPOS"] == 1
    assert header["NEXPERS"] == 3


def test_spectral_line_keys(write_l1_task, mocker, fake_gql_client):
    """
    :Given: a header
    :When: adding spectral line information to the headers
    :Then: the correct values are added
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient",
        new=fake_gql_client,
    )
    task, _, header = write_l1_task
    header = task.add_spectral_line_headers(header=header)
    assert header["SPECLN01"] == "Fe XIII (1079.8 nm)"
    assert header["SPECLN02"] == "He I (1083.0 nm)"
    assert header["NSPECLNS"] == 2
    with pytest.raises(KeyError):
        assert header["SPECLN03"]


def test_check_r0_ao_lock(write_l1_task_no_data):
    """
    :Given: a header
    :When: writing, check if the AO lock is on
    :Then: write the r0 value if AO lock on, don't write if AO lock off
    """
    task, header, r0, _ = write_l1_task_no_data
    header_after_check = task.remove_invalid_r0_values(header=header)
    if header.get("AO_LOCK"):
        assert header_after_check["ATMOS_R0"] == header["ATMOS_R0"]
        assert header["ATMOS_R0"] == r0
        assert header["AO_LOCK"]
    else:
        with pytest.raises(KeyError, match="Keyword 'ATMOS_R0' not found"):
            invalid_r0 = header_after_check["ATMOS_R0"]
        assert header.get("AO_LOCK") != True


@pytest.mark.parametrize(
    "wavelength, wavemin, wavemax, expected",
    [
        pytest.param(
            617,
            615,
            619,
            "Fe I (617.33 nm)",
            id="line_is_between_wavemin_and_wavemax_and_exists",
        ),
        pytest.param(
            700,
            698,
            702,
            None,
            id="line_is_between_wavemin_and_wavemax_and_does_not_exist",
        ),
        pytest.param(
            617,
            698,
            702,
            None,
            id="line_is_not_between_wavemin_and_wavemax_and_exists",
        ),
    ],
)
def test_get_waveband(write_l1_task, wavelength, wavemin, wavemax, expected):
    """
    :Given: an input wavelength contribution
    :When: determining the waveband
    :Then: the correct waveband is returned
    """
    wavelength_range = WavelengthRange(min=wavemin * u.nm, max=wavemax * u.nm)
    task, _, _ = write_l1_task
    waveband = task.get_waveband(wavelength=wavelength * u.nm, wavelength_range=wavelength_range)
    assert waveband == expected


def test_empty_waveband(write_l1_task_with_empty_waveband, mocker, fake_gql_client):
    """
    :Given: a header converted to SPEC 214 L1 and a wavelength range that has no listed spectral lines
    :When: checking the waveband key
    :Then: it does not exist
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    mocker.patch(
        "dkist_processing_common.tasks.write_l1.WriteL1Frame.version_from_module_name",
        new_callable=Mock,
        return_value="fake_version_number",
    )

    task, _, _ = write_l1_task_with_empty_waveband
    task()
    files = list(task.read(tags=[Tag.frame(), Tag.output()]))
    for file in files:
        header = fits.open(file)[1].header
        assert header["WAVEMIN"] == 10000
        assert header["WAVEMAX"] == 10050
        with pytest.raises(KeyError):
            header["WAVEBAND"]
