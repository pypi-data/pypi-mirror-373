"""Cryo CI raw data processing workflow."""

from dkist_processing_common.tasks import PublishCatalogAndQualityMessages
from dkist_processing_common.tasks import QualityL1Metrics
from dkist_processing_common.tasks import SubmitDatasetMetadata
from dkist_processing_common.tasks import Teardown
from dkist_processing_common.tasks import TransferL0Data
from dkist_processing_common.tasks import TransferL1Data
from dkist_processing_core import ResourceQueue
from dkist_processing_core import Workflow

from dkist_processing_cryonirsp.tasks import AssembleCryonirspMovie
from dkist_processing_cryonirsp.tasks import BadPixelMapCalibration
from dkist_processing_cryonirsp.tasks import CIBeamBoundariesCalibration
from dkist_processing_cryonirsp.tasks import CIInstrumentPolarizationCalibration
from dkist_processing_cryonirsp.tasks import CIScienceCalibration
from dkist_processing_cryonirsp.tasks import CISolarGainCalibration
from dkist_processing_cryonirsp.tasks import CIWriteL1Frame
from dkist_processing_cryonirsp.tasks import CryonirspL0QualityMetrics
from dkist_processing_cryonirsp.tasks import CryonirspL1QualityMetrics
from dkist_processing_cryonirsp.tasks import DarkCalibration
from dkist_processing_cryonirsp.tasks import LampGainCalibration
from dkist_processing_cryonirsp.tasks import LinearityCorrection
from dkist_processing_cryonirsp.tasks import MakeCryonirspMovieFrames
from dkist_processing_cryonirsp.tasks import ParseL0CryonirspRampData
from dkist_processing_cryonirsp.tasks.l1_output_data import CIAssembleQualityData
from dkist_processing_cryonirsp.tasks.parse import ParseL0CryonirspCILinearizedData

l0_pipeline = Workflow(
    category="cryonirsp",
    input_data="l0",
    output_data="l1",
    detail="ci",
    workflow_package=__package__,
)
l0_pipeline.add_node(task=TransferL0Data, upstreams=None)

# Science flow
l0_pipeline.add_node(task=ParseL0CryonirspRampData, upstreams=TransferL0Data)
l0_pipeline.add_node(
    task=LinearityCorrection,
    resource_queue=ResourceQueue.HIGH_MEMORY,
    upstreams=ParseL0CryonirspRampData,
)
l0_pipeline.add_node(task=ParseL0CryonirspCILinearizedData, upstreams=LinearityCorrection)
l0_pipeline.add_node(task=BadPixelMapCalibration, upstreams=ParseL0CryonirspCILinearizedData)
l0_pipeline.add_node(task=CIBeamBoundariesCalibration, upstreams=BadPixelMapCalibration)
l0_pipeline.add_node(task=DarkCalibration, upstreams=CIBeamBoundariesCalibration)
l0_pipeline.add_node(task=CISolarGainCalibration, upstreams=DarkCalibration)
l0_pipeline.add_node(task=CIInstrumentPolarizationCalibration, upstreams=CISolarGainCalibration)
l0_pipeline.add_node(task=CIScienceCalibration, upstreams=CIInstrumentPolarizationCalibration)
l0_pipeline.add_node(task=CIWriteL1Frame, upstreams=CIScienceCalibration)

# Movie flow
l0_pipeline.add_node(task=MakeCryonirspMovieFrames, upstreams=CIScienceCalibration)
l0_pipeline.add_node(task=AssembleCryonirspMovie, upstreams=MakeCryonirspMovieFrames)

# Quality flow
l0_pipeline.add_node(task=CryonirspL0QualityMetrics, upstreams=ParseL0CryonirspCILinearizedData)
l0_pipeline.add_node(task=QualityL1Metrics, upstreams=CIScienceCalibration)
l0_pipeline.add_node(task=CryonirspL1QualityMetrics, upstreams=CIScienceCalibration)
l0_pipeline.add_node(
    task=CIAssembleQualityData,
    upstreams=[CryonirspL0QualityMetrics, QualityL1Metrics, CryonirspL1QualityMetrics],
)

# Output flow
l0_pipeline.add_node(
    task=SubmitDatasetMetadata,
    upstreams=[CIWriteL1Frame, CIAssembleQualityData, AssembleCryonirspMovie],
)
l0_pipeline.add_node(task=TransferL1Data, upstreams=[CIWriteL1Frame, AssembleCryonirspMovie])
l0_pipeline.add_node(
    task=PublishCatalogAndQualityMessages, upstreams=[SubmitDatasetMetadata, TransferL1Data]
)

# goodbye
l0_pipeline.add_node(task=Teardown, upstreams=PublishCatalogAndQualityMessages)
