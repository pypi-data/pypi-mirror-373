"""VBI additions to common constants."""

from enum import Enum

from dkist_processing_common.models.constants import ConstantsBase


class VbiBudName(Enum):
    """Names to be used in VBI buds."""

    num_mosaics_repeats = "NUM_MOSAIC_REPEATS"
    spatial_step_pattern = "SPATIAL_STEP_PATTERN"
    num_spatial_steps = "NUM_SPATIAL_STEPS"
    gain_exposure_times = "GAIN_EXPOSURE_TIMES"
    observe_exposure_times = "OBSERVE_EXPOSURE_TIMES"
    obs_ip_start_time = "OBS_IP_START_TIME"


class VbiConstants(ConstantsBase):
    """VBI specific constants to add to the common constants."""

    @property
    def num_mosaic_repeats(self) -> int:
        """Return the number of times the full mosaic is repeated."""
        return self._db_dict[VbiBudName.num_mosaics_repeats.value]

    @property
    def mindices_of_mosaic_field_positions(self) -> list[tuple[int, int]]:
        """
        Define the mapping from mosaic field position to (MINDEX1, MINDEX2) tuple.

        The mosaic fields are defined as:

          BLUE     RED       SINGLE    RED-ALL
          1 2 3    1   2               1     2
          4 5 6                5          5
          7 8 9    3   4               3     4

        Thus, the Nth index of this list gives the (MINDEX1, MINDEX2) tuple for the Nth mosaic field (a dummy 0th
        element is provided so that the 1-indexing of the mosaic fields is preserved).
        """
        # fmt: off
        # A dummy value goes in the 0th position because the mosaic fields are 1-indexed. This means we can
        # simply slice this list with the mosaic field number.
        blue_mosiac = ["index_placeholder",
                       (1, 3), (2, 3), (3, 3),
                       (1, 2), (2, 2), (3, 2),
                       (1, 1), (2, 1), (3, 1),
                       ]
        red_mosiac = ["index_placeholder",
                      (1, 2), (2, 2),
                      (1, 1), (2, 1),
                      ]
        single = ["index_placeholder"] * 5 + [(1, 1)]
        red_all = ["index_placeholder",
                   (1, 3), (3, 3), (1, 1), (3, 1), (2, 2),
                   ]
        # fmt: on
        match len(self.spatial_step_pattern):
            case 1:
                return single

            case 4:
                return red_mosiac

            case 5:
                return red_all

            case 9:
                return blue_mosiac

            case _:
                raise ValueError(
                    f"Spatial step pattern {self.spatial_step_pattern} describes an unknown mosaic. Parsing should have caught this."
                )

    @property
    def spatial_step_pattern(self) -> list[int]:
        """Return a parsed list of the spatial step pattern used to scan the mosaic FOV."""
        raw_list = self._db_dict[VbiBudName.spatial_step_pattern.value]
        return [int(val) for val in raw_list.split(",")]

    @property
    def num_spatial_steps(self) -> int:
        """Spatial steps in a raster."""
        return self._db_dict[VbiBudName.num_spatial_steps.value]

    @property
    def gain_exposure_times(self) -> [float]:
        """Exposure times of gain frames."""
        return self._db_dict[VbiBudName.gain_exposure_times.value]

    @property
    def observe_exposure_times(self) -> [float]:
        """Exposure times of observe frames."""
        return self._db_dict[VbiBudName.observe_exposure_times.value]

    @property
    def obs_ip_start_time(self) -> str:
        """Return the start time of the observe IP."""
        return self._db_dict[VbiBudName.obs_ip_start_time.value]
