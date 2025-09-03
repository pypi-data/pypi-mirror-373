"""Configuration for the dkist-processing-visp package and the logging thereof."""

from dkist_processing_common.config import DKISTProcessingCommonConfiguration


class DKISTProcessingVISPConfigurations(DKISTProcessingCommonConfiguration):
    """Configurations custom to the dkist-processing-visp package."""

    pass  # nothing custom yet


dkist_processing_visp_configurations = DKISTProcessingVISPConfigurations()
dkist_processing_visp_configurations.log_configurations()
