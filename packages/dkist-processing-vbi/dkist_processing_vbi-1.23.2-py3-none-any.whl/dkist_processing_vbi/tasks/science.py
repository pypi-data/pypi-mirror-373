"""VBI science task."""

from astropy.io import fits
from dkist_processing_common.codecs.fits import fits_access_decoder
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_processing_math.arithmetic import divide_fits_access_by_array
from dkist_processing_math.arithmetic import subtract_array_from_fits_access
from dkist_service_configuration.logging import logger

from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.parsers.vbi_l0_fits_access import VbiL0FitsAccess
from dkist_processing_vbi.tasks.vbi_base import VbiTaskBase

__all__ = ["ScienceCalibration"]


class ScienceCalibration(VbiTaskBase, QualityMixin):
    """
    Task class for running full science calibration on a set of observe images.

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
        Perform science calibrations.

        - Do initial array corrections (dark, gain)
        - Write out L1 science frames
        - Record quality metrics

        Returns
        -------
        None

        """
        logger.info(
            f"Starting science with {self.constants.num_spatial_steps} steps and {self.constants.num_mosaic_repeats} mosaic repeats"
        )
        with self.apm_task_step(
            f"Reducing science frames from {self.constants.num_spatial_steps} steps and {self.constants.num_mosaic_repeats} mosaic repeats",
        ):
            for exp_time in self.constants.observe_exposure_times:
                for step in range(1, self.constants.num_spatial_steps + 1):
                    logger.info(f"retrieving dark calibration for step {step} and {exp_time = }")
                    dark_tags = [
                        VbiTag.intermediate(),
                        VbiTag.task_dark_frame(spatial_step=step, exposure_time=exp_time),
                    ]
                    dark_calibration_array = next(
                        self.read(tags=dark_tags, decoder=fits_array_decoder, auto_squeeze=False)
                    )

                    logger.info(f"retrieving gain calibration for step {step}")
                    gain_tags = [
                        VbiTag.intermediate(),
                        VbiTag.task_gain_frame(spatial_step=step),
                    ]
                    gain_calibration_array = next(
                        self.read(tags=gain_tags, decoder=fits_array_decoder, auto_squeeze=False)
                    )

                    for mosaic in range(1, self.constants.num_mosaic_repeats + 1):
                        apm_str = f"step {step} and repeat number {mosaic}"
                        logger.info(f"collecting observe frames for {apm_str}")
                        sci_access = self.read(
                            tags=[
                                VbiTag.input(),
                                VbiTag.frame(),
                                VbiTag.task_observe(),
                                VbiTag.mosaic(mosaic),
                                VbiTag.spatial_step(step),
                                VbiTag.exposure_time(exp_time),
                            ],
                            decoder=fits_access_decoder,
                            fits_access_class=VbiL0FitsAccess,
                            auto_squeeze=False,
                        )

                        with self.apm_processing_step("dark and gain corrections"):
                            logger.info(f"subtracting dark from {apm_str}")
                            sci_access = subtract_array_from_fits_access(
                                access_objs=sci_access, array_to_subtract=dark_calibration_array
                            )

                            logger.info(f"dividing gain from {apm_str}")
                            sci_access = divide_fits_access_by_array(
                                access_objs=sci_access, array_to_divide_by=gain_calibration_array
                            )

                        with self.apm_writing_step("writing calibrated science frames"):
                            for i, access_obj in enumerate(sci_access):
                                exp_num = access_obj.current_mosaic_step_exp
                                logger.info(f"Writing output for {apm_str} and {exp_num = }")
                                self.write_calibrated_fits_obj(access_obj, mosaic, step)

        with self.apm_processing_step("Computing and logging quality metrics"):
            no_of_raw_obs_frames: int = self.count(
                tags=[
                    VbiTag.input(),
                    VbiTag.frame(),
                    VbiTag.task_observe(),
                ],
            )
            self.quality_store_task_type_counts(
                task_type=TaskName.observe.value, total_frames=no_of_raw_obs_frames
            )

    def write_calibrated_fits_obj(self, fits_obj: VbiL0FitsAccess, mosaic: int, step: int) -> None:
        """Write a VbiL0FitsAccess object containing a calibrated array to disk and tag correctly.

        Also update the header with necessary mosaic information.
        """
        processed_hdu_list = fits.HDUList(
            [fits.PrimaryHDU(), fits.CompImageHDU(data=fits_obj.data, header=fits_obj.header)]
        )
        processed_hdu_list[1].header["VBINMOSC"] = self.constants.num_mosaic_repeats
        processed_hdu_list[1].header["VBICMOSC"] = mosaic

        # It is an intentional decision to not tag with exposure time here
        self.write(
            data=processed_hdu_list,
            tags=[
                VbiTag.calibrated(),
                VbiTag.frame(),
                VbiTag.spatial_step(step),
                VbiTag.mosaic(mosaic),
                VbiTag.stokes("I"),
            ],
            encoder=fits_hdulist_encoder,
        )
