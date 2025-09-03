"""ViSP-specific assemble movie task subclass."""

from dkist_processing_common.tasks import AssembleMovie
from PIL import ImageDraw

from dkist_processing_visp.models.constants import VispConstants
from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.parsers.visp_l0_fits_access import VispL0FitsAccess
from dkist_processing_visp.parsers.visp_l1_fits_access import VispL1FitsAccess

__all__ = ["AssembleVispMovie"]


class AssembleVispMovie(AssembleMovie):
    """
    Assemble all ViSP movie frames (tagged with VispTag.movie_frame()) into an mp4 movie file.

    Subclassed from the AssembleMovie task in dkist_processing_common to add ViSP specific text overlays.


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
        """Get ViSP constants."""
        return VispConstants

    @property
    def fits_parsing_class(self):
        """Visp specific subclass of L1FitsAccess to use for reading images."""
        return VispL1FitsAccess

    @property
    def num_images(self) -> int:
        """Total number of images in final movie.

        Overloaded from `dkist-processing-common` because DSPS repeat does not correspond to map scan in ViSP
        """
        return self.constants.num_map_scans

    def tags_for_image_n(self, n: int) -> list[str]:
        """Return tags that grab the n'th movie image.

        Overloaded from `dkist-processing-common` because DSPS repeat does not correspond to map scan in ViSP
        """
        return [VispTag.map_scan(n + 1)]

    def write_overlay(self, draw: ImageDraw, fits_obj: VispL0FitsAccess) -> None:
        """
        Mark each image with it's instrument, observed wavelength, and observation time.

        Parameters
        ----------
        draw
            A PIL.ImageDraw object

        fits_obj
            A single movie "image", i.e., a single array tagged with VispTag.movie_frame
        """
        self.write_line(
            draw=draw,
            text=f"INSTRUMENT: {self.constants.instrument}",
            line=3,
            column="right",
            font=self.font_36,
        )
        self.write_line(
            draw=draw,
            text=f"WAVELENGTH: {fits_obj.wavelength} nm",
            line=2,
            column="right",
            font=self.font_36,
        )
        self.write_line(
            draw=draw,
            text=f"OBS TIME: {fits_obj.time_obs}",
            line=1,
            column="right",
            font=self.font_36,
        )

        if self.constants.correct_for_polarization:
            # The `line` on which an item is drawn is a multiple of the height of that line.
            # The "Q" character is slightly taller than the rest and so n units of the "I   Q"
            # line are taller than n units of the "U   V" line.
            self.write_line(draw=draw, text="I   Q", line=17, column="middle", font=self.font_36)
            self.write_line(draw=draw, text="U   V", line=17, column="middle", font=self.font_36)
