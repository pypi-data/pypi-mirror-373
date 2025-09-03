"""Workflows for trial runs (i.e., not Production)."""

from dkist_processing_common.tasks import CreateTrialAsdf
from dkist_processing_common.tasks import CreateTrialDatasetInventory
from dkist_processing_common.tasks import CreateTrialQualityReport
from dkist_processing_common.tasks import QualityL1Metrics
from dkist_processing_common.tasks import TransferL0Data
from dkist_processing_common.tasks import TransferTrialData
from dkist_processing_common.tasks import TrialTeardown
from dkist_processing_core import Workflow

from dkist_processing_visp.tasks import AssembleVispMovie
from dkist_processing_visp.tasks import BackgroundLightCalibration
from dkist_processing_visp.tasks import DarkCalibration
from dkist_processing_visp.tasks import GeometricCalibration
from dkist_processing_visp.tasks import InstrumentPolarizationCalibration
from dkist_processing_visp.tasks import LampCalibration
from dkist_processing_visp.tasks import MakeVispMovieFrames
from dkist_processing_visp.tasks import ParseL0VispInputData
from dkist_processing_visp.tasks import ScienceCalibration
from dkist_processing_visp.tasks import SolarCalibration
from dkist_processing_visp.tasks import VispAssembleQualityData
from dkist_processing_visp.tasks import VispL0QualityMetrics
from dkist_processing_visp.tasks import VispL1QualityMetrics
from dkist_processing_visp.tasks import VispWriteL1Frame

full_trial_pipeline = Workflow(
    category="visp",
    input_data="l0",
    output_data="l1",
    detail="full-trial",
    workflow_package=__package__,
)
full_trial_pipeline.add_node(task=TransferL0Data, upstreams=None)

# Science flow
full_trial_pipeline.add_node(task=ParseL0VispInputData, upstreams=TransferL0Data)
full_trial_pipeline.add_node(task=DarkCalibration, upstreams=ParseL0VispInputData)
full_trial_pipeline.add_node(task=BackgroundLightCalibration, upstreams=DarkCalibration)
full_trial_pipeline.add_node(task=LampCalibration, upstreams=DarkCalibration)
full_trial_pipeline.add_node(task=GeometricCalibration, upstreams=DarkCalibration)
full_trial_pipeline.add_node(
    task=SolarCalibration,
    upstreams=[LampCalibration, GeometricCalibration, BackgroundLightCalibration],
)
full_trial_pipeline.add_node(task=InstrumentPolarizationCalibration, upstreams=SolarCalibration)
full_trial_pipeline.add_node(task=ScienceCalibration, upstreams=InstrumentPolarizationCalibration)
full_trial_pipeline.add_node(task=VispWriteL1Frame, upstreams=ScienceCalibration)

# Movie flow
full_trial_pipeline.add_node(task=MakeVispMovieFrames, upstreams=ScienceCalibration)
full_trial_pipeline.add_node(task=AssembleVispMovie, upstreams=MakeVispMovieFrames)

# Quality flow
full_trial_pipeline.add_node(task=VispL0QualityMetrics, upstreams=ParseL0VispInputData)
full_trial_pipeline.add_node(task=QualityL1Metrics, upstreams=ScienceCalibration)
full_trial_pipeline.add_node(task=VispL1QualityMetrics, upstreams=ScienceCalibration)
full_trial_pipeline.add_node(
    task=VispAssembleQualityData,
    upstreams=[VispL0QualityMetrics, QualityL1Metrics, VispL1QualityMetrics],
)

# Trial data generation
full_trial_pipeline.add_node(
    task=CreateTrialDatasetInventory, upstreams=VispWriteL1Frame, pip_extras=["inventory"]
)
full_trial_pipeline.add_node(task=CreateTrialAsdf, upstreams=VispWriteL1Frame, pip_extras=["asdf"])
full_trial_pipeline.add_node(
    task=CreateTrialQualityReport, upstreams=VispAssembleQualityData, pip_extras=["quality"]
)

# Output
full_trial_pipeline.add_node(
    task=TransferTrialData,
    upstreams=[
        AssembleVispMovie,
        CreateTrialDatasetInventory,
        CreateTrialAsdf,
        CreateTrialQualityReport,
    ],
)

# goodbye
full_trial_pipeline.add_node(task=TrialTeardown, upstreams=TransferTrialData)
