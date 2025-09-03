import json
from functools import partial
from typing import Callable

import numpy as np
import pytest
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.models.tags import Tag
from dkist_processing_math import transform

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.tasks.geometric import GeometricCalibration
from dkist_processing_visp.tests.conftest import VispConstantsDb
from dkist_processing_visp.tests.conftest import VispInputDatasetParameterValues
from dkist_processing_visp.tests.conftest import tag_on_modstate
from dkist_processing_visp.tests.conftest import write_frames_to_task
from dkist_processing_visp.tests.conftest import write_intermediate_darks_to_task
from dkist_processing_visp.tests.header_models import VispHeadersInputLampGainFrames
from dkist_processing_visp.tests.header_models import VispHeadersInputSolarGainFrames


def make_solar_array_data(
    frame: VispHeadersInputSolarGainFrames,
    intermediate_shape: tuple[int, int],
    dark_signal: float,
    angles: np.ndarray,
    offsets: np.ndarray,
):
    modstate = frame.current_modstate("")  # Weird signature due to key_function
    num_raw_per_fpa = frame.header()["CAM__014"]

    beam_list = []
    for beam in [1, 2]:
        true_solar = 10 * (np.ones(intermediate_shape) + modstate + beam)
        translated_solar = next(
            transform.translate_arrays(
                arrays=true_solar, translation=offsets[beam - 1][modstate - 1]
            )
        )
        translated_solar[translated_solar == 0] = 10 * (modstate + beam + 1)

        # Hairlines
        translated_solar[:, 30] = 5.0
        translated_solar[:, 70] = 5.0
        distorted_solar = next(
            transform.rotate_arrays_about_point(arrays=translated_solar, angle=angles[beam - 1])
        )
        beam_list.append((distorted_solar + dark_signal) * num_raw_per_fpa)

    raw_solar = np.concatenate(beam_list)

    return raw_solar


def make_simple_darked_array_data(
    frame: VispHeadersInputSolarGainFrames | VispHeadersInputLampGainFrames,
    dark_signal: float,
    input_data_shape: tuple[int, int],
    beam_border: int,
):
    modstate = frame.current_modstate("")  # Weird signature due to key_function
    num_raw_per_fpa = frame.header()["CAM__014"]

    true_data = np.ones(input_data_shape) + modstate

    true_data[:beam_border, :] += 1  # Beam 1
    true_data[beam_border:, :] += 2  # Beam 2
    raw_data = (true_data + dark_signal) * num_raw_per_fpa

    return raw_data


def write_geometric_solar_inputs_to_task(
    task,
    num_modstates: int,
    readout_exp_time: float,
    data_shape: tuple[int, int],
    data_func: Callable,
):
    array_shape = (1, *data_shape)
    dataset = VispHeadersInputSolarGainFrames(
        array_shape=array_shape,
        time_delta=10,
        num_modstates=num_modstates,
        readout_exp_time=readout_exp_time,
    )
    write_frames_to_task(
        task=task,
        frame_generator=dataset,
        extra_tags=[
            VispTag.input(),
            VispTag.task_solar_gain(),
            VispTag.readout_exp_time(readout_exp_time),
        ],
        tag_func=tag_on_modstate,
        data_func=data_func,
    )


def make_lamp_array_data(
    frame: VispHeadersInputLampGainFrames,
    intermediate_shape: tuple[int, int],
    dark_signal: float,
    angles: np.ndarray,
    offsets: np.ndarray,
):
    modstate = frame.current_modstate("")  # Weird signature due to key_function
    num_raw_per_fpa = frame.header()["CAM__014"]

    beam_list = []
    for beam in [1, 2]:
        true_lamp = 10 * (np.ones(intermediate_shape) + modstate + beam)
        translated_lamp = next(
            transform.translate_arrays(
                arrays=true_lamp, translation=offsets[beam - 1][modstate - 1]
            )
        )
        translated_lamp[translated_lamp == 0] = 10 * (modstate + beam + 1)

        # Hairlines
        translated_lamp[:, 30] = 5.0
        translated_lamp[:, 70] = 5.0
        # Chop out part of the second hairline so the fitter has to skip over these pixels
        translated_lamp[5:9, 70] = 10 * (modstate + beam + 1)
        distorted_lamp = next(
            transform.rotate_arrays_about_point(arrays=translated_lamp, angle=angles[beam - 1])
        )
        beam_list.append((distorted_lamp + dark_signal) * num_raw_per_fpa)

    raw_lamp = np.concatenate(beam_list)

    return raw_lamp


def write_geometric_lamp_inputs_to_task(
    task,
    num_modstates: int,
    readout_exp_time: float,
    data_shape: tuple[int, int],
    data_func: Callable,
):
    array_shape = (1, *data_shape)
    dataset = VispHeadersInputLampGainFrames(
        array_shape=array_shape,
        time_delta=10,
        num_modstates=num_modstates,
        readout_exp_time=readout_exp_time,
    )

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
def geometric_calibration_task(tmp_path, recipe_run_id, init_visp_constants_db):
    number_of_modstates = 3
    solar_exp_time = 40.0
    lamp_exp_time = 20.0
    readout_exp_times = [lamp_exp_time, solar_exp_time]
    constants_db = VispConstantsDb(
        NUM_MODSTATES=number_of_modstates,
        SOLAR_READOUT_EXP_TIMES=(solar_exp_time,),
        LAMP_READOUT_EXP_TIMES=(lamp_exp_time,),
    )
    init_visp_constants_db(recipe_run_id, constants_db)
    with GeometricCalibration(
        recipe_run_id=recipe_run_id, workflow_name="geometric_calibration", workflow_version="VX.Y"
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )

            yield task, readout_exp_times, number_of_modstates
        except:
            raise
        finally:
            task._purge()


def test_geometric_task(
    geometric_calibration_task, assign_input_dataset_doc_to_task, mocker, fake_gql_client
):
    """
    Given: A set of raw solar gain images and necessary intermediate calibrations
    When: Running the geometric task
    Then: The damn thing runs and makes outputs that at least are the right type
    """
    # This test makes data that look enough like real data that all of the feature detection stuff at least runs
    # through (mostly this is an issue for the angle calculation). It would be great to contrive data that
    # produce a geometric calibration with real numbers that can be checked, but for now we'll rely on the grogu
    # tests for that. In other words, this fixture just tests if the machinery of the task completes and some object
    # (ANY object) is written correctly.
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task, readout_exp_times, num_modstates = geometric_calibration_task
    dark_signal = 3.0
    input_shape = (60, 100)
    intermediate_shape = (30, 100)
    angles = np.array([0.01, -0.01])
    offsets = np.zeros((2, num_modstates, 2))
    beam_border = input_shape[0] // 2
    assign_input_dataset_doc_to_task(
        task, VispInputDatasetParameterValues(visp_beam_border=beam_border)
    )

    # Intermediate darks are needed for correction
    for readout_exp_time in readout_exp_times:
        write_intermediate_darks_to_task(
            task=task,
            dark_signal=dark_signal,
            readout_exp_time=readout_exp_time,
            data_shape=intermediate_shape,
        )

    # Write input lamp and solar data
    lamp_data_func = partial(
        make_lamp_array_data,
        intermediate_shape=intermediate_shape,
        dark_signal=dark_signal,
        angles=angles,
        offsets=offsets,
    )
    write_geometric_lamp_inputs_to_task(
        task=task,
        num_modstates=num_modstates,
        readout_exp_time=readout_exp_times[0],
        data_shape=input_shape,
        data_func=lamp_data_func,
    )

    solar_data_func = partial(
        make_solar_array_data,
        intermediate_shape=intermediate_shape,
        dark_signal=dark_signal,
        angles=angles,
        offsets=offsets,
    )
    write_geometric_solar_inputs_to_task(
        task=task,
        num_modstates=num_modstates,
        readout_exp_time=readout_exp_times[1],
        data_shape=input_shape,
        data_func=solar_data_func,
    )

    task()
    for beam in range(1, task.constants.num_beams + 1):
        angle_array = next(
            task.read(
                tags=[VispTag.intermediate_frame(beam=beam), VispTag.task_geometric_angle()],
                decoder=fits_array_decoder,
            )
        )
        assert type(angle_array[0]) is np.float64
        spec_shift_array = next(
            task.read(
                tags=[
                    VispTag.intermediate_frame(beam=beam),
                    VispTag.task_geometric_spectral_shifts(),
                ],
                decoder=fits_array_decoder,
            )
        )
        assert spec_shift_array.shape == (100,)
        for modstate in range(1, task.constants.num_modstates + 1):
            array = next(
                task.read(
                    tags=[
                        VispTag.intermediate_frame(beam=beam, modstate=modstate),
                        VispTag.task_geometric_offset(),
                    ],
                    decoder=fits_array_decoder,
                )
            )
            assert array.shape == (2,)

    quality_files = task.read(tags=[Tag.quality("TASK_TYPES")])
    for file in quality_files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert data["total_frames"] == task.scratch.count_all(
                tags=[VispTag.input(), VispTag.frame(), VispTag.task_solar_gain()]
            )


def test_basic_corrections(geometric_calibration_task, assign_input_dataset_doc_to_task):
    """
    Given: A set of raw solar gain images and necessary intermediate calibrations
    When: Doing basic dark and lamp gain corrections
    Then: The corrections are applied correctly
    """
    task, readout_exp_times, num_modstates = geometric_calibration_task
    intermediate_shape = (10, 10)
    input_shape = (20, 10)
    dark_signal = 3.0
    beam_border = input_shape[0] // 2
    assign_input_dataset_doc_to_task(
        task, VispInputDatasetParameterValues(visp_beam_border=beam_border)
    )

    # Intermediate darks needed for corrections
    for readout_exp_time in readout_exp_times:
        write_intermediate_darks_to_task(
            task=task,
            dark_signal=dark_signal,
            readout_exp_time=readout_exp_time,
            data_shape=intermediate_shape,
        )

    # Write a crazy dark with the wrong readout_exp_time, just to make sure it doesn't get used
    write_intermediate_darks_to_task(
        task=task,
        dark_signal=1e6,
        readout_exp_time=readout_exp_times[0] ** 2,
        data_shape=intermediate_shape,
    )

    simple_data_func = partial(
        make_simple_darked_array_data,
        dark_signal=dark_signal,
        input_data_shape=input_shape,
        beam_border=task.parameters.beam_border,
    )
    write_geometric_lamp_inputs_to_task(
        task=task,
        num_modstates=num_modstates,
        readout_exp_time=readout_exp_times[0],
        data_shape=input_shape,
        data_func=simple_data_func,
    )

    write_geometric_solar_inputs_to_task(
        task=task,
        num_modstates=num_modstates,
        readout_exp_time=readout_exp_times[1],
        data_shape=input_shape,
        data_func=simple_data_func,
    )

    task.do_basic_corrections()
    for beam in range(1, task.constants.num_beams + 1):
        for modstate in range(1, task.constants.num_modstates + 1):
            expected = np.ones((10, 10)) + modstate + beam
            solar_array = task.basic_corrected_solar_data(beam=beam, modstate=modstate)
            lamp_array = task.basic_corrected_lamp_data(beam=beam, modstate=modstate)
            np.testing.assert_equal(expected, solar_array)
            np.testing.assert_equal(expected, lamp_array)
