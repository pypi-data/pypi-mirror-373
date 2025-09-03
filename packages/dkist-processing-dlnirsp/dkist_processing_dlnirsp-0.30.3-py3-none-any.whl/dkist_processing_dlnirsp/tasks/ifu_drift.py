"""
Task for computing drift between IFU metrology parameter files and current dataset.

The IFU metrology files are generated once, but the IFU may slowly drift in the FOV over time. This task makes sure that
the metrology files are well aligned with the current dataset.

See :doc:`this page </ifu_drift>` for more information.
"""

import numpy as np
import skimage.filters as skif
import skimage.registration as skir
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_math.arithmetic import subtract_array_from_arrays
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_service_configuration.logging import logger

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks.dlnirsp_base import DlnirspTaskBase

__all__ = ["IfuDriftCalibration"]


class IfuDriftCalibration(DlnirspTaskBase):
    """
    Task class for aligning the IFU metrology files with the current dataset.

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
        Compute and apply the drift between the static IFU metrology files and the current dataset.

        1. Compute an average, dark-subtracted solar gain image.

        2. Binarize both the average solar gain and the static group ID array

        3. Compute a shift between the two binary images

        4. Apply this shift to the IFU metrology files and save for use in the downstream pipeline.
        """
        with self.apm_processing_step("Average solar gain images"):
            logger.info("Computing average solar gain array")
            solar_gain_data = self.get_avg_solar_gain()

            self.write(
                data=solar_gain_data,
                tags=[DlnirspTag.debug(), DlnirspTag.task("DC_AVG_SOLAR")],
                encoder=fits_array_encoder,
            )

        with self.apm_processing_step("Compute binary arrays"):
            logger.info("Computing solar binary image")
            solar_binary = self.compute_solar_binary(solar_gain_data)

            raw_ifu_id_array = self.parameters.raw_group_id_array
            logger.info("Computing IFU ID binary image")
            ifu_binary = self.compute_ifu_id_binary(raw_ifu_id_array)

            self.write(
                data=solar_binary,
                tags=[DlnirspTag.debug(), DlnirspTag.frame(), DlnirspTag.task("SOLAR_BIANRY")],
                encoder=fits_array_encoder,
            )
            self.write(
                data=ifu_binary,
                tags=[DlnirspTag.debug(), DlnirspTag.frame(), DlnirspTag.task("IFU_ID_BIANRY")],
                encoder=fits_array_encoder,
            )

        with self.apm_processing_step("Compute IFU drift"):
            logger.info("Computing IFU drift amount")
            drift = self.compute_ifu_drift(solar_binary, ifu_binary)
            logger.info(f"IFU drift = {drift}")

        with self.apm_processing_step("Drift IFU metrology arrays"):
            logger.info("Drifting IFU group ID array")
            drifted_ifu_id_array = self.apply_drift_to_array(raw_ifu_id_array, drift)

            logger.info("Validating drift")
            drift_valid = self.validate_drift(drift, drifted_ifu_id_array, raw_ifu_id_array)
            if not drift_valid:
                logger.info("Invalid drift. Falling back to raw metrology arrays.")
                drifted_ifu_id_array = raw_ifu_id_array

            beam_correction_array = self.compute_beam_match_corrections(drift, drifted_ifu_id_array)

            self.write(
                data=beam_correction_array,
                tags=[DlnirspTag.debug(), DlnirspTag.frame(), DlnirspTag.task("BEAM_CORRECTION")],
                encoder=fits_array_encoder,
            )

            drifted_ifu_id_array *= beam_correction_array
            drifted_arrays_dict = {DlnirspTag.task_drifted_ifu_groups(): drifted_ifu_id_array}
            drifted_tags = [
                DlnirspTag.task_drifted_dispersion(),
                DlnirspTag.task_drifted_ifu_x_pos(),
                DlnirspTag.task_drifted_ifu_y_pos(),
            ]
            raw_arrays = [
                self.parameters.raw_dispersion_array,
                self.parameters.raw_ifu_x_pos_array,
                self.parameters.raw_ifu_y_pos_array,
            ]
            for tag, raw_array in zip(drifted_tags, raw_arrays):
                logger.info(f"Making {tag}")
                drifted_array = (
                    self.apply_drift_to_array(raw_array, drift) if drift_valid else raw_array
                )
                drifted_arrays_dict[tag] = drifted_array * beam_correction_array

        with self.apm_writing_step("Write drifted IFU metrology arrays"):
            logger.info("Writing drifted IFU metrology arrays")
            self.write_drifted_metrology_arrays(drifted_arrays_dict)

    def get_avg_solar_gain(self) -> np.ndarray:
        """
        Compute a single, averaged frame from all linearized solar gain frames.

        If there are multiple exposure times present in the solar gain images, all frames for a single exposure time are
        averged prior to dark correction. Then all averaged exposure time frames are averaged again into a single frame.
        """
        all_exp_times = []
        for exp_time in self.constants.solar_gain_exposure_times:
            logger.info(f"Loading dark calibration for {exp_time = }")
            dark_array = next(
                self.read(
                    tags=DlnirspTag.intermediate_frame_dark(exposure_time=exp_time),
                    decoder=fits_array_decoder,
                )
            )

            logger.info(f"Loading solar gain frames for {exp_time = }")
            tags = [
                DlnirspTag.linearized_frame(),
                DlnirspTag.task_solar_gain(),
                DlnirspTag.exposure_time(exp_time),
            ]
            gain_arrays = self.read(tags=tags, decoder=fits_array_decoder)

            logger.info("Averaging solar gain frames")
            average_solar_gain = average_numpy_arrays(gain_arrays)

            logger.info("Applying dark calibration to average solar gain frame")
            dark_corrected_array = next(
                subtract_array_from_arrays(arrays=average_solar_gain, array_to_subtract=dark_array)
            )

            all_exp_times.append(dark_corrected_array)

        logger.info(f"Computing final average gain array for {len(all_exp_times)} exposure times")
        average_solar_gain = average_numpy_arrays(all_exp_times)

        return average_solar_gain

    def compute_solar_binary(self, data: np.ndarray) -> np.ndarray:
        """
        Segment a solar image into a binary array identifying illuminated and non-illuminated portions.

        The threshold value is found via the `skimage.filters.threshold_minimum` algorithm because the solar gain images
        are highly bi-modal (corresponding to the illuminated and non-illuminated portions of the array).
        """
        nan_mask = np.isnan(data)
        threshold = skif.threshold_minimum(data[~nan_mask])
        logger.info(f"{threshold = }")
        return (data > threshold).astype(int)

    def compute_ifu_id_binary(self, data: np.ndarray) -> np.ndarray:
        """Compute a binary image of the group ID array where illuminated regions are 1."""
        return (~np.isnan(data)).astype(int)

    def compute_ifu_drift(
        self, solar_binary: np.ndarray, ifu_id_binary: np.ndarray
    ) -> tuple[int, int]:
        """Compute a pixel shift between two binary images."""
        result = skir.phase_cross_correlation(
            reference_image=solar_binary, moving_image=ifu_id_binary, upsample_factor=10.0
        )
        drift = tuple(round(i) for i in result[0])

        return drift

    def apply_drift_to_array(self, raw_array: np.ndarray, drift: tuple[int, int]) -> np.ndarray:
        """
        Apply a measured pixel shift/drift to raw array.

        Because we limit the precision of the drift to integer pixel amounts the drift is applied by simply rolling
        and slicing the original array. This avoids small floating point errors caused by interpolation.
        """
        # We pad both sides of each dimension, regardless of the sign of the drift.
        # Thus, for padding and slicing we only need the absolute value because we're *always* padding the start
        # of each dimension and thus *always* need to slice away this pad.
        abs_drift = tuple(abs(i) for i in drift)

        # Because `np.pad` needs (before, after) for each axis
        pad_tuple = tuple((i, i) for i in abs_drift)
        # `or None` for when the drift is 0 (`slice(0, 0)` is an empty slice).
        slice_tuple = tuple(slice(i or None, -i or None) for i in abs_drift)

        padded_array = np.pad(raw_array, pad_tuple, constant_values=np.nan)
        drifted_array = np.roll(padded_array, drift, axis=(0, 1))[slice_tuple]

        return drifted_array

    def validate_drift(
        self, drift: tuple[int, int], drifted_ifu_id_array: np.ndarray, raw_ifu_id_array: np.ndarray
    ) -> bool:
        """
        Validate drift and drifted group ID array.

        Current validations:

        1. Computed drift is not larger than a pre-defined maximum.

        2. The drifted array has the same shape as the raw array.

        3. The number of pixels in each group is preserved in the drifted array. NOTE: Groups within the drift amount
           of the edge of detector are allowed to change size.
        """
        max_drift = self.parameters.group_id_max_drift_px
        warning_prefix = "Invalid DLNIRSP IFU Drift: "
        if any(abs(i) > max_drift for i in drift):
            logger.warning(
                f"{warning_prefix}Computed drift is larger than allowed ({drift = }, {max_drift = })."
            )
            return False

        if drifted_ifu_id_array.shape != raw_ifu_id_array.shape:
            logger.warning(
                f"{warning_prefix}Drifted array does not have the same shape as raw array (({drifted_ifu_id_array.shape = }, {raw_ifu_id_array.shape = })"
            )
            return False

        # Slice indices of the first and last elements of each axis
        edge_id_tuple = tuple((0, i - 1) for i in raw_ifu_id_array.shape)

        max_group = int(np.nanmax(raw_ifu_id_array))
        mismatched_groups = []
        for group in range(max_group + 1):
            # If any group pixel has the same index as either edge index of the corresponding group then the group must
            # be on the edge of the array.
            group_idx_tuple = np.where(raw_ifu_id_array == group)
            is_edge_group = any(
                [
                    any(
                        [
                            # Are any group px within the drift amount of an edge?
                            any(np.abs(group_px - edge_px) < abs(axis_drift))
                            # For both edges of the detector
                            for edge_px in axis_edges
                        ]
                    )
                    # Check for both axis
                    for group_px, axis_edges, axis_drift in zip(
                        group_idx_tuple, edge_id_tuple, drift
                    )
                ]
            )

            num_raw = np.sum(raw_ifu_id_array == group)
            num_drifted = np.sum(drifted_ifu_id_array == group)

            if not is_edge_group and num_drifted != num_raw:
                mismatched_groups.append((group, num_raw, num_drifted))

        if len(mismatched_groups) > 0:
            logger.warning(
                f"{warning_prefix}Drifted group ID array does not preserve group sizes. {mismatched_groups}"
            )
            return False

        return True

    def compute_beam_match_corrections(
        self, drift: tuple[int, int], drifted_group_array: np.ndarray
    ) -> np.ndarray:
        """
        Compute corrections that ensure that matching groups from the two beams have the same number of spatial pixels.

        This is to account for the case where edge groups were drifted off the edge of the array, but the groups for
        each beam are slightly offset relative to each other. In this case, the beam that was closer to the edge will
        lose more pixels compared to its beam partner.

        The result of this method is an array whose value is 1.0 for pixels that are valid and NaN everywhere else.
        Thus, simply multiplying drifted arrays by this array will correct for any spatial pixel differences between
        the two beams.

        NOTE: Because this method runs after `validate_drift` we *know* we're only dealing with groups that were drifted
        off the edge of the array.
        """
        correction_array = np.empty_like(drifted_group_array) * np.nan
        max_group = int(np.nanmax(drifted_group_array))

        for even_group in range(0, max_group, 2):
            even_idx = np.where(drifted_group_array == even_group)
            even_spatial_slice, even_spectral_slice = self.group_id_convert_idx_to_2d_slice(
                even_idx
            )
            even_num_spatial_px = even_spatial_slice.stop - even_spatial_slice.start

            odd_group = even_group + 1
            odd_idx = np.where(drifted_group_array == odd_group)
            odd_spatial_slice, odd_spectral_slice = self.group_id_convert_idx_to_2d_slice(odd_idx)
            odd_num_spatial_px = odd_spatial_slice.stop - odd_spatial_slice.start

            if spatial_diff := even_num_spatial_px - odd_num_spatial_px:
                if spatial_diff > 0:
                    corrected_group = even_group
                    if drift[0] > 0:
                        even_spatial_slice = slice(
                            even_spatial_slice.start, even_spatial_slice.stop - spatial_diff
                        )
                    elif drift[0] < 0:
                        even_spatial_slice = slice(
                            even_spatial_slice.start + spatial_diff, even_spatial_slice.stop
                        )
                    else:
                        raise ValueError(
                            f"Spatial drift is 0, but group {even_group} has more px than its beam counterpart"
                        )

                else:
                    corrected_group = odd_group
                    if drift[0] > 0:
                        odd_spatial_slice = slice(
                            odd_spatial_slice.start, odd_spatial_slice.stop + spatial_diff
                        )
                    elif drift[0] < 0:
                        odd_spatial_slice = slice(
                            odd_spatial_slice.start - spatial_diff, odd_spatial_slice.stop
                        )
                    else:
                        raise ValueError(
                            f"Spatial drift is 0, but group {odd_group} has more px that its beam counterpart"
                        )
                logger.info(
                    f"Group {even_group} and {odd_group} were drifted off the edge by different amounts. Adjusting group {corrected_group} by {spatial_diff} px."
                )

            correction_array[even_spatial_slice, even_spectral_slice] = 1.0
            correction_array[odd_spatial_slice, odd_spectral_slice] = 1.0

        return correction_array

    def write_drifted_metrology_arrays(self, drifted_arrays_dict: dict[str, np.ndarray]) -> None:
        """Write the drifted IFU metrology arrays to disk."""
        for task_tag, array in drifted_arrays_dict.items():
            tags = [DlnirspTag.intermediate_frame(), task_tag]
            self.write(data=array, tags=tags, encoder=fits_array_encoder)
