import pytest
from dkist_processing_common._util.scratch import WorkflowFileSystem

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.tasks.assemble_movie import AssembleVispMovie
from dkist_processing_visp.tests.conftest import VispConstantsDb
from dkist_processing_visp.tests.conftest import write_output_frames_to_task
from dkist_processing_visp.tests.header_models import VispHeadersValidObserveFrames


def tag_on_map_scan(frame: VispHeadersValidObserveFrames):
    map_scan = frame.current_map
    return [VispTag.map_scan(map_scan)]


def write_movie_frames_to_task(task, num_maps: int):
    dataset = VispHeadersValidObserveFrames(
        array_shape=(1, 100, 100),
        time_delta=1.0,
        num_maps=num_maps,
        num_raster_steps=1,
        num_modstates=1,
    )

    write_output_frames_to_task(
        task=task,
        frame_generator=dataset,
        extra_tags=[VispTag.movie_frame()],
        tag_func=tag_on_map_scan,
    )


@pytest.fixture(scope="function")
def assemble_task_with_tagged_movie_frames(tmp_path, recipe_run_id, init_visp_constants_db):
    num_map_scans = 10
    init_visp_constants_db(recipe_run_id, VispConstantsDb(NUM_MAP_SCANS=num_map_scans))
    with AssembleVispMovie(
        recipe_run_id=recipe_run_id, workflow_name="vbi_make_movie_frames", workflow_version="VX.Y"
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            yield task, num_map_scans
        except:
            raise
        finally:
            task._purge()


def test_assemble_movie(assemble_task_with_tagged_movie_frames, mocker, fake_gql_client):
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task, num_maps = assemble_task_with_tagged_movie_frames
    write_movie_frames_to_task(task, num_maps)
    task()
    movie_file = list(task.read(tags=[VispTag.movie()]))
    assert len(movie_file) == 1
    assert movie_file[0].exists()
    # import os
    # os.system(f"cp {movie_file[0]} foo.mp4")
