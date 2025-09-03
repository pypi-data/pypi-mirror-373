import json
import shutil

import asdf
import astropy.units as u
import numpy as np
import pytest
from astropy import constants
from astropy.coordinates import EarthLocation
from astropy.stats import gaussian_fwhm_to_sigma
from astropy.time import Time
from astropy.units import Quantity
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.codecs.json import json_encoder
from dkist_processing_common.models.metric_code import MetricCode
from scipy.ndimage import gaussian_filter1d
from solar_wavelength_calibration import Atlas
from sunpy.coordinates import HeliocentricInertial

from dkist_processing_dlnirsp.models.constants import DlnirspConstants
from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks.wavelength_calibration import WavelengthCalibration
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingConstants
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingParameters
from dkist_processing_dlnirsp.tests.conftest import write_geometric_calibration_to_task


@pytest.fixture
def num_wave_pix() -> int:
    return 250


@pytest.fixture
def num_spatial_pix() -> int:
    return 10


@pytest.fixture
def constants_class_with_1_slit():
    class ConstantsWithOneSlit(DlnirspConstants):
        @property
        def num_slits(self) -> int:
            return 1

    return ConstantsWithOneSlit


@pytest.fixture
def large_group_id_array(num_wave_pix, num_spatial_pix) -> np.ndarray:
    # We just need something simple with two slitbeams of one group each
    padding = np.empty(num_wave_pix // 10) * np.nan
    group_zero = np.zeros(num_wave_pix)
    group_one = np.ones(num_wave_pix)
    single_spatial_row = np.r_[padding, group_zero, padding, group_one, padding]
    group_id_array = np.vstack([single_spatial_row] * num_spatial_pix)

    return group_id_array


@pytest.fixture
def noop_shifts_and_scales(
    num_spatial_pix, large_group_id_array
) -> tuple[dict[int, np.ndarray], dict[int, np.ndarray]]:
    shift_amount = 0.0
    scale_amount = 1.0

    num_groups = int(np.nanmax(large_group_id_array) + 1)

    # This length of these arrays just has to be longer than a single group's spatial size
    shift_dict = {g: np.ones(40) * shift_amount for g in range(num_groups)}
    scale_dict = {g: np.ones(40) * scale_amount for g in range(num_groups)}

    return shift_dict, scale_dict


@pytest.fixture
def reference_geocal_wave_vector(num_wave_pix) -> np.ndarray:
    return np.arange(num_wave_pix)


@pytest.fixture
def telluric_opacity_factor() -> float:
    return 0.4


@pytest.fixture
def solar_ip_start_time() -> str:
    return "1988-07-02T10:00:00"


@pytest.fixture
def doppler_velocity(solar_ip_start_time) -> Quantity:
    _dkist_site_info = {
        "aliases": ["DKIST", "ATST"],
        "name": "Daniel K. Inouye Solar Telescope",
        "elevation": 3067,
        "elevation_unit": "meter",
        "latitude": 20.7067,
        "latitude_unit": "degree",
        "longitude": 203.7436,
        "longitude_unit": "degree",
        "timezone": "US/Hawaii",
        "source": "DKIST website: https://www.nso.edu/telescopes/dki-solar-telescope/",
    }
    location_of_dkist = EarthLocation.from_geodetic(
        _dkist_site_info["longitude"] * u.Unit(_dkist_site_info["longitude_unit"]),
        _dkist_site_info["latitude"] * u.Unit(_dkist_site_info["latitude_unit"]),
        _dkist_site_info["elevation"] * u.Unit(_dkist_site_info["elevation_unit"]),
    )

    coord = location_of_dkist.get_gcrs(obstime=Time(solar_ip_start_time))
    heliocentric_coord = coord.transform_to(HeliocentricInertial(obstime=Time(solar_ip_start_time)))
    obs_vr_kms = heliocentric_coord.d_distance

    return obs_vr_kms


@pytest.fixture
def central_wavelength(arm_id: str) -> Quantity:
    wavelengths = {"VIS": 854.2 * u.nm, "JBand": 1083.0 * u.nm, "HBand": 1565.0 * u.nm}
    return wavelengths[arm_id]


@pytest.fixture
def dispersion(arm_id: str) -> Quantity:
    dispersions = {
        "VIS": 0.0022 * u.nm / u.pix,
        "JBand": 0.0044 * u.nm / u.pix,
        "HBand": 0.0063 * u.nm / u.pix,
    }

    return dispersions[arm_id]


@pytest.fixture
def resolving_power(arm_id: str) -> float:
    powers = {"VIS": 130_000, "JBand": 90_000, "HBand": 90_000}
    return powers[arm_id]


@pytest.fixture(scope="session")
def solar_atlas() -> Atlas:
    return Atlas()


@pytest.fixture
def observed_wavelength_offset() -> Quantity:
    return 0.2 * u.nm


@pytest.fixture
def nan_edge_amount(num_wave_pix) -> int:
    return num_wave_pix // 20


@pytest.fixture
def nan_edges(num_wave_pix, nan_edge_amount, even_pix_desired) -> np.ndarray:
    modification_array = np.ones(num_wave_pix, dtype=float)
    num_good_pix = num_wave_pix - nan_edge_amount * 2
    currently_even = not (num_good_pix % 2)
    match currently_even is even_pix_desired:
        case False:
            modification_array[: nan_edge_amount + 1] = np.nan
        case True:
            modification_array[:nan_edge_amount] = np.nan

    modification_array[-nan_edge_amount:] = np.nan

    return modification_array


@pytest.fixture
def observed_solar_gain_signal(
    central_wavelength,
    dispersion,
    num_wave_pix,
    solar_atlas,
    telluric_opacity_factor,
    doppler_velocity,
    resolving_power,
    observed_wavelength_offset,
    nan_edges,
) -> np.ndarray:
    """Make an "observed" solar spectrum from a shifted and atmospherically corrected combination of solar and telluric atlases."""
    # Making a simple solution with just y = mx + b (no higher order angle or order stuff)
    wave_vec = (
        np.arange(num_wave_pix) - num_wave_pix // 2
    ) * u.pix * dispersion + central_wavelength

    doppler_shift = doppler_velocity / constants.c * central_wavelength
    solar_signal = np.interp(
        wave_vec,
        solar_atlas.solar_atlas_wavelength + doppler_shift + observed_wavelength_offset,
        solar_atlas.solar_atlas_transmission,
    )
    telluric_signal = (
        np.interp(
            wave_vec,
            solar_atlas.telluric_atlas_wavelength + observed_wavelength_offset,
            solar_atlas.telluric_atlas_transmission,
        )
        ** telluric_opacity_factor
    )

    combined_spec = solar_signal * telluric_signal

    sigma_wavelength = (
        central_wavelength.to_value(u.nm) / resolving_power
    ) * gaussian_fwhm_to_sigma
    sigma_pix = sigma_wavelength / np.abs(dispersion.to_value(u.nm / u.pix))
    observed_spec = gaussian_filter1d(combined_spec, np.abs(sigma_pix))

    # Add some NaNs at the ends
    observed_spec *= nan_edges
    return observed_spec


@pytest.fixture
def avg_unrectified_solar_gain_array(
    large_group_id_array, observed_solar_gain_signal
) -> np.ndarray:
    output_array = np.empty_like(large_group_id_array) * np.nan
    output_array[:, np.where(large_group_id_array[0] == 0)[0]] = observed_solar_gain_signal
    output_array[:, np.where(large_group_id_array[0] == 1)[0]] = observed_solar_gain_signal
    return output_array


@pytest.fixture
def wavecal_task_with_data(
    tmp_path,
    recipe_run_id,
    link_constants_db,
    assign_input_dataset_doc_to_task,
    large_group_id_array,
    noop_shifts_and_scales,
    constants_class_with_1_slit,
    reference_geocal_wave_vector,
    central_wavelength,
    resolving_power,
    dispersion,
    solar_ip_start_time,
    avg_unrectified_solar_gain_array,
    arm_id,
) -> WavelengthCalibration:

    link_constants_db(
        recipe_run_id=recipe_run_id,
        # Grating values taken from real data (the canonical test data; they're the same across all arms)
        constants_obj=DlnirspTestingConstants(
            ARM_ID=arm_id,
            SOLAR_GAIN_IP_START_TIME=solar_ip_start_time,
            WAVELENGTH=central_wavelength.to_value(u.nm),
            GRATING_POSITION_DEG=149.4,
            GRATING_CONSTANT_INVERSE_MM=23.0,
        ),
    )
    shifts, scales = noop_shifts_and_scales

    with WavelengthCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        assign_input_dataset_doc_to_task(
            task,
            DlnirspTestingParameters(dlnirsp_wavecal_resolving_power_jband=resolving_power),
        )
        task.constants = constants_class_with_1_slit(recipe_run_id=recipe_run_id, task_name="test")

        task.write(
            data=large_group_id_array,
            tags=[DlnirspTag.intermediate_frame(), DlnirspTag.task_drifted_ifu_groups()],
            encoder=fits_array_encoder,
        )
        write_geometric_calibration_to_task(
            task, shift_dict=shifts, scale_dict=scales, wave_axis=reference_geocal_wave_vector
        )
        task.write(
            data=dispersion.to_value(u.angstrom / u.pix),
            tags=[DlnirspTag.intermediate(), DlnirspTag.task_dispersion()],
            encoder=json_encoder,
        )
        task.write(
            data=avg_unrectified_solar_gain_array,
            tags=[DlnirspTag.intermediate_frame(), DlnirspTag.task_avg_unrectified_solar_gain()],
            encoder=fits_array_encoder,
        )

        yield task
        task._purge()


@pytest.fixture
def wavecal_task_no_data(
    tmp_path,
    recipe_run_id,
    link_constants_db,
    assign_input_dataset_doc_to_task,
) -> WavelengthCalibration:

    link_constants_db(
        recipe_run_id=recipe_run_id,
        constants_obj=DlnirspTestingConstants(),
    )

    with WavelengthCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        assign_input_dataset_doc_to_task(task, DlnirspTestingParameters())

        yield task
        task._purge()


@pytest.mark.parametrize(
    "arm_id, even_pix_desired",
    [
        pytest.param("VIS", True, id="VIS"),
        pytest.param("JBand", True, id="JBand"),
        pytest.param("HBand", True, id="HBand"),
        pytest.param("JBand", False, id="odd_num_wave_pix"),
    ],
)
def test_wavelength_calibration(
    wavecal_task_with_data,
    central_wavelength,
    observed_wavelength_offset,
    dispersion,
    num_wave_pix,
    nan_edges,
    nan_edge_amount,
    mocker,
    fake_gql_client,
):
    """
    Given: A `WavelengthCalibration` task with all the data needed to run
    When: Running the task
    Then: The correct output files are produced and the wavelength solution is close to what's expected
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task = wavecal_task_with_data

    num_good_pix = np.sum(~np.isnan(nan_edges))
    # + 1 from wavecal library
    # `nan_edge_amount + num_good_pix % 2` accounts for the fact that we add a NaN pixel in the `nan_edges` fixture
    # if we want an odd `num_good_pix`.
    expected_crpix = num_good_pix // 2 + 1 + (nan_edge_amount + num_good_pix % 2)

    expected_crval = central_wavelength - observed_wavelength_offset

    task()

    wavelength_solution_header_files = list(
        task.read(tags=[DlnirspTag.intermediate(), DlnirspTag.task_wavelength_solution()])
    )
    assert len(wavelength_solution_header_files) == 1
    with open(wavelength_solution_header_files[0], "r") as f:
        wavecal_header_dict = json.load(f)

    assert wavecal_header_dict["CRPIX3"] == expected_crpix
    np.testing.assert_allclose(
        wavecal_header_dict["CRVAL3"], expected_crval.to_value(u.nm), rtol=1e-4
    )
    np.testing.assert_allclose(
        wavecal_header_dict["CDELT3"], dispersion.to_value(u.nm / u.pix), rtol=1e-1
    )

    incident_light_angle = (
        task.parameters.wavecal_grating_zero_point_angle_offset_deg
        - task.constants.grating_position_deg
    )
    assert wavecal_header_dict["PV3_0"] == task.constants.grating_constant_inverse_mm.to_value(
        1 / u.m
    )
    assert wavecal_header_dict["PV3_1"] == task.compute_spectral_order(
        crval=task.constants.wavelength * u.nm, incident_light_angle=incident_light_angle
    )
    assert wavecal_header_dict["PV3_2"] == incident_light_angle.to_value(u.deg)

    quality_files = list(task.read(tags=[DlnirspTag.quality(MetricCode.wavecal_fit)]))
    assert len(quality_files) == 1
    with open(quality_files[0]) as f:
        quality_dict = json.load(f)
        assert sorted(
            [
                "input_wavelength_nm",
                "input_spectrum",
                "best_fit_wavelength_nm",
                "best_fit_atlas",
                "normalized_residuals",
                "weights",
            ]
        ) == sorted(list(quality_dict.keys()))

    # Uncomment to assess fit with your eyes
    # shutil.copy(quality_files[0], f"./test_fit_{arm_id}.json")


@pytest.mark.parametrize(
    "nan_locations",
    [
        pytest.param("internal", id="internal_NaN"),
        pytest.param("edge", id="edge_NaN"),
        pytest.param("both", id="edge_and_internal_NaN"),
        pytest.param("none", id="non_NaN"),
    ],
)
def test_chop_and_clean_NaNs(wavecal_task_no_data, nan_locations):
    """
    Given: A `WavelengthCalibration` task with a spectrum that has NaNs in strategic places
    When: Cleaning the spectrum with the `chop_and_clean_NaNs` method
    Then: The resulting spectrum has the expected length and no NaN values
    """
    raw_spectrum = np.arange(1000.0)
    num_edge_px = 30
    internal_nan_idx = 628
    match nan_locations:
        case "internal":
            raw_spectrum[internal_nan_idx] = np.nan
        case "edge":
            raw_spectrum[:num_edge_px] = np.nan
            raw_spectrum[-num_edge_px:] = np.nan
        case "both":
            raw_spectrum[internal_nan_idx] = np.nan
            raw_spectrum[:num_edge_px] = np.nan
            raw_spectrum[-num_edge_px:] = np.nan

    cleaned_spec, start_non_nan_idx = wavecal_task_no_data.chop_and_clean_NaNs(
        spectrum=raw_spectrum
    )

    expected_size = raw_spectrum.size
    expected_start_idx = 0
    if nan_locations in ["edge", "both"]:
        expected_size -= 2 * num_edge_px
        expected_start_idx += num_edge_px

    assert cleaned_spec.size == expected_size
    assert start_non_nan_idx == expected_start_idx
    assert np.sum(np.isnan(cleaned_spec)) == 0
    # Check that the interpolation happened correctly. Pretty easy when the spectrum is a line with a slope of 1 and
    # 0 intercept
    np.testing.assert_allclose(
        cleaned_spec[internal_nan_idx - expected_start_idx], internal_nan_idx
    )
