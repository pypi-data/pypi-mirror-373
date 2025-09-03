"""
Fake MakeMovieFrames and AssembleTestMovie
"""

import numpy as np
from astropy.io import fits
from dkist_processing_common.codecs.fits import fits_hdu_decoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.parsers.l1_fits_access import L1FitsAccess
from dkist_processing_common.tasks import AssembleMovie
from dkist_processing_common.tasks import WorkflowTaskBase
from PIL import ImageDraw

__all__ = ["MakeTestMovieFrames", "AssembleTestMovie"]


class MakeTestMovieFrames(WorkflowTaskBase):
    """
    Take each output frame, copy the header and data and write out
    as a movie frame
    """

    def run(self):
        for d in range(1, self.constants.num_dsps_repeats + 1):
            with self.apm_task_step(f"Workign on dsps repeat {d}"):
                for hdu in self.read(
                    tags=[Tag.calibrated(), Tag.dsps_repeat(d)], decoder=fits_hdu_decoder
                ):
                    header = hdu.header
                    data = np.squeeze(hdu.data)
                    output_hdu = fits.PrimaryHDU(data=data, header=header)
                    output_hdul = fits.HDUList([output_hdu])

                    with self.apm_writing_step("Writing data"):
                        self.write(
                            data=output_hdul,
                            tags=[Tag.movie_frame(), Tag.dsps_repeat(d)],
                            encoder=fits_hdulist_encoder,
                        )


class AssembleTestMovie(AssembleMovie):
    """
    A shell to extend the AssembleMovie class for the end-to-end test.
    """

    @property
    def fits_parsing_class(self):
        return L1FitsAccess

    def write_overlay(self, draw: ImageDraw, fits_obj: L1FitsAccess) -> None:
        pass
