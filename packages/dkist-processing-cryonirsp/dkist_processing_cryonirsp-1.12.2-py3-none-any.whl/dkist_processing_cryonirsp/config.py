"""Configuration for the dkist-processing-cryonirsp package and the logging thereof."""

from dkist_processing_common.config import DKISTProcessingCommonConfiguration
from pydantic import Field


class DKISTProcessingCryoNIRSPConfigurations(DKISTProcessingCommonConfiguration):
    """Configurations custom to the dkist-processing-cryonirsp package."""

    fts_atlas_data_dir: str | None = Field(
        default=None, description="Common cached directory for a downloaded FTS Atlas."
    )


dkist_processing_cryonirsp_configurations = DKISTProcessingCryoNIRSPConfigurations()
dkist_processing_cryonirsp_configurations.log_configurations()
