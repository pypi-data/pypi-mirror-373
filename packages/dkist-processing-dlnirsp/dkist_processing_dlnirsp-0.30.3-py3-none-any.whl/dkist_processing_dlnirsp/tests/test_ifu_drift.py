from itertools import product

import numpy as np
import pytest
import scipy.ndimage as spnd
from astropy.io import fits
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_array_encoder

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks.ifu_drift import IfuDriftCalibration
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingConstants
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingParameters


@pytest.fixture
def ifu_drift_task(
    tmp_path,
    recipe_run_id,
    link_constants_db,
    assign_input_dataset_doc_to_task,
    jband_group_id_file_parameter,
    jband_dispersion_file_parameter,
    jband_ifu_x_pos_file_parameter,
    jband_ifu_y_pos_file_parameter,
    constants_class_with_different_num_slits,
):
    link_constants_db(
        recipe_run_id=recipe_run_id,
        constants_obj=DlnirspTestingConstants(),
    )

    with IfuDriftCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        assign_input_dataset_doc_to_task(
            task,
            DlnirspTestingParameters(
                dlnirsp_group_id_file_jband=jband_group_id_file_parameter(task),
                dlnirsp_geo_dispersion_file_jband=jband_dispersion_file_parameter(task),
                dlnirsp_ifu_x_pos_file_jband=jband_ifu_x_pos_file_parameter(task),
                dlnirsp_ifu_y_pos_file_jband=jband_ifu_y_pos_file_parameter(task),
            ),
        )
        task.constants = constants_class_with_different_num_slits(
            recipe_run_id=recipe_run_id, task_name="test"
        )

        yield task
        task._purge()


@pytest.fixture(
    params=[pytest.param((-1.1, 1.9), id="negative_drift"), pytest.param((0, 1.2), id="zero_drift")]
)
def ifu_drift(request) -> tuple[float, float]:
    # See note on `test_ifu_drift_task`
    return request.param


@pytest.fixture
def write_drifted_solar_gain_frame(ifu_drift, jband_group_id_array):
    def writer(task):
        dark_signal = 100.0
        gain_signal = 1000.0
        exp_time = 1.0

        dark_array = np.ones_like(jband_group_id_array) * dark_signal

        solar_gain = np.ones_like(jband_group_id_array) * gain_signal + dark_signal
        solar_gain[np.isnan(jband_group_id_array)] = 0.0
        drifted_solar_gain = spnd.shift(solar_gain, shift=ifu_drift)
        drifted_solar_gain[drifted_solar_gain < gain_signal / 2.0] = dark_signal
        drifted_solar_gain[2, 20] = np.nan

        task.write(
            data=dark_array,
            tags=[
                DlnirspTag.intermediate_frame_dark(exposure_time=exp_time),
            ],
            encoder=fits_array_encoder,
        )
        task.write(
            data=drifted_solar_gain,
            tags=[
                DlnirspTag.linearized_frame(),
                DlnirspTag.task_solar_gain(),
                DlnirspTag.exposure_time(exp_time),
            ],
            encoder=fits_array_encoder,
        )

    return writer


@pytest.mark.parametrize(
    "drift_valid", [pytest.param(True, id="valid_drift"), pytest.param(False, id="invalid_drift")]
)
def test_ifu_drift_task(
    ifu_drift_task,
    write_drifted_solar_gain_frame,
    jband_group_id_array,
    jband_dispersion_array,
    jband_ifu_x_pos_array,
    jband_ifu_y_pos_array,
    ifu_drift,
    drift_valid,
    mocker,
    fake_gql_client,
):
    """
    Given: An `IfuDriftCalibration` task with a solar gain image, an intermediate dark frame, and a known IFU drift
    When: Computing the IFU drift and applying it to the IFU metrology files
    Then: The resulting drifted files are correct.
    """
    # Note, because the test version of the metrology arrays are pretty small this test is pretty fragile to changes
    # in the known drift (the `ifu_drift` fixture). As such, this unit test is more a test that all the machinery of the
    # tasks works correctly for a single known case.
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    validate_mock = mocker.patch(
        "dkist_processing_dlnirsp.tasks.ifu_drift.IfuDriftCalibration.validate_drift"
    )
    validate_mock.return_value = drift_valid

    task = ifu_drift_task
    write_drifted_solar_gain_frame(task)
    task()

    for tag, raw_array in zip(
        [
            DlnirspTag.task_drifted_ifu_groups(),
            DlnirspTag.task_drifted_dispersion(),
            DlnirspTag.task_drifted_ifu_x_pos(),
            DlnirspTag.task_drifted_ifu_y_pos(),
        ],
        [
            jband_group_id_array,
            jband_dispersion_array,
            jband_ifu_x_pos_array,
            jband_ifu_y_pos_array,
        ],
    ):

        if drift_valid:
            int_drift = tuple(round(i) for i in ifu_drift)
            pad_tuple = tuple((abs(i), abs(i)) for i in int_drift)
            slice_tuple = tuple(slice(abs(i) or None, -abs(i) or None) for i in int_drift)

            expected_array = np.roll(
                np.pad(raw_array, pad_tuple, constant_values=np.nan), int_drift, axis=(0, 1)
            )[slice_tuple]
        else:
            expected_array = raw_array

        files = list(
            task.read(
                tags=[
                    DlnirspTag.intermediate_frame(),
                    tag,
                ]
            )
        )
        assert len(files) == 1
        drifted_array = fits.open(files[0])[0].data
        assert drifted_array.shape == raw_array.shape
        np.testing.assert_allclose(expected_array, drifted_array, equal_nan=True)


def test_validate_drift(ifu_drift_task, jband_group_id_array):
    """
    Given: Good and bad drift amounts and drifted arrays that don't preserve group count
    When: Validating these inputs
    Then: Valid inputs return True and invalid ones return False
    """
    task = ifu_drift_task
    max_drift = task.parameters.group_id_max_drift_px
    # Valid
    assert task.validate_drift((0, 0), jband_group_id_array, jband_group_id_array) is True

    # Drift too large
    assert (
        task.validate_drift((max_drift * 2, 0), jband_group_id_array, jband_group_id_array) is False
    )
    assert (
        task.validate_drift((0, -max_drift * 2), jband_group_id_array, jband_group_id_array)
        is False
    )

    # Wrong shape
    assert (
        task.validate_drift(
            (0, 0),
            jband_group_id_array,
            jband_group_id_array[jband_group_id_array.shape[0] // 2 :, :],
        )
        is False
    )

    # Unpreserved group ID pixels
    badly_drifted_array = jband_group_id_array * 1.0
    badly_drifted_array[badly_drifted_array == 0] = 1.0
    assert task.validate_drift((0, 0), badly_drifted_array, jband_group_id_array) is False

    # Except groups within the drift of edge pixels, which are allowed to be missing data
    for drift_mag in range(1, 4):
        raw_array_with_single_group = np.empty((10, 10)) * np.nan
        raw_array_with_single_group[drift_mag:-drift_mag, drift_mag:-drift_mag] = 1.0
        for drift in product([-drift_mag, 0, drift_mag], repeat=2):
            drifted_array = task.apply_drift_to_array(raw_array_with_single_group, drift)
            assert task.validate_drift(drift, drifted_array, raw_array_with_single_group) is True


def test_beam_match_corrections(ifu_drift_task, jband_group_id_array):
    """
    Given: An ID array with two groups (corresponding to the same group in two beams) and a drift that drifts them off
      the edge by different amounts
    When: Computing the beam correction mask
    Then: The correct mask is computed: the masked ID array has the same number of spatial px in each group
    """
    raw_group_id_array = np.empty((10, 10)) * np.nan

    # Number of spectral pixels intentionally different
    raw_group_id_array[4:9, 0:5] = 0.0
    raw_group_id_array[2:7, 7:10] = 1.0

    # Make sure we're starting with groups with the same number of spatial pixels
    assert (
        np.unique(np.where(raw_group_id_array == 0)[0]).size
        == np.unique(np.where(raw_group_id_array == 1)[0]).size
    )

    drift = (3, 1)
    drifted_group_id_array = ifu_drift_task.apply_drift_to_array(raw_group_id_array, drift)

    # Show that the drift did indeed drift one group off the edge more than the other
    assert (
        np.unique(np.where(drifted_group_id_array == 0)[0]).size
        != np.unique(np.where(drifted_group_id_array == 1)[0]).size
    )

    mask = ifu_drift_task.compute_beam_match_corrections(drift, drifted_group_id_array)
    corrected_array = drifted_group_id_array * mask

    # Check that the correction has restored equal spatial pixels between the two groups
    assert (
        np.unique(np.where(corrected_array == 0)[0]).size
        == np.unique(np.where(corrected_array == 1)[0]).size
    )
