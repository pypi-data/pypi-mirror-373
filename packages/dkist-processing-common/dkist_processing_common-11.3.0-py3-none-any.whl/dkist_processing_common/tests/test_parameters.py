"""
HOW TO WRITE TESTS FOR NEW PARAMETER SUBCLASSES :

1. Add parameters to INPUT_DATASET that exercise the necessary logic (this won't be needed in all cases)
2. Create a Parameter object that subclasses `FilledParameters` and the new subclass
3. Create a helper function that returns the `partial` of the new class with the new kwargs already filled in
4. Add a `pytest.param` with this helper function to `test_parameters` to make sure none of the default stuff broke
5. Write a new test that only uses the helper function to test the new functionality.
"""

import json
from datetime import datetime
from datetime import timedelta
from functools import partial
from typing import Any
from typing import Type

import numpy as np
import pytest
from astropy.io import fits

from dkist_processing_common.codecs.array import array_encoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.models.parameters import ParameterArmIdMixin
from dkist_processing_common.models.parameters import ParameterBase
from dkist_processing_common.models.parameters import ParameterWavelengthMixin
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_processing_common.tests.test_input_dataset import input_dataset_frames_part_factory

FITS_FILE = "fits.dat"
NP_FILE = "np.npy"


@pytest.fixture
def input_dataset_parameters():
    return [
        {
            "parameterName": "basic_param",
            "parameterValues": [
                {
                    "parameterValueId": 1,
                    "parameterValue": json.dumps([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
                    "parameterValueStartDate": "1955-01-01",
                }
            ],
        },
        {
            "parameterName": "no_date",
            "parameterValues": [{"parameterValueId": 1, "parameterValue": json.dumps(4)}],
        },
        {
            "parameterName": "three_values",
            "parameterValues": [
                {
                    "parameterValueId": 1,
                    "parameterValue": json.dumps(4),
                    "parameterValueStartDate": "2020-03-13",
                },
                {
                    "parameterValueId": 2,
                    "parameterValue": json.dumps(6),
                    "parameterValueStartDate": "1955-01-02",
                },
                {
                    "parameterValueId": 3,
                    "parameterValue": json.dumps(5),
                    "parameterValueStartDate": (
                        datetime.now() + timedelta(days=365)
                    ).isoformat(),  # Guaranteed to be in the future!
                },
            ],
        },
        {
            "parameterName": "two_values_one_date",
            "parameterValues": [
                {"parameterValueId": 1, "parameterValue": json.dumps(4)},
                {
                    "parameterValueId": 2,
                    "parameterValue": json.dumps(6),
                    "parameterValueStartDate": "1955-01-02",
                },
            ],
        },
        {
            "parameterName": "wavelength_param",
            "parameterValues": [
                {
                    "parameterValueId": 1,
                    "parameterValue": json.dumps(
                        {"wavelength": [10, 20, 30, 40], "values": [1, 2, 3, 4]}
                    ),
                }
            ],
        },
        {
            "parameterName": "arm_parameter_arm1",
            "parameterValues": [{"parameterValueId": 1, "parameterValue": json.dumps("arm1")}],
        },
        {
            "parameterName": "arm_parameter_arm2",
            "parameterValues": [{"parameterValueId": 1, "parameterValue": json.dumps("arm2")}],
        },
        {
            "parameterName": "fits_file_parameter",
            "parameterValues": [
                {
                    "parameterValueId": 1,
                    "parameterValue": json.dumps(
                        {
                            "__file__": {
                                "bucket": "not_used",
                                "objectKey": "not_used",
                                "tag": Tag.parameter(FITS_FILE),
                            }
                        }
                    ),
                }
            ],
        },
        {
            "parameterName": "numpy_file_parameter",
            "parameterValues": [
                {
                    "parameterValueId": 1,
                    "parameterValue": json.dumps(
                        {
                            "__file__": {
                                "bucket": "not_used",
                                "objectKey": "not_used",
                                "tag": Tag.parameter(NP_FILE),
                            }
                        }
                    ),
                }
            ],
        },
    ]


@pytest.fixture()
def input_dataset_parts(input_dataset_parameters) -> tuple[Any, str]:
    return (input_dataset_parameters, Tag.input_dataset_parameters())


@pytest.fixture()
def task_class_with_parameters(parameter_class) -> Type[WorkflowTaskBase]:
    class TaskWithParameters(WorkflowTaskBase):
        def __init__(self, recipe_run_id: int, workflow_name: str, workflow_version: str):
            super().__init__(
                recipe_run_id=recipe_run_id,
                workflow_name=workflow_name,
                workflow_version=workflow_version,
            )
            self.parameters = parameter_class(scratch=self.scratch)

        def run(self) -> None:
            pass

    return TaskWithParameters


@pytest.fixture()
def task_with_parameters(task_with_input_dataset, task_class_with_parameters):
    task_class = task_class_with_parameters
    with task_class(
        recipe_run_id=task_with_input_dataset.recipe_run_id,
        workflow_name=task_with_input_dataset.workflow_name,
        workflow_version=task_with_input_dataset.workflow_version,
    ) as task:
        phdu = fits.PrimaryHDU(np.ones((3, 3)) * 3)
        ihdu = fits.ImageHDU(np.ones((4, 4)) * 4)
        task.write(
            data=fits.HDUList([phdu, ihdu]),
            tags=Tag.parameter(FITS_FILE),
            encoder=fits_hdulist_encoder,
        )
        task.write(data=np.ones((3, 3)) * 4, tags=Tag.parameter(NP_FILE), encoder=array_encoder)
        yield task
        task._purge()


class FilledParametersNoObsTime(ParameterBase):
    @property
    def pre_parse_parameter(self):
        # To emulate parameter retrieval prior to parsing of the obs ip start time
        return self._find_most_recent_past_value("three_values", start_date=datetime.now())


class FilledParametersWithObsTime(ParameterBase):
    @property
    def basic_parameter(self):
        return self._find_most_recent_past_value("basic_param")

    @property
    def no_date_parameter(self):
        return self._find_most_recent_past_value("no_date")

    @property
    def three_values_parameter(self):
        return self._find_most_recent_past_value("three_values")

    @property
    def two_values_one_date_parameter(self):
        return self._find_most_recent_past_value("two_values_one_date")

    @property
    def fits_file_parameter(self):
        param_obj = self._find_most_recent_past_value("fits_file_parameter")
        return self._load_param_value_from_fits(param_obj=param_obj)

    @property
    def non_primary_fits_file_parameter(self):
        param_obj = self._find_most_recent_past_value("fits_file_parameter")
        return self._load_param_value_from_fits(param_obj=param_obj, hdu=1)

    @property
    def numpy_file_parameter(self):
        param_obj = self._find_most_recent_past_value("numpy_file_parameter")
        return self._load_param_value_from_numpy_save(param_obj=param_obj)


def parameter_class_with_obs_ip_start_time():
    obs_ip_start_time = "1955-02-03"
    return partial(FilledParametersWithObsTime, obs_ip_start_time=obs_ip_start_time)


class FilledWavelengthParameters(FilledParametersWithObsTime, ParameterWavelengthMixin):
    @property
    def wavelength_parameter(self):
        return self._find_parameter_closest_wavelength("wavelength_param")

    @property
    def interpolated_wavelength_parameter(self):
        return self._interpolate_wavelength_parameter("wavelength_param", method="linear")


def parameter_class_with_wavelength():
    wavelength = 25  # Exactly halfway between 20 and 30
    obs_ip_start_time = "1955-02-03"
    return partial(
        FilledWavelengthParameters, obs_ip_start_time=obs_ip_start_time, wavelength=wavelength
    )


class FilledArmIdParameters(FilledParametersWithObsTime, ParameterArmIdMixin):
    @property
    def arm_parameter(self):
        return self._find_parameter_for_arm("arm_parameter")


def parameter_class_with_arm1():
    obs_ip_start_time = "1955-02-03"
    arm_id = "arm1"
    return partial(FilledArmIdParameters, obs_ip_start_time=obs_ip_start_time, arm_id=arm_id)


def parameter_class_with_arm2():
    obs_ip_start_time = "1955-02-03"
    arm_id = "arm2"
    return partial(FilledArmIdParameters, obs_ip_start_time=obs_ip_start_time, arm_id=arm_id)


@pytest.mark.parametrize(
    "parameter_class",
    [
        pytest.param(
            parameter_class_with_obs_ip_start_time(),
            id="Parameters_with_OBS_IP_start_time",
        ),
        pytest.param(parameter_class_with_wavelength(), id="Wavelength parameters"),
    ],
)
def test_parameters(task_with_parameters, input_dataset_parts: tuple[Any, str]):
    """ "
    Given: a task with a ParameterBase subclass (with obs_ip_start_time) and populated parameters
    When: asking for specific parameter values
    Then: the correct values are returned
    """
    assert task_with_parameters.parameters.basic_parameter == [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    assert task_with_parameters.parameters.no_date_parameter == 4

    # Make sure the most recent value to the obs ip start date is returned
    assert task_with_parameters.parameters.three_values_parameter == 6

    # Make sure the value with *any* date is returned
    assert task_with_parameters.parameters.two_values_one_date_parameter == 6

    # Make sure fits file loading works correctly
    fits_parameter = task_with_parameters.parameters.fits_file_parameter
    assert isinstance(fits_parameter, np.ndarray)
    np.testing.assert_array_equal(fits_parameter, 3)

    non_primary_fits_parameter = task_with_parameters.parameters.non_primary_fits_file_parameter
    assert isinstance(non_primary_fits_parameter, np.ndarray)
    np.testing.assert_array_equal(non_primary_fits_parameter, 4)

    # Make sure numpy file loading works correctly
    numpy_parameter = task_with_parameters.parameters.numpy_file_parameter
    assert isinstance(numpy_parameter, np.ndarray)
    np.testing.assert_array_equal(numpy_parameter, 4)

    # Raise an error if all values in the db are in the "future"
    with pytest.raises(ValueError):
        task_with_parameters.parameters._find_most_recent_past_value(
            "basic_param", start_date=datetime(1776, 7, 4)
        )


@pytest.mark.parametrize(
    "parameter_class",
    [
        pytest.param(FilledParametersNoObsTime, id="Pre-Parse_Parameters"),
    ],
)
def test_parameters_no_obs_ip_start_time(
    task_with_parameters, input_dataset_parts: tuple[Any, str]
):
    """
    Given: a task with a ParameterBase subclass that doesn't have an obs ip start time set
    When: asking for a parameter that uses datetime.now() as the startdate
    Then: the correct value is returned
    """
    assert task_with_parameters.parameters.pre_parse_parameter == 4


@pytest.mark.parametrize(
    "parameter_class",
    [
        pytest.param(
            parameter_class_with_wavelength(),
            id="Wavelength parameters",
        ),
    ],
)
def test_wavelength_parameters(task_with_parameters, input_dataset_parts: tuple[Any, str]):
    """
    Given: a task with a parameter class that subclasses ParameterWavelengthMixin
    When: asking for a parameter that needs the wavelength
    Then: the correct value is returned
    """
    assert task_with_parameters.parameters.wavelength_parameter == 2
    assert task_with_parameters.parameters.interpolated_wavelength_parameter == 2.5


@pytest.mark.parametrize(
    "parameter_class, arm_id",
    [
        pytest.param(parameter_class_with_arm1(), "arm1", id="arm1"),
        pytest.param(parameter_class_with_arm2(), "arm2", id="arm2"),
    ],
)
def test_armid_parameters(task_with_parameters, arm_id, input_dataset_parts):
    """
    Given: A Parameter class that subclasses ParameterArmIdMixin
    When: Getting a parameter that depends on the arm_id
    Then: The correct value is returned
    """
    assert task_with_parameters.parameters.arm_parameter == arm_id


def test_mixins_error_with_no_arg():
    """
    Given: A Parameter class based on a ParameterMixin
    When: Instantiating that class withOUT an arg required by the mixin
    Then: An error is raised
    """
    with pytest.raises(TypeError):
        parameters = FilledWavelengthParameters(input_dataset_parameters={"foo": []})


@pytest.mark.parametrize(
    ("input_dataset_parts", "parameter_class"),
    [
        pytest.param(
            [
                (input_dataset_frames_part_factory(), Tag.input_dataset_parameters()),
                (input_dataset_frames_part_factory(), Tag.input_dataset_parameters()),
            ],
            parameter_class_with_obs_ip_start_time(),
            id="two_param_docs",
        ),
    ],
)
def test_multiple_input_dataset_parameter_parts(
    request, input_dataset_parts: list[tuple[Any, str]], parameter_class
):
    """
    Given: a task with multiple tagged input dataset parameter docs
    When: initializing the parameter base
    Then: an error is raised
    """
    with pytest.raises(ValueError, match="more than one parameter file"):
        request.getfixturevalue("task_with_parameters")
