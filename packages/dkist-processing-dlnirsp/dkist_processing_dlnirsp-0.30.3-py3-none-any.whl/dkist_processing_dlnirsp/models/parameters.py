"""Machinery to access pipeline parameters served in input dataset document."""

from datetime import datetime
from functools import cached_property

import astropy.units as u
import numpy as np
from dkist_processing_common.models.parameters import ParameterArmIdMixin
from dkist_processing_common.models.parameters import ParameterBase
from solar_wavelength_calibration import DownloadConfig


class DlnirspParsingParameters(ParameterBase):
    """
    Parameters specifically (and only) for the Parse task.

    Needed because the Parse task doesn't know what the wavelength is yet and therefore can't use the
    `ParameterWaveLengthMixin`.
    """

    @property
    def max_cs_step_time_sec(self) -> float:
        """Time window within which CS steps with identical GOS configurations are considered to be the same."""
        return self._find_most_recent_past_value(
            "dlnirsp_max_cs_step_time_sec", start_date=datetime.now()
        )

    @property
    def wcs_crpix_correction_method(self) -> str:
        """
        Define the method used to correct the CRPIX1 and CRPIX2 header values in L1 science headers.

        The specified method must exist in `~dkist_processing_dlnirsp.tasks.science.ScienceCalibration.apply_WCS_corrections`.
        """
        return self._find_most_recent_past_value("dlnirsp_wcs_crpix_correction_method")

    @property
    def parse_bin_crpix_to_multiple_of(self) -> int:
        """
        Return the pixel amount to bin CRPIX values by when parsing the mosaic organization.

        For example, if this value is `5` then the CRPIX values will be rounded/binned to the nearest multiple of 5.
        """
        return self._find_most_recent_past_value("dlnirsp_parse_bin_crpix_to_multiple_of")


class DlnirspParameters(ParameterBase, ParameterArmIdMixin):
    """Put all DLNIRSP parameters parsed from the input dataset document in a single property."""

    @cached_property
    def linearization_poly_coeffs(self) -> np.ndarray:
        """
        Return a set of polynomial coefficients used to correct the raw values in each individual ramp frame.

        Coefficients should be in decreasing polynomial degree, to be compatible with `np.poly1d`.
        """
        list_coeffs = self._find_parameter_for_arm("dlnirsp_linearization_poly_coeffs")
        return np.array(list_coeffs)

    @cached_property
    def linearization_saturation_threshold(self) -> float:
        """Return the raw (i.e., unlinearized) value above which a pixel is considered "bad"."""
        return self._find_parameter_for_arm("dlnirsp_linearization_saturation_threshold")

    @cached_property
    def raw_group_id_array(self) -> np.ndarray:
        """
        Return an array containing 'group ids' of each array pixel.

        The group id labels each IFU ribbon/mirror slice.

        NOTE: This array has NOT been corrected for IFU drift. See `GroupIdMixin.group_id_drifted_id_array` for that.
        """
        param_obj = self._find_parameter_for_arm("dlnirsp_group_id_file")
        return self._load_param_value_from_fits(param_obj)

    @cached_property
    def raw_dispersion_array(self) -> np.ndarray:
        """
        Return an array that provides the dispersion (in Angstrom / px) for each group.

        NOTE: This array has NOT been corrected for IFU drift. Use the intermediate frame
        `DlnirspTag.task_drifted_dispersion()` for that.
        """
        param_obj = self._find_parameter_for_arm("dlnirsp_geo_dispersion_file")
        return self._load_param_value_from_fits(param_obj)

    @property
    def raw_ifu_x_pos_array(self) -> np.ndarray:
        """
        Return the array mapping raw pixel position to an X coordinate in the IFU.

        NOTE: This array has NOT been corrected for IFU drift. Use the intermediate frame
        `DlnirspTag.task_drifted_ifu_x_pos()` for that.
        """
        param_obj = self._find_parameter_for_arm("dlnirsp_ifu_x_pos_file")
        return self._load_param_value_from_fits(param_obj)

    @property
    def raw_ifu_y_pos_array(self) -> np.ndarray:
        """
        Return the array mapping raw pixel position to an X coordinate in the IFU.

        NOTE: This array has NOT been corrected for IFU drift. Use the intermediate frame
        `DlnirspTag.task_drifted_ifu_y_pos()` for that.
        """
        param_obj = self._find_parameter_for_arm("dlnirsp_ifu_y_pos_file")
        return self._load_param_value_from_fits(param_obj)

    @property
    def static_bad_pixel_map(self) -> np.ndarray:
        """Return a binary array where 1 corresponds to the locations of known bad pixels."""
        param_obj = self._find_parameter_for_arm("dlnirsp_static_bad_pixel_map")
        return self._load_param_value_from_fits(param_obj)

    @property
    def bad_pixel_gain_median_smooth_size(self) -> tuple[int, int]:
        """
        Define the size of the median window used when smoothing lamp gain data to identify bad pixels.

        The two numbers correspond to [spatial_px, spectral_px]
        """
        return self._find_most_recent_past_value("dlnirsp_bad_pixel_gain_median_smooth_size")

    @property
    def bad_pixel_dark_median_smooth_size(self) -> tuple[int, int]:
        """
        Define the size of the median window used when smoothing dark sigma data to identify bad pixels.

        The two numbers correspond to [spatial_px, spectral_px]
        """
        return self._find_most_recent_past_value("dlnirsp_bad_pixel_dark_median_smooth_size")

    @property
    def bad_pixel_gain_sigma_threshold(self) -> float:
        """
        Define the stddev threshold used to identify bad pixels from lamp gain array.

        A pixel is "bad" if its value in difference between smoothed and raw arrays is deviant by this number of standard
        deviations.
        """
        return self._find_most_recent_past_value("dlnirsp_bad_pixel_gain_sigma_threshold")

    @property
    def bad_pixel_dark_sigma_threshold(self) -> float:
        """
        Define the stddev threshold used to identify bad pixels from dark sigma array.

        A pixel is "bad" if its value in difference between smoothed and raw arrays is deviant by this number of standard
        deviations.
        """
        return self._find_most_recent_past_value("dlnirsp_bad_pixel_dark_sigma_threshold")

    @property
    def group_id_max_drift_px(self) -> int:
        """
        Define the maximum pixel shift allowed when computing group ID drift.

        If the computed drift is larger than this then the raw group ID array will be used.
        """
        return self._find_most_recent_past_value("dlnirsp_group_id_max_drift_px")

    @property
    def group_id_rough_slit_separation_px(self) -> float:
        """
        Rough pixel distance between slits.

        This is NOT the pixel distance between both beams of the same slit.
        """
        return self._find_most_recent_past_value("dlnirsp_group_id_rough_slit_separation_px")

    @property
    def corrections_max_nan_frac(self) -> float:
        """
        Maximum allowable fraction of NaN in a shifted pixel before that pixel gets converted to NaN.

        Input NaN values are tracked and any shifted pixel that has a value made up of more than this fraction of NaN
        pixels will be set to NaN.
        """
        return self._find_most_recent_past_value("dlnirsp_corrections_max_nan_frac")

    @property
    def pac_remove_linear_I_trend(self) -> bool:
        """Flag that determines if a linear intensity trend is removed from the whole PolCal CS.

        The trend is fit using the average flux in the starting and ending clear steps.
        """
        return self._find_most_recent_past_value("dlnirsp_pac_remove_linear_I_trend")

    @property
    def pac_fit_mode(self) -> str:
        """Name of set of fitting flags to use during PAC Calibration Unit parameter fits."""
        return self._find_most_recent_past_value("dlnirsp_pac_fit_mode")

    @property
    def lamp_despike_kernel(self) -> (float, float):
        """Return the (x, y) stddev of the Gaussian kernel used for lamp despiking."""
        return self._find_most_recent_past_value("dlnirsp_lamp_despike_kernel")

    @property
    def lamp_despike_threshold(self) -> float:
        """Return the threhold value used to identify spikes in lamp gains."""
        return self._find_most_recent_past_value("dlnirsp_lamp_despike_threshold")

    @property
    def geo_spectral_edge_trim(self) -> int:
        """Return the +/- number of pixels to remove from the ends of all spectra prior to fitting."""
        return self._find_most_recent_past_value("dlnirsp_geo_spectral_edge_trim")

    @property
    def geo_continuum_smoothing_sigma_px(self) -> float:
        """
        Return the Gaussian sigma used to smooth out spectral lines when estimating the continuum background.

        This should be roughly the width, in px, of typical spectral lines. Err on the side of too large.
        """
        return self._find_most_recent_past_value("dlnirsp_geo_continuum_smoothing_sigma_px")

    @property
    def geo_max_shift_px(self) -> float:
        """
        Return the maximum shift to consider when computing spectral curvature.

        This is an absolute value: negative and positive shifts are constrained to the same magnitude.
        """
        return self._find_most_recent_past_value("dlnirsp_geo_max_shift_px")

    @property
    def geo_shift_poly_fit_order(self) -> int:
        """Return the order of the polynomial used to fit spectral shifts as a function of slit position."""
        return self._find_most_recent_past_value("dlnirsp_geo_shift_poly_fit_order")

    @property
    def geo_bad_px_sigma_threshold(self) -> float:
        """Any pixels larger than this many stddevs from a difference between a filtered and raw spectrum will be removed."""
        return self._find_most_recent_past_value("dlnirsp_geo_bad_px_sigma_threshold")

    @property
    def geo_slitbeam_fit_sig_clip(self) -> int:
        """Plus/minus number of standard deviations away from the median used to reject outlier values when fitting along the slitbeams."""
        return self._find_most_recent_past_value("dlnirsp_geo_slitbeam_fit_sig_clip")

    @property
    def geo_reference_wave_min_nonnan_frac(self) -> float:
        """
        Minimum fraction of non-NaN values allowed in reference wavelength regions.

        Wavelength regions with less than this fraction of non-NaN pixels (across all slitbeams) will be excluded from
        the reference wavelength vector.
        """
        return self._find_most_recent_past_value("dlnirsp_geo_reference_wave_min_nonnan_frac")

    @property
    def wavecal_atlas_download_config(self) -> DownloadConfig:
        """Define the `~solar_wavelength_calibration.DownloadConfig` used to grab the Solar atlas used for wavelength calibration."""
        config_dict = self._find_most_recent_past_value("dlnirsp_wavecal_atlas_download_config")
        return DownloadConfig.model_validate(config_dict)

    @property
    def wavecal_grating_zero_point_angle_offset_deg(self) -> u.Quantity:
        """Define the zero-point offset for the grating angle header key."""
        return (
            self._find_most_recent_past_value("dlnirsp_wavecal_grating_zero_point_angle_offset_deg")
            * u.deg
        )

    @property
    def wavecal_spectral_camera_focal_length_mm(self) -> u.Quantity:
        """Define the camera focal length."""
        return (
            self._find_most_recent_past_value("dlnirsp_wavecal_spectral_camera_focal_length_mm")
            * u.mm
        )

    @property
    def wavecal_center_axis_position_mm(self) -> u.Quantity:
        """Define the center offset value for the arm linear stage position."""
        return self._find_parameter_for_arm("dlnirsp_wavecal_center_axis_position_mm") * u.mm

    @property
    def wavecal_center_axis_littrow_angle_deg(self) -> u.Quantity:
        """Define the littrow angle at the central axis position."""
        return self._find_parameter_for_arm("dlnirsp_wavecal_center_axis_littrow_angle_deg") * u.deg

    @property
    def wavecal_resolving_power(self) -> float:
        """Define the resolving power of the current spectrograph setup."""
        return self._find_parameter_for_arm("dlnirsp_wavecal_resolving_power")

    @property
    def wavecal_telluric_opacity_factor_initial_guess(self) -> float:
        """Define the initial guess for the telluric opacity factor when computing a wavelength solution."""
        return self._find_most_recent_past_value(
            "dlnirsp_wavecal_telluric_opacity_factor_initial_guess"
        )

    @property
    def solar_characteristic_spectra_normalization_percentage(self) -> float:
        """
        Define the CDF percentage value used when applying global normalization to the final characteristic solar spectra.

        This value is passed directly to `np.nanpercentile`. The correct value depends on the ratio of continuum to line
        pixels in the solar spectrum and different arms will use different values.

        Getting this value *exactly* right is not critical because it only affects a global scaling that determines how
        accurately the units in L1 science data are "relative to solar signal at disk center", which is already a
        not-very-precise statement.
        """
        return self._find_parameter_for_arm(
            "dlnirsp_solar_characteristic_spectra_normalization_percentage"
        )

    @property
    def polcal_demodulation_spatial_poly_fit_order(self) -> int:
        """Return the order of the polynomial used to fit demodulation matrices as a function of IFU group spatial pixel."""
        return self._find_most_recent_past_value(
            "dlnirsp_polcal_demodulation_spatial_poly_fit_order"
        )

    @property
    def polcal_demodulation_fit_sig_clip(self) -> float:
        """Plus/minus number of standard deviations away from the median used to reject outlier values when fitting demodulation matrices along spatial pixels."""
        return self._find_most_recent_past_value("dlnirsp_polcal_demodulation_fit_sig_clip")

    @property
    def polcal_demodulation_fit_max_niter(self) -> int:
        """Maximum number of sigclip rejection steps when fitting demodulation matrices along spatial axis."""
        return self._find_most_recent_past_value("dlnirsp_polcal_demodulation_fit_max_niter")

    @property
    def polcal_metrics_num_sample_points(self) -> int:
        """Define number of points to sub-sample from all spatial pixels when saving polcal metrics."""
        return self._find_most_recent_past_value("dlnirsp_polcal_metrics_num_sample_points")

    @property
    def bad_pixel_correction_interpolation_kernel_shape(self) -> tuple[int, int]:
        """
        Define the 2D box kernel size used to interpolate over bad pixels in science data.

        The kernel used will be `np.ones(shape)` normalized to a sum of 1.
        """
        return self._find_most_recent_past_value(
            "dlnirsp_bad_pixel_correction_interpolation_kernel_shape"
        )

    @property
    def wcs_pc_correction_matrix(self) -> np.ndarray:
        """Define the matrix used to correct the PCi_j matrix in L1 science headers."""
        return np.array(self._find_most_recent_past_value("dlnirsp_wcs_pc_correction_matrix"))

    @property
    def wcs_crpix_correction_method(self) -> str:
        """
        Define the method used to correct the CRPIX1 and CRPIX2 header values in L1 science headers.

        The specified method must exist in `~dkist_processing_dlnirsp.tasks.science.ScienceCalibration.apply_WCS_corrections`.
        """
        return self._find_most_recent_past_value("dlnirsp_wcs_crpix_correction_method")
