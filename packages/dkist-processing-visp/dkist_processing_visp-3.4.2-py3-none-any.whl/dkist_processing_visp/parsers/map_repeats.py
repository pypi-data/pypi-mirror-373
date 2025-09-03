"""Stems for organizing files into separate map scans."""

from __future__ import annotations

from abc import ABC
from collections import defaultdict
from functools import cached_property
from typing import Type

from astropy.time import Time
from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.models.task_name import TaskName

from dkist_processing_visp.models.constants import VispBudName
from dkist_processing_visp.models.tags import VispStemName
from dkist_processing_visp.parsers.visp_l0_fits_access import VispL0FitsAccess


class SingleScanStep:
    """
    An object that uniquely defines a (raster_step, modstate, time_obs) tuple from any number of map scan repeates.

    This is just a fancy tuple.

    Basically, it just hashes the (raster_step, modstate, time_obs) tuple so these objects can easily be compared.
    Also uses the time_obs property so that multiple map scan repeats of the same (step, modstate) can be sorted.

    This is just a fancy tuple.
    """

    def __init__(self, fits_obj: VispL0FitsAccess):
        """Read raster step, modstate, and obs time information from a FitsAccess object."""
        self.raster_step = fits_obj.raster_scan_step
        self.modulator_state = fits_obj.modulator_state
        self.date_obs = Time(fits_obj.time_obs)

    def __repr__(self):
        return f"SingleScanStep with {self.raster_step = }, {self.modulator_state = }, and {self.date_obs = }"

    def __eq__(self, other: SingleScanStep) -> bool:
        """Two frames are equal if they have the same (raster_step, modstate) tuple."""
        if not isinstance(other, SingleScanStep):
            raise TypeError(f"Cannon compare MapRepeat with type {type(other)}")

        for attr in ["raster_step", "modulator_state", "date_obs"]:
            if getattr(self, attr) != getattr(other, attr):
                return False

        return True

    def __lt__(self, other: SingleScanStep) -> bool:
        """Only sort on date_obs."""
        return self.date_obs < other.date_obs

    def __hash__(self) -> int:
        # Not strictly necessary, but does allow for using set() on these objects
        return hash((self.raster_step, self.modulator_state, self.date_obs))


class MapScanStemBase(Stem, ABC):
    """Base class for Stems that use a dictionary of [int, Dict[int, SingleScanStep]] to analyze map_scan-related stuff."""

    # This only here so type-hinting of this complex dictionary will work.
    key_to_petal_dict: dict[str, SingleScanStep]

    @cached_property
    def scan_step_dict(self) -> dict[int, dict[int, list[SingleScanStep]]]:
        """Nested dictionary that contains a SingleScanStep for each ingested frame.

        Dictionary structure is [raster_step (int), Dict[modstate (int), List[SingleScanStep]]
        """
        scan_step_dict = defaultdict(lambda: defaultdict(list))
        for scan_step_obj in self.key_to_petal_dict.values():
            scan_step_dict[scan_step_obj.raster_step][scan_step_obj.modulator_state].append(
                scan_step_obj
            )

        return scan_step_dict

    def setter(self, fits_obj: VispL0FitsAccess) -> SingleScanStep | Type[SpilledDirt]:
        """Ingest observe frames as SingleScanStep objects."""
        if fits_obj.ip_task_type.casefold() != TaskName.observe.value.casefold():
            return SpilledDirt
        return SingleScanStep(fits_obj=fits_obj)


class MapScanFlower(MapScanStemBase):
    """Flower for computing and assigning map scan numbers."""

    def __init__(self):
        super().__init__(stem_name=VispStemName.map_scan.value)

    def getter(self, key: str) -> int:
        """Compute the map scan number for a single frame.

        The frame implies a SingleScanStep. That object is then compared to the sorted list of objects for a single
        (raster_step, modstate) tuple. The location within that sorted list is the map scan number.
        """
        scan_step_obj = self.key_to_petal_dict[key]
        step_list = sorted(
            self.scan_step_dict[scan_step_obj.raster_step][scan_step_obj.modulator_state]
        )
        num_exp = step_list.count(scan_step_obj)
        if num_exp > 1:
            raise ValueError(
                f"More than one exposure detected for a single map scan of a single map step. (Randomly chosen step has {num_exp} exposures)."
            )
        return step_list.index(scan_step_obj) + 1  # Here we decide that map scan indices start at 1


class NumMapScansBud(MapScanStemBase):
    """Bud for determining the total number of map scans.

    Also checks that all raster steps have the same number of map scans.
    """

    def __init__(self):
        super().__init__(stem_name=VispBudName.num_map_scans.value)

    def getter(self, key: str) -> int:
        """Compute the total number of map scans.

        The number of maps for every scan step are calculated and if a map is incomplete,
        it will not be included.
        Assumes the incomplete map is always the last one due to summit abort or cancellation.
        """
        maps_per_scan_step = [
            k[0] for k in [[len(m) for m in md.values()] for md in self.scan_step_dict.values()]
        ]
        if min(maps_per_scan_step) + 1 < max(maps_per_scan_step):
            raise ValueError("More than one incomplete map exists in the data.")
        return min(maps_per_scan_step)
