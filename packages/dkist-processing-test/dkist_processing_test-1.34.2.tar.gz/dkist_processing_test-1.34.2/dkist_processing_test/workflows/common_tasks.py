"""
Workflow which exercises the common tasks in an end to end scenario
"""

from dkist_processing_common.tasks import CreateTrialAsdf
from dkist_processing_common.tasks import CreateTrialDatasetInventory
from dkist_processing_common.tasks import CreateTrialQualityReport
from dkist_processing_common.tasks import PublishCatalogAndQualityMessages
from dkist_processing_common.tasks import QualityL1Metrics
from dkist_processing_common.tasks import SubmitDatasetMetadata
from dkist_processing_common.tasks import Teardown
from dkist_processing_common.tasks import TransferL0Data
from dkist_processing_common.tasks import TransferL1Data
from dkist_processing_common.tasks import TransferTrialData
from dkist_processing_common.tasks import TrialTeardown
from dkist_processing_core import Workflow

from dkist_processing_test.tasks import AssembleTestMovie
from dkist_processing_test.tasks import GenerateCalibratedData
from dkist_processing_test.tasks import MakeTestMovieFrames
from dkist_processing_test.tasks import ParseL0TestInputData
from dkist_processing_test.tasks import TestAssembleQualityData
from dkist_processing_test.tasks import TestQualityL0Metrics
from dkist_processing_test.tasks import WriteL1Data
from dkist_processing_test.tasks.manual import ManualWithoutProvenance
from dkist_processing_test.tasks.manual import ManualWithProvenance

# TransferInputData Task
transfer_input_data = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="transfer-input-data",
    workflow_package=__package__,
)
transfer_input_data.add_node(task=TransferL0Data, upstreams=None)

# ParseInputData Task
parse_input_data = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="parse-input-data",
    workflow_package=__package__,
)
parse_input_data.add_node(task=ParseL0TestInputData, upstreams=None)

# L0Quality Task
quality_l0_metrics = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="quality-l0-metrics",
    workflow_package=__package__,
)
quality_l0_metrics.add_node(task=TestQualityL0Metrics, upstreams=None)

# L1Quality Task
quality_l1_metrics = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="quality-l1-metrics",
    workflow_package=__package__,
)
quality_l1_metrics.add_node(task=QualityL1Metrics, upstreams=None)

# TestAssembleQualityData Task
quality_assemble_data = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="quality-assemble-data",
    workflow_package=__package__,
)
quality_assemble_data.add_node(task=TestAssembleQualityData, upstreams=None)

# GenerateL1CalibratedData Task
generate_calibrated_data = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="generate-calibrated-data",
    workflow_package=__package__,
)
generate_calibrated_data.add_node(task=GenerateCalibratedData, upstreams=None)

# MakeTestMovieFrames task
make_test_movie_frames = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="make-test-movie-frames",
    workflow_package=__package__,
)
make_test_movie_frames.add_node(task=MakeTestMovieFrames, upstreams=None)

# AssembleTestMovie Task
assemble_test_movie = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="assemble-test-movie",
    workflow_package=__package__,
)
assemble_test_movie.add_node(task=AssembleTestMovie, upstreams=None)

# WriteL1 Task
write_l1 = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="write-l1",
    workflow_package=__package__,
)
write_l1.add_node(task=WriteL1Data, upstreams=None)

# TransferOutputData Task
transfer_output_data = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="transfer-output-data",
    workflow_package=__package__,
)
transfer_output_data.add_node(task=TransferL1Data, upstreams=None)

# TransferTrialData Task
transfer_trial_data = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="transfer-trial-data",
    workflow_package=__package__,
)
transfer_trial_data.add_node(task=TransferTrialData, upstreams=None)

# SubmitDatasetMetadata Task
submit_dataset_metadata = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="submit-dataset-metadata",
    workflow_package=__package__,
)
submit_dataset_metadata.add_node(task=SubmitDatasetMetadata, upstreams=None)

# PublishCatalogMessages Task
publish_catalog_messages = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="publish-messages",
    workflow_package=__package__,
)
publish_catalog_messages.add_node(task=PublishCatalogAndQualityMessages, upstreams=None)

# Teardown Task
teardown = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="teardown",
    workflow_package=__package__,
)
teardown.add_node(task=Teardown, upstreams=None)

# Trial Teardown Task
trial_teardown = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="trial-teardown",
    workflow_package=__package__,
)
trial_teardown.add_node(task=TrialTeardown, upstreams=None)

# CreateTrialInventory Task
create_trial_inventory = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="create-trial-inventory",
    workflow_package=__package__,
)
create_trial_inventory.add_node(
    task=CreateTrialDatasetInventory, upstreams=None, pip_extras=["inventory"]
)

# CreateTrialAsdf Task
create_trial_asdf = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="create-trial-asdf",
    workflow_package=__package__,
)
create_trial_asdf.add_node(task=CreateTrialAsdf, upstreams=None, pip_extras=["asdf"])

# CreateTrialQualityReport Task
create_trial_quality_report = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="create-trial-quality",
    workflow_package=__package__,
)
create_trial_quality_report.add_node(
    task=CreateTrialQualityReport, upstreams=None, pip_extras=["quality"]
)


# ManualWithProvenance Task
manual_with_provenance = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="manual-with-provenance",
    workflow_package=__package__,
)
manual_with_provenance.add_node(task=ManualWithProvenance, upstreams=None)


# ManualWithoutProvenance Task
manual_without_provenance = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="manual-without-provenance",
    workflow_package=__package__,
)
manual_without_provenance.add_node(task=ManualWithoutProvenance, upstreams=None)
