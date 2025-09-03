import numpy as np
import pytest
from astropy.io import fits
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_array_encoder

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks.bad_pixel_map import BadPixelCalibration
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingConstants
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingParameters


@pytest.fixture
def bad_pixel_map_task_with_data(
    tmp_path,
    recipe_run_id,
    arm_id,
    link_constants_db,
    dynamic_gain_bad_pix_loc,
    dynamic_dark_bad_pix_loc,
    group_id_array,
    assign_input_dataset_doc_to_task,
    vis_static_bad_pix_map_file_parameter,
    jband_static_bad_pix_map_file_parameter,
    hband_static_bad_pix_map_file_parameter,
    write_drifted_group_ids_to_task,
):
    lamp_exp_time = 34.5
    constants = DlnirspTestingConstants(ARM_ID=arm_id, LAMP_GAIN_EXPOSURE_TIMES=(lamp_exp_time,))
    link_constants_db(
        recipe_run_id=recipe_run_id,
        constants_obj=constants,
    )

    with BadPixelCalibration(
        recipe_run_id=recipe_run_id, workflow_name="workflow_name", workflow_version="vtest.foo"
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        parameters = DlnirspTestingParameters(
            dlnirsp_static_bad_pixel_map_vis=vis_static_bad_pix_map_file_parameter(task),
            dlnirsp_static_bad_pixel_map_jband=jband_static_bad_pix_map_file_parameter(task),
            dlnirsp_static_bad_pixel_map_hband=hband_static_bad_pix_map_file_parameter(task),
            dlnirsp_bad_pixel_gain_median_smooth_size=(1, 3),
            dlnirsp_bad_pixel_gain_sigma_threshold=2,
            dlnirsp_bad_pixel_dark_median_smooth_size=(3, 1),
        )
        assign_input_dataset_doc_to_task(task, parameters, arm_id=arm_id)
        write_drifted_group_ids_to_task(task)
        data_shape = group_id_array.shape
        avg_lamp_data = np.ones(data_shape) * 23456.78
        cold_pix_loc, hot_pix_loc = dynamic_gain_bad_pix_loc
        avg_lamp_data[hot_pix_loc] += 20000.0
        avg_lamp_data[cold_pix_loc] -= 20000.0
        task.write(
            data=avg_lamp_data,
            tags=[DlnirspTag.intermediate_frame(), DlnirspTag.task_lamp_gain()],
            encoder=fits_array_encoder,
        )
        dark1 = np.ones(data_shape) * 100.0
        dark2 = np.ones(data_shape) * 100.0
        dark2[dynamic_dark_bad_pix_loc] *= 10000.0
        task.write(
            data=dark1,
            tags=[
                DlnirspTag.linearized_frame(),
                DlnirspTag.task_dark(),
                DlnirspTag.exposure_time(lamp_exp_time),
            ],
            encoder=fits_array_encoder,
        )
        task.write(
            data=dark2,
            tags=[
                DlnirspTag.linearized_frame(),
                DlnirspTag.task_dark(),
                DlnirspTag.exposure_time(lamp_exp_time),
            ],
            encoder=fits_array_encoder,
        )

        yield task
        task._purge()


@pytest.fixture
def dynamic_gain_bad_pix_loc(arm_id) -> tuple:
    # These all must fall one the "data" regions of the detector, which is kind of a pain.
    # See the `group_id_array` and `slit_boarders` fixtures for help on getting it right.
    if arm_id == "VIS":
        # VIS arm doesn't really matter b/c we don't compute dynamic map. Don't sweat it.
        cold = (np.array([2, 8]), np.array([2, 30]))
        hot = (np.array([4, 7]), np.array([4, 20]))
    elif arm_id == "JBand":
        cold = (np.array([1, 2]), np.array([3, 29]))
        hot = (np.array([4, 4]), np.array([29, 11]))
    elif arm_id == "HBand":
        cold = (np.array([4, 5]), np.array([10, 21]))
        hot = (np.array([7, 8]), np.array([15, 9]))

    return cold, hot


@pytest.fixture
def dynamic_dark_bad_pix_loc(arm_id) -> tuple:
    if arm_id == "VIS":
        return (np.array([3]), np.array([15]))
    if arm_id == "JBand":
        return (np.array([4]), np.array([17]))
    if arm_id == "HBand":
        return (np.array([5]), np.array([19]))


@pytest.mark.parametrize(
    "arm_id",
    [
        pytest.param("VIS", id="VIS"),
        pytest.param("JBand", id="JBand"),
        pytest.param("HBand", id="HBand"),
    ],
)
def test_bad_pixel_map(
    bad_pixel_map_task_with_data,
    dynamic_gain_bad_pix_loc,
    dynamic_dark_bad_pix_loc,
    vis_static_bad_pix_array,
    jband_static_bad_pix_array,
    hband_static_bad_pix_array,
    arm_id,
    mocker,
    fake_gql_client,
):
    """
    Given: A BadPixelCalibration task and an INTERMEDIATE lamp gain array with some hot and cold pixels
    When: Computing the bad pixel map
    Then: The task runs and the computed bad pixel map is correct
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task = bad_pixel_map_task_with_data

    task()

    expected_dynamic = np.zeros(vis_static_bad_pix_array.shape, dtype=int)
    cold_pix_loc, hot_pix_loc = dynamic_gain_bad_pix_loc
    expected_dynamic[cold_pix_loc] = 1
    expected_dynamic[hot_pix_loc] = 1
    expected_dynamic[dynamic_dark_bad_pix_loc] = 1

    match arm_id:
        case "VIS":
            expected_bad_pixel_map = (
                vis_static_bad_pix_array  # Don't add dynamic because we don't check for it in VIS
            )
        case "JBand":
            expected_bad_pixel_map = jband_static_bad_pix_array + expected_dynamic
        case "HBand":
            expected_bad_pixel_map = hband_static_bad_pix_array + expected_dynamic

    bad_pix_files = list(
        task.read(tags=[DlnirspTag.intermediate_frame(), DlnirspTag.task_bad_pixel_map()])
    )
    assert len(bad_pix_files) == 1
    bad_pixel_map = fits.open(bad_pix_files[0])[0].data
    np.testing.assert_array_equal(bad_pixel_map, expected_bad_pixel_map)

    unique_values = np.unique(bad_pixel_map)
    np.testing.assert_array_equal(unique_values, np.array([0, 1]))
