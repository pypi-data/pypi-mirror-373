import json

import numpy as np
import pytest
from dkist_data_simulator.spec122 import Spec122Dataset
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.models.task_name import TaskName

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks.solar import SolarCalibration
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingConstants
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingParameters
from dkist_processing_dlnirsp.tests.conftest import write_dark_frames_to_task
from dkist_processing_dlnirsp.tests.conftest import write_geometric_calibration_to_task
from dkist_processing_dlnirsp.tests.conftest import write_lamp_gain_frames_to_task
from dkist_processing_dlnirsp.tests.conftest import write_solar_gain_frames_to_task


@pytest.fixture
def dark_signal() -> float:
    return 100.0


@pytest.fixture
def lamp_signal() -> float:
    return 10.0


@pytest.fixture
def solar_signal() -> float:
    return 2000.0


@pytest.fixture
def make_dark_data(dark_signal):
    def make_array(frame: Spec122Dataset):
        shape = frame.array_shape[1:]
        return np.ones(shape) * dark_signal

    return make_array


@pytest.fixture
def make_lamp_data(lamp_signal):
    def make_array(frame: Spec122Dataset):
        shape = frame.array_shape[1:]
        return np.ones(shape) * lamp_signal

    return make_array


@pytest.fixture
def make_solar_data(solar_signal, dark_signal, lamp_signal):
    def make_array(frame: Spec122Dataset):
        shape = frame.array_shape[1:]
        modstate = frame.header()["DLN__015"]
        return (np.ones(shape) * solar_signal + 100 * modstate) * lamp_signal + dark_signal

    return make_array


@pytest.fixture
def shifts_and_scales(
    num_groups,
) -> tuple[dict[int, np.ndarray], dict[int, np.ndarray]]:
    shift_amount = 0.0
    scale_amount = 1.0

    # This length of these arrays just has to be longer than a single group's spatial size
    shift_dict = {g: np.ones(40) * shift_amount for g in range(num_groups)}
    scale_dict = {g: np.ones(40) * scale_amount for g in range(num_groups)}

    return shift_dict, scale_dict


@pytest.fixture
def groups_by_slitbeam(num_groups, num_groups_per_slitbeam, num_slits):
    slit_dict = dict()
    current_even_group = 0
    current_odd_group = 1
    for slitbeam in range(num_slits * 2):
        group_list = []
        for i in range(num_groups_per_slitbeam):
            if slitbeam % 2:
                group_list.append(current_odd_group)
                current_odd_group += 2
            else:
                group_list.append(current_even_group)
                current_even_group += 2
        slit_dict[slitbeam] = group_list

    return slit_dict


@pytest.fixture
def array_grouped_by_slitbeam(
    group_id_array, num_groups_per_slitbeam, groups_by_slitbeam
) -> np.ndarray:
    array = np.zeros(group_id_array.shape)
    for slitbeam, groups_in_slit in groups_by_slitbeam.items():
        for i, g in enumerate(groups_in_slit, start=-1 * (num_groups_per_slitbeam // 2)):
            # Starting at -1 * groups // 2 ensures the median of the whole slitbeam will be equal to the slitbeam number
            idx = np.where(group_id_array == g)
            array[idx] = slitbeam + i

    return array


@pytest.fixture
def solar_task_for_basic_corrections(
    tmp_path,
    recipe_run_id,
    link_constants_db,
    assign_input_dataset_doc_to_task,
    make_dark_data,
    make_lamp_data,
    make_solar_data,
    jband_group_id_array,
    shifts_and_scales,
    constants_class_with_different_num_slits,
    reference_wave_axis,
):
    solar_exp_time = 1.0
    num_modstates = 4
    array_shape = jband_group_id_array.shape
    link_constants_db(
        recipe_run_id=recipe_run_id,
        constants_obj=DlnirspTestingConstants(SOLAR_GAIN_EXPOSURE_TIMES=(solar_exp_time,)),
    )

    with SolarCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        assign_input_dataset_doc_to_task(
            task,
            DlnirspTestingParameters(),
        )
        task.constants = constants_class_with_different_num_slits(
            recipe_run_id=recipe_run_id, task_name="test"
        )
        write_dark_frames_to_task(
            task,
            array_shape=array_shape,
            exp_time_ms=solar_exp_time,
            tags=[
                DlnirspTag.intermediate(),
                DlnirspTag.task_dark(),
                DlnirspTag.exposure_time(solar_exp_time),
            ],
            data_func=make_dark_data,
        )
        write_lamp_gain_frames_to_task(
            task,
            array_shape=array_shape,
            num_modstates=num_modstates,
            exp_time_ms=solar_exp_time,
            tags=[DlnirspTag.intermediate(), DlnirspTag.task_lamp_gain()],
            data_func=make_lamp_data,
        )
        num_solar_frames = write_solar_gain_frames_to_task(
            task,
            array_shape=array_shape,
            num_modstates=num_modstates,
            exp_time_ms=solar_exp_time,
            tags=[
                DlnirspTag.linearized(),
                DlnirspTag.task_solar_gain(),
                DlnirspTag.exposure_time(solar_exp_time),
            ],
            data_func=make_solar_data,
        )
        shift_dict, scale_dict = shifts_and_scales
        write_geometric_calibration_to_task(
            task, shift_dict=shift_dict, scale_dict=scale_dict, wave_axis=reference_wave_axis
        )

        yield task, num_modstates, num_solar_frames
        task._purge()


@pytest.fixture
def solar_task_with_full_corr(
    tmp_path,
    recipe_run_id,
    link_constants_db,
    assign_input_dataset_doc_to_task,
    jband_group_id_array,
    array_grouped_by_slitbeam,
    constants_class_with_different_num_slits,
    num_groups,
    reference_wave_axis,
    write_drifted_group_ids_to_task,
):
    link_constants_db(
        recipe_run_id=recipe_run_id,
        constants_obj=DlnirspTestingConstants(),
    )

    dummy_shifts = {g: np.zeros(40) for g in range(num_groups)}
    dummy_scales = {g: np.ones(40) for g in range(num_groups)}

    with SolarCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        assign_input_dataset_doc_to_task(
            task,
            DlnirspTestingParameters(),
        )
        task.constants = constants_class_with_different_num_slits(
            recipe_run_id=recipe_run_id, task_name="test"
        )
        write_drifted_group_ids_to_task(task)
        write_geometric_calibration_to_task(
            task=task,
            shift_dict=dummy_shifts,
            scale_dict=dummy_scales,
            wave_axis=reference_wave_axis,
        )
        task.write(
            data=next(
                task.corrections_remove_spec_geometry(
                    array_grouped_by_slitbeam,
                    shift_dict=dummy_shifts,
                    scale_dict=dummy_scales,
                    reference_wavelength_axis=reference_wave_axis,
                )
            ),
            tags=[DlnirspTag.intermediate_frame(), DlnirspTag.task("SC_FULL_CORR")],
            encoder=fits_array_encoder,
        )

        yield task
        task._purge()


@pytest.fixture
def solar_task_with_no_data(
    tmp_path,
    recipe_run_id,
    link_constants_db,
    assign_input_dataset_doc_to_task,
    constants_class_with_different_num_slits,
):
    link_constants_db(
        recipe_run_id=recipe_run_id,
        constants_obj=DlnirspTestingConstants(),
    )

    with SolarCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        assign_input_dataset_doc_to_task(
            task,
            DlnirspTestingParameters(),
        )
        task.constants = constants_class_with_different_num_slits(
            recipe_run_id=recipe_run_id, task_name="test"
        )

        yield task
        task._purge()


def test_compute_average_gain(
    solar_task_for_basic_corrections, solar_signal, write_drifted_group_ids_to_task
):
    """
    Given: A SolarCalibration task with associated solar gain, lamp, geometric, and dark frames
    When: Computing a single, average solar gain image
    Then: An array with the correct values is returned
    """
    task, num_modstates, _ = solar_task_for_basic_corrections

    write_drifted_group_ids_to_task(task)

    task.compute_average_corrected_gains()

    tags = [DlnirspTag.intermediate_frame(), DlnirspTag.task("SC_FULL_CORR")]
    arrays = list(task.read(tags=tags, decoder=fits_array_decoder))

    assert len(arrays) == 1
    avg_array = arrays[0]
    assert avg_array.shape == task.rectified_array_shape
    expected_value = np.mean(solar_signal + 100 * np.arange(1, num_modstates + 1))
    np.testing.assert_equal(avg_array[~np.isnan(avg_array)], expected_value)

    dark_only_list = list(
        task.read(tags=[DlnirspTag.intermediate_frame(), DlnirspTag.task("SC_DARK_ONLY")])
    )
    assert len(dark_only_list) == 1
    assert dark_only_list[0].exists()


def test_compute_characteristic_spectra(solar_task_with_full_corr, groups_by_slitbeam):
    """
    Given: A SolarCalibration task with an already-processed average solar gain image
    When: Computing the characteristic spectra
    Then: Each slitbeam has the correct value
    """
    # The averaged solar gain image is organized such that the groups in each slitbeam all have different values
    # (see `array_grouped_by_slitbeam`),
    # but their median is equal to the slitbeam number. Thus, each slitbeam's median is the slitbeam number and
    # the median over all slitbeams is the median of the slitbeam numbers. Because we compute a single char spec
    # over all slitbeams this is the expected value for *all* groups.

    task = solar_task_with_full_corr

    char_spec = task.compute_characteristic_spectra()
    assert char_spec.shape == task.rectified_array_shape
    slitbeam_median = np.nanmedian(list(groups_by_slitbeam.keys()))
    for slitbeam, groups_in_slit in groups_by_slitbeam.items():
        for g in groups_in_slit:
            idx = task.group_id_get_idx(group_id=g, rectified=True)
            rectified_group = char_spec[idx]
            np.testing.assert_equal(rectified_group[~np.isnan(rectified_group)], slitbeam_median)


def test_solar_task_completes(
    solar_task_for_basic_corrections, write_drifted_group_ids_to_task, mocker, fake_gql_client
):
    """
    Given: A SolarCalibration task with necessary starting data
    When: Running the task
    Then: The dang thing runs and produces the expected files
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task, _, num_solar_frames = solar_task_for_basic_corrections

    write_drifted_group_ids_to_task(task)

    task()

    solar_cal_list = list(
        task.read(
            tags=[DlnirspTag.intermediate_frame(), DlnirspTag.task_solar_gain()],
        )
    )
    assert len(solar_cal_list) == 1
    assert solar_cal_list[0].exists()

    quality_files = list(task.read(tags=[DlnirspTag.quality("TASK_TYPES")]))
    assert len(quality_files) == 1
    file = quality_files[0]
    with file.open() as f:
        data = json.load(f)
        assert isinstance(data, dict)
        assert data["task_type"] == TaskName.solar_gain.value
        assert data["total_frames"] == num_solar_frames
        assert data["frames_not_used"] == 0
