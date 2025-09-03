"""Global test fixture configuration"""

from random import randint

import numpy as np
import pytest
from astropy.io import fits
from dkist_data_simulator.spec122 import Spec122Dataset
from dkist_header_validator.translator import translate_spec122_to_spec214_l0


@pytest.fixture()
def recipe_run_id():
    return randint(0, 99999)


class S122Headers(Spec122Dataset):
    def __init__(
        self,
        array_shape: tuple[int, ...],
        num_steps: int = 4,
        num_exp_per_step: int = 1,
        num_dsps_repeats: int = 5,
        time_delta: float = 10.0,
        instrument: str = "vbi",
    ):
        dataset_shape = (num_exp_per_step * num_steps * num_dsps_repeats,) + array_shape[-2:]
        super().__init__(
            dataset_shape=dataset_shape,
            array_shape=array_shape,
            time_delta=time_delta,
            instrument=instrument,
        )
        self.num_steps = num_steps
        self.num_exp_per_step = num_exp_per_step
        self.num_dsps_repeats = num_dsps_repeats


def generate_214_l0_fits_frame(
    s122_header: fits.Header, data: np.ndarray | None = None
) -> fits.HDUList:
    """Convert S122 header into 214 L0"""
    if data is None:
        data = np.ones((1, 10, 10))
    translated_header = translate_spec122_to_spec214_l0(s122_header)
    del translated_header["COMMENT"]
    hdu = fits.PrimaryHDU(data=data, header=fits.Header(translated_header))
    return fits.HDUList([hdu])


@pytest.fixture(scope="session")
def array_parameter_file_object_key() -> str:
    return "random.fits"


@pytest.fixture(scope="session")
def early_json_parameter_file_object_key() -> str:
    return "early_message.json"


@pytest.fixture(scope="session")
def late_json_parameter_file_object_key() -> str:
    return "late_message.json"


@pytest.fixture(scope="session")
def random_parameter_hdulist() -> (fits.HDUList, float, float, float):
    rng = np.random.default_rng()
    mu, std = 10.0, 2.0
    const = 5.0
    rand_data = rng.normal(mu, std, size=(100, 100))
    const_data = np.ones((10, 10)) * const
    hdul = fits.HDUList([fits.PrimaryHDU(rand_data), fits.ImageHDU(const_data)])

    return hdul, mu, std, const


@pytest.fixture(scope="session")
def early_file_message_str() -> str:
    return "Early in a file"


@pytest.fixture(scope="session")
def late_file_message_str() -> str:
    return "Late in a file"


@pytest.fixture(scope="session")
def early_value_message_str() -> str:
    return "Early"


@pytest.fixture(scope="session")
def late_value_message_str() -> str:
    return "Late"


@pytest.fixture(scope="session")
def early_date() -> str:
    return "1980-01-01"


@pytest.fixture(scope="session")
def late_date() -> str:
    return "2000-01-01"
