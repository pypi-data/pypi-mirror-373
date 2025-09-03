"""ViSP raw data processing workflow."""

from dkist_processing_common.tasks import PublishCatalogAndQualityMessages
from dkist_processing_common.tasks import QualityL1Metrics
from dkist_processing_common.tasks import SubmitDatasetMetadata
from dkist_processing_common.tasks import Teardown
from dkist_processing_common.tasks import TransferL0Data
from dkist_processing_common.tasks import TransferL1Data
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

l0_pipeline = Workflow(
    category="visp",
    input_data="l0",
    output_data="l1",
    workflow_package=__package__,
)
l0_pipeline.add_node(task=TransferL0Data, upstreams=None)

# Science flow
l0_pipeline.add_node(task=ParseL0VispInputData, upstreams=TransferL0Data)
l0_pipeline.add_node(task=DarkCalibration, upstreams=ParseL0VispInputData)
l0_pipeline.add_node(task=BackgroundLightCalibration, upstreams=DarkCalibration)
l0_pipeline.add_node(task=LampCalibration, upstreams=DarkCalibration)
l0_pipeline.add_node(task=GeometricCalibration, upstreams=DarkCalibration)
l0_pipeline.add_node(
    task=SolarCalibration,
    upstreams=[LampCalibration, GeometricCalibration, BackgroundLightCalibration],
)
l0_pipeline.add_node(task=InstrumentPolarizationCalibration, upstreams=SolarCalibration)
l0_pipeline.add_node(task=ScienceCalibration, upstreams=InstrumentPolarizationCalibration)
l0_pipeline.add_node(task=VispWriteL1Frame, upstreams=ScienceCalibration)

# Movie flow
l0_pipeline.add_node(task=MakeVispMovieFrames, upstreams=ScienceCalibration)
l0_pipeline.add_node(task=AssembleVispMovie, upstreams=MakeVispMovieFrames)

# Quality flow
l0_pipeline.add_node(task=VispL0QualityMetrics, upstreams=ParseL0VispInputData)
l0_pipeline.add_node(task=QualityL1Metrics, upstreams=ScienceCalibration)
l0_pipeline.add_node(task=VispL1QualityMetrics, upstreams=ScienceCalibration)
l0_pipeline.add_node(
    task=VispAssembleQualityData,
    upstreams=[VispL0QualityMetrics, QualityL1Metrics, VispL1QualityMetrics],
)

# Output flow
l0_pipeline.add_node(task=TransferL1Data, upstreams=[VispWriteL1Frame, AssembleVispMovie])
l0_pipeline.add_node(
    task=SubmitDatasetMetadata,
    upstreams=[VispWriteL1Frame, VispAssembleQualityData, AssembleVispMovie],
)
l0_pipeline.add_node(
    task=PublishCatalogAndQualityMessages, upstreams=[SubmitDatasetMetadata, TransferL1Data]
)

# goodbye
l0_pipeline.add_node(task=Teardown, upstreams=PublishCatalogAndQualityMessages)
