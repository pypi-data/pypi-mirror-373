"""
Workflow which exercises the api's but doesn't perform an action
"""

from dkist_processing_core import Workflow

from dkist_processing_test.tasks import NoOpTask
from dkist_processing_test.tasks import NoOpTask2

noop = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="noop",
    workflow_package=__package__,
)
noop.add_node(task=NoOpTask, upstreams=None)


noop_flow = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="noop-flow",
    workflow_package=__package__,
)
noop_flow.add_node(task=NoOpTask, upstreams=None)
noop_flow.add_node(task=NoOpTask2, upstreams=NoOpTask)
