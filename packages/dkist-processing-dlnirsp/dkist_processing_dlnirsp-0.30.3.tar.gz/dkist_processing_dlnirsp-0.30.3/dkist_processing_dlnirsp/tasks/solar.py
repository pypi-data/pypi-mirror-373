"""Module for computing a solar gain image. See :doc:`this page </gain>` for more information."""

import numpy as np
from dkist_processing_common.codecs.asdf import asdf_decoder
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_processing_math.arithmetic import divide_arrays_by_array
from dkist_processing_math.arithmetic import subtract_array_from_arrays
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_service_configuration.logging import logger

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks.dlnirsp_base import DlnirspTaskBase
from dkist_processing_dlnirsp.tasks.mixin.corrections import CorrectionsMixin

__all__ = ["SolarCalibration"]


class SolarCalibration(DlnirspTaskBase, CorrectionsMixin, QualityMixin):
    """
    Task for computing an intermediate solar gain image.

    The solar gain is used to correct the response of science images. Importantly, the lamp gain is NOT applied to the
    final solar gain. Thus, the solar gain contains both lamp and solar gain signals and can be used to correct science
    data by itself.
    """

    record_provenance = True

    def run(self) -> None:
        """
        Compute a solar gain image with the solar spectrum removed.

        1. Apply dark, lamp, and geometric corrections to all solar gain frames and average them together.

        2. Compute a single characteristic spectrum across all slitbeams and place into the full array

        3. Re-apply the geometric calibration (spectral shifts and scales) to the characteristic spectra

        4. Remove the characteristic solar spectra from the dark-corrected solar gain image

        5. Rescale each slitbeam to have the same average value as the raw, dark corrected solar gain image

        6. Write the final, solar-spectrum-removed, solar gain image.
        """
        with self.apm_task_step("Apply dark and lamp corrections"):
            logger.info("Computing average dark/lamp corrected gains")
            self.compute_average_corrected_gains()

        with self.apm_task_step("Compute characteristic spectra"):
            logger.info("Computing characteristic spectra")
            characteristic_spectra = self.compute_characteristic_spectra()

            self.write(
                data=characteristic_spectra,
                tags=[DlnirspTag.frame(), DlnirspTag.debug(), DlnirspTag.task("SC_PAD_CHAR_SPEC")],
                encoder=fits_array_encoder,
            )

        with self.apm_task_step("Re-distort characteristic spectra"):
            logger.info("Re-distorting characteristic spectra")
            distorted_char_spectra = self.redistort_characteristic_spectra(characteristic_spectra)

            logger.info("Normalizing characteristic spectra")
            distorted_char_spectra /= np.nanpercentile(
                distorted_char_spectra,
                self.parameters.solar_characteristic_spectra_normalization_percentage,
            )

            self.write(
                data=distorted_char_spectra,
                tags=[DlnirspTag.frame(), DlnirspTag.debug(), DlnirspTag.task("SC_CHAR_DISTORT")],
                encoder=fits_array_encoder,
            )

        with self.apm_task_step("Remove characteristic spectra"):
            logger.info("Removing characteristic spectra")
            cleaned_gain = self.remove_solar_signal(distorted_char_spectra)

        with self.apm_writing_step("Write solar flat calibration"):
            logger.info("Writing solar flat calibration")
            self.write(
                data=cleaned_gain,
                tags=[DlnirspTag.intermediate_frame(), DlnirspTag.task_solar_gain()],
                encoder=fits_array_encoder,
            )

        with self.apm_processing_step("Computing and logging quality metrics"):
            no_of_raw_solar_frames: int = self.scratch.count_all(
                tags=[DlnirspTag.linearized_frame(), DlnirspTag.task_solar_gain()],
            )

            self.quality_store_task_type_counts(
                task_type=TaskName.solar_gain.value, total_frames=no_of_raw_solar_frames
            )

    def compute_average_corrected_gains(self):
        """
        Compute a single, averaged frame from all linearized solar gain frames.

        Also apply dark, lamp, and geometric calibrations. If there are multiple exposure times present in the solar
        gain images, all frames for a single exposure time are averged prior to dark correction. Then all averaged
        exposure time frames are averaged again into a single frame.
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
            avg_gain_array = average_numpy_arrays(gain_arrays)

            logger.info("Applying dark calibration to average solar gain frame")
            dark_corrected_array = next(
                subtract_array_from_arrays(arrays=avg_gain_array, array_to_subtract=dark_array)
            )

            all_exp_times.append(dark_corrected_array)

        logger.info(f"Computing final average gain array for {len(all_exp_times)} exposure times")
        avg_gain_array = average_numpy_arrays(all_exp_times)

        # This is the array we remove the characteristic solar spectrum from to produce the final gain array
        self.write(
            data=avg_gain_array,
            tags=[DlnirspTag.intermediate_frame(), DlnirspTag.task("SC_DARK_ONLY")],
            encoder=fits_array_encoder,
        )

        logger.info("Loading lamp calibration")
        lamp_array = next(
            self.read(
                tags=[DlnirspTag.intermediate_frame(), DlnirspTag.task_lamp_gain()],
                decoder=fits_array_decoder,
            )
        )

        logger.info("Applying lamp calibration")
        lamp_corrected_array = next(
            divide_arrays_by_array(arrays=avg_gain_array, array_to_divide_by=lamp_array)
        )

        logger.info("Loading geometric calibration")

        geometric_correction = next(
            self.read(
                tags=[DlnirspTag.intermediate(), DlnirspTag.task_geometric()], decoder=asdf_decoder
            )
        )
        shifts = geometric_correction["spectral_shifts"]
        scales = geometric_correction["spectral_scales"]
        reference_wavelength_axis = geometric_correction["reference_wavelength_axis"]

        logger.info("Applying geometric calibration")
        final_gain_array = next(
            self.corrections_remove_spec_geometry(
                arrays=lamp_corrected_array,
                shift_dict=shifts,
                scale_dict=scales,
                reference_wavelength_axis=reference_wavelength_axis,
                handle_nans=True,
            )
        )

        self.write(
            data=final_gain_array,
            tags=[DlnirspTag.intermediate_frame(), DlnirspTag.task("SC_FULL_CORR")],
            encoder=fits_array_encoder,
        )

    def compute_characteristic_spectra(self) -> np.ndarray:
        """
        Compute a full-frame characteristic spectra.

        A single characteristic spectrum is computed across *all* slitbeams and then expanded to fill each slitbeam
        across the whole array.
        """
        corrected_avg_gain = next(
            self.read(
                tags=[DlnirspTag.intermediate_frame(), DlnirspTag.task("SC_FULL_CORR")],
                decoder=fits_array_decoder,
            )
        )

        num_slitbeams = self.constants.num_beams * self.constants.num_slits
        stacked_slitbeams = np.vstack(np.split(corrected_avg_gain, num_slitbeams, axis=1))
        single_characteristic_spectrum = np.nanmedian(stacked_slitbeams, axis=0)
        spatial_size = corrected_avg_gain.shape[0]
        spectral_size = stacked_slitbeams.shape[1]
        single_slitbeam_characteristic_spectra = (
            np.ones((spatial_size, spectral_size)) * single_characteristic_spectrum
        )

        characteristic_spectra = np.hstack([single_slitbeam_characteristic_spectra] * num_slitbeams)

        if characteristic_spectra.shape != corrected_avg_gain.shape:
            raise ValueError("Characteristic spectra is malformed")

        # Re-enforce NaN's in non-illuminated portions. Not strictly necessary, but otherwise the characteristic spectra
        # would look really wrong (even though they wouldn't be).
        characteristic_spectra[~self.group_id_rectified_illuminated_idx] = np.nan

        return characteristic_spectra

    def redistort_characteristic_spectra(self, characteristic_spectra: np.ndarray) -> np.ndarray:
        """Distort a characteristic spectra to re-apply the spectral curvature and scales."""
        logger.info("Loading geometric calibration")
        geometric_correction = next(
            self.read(
                tags=[DlnirspTag.intermediate(), DlnirspTag.task_geometric()],
                decoder=asdf_decoder,
            )
        )
        shifts = geometric_correction["spectral_shifts"]
        scales = geometric_correction["spectral_scales"]
        reference_wavelength_axis = geometric_correction["reference_wavelength_axis"]

        distorted_char_spec = next(
            self.corrections_apply_spec_geometry(
                arrays=characteristic_spectra,
                shift_dict=shifts,
                scale_dict=scales,
                reference_wavelength_axis=reference_wavelength_axis,
                handle_nans=True,
            )
        )

        return distorted_char_spec

    def remove_solar_signal(self, characteristic_spectra: np.ndarray) -> np.ndarray:
        """
        Remove a characteristic solar spectra from the solar gain frames.

        The solar spectra are removed from the dark-corrected solar gain frames so that the final spectra also contains
        the lamp gain signal.
        """
        dark_corrected_avg_solar_gain = next(
            self.read(
                tags=[
                    DlnirspTag.intermediate_frame(),
                    DlnirspTag.task("SC_DARK_ONLY"),
                ],
                decoder=fits_array_decoder,
            )
        )

        final_gain = dark_corrected_avg_solar_gain / characteristic_spectra
        return final_gain
