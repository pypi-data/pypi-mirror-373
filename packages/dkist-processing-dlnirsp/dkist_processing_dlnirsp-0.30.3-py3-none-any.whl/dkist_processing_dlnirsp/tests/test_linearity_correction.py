import re
from dataclasses import dataclass
from functools import partial
from typing import Literal

import numpy as np
import pytest
from astropy.io import fits
from astropy.time import Time
from astropy.time import TimeDelta
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.fits_access import FitsAccessBase
from dkist_processing_common.models.task_name import TaskName
from dkist_service_configuration.logging import logger
from scipy.optimize import fsolve

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks import LinearityCorrection
from dkist_processing_dlnirsp.tests.conftest import AbortedRampHeaders
from dkist_processing_dlnirsp.tests.conftest import BadNumFramesPerRampHeaders
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingConstants
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingParameters
from dkist_processing_dlnirsp.tests.conftest import RawRampHeaders
from dkist_processing_dlnirsp.tests.conftest import SimpleModulatedHeaders
from dkist_processing_dlnirsp.tests.conftest import write_frames_to_task


@pytest.fixture
def raw_ramp_array_shape() -> tuple[int, int, int]:
    return (1, 2, 2)


@pytest.fixture
def discrete_slopes(raw_ramp_array_shape) -> np.ndarray:
    return np.random.random(raw_ramp_array_shape) * 100.0


@pytest.fixture
def discrete_intercepts(raw_ramp_array_shape) -> np.ndarray:
    return np.random.random(raw_ramp_array_shape) * 10.0


@pytest.fixture
def linearity_correction_task(recipe_run_id, tmp_path, link_constants_db):
    link_constants_db(
        recipe_run_id=recipe_run_id,
        constants_obj=DlnirspTestingConstants(),
    )

    with LinearityCorrection(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(recipe_run_id=recipe_run_id, scratch_base_path=tmp_path)

        yield task
        task._purge()


def write_ramps_to_task(
    task,
    num_ramps: int,
    arm_id: str,
    num_reset: int = 4,
    num_coadd: int = 1,
    num_read: int = 3,
    array_shape: tuple[int, int, int] = (1, 2, 2),
    camera_readout_mode: Literal["UpTheRamp", "SubFrame"] = "UpTheRamp",
    modulator_spin_mode: Literal["Continuous", "Discrete"] = "Continuous",
    slopes: np.ndarray | None = None,
    intercepts: np.ndarray | None = None,
):
    start_date = "2024-04-20T16:20:00.00"
    ramp_length_sec = 3.14159
    bias_value = 5.0
    num_line = 2

    start_date_obj = Time(start_date)
    time_delta = TimeDelta(ramp_length_sec, format="sec")
    expected_obs_time_list = [(start_date_obj + time_delta * i).fits for i in range(num_ramps)]

    poly_coeffs = task.parameters.linearization_poly_coeffs
    correction_poly = np.poly1d(poly_coeffs)

    match modulator_spin_mode:
        case "Continuous":
            ramp_data_func = partial(
                make_continuous_ramp_data, bias=bias_value, correction_poly=correction_poly
            )
        case "Discrete":
            ramp_data_func = partial(
                make_discrete_ramp_data,
                slopes=slopes,
                intercepts=intercepts,
                bias=bias_value,
                correction_poly=correction_poly,
            )
        case _:
            raise ValueError(f"Don't know how to make data for {modulator_spin_mode = }")

    dataset = RawRampHeaders(
        array_shape=array_shape,
        num_ramps=num_ramps,
        num_line=num_line,
        num_read=num_read,
        num_reset=num_reset,
        num_coadd=num_coadd,
        ramp_length_sec=ramp_length_sec,
        start_date=start_date,
        arm_id=arm_id,
        camera_readout_mode=camera_readout_mode,
        modulator_spin_mode=modulator_spin_mode,
    )

    write_frames_to_task(
        task=task,
        frame_generator=dataset,
        data_func=ramp_data_func,
        extra_tags=[DlnirspTag.input()],
        tag_func=tag_on_time_obs,
    )

    return expected_obs_time_list, ramp_length_sec, bias_value, num_line, num_read, num_reset


def write_skipable_ramps_to_task(task):

    # Write one good frame
    good_start_date = write_ramps_to_task(task, num_ramps=1, arm_id="JBand")[0][0]

    ramp_data_func = partial(make_continuous_ramp_data, bias=1.0)

    # Write one aborted ramp
    aborted_start_date = "2024-06-28T11:55:30.230"  # Needs to be different than the start_date in `write_ramps_to_task`
    aborted_generator = AbortedRampHeaders(
        array_shape=(1, 2, 2),
        num_line=2,
        num_read=3,
        num_reset=4,
        start_date=aborted_start_date,
    )

    write_frames_to_task(
        task,
        frame_generator=aborted_generator,
        data_func=ramp_data_func,
        extra_tags=[DlnirspTag.input()],
        tag_func=tag_on_time_obs,
    )

    # Write one ramp with weird header values
    bad_ramp_start_date = "2024-03-14T15:55:30.231"  # Needs to be different than the start_date in `write_ramps_to_task`
    bad_ramp_generator = BadNumFramesPerRampHeaders(
        array_shape=(1, 2, 2),
        num_line=2,
        num_read=3,
        num_reset=4,
        start_date=bad_ramp_start_date,
    )

    write_frames_to_task(
        task,
        frame_generator=bad_ramp_generator,
        data_func=ramp_data_func,
        extra_tags=[DlnirspTag.input()],
        tag_func=tag_on_time_obs,
    )

    return good_start_date, aborted_start_date, bad_ramp_start_date


def make_continuous_ramp_data(
    frame: RawRampHeaders, bias: float = 0.0, correction_poly: np.poly1d = np.poly1d([1])
) -> np.ndarray:
    shape = frame.array_shape
    if frame.frame_in_coadd < frame.num_line - 1:
        # Biases before the last bias. We never use these, so they have trash values
        true_value = np.nan

    elif frame.frame_in_coadd == frame.num_line - 1:
        # The last bias. This is the one that gets used so we control its value.
        true_value = bias

    else:
        true_value = (
            (frame.current_ramp + 1) * 100.0
            + (frame.frame_in_coadd + 1) * 10
            + frame.current_coadd_in_ramp
            + 1
        )

    # We want the polynomial corrected frame value to equal `true_value`, but the value of the polynomial will change
    # depending on the "raw" value (`value`). So here we solve for the raw value numerically.
    # Basically, solve for x such that `x / poly(x) == true_value`
    fit_func = lambda x: x / correction_poly(x) - true_value
    value = fsolve(fit_func, true_value)

    return np.ones(shape) * value


def make_discrete_ramp_data(
    frame: RawRampHeaders,
    slopes: np.ndarray,
    intercepts: np.ndarray,
    bias: float,
    correction_poly: np.poly1d = np.poly1d([1]),
):
    shape = frame.array_shape
    if shape != slopes.shape or shape != intercepts.shape:
        raise ValueError(
            f"Dataset shape ({shape}) doesn't match the slopes ({slopes.shape}) or intercepts ({intercepts.shape}) shape"
        )

    if frame.frame_in_coadd < frame.num_line - 1:
        # Biases before the last bias. We never use these, so they have trash values
        true_array = np.ones(shape) * np.nan

    elif frame.frame_in_coadd == frame.num_line - 1:
        # The last bias. This is the one that gets used so we control its value.
        true_array = np.ones(shape) * bias

    else:
        read_num = frame.frame_in_coadd - frame.num_line + 1
        slop_modifier = (frame.current_ramp + 1) * 10 * (frame.current_coadd_in_ramp + 1)
        true_array = (read_num * slopes * slop_modifier + intercepts) + bias

    # We want the polynomial corrected frame value to equal `true_array`, but the value of the polynomial will change
    # depending on the "raw" value (`array`). So here we solve for the raw value numerically.
    # Basically, solve for x such that `x / poly(x) == true_array`
    flat_true_array = true_array.reshape(np.prod(shape))
    flat_array = np.empty_like(flat_true_array)
    for i in range(flat_true_array.size):
        fit_func = lambda x: x / correction_poly(x) - flat_true_array[i]
        flat_array[i] = fsolve(fit_func, flat_true_array[i])
    array = flat_array.reshape(shape)

    return array


def write_vis_inputs_to_task(task, num_frames):
    dataset = SimpleModulatedHeaders(
        num_modstates=num_frames,
        array_shape=(1, 2, 2),
        task=TaskName.dark.value,
        exp_time_ms=10.0,
        arm_id="VIS",
    )

    write_frames_to_task(
        task=task,
        frame_generator=dataset,
        data_func=make_vis_data,
        extra_tags=[DlnirspTag.input()],
        tag_func=tag_on_time_obs,
    )


def make_vis_data(frame: SimpleModulatedHeaders):
    modstate = frame.header()["DLN__015"]
    return np.ones(frame.array_shape) * modstate


def tag_on_time_obs(frame: RawRampHeaders):
    time_obs = frame.header()["DATE-OBS"]
    return [DlnirspTag.time_obs(time_obs)]


def up_the_ramp_continuous_expected_value(
    *,
    ramp_num: int,
    num_line: int,
    num_read: int,
    bias_value: float,
    expected_avg_coadd_value: float,
    **unused_args,
) -> float:
    # See `make_continuous_ramp_data` for where this comes from - we don't include num_reset because we only care about the last read frame
    return ramp_num * 100 + (num_line + num_read) * 10 - bias_value + expected_avg_coadd_value


def subframe_expected_value(
    *, ramp_num: int, num_line: int, num_read: int, expected_avg_coadd_value: float, **unused_args
) -> float:
    # See `make_discrete_ramp_data` for where this comes from
    # Unlike the continuous data methods, the discrete data already includes the bias, so we don't need
    # to subtract it here
    return ramp_num * 100 + (num_line + num_read) * 10 + expected_avg_coadd_value


def discrete_expected_value(
    *,
    ramp_num: int,
    num_read: int,
    expected_avg_coadd_value: float,
    slopes: np.ndarray,
    **unused_args,
):
    return num_read * slopes[0] * ramp_num * 10 * expected_avg_coadd_value


@dataclass
class DummyRampFitsAccess:
    """Just a class that has the two properties that are checked during ramp validation."""

    num_frames_in_ramp: int = 2
    camera_sample_sequence: str = "1line,1read"
    ip_task_type: str = "TASK"
    camera_readout_mode: str = "UpTheRamp"
    modulator_spin_mode: str = "Continuous"


class EmptyFitsAccess(FitsAccessBase):
    """With no stuff so we can just stuff data in an object."""

    pass


@pytest.mark.parametrize("arm_id", [pytest.param("JBand"), pytest.param("HBand")])
@pytest.mark.parametrize(
    "camera_readout_mode, modulator_spin_mode, expected_value_func",
    [
        pytest.param(
            "UpTheRamp",
            "Continuous",
            up_the_ramp_continuous_expected_value,
            id="UpTheRampContinuous",
        ),
        pytest.param("SubFrame", "Continuous", subframe_expected_value, id="SubFrame"),
        pytest.param("UpTheRamp", "Discrete", discrete_expected_value, id="UpTheRampDiscrete"),
    ],
)
@pytest.mark.parametrize(
    "num_reset", [pytest.param(0, id="no_resets"), pytest.param(4, id="with_resets")]
)
@pytest.mark.parametrize(
    "num_coadd", [pytest.param(1, id="1_coadd"), pytest.param(3, id="3_coadds")]
)
def test_linearity_correction(
    linearity_correction_task,
    link_constants_db,
    assign_input_dataset_doc_to_task,
    arm_id,
    mocker,
    num_reset,
    num_coadd,
    camera_readout_mode,
    modulator_spin_mode,
    expected_value_func,
    raw_ramp_array_shape,
    discrete_slopes,
    discrete_intercepts,
    fake_gql_client,
):
    """
    Given: A `LinearityCorrection` task and some raw INPUT frames
    When: Linearizing the data
    Then: The correct number of frames are produced and they have the expected linearized values
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    num_ramps = 3
    task = linearity_correction_task
    assign_input_dataset_doc_to_task(task, DlnirspTestingParameters(), arm_id=arm_id)
    (
        expected_time_obs_list,
        ramp_length_sec,
        bias_value,
        num_line,
        num_read,
        num_reset,
    ) = write_ramps_to_task(
        task,
        num_ramps=num_ramps,
        arm_id=arm_id,
        num_reset=num_reset,
        num_coadd=num_coadd,
        array_shape=raw_ramp_array_shape,
        modulator_spin_mode=modulator_spin_mode,
        camera_readout_mode=camera_readout_mode,
        slopes=discrete_slopes,
        intercepts=discrete_intercepts,
    )

    # Need to update now that we know the expected_time_obs list and arm_id
    link_constants_db(
        task.recipe_run_id,
        DlnirspTestingConstants(
            TIME_OBS_LIST=tuple(expected_time_obs_list),
            ARM_ID=arm_id,
        ),
    )

    task()

    expected_avg_coadd_value = float(np.mean(np.arange(num_coadd) + 1))
    expected_total_exp = ramp_length_sec / num_coadd * 1000
    expected_NDR_exp = ramp_length_sec / num_coadd / num_read * 1000

    assert len(list(task.read([DlnirspTag.linearized_frame()]))) == num_ramps
    for ramp_num, time_obs in enumerate(expected_time_obs_list, start=1):
        files = list(task.read([DlnirspTag.linearized_frame(), DlnirspTag.time_obs(time_obs)]))
        assert len(files) == 1
        expected_value = expected_value_func(
            ramp_num=ramp_num,
            num_line=num_line,
            num_read=num_read,
            bias_value=bias_value,
            expected_avg_coadd_value=expected_avg_coadd_value,
            slopes=discrete_slopes,
        )
        data = fits.getdata(files[0])
        np.testing.assert_allclose(data, expected_value, rtol=1e-13)

        header = fits.getheader(files[0])
        assert header["XPOSURE"] == expected_total_exp
        assert header["TEXPOSUR"] == expected_NDR_exp


def test_VIS_linearity_correction(
    linearity_correction_task, link_constants_db, mocker, fake_gql_client
):
    """
    Given: A `LinearityCorrection` task and some raw visible INPUT frames
    When: Linearizing the data
    Then: The visible frames are re-tagged as LINEARIZED and their data are un-changed
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    num_frames = 3
    task = linearity_correction_task
    write_vis_inputs_to_task(task, num_frames=num_frames)

    link_constants_db(task.recipe_run_id, DlnirspTestingConstants(ARM_ID="VIS"))
    task()

    linearized_frame_list = list(task.read([DlnirspTag.linearized_frame()]))
    assert len(linearized_frame_list) == num_frames

    # All INPUT frames should be retagged as LINEARIZED
    assert len(list(task.read([DlnirspTag.frame(), DlnirspTag.input()]))) == 0

    for path in linearized_frame_list:
        hdu = fits.open(path)[0]
        modstate = hdu.header["DLN__015"]  # See `make_vis_data`
        np.testing.assert_array_equal(hdu.data, modstate)


@pytest.mark.parametrize(
    "camera_sequence, expected_results",
    [
        pytest.param("2line,3read", [[2, 3]], id="2line,3read"),
        pytest.param("14line,3read,23line", [[14, 3]], id="14line,3read,23line"),
        pytest.param(
            "3line,34read,3line,34read", [[3, 34], [3, 34]], id="3line,34read,3line,34read"
        ),
        pytest.param(
            "1line,2read,1line,2read,45line",
            [[1, 2], [1, 2]],
            id="1line,2read,1line,2read,45line",
        ),
        pytest.param(
            "1line,2read,1line,2read,1line,2read,1line,2read",
            [[1, 2], [1, 2], [1, 2], [1, 2]],
            id="1line,2read,1line,2read,1line,2read,1line,2read",
        ),
        pytest.param(
            "3line,2read,3line,2read,3line,2read,1line",
            [[3, 2], [3, 2], [3, 2]],
            id="3line,2read,3line,2read,3line,2read,1line",
        ),
    ],
)
def test_parse_camera_sample_sequence(linearity_correction_task, camera_sequence, expected_results):
    """
    Given: A `LinearityCorrection` task and a camera sample sequence
    When: Parsing the sample sequence into line-read-line numbers per coadd
    Then: The correct results is returned
    """
    assert (
        linearity_correction_task.parse_camera_sample_sequence(camera_sequence) == expected_results
    )


def test_linearity_correction_with_invalid_ramps(
    linearity_correction_task,
    link_constants_db,
    assign_input_dataset_doc_to_task,
    mocker,
    fake_gql_client,
):
    """
    Given: A `LinearityCorrection` task and raw INPUT frames that include 2 invalid ramps
    When: Linearizing the data
    Then: The invalid ramps are not linearized
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task = linearity_correction_task
    assign_input_dataset_doc_to_task(task, DlnirspTestingParameters())
    good_time, aborted_time, bad_time = write_skipable_ramps_to_task(task)
    time_obs_list = [good_time, aborted_time, bad_time]

    # Need to update again now that we know the time_obs_list
    link_constants_db(
        task.recipe_run_id, DlnirspTestingConstants(TIME_OBS_LIST=tuple(time_obs_list))
    )

    task()

    assert len(list(task.read([DlnirspTag.linearized_frame()]))) == 1
    assert (
        len(list(task.read([DlnirspTag.linearized_frame(), DlnirspTag.time_obs(good_time)]))) == 1
    )
    assert (
        len(list(task.read([DlnirspTag.linearized_frame(), DlnirspTag.time_obs(aborted_time)])))
        == 0
    )
    assert len(list(task.read([DlnirspTag.linearized_frame(), DlnirspTag.time_obs(bad_time)]))) == 0


@pytest.mark.parametrize(
    "ramp_list, valid, message",
    [
        pytest.param(
            [
                DummyRampFitsAccess(num_frames_in_ramp=2, camera_sample_sequence=""),
                DummyRampFitsAccess(num_frames_in_ramp=3, camera_sample_sequence=""),
            ],
            False,
            "Not all frames have the same FRAMES_IN_RAMP value",
            id="bad_num_frames_set",
        ),
        pytest.param(
            [DummyRampFitsAccess(num_frames_in_ramp=4, camera_sample_sequence="")],
            False,
            "Missing some ramp frames. Expected 4 from header value",
            id="wrong_number_from_header",
        ),
        pytest.param(
            [
                DummyRampFitsAccess(num_frames_in_ramp=2, camera_sample_sequence="1line,2read"),
                DummyRampFitsAccess(num_frames_in_ramp=2, camera_sample_sequence="1line,3read"),
            ],
            False,
            "Not all frames have the same camera sample sequence",
            id="bad_sequence_set",
        ),
        pytest.param(
            [
                DummyRampFitsAccess(
                    num_frames_in_ramp=1, camera_sample_sequence="1line,2read,1line,3read,5line"
                )
            ],
            False,
            "Sample sequence is not the same for all coadds.",
            id="multi_coadd_seq",
        ),
        pytest.param(
            [
                DummyRampFitsAccess(
                    num_frames_in_ramp=2, camera_sample_sequence="1line,2read,1line,2read,4line"
                ),
                DummyRampFitsAccess(
                    num_frames_in_ramp=2, camera_sample_sequence="1line,2read,1line,2read,4line"
                ),
            ],
            False,
            "Missing some ramp frames. Expected 10 from sample sequence",
            id="wrong_number_from_seq",
        ),
        pytest.param(
            [
                DummyRampFitsAccess(
                    num_frames_in_ramp=1,
                    camera_sample_sequence="1line,2read,3line,1line,2read,3line",
                ),
            ],
            False,
            "Malformed camera sample sequence",
            id="bad_cam_seq",
        ),
        pytest.param(
            [
                DummyRampFitsAccess(camera_readout_mode="UpTheRamp"),
                DummyRampFitsAccess(camera_readout_mode="SubFrame"),
            ],
            False,
            "Not all frames have the same CAMERA_READOUT_MODE value",
            id="multi_cam_readout",
        ),
        pytest.param(
            [DummyRampFitsAccess(num_frames_in_ramp=1, camera_readout_mode="Bad")],
            False,
            "Camera readout mode Bad is unknown",
            id="bad_readout_mode",
        ),
        pytest.param(
            [
                DummyRampFitsAccess(modulator_spin_mode="Continuous"),
                DummyRampFitsAccess(modulator_spin_mode="Discrete"),
            ],
            False,
            "Not all frames have the same MODULATOR_SPIN_MODE value",
            id="multi_mod_spin",
        ),
        pytest.param(
            [DummyRampFitsAccess(num_frames_in_ramp=1, modulator_spin_mode="Bad")],
            False,
            "Modulator spin mode Bad is unknown",
            id="bad_spin_mode",
        ),
        pytest.param(
            [
                DummyRampFitsAccess(num_frames_in_ramp=2, camera_sample_sequence="1line,1read"),
                DummyRampFitsAccess(num_frames_in_ramp=2, camera_sample_sequence="1line,1read"),
            ],
            True,
            "",
            id="valid",
        ),
    ],
)
def test_is_ramp_valid(linearity_correction_task, ramp_list, valid, message, caplog):
    """
    Given: A list of ramp fits access objects
    When: Testing the ramp validity with `is_ramp_valid`
    Then: The correct answer is returned
    """
    logger.add(caplog.handler)
    assert linearity_correction_task.is_ramp_valid(ramp_list) is valid
    if not valid:
        assert re.search(message, caplog.text)


def test_correction_polynomial(linearity_correction_task, assign_input_dataset_doc_to_task):
    """
    Given: A LinearitCorrection task with correction polynomial coefficients and a data array where one pixel is larger
      than the saturation limit
    When: Applying the correction polynomial
    Then: The non-staurated pixels are correctly corrected and the saturated pixel is set to NaN
    """
    task = linearity_correction_task
    arm = task.constants.arm_id
    poly_coeffs = [1.2e-9, 0.023]
    poly = np.poly1d(poly_coeffs)
    param_dict = {f"dlnirsp_linearization_poly_coeffs_{arm.casefold()}": poly_coeffs}
    assign_input_dataset_doc_to_task(
        task, parameters=DlnirspTestingParameters(**param_dict), arm_id=arm
    )
    saturation_limit = task.parameters.linearization_saturation_threshold

    # Show that the *true*/corrected value can be larger than the saturation limit
    true_values = np.array([saturation_limit + 9, 99.232])
    data = np.empty_like(true_values)
    for i in range(true_values.size):
        fit_func = lambda x: x / poly(x) - true_values[i]
        data[i] = fsolve(fit_func, true_values[i])

    data[-1] = saturation_limit + 1
    expected = true_values.copy()
    expected[-1] = np.nan
    corrected = task.apply_correction_polynomial(data)
    np.testing.assert_allclose(corrected, expected)


def test_discrete_linearization_nan_masking(
    linearity_correction_task, assign_input_dataset_doc_to_task
):
    """
    Given: A list representing a single discrete coadd where one pixel saturates in the last read frame and another pixel's
      last read frame value deviates from the slope implied by the other read frames.
    When: Linearizing the ramp
    Then: The pixel with the deviant value is linearized correction; i.e., the last read frame is still considered when
      computing the slope.

    In other words, this test confirms that masking NaN values is done separately for *every pixel* such that a NaN in
    one pixel won't affect the slope calculation of other pixels.
    """
    task = linearity_correction_task
    arm = task.constants.arm_id
    param_dict = {f"dlnirsp_linearization_poly_coeffs_{arm.casefold()}": [1]}
    assign_input_dataset_doc_to_task(
        task, parameters=DlnirspTestingParameters(**param_dict), arm_id=arm
    )
    saturation_limit = task.parameters.linearization_saturation_threshold

    shape = (2, 2)
    num_read = 4

    data_list = []
    slopes = np.arange(np.prod(shape), dtype=float).reshape(shape)
    bias = np.zeros(shape, dtype=float)
    data_list.append(bias)
    for i in range(num_read):
        data = i * slopes
        data_list.append(data)

    data_list[-1][0, 0] = saturation_limit + 1
    data_list[-1][-1, -1] = data_list[-1][-1, -1] * 2

    ramp_obj_list = [EmptyFitsAccess(fits.PrimaryHDU(d)) for d in data_list]

    read_abscissa = np.arange(num_read) + 1.0
    linearized_ramp = task.linearize_uptheramp_discrete_coadd(
        coadd_obj_list=ramp_obj_list, read_abscissa=read_abscissa, num_bias=1
    )

    weird_px_data = [data_list[i + 1][-1, -1] for i in range(num_read)]
    weird_px_slope = np.polyfit(np.arange(num_read), weird_px_data, 1)[0]
    expected = slopes * num_read
    expected[-1, -1] = weird_px_slope * num_read

    np.testing.assert_allclose(linearized_ramp, expected)


def test_discrete_linearization_single_read(
    linearity_correction_task, assign_input_dataset_doc_to_task
):
    """
    Given: A list representing a single discrete coadd that only has one read frame
    When: Linearizing the coadd
    Then: The value of the first read frame is returned
    """
    task = linearity_correction_task
    arm = task.constants.arm_id
    param_dict = {f"dlnirsp_linearization_poly_coeffs_{arm.casefold()}": [1]}
    assign_input_dataset_doc_to_task(
        task, parameters=DlnirspTestingParameters(**param_dict), arm_id=arm
    )

    shape = (2, 2)
    bias = np.zeros(shape, dtype=float)
    data = np.arange(np.prod(shape)).reshape(shape)

    ramp_obj_list = [EmptyFitsAccess(fits.PrimaryHDU(bias)), EmptyFitsAccess(fits.PrimaryHDU(data))]

    read_abscissa = np.arange(1) + 1.0
    linearized_ramp = task.linearize_uptheramp_discrete_coadd(
        coadd_obj_list=ramp_obj_list,
        read_abscissa=read_abscissa,
        num_bias=1,
    )

    np.testing.assert_allclose(data, linearized_ramp)


def test_discrete_linearization_fewer_than_two_non_nan_read(
    linearity_correction_task, assign_input_dataset_doc_to_task
):
    """
    Given: A list representing a single discrete coadd of > 1 reads where some pixels have fewer than 2 non-nan read values
    When: Linearizing the coadd
    Then: The pixels in question has its linearized value set to the value of the first read.
    """
    task = linearity_correction_task
    arm = task.constants.arm_id
    param_dict = {f"dlnirsp_linearization_poly_coeffs_{arm.casefold()}": [1]}
    assign_input_dataset_doc_to_task(
        task, parameters=DlnirspTestingParameters(**param_dict), arm_id=arm
    )
    saturation_limit = task.parameters.linearization_saturation_threshold

    shape = (2, 2)
    num_read = 4

    data_list = []
    slopes = np.arange(np.prod(shape), dtype=float).reshape(shape) + 1
    bias = np.zeros(shape, dtype=float)
    data_list.append(bias)
    for i in range(num_read):
        data = i * slopes
        data[0, 0] = saturation_limit + 1  # Give a pixel no non-nan reads
        if i > 0:
            data[1, 1] = saturation_limit + 1
        if i != 1:
            # Pixel where single valid pixel *isn't* the first read
            data[0, 1] = saturation_limit + 1
        data_list.append(data)

    ramp_obj_list = [EmptyFitsAccess(fits.PrimaryHDU(d)) for d in data_list]

    expected = slopes * num_read
    expected[0, 0] = np.nan
    expected[1, 1] = data_list[0][1, 1]
    expected[0, 1] = np.nan

    read_abscissa = np.arange(num_read) + 1.0
    linearized_ramp = task.linearize_uptheramp_discrete_coadd(
        coadd_obj_list=ramp_obj_list,
        read_abscissa=read_abscissa,
        num_bias=1,
    )
    np.testing.assert_allclose(expected, linearized_ramp)
