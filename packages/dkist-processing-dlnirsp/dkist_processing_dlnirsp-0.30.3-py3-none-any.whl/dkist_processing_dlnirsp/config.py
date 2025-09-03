"""Configuration for the dkist-processing-dlnirsp package and logging thereof."""

from dkist_processing_common.config import DKISTProcessingCommonConfiguration
from pydantic import Field


class DKISTProcessingDLNIRSPConfigurations(DKISTProcessingCommonConfiguration):
    """Configurations custom to the dkist-processing-dlnirsp package."""

    fts_atlas_data_dir: str | None = Field(
        default=None, description="Common cached directory for downloaded FTS Atlas."
    )


dkist_processing_dlnirsp_configurations = DKISTProcessingDLNIRSPConfigurations()
dkist_processing_dlnirsp_configurations.log_configurations()
