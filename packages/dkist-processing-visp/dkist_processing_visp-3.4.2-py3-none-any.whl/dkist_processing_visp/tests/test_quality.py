import json

import numpy as np
import pytest
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.models.task_name import TaskName

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.tasks.quality_metrics import VispL0QualityMetrics
from dkist_processing_visp.tasks.quality_metrics import VispL1QualityMetrics
from dkist_processing_visp.tests.conftest import VispConstantsDb
from dkist_processing_visp.tests.conftest import write_calibrated_frames_to_task
from dkist_processing_visp.tests.header_models import VispHeaders


@pytest.fixture
def visp_l0_quality_task(recipe_run_id, num_modstates, init_visp_constants_db, tmp_path):
    constants = VispConstantsDb(
        NUM_MODSTATES=num_modstates,
        POLARIMETER_MODE="observe_polarimetric" if num_modstates > 1 else "observe_intensity",
    )
    init_visp_constants_db(recipe_run_id, constants)

    with VispL0QualityMetrics(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)

        yield task
        task._purge()


@pytest.fixture()
def l0_quality_task_types() -> list[str]:
    # The tasks types we want to build l0 metrics for
    return [TaskName.lamp_gain.value, TaskName.dark.value]


@pytest.fixture()
def dataset_task_types(l0_quality_task_types) -> list[str]:
    # The task types that exist in the dataset. I.e., a larger set than we want to build metrics for.
    return l0_quality_task_types + [TaskName.solar_gain.value, TaskName.observe.value]


@pytest.fixture
def write_l0_task_frames_to_task(num_modstates, dataset_task_types):
    array_shape = (1, 4, 4)
    data = np.ones(array_shape)

    def writer(task):
        for task_type in dataset_task_types:
            ds = VispHeaders(
                dataset_shape=(num_modstates,) + array_shape[-2:],
                array_shape=array_shape,
                file_schema="level0_spec214",
            )
            for modstate, frame in enumerate(ds, start=1):
                header = frame.header()
                task.write(
                    data=data,
                    header=header,
                    tags=[
                        VispTag.input(),
                        VispTag.frame(),
                        VispTag.task(task_type),
                        VispTag.modstate(modstate),
                    ],
                    encoder=fits_array_encoder,
                )

    return writer


@pytest.fixture(scope="function")
def visp_l1_quality_task(tmp_path, pol_mode, recipe_run_id, init_visp_constants_db):
    num_map_scans = 3
    num_raster_steps = 2
    num_stokes = 4
    if pol_mode == "observe_intensity":
        num_stokes = 1
    constants_db = VispConstantsDb(
        POLARIMETER_MODE=pol_mode,
        NUM_MAP_SCANS=num_map_scans,
        NUM_RASTER_STEPS=num_raster_steps,
    )
    init_visp_constants_db(recipe_run_id, constants_db)
    with VispL1QualityMetrics(
        recipe_run_id=recipe_run_id, workflow_name="science_calibration", workflow_version="VX.Y"
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)

        yield task, num_map_scans, num_raster_steps, num_stokes
        task._purge()


@pytest.mark.parametrize(
    "num_modstates", [pytest.param(4, id="polarimetric"), pytest.param(1, id="intensity")]
)
def test_l0_quality_task(
    visp_l0_quality_task, num_modstates, write_l0_task_frames_to_task, l0_quality_task_types
):
    """
    Given: A `VispL0QualityMetrics` task and some INPUT frames tagged with their task type and modstate
    When: Running the task
    Then: The expected L0 quality metric files exist
    """
    # NOTE: We rely on the unit tests in `*-common` to verify the correct format/data of the metric files
    task = visp_l0_quality_task
    write_l0_task_frames_to_task(task)

    task()

    task_metric_names = ["FRAME_RMS", "FRAME_AVERAGE"]
    for metric_name in task_metric_names:
        for modstate in range(1, num_modstates + 1):
            for task_type in l0_quality_task_types:
                tags = [VispTag.quality(metric_name), VispTag.quality_task(task_type)]
                if num_modstates > 1:
                    tags.append(VispTag.modstate(modstate))
                files = list(task.read(tags))
                assert len(files) == 1

    global_metric_names = ["DATASET_AVERAGE", "DATASET_RMS"]
    for metric_name in global_metric_names:
        files = list(task.read(tags=[VispTag.quality(metric_name)]))
        assert len(files) > 0


@pytest.mark.parametrize("pol_mode", ["observe_polarimetric", "observe_intensity"])
def test_l1_quality_task(visp_l1_quality_task, pol_mode, mocker, fake_gql_client):
    """
    Given: A VispL1QualityMetrics task
    When: Calling the task instance
    Then: A single sensitivity measurement and datetime is recorded for each map scan for each Stokes Q, U, and V,
            and a single noise measurement and datetime is recorded for L1 file for each Stokes Q, U, and V
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    # When
    task, num_maps, num_steps, num_stokes = visp_l1_quality_task
    write_calibrated_frames_to_task(
        task, num_maps=num_maps, num_steps=num_steps, data_shape=(10, 10), pol_mode=pol_mode
    )

    task()
    # Then
    num_map_scans = task.constants.num_map_scans
    num_steps = task.constants.num_raster_steps
    sensitivity_files = list(task.read(tags=[Tag.quality("SENSITIVITY")]))
    assert len(sensitivity_files) == num_stokes
    for file in sensitivity_files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            for time in range(len(data["x_values"])):
                assert type(data["x_values"][time]) == str
            for noise in range(len(data["y_values"])):
                assert type(data["y_values"][noise]) == float
            assert len(data["x_values"]) == len(data["y_values"]) == num_map_scans

    noise_files = list(task.read(tags=[Tag.quality("NOISE")]))
    assert len(noise_files) == num_stokes
    for file in noise_files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            for time in range(len(data["x_values"])):
                assert type(data["x_values"][time]) == str
            for noise in range(len(data["y_values"])):
                assert type(data["y_values"][noise]) == float
            assert len(data["x_values"]) == len(data["y_values"]) == num_map_scans * num_steps
