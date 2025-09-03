"""Configurations for the dkist-processing-test package."""

from dkist_processing_common.config import DKISTProcessingCommonConfiguration


class DKISTProcessingTestConfigurations(DKISTProcessingCommonConfiguration):
    pass  # nothing custom yet


dkist_processing_test_configurations = DKISTProcessingTestConfigurations()
dkist_processing_test_configurations.log_configurations()
