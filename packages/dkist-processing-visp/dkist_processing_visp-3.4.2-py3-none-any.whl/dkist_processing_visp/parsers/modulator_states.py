"""ViSP modulator state parser."""

from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.models.tags import StemName

from dkist_processing_visp.parsers.visp_l0_fits_access import VispL0FitsAccess


class ObserveFrameError(BaseException):
    """Error raised when no observe frames are identified by polarization mode."""

    pass


class NumberModulatorStatesBud(Stem):
    """Bud to check the number of modulator states."""

    def __init__(self):
        super().__init__(stem_name=BudName.num_modstates.value)
        self.polarimeter_mode = "polarimeter_mode"
        self.number_of_modulator_states = "number_of_modulator_states"

    def setter(self, fits_obj: VispL0FitsAccess):
        """
        Set the value of the bud.

        Parameters
        ----------
        fits_obj:
            A single FitsAccess object
        """
        return getattr(fits_obj, self.number_of_modulator_states), getattr(
            fits_obj, self.polarimeter_mode
        )

    def getter(self, key):
        """Get the value of the bud, checking for restrictions on polarimetric observe data."""
        values = self.key_to_petal_dict.values()
        num_modstates_set = set([v[0] for v in values])
        polmode_list = list(set([v[1] for v in values]))

        if "observe_intensity" in polmode_list:
            return 1

        # Polarimetric data must have the same number of modulator states in all frames
        if "observe_polarimetric" in polmode_list:
            if len(num_modstates_set) > 1:
                raise ValueError(
                    f"Polarimetric data must all have the same number of modulator states. Found frames with modstates: {num_modstates_set}"
                )
            return num_modstates_set.pop()

        raise ObserveFrameError(
            "No valid observe frames types were found in the headers of the data. Check the input data."
        )


class ModulatorStateFlower(Stem):
    """Flower to find the ip task type."""

    def __init__(self):
        super().__init__(stem_name=StemName.modstate.value)
        self.modulator_state_key = "modulator_state"
        self.polarimeter_mode_key = "polarimeter_mode"

    def setter(self, fits_obj: VispL0FitsAccess):
        """
        Set value of the flower.

        Parameters
        ----------
        fits_obj:
            A single FitsAccess object
        """
        return getattr(fits_obj, self.polarimeter_mode_key), getattr(
            fits_obj, self.modulator_state_key
        )

    def getter(self, key: str) -> int:
        """Return the modulator state given in the header of each file unless it is in intensity mode - then return modulator state = 1 for everything."""
        values = self.key_to_petal_dict.values()
        obs_mode_set = set([v[0] for v in values])
        if "observe_intensity" in obs_mode_set:
            return 1
        return self.key_to_petal_dict[key][1]
