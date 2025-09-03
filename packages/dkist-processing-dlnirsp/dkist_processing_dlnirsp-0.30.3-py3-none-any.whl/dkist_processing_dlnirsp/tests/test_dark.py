import json

import numpy as np
import pytest
from astropy.io import fits
from dkist_data_simulator.spec122 import Spec122Dataset
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.task_name import TaskName

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks.dark import DarkCalibration
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingConstants
from dkist_processing_dlnirsp.tests.conftest import write_dark_frames_to_task


def make_data_exp_time_value(frame: Spec122Dataset) -> np.ndarray:
    shape = frame.array_shape[1:]
    value = frame.header()["CAM__004"]
    return np.ones(shape) * value


@pytest.fixture
def dark_task(tmp_path, recipe_run_id, link_constants_db):
    lamp_exp_time = 1.0
    solar_exp_time = 2.0
    polcal_exp_time = 3.0
    observe_exp_time = 4.0
    unused_exp_time = 5.0
    constants = DlnirspTestingConstants(
        LAMP_GAIN_EXPOSURE_TIMES=(lamp_exp_time,),
        SOLAR_GAIN_EXPOSURE_TIMES=(solar_exp_time,),
        POLCAL_EXPOSURE_TIMES=(polcal_exp_time,),
        OBSERVE_EXPOSURE_TIMES=(observe_exp_time,),
        POLARIMETER_MODE="Full Stokes",
    )

    link_constants_db(recipe_run_id=recipe_run_id, constants_obj=constants)

    with DarkCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        for exp in [
            lamp_exp_time,
            solar_exp_time,
            observe_exp_time,
            unused_exp_time,
        ]:
            num_frames_per_exp = write_dark_frames_to_task(
                task,
                exp_time_ms=exp,
                data_func=make_data_exp_time_value,
                tags=[
                    DlnirspTag.linearized(),
                    DlnirspTag.task_dark(),
                    DlnirspTag.exposure_time(exp),
                ],
            )

        yield task, lamp_exp_time, solar_exp_time, observe_exp_time, unused_exp_time, num_frames_per_exp
        task._purge()


def test_dark_calibration_task(dark_task, mocker, fake_gql_client):
    """
    Given: A DarkCalibrationTask with tagged DARK frames from a variety of exposure times
    When: Running the task
    Then: The correct darks are made and any dark-only exposure times are not made
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    (
        task,
        lamp_exp_time,
        solar_exp_time,
        observe_exp_time,
        unused_exp_time,
        num_frames_per_exp,
    ) = dark_task

    task()

    for exp in [lamp_exp_time, solar_exp_time, observe_exp_time]:
        dark_list = list(
            task.read(
                tags=[DlnirspTag.intermediate_frame_dark(exposure_time=exp)],
            )
        )
        assert len(dark_list) == 1
        assert np.mean(fits.open(dark_list[0])[0].data) == exp

    unused_dark_list = list(
        task.read(
            tags=[DlnirspTag.intermediate_frame_dark(exposure_time=unused_exp_time)],
        )
    )
    assert len(unused_dark_list) == 0

    quality_files = list(task.read(tags=[DlnirspTag.quality("TASK_TYPES")]))
    assert len(quality_files) == 1
    file = quality_files[0]
    with file.open() as f:
        data = json.load(f)
        assert isinstance(data, dict)
        assert data["task_type"] == TaskName.dark.value
        assert data["total_frames"] == num_frames_per_exp * 4  # For lamp, solar, obs, and unused
        assert data["frames_not_used"] == num_frames_per_exp
