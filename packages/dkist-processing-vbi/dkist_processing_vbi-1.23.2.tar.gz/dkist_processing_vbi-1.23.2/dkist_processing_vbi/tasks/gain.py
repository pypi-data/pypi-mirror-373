"""VBI gain task."""

import numpy as np
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_processing_math.arithmetic import subtract_array_from_arrays
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_service_configuration.logging import logger

from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.tasks.vbi_base import VbiTaskBase

__all__ = ["GainCalibration"]


class GainCalibration(VbiTaskBase, QualityMixin):
    """
    Task class for calculation of a single gain frame for each spatial position. (Note that VBI only ever deals with Solar Gain frames).

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
        For each spatial step.

            - Gather input solar gain frames
            - Calculate average gain
            - Write average gain
            - Record quality metrics

        Returns
        -------
        None

        """
        # These will be running totals used to save a pass when computing the full-FOV normalization
        self.total_counts: float = 0.0
        self.total_non_nan_pix: int = 0

        # We'll just stuff the un-normalized arrays in this dictionary to avoid dealing with tags, io, etc.
        # This is OK (tm) because this will be, at most, 9 4k x 4k arrays. This is a lot (~1G), but not too much.
        step_gain_dict: dict = {}

        with self.apm_processing_step(
            f"Collecting and reducing gain arrays from {self.constants.num_spatial_steps} steps and {len(self.constants.gain_exposure_times)} exp times",
        ):
            for exp_time in self.constants.gain_exposure_times:
                for step in range(1, self.constants.num_spatial_steps + 1):
                    logger.info(f"retrieving dark frame step {step} and {exp_time = }")
                    dark_tags = [
                        VbiTag.intermediate(),
                        VbiTag.task_dark_frame(spatial_step=step, exposure_time=exp_time),
                    ]
                    try:
                        dark_calibration_array = next(
                            self.read(
                                tags=dark_tags, decoder=fits_array_decoder, auto_squeeze=False
                            )
                        )
                    except StopIteration:
                        raise ValueError(f"No matching dark found for {exp_time = }")

                    logger.info(f"collecting gain frames for {step = }")
                    input_gain_arrays = self.read(
                        tags=[
                            VbiTag.input(),
                            VbiTag.task_gain_frame(spatial_step=step, exposure_time=exp_time),
                        ],
                        decoder=fits_array_decoder,
                        auto_squeeze=False,
                    )

                    logger.info(f"averaging arrays from {step = }")
                    averaged_gain_array = average_numpy_arrays(input_gain_arrays)
                    logger.info(
                        f"average raw gain signal in step {step} = {averaged_gain_array.mean():.3e}"
                    )

                    logger.info(f"subtracting dark from average gain for {step = }")
                    dark_subtracted_gain_array = next(
                        subtract_array_from_arrays(
                            arrays=averaged_gain_array, array_to_subtract=dark_calibration_array
                        )
                    )

                    logger.info(f"Recording processed gain image for {step = }")
                    self.total_non_nan_pix += np.sum(~np.isnan(dark_subtracted_gain_array))
                    self.total_counts += np.nansum(dark_subtracted_gain_array)
                    step_gain_dict[step] = dark_subtracted_gain_array

        with self.apm_processing_step("normalizing gain arrays"):
            normalized_array_dict = self.normalize_fov(step_gain_dict)

        with self.apm_writing_step("writing gain arrays to disk"):
            self.write_gain_calibration(normalized_array_dict)

        with self.apm_processing_step("Computing and logging quality metrics"):
            no_of_raw_gain_frames: int = self.count(
                tags=[
                    VbiTag.input(),
                    VbiTag.task_gain_frame(),
                ],
            )
            self.quality_store_task_type_counts(
                task_type=TaskName.gain.value, total_frames=no_of_raw_gain_frames
            )

    def normalize_fov(self, step_gain_dict: dict[int, np.ndarray]) -> dict[int, np.ndarray]:
        """
        Find the global mean of the entire FOV and divide each frame (each spatial step) by this mean.

        Parameters
        ----------
        step_gain_dict : Dict
            Dictionary of dark subtracted gain array for each spatial step

        Returns
        -------
        Dict
            Dict of FOV normalized gain arrays
        """
        fov_mean = self.total_counts / self.total_non_nan_pix
        logger.info(f"full FOV mean = {fov_mean:.3e}")
        for k in step_gain_dict:
            step_gain_dict[k] = step_gain_dict[k] / fov_mean

        return step_gain_dict

    def write_gain_calibration(self, gain_array_dict: dict[int, np.ndarray]) -> None:
        """
        Apply correct tags to each spatial step and write to disk.

        Parameters
        ----------
        gain_array_dict : Dict
            Dictionary of corrected gain arrays

        Returns
        -------
        None
        """
        for step, data in gain_array_dict.items():
            self.write(
                data=data,
                tags=[
                    VbiTag.intermediate(),
                    VbiTag.task_gain_frame(spatial_step=step),
                ],
                encoder=fits_array_encoder,
            )
