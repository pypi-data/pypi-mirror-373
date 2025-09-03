"""
Test task for infrastructure integration
"""

from dkist_processing_core import TaskBase

__all__ = ["NoOpTask", "NoOpTask2"]


class NoOpTask(TaskBase):
    def run(self) -> None:
        pass


class NoOpTask2(NoOpTask):
    pass
