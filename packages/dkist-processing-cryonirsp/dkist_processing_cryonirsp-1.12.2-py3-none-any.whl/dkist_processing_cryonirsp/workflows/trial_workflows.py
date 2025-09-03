"""Workflows for trial runs (i.e., not Production)."""

from dkist_processing_common.tasks import CreateTrialAsdf
from dkist_processing_common.tasks import CreateTrialDatasetInventory
from dkist_processing_common.tasks import CreateTrialQualityReport
from dkist_processing_common.tasks import QualityL1Metrics
from dkist_processing_common.tasks import TransferL0Data
from dkist_processing_common.tasks import TransferTrialData
from dkist_processing_common.tasks import TrialTeardown
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
from dkist_processing_cryonirsp.tasks import SPBeamBoundariesCalibration
from dkist_processing_cryonirsp.tasks import SPGeometricCalibration
from dkist_processing_cryonirsp.tasks import SPInstrumentPolarizationCalibration
from dkist_processing_cryonirsp.tasks import SPScienceCalibration
from dkist_processing_cryonirsp.tasks import SPSolarGainCalibration
from dkist_processing_cryonirsp.tasks import SPWavelengthCalibration
from dkist_processing_cryonirsp.tasks import SPWriteL1Frame
from dkist_processing_cryonirsp.tasks.l1_output_data import CIAssembleQualityData
from dkist_processing_cryonirsp.tasks.l1_output_data import SPAssembleQualityData
from dkist_processing_cryonirsp.tasks.parse import ParseL0CryonirspCILinearizedData
from dkist_processing_cryonirsp.tasks.parse import ParseL0CryonirspSPLinearizedData

full_trial_ci_pipeline = Workflow(
    category="cryonirsp",
    input_data="l0",
    output_data="l1",
    detail="ci-full-trial",
    workflow_package=__package__,
)
full_trial_ci_pipeline.add_node(task=TransferL0Data, upstreams=None)

# Science flow
full_trial_ci_pipeline.add_node(task=ParseL0CryonirspRampData, upstreams=TransferL0Data)
full_trial_ci_pipeline.add_node(
    task=LinearityCorrection,
    resource_queue=ResourceQueue.HIGH_MEMORY,
    upstreams=ParseL0CryonirspRampData,
)
full_trial_ci_pipeline.add_node(
    task=ParseL0CryonirspCILinearizedData, upstreams=LinearityCorrection
)
full_trial_ci_pipeline.add_node(
    task=BadPixelMapCalibration, upstreams=ParseL0CryonirspCILinearizedData
)
full_trial_ci_pipeline.add_node(task=CIBeamBoundariesCalibration, upstreams=BadPixelMapCalibration)
full_trial_ci_pipeline.add_node(task=DarkCalibration, upstreams=CIBeamBoundariesCalibration)
full_trial_ci_pipeline.add_node(task=CISolarGainCalibration, upstreams=DarkCalibration)
full_trial_ci_pipeline.add_node(
    task=CIInstrumentPolarizationCalibration, upstreams=CISolarGainCalibration
)
full_trial_ci_pipeline.add_node(
    task=CIScienceCalibration, upstreams=CIInstrumentPolarizationCalibration
)
full_trial_ci_pipeline.add_node(task=CIWriteL1Frame, upstreams=CIScienceCalibration)

# Movie flow
full_trial_ci_pipeline.add_node(task=MakeCryonirspMovieFrames, upstreams=CIScienceCalibration)
full_trial_ci_pipeline.add_node(task=AssembleCryonirspMovie, upstreams=MakeCryonirspMovieFrames)

# Quality flow
full_trial_ci_pipeline.add_node(
    task=CryonirspL0QualityMetrics, upstreams=ParseL0CryonirspCILinearizedData
)
full_trial_ci_pipeline.add_node(task=QualityL1Metrics, upstreams=CIScienceCalibration)
full_trial_ci_pipeline.add_node(task=CryonirspL1QualityMetrics, upstreams=CIScienceCalibration)
full_trial_ci_pipeline.add_node(
    task=CIAssembleQualityData,
    upstreams=[CryonirspL0QualityMetrics, QualityL1Metrics, CryonirspL1QualityMetrics],
)

# Trial data generation
full_trial_ci_pipeline.add_node(
    task=CreateTrialDatasetInventory, upstreams=CIWriteL1Frame, pip_extras=["inventory"]
)
full_trial_ci_pipeline.add_node(task=CreateTrialAsdf, upstreams=CIWriteL1Frame, pip_extras=["asdf"])
full_trial_ci_pipeline.add_node(
    task=CreateTrialQualityReport, upstreams=CIAssembleQualityData, pip_extras=["quality"]
)

# Output flow
full_trial_ci_pipeline.add_node(
    task=TransferTrialData,
    upstreams=[
        CreateTrialDatasetInventory,
        CreateTrialAsdf,
        CreateTrialQualityReport,
        AssembleCryonirspMovie,
    ],
)

# goodbye
full_trial_ci_pipeline.add_node(task=TrialTeardown, upstreams=TransferTrialData)

#######################
#######################
full_trial_sp_pipeline = Workflow(
    category="cryonirsp",
    input_data="l0",
    output_data="l1",
    detail="sp-full-trial",
    workflow_package=__package__,
)
full_trial_sp_pipeline.add_node(task=TransferL0Data, upstreams=None)

# Science flow
full_trial_sp_pipeline.add_node(task=ParseL0CryonirspRampData, upstreams=TransferL0Data)
full_trial_sp_pipeline.add_node(
    task=LinearityCorrection,
    resource_queue=ResourceQueue.HIGH_MEMORY,
    upstreams=ParseL0CryonirspRampData,
)
full_trial_sp_pipeline.add_node(
    task=ParseL0CryonirspSPLinearizedData, upstreams=LinearityCorrection
)
full_trial_sp_pipeline.add_node(
    task=BadPixelMapCalibration, upstreams=ParseL0CryonirspSPLinearizedData
)
full_trial_sp_pipeline.add_node(task=SPBeamBoundariesCalibration, upstreams=BadPixelMapCalibration)
full_trial_sp_pipeline.add_node(task=DarkCalibration, upstreams=SPBeamBoundariesCalibration)
full_trial_sp_pipeline.add_node(task=LampGainCalibration, upstreams=DarkCalibration)
full_trial_sp_pipeline.add_node(task=SPGeometricCalibration, upstreams=LampGainCalibration)
full_trial_sp_pipeline.add_node(task=SPSolarGainCalibration, upstreams=SPGeometricCalibration)
full_trial_sp_pipeline.add_node(task=SPWavelengthCalibration, upstreams=SPSolarGainCalibration)

full_trial_sp_pipeline.add_node(
    task=SPInstrumentPolarizationCalibration, upstreams=SPSolarGainCalibration
)
full_trial_sp_pipeline.add_node(
    task=SPScienceCalibration,
    upstreams=[SPInstrumentPolarizationCalibration, SPWavelengthCalibration],
)
full_trial_sp_pipeline.add_node(task=SPWriteL1Frame, upstreams=SPScienceCalibration)

# Movie flow
full_trial_sp_pipeline.add_node(task=MakeCryonirspMovieFrames, upstreams=SPScienceCalibration)
full_trial_sp_pipeline.add_node(task=AssembleCryonirspMovie, upstreams=MakeCryonirspMovieFrames)

# Quality flow
full_trial_sp_pipeline.add_node(
    task=CryonirspL0QualityMetrics, upstreams=ParseL0CryonirspSPLinearizedData
)
full_trial_sp_pipeline.add_node(task=QualityL1Metrics, upstreams=SPScienceCalibration)
full_trial_sp_pipeline.add_node(task=CryonirspL1QualityMetrics, upstreams=SPScienceCalibration)
full_trial_sp_pipeline.add_node(
    task=SPAssembleQualityData,
    upstreams=[CryonirspL0QualityMetrics, QualityL1Metrics, CryonirspL1QualityMetrics],
)

# Trial data generation
full_trial_sp_pipeline.add_node(
    task=CreateTrialDatasetInventory, upstreams=SPWriteL1Frame, pip_extras=["inventory"]
)
full_trial_sp_pipeline.add_node(task=CreateTrialAsdf, upstreams=SPWriteL1Frame, pip_extras=["asdf"])
full_trial_sp_pipeline.add_node(
    task=CreateTrialQualityReport, upstreams=SPAssembleQualityData, pip_extras=["quality"]
)

# Output flow
full_trial_sp_pipeline.add_node(
    task=TransferTrialData,
    upstreams=[
        CreateTrialDatasetInventory,
        CreateTrialAsdf,
        CreateTrialQualityReport,
        AssembleCryonirspMovie,
    ],
)

# goodbye
full_trial_sp_pipeline.add_node(task=TrialTeardown, upstreams=TransferTrialData)
