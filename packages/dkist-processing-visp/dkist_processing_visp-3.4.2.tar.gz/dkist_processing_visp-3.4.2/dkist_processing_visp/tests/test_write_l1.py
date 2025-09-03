import astropy.units as u
import pytest
from astropy.io import fits
from astropy.time import Time
from dkist_fits_specifications import __version__ as spec_version
from dkist_header_validator import spec214_validator
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.models.wavelength import WavelengthRange
from dkist_spectral_lines import get_closest_spectral_line
from dkist_spectral_lines import get_spectral_lines

from dkist_processing_visp.tasks.write_l1 import VispWriteL1Frame
from dkist_processing_visp.tests.conftest import VispConstantsDb
from dkist_processing_visp.tests.conftest import write_calibrated_frames_to_task


@pytest.fixture(
    scope="function",
    params=[("HPLT-TAN", "AWAV"), ("AWAV", "HPLT-TAN")],
    ids=["correct wcs axis order", "incorrect wcs axis order"],
)
def wcs_axis_names(request):
    return request.param


@pytest.fixture
def write_l1_task(
    recipe_run_id,
    init_visp_constants_db,
    pol_mode,
):
    constants_db = VispConstantsDb(
        INSTRUMENT="VISP",
        AVERAGE_CADENCE=10,
        MINIMUM_CADENCE=10,
        MAXIMUM_CADENCE=10,
        VARIANCE_CADENCE=0,
        NUM_MAP_SCANS=1,
        NUM_RASTER_STEPS=2,
        SPECTRAL_LINE="VISP Ca II H",
        POLARIMETER_MODE=pol_mode,
        NUM_MODSTATES=1 if pol_mode == "observe_intensity" else 10,
    )
    init_visp_constants_db(recipe_run_id, constants_db)
    with VispWriteL1Frame(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:

        yield task

        task._purge()


@pytest.fixture
def wavelength_range():
    return WavelengthRange(min=656.0 * u.nm, max=677.0 * u.nm)


@pytest.fixture
def mocked_get_wavelength_range(wavelength_range):
    def get_wavelength_range(self, header):
        return wavelength_range

    return get_wavelength_range


@pytest.mark.parametrize("pol_mode", ["observe_polarimetric", "observe_intensity"])
def test_write_l1_frame(
    write_l1_task,
    wcs_axis_names,
    pol_mode,
    wavelength_range,
    mocked_get_wavelength_range,
    mocker,
    fake_gql_client,
):
    """
    :Given: a write L1 task
    :When: running the task
    :Then: no errors are raised
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    mocker.patch(
        "dkist_processing_visp.tasks.write_l1.VispWriteL1Frame.get_wavelength_range",
        mocked_get_wavelength_range,
    )
    task = write_l1_task

    stokes_params = ["I"]
    if pol_mode == "observe_polarimetric":
        stokes_params += ["Q", "U", "V"]

    expected_spectral_lines = get_spectral_lines(
        wavelength_min=wavelength_range.min,
        wavelength_max=wavelength_range.max,
    )
    expected_waveband = get_closest_spectral_line(
        wavelength=656.3 * u.nm
    ).name  # From VispHeaders fixture

    write_calibrated_frames_to_task(
        task, pol_mode=pol_mode, wcs_axis_names=wcs_axis_names, data_shape=(10, 10)
    )

    task()
    for stokes_param in stokes_params:
        files = list(task.read(tags=[Tag.frame(), Tag.output(), Tag.stokes(stokes_param)]))
        assert len(files) == 1
        for file in files:
            assert file.exists
            assert spec214_validator.validate(file, extra=False)
            hdu_list = fits.open(file)
            header = hdu_list[1].header
            assert len(hdu_list) == 2  # Primary, CompImage
            assert type(hdu_list[0]) is fits.PrimaryHDU
            assert type(hdu_list[1]) is fits.CompImageHDU
            assert header["DTYPE1"] == "SPATIAL"
            assert header["DTYPE2"] == "SPECTRAL"
            assert header["DTYPE3"] == "SPATIAL"
            assert header["DAAXES"] == 2
            if len(stokes_params) == 1:
                assert "DNAXIS4" not in header
                assert header["DNAXIS"] == 3
                assert header["DEAXES"] == 1
            else:
                assert header["DNAXIS4"] == 4
                assert header["DNAXIS"] == 4
                assert header["DEAXES"] == 2
            assert header["INFO_URL"] == task.docs_base_url
            assert header["HEADVERS"] == spec_version
            assert (
                header["HEAD_URL"]
                == f"{task.docs_base_url}/projects/data-products/en/v{spec_version}"
            )
            calvers = task.version_from_module_name()
            assert header["CALVERS"] == calvers
            assert (
                header["CAL_URL"]
                == f"{task.docs_base_url}/projects/{task.constants.instrument.lower()}/en/v{calvers}/{task.workflow_name}.html"
            )
            calibrated_file = next(
                task.read(tags=[Tag.frame(), Tag.calibrated(), Tag.stokes(stokes_param)])
            )
            cal_header = fits.open(calibrated_file)[0].header

            # Make sure we didn't overwrite pre-computed DATE-BEG and DATE-END keys
            assert header["DATE-BEG"] == cal_header["DATE-BEG"]
            assert header["DATE-END"] == cal_header["DATE-END"]
            date_avg = (
                (Time(header["DATE-END"], precision=6) - Time(header["DATE-BEG"], precision=6)) / 2
                + Time(header["DATE-BEG"], precision=6)
            ).isot
            assert header["DATE-AVG"] == date_avg
            assert isinstance(header["HLSVERS"], str)
            assert header["PROPID01"] == "PROPID1"
            assert header["PROPID02"] == "PROPID2"
            assert header["EXPRID01"] == "EXPERID1"
            assert header["EXPRID02"] == "EXPERID2"
            assert header["EXPRID03"] == "EXPERID3"
            assert header["WAVEBAND"] == expected_waveband
            assert header["BUNIT"] == ""
            assert (
                header.comments["BUNIT"]
                == "Values are relative to disk center. See calibration docs."
            )
            for i, line in enumerate(expected_spectral_lines, start=1):
                assert header[f"SPECLN{i:02}"] == line.name

            with pytest.raises(KeyError):
                # Make sure no more lines were added
                header[f"SPECLN{i+1:02}"]

            if pol_mode == "observe_polarimetric":
                assert header["CADENCE"] == 100
                assert header["XPOSURE"] == 150
            else:
                assert header["CADENCE"] == 10
                assert header["XPOSURE"] == 15
