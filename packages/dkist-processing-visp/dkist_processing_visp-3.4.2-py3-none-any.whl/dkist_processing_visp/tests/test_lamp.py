import json
from functools import partial

import numpy as np
import pytest
from astropy.io import fits
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.tags import Tag

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.tasks.lamp import LampCalibration
from dkist_processing_visp.tests.conftest import VispConstantsDb
from dkist_processing_visp.tests.conftest import VispInputDatasetParameterValues
from dkist_processing_visp.tests.conftest import tag_on_modstate
from dkist_processing_visp.tests.conftest import write_frames_to_task
from dkist_processing_visp.tests.conftest import write_intermediate_darks_to_task
from dkist_processing_visp.tests.header_models import VispHeadersInputLampGainFrames

RNG = np.random.default_rng()


def make_lamp_array_data(
    frame: VispHeadersInputLampGainFrames, dark_signal: float, beam_border: int
):
    num_raw_frames_per_fpa = frame.header()["CAM__014"]
    data = np.zeros(frame.array_shape)
    data[0, :beam_border, :] = (1.1 + dark_signal) * num_raw_frames_per_fpa
    data[0, beam_border:, :] = (1.2 + dark_signal) * num_raw_frames_per_fpa

    return data


def write_lamp_inputs_to_task(
    task,
    dark_signal: float,
    readout_exp_time: float,
    num_modstates: int,
    data_shape: tuple[int, int],
):
    beam_border = task.parameters.beam_border
    array_shape = (1, *data_shape)

    # These images are for two combined beams
    dataset = VispHeadersInputLampGainFrames(
        array_shape=array_shape,
        time_delta=10,
        num_modstates=num_modstates,
    )

    data_func = partial(make_lamp_array_data, dark_signal=dark_signal, beam_border=beam_border)
    write_frames_to_task(
        task=task,
        frame_generator=dataset,
        extra_tags=[
            VispTag.input(),
            VispTag.task_lamp_gain(),
            VispTag.readout_exp_time(readout_exp_time),
        ],
        tag_func=tag_on_modstate,
        data_func=data_func,
    )


@pytest.fixture(scope="function")
def lamp_calibration_task(
    tmp_path,
    recipe_run_id,
    init_visp_constants_db,
):
    num_modstates = 2
    readout_exp_time = 20.0
    constants_db = VispConstantsDb(
        NUM_MODSTATES=num_modstates, LAMP_READOUT_EXP_TIMES=(readout_exp_time,)
    )
    init_visp_constants_db(recipe_run_id, constants_db)
    with LampCalibration(
        recipe_run_id=recipe_run_id, workflow_name="lamp_gain_calibration", workflow_version="VX.Y"
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )

            yield task, num_modstates, readout_exp_time

        except:
            raise

        finally:
            task._purge()


def test_lamp_calibration_task(
    lamp_calibration_task, assign_input_dataset_doc_to_task, mocker, fake_gql_client
):
    """
    Given: A LampCalibration task
    When: Calling the task instance
    Then: The correct number of output lamp gain frames exists, and are tagged correctly
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    # Given
    task, num_modstates, readout_exp_time = lamp_calibration_task
    input_shape = (20, 10)
    intermediate_shape = (10, 10)
    dark_signal = 3.0
    beam_border = input_shape[0] // 2
    assign_input_dataset_doc_to_task(
        task, VispInputDatasetParameterValues(visp_beam_border=beam_border)
    )
    write_intermediate_darks_to_task(
        task=task,
        dark_signal=dark_signal,
        readout_exp_time=readout_exp_time,
        data_shape=intermediate_shape,
    )
    write_lamp_inputs_to_task(
        task=task,
        dark_signal=dark_signal,
        readout_exp_time=readout_exp_time,
        num_modstates=num_modstates,
        data_shape=input_shape,
    )

    # When
    task()

    # Then
    tags = [
        VispTag.task_lamp_gain(),
        VispTag.intermediate(),
    ]
    assert len(list(task.read(tags=tags))) == num_modstates * 2  # 2 from beams

    for i in range(num_modstates):
        for beam in [1, 2]:
            tags = [
                VispTag.task_lamp_gain(),
                VispTag.intermediate(),
                VispTag.modstate(i + 1),
                VispTag.beam(beam),
            ]
            files = list(task.read(tags=tags))
            assert len(files) == 1
            hdu = fits.open(files[0])[0]
            np.testing.assert_allclose(hdu.data, np.ones((10, 10)) * (1 + (0.1 * beam)))

    tags = [
        VispTag.task_lamp_gain(),
        VispTag.intermediate(),
    ]
    for filepath in task.read(tags=tags):
        assert filepath.exists()

    quality_files = task.read(tags=[Tag.quality("TASK_TYPES")])
    for file in quality_files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert data["total_frames"] == task.scratch.count_all(
                tags=[VispTag.input(), VispTag.frame(), VispTag.task_lamp_gain()]
            )
