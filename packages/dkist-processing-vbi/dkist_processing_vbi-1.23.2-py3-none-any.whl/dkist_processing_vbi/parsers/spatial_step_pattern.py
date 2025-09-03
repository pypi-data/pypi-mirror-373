"""Bud for checking that the spatial step pattern (VBISTPAT) matches expectations."""

from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.parsers.unique_bud import TaskUniqueBud

from dkist_processing_vbi.models.constants import VbiBudName


class SpatialStepPatternBud(TaskUniqueBud):
    """
    Bud for checking and returning the VBI spatial step pattern.

    This is just a `TaskUniqueBud` that performs the following checks on the unique value:

      The step pattern must describe one of the following patterns:
       - either a 1x1, 2x2, or 3x3 grid. This means it must have 1, 4, or 9 elements.
       - a 5-step VBI-RED raster. This means it must have 5 elements where the first four elements from a 2x2 grid and the fifth element overlaps the preceeding four in the center.

      The step pattern cannot be empty.

    """

    def __init__(self):
        super().__init__(
            constant_name=VbiBudName.spatial_step_pattern.value,
            metadata_key="spatial_step_pattern",
            ip_task_types=TaskName.observe.value,
        )

    def getter(self, key):
        """
        Get a unique value and ensure it describes a valid step pattern.

        See this Bud's class docstring for more information.
        """
        spatial_step_str = super().getter(key)
        pos_list = spatial_step_str.split(",")
        num_positions = len(pos_list)

        # We need the check of pos_list[0] because `split` will always return a single element list
        if num_positions not in [1, 4, 5, 9] or pos_list[0] == "":
            raise ValueError(
                f'Spatial step pattern "{spatial_step_str}" does not represent either a 1x1, 2x2, 3x3 mosaic, or a 5-step raster. '
                f"We don't know how to deal with this."
            )

        return spatial_step_str
