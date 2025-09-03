"""
Tasks simulating manual intervention.
Manual tasks are expected to write provenance records regardless of they always record provenance.
"""

from dkist_processing_common.tasks import WorkflowTaskBase

__all__ = ["ManualWithProvenance", "ManualWithoutProvenance"]


class ManualBase(WorkflowTaskBase):
    def run(self):
        with self.apm_task_step("NoOp"):
            pass


class ManualWithProvenance(ManualBase):

    record_provenance = True
    is_task_manual = True


class ManualWithoutProvenance(ManualBase):

    record_provenance = False
    is_task_manual = True
