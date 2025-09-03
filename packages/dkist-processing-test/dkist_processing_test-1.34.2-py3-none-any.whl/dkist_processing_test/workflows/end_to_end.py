"""
Workflow which exercises the common tasks in an end to end scenario
"""

from dkist_processing_common.tasks import PublishCatalogAndQualityMessages
from dkist_processing_common.tasks import QualityL1Metrics
from dkist_processing_common.tasks import SubmitDatasetMetadata
from dkist_processing_common.tasks import Teardown
from dkist_processing_common.tasks import TransferL0Data
from dkist_processing_common.tasks import TransferL1Data
from dkist_processing_core import ResourceQueue
from dkist_processing_core import Workflow

from dkist_processing_test.tasks import AssembleTestMovie
from dkist_processing_test.tasks import GenerateCalibratedData
from dkist_processing_test.tasks import MakeTestMovieFrames
from dkist_processing_test.tasks import ParseL0TestInputData
from dkist_processing_test.tasks import TestAssembleQualityData
from dkist_processing_test.tasks import TestQualityL0Metrics
from dkist_processing_test.tasks import WriteL1Data

end_to_end = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="management-processes-e2e",
    workflow_package=__package__,
)
end_to_end.add_node(task=TransferL0Data, upstreams=None)

# Science flow
end_to_end.add_node(task=ParseL0TestInputData, upstreams=TransferL0Data)
end_to_end.add_node(
    task=GenerateCalibratedData,
    resource_queue=ResourceQueue.HIGH_MEMORY,
    upstreams=ParseL0TestInputData,
)
end_to_end.add_node(task=WriteL1Data, upstreams=GenerateCalibratedData)

# Movie flow
end_to_end.add_node(task=MakeTestMovieFrames, upstreams=GenerateCalibratedData)
end_to_end.add_node(task=AssembleTestMovie, upstreams=MakeTestMovieFrames)

# Quality flow
end_to_end.add_node(task=TestQualityL0Metrics, upstreams=ParseL0TestInputData)
end_to_end.add_node(task=QualityL1Metrics, upstreams=GenerateCalibratedData)
end_to_end.add_node(
    task=TestAssembleQualityData, upstreams=[TestQualityL0Metrics, QualityL1Metrics]
)

# Output flow
end_to_end.add_node(task=SubmitDatasetMetadata, upstreams=[WriteL1Data, TestAssembleQualityData])
end_to_end.add_node(
    task=TransferL1Data, upstreams=[WriteL1Data, AssembleTestMovie, AssembleTestMovie]
)
end_to_end.add_node(
    task=PublishCatalogAndQualityMessages, upstreams=[TransferL1Data, SubmitDatasetMetadata]
)

# goodby
end_to_end.add_node(task=Teardown, upstreams=PublishCatalogAndQualityMessages)
