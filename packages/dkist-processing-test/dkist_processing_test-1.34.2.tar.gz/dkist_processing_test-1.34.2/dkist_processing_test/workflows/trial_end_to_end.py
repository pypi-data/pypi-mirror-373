"""
Workflow which exercises the common tasks end to end in a trial scenario
"""

from dkist_processing_common.tasks import CreateTrialAsdf
from dkist_processing_common.tasks import CreateTrialDatasetInventory
from dkist_processing_common.tasks import CreateTrialQualityReport
from dkist_processing_common.tasks import QualityL1Metrics
from dkist_processing_common.tasks import TransferL0Data
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

trial = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="trial-e2e",
    workflow_package=__package__,
)

trial.add_node(task=TransferL0Data, upstreams=None)

# Science flow
trial.add_node(task=ParseL0TestInputData, upstreams=TransferL0Data)
trial.add_node(task=GenerateCalibratedData, upstreams=ParseL0TestInputData)
trial.add_node(task=WriteL1Data, upstreams=GenerateCalibratedData)

# Movie flow
trial.add_node(task=MakeTestMovieFrames, upstreams=GenerateCalibratedData)
trial.add_node(task=AssembleTestMovie, upstreams=MakeTestMovieFrames)

# Quality flow
trial.add_node(task=TestQualityL0Metrics, upstreams=ParseL0TestInputData)
trial.add_node(task=QualityL1Metrics, upstreams=GenerateCalibratedData)
trial.add_node(task=TestAssembleQualityData, upstreams=[TestQualityL0Metrics, QualityL1Metrics])

# Trial data generation
trial.add_node(task=CreateTrialDatasetInventory, upstreams=WriteL1Data, pip_extras=["inventory"])
trial.add_node(task=CreateTrialAsdf, upstreams=WriteL1Data, pip_extras=["asdf"])
trial.add_node(
    task=CreateTrialQualityReport, upstreams=TestAssembleQualityData, pip_extras=["quality"]
)

# Output flow
trial.add_node(
    task=TransferTrialData,
    upstreams=[
        CreateTrialDatasetInventory,
        CreateTrialAsdf,
        CreateTrialQualityReport,
        AssembleTestMovie,
    ],
)

# goodby
trial.add_node(task=TrialTeardown, upstreams=TransferTrialData)
