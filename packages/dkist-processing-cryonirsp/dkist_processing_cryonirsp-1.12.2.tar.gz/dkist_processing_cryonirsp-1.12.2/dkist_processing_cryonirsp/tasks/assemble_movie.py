"""CryoNIRSP-specific assemble movie task subclass."""

import numpy as np
from dkist_processing_common.tasks import AssembleMovie
from dkist_service_configuration.logging import logger
from PIL import ImageDraw
from PIL.ImageFont import FreeTypeFont

from dkist_processing_cryonirsp.codecs.fits import cryo_fits_array_decoder
from dkist_processing_cryonirsp.models.constants import CryonirspConstants
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import CryonirspL0FitsAccess
from dkist_processing_cryonirsp.parsers.cryonirsp_l1_fits_access import CryonirspL1FitsAccess

__all__ = ["AssembleCryonirspMovie", "SPAssembleCryonirspMovie"]


class AssembleCryonirspMovieBase(AssembleMovie):
    """
    Assemble all CryoNIRSP movie frames (tagged with CryonirspTag.movie_frame()) into an mp4 movie file.

    Subclassed from the AssembleMovie task in dkist_processing_common to add CryoNIRSP specific text overlays.


    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs
    """

    MPL_COLOR_MAP = "gray"

    def compute_frame_shape(self) -> tuple[int, int]:
        """Dynamically set the dimensions of the movie based on L1 file shape."""
        movie_frame_arrays = self.read(
            tags=[CryonirspTag.movie_frame()], decoder=cryo_fits_array_decoder
        )
        random_frame = next(movie_frame_arrays)
        raw_L1_shape = random_frame.shape
        flipped_shape = raw_L1_shape[::-1]

        standard_HD_num_pix = 1920 * 1080
        frame_num_pix = np.prod(flipped_shape)
        scale_factor = (
            np.sqrt(standard_HD_num_pix / frame_num_pix)
            if frame_num_pix > standard_HD_num_pix
            else 1.0
        )
        scaled_shape = tuple(int(i * scale_factor) for i in flipped_shape)

        return scaled_shape

    def pre_run(self) -> None:
        """Set the movie frame shape prior to running."""
        super().pre_run()
        frame_shape = self.compute_frame_shape()
        logger.info(f"Setting movie shape to {frame_shape}")
        self.MOVIE_FRAME_SHAPE = frame_shape

    @property
    def constants_model_class(self):
        """Get CryoNIRSP constants."""
        return CryonirspConstants

    @property
    def fits_parsing_class(self):
        """Cryonirsp specific subclass of L1FitsAccess to use for reading images."""
        return CryonirspL1FitsAccess

    def write_overlay(self, draw: ImageDraw, fits_obj: CryonirspL0FitsAccess) -> None:
        """
        Mark each image with its instrument, observed wavelength, and observation time.

        Parameters
        ----------
        draw
            A PIL.ImageDraw object

        fits_obj
            A single movie "image", i.e., a single array tagged with CryonirspTag.movie_frame
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
            self.write_line(draw=draw, text="Stokes-I", line=4, column="right", font=self.font_36)

    def get_middle_line(self, draw: ImageDraw, text: str, font: FreeTypeFont) -> int:
        """
        Get the line number for the middle of the frame.

        We need to compute this in real time because the frame size is dynamically based on the L1 file shape.
        """
        _, _, _, text_height = draw.textbbox(xy=(0, 0), text=text, font=font)
        # See `write_line` in `dkist-processing-common` for why this is the expression.
        line = (self.MOVIE_FRAME_SHAPE[1] // 2) / (self.TEXT_MARGIN_PX + text_height)
        return line


# See note below on `SPAssembleCryonirspMovie`
class AssembleCryonirspMovie(AssembleCryonirspMovieBase):
    """
    Assemble all CryoNIRSP CI movie frames (tagged with CryonirspTag.movie_frame()) into an mp4 movie file.

    Subclassed from the AssembleMovie task in dkist_processing_common to add CryoNIRSP specific text overlays.


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
    def num_images(self) -> int:
        """Total number of images in final movie.

        Overloaded from `dkist-processing-common` because DSPS repeat does not correspond to map scan in CryoNIRSP
        """
        return self.constants.num_map_scans * self.constants.num_scan_steps

    def tags_for_image_n(self, n: int) -> list[str]:
        """Return tags that grab the n'th movie image.

        Overloaded from `dkist-processing-common` because DSPS repeat does not correspond to map scan in CryoNIRSP
        """
        map_scan_num = n // self.constants.num_scan_steps + 1
        scan_step = n % self.constants.num_scan_steps + 1

        tags = [
            CryonirspTag.map_scan(map_scan_num),
            CryonirspTag.scan_step(scan_step),
        ]
        logger.info(f"AssembleMovie.tags_for_image_n: {tags =}")
        return tags


# NOTE:
# This task isn't used right now because the SP movies need some better handling of the wavelength dimension.
# For the time being both arms use the `MakeCryonirspMovieFrames` task above.
# See PR #91 for more information.
class SPAssembleCryonirspMovie(AssembleCryonirspMovieBase):
    """
    Assemble all CryoNIRSP SP movie frames (tagged with CryonirspTag.movie_frame()) into an mp4 movie file.

    Subclassed from the AssembleMovie task in dkist_processing_common to add CryoNIRSP specific text overlays.


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
    def num_images(self) -> int:
        """Total number of images in final movie.

        Overloaded from `dkist-processing-common` because DSPS repeat does not correspond to map scan in CryoNIRSP
        """
        return self.constants.num_map_scans

    def tags_for_image_n(self, n: int) -> list[str]:
        """Return tags that grab the n'th movie image.

        Overloaded from `dkist-processing-common` because DSPS repeat does not correspond to map scan in CryoNIRSP
        """
        return [CryonirspTag.map_scan(n + 1)]
