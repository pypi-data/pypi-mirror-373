"""
Workflow which exercises the api's but doesn't perform an action
"""

from dkist_processing_core import ResourceQueue
from dkist_processing_core import Workflow

from dkist_processing_test.tasks import HighMemoryTask

high_memory_workflow = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="high_mem",
    workflow_package=__package__,
)
high_memory_workflow.add_node(
    task=HighMemoryTask, resource_queue=ResourceQueue.HIGH_MEMORY, upstreams=None
)
