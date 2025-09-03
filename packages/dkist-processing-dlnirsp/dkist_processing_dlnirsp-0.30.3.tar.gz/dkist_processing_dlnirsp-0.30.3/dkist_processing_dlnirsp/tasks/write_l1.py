"""Task for populating L1 headers with relevant dataset and frame information."""

from functools import cache
from functools import cached_property
from typing import Literal

import astropy.units as u
from astropy.io import fits
from dkist_processing_common.codecs.json import json_decoder
from dkist_processing_common.models.wavelength import WavelengthRange
from dkist_processing_common.tasks import WriteL1Frame
from dkist_service_configuration.logging import logger

from dkist_processing_dlnirsp.models.constants import DlnirspConstants
from dkist_processing_dlnirsp.models.tags import DlnirspTag

cached_info_logger = cache(logger.info)
__all__ = ["DlnirspWriteL1Frame"]


class DlnirspWriteL1Frame(WriteL1Frame):
    """Task class for producing L1 output frames from calibrated DLNIRSP Science frames."""

    # For type-hinting
    constants: DlnirspConstants

    @property
    def constants_model_class(self):
        """Use DLNIRSP constants."""
        return DlnirspConstants

    def add_dataset_headers(
        self, header: fits.Header, stokes: Literal["I", "Q", "U", "V"]
    ) -> fits.Header:
        """Add DLNIRSP specific L1 header values to an L1 header."""
        if stokes.upper() not in self.constants.stokes_params:
            raise ValueError("The stokes parameter must be one of I, Q, U, V")

        # ---Spatial 1---
        header["DNAXIS1"] = header["NAXIS1"]
        header["DTYPE1"] = "SPATIAL"
        header["DPNAME1"] = "helioprojective longitude"
        header["DWNAME1"] = "helioprojective longitude"
        header["CNAME1"] = "helioprojective longitude"
        header["DUNIT1"] = header["CUNIT1"]

        # ---Spatial 2---
        header["DNAXIS2"] = header["NAXIS2"]
        header["DTYPE2"] = "SPATIAL"
        header["DPNAME2"] = "helioprojective latitude"
        header["DWNAME2"] = "helioprojective latitude"
        header["CNAME2"] = "helioprojective latitude"
        header["DUNIT2"] = header["CUNIT2"]

        # ---Spectral---
        # Update wavelength solution
        header.update(self.wavelength_solution)

        header["DNAXIS3"] = header["NAXIS3"]
        header["DTYPE3"] = "SPECTRAL"
        header["DPNAME3"] = "dispersion axis"
        header["DWNAME3"] = "wavelength"
        header["CNAME3"] = "wavelength"
        header["DUNIT3"] = header["CUNIT3"]
        header["WAVEUNIT"] = -9  # nanometers
        header["WAVEREF"] = "Air"

        # AKA the ones above
        num_array_axes = 3

        num_extra_axes = 0
        axis_index = num_array_axes

        header, tile_as_temporal_axis, num_extra_axes, axis_index = self.add_temporal_axis(
            header, num_extra_axes, axis_index
        )

        if self.constants.num_dither_steps > 1:
            num_extra_axes += 1
            axis_index += 1
            header[f"DNAXIS{axis_index}"] = self.constants.num_dither_steps
            header[f"DTYPE{axis_index}"] = "TEMPORAL"
            header[f"DPNAME{axis_index}"] = "dither step"
            header[f"DWNAME{axis_index}"] = "time"
            header[f"DUNIT{axis_index}"] = "s"
            header[f"DINDEX{axis_index}"] = int(header["DLCURSTP"]) + 1

        if self.constants.correct_for_polarization:
            cached_info_logger("Polarimetric data detected")
            num_extra_axes += 1
            axis_index += 1

            header[f"DNAXIS{axis_index}"] = 4
            header[f"DTYPE{axis_index}"] = "STOKES"
            header[f"DPNAME{axis_index}"] = "polarization state"
            header[f"DWNAME{axis_index}"] = "polarization state"
            header[f"DUNIT{axis_index}"] = ""
            header[f"DINDEX{axis_index}"] = self.constants.stokes_params.index(stokes.upper()) + 1

        header["DNAXIS"] = num_array_axes + num_extra_axes
        header["DAAXES"] = num_array_axes
        header["DEAXES"] = num_extra_axes

        if (
            not tile_as_temporal_axis
            and self.constants.num_mosaic_tiles_x * self.constants.num_mosaic_tiles_y > 1
        ):
            # If a mosaic was used add the MAXIS? keys
            header["MAXIS"] = 2
            header["MAXIS1"] = self.constants.num_mosaic_tiles_x
            header["MAXIS2"] = self.constants.num_mosaic_tiles_y
        else:
            # If this isn't a mosaik'd dataset then lets delete the MINDEX keys that were added during Science
            # Calibration.
            del header["MINDEX1"]
            del header["MINDEX2"]

        # Binning headers
        header["NBIN1"] = 1
        header["NBIN2"] = 1
        header["NBIN3"] = 1
        header["NBIN"] = header["NBIN1"] * header["NBIN2"] * header["NBIN3"]

        # It'd be nice if this was 1.5, but the fits spec only allows the integer values 0 or 1
        header["LEVEL"] = 1

        # Values don't have any units because they are relative to disk center
        header["BUNIT"] = ("", "Values are relative to disk center. See calibration docs.")

        return header

    @cached_property
    def wavelength_solution(self) -> dict[str, str | int | float]:
        """Load the wavelength solution from disk."""
        return next(
            self.read(
                tags=[DlnirspTag.intermediate(), DlnirspTag.task_wavelength_solution()],
                decoder=json_decoder,
            )
        )

    def calculate_date_end(self, header: fits.Header) -> str:
        """
        In DLNIRSP, the instrument specific DATE-END keyword is calculated during science calibration.

        Check that it exists.

        Parameters
        ----------
        header
            The input fits header
        """
        try:
            return header["DATE-END"]
        except KeyError:
            raise KeyError(
                f"The 'DATE-END' keyword was not found. "
                f"It was supposed to be inserted during science calibration."
            )

    def get_wavelength_range(self, header: fits.Header) -> WavelengthRange:
        """
        Return the wavelength range of this frame.

        Range is the wavelength values of the pixels at the ends of the wavelength axis.
        """
        wavelength_unit = header["CUNIT3"]
        minimum = header["CRVAL3"] - (header["CRPIX3"] * header["CDELT3"])
        maximum = header["CRVAL3"] + ((header["NAXIS3"] - header["CRPIX3"]) * header["CDELT3"])
        return WavelengthRange(
            min=u.Quantity(minimum, unit=wavelength_unit),
            max=u.Quantity(maximum, unit=wavelength_unit),
        )

    def add_temporal_axis(
        self, header: fits.Header, num_extra_axes: int, axis_index: int
    ) -> tuple[fits.Header, bool, int, int]:
        """
        Add temporal axis keys, if it exists.

        There are two cases where a temporal axis exists:

        1. The `num_mosaic_repeats` constant is > 1. In this the top-level mosaic loop has been used as the temporal
        loop.

        2. `num_mosaic_repeats == 1` and EXACTLY ONE of `num_mosaic_tiles_x` or `num_spatia_steps_Y` > 1. In this case
        the spatial step loop that was used is considered to define the temporal axis.

        If neither of the above is true then no temporal axis is added.

        Returns
        -------
        header
            The (maybe) updated header

        tile_as_temporal_axis
            If True then a spatial/tile dimension was used as the temporal axis. This is returned so downstream code
            knows not to add mosaic keys (because the actual "mosaic" was used as the temporal axis).

        num_extra_axes
            The number of non-array axes. Incremented if a temporal axis is added.

        axis_index
            The number of the current Dataset axis. Incremented if a temporal axis is added.
        """
        num_mosaic_repeats = self.constants.num_mosaic_repeats
        num_X_tiles = self.constants.num_mosaic_tiles_x
        num_Y_tiles = self.constants.num_mosaic_tiles_y
        if num_mosaic_repeats > 1:
            has_temporal_axis = True
            tile_as_temporal_axis = False
            temporal_axis_size = num_mosaic_repeats
            pname = "mosaic repeat number"
            dindex = header["DLCURMOS"]

        elif num_mosaic_repeats == 1 and (
            (num_X_tiles == 1 and num_Y_tiles == 1) or (num_X_tiles > 1 and num_Y_tiles > 1)
        ):
            has_temporal_axis = False
            tile_as_temporal_axis = False

        elif num_mosaic_repeats == 1 and num_X_tiles > 1 and num_Y_tiles == 1:
            has_temporal_axis = True
            tile_as_temporal_axis = True
            temporal_axis_size = num_X_tiles
            pname = "repeat number"
            dindex = header["DLCSTPX"]

        elif num_mosaic_repeats == 1 and num_X_tiles == 1 and num_Y_tiles > 1:
            has_temporal_axis = True
            tile_as_temporal_axis = True
            temporal_axis_size = num_Y_tiles
            pname = "repeat number"
            dindex = header["DLCSTPY"]

        else:
            raise ValueError(
                f"Failure to identify some weird mosaic/loops structure. {num_mosaic_repeats = }, {num_X_tiles = }, {num_Y_tiles = }"
            )

        if has_temporal_axis:
            num_extra_axes += 1
            axis_index += 1
            header[f"DNAXIS{axis_index}"] = temporal_axis_size
            header[f"DTYPE{axis_index}"] = "TEMPORAL"
            header[f"DPNAME{axis_index}"] = pname
            header[f"DWNAME{axis_index}"] = "time"
            header[f"DUNIT{axis_index}"] = "s"
            header[f"DINDEX{axis_index}"] = dindex

        return header, tile_as_temporal_axis, num_extra_axes, axis_index
