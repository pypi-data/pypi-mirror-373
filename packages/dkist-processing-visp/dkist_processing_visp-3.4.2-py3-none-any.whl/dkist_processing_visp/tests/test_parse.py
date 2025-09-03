import pytest
from dkist_data_simulator.dataset import key_function
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.tags import Tag

from dkist_processing_visp.models.parameters import VispParsingParameters
from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.tasks.parse import ParseL0VispInputData
from dkist_processing_visp.tests.conftest import VispInputDatasetParameterValues
from dkist_processing_visp.tests.conftest import write_frames_to_task
from dkist_processing_visp.tests.header_models import VispHeadersInputDarkFrames
from dkist_processing_visp.tests.header_models import VispHeadersInputLampGainFrames
from dkist_processing_visp.tests.header_models import VispHeadersInputPolcalDarkFrames
from dkist_processing_visp.tests.header_models import VispHeadersInputPolcalFrames
from dkist_processing_visp.tests.header_models import VispHeadersInputPolcalGainFrames
from dkist_processing_visp.tests.header_models import VispHeadersInputSolarGainFrames
from dkist_processing_visp.tests.header_models import VispHeadersValidObserveFrames


@pytest.fixture(scope="session")
def lamp_readout_exp_time() -> float:
    return 10.0


@pytest.fixture(scope="session")
def solar_readout_exp_time() -> float:
    return 11.0


@pytest.fixture(scope="session")
def polcal_readout_exp_time() -> float:
    return 12.0


@pytest.fixture(scope="session")
def observe_readout_exp_times() -> list[float]:
    return [13.0, 130.0]


@pytest.fixture(scope="session")
def required_dark_readout_exp_times(
    lamp_readout_exp_time,
    solar_readout_exp_time,
    observe_readout_exp_times,
) -> list[float]:
    return [
        lamp_readout_exp_time,
        solar_readout_exp_time,
    ] + observe_readout_exp_times


@pytest.fixture(scope="session")
def dark_exp_time() -> float:
    return 99.0


@pytest.fixture(scope="session")
def lamp_exp_time() -> float:
    return 0.1


@pytest.fixture(scope="session")
def solar_exp_time() -> float:
    return 0.11


@pytest.fixture(scope="session")
def polcal_exp_time() -> float:
    return 0.12


@pytest.fixture(scope="session")
def observe_exp_times() -> list[float]:
    return [0.13, 1.3]


@pytest.fixture(scope="session")
def num_modstates() -> int:
    return 2


def write_input_dark_frames_to_task(
    task,
    readout_exp_time: float,
    exp_time: float,
    time_delta: float = 10.0,
    num_modstates: int = 2,
    data_shape: tuple[int, int] = (2, 2),
):
    array_shape = (1, *data_shape)
    dataset = VispHeadersInputDarkFrames(
        array_shape=array_shape,
        time_delta=time_delta,
        exp_time=exp_time,
        readout_exp_time=readout_exp_time,
        num_modstates=num_modstates,
    )

    num_written_frames = write_frames_to_task(
        task=task, frame_generator=dataset, extra_tags=[VispTag.input()]
    )
    return num_written_frames


def write_input_lamp_frames_to_task(
    task,
    readout_exp_time: float,
    exp_time: float,
    time_delta: float = 10.0,
    num_modstates: int = 2,
    data_shape: tuple[int, int] = (2, 2),
):
    array_shape = (1, *data_shape)
    dataset = VispHeadersInputLampGainFrames(
        array_shape=array_shape,
        time_delta=time_delta,
        exp_time=exp_time,
        readout_exp_time=readout_exp_time,
        num_modstates=num_modstates,
    )

    num_written_frames = write_frames_to_task(
        task=task, frame_generator=dataset, extra_tags=[VispTag.input()]
    )
    return num_written_frames


def write_input_solar_frames_to_task(
    task,
    readout_exp_time: float,
    exp_time: float,
    time_delta: float = 10.0,
    num_modstates: int = 2,
    data_shape: tuple[int, int] = (2, 2),
):
    array_shape = (1, *data_shape)
    dataset = VispHeadersInputSolarGainFrames(
        array_shape=array_shape,
        time_delta=time_delta,
        exp_time=exp_time,
        readout_exp_time=readout_exp_time,
        num_modstates=num_modstates,
    )

    num_written_frames = write_frames_to_task(
        task=task, frame_generator=dataset, extra_tags=[VispTag.input()]
    )
    return num_written_frames


def write_input_polcal_frames_to_task(
    task,
    readout_exp_time: float,
    exp_time: float,
    time_delta: float = 30.0,
    num_modstates: int = 2,
    data_shape: tuple[int, int] = (2, 2),
):
    array_shape = (1, *data_shape)
    dataset = VispHeadersInputPolcalFrames(
        array_shape=array_shape,
        time_delta=time_delta,
        exp_time=exp_time,
        readout_exp_time=readout_exp_time,
        num_modstates=num_modstates,
    )

    num_written_frames = write_frames_to_task(
        task=task, frame_generator=dataset, extra_tags=[VispTag.input()]
    )
    return num_written_frames


def write_input_polcal_dark_frames_to_task(
    task,
    readout_exp_time: float,
    exp_time: float,
    time_delta: float = 30.0,
    num_modstates: int = 2,
    data_shape: tuple[int, int] = (2, 2),
):
    array_shape = (1, *data_shape)
    dataset = VispHeadersInputPolcalDarkFrames(
        array_shape=array_shape,
        time_delta=time_delta,
        exp_time=exp_time,
        readout_exp_time=readout_exp_time,
        num_modstates=num_modstates,
    )

    num_written_frames = write_frames_to_task(
        task=task, frame_generator=dataset, extra_tags=[VispTag.input()]
    )
    return num_written_frames


def write_input_polcal_gain_frames_to_task(
    task,
    readout_exp_time: float,
    exp_time: float,
    time_delta: float = 30.0,
    num_modstates: int = 2,
    data_shape: tuple[int, int] = (2, 2),
):
    array_shape = (1, *data_shape)
    dataset = VispHeadersInputPolcalGainFrames(
        array_shape=array_shape,
        time_delta=time_delta,
        exp_time=exp_time,
        readout_exp_time=readout_exp_time,
        num_modstates=num_modstates,
    )

    num_written_frames = write_frames_to_task(
        task=task, frame_generator=dataset, extra_tags=[VispTag.input()]
    )
    return num_written_frames


def write_input_observe_frames_to_task(
    task,
    num_maps: int,
    num_steps: int,
    num_modstates: int,
    readout_exp_time: float,
    exp_time: float,
    time_delta: float = 10.0,
    data_shape: tuple[int, int] = (2, 2),
    obs_dataset_class=VispHeadersValidObserveFrames,
):
    array_shape = (1, *data_shape)
    dataset = obs_dataset_class(
        array_shape=array_shape,
        time_delta=time_delta,
        num_maps=num_maps,
        num_raster_steps=num_steps,
        num_modstates=num_modstates,
        exp_time=exp_time,
        readout_exp_time=readout_exp_time,
    )
    num_written_frames = write_frames_to_task(
        task=task, frame_generator=dataset, extra_tags=[VispTag.input()]
    )
    return num_written_frames


class VispHeadersMultiNumRasterSteps(VispHeadersValidObserveFrames):
    @key_function("VISP_010")
    def num_raster_steps(self, key: str) -> int:
        # Just do something to make it not the same for all frames
        return self.index % 2


class VispHeadersIncompleteFinalMap(VispHeadersValidObserveFrames):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, abort_last_step=True, **kwargs)


class VispHeadersIntensityObserveFrames(VispHeadersValidObserveFrames):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, polarimeter_mode="observe_intensity", **kwargs)


@pytest.fixture
def write_input_cal_frames_to_task(
    lamp_readout_exp_time,
    solar_readout_exp_time,
    polcal_readout_exp_time,
    required_dark_readout_exp_times,
    dark_exp_time,
    lamp_exp_time,
    solar_exp_time,
    polcal_exp_time,
    num_modstates,
):
    def write_frames_to_task(task):
        for readout_exp_time in required_dark_readout_exp_times:
            write_input_dark_frames_to_task(
                task=task,
                readout_exp_time=readout_exp_time,
                exp_time=dark_exp_time,
                num_modstates=num_modstates,
            )

        write_input_lamp_frames_to_task(
            task=task,
            readout_exp_time=lamp_readout_exp_time,
            exp_time=lamp_exp_time,
            num_modstates=num_modstates,
        )
        write_input_solar_frames_to_task(
            task=task,
            readout_exp_time=solar_readout_exp_time,
            exp_time=solar_exp_time,
            num_modstates=num_modstates,
        )
        write_input_polcal_frames_to_task(
            task=task,
            readout_exp_time=polcal_readout_exp_time,
            exp_time=polcal_exp_time,
            num_modstates=num_modstates,
        )
        write_input_polcal_dark_frames_to_task(
            task=task,
            readout_exp_time=polcal_readout_exp_time,
            exp_time=polcal_exp_time,
            num_modstates=num_modstates,
        )
        write_input_polcal_gain_frames_to_task(
            task,
            readout_exp_time=polcal_readout_exp_time,
            exp_time=polcal_exp_time,
            num_modstates=num_modstates,
        )

    return write_frames_to_task


@pytest.fixture
def parse_task_with_no_data(tmp_path, recipe_run_id, assign_input_dataset_doc_to_task):
    """You've got to populate the data in the actual test."""
    with ParseL0VispInputData(
        recipe_run_id=recipe_run_id,
        workflow_name="parse_visp_input_data",
        workflow_version="VX.Y",
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            assign_input_dataset_doc_to_task(
                task,
                VispInputDatasetParameterValues(),
                parameter_class=VispParsingParameters,
                obs_ip_start_time=None,
            )

            yield task
        except:
            raise
        finally:
            task._purge()


def test_parse_visp_input_data(
    parse_task_with_no_data,
    write_input_cal_frames_to_task,
    observe_readout_exp_times,
    observe_exp_times,
    num_modstates,
    mocker,
    fake_gql_client,
):
    """
    Given: A ParseVispInputData task
    When: Calling the task instance
    Then: All tagged files exist and individual task tags are applied
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task = parse_task_with_no_data
    write_input_cal_frames_to_task(task)
    for obs_readout_exp_time, obs_exp_time in zip(observe_readout_exp_times, observe_exp_times):
        write_input_observe_frames_to_task(
            task,
            num_maps=1,
            num_modstates=num_modstates,
            num_steps=3,
            readout_exp_time=obs_readout_exp_time,
            exp_time=obs_exp_time,
        )

    # When
    task()
    # Then
    translated_input_files = task.read(tags=[Tag.input(), Tag.frame()])
    for filepath in translated_input_files:
        assert filepath.exists()

    assert list(task.read(tags=[Tag.input(), Tag.task_dark()]))
    assert list(task.read(tags=[Tag.input(), Tag.task_lamp_gain()]))
    assert list(task.read(tags=[Tag.input(), Tag.task_solar_gain()]))
    assert (
        len(list(task.read(tags=[Tag.input(), Tag.task_polcal()]))) == 6
    )  # 2 polcal observes, 2 darks, 2 gains
    assert list(task.read(tags=[Tag.input(), Tag.task_observe()]))
    assert len(list(task.read(tags=[Tag.input(), Tag.task_polcal_dark()]))) == 2  # 2 polcal darks
    assert len(list(task.read(tags=[Tag.input(), Tag.task_polcal_gain()]))) == 2  # 2 polcal gains


def test_parse_visp_input_data_constants(
    parse_task_with_no_data,
    write_input_cal_frames_to_task,
    mocker,
    fake_gql_client,
    lamp_readout_exp_time,
    solar_readout_exp_time,
    polcal_readout_exp_time,
    observe_readout_exp_times,
    dark_exp_time,
    lamp_exp_time,
    solar_exp_time,
    polcal_exp_time,
    observe_exp_times,
    num_modstates,
):
    """
    Given: A ParseVispInputData task
    When: Calling the task instance
    Then: Constants are in the constants object as expected
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task = parse_task_with_no_data
    write_input_cal_frames_to_task(task)

    num_maps_per_readout_exp_time = 1
    num_steps = 3
    for obs_readout_exp_time, obs_exp_time in zip(observe_readout_exp_times, observe_exp_times):
        write_input_observe_frames_to_task(
            task,
            num_maps=num_maps_per_readout_exp_time,
            num_modstates=num_modstates,
            num_steps=num_steps,
            readout_exp_time=obs_readout_exp_time,
            exp_time=obs_exp_time,
        )

    # When
    task()
    # Then
    expected_dark_readout_exp_times = [
        lamp_readout_exp_time,
        solar_readout_exp_time,
    ] + observe_readout_exp_times
    assert task.constants._db_dict["OBS_IP_START_TIME"] == "2022-11-28T13:55:00"
    assert task.constants._db_dict["NUM_MODSTATES"] == num_modstates
    assert task.constants._db_dict["NUM_MAP_SCANS"] == num_maps_per_readout_exp_time * len(
        observe_readout_exp_times
    )
    assert task.constants._db_dict["NUM_RASTER_STEPS"] == num_steps
    assert task.constants._db_dict["WAVELENGTH"] == 656.28
    assert task.constants._db_dict["DARK_EXPOSURE_TIMES"] == [dark_exp_time]
    assert task.constants._db_dict["LAMP_EXPOSURE_TIMES"] == [lamp_exp_time]
    assert task.constants._db_dict["SOLAR_EXPOSURE_TIMES"] == [solar_exp_time]
    assert task.constants._db_dict["POLCAL_EXPOSURE_TIMES"] == [polcal_exp_time]
    assert sorted(task.constants._db_dict["OBSERVE_EXPOSURE_TIMES"]) == sorted(observe_exp_times)
    assert task.constants._db_dict["DARK_READOUT_EXP_TIMES"] == expected_dark_readout_exp_times
    assert task.constants._db_dict["LAMP_READOUT_EXP_TIMES"] == [lamp_readout_exp_time]
    assert task.constants._db_dict["SOLAR_READOUT_EXP_TIMES"] == [solar_readout_exp_time]
    assert task.constants._db_dict["POLCAL_READOUT_EXP_TIMES"] == [polcal_readout_exp_time]
    assert sorted(task.constants._db_dict["OBSERVE_READOUT_EXP_TIMES"]) == sorted(
        observe_readout_exp_times
    )
    assert task.constants._db_dict["RETARDER_NAME"] == "SiO2 OC"


def test_parse_visp_values(
    parse_task_with_no_data,
    write_input_cal_frames_to_task,
    observe_readout_exp_times,
    num_modstates,
    mocker,
    fake_gql_client,
):
    """
    :Given: A valid parse input task
    :When: Calling the task instance
    :Then: Values are correctly loaded into the constants mutable mapping
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task = parse_task_with_no_data
    write_input_cal_frames_to_task(task)
    write_input_observe_frames_to_task(
        task,
        readout_exp_time=observe_readout_exp_times[0],
        exp_time=99.0,
        num_maps=1,
        num_steps=1,
        num_modstates=num_modstates,
    )

    task()
    assert task.constants.instrument == "VISP"
    assert task.constants.average_cadence == 10
    assert task.constants.maximum_cadence == 10
    assert task.constants.minimum_cadence == 10
    assert task.constants.variance_cadence == 0


def test_multiple_num_raster_steps_raises_error(
    parse_task_with_no_data, num_modstates, mocker, fake_gql_client
):
    """
    :Given: A prase task with data that have inconsistent VSPNSTP values
    :When: Calling the parse task
    :Then: The correct error is raised
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task = parse_task_with_no_data
    write_input_dark_frames_to_task(task, readout_exp_time=0.1, exp_time=0.2)
    write_input_observe_frames_to_task(
        task,
        num_maps=1,
        num_steps=2,
        num_modstates=num_modstates,
        readout_exp_time=0.1,
        exp_time=0.2,
        obs_dataset_class=VispHeadersMultiNumRasterSteps,
    )

    with pytest.raises(ValueError, match="Multiple NUM_RASTER_STEPS values found"):
        task()


def test_incomplete_single_map(parse_task_with_no_data, num_modstates, mocker, fake_gql_client):
    """
    :Given: A parse task with data that has an incomplete raster scan
    :When: Calling the parse task
    :Then: The correct number of raster steps are found
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task = parse_task_with_no_data
    num_steps = 4
    num_map_scans = 1
    write_input_dark_frames_to_task(task, readout_exp_time=0.1, exp_time=0.2)
    write_input_observe_frames_to_task(
        task,
        num_maps=num_map_scans,
        num_steps=num_steps,
        num_modstates=num_modstates,
        readout_exp_time=0.1,
        exp_time=0.2,
        obs_dataset_class=VispHeadersIncompleteFinalMap,
    )
    task()
    assert task.constants._db_dict["NUM_RASTER_STEPS"] == num_steps - 1
    assert task.constants._db_dict["NUM_MAP_SCANS"] == num_map_scans


def test_incomplete_final_map(parse_task_with_no_data, num_modstates, mocker, fake_gql_client):
    """
    :Given: A parse task with data that has complete raster scans along with an incomplete raster scan
    :When: Calling the parse task
    :Then: The correct number of raster steps and maps are found
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task = parse_task_with_no_data
    num_steps = 4
    num_map_scans = 3
    write_input_dark_frames_to_task(task, readout_exp_time=0.1, exp_time=0.2)
    write_input_observe_frames_to_task(
        task,
        num_maps=num_map_scans,
        num_steps=num_steps,
        num_modstates=num_modstates,
        readout_exp_time=0.1,
        exp_time=0.2,
        obs_dataset_class=VispHeadersIncompleteFinalMap,
    )
    task()
    assert task.constants._db_dict["NUM_RASTER_STEPS"] == num_steps
    assert task.constants._db_dict["NUM_MAP_SCANS"] == num_map_scans - 1


def test_intensity_observes_and_polarimetric_cals(
    parse_task_with_no_data,
    write_input_cal_frames_to_task,
    observe_readout_exp_times,
    observe_exp_times,
    mocker,
    fake_gql_client,
):
    """
    :Given: Data where the observe frames are in intensity mode and the calibration frames are in polarimetric mode
    :When: Parsing the data
    :Then: All modulator state keys generated for all frames are in the first modulator state
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task = parse_task_with_no_data
    write_input_cal_frames_to_task(task)
    write_input_observe_frames_to_task(
        task,
        num_maps=3,
        num_steps=2,
        num_modstates=1,
        readout_exp_time=observe_readout_exp_times[0],
        exp_time=observe_exp_times[0],
        obs_dataset_class=VispHeadersIntensityObserveFrames,
    )
    task()
    assert task.constants._db_dict["NUM_MODSTATES"] == 1
    assert task.constants._db_dict["POLARIMETER_MODE"] == "observe_intensity"
    files = list(task.read(tags=[Tag.input(), Tag.frame()]))
    for file in files:
        assert "MODSTATE_1" in task.scratch.tags(file)


def test_dark_readout_exp_time_picky_bud(
    parse_task_with_no_data, mocker, fake_gql_client, lamp_readout_exp_time
):
    """
    :Given: Dataset where non-dark readout exp time values are missing from the set of dark IP frames.
    :When: Parsing
    :Then: The `DarkReadoutExpTimePickyBud` raises an error
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    bad_readout_exp_time = lamp_readout_exp_time + 0.02
    dummy_exp_time = 99.0

    write_input_lamp_frames_to_task(
        task=parse_task_with_no_data,
        readout_exp_time=lamp_readout_exp_time,
        exp_time=dummy_exp_time,
    )
    write_input_dark_frames_to_task(
        task=parse_task_with_no_data, readout_exp_time=bad_readout_exp_time, exp_time=dummy_exp_time
    )

    task = parse_task_with_no_data
    with pytest.raises(
        ValueError,
        match=f"Not all required readout exposure times were found in DARK IPs. Missing times = {{{lamp_readout_exp_time}}}",
    ):
        task()
