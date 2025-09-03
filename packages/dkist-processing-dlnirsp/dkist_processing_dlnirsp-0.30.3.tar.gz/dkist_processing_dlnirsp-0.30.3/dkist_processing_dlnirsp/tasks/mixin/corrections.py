"""Mixin for array corrections that are more complicated than simple arithmetic."""

from typing import Generator
from typing import Iterable

import numpy as np
import scipy.interpolate as spi


class CorrectionsMixin:
    """Mixin to provide support for array corrections more complicated than simple arithmetic."""

    def corrections_remove_spec_geometry(
        self,
        arrays: Iterable[np.ndarray] | np.ndarray,
        shift_dict: dict[int, np.ndarray],
        scale_dict: dict[int, np.ndarray],
        reference_wavelength_axis: np.ndarray,
        handle_nans: bool = True,
    ) -> Generator[np.ndarray, None, None]:
        """
        Remove measured spectral shifts and resample all spatial positions to the same wavelength axis.

        The reference wavelength axis is computed during the GeometricCalibration task.
        """
        arrays = [arrays] if isinstance(arrays, np.ndarray) else arrays
        max_nan_frac = self.parameters.corrections_max_nan_frac

        for array in arrays:
            slitbeam_list = []
            for slitbeam, group_ids in self.group_id_slitbeam_group_dict.items():
                slitbeam_array = np.zeros((array.shape[0], reference_wavelength_axis.size)) * np.nan
                for group_id in group_ids:
                    group_data, group_idx = self.group_id_get_data_and_idx(
                        data=array, group_id=group_id
                    )
                    group_spatial_px = np.unique(group_idx[0])

                    for i, spatial_px in enumerate(group_spatial_px):
                        spectrum = group_data[i, :]
                        shift = shift_dict[group_id][i]
                        scale = scale_dict[group_id][i]
                        corrected_spectrum = self.corrections_shift_and_scale_spectrum(
                            spectrum=spectrum,
                            shift=shift,
                            scale=scale,
                            output_wave_axis=reference_wavelength_axis,
                            handle_nans=handle_nans,
                            max_nan_frac=max_nan_frac,
                        )

                        slitbeam_array[spatial_px, :] = corrected_spectrum

                slitbeam_list.append(slitbeam_array)

            array_output = np.hstack(slitbeam_list)
            yield array_output

    def corrections_apply_spec_geometry(
        self,
        arrays: Iterable[np.ndarray] | np.ndarray,
        shift_dict: dict[int, np.ndarray],
        scale_dict: dict[int, np.ndarray],
        reference_wavelength_axis: np.ndarray,
        handle_nans: bool = True,
    ) -> Generator[np.ndarray, None, None]:
        """
        Apply measured shifts and dispersions to an array.

        In other words, reapply optical spectral distortions to an array.
        """
        arrays = [arrays] if isinstance(arrays, np.ndarray) else arrays
        max_nan_frac = self.parameters.corrections_max_nan_frac

        group_ids = shift_dict.keys()
        for array in arrays:
            output_array = np.zeros_like(self.group_id_drifted_id_array) * np.nan
            for group_id in group_ids:
                rectified_idx = self.group_id_get_idx(group_id=group_id, rectified=True)
                rectified_slices = self.group_id_convert_idx_to_2d_slice(rectified_idx)
                group_data = array[rectified_slices]

                OG_idx = self.group_id_get_idx(group_id=group_id, rectified=False)
                OG_spectral_slice = self.group_id_convert_idx_to_2d_slice(OG_idx)[1]
                OG_wave_axis = np.arange(OG_spectral_slice.stop - OG_spectral_slice.start)

                group_spatial_px = np.unique(rectified_idx[0])

                for i, spatial_px in enumerate(group_spatial_px):
                    spectrum = group_data[i, :]
                    shift = -1 * shift_dict[group_id][i] / scale_dict[group_id][i]
                    scale = 1.0 / scale_dict[group_id][i]
                    corrected_spectrum = self.corrections_shift_and_scale_spectrum(
                        spectrum=spectrum,
                        shift=shift,
                        scale=scale,
                        input_wave_axis=reference_wavelength_axis,
                        output_wave_axis=OG_wave_axis,
                        handle_nans=handle_nans,
                        max_nan_frac=max_nan_frac,
                    )

                    output_array[spatial_px, OG_spectral_slice] = corrected_spectrum

            yield output_array

    @staticmethod
    def corrections_shift_and_scale_spectrum(
        spectrum: np.ndarray,
        shift: float,
        scale: float,
        input_wave_axis: np.ndarray | None = None,
        output_wave_axis: np.ndarray | None = None,
        handle_nans: bool = False,
        max_nan_frac: float = 0.03,
        extrapolate: bool = False,
    ) -> np.ndarray:
        """
        Apply a shift and scale (stretch) to an input vector.

        If `handle_nans` is `True` then any non-finte values are monitored during the shift. Any pixels in the shifted
        output that contain more than `max_nan_frac` of an input NaN pixel are set to NaN. This option should probably
        be left to `False` when using this function for fitting.

        `input_wave_axis` and `reference_wave_axis` define the input and output wavelength axis values. If not set then
        the spectrum is simply shifted and scaled onto its own grid (i.e., `np.arange(spectrum.size)`).
        """
        if input_wave_axis is None:
            input_wave_axis = np.arange(spectrum.size)

        if output_wave_axis is None:
            output_wave_axis = np.arange(spectrum.size)

        nan_idx = ~np.isfinite(spectrum)
        nan_frac = np.sum(nan_idx) / spectrum.size
        if nan_frac == 1:
            # If the whole spectrum is trash just return it with the correct size
            return np.resize(spectrum, output_wave_axis.size)

        if handle_nans:
            nan_locations = np.zeros_like(spectrum)
            nan_locations[nan_idx] = 1.0
            # Slice to only the finite values because nanmedian can return +/- infinity
            spectrum[nan_idx] = np.nanmedian(spectrum[~nan_idx])

        spec_wave_axis = input_wave_axis * scale + shift
        spline_func = spi.CubicSpline(spec_wave_axis, spectrum, extrapolate=extrapolate)
        shifted_spec = spline_func(output_wave_axis)

        if handle_nans:
            nan_spline_func = spi.CubicSpline(
                spec_wave_axis, nan_locations, extrapolate=extrapolate
            )
            shifted_nan_locs = nan_spline_func(output_wave_axis)
            nan_bleed = np.where(shifted_nan_locs > max_nan_frac)
            shifted_spec[nan_bleed] = np.nan

        return shifted_spec
