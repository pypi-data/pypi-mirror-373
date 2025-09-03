"""VBI Write L1 task."""

from typing import Literal
from typing import Type

import astropy.units as u
import numpy as np
from astropy.io import fits
from astropy.time import Time
from astropy.time import TimeDelta
from dkist_processing_common.models.constants import ConstantsBase
from dkist_processing_common.tasks.write_l1 import WavelengthRange
from dkist_processing_common.tasks.write_l1 import WriteL1Frame
from dkist_service_configuration.logging import logger

from dkist_processing_vbi.models.constants import VbiConstants
from dkist_processing_vbi.models.filter import VBI_FILTERS
from dkist_processing_vbi.models.filter import find_associated_filter

__all__ = ["VbiWriteL1Frame"]


class VbiWriteL1Frame(WriteL1Frame):
    """
    Task class for writing out calibrated L1 VBI frames.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs
    """

    @property
    def constants_model_class(self) -> Type[ConstantsBase]:
        """Supply the correct class, so we can access VBI-specific constants."""
        return VbiConstants

    def add_dataset_headers(
        self, header: fits.Header, stokes: Literal["I", "Q", "U", "V"]
    ) -> fits.Header:
        """
        Add the VBI specific dataset headers to L1 FITS files.

        Parameters
        ----------
        header : fits.Header
            calibrated data header

        stokes :
            stokes parameter

        Returns
        -------
        fits.Header
            calibrated header with correctly written l1 headers
        """
        if self.constants.num_mosaic_repeats == 1:
            number_of_dataset_axes = 2
        else:
            number_of_dataset_axes = 3  # Third axis is temporal

        header["DNAXIS"] = number_of_dataset_axes
        header["DAAXES"] = 2  # Spatial, spatial
        header["DEAXES"] = number_of_dataset_axes - 2

        # ---Spatial 1---
        header["DNAXIS1"] = header["NAXIS1"]
        header["DTYPE1"] = "SPATIAL"
        header["DPNAME1"] = "helioprojective longitude"
        header["DWNAME1"] = "helioprojective longitude"
        header["CNAME1"] = "helioprojective longitude"
        header["DUNIT1"] = header["CUNIT1"]

        # ---Spatial 2---
        header["DNAXIS2"] = header["NAXIS2"]
        header["DTYPE2"] = "SPATIAL"
        header["DPNAME2"] = "helioprojective latitude"
        header["DWNAME2"] = "helioprojective latitude"
        header["CNAME2"] = "helioprojective latitude"
        header["DUNIT2"] = header["CUNIT2"]

        # ---Temporal---
        if self.constants.num_mosaic_repeats > 1:
            num_exp_per_dsp = header["VBINFRAM"]
            header["DNAXIS3"] = self.constants.num_mosaic_repeats * num_exp_per_dsp
            header["DTYPE3"] = "TEMPORAL"
            header["DPNAME3"] = "time"
            header["DWNAME3"] = "time"
            header["DUNIT3"] = "s"
            # Temporal position in dataset
            current_mosaic_number = header["VBICMOSC"]
            current_exposure = header["VBICFRAM"]
            header["DINDEX3"] = (current_mosaic_number - 1) * num_exp_per_dsp + current_exposure

        # ---Wavelength Info---
        header["WAVEUNIT"] = -9  # nanometers
        header["WAVEREF"] = "Air"

        # --- Mosaic ---
        number_of_spatial_steps = int(header["VBINSTP"])
        current_step = int(header["VBISTP"])
        if number_of_spatial_steps not in [1, 4, 5, 9]:  # not a known number of spatial steps
            raise ValueError(
                f"Mosaic grid must be a known configuration (steps in 1, 4, 5, 9). "
                f"Number of spatial steps in these data are {number_of_spatial_steps}"
            )
        # --- Axis length ---
        if number_of_spatial_steps in [1, 4, 9]:
            axis_length = int(np.sqrt(number_of_spatial_steps))
        if number_of_spatial_steps == 5:
            axis_length = 3
        # --- Build mosaic ---
        if number_of_spatial_steps in [4, 5, 9]:
            current_mosaic_field_position = self.constants.spatial_step_pattern[current_step - 1]
            mindex1, mindex2 = self.constants.mindices_of_mosaic_field_positions[
                current_mosaic_field_position
            ]
            header["MAXIS"] = 2
            header["MAXIS1"] = axis_length  # ex. 3
            header["MAXIS2"] = axis_length  # ex. 3
            header["MINDEX1"] = mindex1
            header["MINDEX2"] = mindex2

        # ---Other info---
        header["LEVEL"] = 1

        # Binning headers
        header["NBIN1"] = 1
        header["NBIN2"] = 1
        header["NBIN3"] = 1
        header["NBIN"] = header["NBIN1"] * header["NBIN2"] * header["NBIN3"]

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
        """
        Return the wavelength range of this frame.

        Range is the wavelengths at the edges of the filter bandpass.
        """
        vbi_filter = find_associated_filter(wavelength=header["LINEWAV"] * u.nm)
        return WavelengthRange(min=vbi_filter.min, max=vbi_filter.max)

    def get_waveband(self, wavelength: u.Quantity, wavelength_range: WavelengthRange) -> str:
        """Get the name of the filter that includes the given wavelength."""
        return find_associated_filter(wavelength=wavelength).name
