"""Repackage VBI data already calibrated before receipt at the Data Center."""

from astropy.io import fits
from dkist_processing_common.codecs.fits import fits_hdulist_encoder

from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.tasks.vbi_base import VbiTaskBase

__all__ = ["GenerateL1SummitData"]


class GenerateL1SummitData(VbiTaskBase):
    """
    Task class for updating the headers of on-summit processed VBI data.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs

    """

    record_provenance = True

    def run(self) -> None:
        """
        For all input frames.

            - Add data-dependent SPEC-0214 headers
            - Write out
        """
        # This loop is how we ensure that only completed mosaics get processed.
        with self.apm_task_step("Re-tagging INPUT observe frames as CALIBRATED"):
            for mosaic in range(1, self.constants.num_mosaic_repeats + 1):
                for step in range(1, self.constants.num_spatial_steps + 1):
                    for file_name in self.read(
                        tags=[
                            VbiTag.input(),
                            VbiTag.frame(),
                            VbiTag.task_observe(),
                            VbiTag.mosaic(mosaic),
                            VbiTag.spatial_step(step),
                        ]
                    ):
                        new_tags = [
                            VbiTag.calibrated(),
                            VbiTag.frame(),
                            VbiTag.mosaic(mosaic),
                            VbiTag.spatial_step(step),
                            VbiTag.stokes("I"),
                        ]

                        # We use `fits` directly because opening the file with VbiL0FitsAccess would require re-compressing
                        # the CompImageHDU on write. Doing it this way allows us to modify the header only.
                        with fits.open(file_name, disable_image_compression=True) as hdul:
                            hdul[1].header["VBINMOSC"] = self.constants.num_mosaic_repeats
                            hdul[1].header["VBICMOSC"] = mosaic

                            self.write(data=hdul, tags=new_tags, encoder=fits_hdulist_encoder)
