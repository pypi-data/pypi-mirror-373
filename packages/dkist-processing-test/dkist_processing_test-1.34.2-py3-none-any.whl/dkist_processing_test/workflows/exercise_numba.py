# TransferInputData Task
from dkist_processing_core import Workflow

from dkist_processing_test.tasks import ExerciseNumba

exercise_numba = Workflow(
    input_data="input",
    output_data="output",
    category="test",
    detail="exercise_numba",
    workflow_package=__package__,
)
exercise_numba.add_node(task=ExerciseNumba, upstreams=None)
