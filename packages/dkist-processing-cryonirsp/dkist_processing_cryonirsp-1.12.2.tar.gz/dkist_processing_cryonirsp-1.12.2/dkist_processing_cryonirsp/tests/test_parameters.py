from dataclasses import asdict
from typing import Any

import numpy as np
import pytest
from astropy.units import Quantity
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.array import array_decoder
from dkist_processing_common.models.input_dataset import InputDatasetFilePointer
from hypothesis import HealthCheck
from hypothesis import example
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st
from pydantic import BaseModel

from dkist_processing_cryonirsp.models.parameters import CryonirspParameters
from dkist_processing_cryonirsp.models.parameters import CryonirspParsingParameters
from dkist_processing_cryonirsp.parsers.optical_density_filters import (
    ALLOWABLE_OPTICAL_DENSITY_FILTERS,
)
from dkist_processing_cryonirsp.tasks.cryonirsp_base import CryonirspTaskBase
from dkist_processing_cryonirsp.tests.conftest import CryonirspConstantsDb
from dkist_processing_cryonirsp.tests.conftest import TestingParameters
from dkist_processing_cryonirsp.tests.conftest import cryonirsp_testing_parameters_factory

# The property names of all parameters on `CryonirspParsingParameters`
PARSE_PARAMETER_NAMES = [
    k for k, v in vars(CryonirspParsingParameters).items() if isinstance(v, property)
]


@pytest.fixture(scope="function")
def basic_science_task_with_parameter_mixin(
    tmp_path,
    recipe_run_id,
    assign_input_dataset_doc_to_task,
    init_cryonirsp_constants_db,
    testing_obs_ip_start_time,
):
    def make_task(
        parameter_class=CryonirspParameters,
        arm_id: str = "SP",
        obs_ip_start_time: str = testing_obs_ip_start_time,
    ):
        class Task(CryonirspTaskBase):
            def run(self): ...

        init_cryonirsp_constants_db(recipe_run_id, CryonirspConstantsDb())
        with Task(
            recipe_run_id=recipe_run_id,
            workflow_name="parse_cryonirsp_input_data",
            workflow_version="VX.Y",
        ) as task:
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=task.recipe_run_id
            )
            test_params = cryonirsp_testing_parameters_factory(task)
            param_dict = test_params()
            assign_input_dataset_doc_to_task(
                task,
                param_dict,
                parameter_class=parameter_class,
                arm_id=arm_id,
                obs_ip_start_time=obs_ip_start_time,
            )
            yield task, param_dict
            task._purge()

    return make_task


def _is_wavelength_param(param_value: Any) -> bool:
    return isinstance(param_value, dict) and "wavelength" in param_value


@given(wave=st.floats(min_value=800.0, max_value=2000.0))
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@example(wave=1082.7)
def test_filter_parameters(basic_science_task_with_parameter_mixin, wave):
    """
    Given: A Science task with the parameter mixin
    When: Accessing properties for the optical density filters
    Then: The correct value is returned
    """
    task, expected = next(basic_science_task_with_parameter_mixin())
    task_params = task.parameters
    task_params._wavelength = wave
    expected = {
        "_linearization_optical_density_filter_attenuation_g278": -1.64,
        "_linearization_optical_density_filter_attenuation_g358": -3.75,
        "_linearization_optical_density_filter_attenuation_g408": -4.26,
    }
    for param in expected:
        assert getattr(task_params, param) == expected[param]
    task._purge()


def _is_file_param(param_value: Any) -> bool:
    return isinstance(param_value, InputDatasetFilePointer)


def test_file_parameters(basic_science_task_with_parameter_mixin):
    """
    Given: A Science task with the parameter mixin
    When: Accessing parameters whose values are loaded from files
    Then: The correct value is returned

    This test exercises all aspects of file parameters from their names to the loading of values
    """
    task, test_params = next(basic_science_task_with_parameter_mixin())
    task_params = task.parameters
    # Iterate over the test parameters and check that each file param exists in the task parameters
    # we load the actual parameter from the task param object using only the param name
    for pn, pv in asdict(test_params).items():
        # We want to test only file parameters
        if _is_file_param(pv):
            # Get the parameter value the way the tasks do
            param_obj = task_params._find_most_recent_past_value(pn)
            actual = task_params._load_param_value_from_numpy_save(param_obj=param_obj)
            # Now get the expected value using the tag in the value from the testing params
            expected = next(task.read(tags=pv.file_pointer.tag, decoder=array_decoder))
            # Compare the actual and expected values
            assert np.array_equal(actual, expected)


def _is_arm_param(
    param_name: str,
    task_params: CryonirspParameters,
    testing_params: TestingParameters,
    single_arm_only: str | None = None,
):
    """
    Test if a parameter is an arm parameter.

    An arm parameter is one which is present in the task_param class with no arm suffix and is also
    present in the test_param class with suffixed forms only, one for each arm.
    This allows a non-arm-specific name to be used as a property in the parameters class which
    encapsulates the mechanism used to return the arm specific parameter value based on the arm in use.
    """
    # NB: param_name is assumed to have a prefix of "cryonirsp_"
    arm_suffixes = ["_sp", "_ci"] if single_arm_only is None else [f"_{single_arm_only}".casefold()]
    suffix = param_name[-3:]
    if suffix not in arm_suffixes:
        return False
    param_name_no_suffix = param_name[:-3]
    param_names_with_suffixes = [f"{param_name_no_suffix}{suffix}" for suffix in arm_suffixes]
    suffixed_names_exist = all(
        [hasattr(testing_params, pname) for pname in param_names_with_suffixes]
    )
    generic_param_name = param_name_no_suffix.removeprefix("cryonirsp_")
    return hasattr(task_params, generic_param_name) and suffixed_names_exist


@pytest.mark.parametrize("arm_id", ["SP", "CI"])
def test_arm_parameters(basic_science_task_with_parameter_mixin, arm_id):
    """
    Given: A Science task with the parameter mixin
    When: Accessing parameters that are "arm" parameters
    Then: The correct value is returned

    This test exercises all aspects of arm parameters from their names to the loading of values,
    which includes exercising the method _find_parameter_for_arm
    """
    # An arm parameter is one which is present in the param class with no arm suffix
    # and is also present in the testing param class with both suffix forms
    task, test_params = next(basic_science_task_with_parameter_mixin(arm_id=arm_id))
    task_params = task.parameters
    # Iterate over the test parameters
    for pn, pv in asdict(test_params).items():
        suffix = f"_{arm_id}".casefold()
        if _is_arm_param(pn, task_params, test_params, single_arm_only=arm_id):
            generic_param_name = pn.removeprefix("cryonirsp_").removesuffix(suffix)
            actual = getattr(task_params, generic_param_name)
            expected = getattr(test_params, pn)
            if isinstance(expected, InputDatasetFilePointer):
                expected_array = task_params._load_param_value_from_numpy_save(param_obj=expected)
                assert np.array_equal(expected_array, actual)
            elif isinstance(actual, np.ndarray):
                assert expected == actual.tolist()
            else:
                assert expected == actual


def test_parameters(basic_science_task_with_parameter_mixin):
    """
    Given: A Science task with the parameter mixin
    When: Accessing properties for parameters that are not wavelength, file or generic parameters
    Then: The correct value is returned
    """
    task, test_params = next(basic_science_task_with_parameter_mixin())
    task_params = task.parameters
    for pn, pv in asdict(test_params).items():
        parameter_name = pn.removeprefix("cryonirsp_")
        if (
            _is_file_param(pv)
            or _is_wavelength_param(pv)
            or _is_arm_param(pn, task_params, test_params)
            or parameter_name in PARSE_PARAMETER_NAMES
        ):
            continue

        accessed_parameter_value = getattr(task_params, parameter_name)
        if isinstance(accessed_parameter_value, Quantity):
            assert pv == accessed_parameter_value.value
        elif isinstance(accessed_parameter_value, BaseModel):
            assert accessed_parameter_value.model_dump() == pv
        else:
            assert pv == getattr(task_params, parameter_name)


def test_parse_parameters(basic_science_task_with_parameter_mixin):
    """
    Given: A Science task with ParsingParameters
    When: Accessing properties for the parsing parameters
    Then: The correct value is returned
    """
    task, test_params = next(
        basic_science_task_with_parameter_mixin(
            parameter_class=CryonirspParsingParameters,
            obs_ip_start_time=None,
        )
    )
    task_param_attr = task.parameters
    for pn, pv in asdict(test_params).items():
        property_name = pn.removeprefix("cryonirsp_")
        if property_name in PARSE_PARAMETER_NAMES and type(pv) is not dict:
            assert getattr(task_param_attr, property_name) == pv


@pytest.mark.parametrize("arm", [pytest.param("CI"), pytest.param("SP")])
def test_linearization_threshold_parameters(
    basic_science_task_with_parameter_mixin, arm, init_cryonirsp_constants_db
):
    """
    Given: A Science task with the parameter mixin
    When: Accessing properties for the linearization thresholds
    Then: The correct type is returned
    """
    task, _ = next(basic_science_task_with_parameter_mixin())
    recipe_run_id = task.recipe_run_id
    init_cryonirsp_constants_db(recipe_run_id, CryonirspConstantsDb(ARM_ID=arm))
    linearization_threshold_array = task.parameters.linearization_thresholds

    assert linearization_threshold_array.dtype == np.float32


def test_optical_density_filter_names(basic_science_task_with_parameter_mixin):
    task, _ = next(basic_science_task_with_parameter_mixin())
    # List of filter attenuation parameters defined in CryonirspParameters:
    defined_filter_params = {
        item[-4:].upper()
        for item in dir(task.parameters)
        if item.startswith("_linearization_optical_density_filter_attenuation_")
    }
    # List of filters in the filter map:
    filter_map_params = {k for k in task.parameters.linearization_filter_attenuation_dict.keys()}
    # Make sure all filter parameters match the allowable list
    assert not defined_filter_params.symmetric_difference(ALLOWABLE_OPTICAL_DENSITY_FILTERS)
    # Make sure all filter map keys match the allowable list
    assert not filter_map_params.symmetric_difference(ALLOWABLE_OPTICAL_DENSITY_FILTERS)
