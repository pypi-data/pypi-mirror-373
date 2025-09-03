"""Cryo SP raw data processing workflow."""

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
from dkist_processing_cryonirsp.tasks import CryonirspL0QualityMetrics
from dkist_processing_cryonirsp.tasks import CryonirspL1QualityMetrics
from dkist_processing_cryonirsp.tasks import DarkCalibration
from dkist_processing_cryonirsp.tasks import LampGainCalibration
from dkist_processing_cryonirsp.tasks import LinearityCorrection
from dkist_processing_cryonirsp.tasks import MakeCryonirspMovieFrames
from dkist_processing_cryonirsp.tasks import ParseL0CryonirspRampData
from dkist_processing_cryonirsp.tasks import SPBeamBoundariesCalibration
from dkist_processing_cryonirsp.tasks import SPGeometricCalibration
from dkist_processing_cryonirsp.tasks import SPInstrumentPolarizationCalibration
from dkist_processing_cryonirsp.tasks import SPScienceCalibration
from dkist_processing_cryonirsp.tasks import SPSolarGainCalibration
from dkist_processing_cryonirsp.tasks import SPWavelengthCalibration
from dkist_processing_cryonirsp.tasks import SPWriteL1Frame
from dkist_processing_cryonirsp.tasks.l1_output_data import SPAssembleQualityData
from dkist_processing_cryonirsp.tasks.parse import ParseL0CryonirspSPLinearizedData

l0_pipeline = Workflow(
    category="cryonirsp",
    input_data="l0",
    output_data="l1",
    detail="sp",
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
l0_pipeline.add_node(task=ParseL0CryonirspSPLinearizedData, upstreams=LinearityCorrection)
l0_pipeline.add_node(task=BadPixelMapCalibration, upstreams=ParseL0CryonirspSPLinearizedData)
l0_pipeline.add_node(task=SPBeamBoundariesCalibration, upstreams=BadPixelMapCalibration)
l0_pipeline.add_node(task=DarkCalibration, upstreams=SPBeamBoundariesCalibration)
l0_pipeline.add_node(task=LampGainCalibration, upstreams=DarkCalibration)
l0_pipeline.add_node(task=SPGeometricCalibration, upstreams=LampGainCalibration)
l0_pipeline.add_node(task=SPSolarGainCalibration, upstreams=SPGeometricCalibration)
l0_pipeline.add_node(task=SPWavelengthCalibration, upstreams=SPSolarGainCalibration)
l0_pipeline.add_node(task=SPInstrumentPolarizationCalibration, upstreams=SPSolarGainCalibration)
l0_pipeline.add_node(
    task=SPScienceCalibration,
    upstreams=[SPInstrumentPolarizationCalibration, SPWavelengthCalibration],
)
l0_pipeline.add_node(task=SPWriteL1Frame, upstreams=SPScienceCalibration)

# Movie flow
l0_pipeline.add_node(task=MakeCryonirspMovieFrames, upstreams=SPScienceCalibration)
l0_pipeline.add_node(task=AssembleCryonirspMovie, upstreams=MakeCryonirspMovieFrames)

# Quality flow
l0_pipeline.add_node(task=CryonirspL0QualityMetrics, upstreams=ParseL0CryonirspSPLinearizedData)
l0_pipeline.add_node(task=QualityL1Metrics, upstreams=SPScienceCalibration)
l0_pipeline.add_node(task=CryonirspL1QualityMetrics, upstreams=SPScienceCalibration)
l0_pipeline.add_node(
    task=SPAssembleQualityData,
    upstreams=[CryonirspL0QualityMetrics, QualityL1Metrics, CryonirspL1QualityMetrics],
)

# Output flow
l0_pipeline.add_node(
    task=SubmitDatasetMetadata,
    upstreams=[SPWriteL1Frame, SPAssembleQualityData, AssembleCryonirspMovie],
)
l0_pipeline.add_node(task=TransferL1Data, upstreams=[SPWriteL1Frame, AssembleCryonirspMovie])
l0_pipeline.add_node(
    task=PublishCatalogAndQualityMessages, upstreams=[SubmitDatasetMetadata, TransferL1Data]
)

# goodbye
l0_pipeline.add_node(task=Teardown, upstreams=PublishCatalogAndQualityMessages)
