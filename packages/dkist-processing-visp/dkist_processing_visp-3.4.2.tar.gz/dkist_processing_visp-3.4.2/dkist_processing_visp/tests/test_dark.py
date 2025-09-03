import json
from functools import partial

import numpy as np
import pytest
from astropy.io import fits
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.tags import Tag

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.tasks.dark import DarkCalibration
from dkist_processing_visp.tests.conftest import VispConstantsDb
from dkist_processing_visp.tests.conftest import VispInputDatasetParameterValues
from dkist_processing_visp.tests.conftest import write_frames_to_task
from dkist_processing_visp.tests.header_models import VispHeadersInputDarkFrames


class VispHeadersDarksWithNumExp(VispHeadersInputDarkFrames):
    def __init__(self, *args, num_exp_per_fpa: int, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_constant_key("CAM__014", num_exp_per_fpa)


def make_dark_array_data(
    dataframe: VispHeadersDarksWithNumExp, readout_exp_time: float, beam_border: int
):
    array_shape = dataframe.array_shape
    data = np.zeros(array_shape)

    data[0, :beam_border, :] = 1 * readout_exp_time  # Beam 1
    data[0, beam_border:, :] = 2 * readout_exp_time  # Beam 2

    return data


def write_darks_to_task(
    task,
    readout_exp_time: float,
    num_raw_per_fpa: int,
    num_frames: int,
    data_shape: tuple[int, int],
    beam_border: int,
):
    array_shape = (1, *data_shape)
    dataset = VispHeadersDarksWithNumExp(
        array_shape=array_shape,
        time_delta=10.0,
        readout_exp_time=readout_exp_time,
        num_modstates=num_frames,
        num_exp_per_fpa=num_raw_per_fpa,
    )

    data_func = partial(
        make_dark_array_data, readout_exp_time=readout_exp_time, beam_border=beam_border
    )
    num_written_frames = write_frames_to_task(
        task=task,
        frame_generator=dataset,
        extra_tags=[
            VispTag.input(),
            VispTag.task_dark(),
            VispTag.readout_exp_time(readout_exp_time),
        ],
        data_func=data_func,
    )
    return num_written_frames


@pytest.fixture(scope="function")
def dark_calibration_task(tmp_path, init_visp_constants_db, recipe_run_id):
    readout_exp_times = [0.02, 2.0, 200.0]
    constants_db = VispConstantsDb(
        NON_DARK_TASK_READOUT_EXP_TIMES=tuple(readout_exp_times),
    )
    init_visp_constants_db(recipe_run_id, constants_db)
    with DarkCalibration(
        recipe_run_id=recipe_run_id, workflow_name="dark_calibration", workflow_version="VX.Y"
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            yield task, readout_exp_times

        except:
            raise

        finally:
            task._purge()


def test_dark_calibration_task(
    dark_calibration_task, assign_input_dataset_doc_to_task, mocker, fake_gql_client
):
    """
    Given: A DarkCalibration task with multiple task exposure times
    When: Calling the task instance
    Then: Only one average intermediate dark frame exists for each exposure time and unused times are not made
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    # Given
    task, readout_exp_times = dark_calibration_task
    num_beam = 2
    num_raw_values = [3, 4, 5]
    unused_time = 100.0
    unused_num_raw = 6
    num_frames_per = 3
    data_shape = (20, 10)
    beam_border = data_shape[0] // 2
    assign_input_dataset_doc_to_task(
        task, VispInputDatasetParameterValues(visp_beam_border=beam_border)
    )
    for readout_exp_time, num_exp_per_fpa in zip(
        readout_exp_times + [unused_time], num_raw_values + [unused_num_raw]
    ):
        write_darks_to_task(
            task=task,
            readout_exp_time=readout_exp_time,
            num_raw_per_fpa=num_exp_per_fpa,
            num_frames=num_frames_per,
            data_shape=data_shape,
            beam_border=beam_border,
        )

    # When
    task()

    # Then
    for e, n in zip(readout_exp_times, num_raw_values):
        for b in range(num_beam):
            files = list(
                task.read(
                    tags=[
                        VispTag.task_dark(),
                        VispTag.intermediate(),
                        VispTag.frame(),
                        VispTag.beam(b + 1),
                        VispTag.readout_exp_time(e),
                    ]
                )
            )
            assert len(files) == 1
            expected = np.ones((data_shape[0] // 2, data_shape[1])) * (b + 1) * e / n
            hdul = fits.open(files[0])
            np.testing.assert_allclose(expected, hdul[0].data, rtol=1e-15)
            hdul.close()

    unused_time_read = task.read(
        tags=[
            VispTag.task_dark(),
            VispTag.intermediate(),
            VispTag.frame(),
            VispTag.readout_exp_time(unused_time),
        ]
    )
    assert len(list(unused_time_read)) == 0

    quality_files = task.read(tags=[Tag.quality("TASK_TYPES")])
    for file in quality_files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert data["total_frames"] == task.scratch.count_all(
                tags=[VispTag.input(), VispTag.frame(), VispTag.task_dark()]
            )
            assert data["frames_not_used"] == num_frames_per
