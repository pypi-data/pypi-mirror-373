"""Parse Task definition."""

from typing import TypeVar

from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.models.flower_pot import Thorn
from dkist_processing_common.models.tags import StemName
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess
from dkist_processing_common.parsers.single_value_single_key_flower import (
    SingleValueSingleKeyFlower,
)
from dkist_processing_common.parsers.time import ObsIpStartTimeBud
from dkist_processing_common.parsers.unique_bud import TaskUniqueBud
from dkist_processing_common.tasks import ParseL0InputDataBase

__all__ = ["ParseL0TestInputData"]

S = TypeVar("S", bound=Stem)


class DspsRepeatNumberFlower(SingleValueSingleKeyFlower):
    def __init__(self):
        super().__init__(
            tag_stem_name=StemName.dsps_repeat.value, metadata_key="current_dsps_repeat"
        )

    def setter(self, fits_obj: L0FitsAccess):
        if fits_obj.ip_task_type != "observe":
            return SpilledDirt
        return super().setter(fits_obj)


class PickyDummyBud(Stem):
    """Exists to do literally nothing"""

    def setter(self, fits_obj: L0FitsAccess):
        if fits_obj.ip_task_type == "bad value":
            raise ValueError("This task type is bad!")

    def getter(self, key):
        return Thorn


class ParseL0TestInputData(ParseL0InputDataBase):
    @property
    def fits_parsing_class(self):
        return L0FitsAccess

    @property
    def tag_flowers(self) -> list[S]:
        return super().tag_flowers + [
            SingleValueSingleKeyFlower(
                tag_stem_name=StemName.task.value, metadata_key="ip_task_type"
            ),
            DspsRepeatNumberFlower(),
        ]

    @property
    def constant_buds(self) -> list[S]:
        return super().constant_buds + [
            TaskUniqueBud(
                constant_name=BudName.num_dsps_repeats.value,
                metadata_key="num_dsps_repeats",
                ip_task_types=TaskName.observe.value,
            ),
            PickyDummyBud(stem_name="PICKY_BUD"),
            ObsIpStartTimeBud(),
        ]
