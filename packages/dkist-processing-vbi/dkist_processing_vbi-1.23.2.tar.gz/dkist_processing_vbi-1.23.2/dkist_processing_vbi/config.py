"""Configuration for the dkist-processing-vbi package and the logging thereof."""

from dkist_processing_common.config import DKISTProcessingCommonConfiguration


class DKISTProcessingVBIConfigurations(DKISTProcessingCommonConfiguration):
    """Configurations custom to the dkist-processing-vbi package."""

    pass  # nothing custom yet


dkist_processing_vbi_configurations = DKISTProcessingVBIConfigurations()
dkist_processing_vbi_configurations.log_configurations()
