"""VBI-specific assemble movie task subclass."""

from typing import Type

import numpy as np
from astropy.visualization import ZScaleInterval
from dkist_processing_common.codecs.json import json_decoder
from dkist_processing_common.models.constants import ConstantsBase
from dkist_processing_common.models.input_dataset import InputDatasetPartDocumentList
from dkist_processing_common.tasks import AssembleMovie
from matplotlib import colormaps
from PIL import ImageDraw

from dkist_processing_vbi.models.constants import VbiConstants
from dkist_processing_vbi.models.parameters import VbiParameters
from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.parsers.vbi_l1_fits_access import VbiL1FitsAccess

__all__ = ["AssembleVbiMovie"]


class AssembleVbiMovie(AssembleMovie):
    """
    Class for assembling pre-made movie frames (as FITS/numpy) into an mp4 movie file.

    Subclassed from the AssembleMovie task in dkist_processing_common to add VBI specific text overlays.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs
    """

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
        self.parameters = VbiParameters(
            scratch=self.scratch,
            obs_ip_start_time=self.constants.obs_ip_start_time,
        )

    MPL_COLOR_MAP = "gray"

    # So tab completion shows all the ViSP constants
    constants: VbiConstants

    @property
    def constants_model_class(self) -> Type[ConstantsBase]:
        """Class used to access constant database."""
        return VbiConstants

    @property
    def fits_parsing_class(self):
        """VBI specific subclass of L1FitsAccess to use for reading images."""
        return VbiL1FitsAccess

    @property
    def num_images(self) -> int:
        """Total number of images in final movie."""
        return self.constants.num_mosaic_repeats

    def tags_for_image_n(self, n: int) -> list[str]:
        """Return the tags needed to find image n."""
        return [VbiTag.mosaic(n + 1)]

    def apply_colormap(self, array: np.ndarray) -> np.ndarray:
        """
        Convert floats to RGB colors using the ZScale normalization scheme.

        Parameters
        ----------
        array : np.ndarray
            data to convert
        """
        # Clip the top and bottom 0.5% of data values to improve the contrast
        movie_intensity_clipping_percentile = self.parameters.movie_intensity_clipping_percentile
        vmin, vmax = np.nanpercentile(
            array, (movie_intensity_clipping_percentile, 100 - movie_intensity_clipping_percentile)
        )
        array = np.clip(a=array, a_min=vmin, a_max=vmax)

        color_mapper = colormaps.get_cmap(self.MPL_COLOR_MAP)
        scaled_array = ZScaleInterval()(array)
        return color_mapper(scaled_array, bytes=True)[
            :, :, :-1
        ]  # Drop the last (alpha) color dimension

    def write_overlay(self, draw: ImageDraw, fits_obj: VbiL1FitsAccess) -> None:
        """
        Mark each image with it's instrument, observed wavelength, and observation time.

        Parameters
        ----------
        draw
            A simple 2D drawing function for PIL images

        fits_obj
            A single movie "image", i.e., a single array tagged with VBITag.movie_frame
        """
        self.write_line(
            draw, f"INSTRUMENT: {self.constants.instrument}", 3, "right", font=self.font_18
        )
        self.write_line(draw, f"WAVELENGTH: {fits_obj.wavelength}", 2, "right", font=self.font_15)
        self.write_line(draw, f"DATE OBS: {fits_obj.time_obs}", 1, "right", font=self.font_15)
