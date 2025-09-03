"""DL wavelength calibration task. See :doc:`this page </wavelength_calibration>` for more information."""

import astropy.units as u
import numpy as np
from astropy.convolution import convolve_fft
from astropy.convolution import interpolate_replace_nans
from astropy.coordinates import EarthLocation
from astropy.time import Time
from astropy.units import Quantity
from astropy.wcs import WCS
from dkist_processing_common.codecs.asdf import asdf_decoder
from dkist_processing_common.codecs.asdf import asdf_encoder
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.json import json_decoder
from dkist_processing_common.codecs.json import json_encoder
from dkist_processing_common.models.dkist_location import location_of_dkist
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_service_configuration.logging import logger
from solar_wavelength_calibration import Atlas
from solar_wavelength_calibration import DispersionBoundRange
from solar_wavelength_calibration import UnitlessBoundRange
from solar_wavelength_calibration import WavelengthCalibrationFitter
from solar_wavelength_calibration.fitter.parameters import BoundsModel
from solar_wavelength_calibration.fitter.parameters import FitFlagsModel
from solar_wavelength_calibration.fitter.parameters import LengthBoundRange
from solar_wavelength_calibration.fitter.parameters import WavelengthCalibrationParameters
from solar_wavelength_calibration.fitter.wavelength_fitter import FitResult
from solar_wavelength_calibration.fitter.wavelength_fitter import WavelengthParameters
from solar_wavelength_calibration.fitter.wavelength_fitter import calculate_initial_crval_guess
from sunpy.coordinates import HeliocentricInertial

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks.dlnirsp_base import DlnirspTaskBase

__all__ = ["WavelengthCalibration"]

from dkist_processing_dlnirsp.tasks.mixin.corrections import CorrectionsMixin


class WavelengthCalibration(DlnirspTaskBase, CorrectionsMixin, QualityMixin):
    """Task class for computing a header wavelength solution.

    The wavelength solution is encoded into FITS headers with the formalism of
    `Greisen et al (2006) <https://ui.adsabs.harvard.edu/abs/2006A%26A...446..747G/abstract>`_ (see Table 6).

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
        Compute and save a header wavelength solution.

        The steps are:

        #. Generate an initial-guess wavelength solution from the L0 headers
        #. Compute a representative solar spectrum by looking at the central group of an average solar gain frame
        #. Fit the input spectrum to a solar atlas with the
           `solar-wavelength-calibration <https://docs.dkist.nso.edu/projects/solar-wavelength-calibration/en/latest/>`_
           library
        #. Encode the fit results into their corresponding header values.
        #. Write the updated header wavelength solution and fit metrics.

        Returns
        -------
        None
        """
        with self.apm_processing_step("Compute input spectrum and wavelength"):
            dispersion = (
                next(
                    self.read(
                        tags=[DlnirspTag.intermediate(), DlnirspTag.task_dispersion()],
                        decoder=json_decoder,
                    )
                )
                # fmt: off
                    * u.angstrom / u.pix
                # fmt: on
            )
            logger.info(f"Loaded dispersion computed in geometric task: {dispersion}")

            logger.info("Computing representative input spectrum")
            representative_spectrum = self.get_representative_spectrum()
            input_spectrum, nan_chop_amount = self.chop_and_clean_NaNs(representative_spectrum)

            incident_light_angle = (
                self.parameters.wavecal_grating_zero_point_angle_offset_deg
                - self.constants.grating_position_deg
            )
            header_wavelength = self.constants.wavelength * u.nm
            spectral_order = self.compute_spectral_order(
                crval=header_wavelength, incident_light_angle=incident_light_angle
            )

            logger.info(f"{incident_light_angle = !s}")
            logger.info(f"{header_wavelength = !s}")
            logger.info(f"{spectral_order = }")

            logger.info("Computing initial guess wavelength vector")
            input_wavelength_vector = self.compute_input_wavelength_vector(
                spectrum=input_spectrum,
                wavelength=header_wavelength,
                dispersion=dispersion,
                grating_constant=self.constants.grating_constant_inverse_mm,
                order=spectral_order,
                incident_light_angle=incident_light_angle,
            )

        with self.apm_processing_step("Compute brute-force CRVAL initial guess"):
            atlas = Atlas(config=self.parameters.wavecal_atlas_download_config)
            wavelength_range = input_wavelength_vector.max() - input_wavelength_vector.min()
            crval_init = calculate_initial_crval_guess(
                input_wavelength_vector=input_wavelength_vector,
                input_spectrum=input_spectrum,
                atlas=atlas,
                negative_limit=-wavelength_range / 2,
                positive_limit=wavelength_range / 2,
                num_steps=500,
            )
            logger.info(f"{crval_init = !s}")

        doppler_velocity = self.compute_doppler_velocity()
        logger.info(f"{doppler_velocity = !s}")

        with self.apm_task_step("Set up wavelength fit"):
            bounds = BoundsModel(
                # This is basically saying "we think the correct CRVAL is *somewhere* in our input vector"
                #  and lines up with the range of values considered when computing the brute-force initial guess above
                crval=LengthBoundRange(
                    min=np.min(input_wavelength_vector), max=np.max(input_wavelength_vector)
                ),
                # We think our input dispersion is pretty darn good, but let's let it move just a tiny bit
                dispersion=DispersionBoundRange(min=dispersion * 0.99, max=dispersion * 1.03),
                continuum_level=UnitlessBoundRange(min=0.5, max=2.0),
                opacity_factor=UnitlessBoundRange(min=0.3, max=5.0),
                # Even though straylight fraction is fixed in the fit, we set some finite bounds so we can use
                # differential evolution if we want
                straylight_fraction=UnitlessBoundRange(min=0.0, max=0.1),
            )

            fit_flags = FitFlagsModel(
                crval=True,
                dispersion=True,
                incident_light_angle=False,
                resolving_power=False,
                opacity_factor=True,
                straylight_fraction=False,
                continuum_level=True,
            )

            input_parameters = WavelengthCalibrationParameters(
                crval=crval_init,
                dispersion=dispersion,
                incident_light_angle=incident_light_angle,
                resolving_power=self.parameters.wavecal_resolving_power,
                opacity_factor=self.parameters.wavecal_telluric_opacity_factor_initial_guess,
                straylight_fraction=0.0,
                grating_constant=self.constants.grating_constant_inverse_mm,
                doppler_velocity=doppler_velocity,
                order=spectral_order,
                bounds=bounds,
                fit_flags=fit_flags,
            )

            fitter = WavelengthCalibrationFitter(
                input_parameters=input_parameters,
                atlas=atlas,
            )
            logger.info(f"Input parameters: {input_parameters.lmfit_parameters.pretty_repr()}")

        with self.apm_processing_step("Run wavelength solution fit"):
            fit_result = fitter(
                input_wavelength_vector=input_wavelength_vector,
                input_spectrum=input_spectrum,
                method="leastsq",
            )

        with self.apm_writing_step("Save wavelength solution and quality metrics"):
            self.write_fit_results(fit_result, nan_chop_amount)
            self.quality_store_wavecal_results(
                input_wavelength=input_wavelength_vector,
                input_spectrum=input_spectrum,
                fit_result=fit_result,
            )

    def get_representative_spectrum(self) -> np.ndarray:
        """
        Compute a representative Solar spectrum that will be used to calibrate the wavelength axis.

        The spectrum is computed as the spatial average of all spectra in the median group (a group near the center of
        the detector FOV). Spectra are taken from data that have geometric corrections applied (i.e., are on a relative
        wavelength grid common across all spectra).

        The average spectrum is also normalized to have a continuum level close to 1. This allows us to have a narrower
        bounds range on the `continuum_level` fit parameter.
        """
        logger.info("Reading average solar gain array")
        avg_solar_gain = next(
            self.read(
                tags=[
                    DlnirspTag.intermediate_frame(),
                    DlnirspTag.task_avg_unrectified_solar_gain(),
                ],
                decoder=fits_array_decoder,
            )
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
        rectified_solar_gain = next(
            self.corrections_remove_spec_geometry(
                arrays=avg_solar_gain,
                shift_dict=shifts,
                scale_dict=scales,
                reference_wavelength_axis=reference_wavelength_axis,
                handle_nans=True,
            )
        )

        slitbeams = list(self.group_id_slitbeam_group_dict.keys())
        middle_slitbeam = max(slitbeams) // 2
        central_group_id = int(np.nanmedian(self.group_id_slitbeam_group_dict[middle_slitbeam]))

        logger.info(f"Creating reference spectrum from group_id = {central_group_id}")
        group_data = self.group_id_get_data(data=rectified_solar_gain, group_id=central_group_id)

        representative_spectrum = np.nanmedian(group_data, axis=0)

        normalized_spectrum = representative_spectrum / np.nanpercentile(
            representative_spectrum,
            self.parameters.solar_characteristic_spectra_normalization_percentage,
        )

        return normalized_spectrum

    def compute_spectral_order(self, crval: Quantity, incident_light_angle: Quantity) -> int:
        r"""
        Compute the spectral order given the current spectrograph configuration.

        The spectral order :math:`m` is

        .. math::
            m = \frac{\sin\alpha + \sin\beta}{\sigma\lambda}

        where :math:`\sigma` is the grating constant (lines per mm), :math:`\alpha` is the incident light angle,
        :math:`\beta` is the diffracted light angle, and :math:`\lambda` is the wavelength. The grating constant, incident
        light angle, and wavelength come from L0 input headers while the diffracted light angles is computed as

        .. math::
            \beta = \alpha - \theta_L

        given :math:`\theta_L`, the littrow angle,

        .. math::
            \theta_L = \tan^{-1}\left(\frac{d}{f}\right),

        where :math:`d` is the linear translation of the camera from the center axis and :math:`f` is the camera focal
        length.
        """
        linear_translation_from_center = (
            self.parameters.wavecal_center_axis_position_mm - self.constants.arm_position_mm
        )
        littrow_angle = (
            np.arctan2(
                linear_translation_from_center,
                self.parameters.wavecal_spectral_camera_focal_length_mm,
            )
            + self.parameters.wavecal_center_axis_littrow_angle_deg
        )
        diffracted_light_angle = incident_light_angle - littrow_angle

        logger.info(f"{linear_translation_from_center = !s}")
        logger.info(f"littrow_angle = {littrow_angle.to(u.deg)}")
        logger.info(f"{diffracted_light_angle = !s}")

        order = (np.sin(incident_light_angle) + np.sin(diffracted_light_angle)) / (
            self.constants.grating_constant_inverse_mm * crval
        )

        return int(order)

    def write_fit_results(self, fit_result: FitResult, nan_chop_amount: int) -> None:
        """
        Save the fit results to disk to later be used to update the l1 headers.

        Here we also update the fit value of CRPIX to account for the fact that we may have chopped some NaN pixels
        away from the start of the data array prior to passing it to the wavecal fitter.
        """
        solution_header = fit_result.wavelength_parameters.to_header(axis_num=3)
        solution_header["CRPIX3"] += nan_chop_amount
        self.write(
            data=solution_header,
            tags=[DlnirspTag.task_wavelength_solution(), DlnirspTag.intermediate()],
            encoder=json_encoder,
        )

    def compute_input_wavelength_vector(
        self,
        *,
        spectrum: np.ndarray,
        wavelength: Quantity,
        dispersion: Quantity,
        grating_constant: Quantity,
        order: int,
        incident_light_angle: Quantity,
    ) -> Quantity:
        """Generate an initial-guess wavelength vector based on init values of wavelength fitting parameters."""
        num_wave_pix = spectrum.size
        wavelength_parameters = WavelengthParameters(
            crpix=num_wave_pix // 2 + 1,
            crval=wavelength.to_value(u.nm),
            dispersion=dispersion.to_value(u.nm / u.pix),
            grating_constant=grating_constant.to_value(1 / u.m),
            order=order,
            incident_light_angle=incident_light_angle.to_value(u.deg),
            cunit="nm",
        )
        header = wavelength_parameters.to_header(axis_num=1)
        wcs = WCS(header)
        input_wavelength_vector = wcs.spectral.pixel_to_world(np.arange(num_wave_pix)).to(u.nm)

        return input_wavelength_vector

    def chop_and_clean_NaNs(self, spectrum: np.ndarray) -> tuple[np.ndarray, int]:
        """
        Chop contiguous regions of NaN from either end of an array and interpolate over interior NaN values.

        Returns
        -------
        np.ndarray
            The input array with NaN's removed

        int
            The number of pixels chopped from the start of the array. This is needed to correctly adjust CRPIX later.
        """
        starting_non_nan_idx = 0
        while np.isnan(spectrum[starting_non_nan_idx]):
            starting_non_nan_idx += 1

        ending_non_nan_idx = spectrum.size - 1
        while np.isnan(spectrum[ending_non_nan_idx]):
            ending_non_nan_idx -= 1

        logger.info(
            f"Chopping NaN values from end of spectrum with slice [{starting_non_nan_idx}:{ending_non_nan_idx + 1}]"
        )
        chopped_spectrum = spectrum[starting_non_nan_idx : ending_non_nan_idx + 1]

        if np.sum(np.isnan(chopped_spectrum)) == 0:
            return chopped_spectrum, starting_non_nan_idx

        logger.info("Interpolating over internal NaN values.")
        # Grab only the spectral dimension of the bad pixel interpolation kernel
        kernel = np.ones(self.parameters.bad_pixel_correction_interpolation_kernel_shape[1])
        interpolated_spectrum = interpolate_replace_nans(
            chopped_spectrum,
            kernel=kernel,
            convolve=convolve_fft,
        )
        return interpolated_spectrum, starting_non_nan_idx

    def compute_doppler_velocity(self) -> u.Quantity:
        """Find the speed at which DKIST is moving relative to the Sun's center.

        Positive values refer to when DKIST is moving away from the sun.
        """
        coord = location_of_dkist.get_gcrs(obstime=Time(self.constants.solar_gain_ip_start_time))
        heliocentric_coord = coord.transform_to(
            HeliocentricInertial(obstime=Time(self.constants.solar_gain_ip_start_time))
        )
        obs_vr_kms = heliocentric_coord.d_distance
        return obs_vr_kms
