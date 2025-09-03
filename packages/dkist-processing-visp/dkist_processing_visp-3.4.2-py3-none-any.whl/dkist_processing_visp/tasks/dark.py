"""Visp dark task."""

from dkist_processing_common.codecs.fits import fits_access_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_service_configuration.logging import logger

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.parsers.visp_l0_fits_access import VispL0FitsAccess
from dkist_processing_visp.tasks.mixin.beam_access import BeamAccessMixin
from dkist_processing_visp.tasks.visp_base import VispTaskBase

__all__ = ["DarkCalibration"]


class DarkCalibration(VispTaskBase, BeamAccessMixin, QualityMixin):
    """
    Task class for calculation of the averaged dark frame for a VISP calibration run.

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

            - Gather input dark frames
            - Calculate master dark
            - Write master dark
            - Record quality metrics

        Returns
        -------
        None

        """
        required_readout_exp_times = list(self.constants.non_dark_task_readout_exp_times)
        logger.info(f"{required_readout_exp_times = }")

        with self.apm_task_step(
            f"Calculating dark frames for {self.constants.num_beams} beams and "
            f"{len(required_readout_exp_times)} readout exp times"
        ):
            total_dark_frames_used = 0
            for readout_exp_time in required_readout_exp_times:
                for beam in range(1, self.constants.num_beams + 1):
                    logger.info(
                        f"Gathering input dark frames for {readout_exp_time = } and {beam = }"
                    )
                    dark_tags = [
                        VispTag.input(),
                        VispTag.frame(),
                        VispTag.task_dark(),
                        VispTag.readout_exp_time(readout_exp_time),
                    ]
                    current_exp_dark_count = self.scratch.count_all(tags=dark_tags)
                    total_dark_frames_used += current_exp_dark_count

                    input_dark_objs = self.read(
                        tags=dark_tags,
                        decoder=fits_access_decoder,
                        fits_access_class=VispL0FitsAccess,
                    )

                    with self.apm_processing_step(
                        f"Calculating dark for {readout_exp_time = } and {beam = }"
                    ):
                        readout_normalized_arrays = (
                            self.beam_access_get_beam(o.data, beam=beam) / o.num_raw_frames_per_fpa
                            for o in input_dark_objs
                        )
                        averaged_dark_array = average_numpy_arrays(readout_normalized_arrays)

                    with self.apm_writing_step(f"Writing dark for {readout_exp_time = } {beam = }"):
                        self.write(
                            data=averaged_dark_array,
                            tags=VispTag.intermediate_frame_dark(
                                beam=beam, readout_exp_time=readout_exp_time
                            ),
                            encoder=fits_array_encoder,
                        )

        with self.apm_processing_step("Computing and logging quality metrics"):
            no_of_raw_dark_frames: int = self.scratch.count_all(
                tags=[
                    VispTag.input(),
                    VispTag.frame(),
                    VispTag.task_dark(),
                ],
            )
            unused_count = int(no_of_raw_dark_frames - (total_dark_frames_used / 2))
            self.quality_store_task_type_counts(
                task_type=TaskName.dark.value,
                total_frames=no_of_raw_dark_frames,
                frames_not_used=unused_count,
            )
