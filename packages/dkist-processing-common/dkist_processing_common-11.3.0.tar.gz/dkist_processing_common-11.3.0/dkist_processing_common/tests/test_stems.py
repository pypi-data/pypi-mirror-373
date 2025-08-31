from itertools import chain

import pytest
from astropy.io import fits

from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.fits_access import FitsAccessBase
from dkist_processing_common.models.tags import StemName
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.parsers.cs_step import CSStepFlower
from dkist_processing_common.parsers.cs_step import NumCSStepBud
from dkist_processing_common.parsers.dsps_repeat import DspsRepeatNumberFlower
from dkist_processing_common.parsers.dsps_repeat import TotalDspsRepeatsBud
from dkist_processing_common.parsers.experiment_id_bud import ContributingExperimentIdsBud
from dkist_processing_common.parsers.experiment_id_bud import ExperimentIdBud
from dkist_processing_common.parsers.near_bud import NearFloatBud
from dkist_processing_common.parsers.near_bud import TaskNearFloatBud
from dkist_processing_common.parsers.proposal_id_bud import ContributingProposalIdsBud
from dkist_processing_common.parsers.proposal_id_bud import ProposalIdBud
from dkist_processing_common.parsers.retarder import RetarderNameBud
from dkist_processing_common.parsers.single_value_single_key_flower import (
    SingleValueSingleKeyFlower,
)
from dkist_processing_common.parsers.task import PolcalTaskFlower
from dkist_processing_common.parsers.task import TaskTypeFlower
from dkist_processing_common.parsers.task import parse_header_ip_task_with_gains
from dkist_processing_common.parsers.time import AverageCadenceBud
from dkist_processing_common.parsers.time import ExposureTimeFlower
from dkist_processing_common.parsers.time import MaximumCadenceBud
from dkist_processing_common.parsers.time import MinimumCadenceBud
from dkist_processing_common.parsers.time import ObsIpStartTimeBud
from dkist_processing_common.parsers.time import ReadoutExpTimeFlower
from dkist_processing_common.parsers.time import TaskExposureTimesBud
from dkist_processing_common.parsers.time import TaskReadoutExpTimesBud
from dkist_processing_common.parsers.time import TaskTimeBudBase
from dkist_processing_common.parsers.time import VarianceCadenceBud
from dkist_processing_common.parsers.unique_bud import TaskUniqueBud
from dkist_processing_common.parsers.unique_bud import UniqueBud
from dkist_processing_common.parsers.wavelength import ObserveWavelengthBud


class FitsReader(FitsAccessBase):
    def __init__(self, hdu, name):
        super().__init__(hdu, name)
        self.thing_id: int = self.header.get("id_key")
        self.constant_thing: float = self.header.get("constant")
        self.near_thing: float = self.header.get("near")
        self.name = name
        self.proposal_id: str = self.header.get("ID___013")
        self.experiment_id: str = self.header.get("ID___012")
        self.ip_task_type: str = self.header.get("DKIST004")
        self.ip_start_time: str = self.header.get("DKIST011")
        self.fpa_exposure_time_ms: float = self.header.get("XPOSURE")
        self.sensor_readout_exposure_time_ms: float = self.header.get("TEXPOSUR")
        self.num_raw_frames_per_fpa: int = self.header.get("NSUMEXP")
        self.num_dsps_repeats: int = self.header.get("DSPSREPS")
        self.current_dsps_repeat: int = self.header.get("DSPSNUM")
        self.time_obs: str = self.header.get("DATE-OBS")
        self.gos_level3_status: str = self.header.get("GOSLVL3")
        self.gos_level3_lamp_status: str = self.header.get("GOSLAMP")
        self.gos_level0_status: str = self.header.get("GOSLVL0")
        self.gos_retarder_status: str = self.header.get("GOSRET")
        self.gos_polarizer_status: str = self.header.get("GOSPOL")
        self.wavelength: str = self.header.get("LINEWAV")
        self.roundable_time: float = self.header.get("RTIME", 0.0)


@pytest.fixture()
def basic_header_objs():
    header_dict = {
        "thing0": fits.header.Header(
            {
                "id_key": 0,
                "constant": 6.28,
                "near": 1.23,
                "DKIST004": "observe",
                "ID___012": "experiment_id_1",
                "ID___013": "proposal_id_1",
                "XPOSURE": 0.0013000123,
                "TEXPOSUR": 10.0,
                "NSUMEXP": 3,
                "DSPSNUM": 1,
                "DSPSREPS": 2,
                "DATE-OBS": "2022-06-17T22:00:00.000",
                "DKIST011": "2023-09-28T10:23.000",
                "LINEWAV": 666.0,
            }
        ),
        "thing1": fits.header.Header(
            {
                "id_key": 1,
                "constant": 6.28,
                "near": 1.22,
                "DKIST004": "observe",
                "ID___012": "experiment_id_1",
                "ID___013": "proposal_id_1",
                "XPOSURE": 0.0013000987,
                "TEXPOSUR": 10.0,
                "NSUMEXP": 3,
                "DSPSNUM": 1,
                "DSPSREPS": 2,
                "DATE-OBS": "2022-06-17T22:00:01.000",
                "DKIST011": "2023-09-28T10:23.000",
                "LINEWAV": 666.0,
                "GOSRET": "incorrect",
            }
        ),
        "thing2": fits.header.Header(
            {
                "id_key": 2,
                "constant": 6.28,
                "near": 1.24,
                "DKIST004": "dark",
                "ID___012": "experiment_id_2",
                "ID___013": "proposal_id_2",
                "XPOSURE": 12.345,
                "TEXPOSUR": 1.123456789,
                "NSUMEXP": 1,
                "DSPSNUM": 2,
                "DSPSREPS": 7,
                "DATE-OBS": "2022-06-17T22:00:02.000",
                "DKIST011": "1903-01-01T12:00.000",
                "LINEWAV": 0.0,
                "GOSRET": "wrong",
                "RTIME": 2.3400000009999,
            }
        ),
        "thing3": fits.header.Header(
            {
                "id_key": 0,
                "constant": 6.28,
                "near": 1.23,
                "DKIST004": "observe",
                "ID___012": "experiment_id_1",
                "ID___013": "proposal_id_1",
                "XPOSURE": 100.0,
                "TEXPOSUR": 11.0,
                "NSUMEXP": 4,
                "DSPSNUM": 2,
                "DSPSREPS": 2,
                "DATE-OBS": "2022-06-17T22:00:03.000",
                "DKIST011": "2023-09-28T10:23.000",
                "LINEWAV": 666.0,
                "GOSRET": "clear",
            },
        ),
        "thing4": fits.header.Header(
            {
                "DKIST004": "gain",
                "ID___013": "proposal_id_1",
                "id_key": 0,
                "constant": 6.28,
                "near": 1.23,
                "ID___012": "experiment_id_1",
                "XPOSURE": 100.0,
                "TEXPOSUR": 11.0,
                "NSUMEXP": 4,
                "DSPSNUM": 2,
                "DSPSREPS": 2,
                "DATE-OBS": "2022-06-17T22:00:03.000",
                "DKIST011": "2023-09-28T10:23.000",
                "LINEWAV": 666.0,
                "GOSRET": "clear",
                "RTIME": 2.340000004444,
            }
        ),
    }
    return (FitsReader.from_header(header, name=path) for path, header in header_dict.items())


@pytest.fixture
def task_with_gains_header_objs():
    header_dict = {
        "lamp_gain": fits.header.Header({"DKIST004": "gain", "GOSLVL3": "lamp", "GOSLAMP": "on"}),
        "solar_gain": fits.header.Header({"DKIST004": "gain", "GOSLVL3": "clear"}),
        "dark": fits.header.Header({"DKIST004": "DARK"}),
    }
    return (FitsReader.from_header(header, name=path) for path, header in header_dict.items())


@pytest.fixture
def retarder_name():
    return "Foo Bar"


@pytest.fixture
def task_with_polcal_header_objs(retarder_name):
    header_dict = {
        "polcal_dark": fits.header.Header(
            {"DKIST004": "polcal", "GOSLVL0": "DarkShutter", "GOSPOL": "clear", "GOSRET": "clear"}
        ),
        "polcal_gain": fits.header.Header(
            {"DKIST004": "polcal", "GOSLVL0": "FieldStop", "GOSPOL": "clear", "GOSRET": "clear"}
        ),
        "just_polcal": fits.header.Header(
            {"DKIST004": "polcal", "GOSLVL0": "something", "GOSRET": retarder_name}
        ),
    }
    return (FitsReader.from_header(header, name=path) for path, header in header_dict.items())


@pytest.fixture()
def bad_header_objs():
    bad_headers = {
        "thing0": fits.header.Header(
            {
                "id_key": 0,
                "constant": 6.28,
                "near": 1.23,
                "DKIST004": "observe",
                "DSPSREPS": 2,
                "DSPSNUM": 2,
                "DATE-OBS": "2022-06-17T22:00:00.000",
                "LINEWAV": 0.0,
            }
        ),
        "thing1": fits.header.Header(
            {
                "id_key": 1,
                "constant": 3.14,
                "near": 1.76,
                "DKIST004": "observe",
                "DSPSREPS": 2,
                "DSPSNUM": 2,
                "DATE-OBS": "2022-06-17T22:00:03.000",
                "LINEWAV": 1.0,
            }
        ),
        "thing2": fits.header.Header(
            {
                "id_key": 1,
                "constant": 2.78,
                "near": 1.76,
                "DKIST004": "gain",
                "DSPSREPS": 2,
                "DSPSNUM": 2,
                "DATE-OBS": "2022-06-17T22:00:03.000",
                "LINEWAV": 1.0,
            }
        ),
        "thing4": fits.header.Header(
            {
                "id_key": 1,
                "constant": 6.66,
                "near": 1.76,
                "DKIST004": "dark",
                "DSPSREPS": 2,
                "DSPSNUM": 2,
                "DATE-OBS": "2022-06-17T22:00:03.000",
                "LINEWAV": 1.0,
            }
        ),
    }
    return (FitsReader.from_header(header, name=path) for path, header in bad_headers.items())


@pytest.fixture
def bad_polcal_header_objs():
    # I.e., GOSRET has multiple values
    header_dict = {
        "thing1": fits.header.Header({"DKIST004": "polcal", "GOSRET": "clear"}),
        "thing2": fits.header.Header({"DKIST004": "polcal", "GOSRET": "RET1"}),
        "thing3": fits.header.Header({"DKIST004": "polcal", "GOSRET": "RET2"}),
    }
    return (FitsReader.from_header(header, name=path) for path, header in header_dict.items())


def test_unique_bud(basic_header_objs):
    """
    Given: A set of headers with a constant value header key
    When: Ingesting headers with a UniqueBud and asking for the value
    Then: The Bud's value is the header constant value
    """
    bud = UniqueBud(
        constant_name="constant",
        metadata_key="constant_thing",
    )
    assert bud.stem_name == "constant"
    for fo in basic_header_objs:
        key = fo.name
        bud.update(key, fo)

    petal = list(bud.petals)
    assert len(petal) == 1
    assert petal[0].value == 6.28


def test_unique_bud_non_unique_inputs(bad_header_objs):
    """
    Given: A set of headers with a non-constant header key that is expected to be constant
    When: Ingesting headers with a UniqueBud and asking for the value
    Then: An error is raised
    """
    bud = UniqueBud(
        constant_name="constant",
        metadata_key="constant_thing",
    )
    assert bud.stem_name == "constant"
    for fo in bad_header_objs:
        key = fo.name
        bud.update(key, fo)

    with pytest.raises(ValueError):
        assert next(bud.petals)


@pytest.mark.parametrize(
    "ip_task_type",
    [
        pytest.param("observe", id="single_task_type"),
        pytest.param(["observe", "gain"], id="task_type_list"),
    ],
)
def test_task_unique_bud(basic_header_objs, ip_task_type):
    """
    Given: A set of headers with a constant value header key
    When: Ingesting headers with a TaskUniqueBud and asking for the value
    Then: The bud's value is the header constant value
    """
    bud = TaskUniqueBud(
        constant_name="proposal", metadata_key="proposal_id", ip_task_types=ip_task_type
    )
    assert bud.stem_name == "proposal"
    for fo in basic_header_objs:
        key = fo.name
        bud.update(key, fo)

    petal = list(bud.petals)
    assert len(petal) == 1
    assert petal[0].value == "proposal_id_1"


@pytest.mark.parametrize(
    "ip_task_type",
    [
        pytest.param("observe", id="single_task_type"),
        pytest.param(["dark", "gain"], id="task_type_list"),
    ],
)
def test_task_unique_bud_non_unique_inputs(bad_header_objs, ip_task_type):
    """
    Given: A set of headers with a non-constant header key that is expected to be constant
    When: Ingesting headers with a UniqueBud and asking for the value
    Then: An error is raised
    """
    bud = TaskUniqueBud(
        constant_name="constant", metadata_key="constant_thing", ip_task_types=ip_task_type
    )
    assert bud.stem_name == "constant"
    for fo in bad_header_objs:
        key = fo.name
        bud.update(key, fo)

    with pytest.raises(ValueError):
        list(bud.petals)


def test_single_value_single_key_flower(basic_header_objs):
    """
    Given: A set of filepaths and associated headers with a single key that has a limited set of values
    When: Ingesting with a SingleValueSingleKeyFlower and asking for the grouping
    Then: The filepaths are grouped correctly based on the header key value
    """
    flower = SingleValueSingleKeyFlower(tag_stem_name="id", metadata_key="thing_id")
    assert flower.stem_name == "id"
    for fo in basic_header_objs:
        key = fo.name
        flower.update(key, fo)

    petals = sorted(list(flower.petals), key=lambda x: x.value)
    assert len(petals) == 3
    assert petals[0].value == 0
    assert petals[0].keys == ["thing0", "thing3", "thing4"]
    assert petals[1].value == 1
    assert petals[1].keys == ["thing1"]
    assert petals[2].value == 2
    assert petals[2].keys == ["thing2"]


@pytest.mark.parametrize(
    "ip_task_type, expected_value",
    [
        pytest.param("dark", (2.34,), id="single_task_type"),
        pytest.param(["dark", "gain"], (2.34,), id="task_type_list"),
        pytest.param(["dark", "gain", "observe"], (0.0, 2.34), id="task_type_list2"),
    ],
)
def test_task_time_base_bud(basic_header_objs, ip_task_type, expected_value):
    """
    Given: A set of headers with a value that needs to be rounded
    When: Ingesting headers with a `TaskTimeBudBase` bud and asking for the value
    Then: The bud's value is the header constant value
    """
    bud = TaskTimeBudBase(
        stem_name="rounded_time", metadata_key="roundable_time", ip_task_types=ip_task_type
    )
    assert bud.stem_name == "rounded_time"
    for fo in basic_header_objs:
        key = fo.name
        bud.update(key, fo)

    petal = list(bud.petals)
    assert len(petal) == 1
    assert petal[0].value == expected_value


def test_cs_step_flower(grouped_cal_sequence_headers, non_polcal_headers, max_cs_step_time_sec):
    """
    Given: A set of PolCal headers, non-PolCal headers, and the CSStepFlower
    When: Updating the CSStepFlower with all headers
    Then: The flower correctly organizes the PolCal frames and ignores the non-PolCal frames
    """
    cs_step_flower = CSStepFlower(max_cs_step_time_sec=max_cs_step_time_sec)
    for step, headers in grouped_cal_sequence_headers.items():
        for i, h in enumerate(headers):
            key = f"step_{step}_file_{i}"
            cs_step_flower.update(key, h)

    for h in non_polcal_headers:
        cs_step_flower.update("non_polcal", h)

    assert len(list(cs_step_flower.petals)) == len(list(grouped_cal_sequence_headers.keys()))
    for step_petal in cs_step_flower.petals:
        assert sorted(step_petal.keys) == [
            f"step_{step_petal.value}_file_{i}" for i in range(len(step_petal.keys))
        ]


def test_num_cs_step_bud(grouped_cal_sequence_headers, non_polcal_headers, max_cs_step_time_sec):
    """
    Given: A set of PolCal headers, non-PolCal headers, and the NumCSStepBud
    When: Updating the NumCSStepBud with all headers
    Then: The bud reports the correct number of CS Steps (thus ignoring the non-PolCal frames)
    """
    num_cs_bud = NumCSStepBud(max_cs_step_time_sec=max_cs_step_time_sec)
    for step, headers in grouped_cal_sequence_headers.items():
        for h in headers:
            num_cs_bud.update(step, h)

    for h in non_polcal_headers:
        num_cs_bud.update("foo", h)

    bud = list(num_cs_bud.petals)
    assert len(bud) == 1
    assert bud[0].value == len(grouped_cal_sequence_headers.keys())


def test_proposal_id_bud(basic_header_objs):
    """
    Given: A set of headers with proposal ID values
    When: Ingesting the headers with a ProposalIdBud
    Then: The Bud's petal has the correct value
    """
    bud = ProposalIdBud()
    assert bud.stem_name == BudName.proposal_id.value
    for fo in basic_header_objs:
        key = fo.name
        bud.update(key, fo)

    petal = list(bud.petals)
    assert len(petal) == 1
    assert petal[0].value == "proposal_id_1"


def test_contributing_proposal_ids_bud(basic_header_objs):
    """
    Given: A set of headers with proposal ID values
    When: Ingesting the headers with a ContributingProposalIdsBud
    Then: The Bud's petal is the tuple of all input proposal IDs
    """
    bud = ContributingProposalIdsBud()
    assert bud.stem_name == BudName.contributing_proposal_ids.value
    for fo in basic_header_objs:
        key = fo.name
        bud.update(key, fo)

    petal = list(bud.petals)
    assert len(petal) == 1
    assert sorted(list(petal[0].value)) == ["proposal_id_1", "proposal_id_2"]


def test_experiment_id_bud(basic_header_objs):
    """
    Given: A set of headers with experiment ID values
    When: Ingesting the headers with a ExperimentIdBud
    Then: The Bud's petal has the correct value
    """
    bud = ExperimentIdBud()
    assert bud.stem_name == BudName.experiment_id.value
    for fo in basic_header_objs:
        key = fo.name
        bud.update(key, fo)

    petal = list(bud.petals)
    assert len(petal) == 1
    assert petal[0].value == "experiment_id_1"


def test_contributing_experiment_ids_bud(basic_header_objs):
    """
    Given: A set of headers with experiment ID values
    When: Ingesting the headers with a ContributingExperimentIdsBud
    Then: The Bud's petal is the tuple of all input experiment IDs
    """
    bud = ContributingExperimentIdsBud()
    assert bud.stem_name == BudName.contributing_experiment_ids.value
    for fo in basic_header_objs:
        key = fo.name
        bud.update(key, fo)

    petal = list(bud.petals)
    assert len(petal) == 1
    assert sorted(list(petal[0].value)) == ["experiment_id_1", "experiment_id_2"]


def test_exp_time_flower(basic_header_objs):
    """
    Given: A set of filepaths and associated headers with XPOSURE keywords
    When: Ingesting with an ExposureTimeFlower
    Then: The filepaths are grouped correctly based on their exposure time
    """
    flower = ExposureTimeFlower()
    assert flower.stem_name == StemName.exposure_time.value
    for fo in basic_header_objs:
        key = fo.name
        flower.update(key, fo)

    petals = sorted(list(flower.petals), key=lambda x: x.value)
    assert len(petals) == 3
    assert petals[0].value == 0.0013
    assert petals[0].keys == ["thing0", "thing1"]
    assert petals[1].value == 12.345
    assert petals[1].keys == ["thing2"]
    assert petals[2].value == 100.0
    assert petals[2].keys == ["thing3", "thing4"]


def test_readout_exp_time_flower(basic_header_objs):
    """
    Given: A set of filepaths and associated headers with TEXPOSUR keywords
    When: Ingesting with an ReadoutExpTimeFlower
    Then: The filepaths are grouped correctly based on their readout exposure time
    """
    flower = ReadoutExpTimeFlower()
    assert flower.stem_name == StemName.readout_exp_time.value
    for fo in basic_header_objs:
        key = fo.name
        flower.update(key, fo)

    petals = sorted(list(flower.petals), key=lambda x: x.value)
    assert len(petals) == 3
    assert petals[0].value == 1.123457
    assert petals[0].keys == ["thing2"]
    assert petals[1].value == 10.0
    assert petals[1].keys == ["thing0", "thing1"]
    assert petals[2].value == 11.0
    assert petals[2].keys == ["thing3", "thing4"]


def test_task_type_flower(task_with_gains_header_objs):
    """
    Given: A set of filepaths and associated headers with various task-related header keys
    When: Ingesting with the TaskTypeFlower
    Then: The correct tags are returned
    """
    flower = TaskTypeFlower(header_task_parsing_func=parse_header_ip_task_with_gains)
    assert flower.stem_name == StemName.task.value
    for fo in task_with_gains_header_objs:
        key = fo.name
        flower.update(key, fo)

    petals = sorted(list(flower.petals), key=lambda x: x.value.casefold())
    assert len(petals) == 3
    assert petals[0].value == TaskName.dark.value
    assert petals[0].keys == ["dark"]
    assert petals[1].value == TaskName.lamp_gain.value
    assert petals[1].keys == ["lamp_gain"]
    assert petals[2].value == TaskName.solar_gain.value
    assert petals[2].keys == ["solar_gain"]


def test_polcal_task_flower(task_with_polcal_header_objs):
    """
    Given: A set of filepaths and associated headers with various polcal task-related header keys
    When: Ingesting with the PolcalTaskFlower
    Then: The correct tags are returned
    """
    flower = PolcalTaskFlower()
    assert flower.stem_name == StemName.task.value
    for fo in task_with_polcal_header_objs:
        key = fo.name
        flower.update(key, fo)

    petals = sorted(list(flower.petals), key=lambda x: x.value.casefold())
    assert len(petals) == 2
    assert petals[0].value == TaskName.polcal_dark.value
    assert petals[0].keys == ["polcal_dark"]
    assert petals[1].value == TaskName.polcal_gain.value
    assert petals[1].keys == ["polcal_gain"]


def test_obs_ip_start_time_bud(basic_header_objs):
    """
    Given: A set of filepaths and associated headers that span multiple IP types, each with DKIST011 (IP start time) keywords
    When: Ingesting with a ObsIpStartTimeBud
    Then: The correct value from *only* the observe IP is returned
    """
    bud = ObsIpStartTimeBud()
    assert bud.stem_name == BudName.obs_ip_start_time.value
    for fo in basic_header_objs:
        key = fo.name
        bud.update(key, fo)

    petals = list(bud.petals)
    assert len(petals) == 1
    assert petals[0].value == "2023-09-28T10:23.000"


def test_fpa_exp_times_bud(basic_header_objs):
    """
    Given: A set of filepaths and associated headers with XPOSURE keywords
    When: Ingesting with a TaskExposureTimesBud
    Then: All (rounded) exposure times are accounted for in the resulting tuple
    """
    dark_bud = TaskExposureTimesBud(stem_name=BudName.dark_exposure_times, ip_task_types="DARK")
    obs_bud = TaskExposureTimesBud(stem_name="obs_exp_times", ip_task_types="OBSERVE")
    assert dark_bud.stem_name == BudName.dark_exposure_times.value
    for fo in basic_header_objs:
        key = fo.name
        dark_bud.update(key, fo)
        obs_bud.update(key, fo)

    dark_petal = list(dark_bud.petals)
    assert len(dark_petal) == 1
    assert type(dark_petal[0].value) is tuple
    assert tuple(sorted(dark_petal[0].value)) == (12.345,)

    obs_petal = list(obs_bud.petals)
    assert len(obs_petal) == 1
    assert type(obs_petal[0].value) is tuple
    assert tuple(sorted(obs_petal[0].value)) == (0.0013, 100.0)


def test_readout_exp_times_bud(basic_header_objs):
    """
    Given: A set of filepaths and associated headers with TEXPOSUR keywords
    When: Ingesting with a TaskReadoutExpTimesBud
    Then: All (rounded) exposure times are accounted for in the resulting tuple
    """
    dark_bud = TaskReadoutExpTimesBud(stem_name=BudName.dark_exposure_times, ip_task_types="DARK")
    obs_bud = TaskReadoutExpTimesBud(stem_name="obs_exp_times", ip_task_types="OBSERVE")
    assert dark_bud.stem_name == BudName.dark_exposure_times.value
    for fo in basic_header_objs:
        key = fo.name
        dark_bud.update(key, fo)
        obs_bud.update(key, fo)

    dark_petal = list(dark_bud.petals)
    assert len(dark_petal) == 1
    assert type(dark_petal[0].value) is tuple
    assert tuple(sorted(dark_petal[0].value)) == (1.123457,)

    obs_petal = list(obs_bud.petals)
    assert len(obs_petal) == 1
    assert type(obs_petal[0].value) is tuple
    assert tuple(sorted(obs_petal[0].value)) == (10.0, 11.0)


def test_dsps_bud(basic_header_objs):
    bud = TotalDspsRepeatsBud()
    assert bud.stem_name == BudName.num_dsps_repeats.value
    for fo in basic_header_objs:
        key = fo.name
        bud.update(key, fo)

    petal = list(bud.petals)
    assert len(petal) == 1
    assert petal[0].value == 2


def test_dsps_flower(basic_header_objs):
    """
    Given: A set of filepaths and associated headers with DSPS keywords
    When: Ingesting with a DspsRepeatNumber Flower
    Then: The correct values are returned
    """
    flower = DspsRepeatNumberFlower()
    assert flower.stem_name == StemName.dsps_repeat.value
    for fo in basic_header_objs:
        key = fo.name
        flower.update(key, fo)

    petals = sorted(list(flower.petals), key=lambda x: x.value)
    assert len(petals) == 2
    assert petals[0].value == 1
    assert petals[0].keys == ["thing0", "thing1"]
    assert petals[1].value == 2
    assert petals[1].keys == ["thing3"]


def test_average_cadence_bud(basic_header_objs):
    """
    Given: A set of filepaths and associated headers with DATE-OBS keywords
    When: Ingesting with the AverageCadenceBud
    Then: The correct values are returned
    """
    bud = AverageCadenceBud()
    assert bud.stem_name == BudName.average_cadence.value
    for fo in basic_header_objs:
        key = fo.name
        bud.update(key, fo)

    petal = list(bud.petals)
    assert len(petal) == 1

    # Because there are 3 observe frames in `basic_header_objs` spaced 1, and 2 seconds apart.
    assert petal[0].value == 1.5


def test_max_cadence_bud(basic_header_objs):
    """
    Given: A set of filepaths and associated headers with DATE-OBS keywords
    When: Ingesting with the MaxCadenceBud
    Then: The correct values are returned
    """
    bud = MaximumCadenceBud()
    assert bud.stem_name == BudName.maximum_cadence.value
    for fo in basic_header_objs:
        key = fo.name
        bud.update(key, fo)

    petal = list(bud.petals)
    assert len(petal) == 1

    # Because there are 3 observe frames in `basic_header_objs` spaced 1, and 2 seconds apart.
    assert petal[0].value == 2


def test_minimum_cadence_bud(basic_header_objs):
    """
    Given: A set of filepaths and associated headers with DATE-OBS keywords
    When: Ingesting with the MinimumCadenceBud
    Then: The correct values are returned
    """
    bud = MinimumCadenceBud()
    assert bud.stem_name == BudName.minimum_cadence.value
    for fo in basic_header_objs:
        key = fo.name
        bud.update(key, fo)

    petal = list(bud.petals)
    assert len(petal) == 1

    # Because there are 3 observe frames in `basic_header_objs` spaced 1, and 2 seconds apart.
    assert petal[0].value == 1


def test_variance_cadence_bud(basic_header_objs):
    """
    Given: A set of filepaths and associated headers with DATE-OBS keywords
    When: Ingesting with the VarianceCadenceBud
    Then: The correct values are returned
    """
    bud = VarianceCadenceBud()
    assert bud.stem_name == BudName.variance_cadence.value
    for fo in basic_header_objs:
        key = fo.name
        bud.update(key, fo)

    petal = list(bud.petals)
    assert len(petal) == 1

    # Because there are 3 observe frames in `basic_header_objs` spaced 1, and 2 seconds apart.
    assert petal[0].value == 0.25


def test_observe_wavelength_bud(basic_header_objs):
    """
    Given: A set of headers with wavelength values
    When: Ingesting the headers with the ObserveWavelengthBud
    Then: The petal contains the wavelength header value of the observe frames
    """
    bud = ObserveWavelengthBud()
    assert bud.stem_name == BudName.wavelength.value
    for fo in basic_header_objs:
        key = fo.name
        bud.update(key, fo)

    petal = list(bud.petals)
    assert len(petal) == 1
    assert petal[0].value == 666.0


def test_near_bud(basic_header_objs):
    """
    Given: A set of headers with a near constant value header key that are within a given range
    When: Ingesting headers with a NearBud and asking for the value
    Then: The Bud's value is the average of the header values
    """
    bud = NearFloatBud(
        constant_name="near",
        metadata_key="near_thing",
        tolerance=0.5,
    )
    assert bud.stem_name == "near"
    for fo in basic_header_objs:
        key = fo.name
        bud.update(key, fo)

    petal = list(bud.petals)
    assert len(petal) == 1
    assert petal[0].value == 1.23


def test_task_near_bud(basic_header_objs):
    """
    Given: A set of headers with a near constant value header key that are within a given range
    When: Ingesting headers with a TaskNearBud and asking for the value
    Then: The bud's value is the average of the header values of that task type
    """
    bud = TaskNearFloatBud(
        constant_name="near", metadata_key="near_thing", ip_task_types="observe", tolerance=0.5
    )
    assert bud.stem_name == "near"
    for fo in basic_header_objs:
        key = fo.name
        bud.update(key, fo)

    petal = list(bud.petals)
    assert len(petal) == 1
    assert round(petal[0].value, 3) == 1.227


def test_multi_task_near_bud():
    """
    Given: A set of headers where multiple, but not all, task types have the same values
    When: Ingesting the headers with a `TaskNearBud`
    Then: When multiple tasks have the same value the correct value is returned. When a task has a different value, an
      Error is raised.
    """
    header_dicts = [
        {"DKIST004": "observe", "near": 3.2},
        {"DKIST004": "dark", "near": 3.11},
        {"DKIST004": "solar", "near": 1e3},
    ]
    header_objs = [FitsReader.from_header(h, f"{i}") for i, h in enumerate(header_dicts)]

    bud = TaskNearFloatBud(
        constant_name="near",
        metadata_key="near_thing",
        ip_task_types=["observe", "dark"],
        tolerance=0.1,
    )
    for fo in header_objs:
        bud.update(fo.name, fo)

    petal = list(bud.petals)
    assert len(petal) == 1
    assert round(petal[0].value, 0) == 3.0

    bad_bud = TaskNearFloatBud(
        constant_name="near",
        metadata_key="near_thing",
        ip_task_types=["observe", "solar"],
        tolerance=0.1,
    )
    for fo in header_objs:
        bad_bud.update(fo.name, fo)

    with pytest.raises(ValueError, match="near values are not close enough"):
        list(bad_bud.petals)


def test_near_bud_not_near_inputs(bad_header_objs):
    """
    Given: A set of headers with a header key that is expected to be in a given range but is not
    When: Ingesting headers with a NearBud and asking for the value
    Then: An error is raised
    """
    bud = NearFloatBud(
        constant_name="near",
        metadata_key="near_thing",
        tolerance=0.5,
    )
    assert bud.stem_name == "near"
    for fo in bad_header_objs:
        key = fo.name
        bud.update(key, fo)

    with pytest.raises(ValueError):
        assert next(bud.petals)


def test_retarder_name_bud(basic_header_objs, task_with_polcal_header_objs, retarder_name):
    """
    Given: A set of headers with two values for LVL1STAT: "clear" and another name
    When: Ingesting the headers with RetarderNameBud and asking for the value
    Then: The retarder name is returned
    """
    bud = RetarderNameBud()
    input_objects = chain(basic_header_objs, task_with_polcal_header_objs)
    for fo in input_objects:
        key = fo.name
        bud.update(key, fo)

    assert bud.bud.value == retarder_name


def test_retarder_name_bud_error(bad_polcal_header_objs):
    """
    Given: A set of headers with "clear" and two other values for LVL1STAT
    When: Ingesting the headers with RetarderNameBud and asking for the value
    Then: An error is raised
    """
    bud = RetarderNameBud()
    for fo in bad_polcal_header_objs:
        key = fo.name
        bud.update(key, fo)

    # Crazy regex to handle non-deterministic order of sets.
    # https://regex101.com/r/zh9iG6/1
    with pytest.raises(
        ValueError,
        match=r"Multiple non-clear retarder names found. Names: {'RET(1)?(?(1)|2)', 'RET(?(1)2|1)'}",
    ):
        _ = bud.bud


# TODO: test new stems that have been added to parse_l0_input_data
