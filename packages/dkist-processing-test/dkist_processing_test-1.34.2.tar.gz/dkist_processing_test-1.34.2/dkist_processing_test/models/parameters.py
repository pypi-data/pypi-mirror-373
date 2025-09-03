import json
from datetime import datetime

import numpy as np
from dkist_processing_common.codecs.json import json_decoder
from dkist_processing_common.models.input_dataset import InputDatasetFilePointer
from dkist_processing_common.models.parameters import ParameterBase
from dkist_processing_common.models.parameters import ParameterWavelengthMixin


class TestParameters(ParameterBase, ParameterWavelengthMixin):
    """Class to test loading parameters from a file."""

    def _load_param_value_from_json_file(self, param_obj: InputDatasetFilePointer) -> np.ndarray:
        """Return the data associated with a tagged parameter file saved with a string message."""
        tag = param_obj.file_pointer.tag
        param_value = self._read_parameter_file(tag=tag, decoder=json_decoder)
        return param_value

    @property
    def randomness(self) -> (float, float):
        """A dummy parameter that requires loading a file."""
        param_dict = self._find_most_recent_past_value(
            "test_random_data", start_date=datetime.now()
        )
        data = self._load_param_value_from_fits(param_dict)
        mean = np.nanmean(data)
        std = np.nanstd(data)

        return mean, std

    @property
    def constant(self) -> float:
        """A dummy parameter that depends on the same file as a different parameter."""
        param_dict = self._find_most_recent_past_value("test_random_data")
        data = self._load_param_value_from_fits(param_dict, hdu=1)
        constant = np.median(data)

        return float(constant)

    @property
    def wavelength_category(self) -> str:
        """A dummy parameter that depends on wavelength."""
        return self._find_parameter_closest_wavelength("test_wavelength_category")

    @property
    def value_message(self) -> str:
        """A dummy parameter that returns a message."""
        return self._find_most_recent_past_value("test_message")

    @property
    def file_message(self) -> str:
        """A dummy parameter that returns a message from a file."""
        param_dict = self._find_most_recent_past_value("test_message_file")
        message = self._load_param_value_from_json_file(param_dict)

        return message
