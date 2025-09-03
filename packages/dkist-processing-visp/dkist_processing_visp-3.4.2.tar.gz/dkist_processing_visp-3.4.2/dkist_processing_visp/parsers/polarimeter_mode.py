"""ViSP polarimeter mode parser."""

from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.parsers.unique_bud import TaskUniqueBud

from dkist_processing_visp.models.constants import VispBudName


class PolarimeterModeBud(TaskUniqueBud):
    """Bud to find the ViSP polarimeter mode."""

    def __init__(self):
        super().__init__(
            constant_name=VispBudName.polarimeter_mode.value,
            metadata_key="polarimeter_mode",
            ip_task_types=TaskName.observe.value,
        )
