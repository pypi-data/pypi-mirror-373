"""Stems for organizing files based on their Mosaic repeat number."""

from __future__ import annotations

from abc import ABC
from collections import defaultdict
from functools import cached_property
from typing import Type

from astropy.time import Time
from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.models.task_name import TaskName

from dkist_processing_vbi.models.constants import VbiBudName
from dkist_processing_vbi.models.tags import VbiStemName
from dkist_processing_vbi.parsers.vbi_l0_fits_access import VbiL0FitsAccess


class SingleMosaicTile:
    """
    An object that uniquely defines a (mosaic_step, exp_num, time_obs) tuple from any number of mosaic repeats.

    This is just a fancy tuple.

    Basically, it just hashes the (mosaic_step, exp_num, time_obs) tuple so these objects can easily be compared.
    Also uses the time_obs property so that multiple DSPS repeats of the same (mosaic_step, modstate) can be sorted.

    This is just a fancy tuple.
    """

    def __init__(self, fits_obj: VbiL0FitsAccess):
        """Read mosaic step, exp_num, and obs time information from a FitsAccess object."""
        self.mosaic_step = fits_obj.current_spatial_step
        self.exposure_num = fits_obj.current_mosaic_step_exp
        self.date_obs = Time(fits_obj.time_obs)

    def __repr__(self):
        return f"SingleMosaicTile with {self.mosaic_step = }, {self.exposure_num = }, and {self.date_obs = }"

    def __eq__(self, other: SingleMosaicTile) -> bool:
        """Two frames are equal if they have the same (mosaic_step, exp_num, date_obs) tuple."""
        if not isinstance(other, SingleMosaicTile):
            raise TypeError(f"Cannot compare SingleMosaicTile with type {type(other)}")

        for attr in ["mosaic_step", "exposure_num", "date_obs"]:
            if getattr(self, attr) != getattr(other, attr):
                return False

        return True

    def __lt__(self, other: SingleMosaicTile) -> bool:
        """Only sort on date_obs."""
        return self.date_obs < other.date_obs

    def __hash__(self) -> int:
        # Not strictly necessary, but does allow for using set() on these objects
        return hash((self.mosaic_step, self.exposure_num, self.date_obs))


class MosaicBase(Stem, ABC):
    """Base class for Stems that use a dict of [int, Dict[int, SingleMosaicTile]] to parse mosaic tiles."""

    # This only here so type-hinting of this complex dictionary will work.
    key_to_petal_dict: dict[str, SingleMosaicTile]

    @cached_property
    def mosaic_tile_dict(self) -> dict[int, dict[int, list[SingleMosaicTile]]]:
        """Nested dictionary that contains a SingleMosaicTile for each ingested frame.

        Dictionary structure is [mosaic_step (int), Dict[exp_num (int), List[SingleMosaicTile]]
        """
        scan_step_dict = defaultdict(lambda: defaultdict(list))
        for scan_step_obj in self.key_to_petal_dict.values():
            scan_step_dict[scan_step_obj.mosaic_step][scan_step_obj.exposure_num].append(
                scan_step_obj
            )

        return scan_step_dict

    def setter(self, fits_obj: VbiL0FitsAccess) -> SingleMosaicTile | Type[SpilledDirt]:
        """Ingest observe frames as SingleMosaicTile objects."""
        if fits_obj.ip_task_type.casefold() != TaskName.observe.value.casefold():
            return SpilledDirt
        return SingleMosaicTile(fits_obj=fits_obj)


class MosaicRepeatNumberFlower(MosaicBase):
    """Flower for computing and assigning mosaic repeat numbers.

    We can't use DKIST009 directly because subcycling in the instrument program task breaks the 1-to-1 mapping between
    DSPS repeat and mosaic repeat
    """

    def __init__(self):
        super().__init__(stem_name=VbiStemName.current_mosaic.value)

    def getter(self, key: str) -> int:
        """Compute the mosaic repeat number for a single frame.

        A list of all the frames associated with a single (mosaic_step, exp_num) tuple is sorted by date and that list
        is used to find the index of the frame in question.
        """
        mosaic_tile_obj = self.key_to_petal_dict[key]
        all_obj_for_tile = sorted(
            self.mosaic_tile_dict[mosaic_tile_obj.mosaic_step][mosaic_tile_obj.exposure_num]
        )

        num_files = all_obj_for_tile.count(mosaic_tile_obj)
        if num_files > 1:
            raise ValueError(
                f"More than one file found for a single (mosaic_step, exp_num). Randomly selected example has {num_files} files."
            )

        # Here is where we decide that mosaic repeat numbers start at 1
        return all_obj_for_tile.index(mosaic_tile_obj) + 1


class TotalMosaicRepeatsBud(MosaicBase):
    """Compute the total number of *complete* VBI Mosaics.

    Note that an IP with only one camera position is still considered a "mosaic".

    We can't use DKIST008 directly for two reasons:

    1. Subcycling in the instrument program task breaks the 1-to-1 mapping between DSPS repeat and mosaic repeat

    2. It's possible that the last repeat has an aborted mosaic. Instead, we return the number of completed mosaics found.
    """

    def __init__(self):
        super().__init__(stem_name=VbiBudName.num_mosaics_repeats.value)

    def getter(self, key: str) -> int:
        """Compute the total number of mosaic repeats.

        The number of mosaic repeats for every camera position are calculated and if a mosaic is incomplete,
        it will not be included.
        Assumes the incomplete mosaic is always the last one due to summit abort or cancellation.
        """
        # HOW THIS WORKS
        ################
        # self.mosaic_tile_dict conceptually looks like this:
        # {mosaic_1:
        #    {exp_1: [file1, file2],
        #     exp_2: [file3, file4]},
        #  mosaic_2:
        #    {exp_1: [file5, file6],
        #     exp_2: [file7, file7]}}
        #
        # We assume that each file for a (mosaic_step, exp_num) tuple is a different mosaic repeat
        # (there are 2 repeats in the above example). So all we really need to do is find the lengths of all
        # of the lists at the "exp_N" level.

        # The k[0] assumes that a mosaic step has the same number of exposures for all DSPS repeats
        repeats_per_mosaic_tile = [
            k[0]
            # The following list is the number of files found for each mosaic location for each exp_num
            for k in [
                # exp_dict is a dict of {exp_num: list(SingleMosaicTile)}
                # so len(m) is the number of SingleMosaicTiles detected for each exp_num
                [len(m) for m in exp_dict.values()]
                for exp_dict in self.mosaic_tile_dict.values()
            ]
        ]
        if min(repeats_per_mosaic_tile) + 1 < max(repeats_per_mosaic_tile):
            raise ValueError("More than one incomplete mosaic exists in the data.")
        return min(repeats_per_mosaic_tile)
