import random
import re
from collections import defaultdict

import numpy as np
import pytest
from astropy.io import fits
from astropy.time import Time
from dkist_header_validator.translator import translate_spec122_to_spec214_l0
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.parsers.single_value_single_key_flower import (
    SingleValueSingleKeyFlower,
)

from dkist_processing_visp.models.constants import VispBudName
from dkist_processing_visp.models.tags import VispStemName
from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.parsers.map_repeats import MapScanFlower
from dkist_processing_visp.parsers.map_repeats import NumMapScansBud
from dkist_processing_visp.parsers.map_repeats import SingleScanStep
from dkist_processing_visp.parsers.raster_step import RasterScanStepFlower
from dkist_processing_visp.parsers.visp_l0_fits_access import VispL0FitsAccess
from dkist_processing_visp.tasks.parse import ParseL0VispInputData
from dkist_processing_visp.tasks.parse import S
from dkist_processing_visp.tests.conftest import VispInputDatasetParameterValues
from dkist_processing_visp.tests.header_models import VispHeadersValidObserveFrames


@pytest.fixture(scope="session")
def complete_map_headers():
    num_steps = 5
    num_modstates = 4
    num_maps = 3
    dataset = VispHeadersValidObserveFrames(
        array_shape=(1, 2, 2),
        time_delta=10,
        num_maps=num_maps,
        num_raster_steps=num_steps,
        num_modstates=num_modstates,
    )
    header_list = [translate_spec122_to_spec214_l0(d.header()) for d in dataset]

    return header_list, num_steps, num_modstates, num_maps


@pytest.fixture()
def organized_fits_access_dict(complete_map_headers):
    all_dict = defaultdict(lambda: defaultdict(list))

    for header in complete_map_headers[0]:
        fits_obj = VispL0FitsAccess.from_header(header)
        all_dict[fits_obj.raster_scan_step][fits_obj.modulator_state].append(fits_obj)

    return all_dict


def write_obs_frames_with_multiple_exp_per_step_to_task(task, num_exp: int):
    array_shape = (1, 2, 2)
    num_maps = 2
    num_steps = 3
    num_modstates = 1
    dataset = VispHeadersValidObserveFrames(
        array_shape=array_shape,
        time_delta=10,
        num_maps=num_maps,
        num_raster_steps=num_steps,
        num_modstates=num_modstates,
    )
    header_list = [translate_spec122_to_spec214_l0(d.header()) for d in dataset]
    for header in header_list:
        hdu = fits.PrimaryHDU(data=np.ones(array_shape), header=fits.Header(header))
        hdul = fits.HDUList([hdu])

        # Make multiple exposures by just writing the same header twice
        for _ in range(num_exp):
            task.write(
                data=hdul, tags=[VispTag.input(), VispTag.frame()], encoder=fits_hdulist_encoder
            )


class ParseTaskJustMapStuff(ParseL0VispInputData):
    @property
    def constant_buds(self) -> list[S]:
        return [NumMapScansBud()]

    @property
    def tag_flowers(self) -> list[S]:
        return [
            MapScanFlower(),
            RasterScanStepFlower(),
            SingleValueSingleKeyFlower(
                tag_stem_name=VispStemName.modstate.value, metadata_key="modulator_state"
            ),
        ]


@pytest.fixture()
def map_only_parse_task(tmp_path_factory, recipe_run_id, assign_input_dataset_doc_to_task):

    with ParseTaskJustMapStuff(
        recipe_run_id=recipe_run_id, workflow_name="parse_map_scans", workflow_version="X.Y.Z"
    ) as task:
        try:
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path_factory.mktemp("map_scan"), recipe_run_id=recipe_run_id
            )
            assign_input_dataset_doc_to_task(task, VispInputDatasetParameterValues())

            yield task

        except:
            raise

        finally:
            task._purge()


def test_singlescanstep_correct(organized_fits_access_dict):
    """
    :Given: A group of FitsAccess objects corresponding to multiple map scans with unique frames
    :When: Using the SingleScanStep object to distill the FitsAccess objects
    :Then: The resulting objects sort correctly and are not equal to each other
    """
    # Test sorting happens correctly
    for modstate_dict in organized_fits_access_dict.values():
        for access_list in modstate_dict.values():
            singlescan_list = [SingleScanStep(o) for o in access_list]
            random.shuffle(singlescan_list)  # Put them out of order
            obj_sort_idx = np.argsort(singlescan_list)
            time_sort_idx = np.argsort([s.date_obs for s in singlescan_list])
            assert np.array_equal(obj_sort_idx, time_sort_idx)

    # Test that the first object from each (raster_step, modstate, date_obs) tuple is unequal to all others
    flat_obj_list = sum(
        sum([list(md.values()) for md in organized_fits_access_dict.values()], []), []
    )
    # I.e., the entire set of values is identical to the unique set of values
    assert len(set(flat_obj_list)) == len(flat_obj_list)


def test_parse_map_repeats(map_only_parse_task, complete_map_headers):
    """
    :Given: A map-parsing task with files that represent complete maps
    :When: Parsing the files
    :Then: The correct number of map scans is inferred and each file is tagged correctly
    """
    task = map_only_parse_task
    complete_headers, num_steps, num_modstates, num_maps = complete_map_headers

    for header in complete_headers:
        hdu = fits.PrimaryHDU(data=np.ones((1, 2, 2)), header=fits.Header(header))
        hdul = fits.HDUList([hdu])
        task.write(data=hdul, tags=[VispTag.input(), VispTag.frame()], encoder=fits_hdulist_encoder)

    task()

    assert task.constants._db_dict[VispBudName.num_map_scans.value] == num_maps
    for step in range(0, num_steps):
        for modstate in range(1, num_modstates + 1):
            files = list(
                task.read(
                    tags=[
                        VispTag.input(),
                        VispTag.frame(),
                        VispTag.raster_step(step),
                        VispTag.modstate(modstate),
                    ]
                )
            )
            assert len(files) == num_maps
            map_scan_tags = [
                [
                    t.replace(f"{VispStemName.map_scan.value}_", "")
                    for t in task.tags(f)
                    if VispStemName.map_scan.value in t
                ][0]
                for f in files
            ]
            time_list = [Time(VispL0FitsAccess.from_path(f).time_obs) for f in files]
            map_idx = np.argsort(map_scan_tags)
            time_idx = np.argsort(time_list)
            assert np.array_equal(time_idx, map_idx)


def test_multiple_exp_per_step_raises_error(
    map_only_parse_task,
):
    """
    :Given: A map-parsing task with data that has multiple exposures per (raster, modstate, map_scan)
    :When: Calling the parse task
    :Then: The correct error is raised
    """
    task = map_only_parse_task
    num_exp = 3
    write_obs_frames_with_multiple_exp_per_step_to_task(task=task, num_exp=num_exp)
    with pytest.raises(
        ValueError,
        match=re.escape(
            f"More than one exposure detected for a single map scan of a single map step. (Randomly chosen step has {num_exp} exposures)."
        ),
    ):
        task()
