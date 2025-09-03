import json

import asdf
import numpy as np
import pytest
from dkist_data_simulator.spec122 import Spec122Dataset
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.models.task_name import TaskName

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks.geometric import GeometricCalibration
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingConstants
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingParameters
from dkist_processing_dlnirsp.tests.conftest import write_dark_frames_to_task
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
def make_basic_geometric_data(solar_signal, dark_signal, lamp_signal):
    def make_array(frame: Spec122Dataset):
        shape = frame.array_shape[1:]
        modstate = frame.header()["DLN__015"]
        return (np.ones(shape) * solar_signal + 100 * modstate) * lamp_signal + dark_signal

    return make_array


@pytest.fixture
def geometric_task_for_basic_corrections(
    tmp_path,
    recipe_run_id,
    link_constants_db,
    assign_input_dataset_doc_to_task,
    make_dark_data,
    make_lamp_data,
    make_basic_geometric_data,
    jband_dispersion_array,
    constants_class_with_different_num_slits,
    write_drifted_group_ids_to_task,
):
    solar_exp_time = 1.0
    num_modstates = 4
    array_shape = jband_dispersion_array.shape
    link_constants_db(
        recipe_run_id=recipe_run_id,
        constants_obj=DlnirspTestingConstants(SOLAR_GAIN_EXPOSURE_TIMES=(solar_exp_time,)),
    )

    with GeometricCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        assign_input_dataset_doc_to_task(task, DlnirspTestingParameters())
        task.constants = constants_class_with_different_num_slits(
            recipe_run_id=recipe_run_id, task_name="test"
        )
        write_drifted_group_ids_to_task(task)
        task.write(
            data=jband_dispersion_array,
            tags=[
                DlnirspTag.intermediate_frame(),
                DlnirspTag.task_drifted_dispersion(),
            ],
            encoder=fits_array_encoder,
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
            data_func=make_basic_geometric_data,
        )

        yield task, num_modstates, num_solar_frames
        task._purge()


def test_compute_average_gain(geometric_task_for_basic_corrections, solar_signal):
    """
    Given: A GeometricCalibration task with associated solar gain and dark frames
    When: Computing a single, average solar gain image
    Then: An array with the correct values is returned
    """
    task, num_modstates, _ = geometric_task_for_basic_corrections

    task.compute_average_corrected_gain()

    tags = [DlnirspTag.intermediate_frame(), DlnirspTag.task_avg_unrectified_solar_gain()]
    arrays = list(task.read(tags=tags, decoder=fits_array_decoder))

    assert len(arrays) == 1
    expected_value = np.mean(solar_signal + 100 * np.arange(1, num_modstates + 1))
    np.testing.assert_equal(arrays[0], expected_value)


def test_compute_reference_dispersion(
    geometric_task_for_basic_corrections, jband_dispersion_array, jband_group_id_array, num_slits
):
    """
    Given: A GeometricCalibration task
    When: Computing the reference dispersion
    Then: The correct value (median of slit with max dispersion) is found
    """
    task, _, _ = geometric_task_for_basic_corrections

    max_slit_value = num_slits - 1  # 0 indexed

    ## See the fixtures in conftest as to why this the expected value
    #
    dispersion_offset = np.nanmean(jband_dispersion_array - (jband_group_id_array * 10))
    # + 0.5 because the even and odd groups are averaged due to an even number of groups across both
    expected_value = (2 + (6 * max_slit_value) + 0.5) * 10 + dispersion_offset

    assert task.get_reference_dispersion(jband_dispersion_array) == expected_value


def test_geometric_task_completes(geometric_task_for_basic_corrections, mocker, fake_gql_client):
    """
    Given: A GeometricCalibration task with some solar gain and dark data
    When: Running the task
    Then: The dang thing completes and the output has the correct form

    This test does NOT check for correctness of the calibration or anything like that. That coverage is provided by
    GROGU tests.
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task, _, num_solar_frames = geometric_task_for_basic_corrections
    task()

    files = list(task.read(tags=[DlnirspTag.intermediate(), DlnirspTag.task_geometric()]))
    assert len(files) == 1
    with asdf.open(files[0], lazy_load=False) as f:
        tree = f.tree
        shift_dict = tree["spectral_shifts"]
        scale_dict = tree["spectral_scales"]
        assert sorted(list(shift_dict.keys())) == sorted(list(scale_dict.keys()))
        for k in shift_dict.keys():
            assert shift_dict[k].shape == scale_dict[k].shape
            assert len(shift_dict[k].shape) == 1

    dispersion_files = list(
        task.read(tags=[DlnirspTag.intermediate(), DlnirspTag.task_dispersion()])
    )
    assert len(dispersion_files) == 1
    with open(dispersion_files[0], "r") as f:
        dispersion = json.load(f)
        assert isinstance(dispersion, float)

    quality_files = list(task.read(tags=[DlnirspTag.quality("TASK_TYPES")]))
    assert len(quality_files) == 1
    file = quality_files[0]
    with file.open() as f:
        data = json.load(f)
        assert isinstance(data, dict)
        assert data["task_type"] == TaskName.geometric.value
        assert data["total_frames"] == num_solar_frames
        assert data["frames_not_used"] == 0
