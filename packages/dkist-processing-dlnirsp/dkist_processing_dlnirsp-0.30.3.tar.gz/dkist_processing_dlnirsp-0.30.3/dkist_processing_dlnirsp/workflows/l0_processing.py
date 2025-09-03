"""DLNIRSP raw data processing workflow."""

from dkist_processing_common.tasks import PublishCatalogAndQualityMessages
from dkist_processing_common.tasks import QualityL1Metrics
from dkist_processing_common.tasks import SubmitDatasetMetadata
from dkist_processing_common.tasks import Teardown
from dkist_processing_common.tasks import TransferL0Data
from dkist_processing_common.tasks import TransferL1Data
from dkist_processing_core import ResourceQueue
from dkist_processing_core import Workflow

from dkist_processing_dlnirsp.tasks import AssembleDlnirspMovie
from dkist_processing_dlnirsp.tasks import BadPixelCalibration
from dkist_processing_dlnirsp.tasks import DarkCalibration
from dkist_processing_dlnirsp.tasks import DlnirspAssembleQualityData
from dkist_processing_dlnirsp.tasks import DlnirspL0QualityMetrics
from dkist_processing_dlnirsp.tasks import DlnirspL1QualityMetrics
from dkist_processing_dlnirsp.tasks import DlnirspWriteL1Frame
from dkist_processing_dlnirsp.tasks import GeometricCalibration
from dkist_processing_dlnirsp.tasks import IfuDriftCalibration
from dkist_processing_dlnirsp.tasks import InstrumentPolarizationCalibration
from dkist_processing_dlnirsp.tasks import LampCalibration
from dkist_processing_dlnirsp.tasks import LinearityCorrection
from dkist_processing_dlnirsp.tasks import MakeDlnirspMovieFrames
from dkist_processing_dlnirsp.tasks import ParseL0DlnirspLinearizedData
from dkist_processing_dlnirsp.tasks import ParseL0DlnirspRampData
from dkist_processing_dlnirsp.tasks import ScienceCalibration
from dkist_processing_dlnirsp.tasks import SolarCalibration
from dkist_processing_dlnirsp.tasks import WavelengthCalibration

l0_pipeline = Workflow(
    category="dlnirsp",
    input_data="l0",
    output_data="l1",
    workflow_package=__package__,
)

l0_pipeline.add_node(task=TransferL0Data, upstreams=None)

# Science flow
l0_pipeline.add_node(task=ParseL0DlnirspRampData, upstreams=TransferL0Data)
l0_pipeline.add_node(task=LinearityCorrection, upstreams=ParseL0DlnirspRampData)
l0_pipeline.add_node(task=ParseL0DlnirspLinearizedData, upstreams=LinearityCorrection)
l0_pipeline.add_node(task=DarkCalibration, upstreams=ParseL0DlnirspLinearizedData)
l0_pipeline.add_node(task=IfuDriftCalibration, upstreams=DarkCalibration)
l0_pipeline.add_node(task=LampCalibration, upstreams=DarkCalibration)
l0_pipeline.add_node(task=BadPixelCalibration, upstreams=[LampCalibration, IfuDriftCalibration])
l0_pipeline.add_node(task=GeometricCalibration, upstreams=[IfuDriftCalibration, LampCalibration])
l0_pipeline.add_node(task=WavelengthCalibration, upstreams=GeometricCalibration)
l0_pipeline.add_node(task=SolarCalibration, upstreams=GeometricCalibration)
l0_pipeline.add_node(
    task=InstrumentPolarizationCalibration,
    resource_queue=ResourceQueue.HIGH_MEMORY,
    upstreams=BadPixelCalibration,
)
l0_pipeline.add_node(
    task=ScienceCalibration, upstreams=[InstrumentPolarizationCalibration, SolarCalibration]
)
l0_pipeline.add_node(
    task=DlnirspWriteL1Frame, upstreams=[WavelengthCalibration, ScienceCalibration]
)

# Movie flow
l0_pipeline.add_node(task=MakeDlnirspMovieFrames, upstreams=ScienceCalibration)
l0_pipeline.add_node(task=AssembleDlnirspMovie, upstreams=MakeDlnirspMovieFrames)

# Quality flow
l0_pipeline.add_node(task=DlnirspL0QualityMetrics, upstreams=ParseL0DlnirspLinearizedData)
l0_pipeline.add_node(task=DlnirspL1QualityMetrics, upstreams=ScienceCalibration)
l0_pipeline.add_node(task=QualityL1Metrics, upstreams=ScienceCalibration)
l0_pipeline.add_node(
    task=DlnirspAssembleQualityData,
    upstreams=[DlnirspL0QualityMetrics, DlnirspL1QualityMetrics, QualityL1Metrics],
)

# Output flow
l0_pipeline.add_node(task=TransferL1Data, upstreams=[DlnirspWriteL1Frame, AssembleDlnirspMovie])
l0_pipeline.add_node(
    task=SubmitDatasetMetadata,
    upstreams=[DlnirspWriteL1Frame, DlnirspAssembleQualityData, AssembleDlnirspMovie],
)
l0_pipeline.add_node(
    task=PublishCatalogAndQualityMessages, upstreams=[TransferL1Data, SubmitDatasetMetadata]
)

l0_pipeline.add_node(task=Teardown, upstreams=PublishCatalogAndQualityMessages)
