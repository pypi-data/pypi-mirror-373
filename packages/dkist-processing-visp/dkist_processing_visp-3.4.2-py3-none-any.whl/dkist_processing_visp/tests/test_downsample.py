import numpy as np
import pytest
import skimage.measure as skime

from dkist_processing_visp.tasks.mixin.downsample import DownsampleMixin
from dkist_processing_visp.tasks.visp_base import VispTaskBase
from dkist_processing_visp.tests.conftest import VispConstantsDb
from dkist_processing_visp.tests.conftest import VispInputDatasetParameterValues


@pytest.fixture()
def task_with_downsample_mixin(
    recipe_run_id, init_visp_constants_db, assign_input_dataset_doc_to_task
):
    class TaskWithDownsample(VispTaskBase, DownsampleMixin):
        def run(self) -> None:
            pass

    constants_db = VispConstantsDb()
    init_visp_constants_db(recipe_run_id, constants_db)
    task = TaskWithDownsample(
        recipe_run_id=recipe_run_id,
        workflow_name="do_stuff",
        workflow_version="VX.Y",
    )
    assign_input_dataset_doc_to_task(task, VispInputDatasetParameterValues())

    yield task
    task._purge()


@pytest.fixture(scope="session")
def dummy_array() -> np.ndarray:
    return np.random.random((100, 2560))


def test_downsample_spatial_local_median(task_with_downsample_mixin, dummy_array):
    """
    Given: A 2-dimensional array
    When: Downsampling the spatial dimension with the numpy axis trick
    Then: The result is the same as calling scikit-image block reduce on the large array
    """
    task = task_with_downsample_mixin

    spat_block = dummy_array.shape[-1] // task.parameters.background_num_spatial_bins
    expected = skime.block_reduce(dummy_array, block_size=(1, spat_block), func=np.median)
    observed = task.downsample_spatial_dimension_local_median(
        dummy_array, task.parameters.background_num_spatial_bins
    )

    assert np.array_equal(expected, observed)


def test_looping_spatial_resample_fail_on_bad_bin_param(task_with_downsample_mixin, dummy_array):
    """
    Given: A 2-dimensional array
    When: Downsampling the spatial dimension with a non-integer bin divisor
    Then: An error is raised
    """
    task = task_with_downsample_mixin

    bad_bin_number = dummy_array.shape[-1] / 2 + 1

    with pytest.raises(ValueError):
        observed = task.downsample_spatial_dimension_local_median(dummy_array, bad_bin_number)
