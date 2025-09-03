import numpy as np
import pytest
from astropy.io import fits
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_array_encoder

from dkist_processing_dlnirsp.models.constants import DlnirspConstants
from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks.dlnirsp_base import DlnirspTaskBase
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingConstants
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingParameters
from dkist_processing_dlnirsp.tests.conftest import FileParameter


class Task(DlnirspTaskBase):
    def run(self) -> None:
        pass


@pytest.fixture
def task_with_group_id(
    recipe_run_id,
    assign_input_dataset_doc_to_task,
    link_constants_db,
    constants_class_with_different_num_slits,
    write_drifted_group_ids_to_task,
    tmp_path,
):
    link_constants_db(
        recipe_run_id=recipe_run_id,
        constants_obj=DlnirspTestingConstants(),
    )
    with Task(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        task.constants = constants_class_with_different_num_slits(
            recipe_run_id=recipe_run_id, task_name="test"
        )
        parameters = DlnirspTestingParameters()
        assign_input_dataset_doc_to_task(task=task, parameters=parameters)
        write_drifted_group_ids_to_task(task)

        yield task
        task._purge()


@pytest.fixture
def non_rect_group_id_array():
    array = np.empty((10, 20)) * np.nan
    array[3:7, 4:12] = 0
    array[2:6, 11:17] = 1

    return array


@pytest.fixture
def non_rect_group_id_file_parameter(non_rect_group_id_array, tmp_path):
    file_path = tmp_path / "non_rect_group_id.fits"
    fits.PrimaryHDU(non_rect_group_id_array).writeto(file_path)

    return FileParameter(param_path=str(file_path))


@pytest.fixture
def task_with_non_rect_group_id_array(
    recipe_run_id,
    assign_input_dataset_doc_to_task,
    link_constants_db,
    non_rect_group_id_array,
    tmp_path,
):
    link_constants_db(recipe_run_id, DlnirspTestingConstants())

    class ConstantsWithSingleSlit(DlnirspConstants):
        @property
        def num_beams(self) -> int:
            return 2

        @property
        def num_slits(self) -> int:
            return 1

    with Task(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        task.constants = ConstantsWithSingleSlit(recipe_run_id=recipe_run_id, task_name="task")
        parameters = DlnirspTestingParameters()
        assign_input_dataset_doc_to_task(task=task, parameters=parameters)
        # Because we need to use a non-rectangular drifted group ID array
        task.write(
            data=non_rect_group_id_array,
            tags=[
                DlnirspTag.intermediate_frame(),
                DlnirspTag.task_drifted_ifu_groups(),
            ],
            encoder=fits_array_encoder,
        )

        yield task
        task._purge()


def test_group_id_mixin(task_with_group_id, array_with_groups, num_groups):
    """
    Given: A task with the GroupIdMixin
    When: Using the mixin to access groups in a data array
    Then: The correct indices and values are returned
    """
    task = task_with_group_id
    array = array_with_groups

    assert task.group_id_num_groups == num_groups
    assert np.all(~np.isnan(array[task.group_id_illuminated_idx]))
    for g in range(num_groups):
        group_array = task.group_id_get_data(data=array, group_id=g)
        assert group_array.shape != array.shape
        assert len(group_array.shape) == 2
        assert np.all(group_array == g * 100)


def test_non_rect_group(task_with_non_rect_group_id_array, non_rect_group_id_array):
    """
    Given: A task with the GroupIdMixin and a IFU ID array that contains non-rectangular groups
    When: Accessing groups in a data array
    Then: The returned groups are rectangular
    """
    task = task_with_non_rect_group_id_array
    array = np.copy(non_rect_group_id_array)
    array[array == 0] = 100.0
    array[array == 1] = 200.0

    num_groups = 2
    for g in range(num_groups):
        group_array, idx = task.group_id_get_data_and_idx(data=array, group_id=g)
        # The spatial shape isn't changed by rectangle-ification
        nump_spatial_px = np.unique(idx[0]).size
        assert group_array.shape[0] == nump_spatial_px


def test_convert_idx_to_2d_slice(task_with_group_id):
    """
    Given: A task with the GroupIdMixin
    When: Converting a tuple of indices to a 2D slice
    Then: The correct slice is returned
    """
    task = task_with_group_id

    spatial_idx = np.array([3, 3, 3, 3, 4, 4, 4, 4])
    spectral_idx = np.array([10, 11, 12, 13, 10, 11, 12, 13])
    idx = (spatial_idx, spectral_idx)

    slices = task.group_id_convert_idx_to_2d_slice(idx)

    assert len(slices) == 2
    assert slices[0].start == 3
    assert slices[0].stop == 5
    assert slices[1].start == 10
    assert slices[1].stop == 14


def test_slitbeam_group_dict(task_with_group_id, num_slits, num_groups_per_slitbeam):
    """
    Given: A task with the GroupIdMixin
    When: Computing the assignment of groups to slitbeams
    Then: Groups are assigned to the correct slit beam
    """
    slitbeam_dict = task_with_group_id.group_id_slitbeam_group_dict
    assert sorted(list(slitbeam_dict.keys())) == list(range(num_slits * 2))

    num_groups_per_slit = num_groups_per_slitbeam * 2
    even_expected = [
        list(range(i, i + num_groups_per_slit, 2)) for i in range(0, 18, num_groups_per_slit)
    ]

    for i, slitbeam in enumerate(range(0, num_slits * 2, 2)):
        assert slitbeam_dict[slitbeam] == even_expected[i]

    odd_expected = [
        list(range(i, i + num_groups_per_slit, 2)) for i in range(1, 18, num_groups_per_slit)
    ]
    for i, slitbeam in enumerate(range(1, num_slits * 2, 2)):
        assert slitbeam_dict[slitbeam] == odd_expected[i]
