from typing import Literal

import astropy.units as u
from astropy.io import fits
from astropy.time import Time
from astropy.time import TimeDelta
from dkist_processing_common.models.wavelength import WavelengthRange
from dkist_processing_common.tasks import WriteL1Frame

__all__ = ["WriteL1Data"]


class WriteL1Data(WriteL1Frame):
    def add_dataset_headers(
        self, header: fits.Header, stokes: Literal["I", "Q", "U", "V"]
    ) -> fits.Header:
        header["DAAXES"] = 2
        header["DEAXES"] = 1
        header["DNAXIS"] = 3
        header["LEVEL"] = 1
        header["WAVEREF"] = "Air"
        header["WAVEUNIT"] = -9
        header["DINDEX3"] = 3
        header["DNAXIS1"] = header["NAXIS1"]
        header["DNAXIS2"] = header["NAXIS2"]
        header["DNAXIS3"] = 10
        header["DPNAME1"] = "spatial x"
        header["DPNAME2"] = "spatial y"
        header["DPNAME3"] = "frame number"
        header["DTYPE1"] = "SPATIAL"
        header["DTYPE2"] = "SPATIAL"
        header["DTYPE3"] = "TEMPORAL"
        header["DUNIT1"] = "arcsec"
        header["DUNIT2"] = "arcsec"
        header["DUNIT3"] = "s"
        header["DWNAME1"] = "helioprojective longitude"
        header["DWNAME2"] = "helioprojective latitude"
        header["DWNAME3"] = "time"
        header["NBIN"] = 1
        for i in range(1, header["NAXIS"] + 1):
            header[f"NBIN{i}"] = 1

        return header

    def calculate_date_end(self, header: fits.Header) -> str:
        """
        Calculate the VBI specific version of the "DATE-END" keyword.

        Parameters
        ----------
        header
            The input fits header

        Returns
        -------
        The isot formatted string of the DATE-END keyword value
        """
        return (
            Time(header["DATE-BEG"], format="isot", precision=6)
            + TimeDelta(float(header["TEXPOSUR"]) / 1000, format="sec")
        ).to_value("isot")

    def get_wavelength_range(self, header: fits.Header) -> WavelengthRange:
        return WavelengthRange(min=1075.0 * u.nm, max=1085.0 * u.nm)
