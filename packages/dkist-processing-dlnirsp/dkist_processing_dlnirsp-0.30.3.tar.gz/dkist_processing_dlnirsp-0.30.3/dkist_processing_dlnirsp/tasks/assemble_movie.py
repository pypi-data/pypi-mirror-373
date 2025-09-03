"""Task for constructing a browse movie."""

from typing import Type

import numpy as np
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.tasks import AssembleMovie
from dkist_service_configuration.logging import logger
from PIL import ImageDraw
from PIL.ImageFont import FreeTypeFont

from dkist_processing_dlnirsp.models.constants import DlnirspConstants
from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.parsers.dlnirsp_l1_fits_acess import DlnirspL1FitsAccess

__all__ = ["AssembleDlnirspMovie"]


class AssembleDlnirspMovie(AssembleMovie):
    """
    Assemble all DLNIRSP movie frames (tagged with DlnirspTag.movie_frame()) into an mp4 movie file.

    Subclassed from the `AssembleMovie` task in `dkist_processing_common` as required to add DLNIRSP specific
    text overlays.
    """

    constants: DlnirspConstants

    MPL_COLOR_MAP = "afmhot"

    @property
    def constants_model_class(self) -> Type[DlnirspConstants]:
        """Get DLNIRSP constants."""
        return DlnirspConstants

    @property
    def fits_parsing_class(self):
        """Parse frames as DlnirspL1FitsAccess objects."""
        return DlnirspL1FitsAccess

    def compute_frame_shape(self) -> tuple[int, int]:
        """Dynamically set the dimensions of the movie based on L1 file shape."""
        movie_frame_arrays = self.read(tags=[DlnirspTag.movie_frame()], decoder=fits_array_decoder)
        random_frame = next(movie_frame_arrays)
        raw_L1_shape = random_frame.shape
        flipped_shape = raw_L1_shape[::-1]

        standard_HD_num_pix = 1920 * 1080
        frame_num_pix = np.prod(flipped_shape)
        scale_factor = np.sqrt(standard_HD_num_pix / frame_num_pix)
        scaled_shape = tuple(int(i * scale_factor) for i in flipped_shape)

        return scaled_shape

    def pre_run(self) -> None:
        """Set the movie frame shape prior to running."""
        super().pre_run()
        frame_shape = self.compute_frame_shape()
        logger.info(f"Setting movie shape to {frame_shape}")
        self.MOVIE_FRAME_SHAPE = frame_shape

    @property
    def num_images(self) -> int:
        """
        Total number of images in final movie.

        Overloaded from `dkist-processing-common` so we can handle all the levels of instrument looping.
        """
        return (
            self.constants.num_mosaic_repeats
            * self.constants.num_dither_steps
            * self.constants.num_mosaic_tiles
        )

    def tags_for_image_n(self, n: int) -> list[str]:
        """Return tags that grab the n'th movie image.

        Overloaded from `dkist-processing-common` so we can handle all the levels of instrument looping.
        """
        mosaic_num = n // (self.constants.num_dither_steps * self.constants.num_mosaic_tiles)
        dither_step = (n // self.constants.num_mosaic_tiles) % self.constants.num_dither_steps
        tile_num = n % self.constants.num_mosaic_tiles
        X_tile, Y_tile = np.unravel_index(
            tile_num, (self.constants.num_mosaic_tiles_x, self.constants.num_mosaic_tiles_y)
        )
        # mosaic tile nums are 1-indexed
        X_tile += 1
        Y_tile += 1

        tags = [
            DlnirspTag.mosaic_num(mosaic_num),
            DlnirspTag.dither_step(dither_step),
            DlnirspTag.mosaic_tile_x(X_tile),
            DlnirspTag.mosaic_tile_y(Y_tile),
        ]
        logger.info(f"AssembleMovie.tags_for_image_n: {tags = }")
        return tags

    def write_overlay(self, draw: ImageDraw, fits_obj: DlnirspL1FitsAccess) -> None:
        """
        Mark each movie frame the instrument, wavelength, and observe time.

        Additionally, add labels for the 4 Stokes sub-frames if the data are polarimetric.
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
            IQ_line = self.get_middle_line(draw=draw, text="I  Q", font=self.font_36)

            # Subtract 1 from the UV line so that it's below IQ_line
            UV_line = IQ_line - 1

            self.write_line(
                draw=draw, text="I   Q", line=IQ_line, column="middle", font=self.font_36
            )
            self.write_line(
                draw=draw, text="U   V", line=UV_line, column="middle", font=self.font_36
            )

    def get_middle_line(self, draw: ImageDraw, text: str, font: FreeTypeFont) -> int:
        """
        Get the line number for the middle of the frame.

        We need to compute this in real time because the frame size is dynamically based on the L1 file shape.
        """
        _, _, _, text_height = draw.textbbox(xy=(0, 0), text=text, font=font)
        # See `write_line` in `dkist-processing-common` for why this is the expression.
        line = (self.MOVIE_FRAME_SHAPE[1] // 2) / (self.TEXT_MARGIN_PX + text_height)
        return line
