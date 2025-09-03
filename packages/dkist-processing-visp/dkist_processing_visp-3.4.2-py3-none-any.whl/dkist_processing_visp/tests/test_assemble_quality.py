from unittest.mock import MagicMock

import pytest

from dkist_processing_visp.tasks.l1_output_data import VispAssembleQualityData


@pytest.fixture
def visp_assemble_quality_data_task(tmp_path, recipe_run_id) -> VispAssembleQualityData:

    with VispAssembleQualityData(
        recipe_run_id=recipe_run_id, workflow_name="visp_assemble_quality", workflow_version="VX.Y"
    ) as task:
        yield task
        task._purge()


@pytest.fixture
def dummy_quality_data() -> list[dict]:
    return [{"dummy_key": "dummy_value"}]


@pytest.fixture
def quality_assemble_data_mock(mocker, dummy_quality_data) -> MagicMock:
    yield mocker.patch(
        "dkist_processing_common.tasks.mixin.quality.QualityMixin.quality_assemble_data",
        return_value=dummy_quality_data,
        autospec=True,
    )


def test_correct_polcal_label_list(visp_assemble_quality_data_task, quality_assemble_data_mock):
    """
    Given: A VispAssembleQualityData task
    When: Calling the task
    Then: The correct polcal_label_list property is passed to .quality_assemble_data
    """
    task = visp_assemble_quality_data_task

    task()
    quality_assemble_data_mock.assert_called_once_with(task, polcal_label_list=["Beam 1", "Beam 2"])
