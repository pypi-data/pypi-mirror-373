from dataclasses import asdict

import astropy.units as u
import numpy as np
import pytest
from dkist_processing_common._util.scratch import WorkflowFileSystem
from pydantic import BaseModel

from dkist_processing_dlnirsp.models.parameters import DlnirspParameters
from dkist_processing_dlnirsp.models.parameters import DlnirspParsingParameters
from dkist_processing_dlnirsp.tasks.dlnirsp_base import DlnirspTaskBase
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingConstants
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingParameters


@pytest.fixture(scope="session")
def parse_parameter_names() -> list[str]:
    # The property names of all parameters on `DlnirspParsingParameters`
    return [k for k, v in vars(DlnirspParsingParameters).items() if isinstance(v, property)]


@pytest.fixture(scope="session")
def arm_parameter_names() -> list[str]:
    return [
        "linearization_poly_coeffs_jband",
        "linearization_poly_coeffs_hband",
        "linearization_saturation_threshold_jband",
        "linearization_saturation_threshold_hband",
        "group_id_file_vis",
        "group_id_file_jband",
        "group_id_file_hband",
        "static_bad_pixel_map_vis",
        "static_bad_pixel_map_jband",
        "static_bad_pixel_map_hband",
        "geo_dispersion_file_vis",
        "geo_dispersion_file_jband",
        "geo_dispersion_file_hband",
        "wavecal_center_axis_position_mm_vis",
        "wavecal_center_axis_position_mm_jband",
        "wavecal_center_axis_position_mm_hband",
        "wavecal_center_axis_littrow_angle_deg_vis",
        "wavecal_center_axis_littrow_angle_deg_jband",
        "wavecal_center_axis_littrow_angle_deg_hband",
        "wavecal_resolving_power_vis",
        "wavecal_resolving_power_jband",
        "wavecal_resolving_power_hband",
        "solar_characteristic_spectra_normalization_percentage_vis",
        "solar_characteristic_spectra_normalization_percentage_jband",
        "solar_characteristic_spectra_normalization_percentage_hband",
        "ifu_x_pos_file_vis",
        "ifu_x_pos_file_jband",
        "ifu_x_pos_file_hband",
        "ifu_y_pos_file_vis",
        "ifu_y_pos_file_jband",
        "ifu_y_pos_file_hband",
    ]


@pytest.fixture(scope="session")
def unit_parameter_names_and_units() -> dict[str, u.Unit]:
    return {
        "wavecal_grating_zero_point_angle_offset_deg": u.deg,
        "wavecal_spectral_camera_focal_length_mm": u.mm,
        "wavecal_center_axis_position_mm": u.mm,
        "wavecal_center_axis_littrow_angle_deg": u.deg,
    }


class Task(DlnirspTaskBase):
    def run(self):
        pass


@pytest.fixture
def task_with_parameters(
    tmp_path,
    recipe_run_id,
    assign_input_dataset_doc_to_task,
    link_constants_db,
    arm_id,
    default_obs_ip_start_time,
    vis_group_id_file_parameter,
    vis_static_bad_pix_map_file_parameter,
    vis_dispersion_file_parameter,
    vis_ifu_x_pos_file_parameter,
    vis_ifu_y_pos_file_parameter,
    jband_group_id_file_parameter,
    jband_static_bad_pix_map_file_parameter,
    jband_dispersion_file_parameter,
    jband_ifu_x_pos_file_parameter,
    jband_ifu_y_pos_file_parameter,
    hband_group_id_file_parameter,
    hband_static_bad_pix_map_file_parameter,
    hband_dispersion_file_parameter,
    hband_ifu_x_pos_file_parameter,
    hband_ifu_y_pos_file_parameter,
):
    def make_task(parameter_class=DlnirspParameters, obs_ip_start_time=default_obs_ip_start_time):
        link_constants_db(
            recipe_run_id=recipe_run_id,
            constants_obj=DlnirspTestingConstants(),
        )
        with Task(
            recipe_run_id=recipe_run_id,
            workflow_name="workflow_name",
            workflow_version="workflow_version",
        ) as task:
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            parameters = DlnirspTestingParameters(
                dlnirsp_group_id_file_vis=vis_group_id_file_parameter(task),
                dlnirsp_static_bad_pixel_map_vis=vis_static_bad_pix_map_file_parameter(task),
                dlnirsp_geo_dispersion_file_vis=vis_dispersion_file_parameter(task),
                dlnirsp_ifu_x_pos_file_vis=vis_ifu_x_pos_file_parameter(task),
                dlnirsp_ifu_y_pos_file_vis=vis_ifu_y_pos_file_parameter(task),
                dlnirsp_group_id_file_jband=jband_group_id_file_parameter(task),
                dlnirsp_static_bad_pixel_map_jband=jband_static_bad_pix_map_file_parameter(task),
                dlnirsp_geo_dispersion_file_jband=jband_dispersion_file_parameter(task),
                dlnirsp_ifu_x_pos_file_jband=jband_ifu_x_pos_file_parameter(task),
                dlnirsp_ifu_y_pos_file_jband=jband_ifu_y_pos_file_parameter(task),
                dlnirsp_group_id_file_hband=hband_group_id_file_parameter(task),
                dlnirsp_static_bad_pixel_map_hband=hband_static_bad_pix_map_file_parameter(task),
                dlnirsp_geo_dispersion_file_hband=hband_dispersion_file_parameter(task),
                dlnirsp_ifu_x_pos_file_hband=hband_ifu_x_pos_file_parameter(task),
                dlnirsp_ifu_y_pos_file_hband=hband_ifu_y_pos_file_parameter(task),
            )
            assign_input_dataset_doc_to_task(
                task=task,
                parameters=parameters,
                parameter_class=parameter_class,
                arm_id=arm_id,
                obs_ip_start_time=obs_ip_start_time,
            )

            yield task, parameters
            task._purge()

    return make_task


@pytest.mark.parametrize("arm_id", [pytest.param("VIS")])
def test_standard_parameters(
    task_with_parameters,
    parse_parameter_names,
    arm_parameter_names,
    unit_parameter_names_and_units,
    arm_id,
):
    """
    Given: A Science task with the parameter mixin
    When: Accessing properties for parameters that are just base values
    Then: The correct value is returned
    """
    task, expected = next(task_with_parameters())
    task_param_attr = task.parameters
    for pn, pv in asdict(expected).items():
        property_name = pn.removeprefix("dlnirsp_")
        if property_name not in parse_parameter_names + arm_parameter_names:
            param_obj_value = getattr(task_param_attr, property_name)

            if isinstance(pv, tuple):
                pv = list(pv)

            # Order of if statements matters here; all `Quantities` are *also* instances of `np.ndarray` :(
            if isinstance(param_obj_value, u.Quantity):
                assert param_obj_value.value == pv
                assert param_obj_value.unit == unit_parameter_names_and_units[property_name]
            elif isinstance(param_obj_value, np.ndarray):
                np.testing.assert_array_equal(param_obj_value, pv)
            elif isinstance(param_obj_value, BaseModel):
                assert param_obj_value.model_dump() == pv
            else:
                assert param_obj_value == pv


# These params are capitalized on purpose
@pytest.mark.parametrize(
    "arm_id", [pytest.param("VIS"), pytest.param("JBand"), pytest.param("HBand")]
)
def test_arm_parameters(
    task_with_parameters, arm_parameter_names, unit_parameter_names_and_units, request, arm_id
):
    """
    Given: A task with parameters
    When: Accessing parameters that are arm dependent
    Then: The correct values are returned
    """
    # This might just be a test of the fixturization of our test environment. But it's still useful for that.
    cased_arm_id = arm_id.casefold()
    expected_group_id_array = request.getfixturevalue(f"{cased_arm_id}_group_id_array")
    expected_static_bad_pix_map = request.getfixturevalue(f"{cased_arm_id}_static_bad_pix_array")
    expcted_dispersion_array = request.getfixturevalue(f"{cased_arm_id}_dispersion_array")
    expected_ifu_x_pos_array = request.getfixturevalue(f"{cased_arm_id}_ifu_x_pos_array")
    expected_ifu_y_pos_array = request.getfixturevalue(f"{cased_arm_id}_ifu_y_pos_array")

    task, expected = next(task_with_parameters(parameter_class=DlnirspParameters))
    assert task.parameters.solar_characteristic_spectra_normalization_percentage == getattr(
        expected,
        f"dlnirsp_solar_characteristic_spectra_normalization_percentage_{arm_id.casefold()}",
    )
    np.testing.assert_array_equal(task.parameters.raw_group_id_array, expected_group_id_array)
    np.testing.assert_array_equal(task.parameters.static_bad_pixel_map, expected_static_bad_pix_map)
    np.testing.assert_array_equal(
        task.parameters.raw_dispersion_array,
        expcted_dispersion_array,
    )
    np.testing.assert_array_equal(task.parameters.raw_ifu_x_pos_array, expected_ifu_x_pos_array)
    np.testing.assert_array_equal(task.parameters.raw_ifu_y_pos_array, expected_ifu_y_pos_array)

    for param_name, unit in unit_parameter_names_and_units.items():
        if f"{param_name}_{cased_arm_id}" not in arm_parameter_names:
            continue
        assert getattr(task.parameters, param_name).value == getattr(
            expected, f"dlnirsp_{param_name}_{cased_arm_id}"
        )
        assert getattr(task.parameters, param_name).unit == unit

    if cased_arm_id != "vis":
        np.testing.assert_array_equal(
            task.parameters.linearization_poly_coeffs,
            getattr(expected, f"dlnirsp_linearization_poly_coeffs_{cased_arm_id}"),
        )
        np.testing.assert_array_equal(
            task.parameters.linearization_saturation_threshold,
            getattr(expected, f"dlnirsp_linearization_saturation_threshold_{cased_arm_id}"),
        )


@pytest.mark.parametrize("arm_id", [pytest.param("VIS")])
def test_parse_parameters(task_with_parameters, parse_parameter_names):
    """
    Given: A Science task with Parsing parameters
    When: Accessing properties for Parse parameters
    Then: The correct value is returned
    """
    task, expected = next(
        task_with_parameters(
            parameter_class=DlnirspParsingParameters,
        )
    )
    task_param_attr = task.parameters
    for pn, pv in asdict(expected).items():
        property_name = pn.removeprefix("dlnirsp_")
        if property_name in parse_parameter_names and type(pv) is not dict:
            assert getattr(task_param_attr, property_name) == pv
