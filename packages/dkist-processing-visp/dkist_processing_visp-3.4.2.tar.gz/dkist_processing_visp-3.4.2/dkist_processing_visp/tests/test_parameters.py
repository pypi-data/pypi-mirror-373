from dataclasses import asdict
from dataclasses import dataclass

import numpy as np
import pytest
from hypothesis import HealthCheck
from hypothesis import example
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st

from dkist_processing_visp.models.parameters import VispParameters
from dkist_processing_visp.models.parameters import VispParsingParameters
from dkist_processing_visp.tasks.visp_base import VispTaskBase
from dkist_processing_visp.tests.conftest import VispConstantsDb
from dkist_processing_visp.tests.conftest import VispInputDatasetParameterValues

# The property names of all parameters on `VispParsingParameters`
PARSE_PARAMETER_NAMES = [
    k for k, v in vars(VispParsingParameters).items() if isinstance(v, property)
]


@pytest.fixture(scope="function")
def basic_science_task_with_parameter_mixin(
    recipe_run_id,
    assign_input_dataset_doc_to_task,
    init_visp_constants_db,
    testing_obs_ip_start_time,
):
    def make_task(
        parameters_part: dataclass,
        parameter_class=VispParameters,
        obs_ip_start_time=testing_obs_ip_start_time,
    ):
        class Task(VispTaskBase):
            def run(self): ...

        init_visp_constants_db(recipe_run_id, VispConstantsDb())
        task = Task(
            recipe_run_id=recipe_run_id,
            workflow_name="parse_visp_input_data",
            workflow_version="VX.Y",
        )
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            assign_input_dataset_doc_to_task(
                task,
                parameters_part,
                parameter_class=parameter_class,
                obs_ip_start_time=obs_ip_start_time,
            )
            yield task, parameters_part
        except:
            raise
        finally:
            task._purge()

    return make_task


def test_non_wave_parameters(basic_science_task_with_parameter_mixin):
    """
    Given: A Science task with the parameter mixin
    When: Accessing properties for parameters that do not depend on wavelength
    Then: The correct value is returned
    """
    task, expected = next(
        basic_science_task_with_parameter_mixin(VispInputDatasetParameterValues())
    )
    task_param_attr = task.parameters
    for pn, pv in asdict(expected).items():
        property_name = pn.removeprefix("visp_")
        if (
            type(pv) is not dict and property_name not in PARSE_PARAMETER_NAMES
        ):  # Don't test wavelength dependent parameters
            assert getattr(task_param_attr, property_name) == pv


def test_parse_parameters(basic_science_task_with_parameter_mixin):
    """
    Given: A Science task with Parsing parameters
    When: Accessing properties for Parse parameters
    Then: The correct value is returned
    """
    task, expected = next(
        basic_science_task_with_parameter_mixin(
            VispInputDatasetParameterValues(),
            parameter_class=VispParsingParameters,
            obs_ip_start_time=None,
        )
    )
    task_param_attr = task.parameters
    for pn, pv in asdict(expected).items():
        property_name = pn.removeprefix("visp_")
        if property_name in PARSE_PARAMETER_NAMES and type(pv) is not dict:
            assert getattr(task_param_attr, property_name) == pv


@given(wave=st.floats(min_value=500.0, max_value=2000.0))
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@example(wave=492.5)
def test_wave_parameters(basic_science_task_with_parameter_mixin, wave):
    """
    Given: A Science task with the paramter mixin
    When: Accessing properties for parameters that depend on wavelength
    Then: The correct value is returned
    """
    task, expected = next(
        basic_science_task_with_parameter_mixin(VispInputDatasetParameterValues())
    )
    task_param_attr = task.parameters
    task_param_attr._wavelength = wave
    pwaves = np.array(expected.visp_solar_zone_normalization_percentile.wavelength)
    midpoints = 0.5 * (pwaves[1:] + pwaves[:-1])
    idx = np.sum(midpoints < wave)
    for pn, pv in asdict(expected).items():
        property_name = pn.removeprefix("visp_")
        if type(pv) is dict and property_name not in PARSE_PARAMETER_NAMES:
            assert getattr(task_param_attr, property_name) == pv["values"][idx]
