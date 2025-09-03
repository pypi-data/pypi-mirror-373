"""Copies of UniqueBud and SingleValueSingleKeyFlower from common that only activate if the frames are "observe" task."""

from typing import Type

from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.parsers.single_value_single_key_flower import (
    SingleValueSingleKeyFlower,
)

from dkist_processing_visp.models.constants import VispBudName
from dkist_processing_visp.models.tags import VispStemName
from dkist_processing_visp.parsers.visp_l0_fits_access import VispL0FitsAccess


class TotalRasterStepsBud(Stem):
    """Bud for finding the total number of raster steps."""

    def __init__(self):
        super().__init__(stem_name=VispBudName.num_raster_steps.value)

        self.total_num_key = "total_raster_steps"
        self.single_step_key = "raster_scan_step"

    def setter(self, fits_obj: VispL0FitsAccess) -> Type[SpilledDirt] | tuple[int, int]:
        """
        Setter for the bud.

        Parameters
        ----------
        fits_obj:
            A single FitsAccess object
        """
        if fits_obj.ip_task_type.casefold() != TaskName.observe.value.casefold():
            return SpilledDirt

        num_raster = getattr(fits_obj, self.total_num_key)
        single_step = getattr(fits_obj, self.single_step_key)

        return num_raster, single_step

    def getter(self, key) -> str | float | int:
        """
        Getter and check for bud.

        Return value if only a single value was found in dataset. Error if multiple values were found or if the actual
        raster steps found do not form a complete set based on the number-of-raster-steps header key.
        """
        values = self.key_to_petal_dict.values()
        num_steps_set = set([v[0] for v in values])

        # This is copied from UniqueBud because we still want to check this
        if len(num_steps_set) > 1:
            raise ValueError(
                f"Multiple {self.stem_name} values found for key {key}. Values: {num_steps_set}"
            )

        # Now check that all the steps we expect are present
        all_steps = sorted(list(set([v[1] for v in values])))
        if all_steps != list(range(0, max(all_steps) + 1)):
            raise ValueError(f"Not all sequential steps could be found. Found {all_steps}")

        return len(all_steps)


class RasterScanStepFlower(SingleValueSingleKeyFlower):
    """Flower for a raster scan step."""

    def __init__(self):
        super().__init__(
            tag_stem_name=VispStemName.raster_step.value, metadata_key="raster_scan_step"
        )

    def setter(self, fits_obj: VispL0FitsAccess):
        """
        Setter for a flower.

        Parameters
        ----------
        fits_obj:
            A single FitsAccess object
        """
        if fits_obj.ip_task_type.casefold() != TaskName.observe.value.casefold():
            return SpilledDirt
        return super().setter(fits_obj)
