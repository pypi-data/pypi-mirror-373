"""
Fake science task
"""

import numpy as np
from astropy.io import fits
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.codecs.fits import fits_hdu_decoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.codecs.json import json_encoder
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_service_configuration.logging import logger

from dkist_processing_test.models.parameters import TestParameters

__all__ = ["GenerateCalibratedData"]


class GenerateCalibratedData(WorkflowTaskBase):

    record_provenance = True

    def __init__(
        self,
        recipe_run_id: int,
        workflow_name: str,
        workflow_version: str,
    ):
        super().__init__(
            recipe_run_id=recipe_run_id,
            workflow_name=workflow_name,
            workflow_version=workflow_version,
        )
        self.parameters = TestParameters(
            scratch=self.scratch,
            obs_ip_start_time=self.constants.obs_ip_start_time,
            wavelength=2.0,
        )

    def run(self):
        rng = np.random.default_rng()
        with self.apm_task_step("Create debug frame"):
            self.write(
                data=np.arange(10), tags=[Tag.frame(), Tag.debug()], encoder=fits_array_encoder
            )

        with self.apm_task_step("Creating intermediate frame"):
            self.write(
                data=np.arange(5),
                tags=[Tag.frame(), Tag.intermediate(), Tag.task("DUMMY")],
                encoder=fits_array_encoder,
            )

        with self.apm_task_step("Creating unique frames"):
            for _ in range(2):
                self.write(data=np.arange(3), tags=["FOO", "BAR"], encoder=fits_array_encoder)

            self.write(data={"test": "dictionary"}, tags=["BAZ"], encoder=json_encoder)

        with self.apm_task_step(
            "Creating frames that won't be used or transferred as trial outputs"
        ):
            self.write(data=b"123", tags=[Tag.intermediate(), Tag.task("NOT_USED"), Tag.frame()])
            self.write(data=b"123", tags=["FOO"])

        logger.info(f"Using {self.parameters.value_message = }")
        logger.info(f"Using {self.parameters.file_message = }")

        with self.apm_task_step("Loop over inputs"):
            count = 1  # keep a running count to increment the dsps repeat number
            for hdu in self.read(tags=Tag.input(), decoder=fits_hdu_decoder):
                header = hdu.header
                with self.apm_processing_step("Doing some calculations"):
                    header["DSPSNUM"] = count
                    data = hdu.data

                    # Just do some weird crap. We don't use the loaded random array directly so that we
                    # don't have to care that the shapes are the same as the "real" data.
                    random_signal = rng.normal(*self.parameters.randomness, size=data.shape)
                    data = (
                        data + random_signal
                    )  # Needs to be like this because data will start as int-type
                    data += self.parameters.constant

                    # Add needed VBI L1 keys that would be computed during real VBI science
                    header["VBINMOSC"] = self.constants.num_dsps_repeats
                    header["VBICMOSC"] = count

                    # Sneak date-dependent parameter values into header for end-to-end checking
                    header["CAM_ID"] = self.parameters.file_message
                    header["CAMERA"] = self.parameters.value_message

                    output_hdu = fits.PrimaryHDU(data=data, header=header)

                    wavelength_category = self.parameters.wavelength_category
                    header["WAVECAT"] = wavelength_category

                with self.apm_writing_step("Writing data"):
                    output_hdul = fits.HDUList([output_hdu])
                    self.write(
                        data=output_hdul,
                        tags=[
                            Tag.calibrated(),
                            Tag.frame(),
                            Tag.stokes("I"),
                            Tag.dsps_repeat(count),
                        ],
                        encoder=fits_hdulist_encoder,
                    )
                count += 1
