import json
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import is_dataclass
from random import randint
from typing import Callable
from typing import Type

import numpy as np
import pytest
from astropy.io import fits
from dkist_data_simulator.spec122 import Spec122Dataset
from dkist_header_validator.translator import sanitize_to_spec214_level1
from dkist_header_validator.translator import translate_spec122_to_spec214_l0
from dkist_processing_common.codecs.basemodel import basemodel_encoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.models.input_dataset import InputDatasetPartDocumentList
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_processing_common.tests.mock_metadata_store import fake_gql_client

from dkist_processing_visp.models.constants import VispConstants
from dkist_processing_visp.models.parameters import VispParameters
from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.tests.header_models import VispHeaders
from dkist_processing_visp.tests.header_models import VispHeadersValidCalibratedFrames


@pytest.fixture()
def init_visp_constants_db():
    def constants_maker(recipe_run_id: int, constants_obj):
        if is_dataclass(constants_obj):
            constants_obj = asdict(constants_obj)
        constants = VispConstants(recipe_run_id=recipe_run_id, task_name="test")
        constants._purge()
        constants._update(constants_obj)
        return

    return constants_maker


@dataclass
class VispConstantsDb:
    POLARIMETER_MODE: str = "observe_polarimetric"
    OBS_IP_START_TIME: str = "2022-11-28T13:54:00"
    NUM_MODSTATES: int = 10
    NUM_MAP_SCANS: int = 2
    NUM_RASTER_STEPS: int = 3
    NUM_BEAMS: int = 2
    NUM_CS_STEPS: int = 18
    NUM_SPECTRAL_BINS: int = 1
    NUM_SPATIAL_BINS: int = 1
    INSTRUMENT: str = "VISP"
    AVERAGE_CADENCE: float = 10.0
    MINIMUM_CADENCE: float = 10.0
    MAXIMUM_CADENCE: float = 10.0
    VARIANCE_CADENCE: float = 0.0
    WAVELENGTH: float = 588.0
    NON_DARK_TASK_READOUT_EXP_TIMES: tuple[float, ...] = (200.0, 2.0, 0.02)
    LAMP_EXPOSURE_TIMES: tuple[float] = (100.0,)
    SOLAR_EXPOSURE_TIMES: tuple[float] = (1.0,)
    OBSERVE_EXPOSURE_TIMES: tuple[float] = (0.01,)
    POLCAL_EXPOSURE_TIMES: tuple[float] = ()
    LAMP_READOUT_EXP_TIMES: tuple[float] = (200.0,)
    SOLAR_READOUT_EXP_TIMES: tuple[float] = (2.0,)
    OBSERVE_READOUT_EXP_TIMES: tuple[float] = (0.02,)
    POLCAL_READOUT_EXP_TIMES: tuple[float] = (0.02,)
    SPECTRAL_LINE: str = "VISP Ca II H"
    STOKES_PARAMS: tuple[str] = (
        "I",
        "Q",
        "U",
        "V",
    )  # A tuple because lists aren't allowed on dataclasses
    CONTRIBUTING_PROPOSAL_IDS: tuple[str] = (
        "PROPID1",
        "PROPID2",
    )
    CONTRIBUTING_EXPERIMENT_IDS: tuple[str] = (
        "EXPERID1",
        "EXPERID2",
        "EXPERID3",
    )
    AXIS_1_TYPE: str = "HPLT-TAN"
    AXIS_2_TYPE: str = "AWAV"
    AXIS_3_TYPE: str = "HPLN-TAN"
    RETARDER_NAME: str = "SiO2 OC"


@pytest.fixture()
def recipe_run_id():
    return randint(0, 99999)


@dataclass
class WavelengthParameter:
    values: tuple
    wavelength: tuple = (397.0, 588.0, 630.0, 854.0)  # This must always be in order

    def __hash__(self):
        return hash((self.values, self.wavelength))


@dataclass
class VispInputDatasetParameterValues:
    visp_max_cs_step_time_sec: float = 180.0
    visp_beam_border: int = 1000
    visp_background_on: bool = True
    visp_background_num_spatial_bins: WavelengthParameter = WavelengthParameter(values=(1, 4, 1, 1))
    visp_background_wavelength_subsample_factor: WavelengthParameter = WavelengthParameter(
        values=(10, 7, 10, 10)
    )
    visp_background_num_fit_iterations: WavelengthParameter = WavelengthParameter(
        values=(20, 100, 20, 20)
    )
    visp_background_continuum_index: WavelengthParameter = WavelengthParameter(
        values=(list(range(190)), list(range(190)), list(range(190)), list(range(190)))
    )
    visp_hairline_median_spatial_smoothing_width_px: int = 30
    visp_hairline_fraction: float = 0.11
    visp_hairline_mask_spatial_smoothing_width_px: float = 1.0
    visp_hairline_mask_gaussian_peak_cutoff_fraction: float = 0.02
    visp_geo_binary_opening_diameter: int = 21
    visp_geo_hairline_flat_id_threshold: float = 0.9
    visp_geo_hairline_fit_width_px: int = 10
    visp_geo_hairline_angle_fit_sig_clip: float = 3.0
    visp_geo_max_beam_2_angle_refinement: float = np.deg2rad(0.1)
    visp_geo_upsample_factor: float = 10.0
    visp_geo_max_shift: float = 40.0
    visp_geo_poly_fit_order: int = 3
    visp_solar_spectral_avg_window: WavelengthParameter = WavelengthParameter(
        values=(800, 800, 800, 800)
    )
    visp_solar_characteristic_spatial_normalization_percentile: float = 90.0
    visp_solar_zone_prominence: WavelengthParameter = WavelengthParameter(
        values=(0.2, 0.2, 0.3, 0.2)
    )
    visp_solar_zone_width: WavelengthParameter = WavelengthParameter(values=(7, 2, 3, 2))
    visp_solar_zone_bg_order: WavelengthParameter = WavelengthParameter(values=(21, 22, 11, 22))
    visp_solar_zone_normalization_percentile: WavelengthParameter = WavelengthParameter(
        values=(90, 99, 90, 90)
    )
    visp_solar_zone_rel_height: float = 0.97
    visp_polcal_spatial_median_filter_width_px: int = 10
    visp_polcal_num_spatial_bins: int = 10
    visp_polcal_demod_spatial_smooth_fit_order: int = 17
    visp_polcal_demod_spatial_smooth_min_samples: float = 0.9
    visp_polcal_demod_upsample_order: int = 3
    visp_pac_remove_linear_I_trend: bool = True
    visp_pac_fit_mode: str = "use_M12_I_sys_per_step"


@pytest.fixture(scope="session")
def testing_wavelength() -> float:
    return 588.0


@pytest.fixture(scope="session")
def testing_obs_ip_start_time() -> str:
    return "1946-11-20T12:34:56"


@pytest.fixture(scope="session")
def input_dataset_document_simple_parameters_part():
    """Convert a dataclass of parameterValues into an actual input dataset parameters part."""

    def make_input_dataset_parameters_part(parameter_values: dataclass):
        parameters_list = []
        value_id = randint(1000, 2000)
        for pn, pv in asdict(parameter_values).items():
            if type(pv) is WavelengthParameter:
                pv = asdict(pv)
            values = [
                {
                    "parameterValueId": value_id,
                    "parameterValue": json.dumps(pv),
                    "parameterValueStartDate": "1946-11-20",  # Remember Duane Allman
                }
            ]
            parameter = {"parameterName": pn, "parameterValues": values}
            parameters_list.append(parameter)
        return parameters_list

    return make_input_dataset_parameters_part


@pytest.fixture(scope="session")
def assign_input_dataset_doc_to_task(
    input_dataset_document_simple_parameters_part, testing_obs_ip_start_time, testing_wavelength
):
    def update_task(
        task: WorkflowTaskBase,
        parameter_values,
        parameter_class=VispParameters,
        obs_ip_start_time=testing_obs_ip_start_time,
    ):
        task.write(
            data=InputDatasetPartDocumentList(
                doc_list=input_dataset_document_simple_parameters_part(parameter_values)
            ),
            tags=VispTag.input_dataset_parameters(),
            encoder=basemodel_encoder,
        )
        task.parameters = parameter_class(
            scratch=task.scratch,
            obs_ip_start_time=obs_ip_start_time,
            wavelength=testing_wavelength,
        )

    return update_task


def make_random_data(frame: Spec122Dataset) -> np.ndarray:
    data = np.random.random(frame.array_shape)

    return data


def tag_on_modstate(frame: VispHeaders) -> list[str]:
    """Tage a given frame based on its current modstate value."""
    modstate = frame.current_modstate(
        ""
    )  # Weird signature b/c `current_modstate` is a `key_function`
    return [VispTag.modstate(modstate)]


def write_frames_to_task(
    task: Type[WorkflowTaskBase],
    frame_generator: Spec122Dataset,
    data_func: Callable[[Spec122Dataset], np.ndarray] = make_random_data,
    extra_tags: list[str] | None = None,
    tag_func: Callable[[Spec122Dataset], list[str]] = lambda x: [],
):
    """
    Write all frames from a given *Dataset generator to a task.

    Parameters
    ----------
    data_func
        A function that takes a single frame and produces a numpy array containing that frame's data

    extra_tags
        List of tags to apply to frames (all frames get the "FRAME" tag)

    tag_func
        Function that takes a single frame and produces specific tags for just that frame
    """
    if not extra_tags:
        extra_tags = []
    tags = [VispTag.frame()] + extra_tags

    num_frames = 0
    for frame in frame_generator:
        header = frame.header()
        data = data_func(frame)
        frame_tags = tags + tag_func(frame)
        translated_header = fits.Header(translate_spec122_to_spec214_l0(header))
        task.write(data=data, header=translated_header, tags=frame_tags, encoder=fits_array_encoder)
        num_frames += 1

    return num_frames


def write_output_frames_to_task(
    task: Type[WorkflowTaskBase],
    frame_generator: Spec122Dataset,
    data_func: Callable[[Spec122Dataset], np.ndarray] = make_random_data,
    extra_tags: list[str] | None = None,
    tag_func: Callable[[Spec122Dataset], list[str]] = lambda x: [],
    num_dataset_axes: int = 5,
):
    """
    Write all frames from a given *Dataset generator to a task as OUTPUT frames.

    Unlike `write_frames_to_task` this function enforces ONLY SPEC-0214 header keys and a compressed HDU.

    Parameters
    ----------
    data_func
        A function that takes a single frame and produces a numpy array containing that frame's data

    extra_tags
        List of tags to apply to frames (all frames get the "FRAME" tag)

    tag_func
        Function that takes a single frame and produces specific tags for just that frame

    num_dataset_axes
        Total number of axes in the larger dataset. Can be different for pol and non-pol data
    """
    if not extra_tags:
        extra_tags = []
    tags = [VispTag.frame()] + extra_tags

    num_frames = 0
    for frame in frame_generator:
        header = frame.header()
        data = data_func(frame)
        frame_tags = tags + tag_func(frame)
        translated_header = convert_header_122l0_to_214l1(header, num_dataset_axes)
        hdu_list = fits.HDUList(
            [fits.PrimaryHDU(), fits.CompImageHDU(data=data, header=translated_header)]
        )
        task.write(data=hdu_list, tags=frame_tags, encoder=fits_hdulist_encoder)
        num_frames += 1

    return num_frames


def convert_header_122l0_to_214l1(header: dict, num_dataset_axes) -> dict:
    l0_214_header = translate_spec122_to_spec214_l0(header)
    l0_214_header["DNAXIS"] = num_dataset_axes
    l0_214_header["DAAXES"] = 2
    l0_214_header["DEAXES"] = num_dataset_axes - 2
    l1_header = sanitize_to_spec214_level1(input_headers=l0_214_header)

    return l1_header


def write_intermediate_darks_to_task(
    task, *, dark_signal: float, readout_exp_time: float, data_shape: tuple[int, int]
):
    dark_cal = np.ones(data_shape) * dark_signal
    # Need a dark for each beam
    for beam in [1, 2]:
        task.write(
            data=dark_cal,
            tags=VispTag.intermediate_frame_dark(beam=beam, readout_exp_time=readout_exp_time),
            encoder=fits_array_encoder,
        )


def write_intermediate_background_to_task(
    task, *, background_signal: float, data_shape: tuple[int, int]
):
    bg_array = np.ones(data_shape) * background_signal
    # Need a dark for each beam
    for beam in [1, 2]:
        task.write(
            data=bg_array,
            tags=[VispTag.intermediate_frame(beam=beam), VispTag.task_background()],
            encoder=fits_array_encoder,
        )


def write_intermediate_lamp_to_task(
    task, *, lamp_signal: float, beam: int, modstate: int, data_shape: tuple[int, int]
):
    lamp_array = np.ones(data_shape) * lamp_signal
    task.write(
        data=lamp_array,
        tags=[
            VispTag.intermediate_frame(beam=beam, modstate=modstate),
            VispTag.task_lamp_gain(),
        ],
        encoder=fits_array_encoder,
    )


def write_intermediate_solar_to_task(
    task, *, solar_signal: float, beam: int, modstate: int, data_shape: tuple[int, int]
):
    solar_array = np.ones(data_shape) * solar_signal
    task.write(
        data=solar_array,
        tags=[
            VispTag.intermediate_frame(beam=beam, modstate=modstate),
            VispTag.task_solar_gain(),
        ],
        encoder=fits_array_encoder,
    )


def write_intermediate_geometric_to_task(
    task,
    *,
    num_modstates: int,
    data_shape: tuple[int, int],
    angles: np.ndarray | None = None,
    offsets: np.ndarray | None = None,
    shifts: np.ndarray | None = None,
):
    if angles is None:
        angles = np.zeros((2, 1))
    if offsets is None:
        offsets = np.zeros((2, num_modstates, 2))
    if shifts is None:
        shifts = np.zeros((2, data_shape[0]))

    for beam in [1, 2]:
        task.write(
            data=angles[beam - 1],
            tags=[VispTag.intermediate_frame(beam=beam), VispTag.task_geometric_angle()],
            encoder=fits_array_encoder,
        )

        task.write(
            data=shifts[beam - 1],
            tags=[VispTag.intermediate_frame(beam=beam), VispTag.task_geometric_spectral_shifts()],
            encoder=fits_array_encoder,
        )

        for modstate in range(1, num_modstates + 1):
            task.write(
                data=offsets[beam - 1, modstate - 1],
                tags=[
                    VispTag.intermediate_frame(beam=beam, modstate=modstate),
                    VispTag.task_geometric_offset(),
                ],
                encoder=fits_array_encoder,
            )


def write_dummy_intermediate_solar_cals_to_task(
    task,
    *,
    num_modstates: int,
    data_shape: tuple[int, int],
):
    solar_signal = 1.0
    for beam in [1, 2]:
        for modstate in range(1, num_modstates + 1):
            write_intermediate_solar_to_task(
                task=task,
                solar_signal=solar_signal,
                beam=beam,
                modstate=modstate,
                data_shape=data_shape,
            )


def write_intermediate_polcal_darks_to_task(
    task, *, dark_signal: float, readout_exp_time: float, data_shape: tuple[int, int]
):
    dark_cal = np.ones(data_shape) * dark_signal
    # Need a dark for each beam
    for beam in [1, 2]:
        task.write(
            data=dark_cal,
            tags=VispTag.intermediate_frame_polcal_dark(
                beam=beam, readout_exp_time=readout_exp_time
            ),
            encoder=fits_array_encoder,
        )


def write_intermediate_polcal_gains_to_task(
    task, *, gain_signal: float, readout_exp_time: float, data_shape: tuple[int, int]
):
    gain_cal = np.ones(data_shape) * gain_signal
    # Need a dark for each beam
    for beam in [1, 2]:
        task.write(
            data=gain_cal,
            tags=VispTag.intermediate_frame_polcal_gain(
                beam=beam, readout_exp_time=readout_exp_time
            ),
            encoder=fits_array_encoder,
        )


def tag_on_map_raster_stokes(frame: VispHeadersValidCalibratedFrames) -> list[str]:
    map_scan = frame.current_map
    raster_step = frame.current_raster_step("")
    stokes = frame.current_stokes

    return [VispTag.map_scan(map_scan), VispTag.raster_step(raster_step), VispTag.stokes(stokes)]


def write_calibrated_frames_to_task(
    task,
    *,
    pol_mode: str,
    data_shape: tuple[int, int],
    wcs_axis_names: tuple[str, str] = ("HPLT-TAN", "AWAV"),
    num_maps: int = 1,
    num_steps: int = 1,
):
    array_shape = (1, *data_shape)
    dataset = VispHeadersValidCalibratedFrames(
        array_shape=array_shape,
        time_delta=10.0,
        num_maps=num_maps,
        num_raster_steps=num_steps,
        polarimeter_mode=pol_mode,
        wcs_axis_names=wcs_axis_names,
    )

    num_written_frames = write_frames_to_task(
        task=task,
        frame_generator=dataset,
        extra_tags=[VispTag.calibrated()],
        tag_func=tag_on_map_raster_stokes,
        data_func=make_random_data,
    )
    return num_written_frames
