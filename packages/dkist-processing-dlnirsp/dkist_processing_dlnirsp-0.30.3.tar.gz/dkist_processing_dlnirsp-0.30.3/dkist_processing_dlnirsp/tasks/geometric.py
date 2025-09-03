"""
Module for computing a universal, relative wavelength solution for all spatial positions.

See :doc:`this page </geometric>` for more information.
"""

from typing import Callable

import numpy as np
import peakutils
import scipy.ndimage as spnd
from astropy.modeling import fitting
from astropy.modeling import polynomial
from astropy.stats import sigma_clip
from dkist_processing_common.codecs.asdf import asdf_encoder
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.codecs.json import json_encoder
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_processing_math.arithmetic import divide_arrays_by_array
from dkist_processing_math.arithmetic import subtract_array_from_arrays
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_service_configuration.logging import logger
from scipy.optimize import minimize

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks.dlnirsp_base import DlnirspTaskBase
from dkist_processing_dlnirsp.tasks.mixin.corrections import CorrectionsMixin

__all__ = ["GeometricCalibration"]


class GeometricCalibration(DlnirspTaskBase, CorrectionsMixin, QualityMixin):
    """
    Task class for computing a "Geometric Calibration" object.

    This calibration allows downstream tasks to adjust each individual spectrum so that all spectra are on the same
    relative wavelength grid. Absolute wavelength calibration is not supported at this time.
    """

    record_provenance = True

    def run(self) -> None:
        """
        Compute a relative wavelength solution for all spectra in all groups.

        1. Average all solar gain images and apply a dark correction

        2. Determine an IFU group near the center of the FOV to use as a reference spectrum

        3. Compute the reference dispersion as the maximum dispersion present in the dispersion metrology array

        4. Compute a reference wavelength axis using the reference spectrum and dispersion

        5. Compute the spectral shift and scale between each spatial pixel and the reference wavelenght axis

        6. Write shifts, scales, and reference wavelength axis to a file
        """
        with self.apm_task_step("Apply dark and lamp corrections"):
            logger.info("Computing average dark/lamp corrected gain image")
            self.compute_average_corrected_gain()

        with self.apm_task_step("Compute spectral curvature"):
            logger.info("Computing spectral curvature")
            shift_dict, scale_dict = self.compute_spectral_curvature_and_dispersion()

        with self.apm_task_step("Compute reference wavelength grid"):
            logger.info("Computing reference wavelength grid")
            reference_wavelength_axis = self.compute_reference_wavelength_axis(
                shift_dict, scale_dict
            )

        with self.apm_writing_step("Write geometric calibration calibration"):
            logger.info("Writing geometric calibration")
            self.write_geometric_calibration(shift_dict, scale_dict, reference_wavelength_axis)

        with self.apm_processing_step("Computing and logging quality metrics"):
            no_of_raw_solar_frames: int = self.scratch.count_all(
                tags=[DlnirspTag.linearized_frame(), DlnirspTag.task_solar_gain()],
            )

            self.quality_store_task_type_counts(
                task_type=TaskName.geometric.value, total_frames=no_of_raw_solar_frames
            )

    def compute_average_corrected_gain(self) -> None:
        """
        Compute a single, averaged frame from all linearized solar gain frames.

        Also remove dark and lamp signals. If there are multiple exposure times present in the solar gain images, all
        frames for a single exposure time are averaged prior to dark correction. Then all averaged exposure time frames
        are averaged again into a single frame.
        """
        all_exp_times = []
        logger.info("Loading lamp calibration")
        lamp_array = next(
            self.read(
                tags=[DlnirspTag.intermediate_frame(), DlnirspTag.task_lamp_gain()],
                decoder=fits_array_decoder,
            )
        )
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
            dark_corrected_array = subtract_array_from_arrays(
                arrays=avg_gain_array, array_to_subtract=dark_array
            )

            logger.info("Applying lamp calibration")
            lamp_corrected_array = next(
                divide_arrays_by_array(arrays=dark_corrected_array, array_to_divide_by=lamp_array)
            )

            all_exp_times.append(lamp_corrected_array)

        logger.info(f"Computing final average gain array for {len(all_exp_times)} exposure times")
        final_gain_array = average_numpy_arrays(all_exp_times)

        self.write(
            data=final_gain_array,
            tags=[DlnirspTag.intermediate_frame(), DlnirspTag.task_avg_unrectified_solar_gain()],
            encoder=fits_array_encoder,
        )

    def compute_spectral_curvature_and_dispersion(
        self,
    ) -> tuple[dict[int, np.ndarray], dict[int, np.ndarray]]:
        """
        Calculate the spectral shift and scale (dispersion) needed to align each spectrum to the same wavelength grid.

        Shifts are fit for every spectrum and then the measured shifts are fit as a function of spatial position for
        each slit beam.

        A relative dispersion is also computed for each spectrum from known absolute dispersions. The dispersion
        correction (i.e., a scale) is applied prior to fitting the shifts. This is needed because each slit has slightly
        different dispersions and optical distortions. This is also true, to a lesser extent, for differences between
        the two polarimetric beams.

        Even though each slitbeam is treated separately, the same reference spectrum is used for *all* spectra and thus
        the result is a relative spectral scale that applies across the entire chip (i.e., all slits and beams).

        Returns
        -------
        dict[int, np.ndarray]
            Dictionary whose keys are group_ids and values are a numpy array containing the spectral shift for each
            spatial pixel in that group.

        dict[int, np.ndarray]
            Dictionary whose keys are group_ids and values are a numpy array containing the relative dispersion for each
            spatial pixel in that group.
        """
        dispersion_array = next(
            self.read(
                tags=[DlnirspTag.intermediate_frame(), DlnirspTag.task_drifted_dispersion()],
                decoder=fits_array_decoder,
            )
        )

        avg_gain_array = next(
            self.read(
                tags=[
                    DlnirspTag.intermediate_frame(),
                    DlnirspTag.task_avg_unrectified_solar_gain(),
                ],
                decoder=fits_array_decoder,
            )
        )

        raw_reference_spectrum, reference_group = self.get_reference_spectrum(
            avg_gain_array=avg_gain_array
        )
        reference_dispersion = self.get_reference_dispersion(dispersion_array=dispersion_array)

        self.write(
            data=reference_dispersion,
            tags=[DlnirspTag.intermediate(), DlnirspTag.task_dispersion()],
            encoder=json_encoder,
        )

        group_dispersion = np.nanmedian(
            self.group_id_get_data(data=dispersion_array, group_id=reference_group)
        )
        scale = group_dispersion / reference_dispersion
        logger.info(f"Reference spectrum dispersion = {group_dispersion} => {scale = }")
        reference_spectrum = self.corrections_shift_and_scale_spectrum(
            raw_reference_spectrum, shift=0.0, scale=scale, extrapolate=False
        )

        self.write(
            reference_spectrum,
            tags=[DlnirspTag.frame(), DlnirspTag.debug(), DlnirspTag.task("GC_REF_SPEC")],
            encoder=fits_array_encoder,
            overwrite=True,
        )

        group_shift_dict = dict()
        group_scale_dict = dict()
        group_id_to_slitbeam_mapping = self.group_id_slitbeam_group_dict
        for slitbeam in group_id_to_slitbeam_mapping.keys():
            logger.info(f"Computing spectral curvature and dispersion for {slitbeam = }")

            # python lists because we don't know how long they will be and appending to numpy arrays is expensive
            curve_abscissa = []
            curve_shifts = []
            curve_scales = []

            groups_in_slitbeam = group_id_to_slitbeam_mapping[slitbeam]

            for group_id in groups_in_slitbeam:
                logger.info(f"Computing curve for {group_id = }")
                group_dispersion = np.nanmedian(
                    self.group_id_get_data(data=dispersion_array, group_id=group_id)
                )
                scale = group_dispersion / reference_dispersion
                logger.info(f"Group dispersion = {group_dispersion} => {scale = }")

                group_data, group_idx = self.group_id_get_data_and_idx(
                    data=avg_gain_array, group_id=group_id
                )
                group_spatial_px = np.unique(group_idx[0])

                for i, spatial_px in enumerate(group_spatial_px):
                    spectrum = group_data[i, :]
                    corrected_spec = self.prep_spectrum_for_fit(spectrum)

                    # self.write(
                    #     data=corrected_spec,
                    #     tags=[DlnirspTag.frame(), DlnirspTag.debug(), DlnirspTag.task(f"TARGET_SPEC_{group_id}_{i}")],
                    #     encoder=fits_array_encoder,
                    # )

                    try:
                        shift = self.fit_single_shift(
                            input_reference_spectrum=reference_spectrum,
                            input_target_spectrum=corrected_spec,
                            scale=scale,
                        )
                    except ValueError:
                        logger.info(
                            f"Spatial px {spatial_px} in {group_id = } failed to fit. Setting values to NaN"
                        )
                        shift = np.nan

                    curve_abscissa.append(spatial_px)
                    curve_shifts.append(shift)
                    curve_scales.append(scale)

            logger.info(f"Fitting shifts for {slitbeam = }")
            curve_abscissa = np.array(curve_abscissa)
            curve_shifts = np.array(curve_shifts)
            curve_scales = np.array(curve_scales)

            # TODO: With MISI do we need to fit? If so this needs to be improved to handle the offsets between
            # the alternating slices
            shift_poly_fit_order = self.parameters.geo_shift_poly_fit_order
            shift_fit_values = self.fit_values_along_slitbeam(
                spatial_pixels=curve_abscissa,
                values=curve_shifts,
                poly_fit_order=shift_poly_fit_order,
            )

            # TODO: Is this the best way to do this?
            curve_shifts[~np.isfinite(curve_shifts)] = 0.0

            debug_data = np.stack([curve_abscissa, curve_shifts, shift_fit_values, curve_scales])
            self.write(
                data=debug_data,
                tags=[
                    DlnirspTag.frame(),
                    DlnirspTag.debug(),
                    DlnirspTag.task(f"GC_RAW_FIT_VALUES_SLITB_{slitbeam}"),
                ],
                encoder=fits_array_encoder,
                overwrite=True,
            )

            slitbeam_group_shifts = self.group_values_by_group_id(
                values=curve_shifts,
                group_ids=groups_in_slitbeam,
            )
            group_shift_dict.update(slitbeam_group_shifts)

            # Don't fit the dispersion, just reformat it so it can be used in the same way as the shifts
            slitbeam_group_scales = self.group_values_by_group_id(
                values=curve_scales,
                group_ids=groups_in_slitbeam,
            )
            group_scale_dict.update(slitbeam_group_scales)

        return group_shift_dict, group_scale_dict

    def compute_reference_wavelength_axis(
        self, shift_dict: dict[int, np.ndarray], scale_dict: dict[int, np.ndarray]
    ) -> np.ndarray:
        """
        Compute a reference wavelength axis that will be used for all spatial positions.

        The largest spectral range spanned by the rectified spectra is considered a starting point. An average solar
        gain frame is then rectified using this spectral range and spectral regions that have minimal real data are
        excluded. These regions may exist where one or two spatial pixels had large errors in their spectral shifts.

        NOTE: When we say "wavelength" here, we're talking about *relative* *pixel* differences in the wavelength axis.
        At some point this could become a true wavelength, but not right now.
        """
        # First compute a "wavelength" range based solely on the computed shifts
        group_spectral_sizes = [
            np.mean(scale_dict[group])
            * (
                self.group_id_get_idx(group_id=group)[1].max()
                - self.group_id_get_idx(group_id=group)[1].min()
            )
            for group in range(self.group_id_num_groups)
        ]
        max_spectral_size = max(group_spectral_sizes)
        flat_shifts = np.hstack(tuple(shift_dict.values()))
        most_negative_shift = max(np.nanmin(flat_shifts), -self.parameters.geo_max_shift_px)
        most_positive_shift = min(np.nanmax(flat_shifts), self.parameters.geo_max_shift_px)

        full_spectral_size = max_spectral_size + abs(most_negative_shift) + abs(most_positive_shift)
        initial_ref_wave = np.arange(full_spectral_size) - abs(most_negative_shift)

        # Now apply the initial reference wavelength and truncate it to only span regions that actually have data
        avg_gain_array = next(
            self.read(
                tags=[
                    DlnirspTag.intermediate_frame(),
                    DlnirspTag.task_avg_unrectified_solar_gain(),
                ],
                decoder=fits_array_decoder,
            )
        )

        rectified_array = next(
            self.corrections_remove_spec_geometry(
                arrays=avg_gain_array,
                shift_dict=shift_dict,
                scale_dict=scale_dict,
                reference_wavelength_axis=initial_ref_wave,
            )
        )

        # All slitbeams in a single stack
        stacked_slitbeams = np.vstack(
            np.split(rectified_array, self.constants.num_slits * self.constants.num_beams, axis=1)
        )

        if stacked_slitbeams.shape[1] != initial_ref_wave.size:
            raise ValueError("The rectified data are not composed of correctly stacked slitbeams.")

        non_nan_frac = np.sum(~np.isnan(stacked_slitbeams), axis=0) / stacked_slitbeams.shape[0]
        good_idx = np.where(non_nan_frac > self.parameters.geo_reference_wave_min_nonnan_frac)[0]

        reference_wavelength = initial_ref_wave[good_idx.min() : good_idx.max() + 1]

        return reference_wavelength

    def write_geometric_calibration(
        self,
        shift_dict: dict[int, np.ndarray],
        scale_dict: dict[int, np.ndarray],
        reference_wavelength_axis: np.ndarray,
    ) -> None:
        """
        Combine shifts and scales into a single dict and save to an ASDF file.

        ASDF is needed because each group may have different shapes.

        Also write the reference wavelength axis for use in other tasks.
        """
        tree = {
            "spectral_shifts": shift_dict,
            "spectral_scales": scale_dict,
            "reference_wavelength_axis": reference_wavelength_axis,
        }

        self.write(
            data=tree,
            tags=[DlnirspTag.intermediate(), DlnirspTag.task_geometric()],
            encoder=asdf_encoder,
        )

    def get_reference_spectrum(self, avg_gain_array: np.ndarray) -> tuple[np.ndarray, int]:
        """
        Compute the average spectrum that will be used as the reference wavelength scale.

        The spectrum is the median spectrum of the central group_id.
        """
        # TODO: Would it be possible to have the ref spec include both beams? (maybe not if the dispersion is different)
        slitbeams = list(self.group_id_slitbeam_group_dict.keys())
        middle_slitbeam = max(slitbeams) // 2
        central_group_id = int(np.nanmedian(self.group_id_slitbeam_group_dict[middle_slitbeam]))

        logger.info(f"Creating reference spectrum from group_id = {central_group_id}")
        group_data = self.group_id_get_data(data=avg_gain_array, group_id=central_group_id)

        median_spec = np.nanmedian(group_data, axis=0)

        return self.prep_spectrum_for_fit(median_spec), central_group_id

    def get_reference_dispersion(self, dispersion_array: np.ndarray) -> float:
        """
        Compute the reference dispersion (angstrom / px) to apply to all spectra.

        Dispersion values for each group are known a priori; this method returns the median dispersion value of the slit
        with the largest dispersion. The largest dispersion is used so we don't artificially create data that don't
        exist. I.e., we degrade all spectra to the worst dispersion.
        """
        slitbeam_group_mapping = self.group_id_slitbeam_group_dict

        slit_median_dispersions = []
        for slit in range(self.constants.num_slits):
            even_slitbeam = slit * 2
            odd_slitbeam = even_slitbeam + 1
            even_dispersions = [
                np.nanmedian(self.group_id_get_data(data=dispersion_array, group_id=g))
                for g in slitbeam_group_mapping[even_slitbeam]
            ]
            odd_dispersions = [
                np.nanmedian(self.group_id_get_data(data=dispersion_array, group_id=g))
                for g in slitbeam_group_mapping[odd_slitbeam]
            ]
            median_dispersion = np.nanmedian(np.r_[even_dispersions, odd_dispersions])
            slit_median_dispersions.append(median_dispersion)

        max_dispersion_slit = np.argmax(slit_median_dispersions)
        max_dispersion = np.max(slit_median_dispersions)

        logger.info(f"Reference dispersion = {max_dispersion} from slit {max_dispersion_slit}")
        return float(max_dispersion)

    def fit_single_shift(
        self, input_reference_spectrum: np.ndarray, input_target_spectrum: np.ndarray, scale: float
    ) -> float:
        """
        Compute the pixel shift needed to make a target spectrum match the reference spectrum.

        An initial guess of the shift is made via correlation. Then shift is refined with a simple chisq minimization.
        """
        ## Scipy minimize requires the spectra to be the same length, so just chop/extend the reference spectrum
        size_diff = input_target_spectrum.size - input_reference_spectrum.size
        if size_diff < 0:
            reference_spectrum = np.resize(input_reference_spectrum, input_target_spectrum.size)
            target_spectrum = input_target_spectrum
        elif size_diff > 0:
            target_spectrum = np.resize(input_target_spectrum, input_reference_spectrum.size)
            reference_spectrum = np.copy(input_reference_spectrum)
        else:
            target_spectrum = input_target_spectrum
            reference_spectrum = np.copy(input_reference_spectrum)

        initial_guess_shift = self.compute_initial_guess_shift(reference_spectrum, target_spectrum)

        ## Then refine shift with a chisq minimization
        shift = minimize(
            self.shift_chisq,
            np.array([float(initial_guess_shift)]),
            args=(
                reference_spectrum,
                target_spectrum,
                scale,
                self.corrections_shift_and_scale_spectrum,
            ),
            method="nelder-mead",
        ).x[0]

        # logger.info(f"{initial_guess_shift = } => {shift = }")

        return shift

    def compute_initial_guess_shift(
        self, reference_spectrum: np.ndarray, target_spectrum: np.ndarray
    ) -> float:
        """Make a rough, integer pixel guess of the shift between two spectra by identifying peaks in their cross-correlation."""
        target_signal = target_spectrum - np.nanmean(target_spectrum)
        target_signal[~np.isfinite(target_signal)] = np.nanmedian(
            target_signal[np.isfinite(target_signal)]
        )

        reference_signal = reference_spectrum - np.nanmean(reference_spectrum)
        reference_signal[~np.isfinite(reference_signal)] = np.nanmedian(
            reference_signal[np.isfinite(reference_signal)]
        )

        corr = np.correlate(
            target_signal,
            reference_signal,
            mode="same",
        )

        # Truncate the correlation to contain only allowable shifts
        max_shift = self.parameters.geo_max_shift_px
        mid_position = corr.size // 2

        # max and min here make sure we don't wrap around the array bounds
        start = max(0, int(mid_position - max_shift))
        stop = min(corr.size - 1, int(mid_position + max_shift + 1))
        truncated_corr = corr[start:stop]

        # This min_dist ensures we only find a single peak in each correlation signal
        pidx = peakutils.indexes(truncated_corr, min_dist=corr.size)

        # -1 because of how the interpolation shift function defines its shift
        initial_guess_shift = -1 * (pidx - truncated_corr.size // 2)

        # These edge-cases are very rare, but do happen sometimes
        if initial_guess_shift.size == 0:
            logger.info(f"No correlation peak found. Initial guess set to 0")
            initial_guess_shift = 0.0

        elif initial_guess_shift.size > 1:
            logger.info(
                f"More than one correlation peak found ({initial_guess_shift}). Initial guess set to mean ({np.nanmean(initial_guess_shift)})"
            )
            initial_guess_shift = np.nanmean(initial_guess_shift)

        return initial_guess_shift

    def fit_values_along_slitbeam(
        self,
        spatial_pixels: np.ndarray,
        values: np.ndarray,
        poly_fit_order: int,
    ) -> np.ndarray:
        """
        Fit a set of measurements along the spatial extent of a full slitbeam.

        The fit accounts for spatial locations that aren't illuminate (i.e., gaps are preserved) and helps control
        outlier measurements.

        Fitting is done with an iterative, sigma-clipping algorithm to further reject fit outliers.
        """
        logger.info(f"Fitting along slit with order {poly_fit_order} polynomial")
        good_idx = np.isfinite(values)

        poly_fitter = fitting.LinearLSQFitter()
        outlier_rejection_fitter = fitting.FittingWithOutlierRemoval(
            fitter=poly_fitter,
            outlier_func=sigma_clip,
            sigma=self.parameters.geo_slitbeam_fit_sig_clip,
            niter=10,
            cenfunc="median",
            stdfunc="std",
        )
        poly_model = polynomial.Polynomial1D(degree=poly_fit_order)

        fit_poly, _ = outlier_rejection_fitter(
            model=poly_model, x=spatial_pixels[good_idx], y=values[good_idx]
        )
        logger.info(f"Ran {outlier_rejection_fitter.fit_info['niter']} outlier iterations")
        fit_values = fit_poly(spatial_pixels)

        return fit_values

    def group_values_by_group_id(
        self, values: np.ndarray, group_ids: list[int]
    ) -> dict[int, np.ndarray]:
        """Group values into separate arrays for each group id.

        Grouping by group_id is important because it allows us to apply the geometric correction on a per-group basis.
        """
        group_value_dict = dict()
        fit_idx = 0
        for group_id in group_ids:
            group_spatial_px = np.unique(self.group_id_get_idx(group_id=group_id)[0])
            group_array = np.zeros(group_spatial_px.size)
            for j, _ in enumerate(group_spatial_px):
                # This loop is where we assume that the order of values exactly matches the spatial ordering of all
                # groups in a single slitbeam. This is a good assumption, but if it ever breaks down then we'll need a
                # `np.where` call here.
                group_array[j] = values[fit_idx]
                fit_idx += 1

            group_value_dict[group_id] = group_array

        if fit_idx != values.size:
            raise ValueError("Did not assign all values to a group. This should never happen.")

        return group_value_dict

    def prep_spectrum_for_fit(self, spectrum: np.ndarray) -> np.ndarray:
        """
        Prepare a spectrum to be fit by normalizing its amplitude and subtracting the continuum.

        The continuum is estimated by smoothing out the lines with a Gaussian kernel.
        """
        edge_trim = self.parameters.geo_spectral_edge_trim
        cut_spectrum = spectrum[edge_trim:-edge_trim]
        cleaned_spectrum = self.clean_bad_px(cut_spectrum)
        normed_spec = cleaned_spectrum / np.nanmedian(cleaned_spectrum)
        normed_spec[~np.isfinite(normed_spec)] = np.nanmedian(normed_spec)

        smoothed_spec = normed_spec / spnd.gaussian_filter1d(
            normed_spec, sigma=self.parameters.geo_continuum_smoothing_sigma_px
        )

        return smoothed_spec

    def clean_bad_px(self, spectrum: np.ndarray) -> np.ndarray:
        """Replace deviant pixels with a local median."""
        filtered = spnd.median_filter(
            spectrum.astype(float), 5, mode="constant", cval=np.nanmedian(spectrum)
        )
        diff = filtered - spectrum
        bad_idx = np.where(
            np.abs(diff) > self.parameters.geo_bad_px_sigma_threshold * np.nanstd(diff)
        )
        spectrum[bad_idx] = filtered[bad_idx]

        return spectrum

    @staticmethod
    def shift_chisq(
        par: np.ndarray,
        ref_spec: np.ndarray,
        spec: np.ndarray,
        scale: float,
        shift_scale_func: Callable,
    ) -> float:
        """
        Goodness of fit calculation for a simple shift.

        Only the shift is fit, but the scale/dispersion is needed to ensure the shift is computed with the correct
        dispersion.

        Uses chisq as goodness of fit.

        Parameters
        ----------
        par : np.ndarray
            Spectral shift being optimized

        ref_spec : np.ndarray
            Reference spectra (from first modstate)

        spec : np.ndarray
            Spectra being fitted

        scale
            The relative dispersion to apply to the raw spectrum prior to fitting for the shift.

        Returns
        -------
        float
            Sum of chisquared
        """
        shift = par
        new_spec = shift_scale_func(spectrum=spec, shift=shift, scale=scale)
        chisq = np.nansum(np.abs((ref_spec - new_spec) ** 2 / ref_spec))
        return chisq
