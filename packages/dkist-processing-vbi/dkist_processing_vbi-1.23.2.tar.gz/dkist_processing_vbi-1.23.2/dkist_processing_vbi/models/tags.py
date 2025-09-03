"""VBI tags."""

from enum import Enum

from dkist_processing_common.models.tags import Tag


class VbiStemName(str, Enum):
    """VBI specific tag stems."""

    current_spatial_step = "STEP"
    current_mosaic = "MOSAIC"


class VbiTag(Tag):
    """VBI specific tag formatting."""

    @classmethod
    def spatial_step(cls, step_num: int) -> str:
        """
        Tags by spatial step.

        Parameters
        ----------
        step_num: int
            The step number in the FOV
        """
        return cls.format_tag(VbiStemName.current_spatial_step, step_num)

    @classmethod
    def mosaic(cls, mosaic_num: int) -> str:
        """Tags by mosaic number."""
        return cls.format_tag(VbiStemName.current_mosaic, mosaic_num)

    @classmethod
    def task_dark_frame(
        cls, spatial_step: int | None = None, exposure_time: float | None = None
    ) -> list[str]:
        """Tags by frame and dark task, optionally by spatial step and exposure time."""
        tag_list = [cls.frame(), cls.task_dark()]
        if spatial_step is not None:
            tag_list += [cls.spatial_step(spatial_step)]
        if exposure_time is not None:
            tag_list += [cls.exposure_time(exposure_time)]
        return tag_list

    @classmethod
    def task_gain_frame(
        cls, spatial_step: int | None = None, exposure_time: float | None = None
    ) -> list[str]:
        """Tags by frame and gain task, optionally by spatial step and exposure time."""
        tag_list = [cls.frame(), cls.task_gain()]
        if spatial_step is not None:
            tag_list += [cls.spatial_step(spatial_step)]
        if exposure_time is not None:
            tag_list += [cls.exposure_time(exposure_time)]
        return tag_list
