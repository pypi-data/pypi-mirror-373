"""
Task for computing bad pixel map.

See :doc:`this page </bad_pixel_calibration>` for more information.
"""

import numpy as np
import scipy.ndimage as spnd
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_math.statistics import stddev_numpy_arrays
from dkist_service_configuration.logging import logger

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks.dlnirsp_base import DlnirspTaskBase

__all__ = ["BadPixelCalibration"]


class BadPixelCalibration(DlnirspTaskBase):
    """
    Task class for calculating a map of bad pixels.

    All cameras have a static map of bad pixels defined as a pipeline parameter, and the visible arm uses only this static
    map to locate bad pixels. The two IR arms also compute a dynamic map of bad pixels based on lamp gain data for the
    current dataset. The static and dynamic maps are then combined into a final bad pixel map.

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

    def run(self) -> None:
        """
        Compute a bad pixel map.

        For the visible arm we simply read the static map from parameters and save that as the final bad pixel map.

        For IR arms we also compute a "dynamic" bad pixel map for the current dataset based on lamp data using the
        following algorithm:

        1. Retrieve the average, dark-corrected lamp gain image

        2. Compute the per-pixel standard deviation of the dark frames used to compute the average lamp gain image

        3. For each of the two arrays collected above:

          a. Smooth the image with a median filter

          b. Subtract the image from the smoothed image

          c. Identify pixels in this difference image that are highly deviant. These are the bad pixels.

        The two dynamic and single static bad pixel maps are then combined to produce the final bad pixel map.
        """
        static_bad_pixel_map = self.parameters.static_bad_pixel_map
        if self.constants.is_ir_data:
            gain_dynamic_bad_pixel_map = self.compute_dynamic_bad_pixels_from_gain()
            dark_dynamic_bad_pixel_map = self.compute_dynamic_bad_pixels_from_dark_stack()
            dynamic_bad_pixel_map = gain_dynamic_bad_pixel_map + dark_dynamic_bad_pixel_map

        else:
            logger.info("VIS data detected. Setting dynamic bad pixel map to empty.")
            dynamic_bad_pixel_map = np.zeros_like(static_bad_pixel_map)

        with self.apm_writing_step("Combine dynamic and static maps and write"):
            logger.info("Combining dynamic and static bad pixel maps")
            logger.info(f"Static map has {int(np.sum(static_bad_pixel_map))} bad pixels")
            logger.info(f"Dynamic map has {int(np.sum(dynamic_bad_pixel_map))} bad pixels")

            # .astype(bool).astype(np.int8) is to make a "boolean" map that can be saved efficiently with astropy
            final_bad_pixel_map = (
                (static_bad_pixel_map + dynamic_bad_pixel_map).astype(bool).astype(np.int8)
            )

            logger.info("Writing final bad pixel map")
            self.write(
                data=final_bad_pixel_map,
                tags=[
                    DlnirspTag.intermediate_frame(),
                    DlnirspTag.task_bad_pixel_map(),
                ],
                encoder=fits_array_encoder,
            )

    def compute_dynamic_bad_pixels_from_gain(self) -> np.ndarray:
        """
        Find bad pixels in an averaged, dark-correct lamp gain image.

        First, the gain array is smoothed with a median filter whose shape is a pipeline parameter. This smoothed array
        is then subtracted from the original array. Pixels in this difference array that are deviant by a large amount
        (a settable pipeline parameter) are flagged as bad pixels. Prior to computing the standard deviation of the
        difference image the illuminated array mask is applied so non-illuminated regions don't impact the results.
        """
        with self.apm_processing_step("Smooth average lamp gain image"):
            avg_lamp_gain = next(
                self.read(
                    tags=[
                        DlnirspTag.intermediate_frame(),
                        DlnirspTag.task_lamp_gain(),
                    ],
                    decoder=fits_array_decoder,
                )
            )

            logger.info("Smoothing average lamp gain image")
            smoothed_array = spnd.median_filter(
                avg_lamp_gain,
                size=self.parameters.bad_pixel_gain_median_smooth_size,
                mode="constant",
                cval=np.nanmedian(avg_lamp_gain),
            )
        with self.apm_processing_step("Compute gain dynamic bad pixel map"):
            logger.info("Finding bad pixel locations in lamp gain")
            diff = smoothed_array - avg_lamp_gain
            diff[~self.group_id_illuminated_idx] = np.nan

            sigma_threshold = self.parameters.bad_pixel_gain_sigma_threshold
            absolute_threshold = sigma_threshold * np.nanstd(diff)

            dynamic_bad_pixel_map = np.array(np.abs(diff) > absolute_threshold, dtype=int)
            self.write(
                data=dynamic_bad_pixel_map,
                tags=[DlnirspTag.debug(), DlnirspTag.task("GAIN_BAD_PX_MAP")],
                encoder=fits_array_encoder,
            )

            logger.info(f"Lamp gain has {int(np.sum(dynamic_bad_pixel_map))} bad pixels")

        return dynamic_bad_pixel_map

    def compute_dynamic_bad_pixels_from_dark_stack(self) -> np.ndarray:
        """
        Find bad pixels based on the standard deviation of a stack of dark frames.

        The dark frames used are those used to correct the average lamp gain.

        First, the dark array is smoothed with a median filter whose shape is a pipeline parameter. This smoothed array
        is then subtracted from the original array. Pixels in this difference array that are deviant by a large amount
        (a settable pipeline parameter) are flagged as bad pixels.
        """
        with self.apm_processing_step("Compute lamp dark sigma image"):
            smallest_lamp_exp_time = sorted(self.constants.lamp_gain_exposure_times)[0]
            logger.info(f"Using darks from exposure time = {smallest_lamp_exp_time}")
            lamp_darks = self.read(
                tags=[
                    DlnirspTag.linearized_frame(),
                    DlnirspTag.task_dark(),
                    DlnirspTag.exposure_time(smallest_lamp_exp_time),
                ],
                decoder=fits_array_decoder,
            )
            dark_sigma = stddev_numpy_arrays(lamp_darks)

        with self.apm_processing_step("Smooth dark sigma array"):
            logger.info("Smoothing dark sigma array")
            smoothed_array = spnd.median_filter(
                dark_sigma,
                size=self.parameters.bad_pixel_dark_median_smooth_size,
                mode="constant",
                cval=np.nanmedian(dark_sigma),
            )

        with self.apm_processing_step("Compute dark dynamic bad pixel map"):
            logger.info("Finding bad pixel locations in dark sigma")
            diff = smoothed_array - dark_sigma

            sigma_threshold = self.parameters.bad_pixel_dark_sigma_threshold
            absolute_threshold = sigma_threshold * np.nanstd(diff)

            dynamic_bad_pixel_map = np.array(np.abs(diff) > absolute_threshold, dtype=int)
            self.write(
                data=dynamic_bad_pixel_map,
                tags=[DlnirspTag.debug(), DlnirspTag.task("DARK_BAD_PX_MAP")],
                encoder=fits_array_encoder,
            )

            logger.info(f"Dark sigma has {int(np.sum(dynamic_bad_pixel_map))} bad pixels")

        return dynamic_bad_pixel_map
