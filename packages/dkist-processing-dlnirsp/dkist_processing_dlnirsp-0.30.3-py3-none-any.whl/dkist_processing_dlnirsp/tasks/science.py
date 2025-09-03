"""Produce L1 DL-NIRSP science data from linearized, L0 inputs. See :doc:`this page </science_calibration>` for more information."""

from dataclasses import dataclass
from functools import cache
from functools import cached_property
from typing import Iterable

import numpy as np
import scipy.interpolate as spi
from astropy.convolution import Gaussian2DKernel
from astropy.convolution import convolve_fft
from astropy.convolution import interpolate_replace_nans
from astropy.io import fits
from astropy.time import Time
from astropy.time import TimeDelta
from dkist_processing_common.codecs.asdf import asdf_decoder
from dkist_processing_common.codecs.fits import fits_access_decoder
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.models.tags import EXP_TIME_ROUND_DIGITS
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_processing_math.arithmetic import divide_arrays_by_array
from dkist_processing_math.arithmetic import subtract_array_from_arrays
from dkist_processing_math.linear_algebra import nd_left_matrix_multiply
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_processing_pac.optics.telescope import Telescope
from dkist_service_configuration.logging import logger
from scipy.spatial import Delaunay

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.parsers.dlnirsp_l0_fits_access import DlnirspL0FitsAccess
from dkist_processing_dlnirsp.parsers.wcs_corrections import correct_crpix_values
from dkist_processing_dlnirsp.parsers.wcs_corrections import correct_header_PC_matrix
from dkist_processing_dlnirsp.tasks.dlnirsp_base import DlnirspTaskBase
from dkist_processing_dlnirsp.tasks.mixin.corrections import CorrectionsMixin

cached_info_logger = cache(logger.info)

__all__ = ["ScienceCalibration"]


@dataclass
class CalibrationCollection:
    """Dataclass to hold all calibration objects and allow for easy, property-based access."""

    bad_pixel_map: np.ndarray
    NaN_correction_kernel: np.ndarray
    dark_dict: dict
    solar_gain: np.ndarray
    spec_shift: dict[int, np.ndarray]
    spec_scales: dict[int, np.ndarray]
    reference_wavelength_axis: np.ndarray
    geo_corr_ifu_x_pos: np.ndarray
    geo_corr_ifu_y_pos: np.ndarray
    demod_matrices: np.ndarray | None

    @cached_property
    def ifu_spatial_points(self) -> np.ndarray:
        """
        Return the (X, Y) IFU (spatial) coordinates corresponding to each spatial pixel.

        Shape is (num_spatial_points, 2).
        """
        full_points = np.stack([self.geo_corr_ifu_x_pos, self.geo_corr_ifu_y_pos], -1)

        # Here's where we assume that the IFU FOV position is not dependent on wavelength.
        # (a pretty good assumption)
        points = np.nanmedian(full_points, axis=1)  # Will have shape (num_spatial_pos, 2)

        return points

    @cached_property
    def spatial_mask(self) -> np.ndarray:
        """
        Return boolean mask that selects spatial positions that aren't all NaN.

        I.e., selects all spatial positions that have *any* data.
        """
        spatial_mask = ~np.sum(np.isnan(self.ifu_spatial_points), axis=1).astype(bool)
        return spatial_mask

    @cached_property
    def ifu_shape(self) -> tuple[int, int]:
        """Return the spatial shape of the remapped IFU array, in pixels."""
        ifu_shape = self.ifu_output_grid_coordinates[0].shape
        return ifu_shape

    @cached_property
    def ifu_output_grid_coordinates(self) -> tuple[np.ndarray, np.ndarray]:
        """
        Return the grids onto which data will be interpolated when remapping to the IFU cube.

        I.e., the IFU "pixel" locations of the output cube. The IFU coordinate arrays are already in IFU "pixel" units,
        so we just construct coordinates based on the ranges of those values.
        """
        # + 1 at the end so we include the last real data point. It doesn't matter if we go over a bit because
        # extrapolation is turned off.
        x_vec = np.arange(
            np.nanmin(self.geo_corr_ifu_x_pos), np.nanmax(self.geo_corr_ifu_x_pos) + 1, step=1
        )
        y_vec = np.arange(
            np.nanmin(self.geo_corr_ifu_y_pos), np.nanmax(self.geo_corr_ifu_y_pos) + 1, step=1
        )
        ifu_x_grid, ifu_y_grid = np.meshgrid(x_vec, y_vec)
        logger.info(f"IFU will have spatial shape {ifu_x_grid.shape}")
        return ifu_x_grid, ifu_y_grid

    @cached_property
    def ifu_delaunay(self) -> Delaunay:
        """
        Return the Delaunay tessellation of the coordinates of the pre-mapped IFU coordinates.

        Computing this once *greatly* speeds up remapping because every science frame has the same tessellation and it's
        a fairly expensive calculation.
        """
        ifu_delaunay = Delaunay(self.ifu_spatial_points[self.spatial_mask])
        return ifu_delaunay


class ScienceCalibration(
    DlnirspTaskBase,
    CorrectionsMixin,
    QualityMixin,
):
    """
    Task class for DL-NIRSP science calibration of polarized and non-polarized data.

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
        Run science calibration.

        - Collect all calibration objects needed
        - Process all science frames
        """
        with self.apm_task_step("Load calibration objects"):
            logger.info("Loading calibration objects")
            calibrations = self.collect_calibration_objects()

        with self.apm_task_step("Generate remapped bad pixel mask"):
            logger.info("Generating remapped bad pixel mask")
            self.save_bad_pixel_cube(calibrations)

        with self.apm_task_step("Process science frames"):
            logger.info("Processing science frames")
            self.process_science_frames(calibrations=calibrations)

        with self.apm_processing_step("Computing and logging quality metrics"):
            no_of_raw_science_frames: int = self.scratch.count_all(
                tags=[
                    DlnirspTag.linearized_frame(),
                    DlnirspTag.task_observe(),
                ],
            )

            self.quality_store_task_type_counts(
                task_type=TaskName.observe.value, total_frames=no_of_raw_science_frames
            )

    def collect_calibration_objects(self) -> CalibrationCollection:
        """
        Collect *all* calibration objects that will be needed to calibrate all science frames.

        We do it once here to avoid having to read the cal objects for every science frame.
        """
        logger.info("Loading bad pixel map")
        bad_pixel_map = next(
            self.read(
                tags=[
                    DlnirspTag.intermediate_frame(),
                    DlnirspTag.task_bad_pixel_map(),
                ],
                decoder=fits_array_decoder,
            )
        ).astype(bool)
        NaN_kernel = np.ones(self.parameters.bad_pixel_correction_interpolation_kernel_shape)
        NaN_kernel /= np.sum(NaN_kernel)

        logger.info("Loading dark arrays")
        dark_dict = {
            exp_time: next(
                self.read(
                    tags=DlnirspTag.intermediate_frame_dark(exposure_time=exp_time),
                    decoder=fits_array_decoder,
                )
            )
            for exp_time in self.constants.observe_exposure_times
        }

        logger.info("Loading solar gain array")
        solar_gain = next(
            self.read(
                tags=[DlnirspTag.intermediate_frame(), DlnirspTag.task_solar_gain()],
                decoder=fits_array_decoder,
            )
        )

        logger.info("Loading geometric corrections")
        geometric_correction = next(
            self.read(
                tags=[DlnirspTag.intermediate(), DlnirspTag.task_geometric()], decoder=asdf_decoder
            )
        )
        spec_shifts = geometric_correction["spectral_shifts"]
        spec_scales = geometric_correction["spectral_scales"]
        reference_wavelength_axis = geometric_correction["reference_wavelength_axis"]

        with self.apm_processing_step("Prepare IFU remapping information"):
            logger.info("Prepping IFU remapping data.")
            ifu_x_points, ifu_y_points = self.apply_geometry_to_ifu_files(
                spec_shifts=spec_shifts,
                spec_scales=spec_scales,
                reference_wavelength_axis=reference_wavelength_axis,
            )

        demod_matrices = None
        if self.constants.correct_for_polarization:
            logger.info("Loading demodulation matrices")
            demod_matrices = next(
                self.read(
                    tags=[DlnirspTag.intermediate_frame(), DlnirspTag.task_demodulation_matrices()],
                    decoder=fits_array_decoder,
                )
            )

        return CalibrationCollection(
            bad_pixel_map=bad_pixel_map,
            NaN_correction_kernel=NaN_kernel,
            dark_dict=dark_dict,
            solar_gain=solar_gain,
            spec_shift=spec_shifts,
            spec_scales=spec_scales,
            reference_wavelength_axis=reference_wavelength_axis,
            geo_corr_ifu_x_pos=ifu_x_points,
            geo_corr_ifu_y_pos=ifu_y_points,
            demod_matrices=demod_matrices,
        )

    def process_science_frames(self, calibrations: CalibrationCollection) -> None:
        """
        Fully process all science frames.

        Loops through all tiles in all mosaic repeats.
        """
        for mosaic_num in range(self.constants.num_mosaic_repeats):
            for dither_step in range(self.constants.num_dither_steps):
                for X_tile in range(1, self.constants.num_mosaic_tiles_x + 1):
                    for Y_tile in range(1, self.constants.num_mosaic_tiles_y + 1):
                        debug_tags = [
                            DlnirspTag.frame(),
                            DlnirspTag.debug(),
                            DlnirspTag.mosaic_num(mosaic_num),
                            DlnirspTag.dither_step(dither_step),
                            DlnirspTag.mosaic_tile_x(X_tile),
                            DlnirspTag.mosaic_tile_y(Y_tile),
                        ]

                        if self.constants.correct_for_polarization:
                            logger.info(
                                f"Processing polarimetric frames for {mosaic_num = }, {dither_step  = }, {X_tile = }, {Y_tile = }"
                            )
                            calibrated_frame, calibrated_header = self.process_polarimetric_frames(
                                mosaic_num, dither_step, X_tile, Y_tile, calibrations=calibrations
                            )

                            self.write(
                                calibrated_frame,
                                tags=debug_tags + [DlnirspTag.task("PRE_COMBINE")],
                                encoder=fits_array_encoder,
                                overwrite=True,
                            )

                            logger.info("Combining polarimetric beams")
                            combined_frame = self.combine_polarimetric_beams(calibrated_frame)

                            logger.info("Applying telescope polarization correction")
                            combined_frame = self.apply_telescope_polarization_correction(
                                combined_frame, calibrated_header
                            )

                        else:
                            logger.info(
                                f"Processing frame for {mosaic_num = }, {dither_step = }, {X_tile = }, and {Y_tile = }"
                            )
                            (
                                basic_corrected_array,
                                header,
                            ) = self.bad_pix_dark_and_gain_correct_single_frame(
                                mosaic_num,
                                dither_step,
                                X_tile,
                                Y_tile,
                                modstate=1,
                                calibrations=calibrations,
                            )
                            calibrated_array = next(
                                self.corrections_remove_spec_geometry(
                                    arrays=basic_corrected_array,
                                    shift_dict=calibrations.spec_shift,
                                    scale_dict=calibrations.spec_scales,
                                    reference_wavelength_axis=calibrations.reference_wavelength_axis,
                                    handle_nans=True,
                                )
                            )
                            calibrated_header = self.compute_header_dates(header)
                            self.write(
                                calibrated_array,
                                tags=debug_tags + [DlnirspTag.task("PRE_COMBINE")],
                                encoder=fits_array_encoder,
                                overwrite=True,
                            )

                            logger.info("Combining beams")
                            combined_frame = self.combine_spectrographic_beams(calibrated_array)

                        self.write(
                            data=combined_frame,
                            tags=debug_tags + [DlnirspTag.task("SLIT_STACKED")],
                            encoder=fits_array_encoder,
                        )

                        logger.info("Remapping to IFU cube")
                        ifu_frame = self.remap_ifu_cube(combined_frame, calibrations)

                        logger.info("Applying WCS correction")
                        wcs_corrected_header = self.apply_WCS_corrections(calibrated_header)

                        logger.info("Adding MINDEX keys")
                        final_header = self.add_mindex_keys(
                            wcs_corrected_header, X_tile_num=X_tile, Y_tile_num=Y_tile
                        )

                        logger.info("Writing calibrated array")
                        self.write_calibrated_array(
                            ifu_frame, final_header, mosaic_num, dither_step, X_tile, Y_tile
                        )

    def process_polarimetric_frames(
        self,
        mosaic_num: int,
        dither_step: int,
        X_tile_num: int,
        Y_tile_num: int,
        calibrations: CalibrationCollection,
    ) -> tuple[np.ndarray, fits.Header]:
        """Apply calibration objects to all modstates in a single tile and then demodulate the result."""
        data_shape = self.unrectified_array_shape
        modstate_stack = np.zeros(data_shape + (self.constants.num_modstates,))
        header_list = []

        for modstate in range(1, self.constants.num_modstates + 1):
            logger.info(f"Working on {modstate = }")
            corrected_data, header = self.bad_pix_dark_and_gain_correct_single_frame(
                mosaic_num=mosaic_num,
                dither_step=dither_step,
                X_tile_num=X_tile_num,
                Y_tile_num=Y_tile_num,
                modstate=modstate,
                calibrations=calibrations,
            )
            modstate_stack[:, :, modstate - 1] = corrected_data
            header_list.append(header)

        logger.info("Demodulating data")
        demodulated_data = nd_left_matrix_multiply(
            vector_stack=modstate_stack, matrix_stack=calibrations.demod_matrices
        )
        self.write(
            data=demodulated_data,
            tags=[
                DlnirspTag.frame(),
                DlnirspTag.debug(),
                DlnirspTag.task("DEMOD"),
                DlnirspTag.mosaic_num(mosaic_num),
                DlnirspTag.dither_step(dither_step),
                DlnirspTag.mosaic_tile_x(X_tile_num),
                DlnirspTag.mosaic_tile_y(Y_tile_num),
            ],
            encoder=fits_array_encoder,
            overwrite=True,
        )
        corrected_header = self.compute_header_dates(header_list)

        logger.info("Applying geometric correction")
        geo_corrected_array = np.zeros(self.rectified_array_shape + (4,))
        for stokes in range(4):
            geo_corrected_array[:, :, stokes] = next(
                self.corrections_remove_spec_geometry(
                    arrays=demodulated_data[:, :, stokes],
                    shift_dict=calibrations.spec_shift,
                    scale_dict=calibrations.spec_scales,
                    reference_wavelength_axis=calibrations.reference_wavelength_axis,
                    handle_nans=True,
                )
            )

        self.write(
            data=geo_corrected_array,
            tags=[
                DlnirspTag.frame(),
                DlnirspTag.debug(),
                DlnirspTag.task("FULL_CORRECTED"),
                DlnirspTag.mosaic_num(mosaic_num),
                DlnirspTag.dither_step(dither_step),
                DlnirspTag.mosaic_tile_x(X_tile_num),
                DlnirspTag.mosaic_tile_y(Y_tile_num),
            ],
            encoder=fits_array_encoder,
            overwrite=True,
        )

        return geo_corrected_array, corrected_header

    def bad_pix_dark_and_gain_correct_single_frame(
        self,
        mosaic_num: int,
        dither_step: int,
        X_tile_num: int,
        Y_tile_num: int,
        modstate: int,
        calibrations: CalibrationCollection,
    ) -> tuple[np.ndarray, fits.Header]:
        """Apply dark and gain corrections and mask bad pixels to a frame from a single mosaic tile and modstate."""
        tags = [
            DlnirspTag.linearized_frame(),
            DlnirspTag.task_observe(),
            DlnirspTag.mosaic_num(mosaic_num),
            DlnirspTag.dither_step(dither_step),
            DlnirspTag.mosaic_tile_x(X_tile_num),
            DlnirspTag.mosaic_tile_y(Y_tile_num),
            DlnirspTag.modstate(modstate),
        ]

        observe_object_list = list(
            self.read(tags=tags, decoder=fits_access_decoder, fits_access_class=DlnirspL0FitsAccess)
        )
        num_accumulations = len(observe_object_list)
        logger.info(
            f"Found {num_accumulations} data cycles for {mosaic_num = }, {dither_step = }, {X_tile_num = }, and {Y_tile_num = }"
        )

        # TODO: Do a better job of getting a representative header
        random_observe_object = observe_object_list[0]
        observe_data = average_numpy_arrays((o.data for o in observe_object_list))
        observe_exp_time = round(random_observe_object.fpa_exposure_time_ms, EXP_TIME_ROUND_DIGITS)
        if observe_exp_time not in calibrations.dark_dict.keys():
            raise ValueError(f"Could not find matching dark for {observe_exp_time = }")

        dark_corrected_data = next(
            subtract_array_from_arrays(
                arrays=observe_data, array_to_subtract=calibrations.dark_dict[observe_exp_time]
            )
        )

        self.write(
            data=dark_corrected_data,
            tags=[
                DlnirspTag.frame(),
                DlnirspTag.debug(),
                DlnirspTag.task("DARK_CORRECTED"),
                DlnirspTag.mosaic_num(mosaic_num),
                DlnirspTag.dither_step(dither_step),
                DlnirspTag.mosaic_tile_x(X_tile_num),
                DlnirspTag.mosaic_tile_y(Y_tile_num),
                DlnirspTag.modstate(modstate),
            ],
            encoder=fits_array_encoder,
            overwrite=True,
        )

        gain_corrected_data = next(
            divide_arrays_by_array(
                arrays=dark_corrected_data, array_to_divide_by=calibrations.solar_gain
            )
        )

        self.write(
            data=gain_corrected_data,
            tags=[
                DlnirspTag.frame(),
                DlnirspTag.debug(),
                DlnirspTag.task("GAIN_CORRECTED"),
                DlnirspTag.mosaic_num(mosaic_num),
                DlnirspTag.dither_step(dither_step),
                DlnirspTag.mosaic_tile_x(X_tile_num),
                DlnirspTag.mosaic_tile_y(Y_tile_num),
                DlnirspTag.modstate(modstate),
            ],
            encoder=fits_array_encoder,
            overwrite=True,
        )

        bad_pixel_corrected_data = self.mask_bad_pixels(gain_corrected_data, calibrations)

        self.write(
            data=bad_pixel_corrected_data,
            tags=[
                DlnirspTag.frame(),
                DlnirspTag.debug(),
                DlnirspTag.task("BAD_PX_CORRECTED"),
                DlnirspTag.mosaic_num(mosaic_num),
                DlnirspTag.dither_step(dither_step),
                DlnirspTag.mosaic_tile_x(X_tile_num),
                DlnirspTag.mosaic_tile_y(Y_tile_num),
                DlnirspTag.modstate(modstate),
            ],
            encoder=fits_array_encoder,
            overwrite=True,
        )

        return bad_pixel_corrected_data, random_observe_object.header

    def mask_bad_pixels(self, array: np.ndarray, calibrations: CalibrationCollection) -> np.ndarray:
        """
        Interpolate over bad pixels using a 2D Gaussian kernel.

        Interpolation is done using `astropy.convolution.interpolate_replace_nans` with a Gaussian kernel defined
        by the `~dkist_processing_dlnirsp.models.parameters.DlnirspParameters.bad_pixel_correction_interpolation_kernel_shape`
        pipeline parameter.
        """
        bad_pixel_map = calibrations.bad_pixel_map
        array[bad_pixel_map] = np.nan

        corrected_array = interpolate_replace_nans(
            array,
            kernel=calibrations.NaN_correction_kernel,
            convolve=convolve_fft,
            # Using "fill" with a NaN fill value here has the effect of *ignoring* pixels outside the array boundaries.
            boundary="fill",
            fill_value=np.nan,
        )

        return corrected_array

    def combine_spectrographic_beams(self, data: np.ndarray) -> np.ndarray:
        """
        Combine the 2 DL beams for non-polarimetric data.

        The combination in this case is a simple average.
        """
        combined_list = []

        group_id_to_slitbeam_mapping = self.group_id_slitbeam_group_dict
        for slit in range(self.constants.num_slits):
            groups = group_id_to_slitbeam_mapping[slit * 2]
            for even_group in groups:
                odd_group = even_group + 1

                even_idxs = self.group_id_get_idx(group_id=even_group, rectified=True)
                even_slices = self.group_id_convert_idx_to_2d_slice(even_idxs)

                odd_idxs = self.group_id_get_idx(group_id=odd_group, rectified=True)
                odd_slices = self.group_id_convert_idx_to_2d_slice(odd_idxs)

                even_data = data[even_slices]
                odd_data = data[odd_slices]
                combined_data = 0.5 * (even_data + odd_data)

                combined_list.append(combined_data)

        final_stack = np.vstack(combined_list)

        return final_stack[:, :, None]  # Add "stokes" dimension so later loops will work

    def combine_polarimetric_beams(self, data: np.ndarray) -> np.ndarray:
        """
        Combine the 2 DL beams for polarimetric data such that each Stokes state is normalized by Stokes I.

        In other words:

        avg_I = (beam1_I + beam2_I) / 2
        avg_Q = (beam1_Q / beam1_I + beam2_Q / beam2_I) / 2. * avg_I

        ...and the same for U and V
        """
        avg_I_data = self.combine_spectrographic_beams(data[:, :, 0])[:, :, 0]

        avg_data = np.zeros(avg_I_data.shape + (4,))
        avg_data[:, :, 0] = avg_I_data
        for stokes in range(1, 4):
            normed_data = data[:, :, stokes] / data[:, :, 0]
            avg_data[:, :, stokes] = (
                self.combine_spectrographic_beams(normed_data)[:, :, 0] * avg_I_data
            )

        return avg_data

    def apply_telescope_polarization_correction(
        self, stokes_stack: np.ndarray, header: fits.Header
    ) -> np.ndarray:
        """
        Apply a Mueller matrix to the input data that removes the effects of the Telescope.

        The "Telescope" in this case is everything upstream of M7. The inverse model is computed for the time of
        observation.
        """
        fits_obj = DlnirspL0FitsAccess.from_header(header)
        tm = Telescope.from_fits_access(fits_obj)
        mueller_matrix = tm.generate_inverse_telescope_model(
            M12=True, rotate_to_fixed_SDO_HINODE_polarized_frame=True, swap_UV_signs=True
        )
        corrected_data = nd_left_matrix_multiply(
            vector_stack=stokes_stack, matrix_stack=mueller_matrix
        )

        return corrected_data

    def write_calibrated_array(
        self,
        array: np.ndarray,
        header: fits.Header,
        mosaic_num: int,
        dither_step: int,
        X_tile_num: int,
        Y_tile_num: int,
    ) -> None:
        """
        Write a calibrated array to disk and tag it appropriately.

        Input polarimetric data produce 4 calibration files; one for each Stokes parameter.
        """
        if self.constants.correct_for_polarization:
            stokes_targets = self.constants.stokes_params
        else:
            stokes_targets = ["I"]

        stokes_I_data = array[:, :, :, 0]
        for i, stokes in enumerate(stokes_targets):
            final_data = array[:, :, :, i]
            if self.constants.correct_for_polarization:
                header = self.add_L1_pol_headers(
                    input_header=header, stokes_data=final_data, stokes_I_data=stokes_I_data
                )

            tags = [
                DlnirspTag.calibrated(),
                DlnirspTag.frame(),
                DlnirspTag.stokes(stokes),
                DlnirspTag.mosaic_num(mosaic_num),
                DlnirspTag.dither_step(dither_step),
                DlnirspTag.mosaic_tile_x(X_tile_num),
                DlnirspTag.mosaic_tile_y(Y_tile_num),
            ]
            hdul = fits.HDUList([fits.PrimaryHDU(header=header, data=final_data)])
            filename = self.write(
                data=hdul,
                tags=tags,
                encoder=fits_hdulist_encoder,
            )

            logger.info(f"Wrote calibrated frame for {tags = } to {str(filename)}")

    def apply_geometry_to_ifu_files(
        self,
        spec_shifts: dict[int, np.ndarray],
        spec_scales: dict[int, np.ndarray],
        reference_wavelength_axis: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Apply geometric corrections and combine the beams for the IFU mapping arrays.

        The resultant arrays allows us to correctly map the CALIBRATED science frames.
        """
        points_list = []
        ifu_x_pos_array = next(
            self.read(
                tags=[DlnirspTag.intermediate_frame(), DlnirspTag.task_drifted_ifu_x_pos()],
                decoder=fits_array_decoder,
            )
        )
        ifu_y_pos_array = next(
            self.read(
                tags=[DlnirspTag.intermediate_frame(), DlnirspTag.task_drifted_ifu_y_pos()],
                decoder=fits_array_decoder,
            )
        )
        for name, array in zip(
            ["FXPOS", "FYPOS"],
            [ifu_x_pos_array, ifu_y_pos_array],
        ):
            geo_corrected_array = next(
                self.corrections_remove_spec_geometry(
                    arrays=array,
                    shift_dict=spec_shifts,
                    scale_dict=spec_scales,
                    reference_wavelength_axis=reference_wavelength_axis,
                    handle_nans=True,
                )
            )
            # Slice removes dummy Stokes dimension
            combined_array = self.combine_spectrographic_beams(geo_corrected_array)[:, :, 0]
            tags = [DlnirspTag.frame(), DlnirspTag.debug(), DlnirspTag.task(f"REMAPPED_IFU_{name}")]
            self.write(data=combined_array, tags=tags, encoder=fits_array_encoder, overwrite=True)
            points_list.append(combined_array)

        return tuple(points_list)

    @staticmethod
    def compute_header_dates(
        headers: Iterable[fits.Header] | fits.Header,
    ) -> fits.Header:
        """
        Generate correct DATE-??? header keys from a set of input headers.

        Keys are computed thusly:
        * DATE-BEG - The (Spec-0122) DATE-OBS of the earliest input header
        * DATE-END - The (Spec-0122) DATE-OBS of the latest input header, plus the FPA exposure time

        Returns
        -------
        fits.Header
            A copy of the earliest header, but with correct DATE-??? keys
        """
        # TODO: This method is currently wrong. We need info from the DL team to get this right. SDPO-065 is a clue.
        if isinstance(headers, fits.Header) or isinstance(
            headers, fits.hdu.compressed.CompImageHeader
        ):
            headers = [headers]

        sorted_obj_list = sorted(
            [DlnirspL0FitsAccess.from_header(h) for h in headers], key=lambda x: Time(x.time_obs)
        )
        date_beg = sorted_obj_list[0].time_obs
        exp_time = TimeDelta(sorted_obj_list[-1].fpa_exposure_time_ms / 1000.0, format="sec")
        date_end = (Time(sorted_obj_list[-1].time_obs) + exp_time).isot

        header = sorted_obj_list[0].header
        header["DATE-BEG"] = date_beg
        header["DATE-END"] = date_end

        return header

    def add_mindex_keys(self, header: fits.Header, X_tile_num: int, Y_tile_num: int) -> fits.Header:
        """
        Add MINDEX[12] keys based on the current mosaic (X, Y) tile location.

        These keys are used by DKIST user tools to reconstruct the mosaic.
        """
        # Note: See `DlnirspWriteL1Frame.add_dataset_headers` for the logic that determines whether these keys survive
        # into the L1 headers.
        header[f"MINDEX1"] = X_tile_num
        header[f"MINDEX2"] = Y_tile_num

        return header

    def apply_WCS_corrections(self, header: fits.Header) -> fits.Header:
        """
        Apply a correction to WCS header keys.

        The correction is in two parts, each based on a pipeline parameter:

        1. The PCi_j matrix is matrix-multiplied by the "pc_correction_matrix" parameter

        2. The CRPIX1 and CRPIX2 values are modified based on the method described by the "crpix_correction_method".
           Each correction method is defined here.
        """
        correction_matrix = self.parameters.wcs_pc_correction_matrix
        cached_info_logger(f"Applying PC correction matrix {correction_matrix.tolist()}")
        header = correct_header_PC_matrix(header, correction_matrix)

        crpix_correction_method = self.parameters.wcs_crpix_correction_method
        cached_info_logger(f"Applying CRPIX correction method '{crpix_correction_method}'")
        OG_crpix1 = header["CRPIX1"]
        OG_crpix2 = header["CRPIX2"]

        new_crpix1, new_crpix2 = correct_crpix_values(OG_crpix1, OG_crpix2, crpix_correction_method)

        header["CRPIX1"] = new_crpix1
        header["CRPIX2"] = new_crpix2

        return header

    def add_L1_pol_headers(
        self, input_header: fits.Header, stokes_data: np.ndarray, stokes_I_data: np.ndarray
    ) -> fits.Header:
        """Compute and add 214 header values specific to polarimetric datasets."""
        # Probably not needed, but just to be safe
        output_header = input_header.copy()

        pol_noise = self.compute_polarimetric_noise(stokes_data, stokes_I_data)
        pol_sensitivity = self.compute_polarimetric_sensitivity(stokes_I_data)
        output_header["POL_NOIS"] = pol_noise
        output_header["POL_SENS"] = pol_sensitivity

        return output_header

    def compute_polarimetric_noise(
        self, stokes_data: np.ndarray, stokes_I_data: np.ndarray
    ) -> float:
        r"""
        Compute the polarimetric noise for a single frame.

        The polarimetric noise, :math:`N`, is defined as

        .. math::

            N = stddev(\frac{F_i}{F_I})

        where :math:`F_i` is a full array of values for Stokes parameter :math:`i` (I, Q, U, V), and :math:`F_I` is the
        full frame of Stokes-I. The stddev is computed across the entire frame.
        """
        return float(np.nanstd(stokes_data / stokes_I_data))

    def compute_polarimetric_sensitivity(self, stokes_I_data: np.ndarray) -> float:
        r"""
        Compute the polarimetric sensitivity for a single frame.

        The polarimetric sensitivity is the smallest signal that can be measured based on the values in the Stokes-I
        frame. The sensitivity, :math:`S`, is computed as

        .. math::

            S = \frac{1}{\sqrt{\mathrm{max}(F_I)}}

        where :math:`F_I` is the full frame of values for Stokes-I.
        """
        return float(1.0 / np.sqrt(np.nanmax(stokes_I_data)))

    def remap_ifu_cube(self, data: np.ndarray, calibrations: CalibrationCollection) -> np.ndarray:
        """Remap the stacked IFU slit into a 3D cube."""
        interp_func = spi.LinearNDInterpolator(
            calibrations.ifu_delaunay, data[calibrations.spatial_mask, :, :]
        )
        ifu_cube_temp_axes = interp_func(*calibrations.ifu_output_grid_coordinates)

        ifu_cube = np.moveaxis(ifu_cube_temp_axes, 2, 0)

        return ifu_cube

    def save_bad_pixel_cube(self, calibrations: CalibrationCollection) -> None:
        """
        Generate a "cubed" version of the Bad Pixel Map.

        Because we mask bad pixels in the L1 data, this cubed bad pixel map is needed so scientists can see which pixels
        in their L1 data are bad pixels.
        """
        float_bad_px_array = calibrations.bad_pixel_map.astype(float)
        geo_corrected_bad_px_array = next(
            self.corrections_remove_spec_geometry(
                arrays=float_bad_px_array,
                shift_dict=calibrations.spec_shift,
                scale_dict=calibrations.spec_scales,
                reference_wavelength_axis=calibrations.reference_wavelength_axis,
                handle_nans=True,
            )
        )

        combined_bad_px_array = self.combine_spectrographic_beams(geo_corrected_bad_px_array)
        # Slice to remove final Stokes dimension
        bad_pixel_mask_cube = self.remap_ifu_cube(
            data=combined_bad_px_array, calibrations=calibrations
        )[:, :, :, 0]

        # Convert back to a "boolean" (i.e., int8) array
        boolean_cube = (bad_pixel_mask_cube > self.parameters.corrections_max_nan_frac).astype(
            np.int8
        )
        # TODO: Tag this as a dataset extra once those are a thing
        self.write(
            data=boolean_cube,
            tags=[DlnirspTag.intermediate_frame(), DlnirspTag.task("BAD_PIXEL_CUBE")],
            encoder=fits_array_encoder,
        )
