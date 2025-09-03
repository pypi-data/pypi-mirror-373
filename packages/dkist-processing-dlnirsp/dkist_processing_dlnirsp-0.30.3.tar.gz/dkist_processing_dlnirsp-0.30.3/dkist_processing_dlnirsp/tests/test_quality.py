import numpy as np
import pytest
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.json import json_decoder
from dkist_processing_common.models.task_name import TaskName

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks.quality_metrics import DlnirspL0QualityMetrics
from dkist_processing_dlnirsp.tasks.quality_metrics import DlnirspL1QualityMetrics
from dkist_processing_dlnirsp.tests.conftest import CalibratedHeaders
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingConstants
from dkist_processing_dlnirsp.tests.conftest import tag_on_modstate
from dkist_processing_dlnirsp.tests.conftest import write_calibrated_frames_to_task
from dkist_processing_dlnirsp.tests.conftest import write_lamp_gain_frames_to_task
from dkist_processing_dlnirsp.tests.conftest import write_solar_gain_frames_to_task


def make_infy_3D_data(frame: CalibratedHeaders) -> np.ndarray:
    # Data with some inf values. `np.nanstd` return NaN if there are any infs
    shape = frame.array_shape
    data = np.random.random(shape)

    inf_idx = np.where(data < 0.333)  # Roughly 1/3 of the data array
    data[inf_idx] = np.inf

    return data


@pytest.fixture
def quality_l0_task(recipe_run_id, is_polarimetric, link_constants_db, tmp_path):
    constants = DlnirspTestingConstants(
        NUM_MODSTATES=8 if is_polarimetric else 1,
        POLARIMETER_MODE="Full Stokes" if is_polarimetric else "Stokes I",
    )
    link_constants_db(recipe_run_id, constants)

    with DlnirspL0QualityMetrics(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)

        yield task
        task._purge()


@pytest.fixture
def quality_l1_task(recipe_run_id, is_polarimetric, link_constants_db, tmp_path):
    num_mosaics = 2
    num_X_tiles = 2
    num_Y_tiles = 2
    constants = DlnirspTestingConstants(
        NUM_MODSTATES=8 if is_polarimetric else 1,
        POLARIMETER_MODE="Full Stokes" if is_polarimetric else "Stokes I",
        NUM_MOSAIC_REPEATS=num_mosaics,
        NUM_MOSAIC_TILES_X=num_X_tiles,
        NUM_MOSAIC_TILES_Y=num_Y_tiles,
    )
    link_constants_db(recipe_run_id, constants)

    with DlnirspL1QualityMetrics(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)

        yield task, num_mosaics, num_X_tiles, num_Y_tiles
        task._purge()


@pytest.fixture
def l0_task_types_and_writers():
    return [
        (TaskName.lamp_gain.value, write_lamp_gain_frames_to_task),
        (TaskName.solar_gain.value, write_solar_gain_frames_to_task),
    ]


@pytest.fixture
def metric_names():
    return ["FRAME_RMS", "FRAME_AVERAGE"]


@pytest.fixture
def write_l0_data_to_task(l0_task_types_and_writers, is_polarimetric):
    def writer(task):
        for task_type, task_writer in l0_task_types_and_writers:
            task_writer(
                task=task,
                num_modstates=8 if is_polarimetric else 1,
                array_shape=(3, 3),
                tags=[DlnirspTag.task(task_type), DlnirspTag.linearized_frame()],
                tag_func=tag_on_modstate,
            )

    return writer


@pytest.mark.parametrize(
    "is_polarimetric",
    [pytest.param(True, id="polarimetric"), pytest.param(False, id="spectrographic")],
)
def test_qualiy_l0_task(
    quality_l0_task, is_polarimetric, write_l0_data_to_task, l0_task_types_and_writers, metric_names
):
    """
    Given: A quality L0 task and some linearized data
    When: Calling the task
    Then: The expected type and number of quality metric files is written
    """
    task = quality_l0_task

    write_l0_data_to_task(task)

    task()

    for metric_name in metric_names:
        for task_type, _ in l0_task_types_and_writers:
            quality_files = list(
                task.read(
                    tags=[DlnirspTag.quality_task(task_type), DlnirspTag.quality(metric_name)]
                )
            )
            assert len(quality_files) == task.constants.num_modstates
            for f in quality_files:
                assert f.exists()


@pytest.mark.parametrize(
    "is_polarimetric",
    [pytest.param(True, id="polarimetric"), pytest.param(False, id="spectrographic")],
)
def test_qualiy_l1_task(
    quality_l1_task,
    is_polarimetric,
):
    """
    Given: A DlnirspL1QualityMetrics task with some OUTPUT frames
    When: Running the task
    Then: The correct files are produced and they have the expected amount of data
    """
    task, num_mosaics, num_X_tiles, num_Y_tiles = quality_l1_task

    num_l1_frames = write_calibrated_frames_to_task(
        task=task,
        num_mosaics=num_mosaics,
        num_X_tiles=num_X_tiles,
        num_Y_tiles=num_Y_tiles,
        is_polarimetric=is_polarimetric,
        array_shape=(200, 20, 20),
        data_func=make_infy_3D_data,
    )
    task()

    stokes_params = ["I"]
    if is_polarimetric:
        stokes_params += ["Q", "U", "V"]

    for stokes in stokes_params:
        sensitivity_data = list(
            task.read(
                tags=[DlnirspTag.quality("SENSITIVITY"), DlnirspTag.stokes(stokes)],
                decoder=json_decoder,
            )
        )
        assert len(sensitivity_data) == 1
        assert (
            len(sensitivity_data[0]["x_values"])
            == len(sensitivity_data[0]["y_values"])
            == num_l1_frames / len(stokes_params)
        )

        noise_data = list(
            task.read(
                tags=[DlnirspTag.quality("NOISE"), DlnirspTag.stokes(stokes)], decoder=json_decoder
            )
        )
        assert len(noise_data) == 1
        assert (
            len(noise_data[0]["x_values"])
            == len(noise_data[0]["y_values"])
            == num_l1_frames / len(stokes_params)
        )
