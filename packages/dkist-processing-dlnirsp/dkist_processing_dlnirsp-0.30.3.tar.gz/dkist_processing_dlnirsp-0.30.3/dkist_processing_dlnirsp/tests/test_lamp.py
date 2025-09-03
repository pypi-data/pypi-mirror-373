import json

import numpy as np
import pytest
from astropy.io import fits
from dkist_data_simulator.spec122 import Spec122Dataset
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.task_name import TaskName

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks.lamp import LampCalibration
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingConstants
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingParameters
from dkist_processing_dlnirsp.tests.conftest import tag_on_modstate
from dkist_processing_dlnirsp.tests.conftest import write_dark_frames_to_task
from dkist_processing_dlnirsp.tests.conftest import write_lamp_gain_frames_to_task


@pytest.fixture
def dark_signal() -> float:
    return 100.0


@pytest.fixture
def lamp_signal() -> float:
    return 2000.0


@pytest.fixture
def make_dark_data(dark_signal):
    def make_array(frame: Spec122Dataset):
        shape = frame.array_shape[1:]
        return np.ones(shape) * dark_signal

    return make_array


@pytest.fixture
def make_lamp_data(lamp_signal, dark_signal):
    def make_array(frame: Spec122Dataset):
        shape = frame.array_shape[1:]
        return (np.ones(shape) * lamp_signal) + dark_signal

    return make_array


@pytest.fixture
def lamp_task(
    tmp_path,
    recipe_run_id,
    link_constants_db,
    assign_input_dataset_doc_to_task,
    make_dark_data,
    make_lamp_data,
):
    lamp_exp_time = 1.0
    link_constants_db(
        recipe_run_id=recipe_run_id,
        constants_obj=DlnirspTestingConstants(LAMP_GAIN_EXPOSURE_TIMES=(lamp_exp_time,)),
    )

    with LampCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        assign_input_dataset_doc_to_task(task, DlnirspTestingParameters())
        write_dark_frames_to_task(
            task,
            exp_time_ms=lamp_exp_time,
            tags=[
                DlnirspTag.intermediate(),
                DlnirspTag.task_dark(),
                DlnirspTag.exposure_time(lamp_exp_time),
            ],
            data_func=make_dark_data,
        )
        num_lamp_frames = write_lamp_gain_frames_to_task(
            task,
            exp_time_ms=lamp_exp_time,
            tags=[
                DlnirspTag.linearized(),
                DlnirspTag.task_lamp_gain(),
                DlnirspTag.exposure_time(lamp_exp_time),
            ],
            data_func=make_lamp_data,
            tag_func=tag_on_modstate,
        )

        yield task, lamp_exp_time, num_lamp_frames
        task._purge()


def test_lamp_calibration_task(lamp_task, lamp_signal, mocker, fake_gql_client):
    """
    Given: A LampCalibration task with tagged linearized and intermediate frames
    When: Running the LampCalibration task
    Then: Lamp gain objects with the correct values are made
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task, lamp_exp_time, num_lamp_frames = lamp_task

    task()

    file_list = list(
        task.read(
            tags=[
                DlnirspTag.intermediate_frame(),
                DlnirspTag.task_lamp_gain(),
            ]
        )
    )

    assert len(file_list) == 1
    data = fits.open(file_list[0])[0].data
    assert np.allclose(data, lamp_signal)

    quality_files = list(task.read(tags=[DlnirspTag.quality("TASK_TYPES")]))
    assert len(quality_files) == 1
    file = quality_files[0]
    with file.open() as f:
        data = json.load(f)
        assert isinstance(data, dict)
        assert data["task_type"] == TaskName.lamp_gain.value
        assert data["total_frames"] == num_lamp_frames
        assert data["frames_not_used"] == 0
