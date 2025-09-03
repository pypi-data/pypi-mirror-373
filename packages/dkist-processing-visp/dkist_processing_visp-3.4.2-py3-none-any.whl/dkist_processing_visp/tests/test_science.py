import json
import random
from datetime import datetime
from typing import Literal

import numpy as np
import pytest
from astropy.io import fits
from astropy.time import Time
from astropy.time import TimeDelta
from dkist_header_validator import spec122_validator
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.codecs.fits import fits_hdu_decoder
from dkist_processing_common.models.tags import Tag

from dkist_processing_visp.models.tags import VispStemName
from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.parsers.visp_l0_fits_access import VispL0FitsAccess
from dkist_processing_visp.tasks.science import CalibrationCollection
from dkist_processing_visp.tasks.science import ScienceCalibration
from dkist_processing_visp.tests.conftest import VispConstantsDb
from dkist_processing_visp.tests.conftest import VispInputDatasetParameterValues
from dkist_processing_visp.tests.conftest import write_dummy_intermediate_solar_cals_to_task
from dkist_processing_visp.tests.conftest import write_frames_to_task
from dkist_processing_visp.tests.conftest import write_intermediate_background_to_task
from dkist_processing_visp.tests.conftest import write_intermediate_darks_to_task
from dkist_processing_visp.tests.conftest import write_intermediate_geometric_to_task
from dkist_processing_visp.tests.header_models import VispHeadersValidObserveFrames


def write_demod_matrices_to_task(task, num_modstates: int):
    demod_matrices = np.zeros((4, num_modstates)) + np.array([1, 2, 3, 4])[:, None]
    for beam in [1, 2]:
        task.write(
            data=demod_matrices,
            tags=[
                VispTag.intermediate(),
                VispTag.frame(),
                VispTag.task_demodulation_matrices(),
                VispTag.beam(beam),
            ],
            encoder=fits_array_encoder,
        )


def tag_on_modstate_raster_map(frame: VispHeadersValidObserveFrames) -> list[str]:
    modstate = frame.current_modstate("")  # Weird signature due to key_function
    raster_step = frame.current_raster_step("")
    map_scan = frame.current_map

    return [
        VispTag.modstate(modstate),
        VispTag.raster_step(raster_step),
        VispTag.map_scan(map_scan),
    ]


def write_input_observe_frames_to_task(
    task,
    readout_exp_time: float,
    num_modstates: int,
    num_raster_steps: int,
    num_maps: int,
    data_shape: tuple[int, int],
    polarimeter_mode: Literal["observe_polarimetric", "obser_intensity"] = "observe_polarimetric",
):
    array_shape = (1, *data_shape)
    dataset = VispHeadersValidObserveFrames(
        array_shape=array_shape,
        time_delta=10,
        num_modstates=num_modstates,
        num_raster_steps=num_raster_steps,
        num_maps=num_maps,
        polarimeter_mode=polarimeter_mode,
    )
    write_frames_to_task(
        task=task,
        frame_generator=dataset,
        extra_tags=[
            VispTag.input(),
            VispTag.readout_exp_time(readout_exp_time),
            VispTag.task_observe(),
        ],
        tag_func=tag_on_modstate_raster_map,
    )


def get_input_obs_frame_header(task):

    tags = [VispTag.input(), VispTag.task_observe()]
    random_hdu = next(task.read(tags=tags, decoder=fits_hdu_decoder))
    return random_hdu.header


@pytest.fixture(scope="function", params=["observe_polarimetric", "observe_intensity"])
def science_calibration_task(
    tmp_path,
    recipe_run_id,
    init_visp_constants_db,
    request,
):
    num_map_scans = 2
    num_raster_steps = 2
    readout_exp_time = 0.04
    pol_mode = request.param
    if pol_mode == "observe_polarimetric":
        num_modstates = 2
    else:
        num_modstates = 1

    constants_db = VispConstantsDb(
        POLARIMETER_MODE=pol_mode,
        NUM_MODSTATES=num_modstates,
        NUM_MAP_SCANS=num_map_scans,
        NUM_RASTER_STEPS=num_raster_steps,
        NUM_BEAMS=2,
        OBSERVE_READOUT_EXP_TIMES=(readout_exp_time,),
    )
    init_visp_constants_db(recipe_run_id, constants_db)
    with ScienceCalibration(
        recipe_run_id=recipe_run_id, workflow_name="science_calibration", workflow_version="VX.Y"
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )

            yield task, pol_mode, readout_exp_time, num_map_scans, num_raster_steps, num_modstates
        except:
            raise
        finally:
            task._purge()


@pytest.fixture(scope="function")
def dummy_calibration_collection():
    input_shape = (50, 20)
    intermediate_shape = (25, 20)

    beam = 1
    modstate = 1

    dark_dict = {VispTag.beam(beam): {VispTag.readout_exp_time(0.04): np.zeros(intermediate_shape)}}
    background_dict = {VispTag.beam(beam): np.zeros(intermediate_shape)}
    solar_dict = {VispTag.beam(beam): {VispTag.modstate(modstate): np.ones(intermediate_shape)}}
    angle_dict = {VispTag.beam(beam): 0.0}
    spec_dict = {VispTag.beam(beam): np.zeros(intermediate_shape[1])}
    offset_dict = {VispTag.beam(beam): {VispTag.modstate(modstate): np.zeros(2)}}

    collection = CalibrationCollection(
        dark=dark_dict,
        background=background_dict,
        solar_gain=solar_dict,
        angle=angle_dict,
        spec_shift=spec_dict,
        state_offset=offset_dict,
        demod_matrices=None,
    )

    return collection, input_shape, intermediate_shape


@pytest.fixture(scope="session")
def headers_with_dates() -> tuple[list[fits.Header], str, int, int]:
    num_headers = 5
    start_time = "1969-12-06T18:00:00"
    exp_time = 12
    time_delta = 10
    ds = VispHeadersValidObserveFrames(
        array_shape=(1, 4, 4),
        time_delta=time_delta,
        num_maps=num_headers,
        num_raster_steps=1,
        num_modstates=1,
        start_time=datetime.fromisoformat(start_time),
    )
    headers = [
        spec122_validator.validate_and_translate_to_214_l0(d.header(), return_type=fits.HDUList)[
            0
        ].header
        for d in ds
    ]
    random.shuffle(headers)  # Shuffle to make sure they're not already in time order
    for h in headers:
        h["XPOSURE"] = exp_time  # Exposure time, in ms

    return headers, start_time, exp_time, time_delta


@pytest.fixture(scope="session")
def compressed_headers_with_dates(headers_with_dates) -> tuple[list[fits.Header], str, int, int]:
    headers, start_time, exp_time, time_delta = headers_with_dates
    comp_headers = [fits.hdu.compressed.CompImageHeader(h, h) for h in headers]
    return comp_headers, start_time, exp_time, time_delta


@pytest.fixture(scope="function")
def calibration_collection_with_geo_shifts(shifts) -> CalibrationCollection:
    num_beams, num_mod, _ = shifts.shape
    geo_shifts = {
        str(b + 1): {f"m{m + 1}": shifts[b, m, :] for m in range(num_mod)} for b in range(num_beams)
    }
    return CalibrationCollection(
        dark=dict(),
        background=dict(),
        solar_gain=dict(),
        angle=dict(),
        state_offset=geo_shifts,
        spec_shift=dict(),
        demod_matrices=None,
    )


@pytest.fixture(scope="session")
def calibrated_array_and_header_dicts(
    headers_with_dates,
) -> tuple[dict[str, np.ndarray], dict[str, fits.Header]]:
    headers = headers_with_dates[0]
    header = headers[0]

    # It's kind of a hack to have the stokes dimension here; spectrographic data will not have this, but it actually
    # doesn't matter
    shape = (10, 10, 4)
    beam1 = np.ones(shape) + np.arange(4)[None, None, :]
    beam2 = np.ones(shape) + np.arange(4)[::-1][None, None, :]

    array_dict = {VispTag.beam(1): beam1, VispTag.beam(2): beam2}
    header_dict = {VispTag.beam(1): header, VispTag.beam(2): header}

    return array_dict, header_dict


@pytest.fixture(scope="function")
def calibration_collection_with_full_overlap_slice() -> CalibrationCollection:
    shifts = np.array([[[0.0, 0.0]], [[0.0, 0.0]]])
    num_beams, num_mod, _ = shifts.shape
    geo_shifts = {
        str(b + 1): {f"m{m + 1}": shifts[b, m, :] for m in range(num_mod)} for b in range(num_beams)
    }
    return CalibrationCollection(
        dark=dict(),
        background=dict(),
        solar_gain=dict(),
        angle=dict(),
        state_offset=geo_shifts,
        spec_shift=dict(),
        demod_matrices=None,
    )


@pytest.mark.parametrize(
    "background_on",
    [pytest.param(True, id="Background on"), pytest.param(False, id="Background off")],
)
def test_science_calibration_task(
    science_calibration_task,
    background_on,
    assign_input_dataset_doc_to_task,
    mocker,
    fake_gql_client,
):
    """
    Given: A ScienceCalibration task
    When: Calling the task instance
    Then: There are the expected number of science frames with the correct tags applied and the headers have been correctly updated
    """

    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )

    # When
    (
        task,
        polarization_mode,
        readout_exp_time,
        num_maps,
        num_raster_steps,
        num_modstates,
    ) = science_calibration_task
    input_shape = (50, 20)
    intermediate_shape = (25, 20)
    beam_border = input_shape[0] // 2
    assign_input_dataset_doc_to_task(
        task,
        VispInputDatasetParameterValues(
            visp_background_on=background_on, visp_beam_border=beam_border
        ),
    )

    offsets = np.tile(np.array([-10.2, 5.1]), (2, num_modstates, 1))
    offsets[0] = 0.0  # So beam 1 has zero offset

    write_intermediate_darks_to_task(
        task=task,
        dark_signal=0,
        readout_exp_time=readout_exp_time,
        data_shape=intermediate_shape,
    )
    if background_on:
        write_intermediate_background_to_task(
            task=task, background_signal=0.0, data_shape=intermediate_shape
        )

    write_intermediate_geometric_to_task(
        task=task, num_modstates=num_modstates, data_shape=intermediate_shape, offsets=offsets
    )
    write_dummy_intermediate_solar_cals_to_task(
        task=task, data_shape=intermediate_shape, num_modstates=num_modstates
    )
    write_demod_matrices_to_task(task=task, num_modstates=num_modstates)
    write_input_observe_frames_to_task(
        task=task,
        readout_exp_time=readout_exp_time,
        num_modstates=num_modstates,
        num_raster_steps=num_raster_steps,
        num_maps=num_maps,
        data_shape=input_shape,
    )

    input_header = get_input_obs_frame_header(task=task)

    task()

    # 1 from re-dummification
    expected_final_shape = (
        1,
        # The use of np.abs means we can use np.ceil regardless of whether the offset is negative or positive.
        intermediate_shape[0] - np.ceil(np.abs(offsets[1, 0, 0])),
        intermediate_shape[1] - np.ceil(np.abs(offsets[1, 0, 1])),
    )

    # Then
    tags = [
        VispTag.calibrated(),
        VispTag.frame(),
    ]
    files = list(task.read(tags=tags))
    if polarization_mode == "observe_polarimetric":
        # 2 raster steps * 2 map scans * 4 stokes params = 16 frames
        assert len(files) == 16
    elif polarization_mode == "observe_intensity":
        # 2 raster steps * 2 map scans * 1 stokes param = 4 frames
        assert len(files) == 4
    for file in files:
        hdul = fits.open(file)
        header = hdul[1].header
        assert type(hdul[0]) is fits.PrimaryHDU
        assert type(hdul[1]) is fits.CompImageHDU
        assert hdul[1].data.shape == expected_final_shape
        assert "DATE-BEG" in header.keys()
        assert "DATE-END" in header.keys()
        if polarization_mode == "observe_polarimetric":
            assert "POL_NOIS" in header.keys()
            assert "POL_SENS" in header.keys()

        # Check that map scan keys were updated
        map_scan = [
            int(t.split("_")[-1]) for t in task.tags(file) if VispStemName.map_scan.value in t
        ][0]
        assert header["VSPNMAPS"] == 2
        assert header["VSPMAP"] == map_scan

        # Check that WCS keys were updated
        if offsets[1, 0, 0] > 0:
            assert header["CRPIX2"] == input_header["CRPIX2"] - np.ceil(offsets[1, 0, 0])
        if offsets[1, 0, 1] > 0:
            assert header["CRPIX1"] == input_header["CRPIX1"] - np.ceil(offsets[1, 0, 1])

    quality_files = task.read(tags=[Tag.quality("TASK_TYPES")])
    for file in quality_files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert data["total_frames"] == task.scratch.count_all(
                tags=[VispTag.input(), VispTag.frame(), VispTag.task_observe()]
            )


def test_readout_normalization_correct(
    science_calibration_task, dummy_calibration_collection, assign_input_dataset_doc_to_task
):
    """
    Given: A ScienceCalibration task with associated observe frames
    When: Correcting a single array
    Then: The correct normalization by the number of readouts per FPA is performed
    """
    task = science_calibration_task[0]
    corrections, input_shape, intermediate_shape = dummy_calibration_collection
    beam_border = input_shape[0] // 2
    assign_input_dataset_doc_to_task(
        task, VispInputDatasetParameterValues(visp_beam_border=beam_border)
    )

    # Assign a single input observe frame
    dataset = VispHeadersValidObserveFrames(
        array_shape=(1, *input_shape),
        time_delta=10,
        num_raster_steps=1,
        num_modstates=1,
        num_maps=1,
        start_time=datetime.now(),
    )
    readout_exp_time = task.constants.observe_readout_exp_times[0]
    data_func = lambda frame: np.ones(frame.array_shape) * 100 * frame.header()["CAM__014"]
    write_frames_to_task(
        task=task,
        frame_generator=dataset,
        extra_tags=[
            VispTag.task_observe(),
            VispTag.raster_step(1),
            VispTag.map_scan(1),
            VispTag.modstate(1),
            VispTag.input(),
            VispTag.readout_exp_time(readout_exp_time),
        ],
        data_func=data_func,
    )

    # When:
    corrected_array, _ = task.correct_single_frame(
        beam=1,
        modstate=1,
        raster_step=1,
        map_scan=1,
        readout_exp_time=readout_exp_time,
        calibrations=corrections,
    )

    expected = np.ones(intermediate_shape) * 100.0
    np.testing.assert_allclose(corrected_array, expected, rtol=1e-15)


def test_compute_date_keys(headers_with_dates, recipe_run_id, init_visp_constants_db):
    """
    Given: A set of headers with different DATE-OBS values
    When: Computing the time over which the headers were taken
    Then: A header with correct DATE-BEG, DATE-END, and DATE-AVG keys is returned
    """
    headers, start_time, exp_time, time_delta = headers_with_dates
    constants_db = VispConstantsDb()
    init_visp_constants_db(recipe_run_id, constants_db)
    with ScienceCalibration(
        recipe_run_id=recipe_run_id, workflow_name="science_calibration", workflow_version="VX.Y"
    ) as task:
        final_header = task.compute_date_keys(headers)
        final_header_from_single = task.compute_date_keys(headers[0])

    date_end = (
        Time(start_time)
        + (len(headers) - 1) * TimeDelta(time_delta, format="sec")
        + TimeDelta(exp_time / 1000.0, format="sec")
    ).isot

    assert final_header["DATE-BEG"] == start_time
    assert final_header["DATE-END"] == date_end

    date_end_from_single = (
        Time(headers[0]["DATE-BEG"])
        # + TimeDelta(time_delta, format="sec")
        + TimeDelta(exp_time / 1000.0, format="sec")
    ).isot

    assert final_header_from_single["DATE-BEG"] == headers[0]["DATE-BEG"]
    assert final_header_from_single["DATE-END"] == date_end_from_single


def test_compute_date_keys_compressed_headers(
    compressed_headers_with_dates, recipe_run_id, init_visp_constants_db
):
    """
    Given: A set of compressed headers with different DATE-OBS values
    When: Computing the time over which the headers were taken
    Then: A header with correct DATE-BEG, DATE-END, and DATE-AVG keys is returned
    """
    headers, start_time, exp_time, time_delta = compressed_headers_with_dates
    constants_db = VispConstantsDb()
    init_visp_constants_db(recipe_run_id, constants_db)
    with ScienceCalibration(
        recipe_run_id=recipe_run_id, workflow_name="science_calibration", workflow_version="VX.Y"
    ) as task:
        final_header = task.compute_date_keys(headers)
        final_header_from_single = task.compute_date_keys(headers[0])

    date_end = (
        Time(start_time)
        + (len(headers) - 1) * TimeDelta(time_delta, format="sec")
        + TimeDelta(exp_time / 1000.0, format="sec")
    ).isot

    assert final_header["DATE-BEG"] == start_time
    assert final_header["DATE-END"] == date_end

    date_end_from_single = (
        Time(headers[0]["DATE-BEG"]) + TimeDelta(exp_time / 1000.0, format="sec")
    ).isot

    assert final_header_from_single["DATE-BEG"] == headers[0]["DATE-BEG"]
    assert final_header_from_single["DATE-END"] == date_end_from_single


@pytest.mark.parametrize(
    "shifts, expected",
    # Shifts have shape (num_beams, num_modstates, 2)
    # So the inner-most lists below (e.g., [5.0, 6.0]) correspond to [x_shift, y_shit]
    [
        (
            np.array(
                [  # mod1        mod2        mod3
                    [[0.0, 0.0], [1.0, 2.0], [5.0, 6.0]],  # Beam 1
                    [[1.0, 2.0], [11.0, 10.0], [3.0, 2.0]],  # Beam 2
                ]
            ),
            [slice(11, None, None), slice(10, None, None)],
        ),
        (
            np.array(
                [
                    [[0.0, 0.0], [-1.0, -2.0], [-5.0, -6.0]],  # Beam 1
                    [[-1.0, -2.0], [-11.0, -10.0], [-3.0, -2.0]],  # Beam 2
                ]
            ),
            [slice(0, -11, None), slice(0, -10, None)],
        ),
        (
            np.array(
                [
                    [[0.0, 0.0], [10.0, 2.0], [5.0, 6.0]],  # Beam 1
                    [[1.0, 2.0], [-11.0, 10.0], [-3.0, -2.0]],  # Beam 2
                ]
            ),
            [slice(10, -11, None), slice(10, -2, None)],
        ),
    ],
    ids=["All positive", "All negative", "Positive and negative"],
)
def test_beam_overlap_slice(calibration_collection_with_geo_shifts, expected):
    """
    Given: A CalibrationCollection object with populated state_offsets
    When: Computing the overlapping beam slices
    Then: The correct values are returned
    """
    calibrations = calibration_collection_with_geo_shifts
    x_slice, y_slice = calibrations.beams_overlap_slice

    assert x_slice == expected[0]
    assert y_slice == expected[1]


def test_combine_beams(
    science_calibration_task,
    calibrated_array_and_header_dicts,
    calibration_collection_with_full_overlap_slice,
):
    """
    Given: A ScienceCalibration task and set of calibrated array data
    When: Combining the two beams
    Then: The correct result is returned
    """
    task = science_calibration_task[0]
    array_dict, header_dict = calibrated_array_and_header_dicts
    result = task.combine_beams(
        array_dict=array_dict,
        header_dict=header_dict,
        calibrations=calibration_collection_with_full_overlap_slice,
    )
    assert isinstance(result, VispL0FitsAccess)
    data = result.data

    x = np.arange(1, 5)
    if task.constants.correct_for_polarization:
        expected_I = np.ones((10, 10)) * 2.5
        expected_Q = np.ones((10, 10)) * (x[1] / x[0] + x[-2] / x[-1]) / 2.0 * 2.5
        expected_U = np.ones((10, 10)) * (x[2] / x[0] + x[-3] / x[-1]) / 2.0 * 2.5
        expected_V = np.ones((10, 10)) * (x[3] / x[0] + x[-4] / x[-1]) / 2.0 * 2.5
        expected = np.dstack([expected_I, expected_Q, expected_U, expected_V])

    else:
        expected = np.ones((10, 10, 4)) * 2.5

    np.testing.assert_array_equal(data, expected)
