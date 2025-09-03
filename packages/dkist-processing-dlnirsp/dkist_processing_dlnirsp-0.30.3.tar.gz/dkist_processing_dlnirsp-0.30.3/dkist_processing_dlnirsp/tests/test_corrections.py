import numpy as np
import pytest
from dkist_processing_common._util.scratch import WorkflowFileSystem

from dkist_processing_dlnirsp.tasks.dlnirsp_base import DlnirspTaskBase
from dkist_processing_dlnirsp.tasks.mixin.corrections import CorrectionsMixin
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingConstants
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingParameters
from dkist_processing_dlnirsp.tests.conftest import write_geometric_calibration_to_task


class DummyTask(DlnirspTaskBase, CorrectionsMixin):
    def run(self) -> None:
        pass


def convert_idx_to_slices(indices: tuple[np.ndarray, np.ndarray]) -> tuple[slice, slice]:
    spatial_index, spectral_index = indices
    spatial_slice = slice(spatial_index.min(), spatial_index.max() + 1)
    spectral_slice = slice(spectral_index.min(), spectral_index.max() + 1)

    return spatial_slice, spectral_slice


def gaussian(x: np.ndarray, mu: float, FWHM: float) -> np.ndarray:
    sigma = FWHM / 2.355
    return np.exp(-0.5 * (x - mu) ** 2 / sigma**2)


@pytest.fixture
def array_to_be_shifted(group_id_array, num_groups) -> tuple[np.ndarray, int]:
    array = np.ones(group_id_array.shape) * 99.0
    idx_of_marker = 2

    for g in range(num_groups):
        idx = np.where(group_id_array == g)
        spat_slice, spec_slice = convert_idx_to_slices(idx)
        spec_size = spec_slice.stop - spec_slice.start
        group_spec = np.zeros(spec_size)
        group_spec[idx_of_marker] = 1.0
        array[spat_slice, spec_slice] = group_spec

    return array, idx_of_marker


@pytest.fixture
def task_with_corrections_mixin(
    tmp_path,
    recipe_run_id,
    link_constants_db,
    assign_input_dataset_doc_to_task,
    shifts_and_scales,
    reference_wave_axis,
    write_drifted_group_ids_to_task,
):
    link_constants_db(recipe_run_id=recipe_run_id, constants_obj=DlnirspTestingConstants())

    with DummyTask(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        assign_input_dataset_doc_to_task(task, DlnirspTestingParameters())
        write_drifted_group_ids_to_task(task)
        shift_dict, scale_dict, _, _ = shifts_and_scales
        write_geometric_calibration_to_task(
            task=task, shift_dict=shift_dict, scale_dict=scale_dict, wave_axis=reference_wave_axis
        )

        yield task
        task._purge()


def test_remove_spec_geometry(
    task_with_corrections_mixin,
    array_to_be_shifted,
    shifts_and_scales,
    reference_wave_axis,
    num_groups,
):
    """
    Given: A task with the CorrectionsMixin
    When: Using the corrections mixin to shift an array
    Then: The correct shift is applied and the parts of the array outside a group are NaN
    """
    task = task_with_corrections_mixin
    shift_dict, scale_dict, shift_amount, scale_amount = shifts_and_scales

    array, marker_idx = array_to_be_shifted

    output_array_list = list(
        task.corrections_remove_spec_geometry(
            array,
            shift_dict=shift_dict,
            scale_dict=scale_dict,
            reference_wavelength_axis=reference_wave_axis,
        )
    )

    assert len(output_array_list) == 1
    output_array = output_array_list[0]

    # Relying on knowledge that [0,0] is not in any group
    assert np.isnan(output_array[0, 0])

    expected_marker_location = marker_idx + shift_amount
    for g in range(num_groups):
        group_data = task.group_id_get_data(data=output_array, group_id=g)
        for i in range(group_data.shape[0]):
            assert group_data[i, expected_marker_location] == 1.0


def test_apply_spec_geometry(
    task_with_corrections_mixin,
    array_to_be_shifted,
    shifts_and_scales,
    reference_wave_axis,
    num_groups,
):
    """
    Given: A task with the CorrectionsMixin
    When: Using the corrections mixin to reapply distortions to an array that has been de-distorted
    Then: The re-distorted array is the same as the original array
    """
    task = task_with_corrections_mixin
    shift_dict, scale_dict, shift_amount, scale_amount = shifts_and_scales

    OG_array, marker_idx = array_to_be_shifted

    corrected_array = task.corrections_remove_spec_geometry(
        OG_array,
        shift_dict=shift_dict,
        scale_dict=scale_dict,
        reference_wavelength_axis=reference_wave_axis,
    )

    redistorted_array_list = list(
        task.corrections_apply_spec_geometry(
            corrected_array,
            shift_dict=shift_dict,
            scale_dict=scale_dict,
            reference_wavelength_axis=reference_wave_axis,
        )
    )
    assert len(redistorted_array_list) == 1
    redistorted_array = redistorted_array_list[0]
    non_nan_idx = ~np.isnan(redistorted_array)
    np.testing.assert_allclose(OG_array[non_nan_idx], redistorted_array[non_nan_idx])


def test_rectified_machinery(
    task_with_corrections_mixin,
    array_with_groups,
    shifts_and_scales,
    num_groups,
    reference_wave_axis,
    num_slitbeams,
):
    """
    Given: A task with the CorrectionsMixin and GroupIdMixin
    When: Rectifying (applying geo correction to) an array, accessing groups in that array, and un-rectifying the array
    Then: The array is correctly placed on the universal wavelength axis without affecting the underlying data, and
          the re-application of the geometric offsets results in the same array.
    """
    task = task_with_corrections_mixin
    array = array_with_groups
    shift_dict, scale_dict, shift_amount, scale_amount = shifts_and_scales

    # Rectified group id array shape is correct
    expected_rectified_shape = (array.shape[0], reference_wave_axis.size * num_slitbeams)
    assert task.rectified_group_id_array.shape == expected_rectified_shape
    rectified_array = next(
        task.corrections_remove_spec_geometry(
            arrays=array,
            shift_dict=shift_dict,
            scale_dict=scale_dict,
            reference_wavelength_axis=reference_wave_axis,
        )
    )

    for g in range(num_groups):
        rectified_group_array = task.group_id_get_data(data=rectified_array, group_id=g)
        raw_group_array = task.group_id_get_data(data=array, group_id=g)
        # The spatial shape isn't affecting by padding
        assert rectified_group_array.shape[0] == raw_group_array.shape[0]

        nonnan_idx = ~np.isnan(rectified_group_array)
        # The number of true data elements remains the same
        assert rectified_group_array[nonnan_idx].size == raw_group_array.size
        # The values aren't changed
        assert np.all(rectified_group_array[nonnan_idx] == g * 100)


def test_shift_and_scale(task_with_corrections_mixin):
    """
    Given: A spectrum
    When: Shifting and scaling it
    Then: The spectrum is shifted and scaled correctly
    """
    mu = 500.0
    FWHM = 50.0
    x = np.arange(1000.0)
    spectrum = gaussian(x, mu=mu, FWHM=FWHM)

    shift = 44.0
    scale = 1.1

    task = task_with_corrections_mixin
    output_spectrum = task.corrections_shift_and_scale_spectrum(
        spectrum=spectrum, shift=shift, scale=scale
    )

    new_peak = np.nanargmax(output_spectrum)
    assert new_peak == (mu * scale) + shift

    new_FWHM = np.where(output_spectrum > np.nanmax(output_spectrum) * 0.5)[0].size
    # Allow a 2px slop because we're dealing pixel index values as a proxy for FWHM
    assert abs(new_FWHM - FWHM * scale) < 2
