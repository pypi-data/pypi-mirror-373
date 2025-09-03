"""ViSP tags."""

from enum import Enum

from dkist_processing_common.models.tags import Tag

from dkist_processing_visp.models.task_name import VispTaskName


class VispStemName(str, Enum):
    """ViSP specific tag stems."""

    beam = "BEAM"
    raster_step = "RASTER_STEP"  # The number of the current step within a raster scan
    modstate = "MODSTATE"
    file_id = "FILE_ID"
    map_scan = "MAP_SCAN"


class VispTag(Tag):
    """ViSP specific tag formatting."""

    @classmethod
    def task_background(cls) -> str:
        """Tags intermediate background frames."""
        return cls.task(VispTaskName.background.value)

    @classmethod
    def beam(cls, beam_num: int) -> str:
        """
        Tags by beam number.

        Parameters
        ----------
        beam_num: int
            The beam number

        """
        return cls.format_tag(VispStemName.beam, beam_num)

    @classmethod
    def raster_step(cls, raster_scan_step_num: int) -> str:
        """
        Tags by raster step.

        Parameters
        ----------
        raster_scan_step_num: int
            The raster scan step number

        """
        return cls.format_tag(VispStemName.raster_step, raster_scan_step_num)

    @classmethod
    def map_scan(cls, map_scan_num: int) -> str:
        """
        Tags by map scan number.

        Parameters
        ----------
        map_scan_num
            The map scan number
        """
        return cls.format_tag(VispStemName.map_scan, map_scan_num)

    ##################
    # Composite tags #
    ##################
    @classmethod
    def intermediate_frame(cls, beam: int, modstate: int | None = None) -> list[str]:
        """Tag by intermediate, by frame, by beam, and optionally by modstate."""
        tag_list = [cls.intermediate(), cls.frame(), cls.beam(beam)]
        if modstate is not None:
            tag_list += [cls.modstate(modstate)]
        return tag_list

    @classmethod
    def intermediate_frame_dark(
        cls,
        beam: int,
        readout_exp_time: float,
    ) -> list[str]:
        """Tag by intermediate_frame composite tag, task_dark, and readout_exposure_time."""
        tag_list = [
            cls.intermediate_frame(beam),
            cls.task_dark(),
            cls.readout_exp_time(readout_exp_time),
        ]
        return tag_list

    @classmethod
    def intermediate_frame_polcal_dark(cls, beam: int, readout_exp_time: float) -> list[str]:
        """Return tag list for averaged polcal dark frames."""
        tag_list = [
            cls.intermediate_frame(beam),
            cls.task_polcal_dark(),
            cls.readout_exp_time(readout_exp_time),
        ]
        return tag_list

    @classmethod
    def intermediate_frame_polcal_gain(cls, beam: int, readout_exp_time: float) -> list[str]:
        """Return tag list for averaged polcal gain frames."""
        tag_list = [
            cls.intermediate_frame(beam),
            cls.task_polcal_gain(),
            cls.readout_exp_time(readout_exp_time),
        ]
        return tag_list
