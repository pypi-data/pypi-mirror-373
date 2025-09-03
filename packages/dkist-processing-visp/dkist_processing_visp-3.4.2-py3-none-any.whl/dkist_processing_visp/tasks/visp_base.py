"""ViSP base class."""

from abc import ABC

from dkist_processing_common.tasks import WorkflowTaskBase

from dkist_processing_visp.models.constants import VispConstants
from dkist_processing_visp.models.parameters import VispParameters


class VispTaskBase(WorkflowTaskBase, ABC):
    """
    Task class for base ViSP tasks.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs
    """

    # So tab completion shows all the ViSP constants
    constants: VispConstants

    @property
    def constants_model_class(self):
        """Get ViSP pipeline constants."""
        return VispConstants

    def __init__(
        self,
        recipe_run_id: int,
        workflow_name: str,
        workflow_version: str,
    ):
        super().__init__(
            recipe_run_id=recipe_run_id,
            workflow_name=workflow_name,
            workflow_version=workflow_version,
        )
        self.parameters = VispParameters(
            scratch=self.scratch,
            obs_ip_start_time=self.constants.obs_ip_start_time,
            wavelength=self.constants.wavelength,
        )
