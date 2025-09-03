from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.constants import ConstantsBase


class TestConstants(ConstantsBase):
    """
    Constants for the test instrument.

    This class is only used on the `TestQualityL0Metrics` task to allow us to check for `num_modstates`.
    """

    @property
    def num_modstates(self) -> int:
        """Return the number of modstates."""
        # Use .get with default because integration tests use VBI, which doesn't have a modstate key and thus the db
        # entry won't be there.
        # In other words, we get the actual db value in unit tests and 1 in integration tests
        return self._db_dict.get(BudName.num_modstates, 1)
