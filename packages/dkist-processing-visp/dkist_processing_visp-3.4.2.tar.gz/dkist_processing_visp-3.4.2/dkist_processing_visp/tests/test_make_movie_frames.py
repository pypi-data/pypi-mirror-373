import pytest
from astropy.io import fits
from dkist_processing_common._util.scratch import WorkflowFileSystem

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.tasks.make_movie_frames import MakeVispMovieFrames
from dkist_processing_visp.tests.conftest import VispConstantsDb
from dkist_processing_visp.tests.conftest import write_calibrated_frames_to_task


@pytest.fixture(scope="function")
def movie_frames_task(tmp_path, recipe_run_id, init_visp_constants_db):
    num_steps = 3
    num_maps = 2
    constants_db = VispConstantsDb(NUM_MAP_SCANS=num_maps, NUM_RASTER_STEPS=num_steps)
    init_visp_constants_db(recipe_run_id, constants_db)
    with MakeVispMovieFrames(
        recipe_run_id=recipe_run_id, workflow_name="make_movie_frames", workflow_version="VX.Y"
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            yield task, num_maps, num_steps
        except:
            raise
        finally:
            task._purge()


@pytest.mark.parametrize("pol_mode", ["observe_polarimetric", "observe_intensity"])
def test_make_movie_frames(movie_frames_task, pol_mode, mocker, fake_gql_client):
    """
    Given: A MakeVispMovieFrames task
    When: Calling the task instance
    Then: a fits file is made for each raster scan containing the movie frame for that scan
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task, num_maps, num_steps = movie_frames_task
    spectral_size = 3
    spatial_size = 4
    data_shape = (spatial_size, spectral_size)
    write_calibrated_frames_to_task(
        task=task, num_maps=num_maps, num_steps=num_steps, data_shape=data_shape, pol_mode=pol_mode
    )

    expected_movie_fram_shape = (spectral_size, num_steps)
    if pol_mode == "observe_polarimetric":
        # Multiple by 2 because a single map is (axis_length, steps) but there are 4 stokes in a 2x2 array
        expected_movie_fram_shape = (spectral_size * 2, num_steps * 2)

    task()
    assert len(list(task.read(tags=[VispTag.movie_frame()]))) == num_maps
    for filepath in task.read(tags=[VispTag.movie_frame()]):
        assert filepath.exists()
        hdul = fits.open(filepath)
        assert hdul[0].header["INSTRUME"] == "VISP"
        assert hdul[0].data.shape == expected_movie_fram_shape
