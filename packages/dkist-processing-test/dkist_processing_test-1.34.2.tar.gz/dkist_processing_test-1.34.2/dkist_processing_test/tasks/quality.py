"""Quality task definition."""

from typing import Iterable
from typing import Type

from dkist_processing_common.models.constants import ConstantsBase
from dkist_processing_common.tasks import AssembleQualityData
from dkist_processing_common.tasks import QualityL0Metrics

__all__ = ["TestQualityL0Metrics", "TestAssembleQualityData"]

from dkist_processing_test.models.constants import TestConstants


class TestQualityL0Metrics(QualityL0Metrics):
    @property
    def constants_model_class(self) -> Type[ConstantsBase]:
        return TestConstants

    @property
    def modstate_list(self) -> Iterable[int] | None:
        if self.constants.num_modstates > 1:
            return range(1, self.constants.num_modstates + 1)

        return None


class TestAssembleQualityData(AssembleQualityData):
    @property
    def polcal_label_list(self) -> list[str] | None:
        return ["Beam 1"]
