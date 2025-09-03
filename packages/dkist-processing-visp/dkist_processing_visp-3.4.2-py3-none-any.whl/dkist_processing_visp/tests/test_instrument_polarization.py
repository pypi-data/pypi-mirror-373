from unittest.mock import ANY
from unittest.mock import patch

import numpy as np
import pytest
from astropy.io import fits
from dkist_data_simulator.spec122 import Spec122Dataset
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_pac.fitter.polcal_fitter import PolcalFitter
from dkist_processing_pac.input_data.dresser import Dresser

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.tasks.instrument_polarization import InstrumentPolarizationCalibration
from dkist_processing_visp.tests.conftest import VispConstantsDb
from dkist_processing_visp.tests.conftest import VispInputDatasetParameterValues
from dkist_processing_visp.tests.conftest import write_dummy_intermediate_solar_cals_to_task
from dkist_processing_visp.tests.conftest import write_frames_to_task
from dkist_processing_visp.tests.conftest import write_intermediate_background_to_task
from dkist_processing_visp.tests.conftest import write_intermediate_darks_to_task
from dkist_processing_visp.tests.conftest import write_intermediate_geometric_to_task
from dkist_processing_visp.tests.conftest import write_intermediate_polcal_darks_to_task
from dkist_processing_visp.tests.conftest import write_intermediate_polcal_gains_to_task
from dkist_processing_visp.tests.header_models import VispHeadersInputPolcalDarkFrames
from dkist_processing_visp.tests.header_models import VispHeadersInputPolcalFrames
from dkist_processing_visp.tests.header_models import VispHeadersInputPolcalGainFrames


class DummyPolcalFitter(PolcalFitter):
    def __init__(
        self,
        *,
        local_dresser: Dresser,
        global_dresser: Dresser,
        fit_mode: str,
        init_set: str,
        fit_TM: bool = False,
        threads: int = 1,
        super_name: str = "",
        _dont_fit: bool = False,
        **fit_kwargs,
    ):
        with patch("dkist_processing_pac.fitter.polcal_fitter.FitObjects"):
            with patch("dkist_processing_pac.fitter.polcal_fitter.PolcalFitter.check_dressers"):
                super().__init__(
                    local_dresser=local_dresser,
                    global_dresser=global_dresser,
                    fit_mode="use_M12",
                    init_set="OCCal_VIS",
                    _dont_fit=True,
                )

        self.num_modstates = local_dresser.nummod

    @property
    def demodulation_matrices(self) -> np.ndarray:
        return np.ones((1, 1, 4, self.num_modstates))


def tag_on_modstate_and_cs_step(frame: VispHeadersInputPolcalFrames):
    modstate = frame.current_modstate("")  # Weird signature due to key_function
    cs_step = frame.current_cs_step

    return [VispTag.modstate(modstate), VispTag.cs_step(cs_step)]


def write_input_polcals_to_task(
    task,
    readout_exp_time: float,
    num_modstates: int,
    num_cs_steps: int,
    data_shape: tuple[int, int],
):
    array_shape = (1, *data_shape)
    dataset = VispHeadersInputPolcalFrames(
        array_shape=array_shape,
        time_delta=10,
        num_modstates=num_modstates,
        num_cs_steps=num_cs_steps,
        readout_exp_time=readout_exp_time,
    )

    write_frames_to_task(
        task=task,
        frame_generator=dataset,
        extra_tags=[
            VispTag.input(),
            VispTag.task_polcal(),
            VispTag.readout_exp_time(readout_exp_time),
        ],
        tag_func=tag_on_modstate_and_cs_step,
    )


def write_input_polcal_darks_to_task(
    task,
    readout_exp_time: float,
    num_modstates: int,
    data_shape: tuple[int, int],
):
    array_shape = (1, *data_shape)
    dataset = VispHeadersInputPolcalDarkFrames(
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
            VispTag.task_polcal(),
            VispTag.task_polcal_dark(),
            VispTag.readout_exp_time(readout_exp_time),
        ],
    )


def write_input_polcal_gains_to_task(
    task,
    readout_exp_time: float,
    num_modstates: int,
    data_shape: tuple[int, int],
):
    array_shape = (1, *data_shape)
    dataset = VispHeadersInputPolcalGainFrames(
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
            VispTag.task_polcal(),
            VispTag.task_polcal_gain(),
            VispTag.readout_exp_time(readout_exp_time),
        ],
    )


@pytest.fixture(scope="function")
def instrument_polarization_calibration_task(
    tmp_path,
    recipe_run_id,
    init_visp_constants_db,
):
    num_modstates = 2
    num_cs_steps = 2
    readout_exp_time = 0.02
    constants_db = VispConstantsDb(
        POLARIMETER_MODE="observe_polarimetric",
        NUM_MODSTATES=num_modstates,
        NUM_BEAMS=2,
        NUM_CS_STEPS=num_cs_steps,
        POLCAL_READOUT_EXP_TIMES=(readout_exp_time,),
    )
    init_visp_constants_db(recipe_run_id, constants_db)
    with InstrumentPolarizationCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="instrument_polarization_calibration",
        workflow_version="VX.Y",
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            yield task, readout_exp_time, num_modstates, num_cs_steps

        except:
            raise
        finally:
            task._purge()


@pytest.fixture()
def full_beam_shape() -> tuple[int, int]:
    return (100, 256)


@pytest.fixture()
def single_demodulation_matrix() -> np.ndarray:
    return np.arange(40).reshape(1, 1, 4, 10)


@pytest.fixture()
def multiple_demodulation_matrices() -> np.ndarray:
    return np.arange(2 * 3 * 4 * 10).reshape(2, 3, 4, 10)


@pytest.fixture()
def full_spatial_beam_shape() -> tuple[int, int]:
    return (1, 256)


@pytest.fixture()
def spatially_binned_demodulation_matrices(full_spatial_beam_shape) -> np.ndarray:
    num_bins = full_spatial_beam_shape[1] // 4
    return np.arange(1 * num_bins * 4 * 10).reshape(1, num_bins, 4, 10)


@pytest.mark.parametrize(
    "background_on",
    [pytest.param(True, id="Background on"), pytest.param(False, id="Background off")],
)
def test_instrument_polarization_calibration_task(
    instrument_polarization_calibration_task,
    background_on,
    assign_input_dataset_doc_to_task,
    mocker,
    fake_gql_client,
):
    """
    Given: An InstrumentPolarizationCalibration task
    When: Calling the task instance
    Then: A demodulation matrix for each beam is produced and the correct call to the quality storage system was made
    """

    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    mocker.patch(
        "dkist_processing_visp.tasks.instrument_polarization.PolcalFitter",
        new=DummyPolcalFitter,
    )

    # Don't test place-holder QA stuff for now
    quality_metric_mocker = mocker.patch(
        "dkist_processing_visp.tasks.instrument_polarization.InstrumentPolarizationCalibration.quality_store_polcal_results",
        autospec=True,
    )

    # When
    task, readout_exp_time, num_modstates, num_cs_steps = instrument_polarization_calibration_task
    intermediate_shape = (10, 10)
    input_shape = (20, 10)
    beam_border = input_shape[0] // 2
    assign_input_dataset_doc_to_task(
        task,
        VispInputDatasetParameterValues(
            visp_background_on=background_on, visp_beam_border=beam_border
        ),
    )

    if background_on:
        write_intermediate_background_to_task(
            task=task, background_signal=0.0, data_shape=intermediate_shape
        )

    write_intermediate_geometric_to_task(
        task=task, num_modstates=num_modstates, data_shape=intermediate_shape
    )
    write_dummy_intermediate_solar_cals_to_task(
        task=task, data_shape=intermediate_shape, num_modstates=num_modstates
    )
    write_input_polcals_to_task(
        task=task,
        readout_exp_time=readout_exp_time,
        num_modstates=num_modstates,
        num_cs_steps=num_cs_steps,
        data_shape=input_shape,
    )
    write_input_polcal_darks_to_task(
        task=task,
        readout_exp_time=readout_exp_time,
        num_modstates=num_modstates,
        data_shape=input_shape,
    )
    write_input_polcal_gains_to_task(
        task=task,
        readout_exp_time=readout_exp_time,
        num_modstates=num_modstates,
        data_shape=input_shape,
    )

    task()

    # Then
    for beam in [1, 2]:
        tags = [
            VispTag.intermediate(),
            VispTag.task_demodulation_matrices(),
            VispTag.beam(beam),
        ]
        file_list = list(task.read(tags=tags))
        assert len(file_list) == 1
        hdul = fits.open(file_list[0])
        assert len(hdul) == 1
        data = hdul[0].data
        assert data.shape == (*intermediate_shape, 4, num_modstates)

        quality_metric_mocker.assert_any_call(
            task,
            polcal_fitter=ANY,
            label=f"Beam {beam}",
            bin_nums=[1, task.parameters.polcal_num_spatial_bins],
            bin_labels=["spectral", "spatial"],
            skip_recording_constant_pars=beam == 2,
        )


def test_smooth_demod_matrices(
    instrument_polarization_calibration_task,
    spatially_binned_demodulation_matrices,
    assign_input_dataset_doc_to_task,
    full_spatial_beam_shape,
):
    """
    Given: An InstrumentPolarizationCalibration task and a set of demod matrices binned in the spatial dimension
    When: Smooth the demodulation matrices
    Then: Smoothing doesn't fail and the result fully samples the full spatial dimension
    """
    task = instrument_polarization_calibration_task[0]
    assign_input_dataset_doc_to_task(task, VispInputDatasetParameterValues())
    task.single_beam_shape = full_spatial_beam_shape
    result = task.smooth_demod_matrices(spatially_binned_demodulation_matrices)
    assert result.shape == full_spatial_beam_shape + (4, 10)


def test_reshape_demod_matrices(
    instrument_polarization_calibration_task,
    multiple_demodulation_matrices,
    full_beam_shape,
    assign_input_dataset_doc_to_task,
):
    """
    Given: An InstrumentPolarizationCalibration task and a set of demodulation matrices sampled over the full FOV
    When: Up-sampling the demodulation matrices
    Then: The final set of demodulation matrices has the correct, full-FOV shape
    """
    task = instrument_polarization_calibration_task[0]
    assign_input_dataset_doc_to_task(task, VispInputDatasetParameterValues())
    task.single_beam_shape = full_beam_shape
    result = task.reshape_demod_matrices(multiple_demodulation_matrices)
    assert result.shape == full_beam_shape + (4, 10)


def test_reshape_single_demod_matrix(
    instrument_polarization_calibration_task,
    single_demodulation_matrix,
    full_beam_shape,
    assign_input_dataset_doc_to_task,
):
    """
    Given: An InstrumentPolarizationCalibration task and a single demodulation matrix for the whole FOV
    When: Up-sampling the demodulation matrices
    Then: The final set of demodulation matrices still only has a single matrix
    """
    task = instrument_polarization_calibration_task[0]
    assign_input_dataset_doc_to_task(task, VispInputDatasetParameterValues())
    task.single_beam_shape = full_beam_shape
    result = task.reshape_demod_matrices(single_demodulation_matrix)
    assert result.shape == (4, 10)
