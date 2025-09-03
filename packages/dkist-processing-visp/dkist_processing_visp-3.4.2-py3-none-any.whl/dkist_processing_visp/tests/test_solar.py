import json
from functools import partial
from typing import Callable

import numpy as np
import pytest
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.models.tags import Tag

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.tasks.solar import SolarCalibration
from dkist_processing_visp.tests.conftest import VispConstantsDb
from dkist_processing_visp.tests.conftest import VispInputDatasetParameterValues
from dkist_processing_visp.tests.conftest import tag_on_modstate
from dkist_processing_visp.tests.conftest import write_frames_to_task
from dkist_processing_visp.tests.conftest import write_intermediate_background_to_task
from dkist_processing_visp.tests.conftest import write_intermediate_darks_to_task
from dkist_processing_visp.tests.conftest import write_intermediate_geometric_to_task
from dkist_processing_visp.tests.conftest import write_intermediate_lamp_to_task
from dkist_processing_visp.tests.header_models import VispHeadersInputSolarGainFrames


def lamp_signal_func(beam: int, modstate: int):
    return 10 * beam * modstate


def write_full_set_of_intermediate_lamp_cals_to_task(
    task,
    data_shape: tuple[int, int],
    num_modstates: int,
    lamp_signal_func: Callable[[int, int], float] = lamp_signal_func,
):
    for beam in [1, 2]:
        for modstate in range(1, num_modstates + 1):
            lamp_signal = lamp_signal_func(beam, modstate)
            write_intermediate_lamp_to_task(
                task=task,
                lamp_signal=lamp_signal,
                beam=beam,
                modstate=modstate,
                data_shape=data_shape,
            )


def make_solar_input_array_data(
    frame: VispHeadersInputSolarGainFrames,
    dark_signal: float,
    lamp_signal_func: Callable[[int, int], float] = lamp_signal_func,
):
    data_shape = frame.array_shape[1:]
    beam_shape = (data_shape[0] // 2, data_shape[1])
    modstate = frame.current_modstate("")  # Weird signature due to key_function
    num_raw_per_fpa = frame.header()["CAM__014"]

    beam_list = []
    for beam in [1, 2]:
        true_gain = np.ones(beam_shape) + modstate + beam
        true_solar_signal = np.arange(1, beam_shape[0] + 1) / 5
        true_solar_gain = true_gain * true_solar_signal[:, None]
        lamp_signal = lamp_signal_func(beam, modstate)
        raw_beam = (true_solar_gain * lamp_signal) + dark_signal
        beam_list.append(raw_beam)

    raw_solar = np.concatenate(beam_list) * num_raw_per_fpa
    return raw_solar


def write_input_solar_gains_to_task(
    task,
    data_shape: tuple[int, int],
    dark_signal: float,
    readout_exp_time: float,
    num_modstates: int,
    lamp_signal_func: Callable[[int, int], float] = lamp_signal_func,
):
    array_shape = (1, *data_shape)
    dataset = VispHeadersInputSolarGainFrames(
        array_shape=array_shape,
        time_delta=10,
        num_modstates=num_modstates,
    )
    data_func = partial(
        make_solar_input_array_data, dark_signal=dark_signal, lamp_signal_func=lamp_signal_func
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


@pytest.fixture(scope="function")
def solar_gain_task(
    tmp_path,
    recipe_run_id,
    init_visp_constants_db,
):
    number_of_modstates = 3
    readout_exp_time = 40.0
    constants_db = VispConstantsDb(
        NUM_MODSTATES=number_of_modstates, SOLAR_READOUT_EXP_TIMES=(readout_exp_time,)
    )
    init_visp_constants_db(recipe_run_id, constants_db)
    with SolarCalibration(
        recipe_run_id=recipe_run_id, workflow_name="geometric_calibration", workflow_version="VX.Y"
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )

            yield task, readout_exp_time, number_of_modstates
        except:
            raise
        finally:
            task._purge()


@pytest.mark.parametrize(
    "background_on",
    [pytest.param(True, id="Background on"), pytest.param(False, id="Background off")],
)
def test_solar_gain_task(
    solar_gain_task, background_on, assign_input_dataset_doc_to_task, mocker, fake_gql_client
):
    """
    Given: A set of raw solar gain images and necessary intermediate calibrations
    When: Running the solargain task
    Then: The task completes and the outputs are correct
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )

    # It's way too hard to make data for a unit test that will get through the line zones calculation.
    # Leave that for grogu.
    mocker.patch(
        "dkist_processing_visp.tasks.solar.SolarCalibration.compute_line_zones",
        return_value=[(4, 7)],
    )

    task, readout_exp_time, num_modstates = solar_gain_task
    dark_signal = 3.0
    input_shape = (20, 10)
    intermediate_shape = (10, 10)
    beam_border = input_shape[0] // 2
    assign_input_dataset_doc_to_task(
        task,
        VispInputDatasetParameterValues(
            visp_background_on=background_on, visp_beam_border=beam_border
        ),
    )
    write_intermediate_darks_to_task(
        task=task,
        dark_signal=dark_signal,
        readout_exp_time=readout_exp_time,
        data_shape=intermediate_shape,
    )
    if background_on:
        write_intermediate_background_to_task(
            task=task, background_signal=0.0, data_shape=intermediate_shape
        )
    write_full_set_of_intermediate_lamp_cals_to_task(
        task=task, data_shape=intermediate_shape, num_modstates=num_modstates
    )
    write_intermediate_geometric_to_task(
        task=task, num_modstates=num_modstates, data_shape=intermediate_shape
    )
    write_input_solar_gains_to_task(
        task=task,
        data_shape=input_shape,
        dark_signal=dark_signal,
        readout_exp_time=readout_exp_time,
        num_modstates=num_modstates,
    )

    task()
    for beam in range(1, task.constants.num_beams + 1):
        equalization_flux = np.nanmedian(
            [
                np.ones(intermediate_shape)
                * (1 + beam + m)
                * (10 * beam * m)
                * np.nanpercentile(
                    np.arange(1, 11) / 5,
                    task.parameters.solar_characteristic_spatial_normalization_percentile,
                )
                for m in range(1, task.constants.num_modstates + 1)
            ],
            axis=0,
        )

        for modstate in range(1, task.constants.num_modstates + 1):
            # Gains aren't normalized so their expected value is weird. This expression comes from the math applied above. Sorry.
            raw = (
                np.ones(intermediate_shape)
                * (1 + beam + modstate)
                * (10 * beam * modstate)
                * np.mean(np.arange(1, 11) / 5)
            )
            expected = raw * equalization_flux / np.nanmedian(raw)
            solar_gain = next(
                task.read(
                    tags=[
                        VispTag.intermediate_frame(beam=beam, modstate=modstate),
                        VispTag.task_solar_gain(),
                    ],
                    decoder=fits_array_decoder,
                )
            )
            np.testing.assert_allclose(expected, solar_gain)

    quality_files = task.read(tags=[Tag.quality("TASK_TYPES")])
    for file in quality_files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert data["total_frames"] == task.scratch.count_all(
                tags=[VispTag.input(), VispTag.frame(), VispTag.task_solar_gain()]
            )


def test_line_zones(solar_gain_task):
    """
    Given: A spectrum with some absorption lines
    When: Computing zones around the lines
    Then: Correct results are returned
    """

    # This is here because we mocked it out in the solar gain task test above
    # NOTE that it does not test for removal of overlapping regions
    def gaussian(x, amp, mu, sig):
        return amp * np.exp(-np.power(x - mu, 2.0) / (2 * np.power(sig, 2.0)))

    spec = np.ones(1000) * 100
    x = np.arange(1000.0)
    expected = []
    for m, s in zip([100.0, 300.0, 700], [10.0, 20.0, 5.0]):
        spec -= gaussian(x, 40, m, s)
        hwhm = s * 2.355 / 2
        expected.append((np.floor(m - hwhm).astype(int), np.ceil(m + hwhm).astype(int)))

    task = solar_gain_task[0]

    zones = task.compute_line_zones(spec[:, None], bg_order=0, rel_height=0.5)
    assert zones == expected


def test_identify_overlapping_zones(solar_gain_task):
    """
    Given: A list of zone borders that contain overlapping zones
    When: Identifying zones that overlap
    Then: The smaller of the overlapping zones are identified for removal
    """
    rips = np.array([100, 110, 220, 200])
    lips = np.array([150, 120, 230, 250])

    task = solar_gain_task[0]

    idx_to_remove = task.identify_overlapping_zones(rips, lips)
    assert idx_to_remove == [1, 2]
