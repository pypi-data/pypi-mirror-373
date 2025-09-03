"""VBI parse task."""

from dkist_processing_common.models.tags import StemName
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.parsers.single_value_single_key_flower import (
    SingleValueSingleKeyFlower,
)
from dkist_processing_common.parsers.time import ExposureTimeFlower
from dkist_processing_common.parsers.time import ObsIpStartTimeBud
from dkist_processing_common.parsers.time import TaskExposureTimesBud
from dkist_processing_common.parsers.unique_bud import UniqueBud
from dkist_processing_common.tasks import ParseL0InputDataBase
from dkist_processing_common.tasks.parse_l0_input_data import S

from dkist_processing_vbi.models.constants import VbiBudName
from dkist_processing_vbi.models.tags import VbiStemName
from dkist_processing_vbi.parsers.mosaic_repeats import MosaicRepeatNumberFlower
from dkist_processing_vbi.parsers.mosaic_repeats import TotalMosaicRepeatsBud
from dkist_processing_vbi.parsers.spatial_step_pattern import SpatialStepPatternBud
from dkist_processing_vbi.parsers.vbi_l0_fits_access import VbiL0FitsAccess

__all__ = ["ParseL0VbiInputData"]


class ParseL0VbiInputData(ParseL0InputDataBase):
    """
    Parse input VBI data.

    Subclassed from the ParseL0InputDataBase task in dkist_processing_common to add VBI specific parameters.

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
    def fits_parsing_class(self):
        """FITS access class to use in this task."""
        return VbiL0FitsAccess

    @property
    def constant_buds(self) -> list[S]:
        """VBI specific constants to append to the common constants."""
        return super().constant_buds + [
            UniqueBud(
                constant_name=VbiBudName.num_spatial_steps.value,
                metadata_key="number_of_spatial_steps",
            ),
            SpatialStepPatternBud(),
            ObsIpStartTimeBud(),
            TotalMosaicRepeatsBud(),
            TaskExposureTimesBud(
                VbiBudName.gain_exposure_times.value, ip_task_types=TaskName.gain.value
            ),
            TaskExposureTimesBud(
                VbiBudName.observe_exposure_times.value, ip_task_types=TaskName.observe.value
            ),
        ]

    @property
    def tag_flowers(self) -> list[S]:
        """VBI specific tags to append to the common tags."""
        return super().tag_flowers + [
            SingleValueSingleKeyFlower(
                tag_stem_name=VbiStemName.current_spatial_step.value,
                metadata_key="current_spatial_step",
            ),
            SingleValueSingleKeyFlower(
                tag_stem_name=StemName.task.value, metadata_key="ip_task_type"
            ),
            MosaicRepeatNumberFlower(),
            ExposureTimeFlower(),
        ]
