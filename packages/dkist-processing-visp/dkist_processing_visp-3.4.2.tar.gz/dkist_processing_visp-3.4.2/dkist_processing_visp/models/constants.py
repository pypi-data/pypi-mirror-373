"""Visp additions to common constants."""

from enum import Enum

from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.constants import ConstantsBase


class VispBudName(Enum):
    """Names to be used in Visp buds."""

    num_raster_steps = "NUM_RASTER_STEPS"
    polarimeter_mode = "POLARIMETER_MODE"
    wavelength = "WAVELENGTH"
    obs_ip_start_time = "OBS_IP_START_TIME"
    lamp_exposure_times = "LAMP_EXPOSURE_TIMES"
    lamp_readout_exp_times = "LAMP_READOUT_EXP_TIMES"
    solar_exposure_times = "SOLAR_EXPOSURE_TIMES"
    solar_readout_exp_times = "SOLAR_READOUT_EXP_TIMES"
    observe_exposure_times = "OBSERVE_EXPOSURE_TIMES"
    observe_readout_exp_times = "OBSERVE_READOUT_EXP_TIMES"
    polcal_exposure_times = "POLCAL_EXPOSURE_TIMES"
    polcal_readout_exp_times = "POLCAL_READOUT_EXP_TIMES"
    non_dark_task_readout_exp_times = "NON_DARK_TASK_READOUT_EXP_TIMES"
    num_map_scans = "NUM_MAP_SCANS"
    axis_1_type = "AXIS_1_TYPE"
    axis_2_type = "AXIS_2_TYPE"
    axis_3_type = "AXIS_3_TYPE"
    dark_readout_exp_time_picky_bud = "DARK_READOUT_EXP_TIME_PICKY_BUD"


class VispConstants(ConstantsBase):
    """Visp specific constants to add to the common constants."""

    @property
    def wavelength(self) -> float:
        """Wavelength."""
        return self._db_dict[VispBudName.wavelength.value]

    @property
    def obs_ip_start_time(self) -> str:
        """Return the start time of the observe IP."""
        return self._db_dict[VispBudName.obs_ip_start_time.value]

    @property
    def num_modstates(self):
        """Find the number of modulation states."""
        return self._db_dict[BudName.num_modstates.value]

    @property
    def num_beams(self):
        """
        Find the number of beams.

        The VISP will always have two beams
        """
        return 2

    @property
    def num_cs_steps(self):
        """Find the number of calibration sequence steps."""
        return self._db_dict[BudName.num_cs_steps.value]

    @property
    def num_raster_steps(self):
        """Find the number of raster steps."""
        return self._db_dict[VispBudName.num_raster_steps.value]

    @property
    def num_map_scans(self):
        """Return the number of map scans."""
        return self._db_dict[VispBudName.num_map_scans.value]

    @property
    def correct_for_polarization(self):
        """Correct for polarization."""
        return self._db_dict[VispBudName.polarimeter_mode.value] == "observe_polarimetric"

    @property
    def pac_init_set(self):
        """Return the label for the initial set of parameter values used when fitting demodulation matrices."""
        retarder_name = self._db_dict[BudName.retarder_name.value]
        match retarder_name:
            case "SiO2 OC":
                return "OCCal_VIS"
            case _:
                raise ValueError(f"No init set known for {retarder_name = }")

    @property
    def lamp_exposure_times(self) -> [float]:
        """Find the lamp exposure time."""
        return self._db_dict[VispBudName.lamp_exposure_times.value]

    @property
    def solar_exposure_times(self) -> [float]:
        """Find the solar exposure time."""
        return self._db_dict[VispBudName.solar_exposure_times.value]

    @property
    def polcal_exposure_times(self) -> [float]:
        """Find the polarization calibration exposure time."""
        if self.correct_for_polarization:
            return self._db_dict[VispBudName.polcal_exposure_times.value]
        else:
            return []

    @property
    def observe_exposure_times(self) -> [float]:
        """Find the observation exposure time."""
        return self._db_dict[VispBudName.observe_exposure_times.value]

    @property
    def lamp_readout_exp_times(self) -> [float]:
        """Find the lamp readout exposure time."""
        return self._db_dict[VispBudName.lamp_readout_exp_times.value]

    @property
    def solar_readout_exp_times(self) -> [float]:
        """Find the solar readout exposure time."""
        return self._db_dict[VispBudName.solar_readout_exp_times.value]

    @property
    def polcal_readout_exp_times(self) -> [float]:
        """Find the polarization calibration readout exposure time."""
        if self.correct_for_polarization:
            return self._db_dict[VispBudName.polcal_readout_exp_times.value]
        else:
            return []

    @property
    def non_dark_task_readout_exp_times(self) -> [float]:
        """
        Find all readout exposure times that *need* to exist in a dark IP.

        Every non-dark task needs to be corrected with an average dark frame of the same readout exp time, which means
        we need DARK IP task frames for all of these readout exposure times.
        """
        return self._db_dict[VispBudName.non_dark_task_readout_exp_times.value]

    @property
    def observe_readout_exp_times(self) -> [float]:
        """Find the observation readout exposure time."""
        return self._db_dict[VispBudName.observe_readout_exp_times.value]

    @property
    def axis_1_type(self) -> str:
        """Find the type of the first array axis."""
        return self._db_dict[VispBudName.axis_1_type.value]

    @property
    def axis_2_type(self) -> str:
        """Find the type of the second array axis."""
        return self._db_dict[VispBudName.axis_2_type.value]

    @property
    def axis_3_type(self) -> str:
        """Find the type of the third array axis."""
        return self._db_dict[VispBudName.axis_3_type.value]
