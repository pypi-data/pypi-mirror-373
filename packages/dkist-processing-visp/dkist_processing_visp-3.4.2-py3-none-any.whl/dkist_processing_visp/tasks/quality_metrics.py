"""ViSP quality metrics task."""

from dataclasses import dataclass
from dataclasses import field
from typing import Iterable

import numpy as np
from astropy.time import Time
from dkist_processing_common.codecs.fits import fits_access_decoder
from dkist_processing_common.parsers.quality import L1QualityFitsAccess
from dkist_processing_common.tasks import QualityL0Metrics
from dkist_processing_common.tasks.mixin.quality import QualityMixin

from dkist_processing_visp.models.constants import VispConstants
from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.tasks.visp_base import VispTaskBase

__all__ = ["VispL0QualityMetrics", "VispL1QualityMetrics"]


@dataclass
class _QualityData:
    """Class for storage of Visp quality data."""

    datetimes: list[str] = field(default_factory=list)
    I_sensitivity: list[float] = field(default_factory=list)
    Q_sensitivity: list[float] = field(default_factory=list)
    U_sensitivity: list[float] = field(default_factory=list)
    V_sensitivity: list[float] = field(default_factory=list)


@dataclass
class _QualityTaskTypeData:
    """Class for storage of Visp quality task type data."""

    quality_task_type: str
    average_values: list[float] = field(default_factory=list)
    rms_values_across_frame: list[float] = field(default_factory=list)
    datetimes: list[str] = field(default_factory=list)

    @property
    def has_values(self) -> bool:
        return bool(self.average_values)


class VispL0QualityMetrics(QualityL0Metrics):
    """
    Task class for collection of Visp L0 specific quality metrics.

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
    def constants_model_class(self):
        """Class for Visp constants."""
        return VispConstants

    @property
    def modstate_list(self) -> Iterable[int] | None:
        """
        Define the list of modstates over which to compute L0 quality metrics.

        If the dataset is non-polarimetric then we just compute all metrics over all modstates at once.
        """
        if self.constants.correct_for_polarization:
            return range(1, self.constants.num_modstates + 1)

        return None


class VispL1QualityMetrics(VispTaskBase, QualityMixin):
    """
    Task class for collection of Visp L1 specific quality metrics.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs

    """

    def run(self) -> None:
        """
        For each spectral scan.

            - Gather stokes data
            - Find Stokes Q, U, and V RMS noise
            - Find the polarimetric sensitivity (smallest intensity signal measured)
            - Send metrics for storage

        """
        self.compute_sensitivity()
        self.compute_noise()

    def compute_sensitivity(self) -> None:
        """Compute RMS noise and sensitivity estimate for L1 Visp frames."""
        with self.apm_processing_step("Calculating polarization metrics"):
            all_datetimes = []
            all_I_sensitivity = []
            all_Q_sensitivity = []
            all_U_sensitivity = []
            all_V_sensitivity = []
            for map_scan in range(1, self.constants.num_map_scans + 1):
                polarization_data = _QualityData()
                poldata_noise_list_list = [
                    polarization_data.I_sensitivity,
                    polarization_data.Q_sensitivity,
                    polarization_data.U_sensitivity,
                    polarization_data.V_sensitivity,
                ]
                for step in range(0, self.constants.num_raster_steps):

                    # grab stokes I data
                    stokesI_frame = next(
                        self.read(
                            tags=[
                                VispTag.calibrated(),
                                VispTag.frame(),
                                VispTag.raster_step(step),
                                VispTag.map_scan(map_scan),
                                VispTag.stokes("I"),
                            ],
                            decoder=fits_access_decoder,
                            fits_access_class=L1QualityFitsAccess,
                        )
                    )
                    stokesI_med = np.nanmedian(stokesI_frame.data)
                    polarization_data.datetimes.append(Time(stokesI_frame.time_obs).mjd)

                    # grab other stokes data and find and store RMS noise
                    for stokes_param, data_list in zip(
                        ("I", "Q", "U", "V"), poldata_noise_list_list
                    ):
                        try:
                            stokes_frame = next(
                                self.read(
                                    tags=[
                                        VispTag.calibrated(),
                                        VispTag.frame(),
                                        VispTag.raster_step(step),
                                        VispTag.map_scan(map_scan),
                                        VispTag.stokes(stokes_param),
                                    ],
                                    decoder=fits_access_decoder,
                                    fits_access_class=L1QualityFitsAccess,
                                )
                            )
                        except StopIteration:
                            # This stokes parameter doesn't exist. No big deal.
                            continue

                        # compute sensitivity for this Stokes parameter
                        data_list.append(np.std(stokes_frame.data) / stokesI_med)

                all_datetimes.append(Time(np.mean(polarization_data.datetimes), format="mjd").isot)
                for target, source in zip(
                    [all_I_sensitivity, all_Q_sensitivity, all_U_sensitivity, all_V_sensitivity],
                    poldata_noise_list_list,
                ):
                    if not source:
                        # Empty list means there are no data for this Stokes parameter
                        continue
                    target.append(np.mean(source))

        with self.apm_step("Sending lists for storage"):
            for stokes_index, stokes_noise in zip(
                ("I", "Q", "U", "V"),
                (all_I_sensitivity, all_Q_sensitivity, all_U_sensitivity, all_V_sensitivity),
            ):
                if not stokes_noise:
                    continue
                self.quality_store_sensitivity(
                    stokes=stokes_index, datetimes=all_datetimes, values=stokes_noise
                )

    def compute_noise(self):
        """Compute noise in data."""
        with self.apm_processing_step("Calculating L1 ViSP noise metrics"):
            for stokes in ["I", "Q", "U", "V"]:
                tags = [VispTag.calibrated(), VispTag.frame(), VispTag.stokes(stokes)]
                if self.scratch.count_all(tags=tags) > 0:
                    frames = self.read(
                        tags=tags,
                        decoder=fits_access_decoder,
                        fits_access_class=L1QualityFitsAccess,
                    )
                    noise_values = []
                    datetimes = []
                    for frame in frames:
                        noise_values.append(self.avg_noise(frame.data))
                        datetimes.append(frame.time_obs)
                    self.quality_store_noise(
                        datetimes=datetimes, values=noise_values, stokes=stokes
                    )
