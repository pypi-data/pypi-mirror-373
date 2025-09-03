"""Stems for parsing constants and tags related to time header keys."""

from collections import namedtuple
from pathlib import Path

from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.models.flower_pot import Thorn
from dkist_processing_common.models.tags import EXP_TIME_ROUND_DIGITS
from dkist_processing_common.models.task_name import TaskName

from dkist_processing_visp.models.constants import VispBudName
from dkist_processing_visp.parsers.visp_l0_fits_access import VispL0FitsAccess


class NonDarkNonPolcalTaskReadoutExpTimesBud(Stem):
    """Produce a tuple of all exposure times present in the dataset for ip task types that are not DARK or POLCAL."""

    def __init__(self):
        super().__init__(stem_name=VispBudName.non_dark_task_readout_exp_times.value)
        self.metadata_key = "sensor_readout_exposure_time_ms"

    def setter(self, fits_obj: VispL0FitsAccess) -> float | SpilledDirt:
        """
        Set the task exposure time for this fits object.

        Parameters
        ----------
        fits_obj
            The input fits object

        Returns
        -------
        The exposure time associated with this fits object
        """
        excluded_task_types = [TaskName.dark.value.casefold(), TaskName.polcal.value.casefold()]
        if fits_obj.ip_task_type.casefold() not in excluded_task_types:
            raw_exposure_time = getattr(fits_obj, self.metadata_key)
            return round(raw_exposure_time, EXP_TIME_ROUND_DIGITS)

        return SpilledDirt

    def getter(self, key: str | Path) -> (float, ...):
        """
        Get the list of exposure times.

        Parameters
        ----------
        key
            The input key

        Returns
        -------
        A tuple of exposure times
        """
        exposure_times = tuple(sorted(set(self.key_to_petal_dict.values())))
        return exposure_times


class DarkReadoutExpTimePickyBud(Stem):
    """Parse exposure times to ensure existence of the necessary DARK exposure times."""

    ReadoutExposureTime = namedtuple(
        "ReadoutExposureTime", ["is_dark", "is_polcal", "readout_exposure_time"]
    )
    key_to_petal_dict: dict[str | Path, ReadoutExposureTime]  # For type hinting

    def __init__(self):
        super().__init__(stem_name=VispBudName.dark_readout_exp_time_picky_bud.value)
        self.metadata_key = "sensor_readout_exposure_time_ms"

    def setter(self, fits_obj: VispL0FitsAccess) -> tuple:
        """
        Set the task exposure time and whether it is a DARK task for this fits object.

        Parameters
        ----------
        fits_obj
            The input fits object
        Returns
        -------
        A tuple of a boolean indicating if the task type is dark and the exposure time associated with this fits object
        """
        raw_exposure_time = getattr(fits_obj, self.metadata_key)
        exposure_time = round(raw_exposure_time, EXP_TIME_ROUND_DIGITS)
        is_dark = fits_obj.ip_task_type.casefold() == TaskName.dark.value.casefold()
        is_polcal = fits_obj.ip_task_type.casefold() == TaskName.polcal.value.casefold()

        return self.ReadoutExposureTime(
            is_dark=is_dark, is_polcal=is_polcal, readout_exposure_time=exposure_time
        )

    def getter(self, key: str | Path) -> Thorn:
        """
        Parse all exposure times and raise an error if any non-dark exposure time is missing from the set of dark exposure times.

        Parameters
        ----------
        key
            The input key

        Returns
        -------
        Thorn
        """
        readout_exp_tuples = list(self.key_to_petal_dict.values())

        dark_readout_exp_times = {
            exp_time.readout_exposure_time for exp_time in readout_exp_tuples if exp_time.is_dark
        }

        required_readout_exp_times = {
            exp_time.readout_exposure_time
            for exp_time in readout_exp_tuples
            if (not exp_time.is_dark and not exp_time.is_polcal)
        }

        required_exp_times_missing_from_dark_exposure_times = (
            required_readout_exp_times - dark_readout_exp_times
        )

        if required_exp_times_missing_from_dark_exposure_times:
            raise ValueError(
                f"Not all required readout exposure times were found in DARK IPs. Missing times = {required_exp_times_missing_from_dark_exposure_times}"
            )

        return Thorn
