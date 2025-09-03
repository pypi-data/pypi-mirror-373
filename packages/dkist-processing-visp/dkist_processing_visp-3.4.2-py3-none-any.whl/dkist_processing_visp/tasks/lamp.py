"""ViSP lamp calibration task. See :doc:`this page </gain_correction>` for more information."""

import numpy as np
from dkist_processing_common.codecs.fits import fits_access_decoder
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_processing_math.arithmetic import subtract_array_from_arrays
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_service_configuration.logging import logger

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.parsers.visp_l0_fits_access import VispL0FitsAccess
from dkist_processing_visp.tasks.mixin.beam_access import BeamAccessMixin
from dkist_processing_visp.tasks.mixin.corrections import CorrectionsMixin
from dkist_processing_visp.tasks.visp_base import VispTaskBase

__all__ = ["LampCalibration"]


class LampCalibration(
    VispTaskBase,
    CorrectionsMixin,
    BeamAccessMixin,
    QualityMixin,
):
    """
    Task class for calculation of the averaged lamp gain frame for a VISP calibration run.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs

    """

    record_provenance = True

    def run(self):
        """
        For each beam.

            - Gather input lamp gain and averaged dark arrays
            - Calculate master lamp
            - Write master lamp
            - Record quality metrics

        Returns
        -------
        None

        """
        with self.apm_task_step(
            f"Generate lamp gains for {self.constants.num_beams} beams and {len(self.constants.lamp_readout_exp_times)} exposure times"
        ):
            for readout_exp_time in self.constants.lamp_readout_exp_times:
                for beam in range(1, self.constants.num_beams + 1):
                    logger.info(f"Load dark for beam {beam}")
                    dark_array = next(
                        self.read(
                            tags=VispTag.intermediate_frame_dark(
                                beam=beam, readout_exp_time=readout_exp_time
                            ),
                            decoder=fits_array_decoder,
                        )
                    )

                    for state_num in range(
                        1, self.constants.num_modstates + 1
                    ):  # modulator states go from 1 to n
                        logger.info(
                            f"Calculating average lamp gain for beam {beam}, modulator state {state_num}"
                        )
                        self.compute_and_write_master_lamp_gain_for_modstate(
                            modstate=state_num,
                            dark_array=dark_array,
                            beam=beam,
                            readout_exp_time=readout_exp_time,
                        )

        with self.apm_processing_step("Computing and logging quality metrics"):
            no_of_raw_lamp_frames: int = self.scratch.count_all(
                tags=[
                    VispTag.input(),
                    VispTag.frame(),
                    VispTag.task_lamp_gain(),
                ],
            )

            self.quality_store_task_type_counts(
                task_type=TaskName.lamp_gain.value, total_frames=no_of_raw_lamp_frames
            )

    def compute_and_write_master_lamp_gain_for_modstate(
        self,
        modstate: int,
        dark_array: np.ndarray,
        beam: int,
        readout_exp_time: float,
    ) -> None:
        """
        Compute and write master lamp gain for a given modstate and beam.

        Generally the algorithm is:
            1. Average input gain arrays
            2. Subtract average dark to get the dark corrected gain data
            3. Normalize each beam to unity mean
            4. Write to disk

        Parameters
        ----------
        modstate : int
            The modulator state to calculate the master lamp gain for

        dark_array : np.ndarray
            The master dark to be subtracted from each lamp gain file

        beam : int
            The number of the beam

        readout_exp_time : float
            Exposure time of single readout

        Returns
        -------
        None
        """
        apm_str = f"{beam = }, {modstate = }, and {readout_exp_time = }"
        # Get the input lamp gain arrays
        tags = [
            VispTag.input(),
            VispTag.frame(),
            VispTag.task_lamp_gain(),
            VispTag.modstate(modstate),
            VispTag.readout_exp_time(readout_exp_time),
        ]
        input_lamp_gain_objs = self.read(
            tags=tags, decoder=fits_access_decoder, fits_access_class=VispL0FitsAccess
        )

        with self.apm_processing_step(f"Computing gain for {apm_str}"):

            readout_normalized_arrays = (
                self.beam_access_get_beam(o.data, beam=beam) / o.num_raw_frames_per_fpa
                for o in input_lamp_gain_objs
            )
            averaged_gain_data = average_numpy_arrays(readout_normalized_arrays)

            dark_corrected_gain_data = next(
                subtract_array_from_arrays(averaged_gain_data, dark_array)
            )
            filtered_gain_data = self.corrections_mask_hairlines(dark_corrected_gain_data)

        with self.apm_writing_step(f"Writing gain array for {apm_str}"):
            self.write(
                data=filtered_gain_data,
                tags=[
                    VispTag.intermediate_frame(beam=beam, modstate=modstate),
                    VispTag.task_lamp_gain(),
                ],
                encoder=fits_array_encoder,
            )
