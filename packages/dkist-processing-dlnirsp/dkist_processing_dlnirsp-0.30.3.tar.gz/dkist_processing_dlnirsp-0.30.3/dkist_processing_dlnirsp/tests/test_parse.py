import numpy as np
import pytest
from astropy.io import fits
from astropy.time import Time
from astropy.time import TimeDelta
from dkist_header_validator.translator import translate_spec122_to_spec214_l0
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_access_decoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.task_name import TaskName

from dkist_processing_dlnirsp.models.constants import DlnirspBudName
from dkist_processing_dlnirsp.models.parameters import DlnirspParsingParameters
from dkist_processing_dlnirsp.models.tags import DlnirspStemName
from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.parsers.dlnirsp_l0_fits_access import DlnirspL0FitsAccess
from dkist_processing_dlnirsp.parsers.dlnirsp_l0_fits_access import DlnirspRampFitsAccess
from dkist_processing_dlnirsp.parsers.mosaic import NumMosaicXTilesBud
from dkist_processing_dlnirsp.tasks.parse import ParseL0DlnirspLinearizedData
from dkist_processing_dlnirsp.tasks.parse import ParseL0DlnirspRampData
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingParameters
from dkist_processing_dlnirsp.tests.conftest import MissingDitherStepObserveHeaders
from dkist_processing_dlnirsp.tests.conftest import MissingMosaicStepObserveHeaders
from dkist_processing_dlnirsp.tests.conftest import MissingXStepObserveHeaders
from dkist_processing_dlnirsp.tests.conftest import MissingYStepObserveHeaders
from dkist_processing_dlnirsp.tests.conftest import ModulatedObserveHeaders
from dkist_processing_dlnirsp.tests.conftest import RawRampHeaders
from dkist_processing_dlnirsp.tests.conftest import make_random_data
from dkist_processing_dlnirsp.tests.conftest import write_dark_frames_to_task
from dkist_processing_dlnirsp.tests.conftest import write_frames_to_task
from dkist_processing_dlnirsp.tests.conftest import write_lamp_gain_frames_to_task
from dkist_processing_dlnirsp.tests.conftest import write_observe_frames_to_task
from dkist_processing_dlnirsp.tests.conftest import write_polcal_frames_to_task
from dkist_processing_dlnirsp.tests.conftest import write_solar_gain_frames_to_task


@pytest.fixture
def raw_ramp_parse_task(tmp_path, recipe_run_id, arm_id):
    num_ramps = 3
    num_line = 2
    num_read = 3
    num_reset = 4
    start_date = "2023-01-01T01:23:45"
    ramp_length_sec = 1.0
    array_shape = (3, 3)
    modulator_spin_mode = "Really fast"
    camera_readout_mode = "Super cool"
    with ParseL0DlnirspRampData(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        frame_generator = RawRampHeaders(
            array_shape=array_shape,
            num_ramps=num_ramps,
            num_line=num_line,
            num_read=num_read,
            num_reset=num_reset,
            start_date=start_date,
            ramp_length_sec=ramp_length_sec,
            arm_id=arm_id,
            modulator_spin_mode=modulator_spin_mode,
            camera_readout_mode=camera_readout_mode,
        )
        for frame in frame_generator:
            header = frame.header()
            data = np.random.randint(0, 4e5, array_shape).astype(np.int16)
            translated_header = fits.Header(translate_spec122_to_spec214_l0(header))
            hdul = fits.HDUList(
                [fits.PrimaryHDU(), fits.CompImageHDU(data=data, header=translated_header)]
            )
            task.write(
                data=hdul,
                tags=[DlnirspTag.input(), DlnirspTag.frame()],
                encoder=fits_hdulist_encoder,
            )

        yield task, num_ramps, num_line, num_read, num_reset, start_date, ramp_length_sec, modulator_spin_mode, camera_readout_mode
        task._purge()


@pytest.mark.parametrize("arm_id", [pytest.param("HBand", id="IR"), pytest.param("VIS", id="VIS")])
def test_parse_ramp_data(raw_ramp_parse_task, arm_id):
    """
    Given: A ParseL0DlnirspRampData task with raw ramp data
    When: Parsing the input frames
    Then: Constants and tags are updated/applied correctly
    """
    (
        task,
        num_ramps,
        num_line,
        num_read,
        num_reset,
        start_date,
        ramp_length_sec,
        modulator_spin_mode,
        camera_readout_mode,
    ) = raw_ramp_parse_task

    task()

    # Constants
    start_date_obj = Time(start_date)
    time_delta = TimeDelta(ramp_length_sec, format="sec")
    expected_obs_time_list = [(start_date_obj + time_delta * i).fits for i in range(num_ramps)]
    assert task.constants._db_dict[DlnirspBudName.arm_id.value] == arm_id
    if arm_id == "VIS":
        return

    assert task.constants._db_dict[DlnirspBudName.time_obs_list.value] == expected_obs_time_list

    # Tags
    for ramp_time in expected_obs_time_list:
        fits_obj_list = list(
            task.read(
                tags=[DlnirspTag.time_obs(ramp_time)],
                decoder=fits_access_decoder,
                fits_access_class=DlnirspRampFitsAccess,
            )
        )
        assert len(fits_obj_list) == num_line + num_read + num_reset
        for fits_obj in fits_obj_list:
            header_curr_frame = fits_obj.header["DLCAMCUR"]
            tags = task.tags(fits_obj.name)
            tag_curr_frame = [
                int(t.split("_")[-1])
                for t in tags
                if DlnirspStemName.current_frame_in_ramp.value in t
            ][0]
            assert header_curr_frame == tag_curr_frame


@pytest.fixture
def linearized_parse_task_flip_crpix1_wcs_correction(
    tmp_path, recipe_run_id, assign_input_dataset_doc_to_task, link_constants_db
):
    constants = {"OBS_IP_START_TIME": "2024-01-01"}
    link_constants_db(recipe_run_id=recipe_run_id, constants_obj=constants)
    with ParseL0DlnirspLinearizedData(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        assign_input_dataset_doc_to_task(
            task=task,
            parameters=DlnirspTestingParameters(dlnirsp_wcs_crpix_correction_method="flip_crpix1"),
            parameter_class=DlnirspParsingParameters,
            obs_ip_start_time=task.constants.obs_ip_start_time,
        )

        yield task
        task._purge()


@pytest.fixture(params=["flip_crpix1", "swap_then_flip_crpix2"])
def linearized_parse_task_with_multi_crpix_correction_methods(
    tmp_path, recipe_run_id, assign_input_dataset_doc_to_task, link_constants_db, request
):
    crpix_correction_method = request.param
    constants = {"OBS_IP_START_TIME": "2024-01-01"}
    link_constants_db(recipe_run_id=recipe_run_id, constants_obj=constants)
    with ParseL0DlnirspLinearizedData(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        assign_input_dataset_doc_to_task(
            task=task,
            parameters=DlnirspTestingParameters(
                dlnirsp_wcs_crpix_correction_method=crpix_correction_method
            ),
            parameter_class=DlnirspParsingParameters,
            obs_ip_start_time=task.constants.obs_ip_start_time,
        )

        yield task
        task._purge()


@pytest.mark.parametrize(
    "dither_mode_on",
    [pytest.param(False, id="dither_mode_off"), pytest.param(True, id="dither_mode_on")],
)
def test_parse_linearized_data(
    linearized_parse_task_with_multi_crpix_correction_methods, dither_mode_on
):
    """
    Given: A set of LINEARIZED frames and a Parse task
    When: Parsing the frames
    Then: The frames are tagged correctly and constants are populated correctly
    """

    task = linearized_parse_task_with_multi_crpix_correction_methods

    lamp_exp_time = 10.0
    solar_exp_time = 5.0
    obs_exp_time = 6.0
    polcal_exp_time = 7.0
    unused_exp_time = 99.0
    num_mod = 4
    num_dither = int(dither_mode_on) + 1
    num_mosaic = 3
    num_X_tile = 2
    num_Y_tile = 3
    num_data_cycles = 2
    dark_exp_times = [lamp_exp_time, solar_exp_time, obs_exp_time, unused_exp_time]
    arm_position = 6.28
    grating_constant = 43
    grating_angle = 132.2
    solar_ip_start_date = "1999-12-31T23:59:59"

    num_dark = 0
    lin_tag = [DlnirspTag.linearized()]

    # Give dark, lamp, and polcal frames different grating constant, angle, and arm position values to test that the
    # `TaskIn*` buds are correctly discriminating
    for exp_time in dark_exp_times:
        num_dark += write_dark_frames_to_task(
            task,
            exp_time_ms=exp_time,
            tags=lin_tag,
            num_modstates=num_mod,
            arm_position=arm_position * 10,
            grating_constant=grating_constant * 100,
            grating_angle=grating_angle * -2,
        )
    num_lamp = write_lamp_gain_frames_to_task(
        task,
        tags=lin_tag,
        num_modstates=num_mod,
        arm_position=arm_position * 20,
        grating_constant=grating_constant * 200,
        grating_angle=grating_angle * -4,
    )
    num_solar = write_solar_gain_frames_to_task(
        task,
        tags=lin_tag,
        num_modstates=num_mod,
        arm_position=arm_position,
        grating_constant=grating_constant,
        grating_angle=grating_angle,
        start_date=solar_ip_start_date,
    )
    num_polcal = write_polcal_frames_to_task(
        task,
        tags=lin_tag,
        num_modstates=num_mod,
        arm_position=arm_position * 30,
        grating_constant=grating_constant * 300,
        grating_angle=grating_angle * -6,
    )
    num_obs = write_observe_frames_to_task(
        task,
        num_modstates=num_mod,
        num_mosaics=num_mosaic,
        num_X_tiles=num_X_tile,
        num_Y_tiles=num_Y_tile,
        num_data_cycles=num_data_cycles,
        tags=lin_tag,
        arm_position=arm_position,
        grating_constant=grating_constant,
        grating_angle=grating_angle,
        dither_mode_on=dither_mode_on,
        swap_crpix_values="swap" in task.parameters.wcs_crpix_correction_method,
    )

    task()

    # Tags applied correctly
    assert len(list(task.read(tags=[DlnirspTag.linearized(), DlnirspTag.task_dark()]))) == num_dark
    assert (
        len(list(task.read(tags=[DlnirspTag.linearized(), DlnirspTag.task_lamp_gain()])))
        == num_lamp
    )
    assert (
        len(list(task.read(tags=[DlnirspTag.linearized(), DlnirspTag.task_solar_gain()])))
        == num_solar
    )
    assert (
        len(list(task.read(tags=[DlnirspTag.linearized(), DlnirspTag.task_polcal()]))) == num_polcal
    )
    assert (
        len(list(task.read(tags=[DlnirspTag.linearized(), DlnirspTag.task_observe()]))) == num_obs
    )

    for task_name, exp_times in zip(
        [
            TaskName.dark.value,
            TaskName.lamp_gain.value,
            TaskName.solar_gain.value,
            TaskName.polcal.value,
        ],
        [dark_exp_times, [lamp_exp_time], [solar_exp_time], [polcal_exp_time]],
    ):
        for exp in exp_times:
            for modstate in range(1, num_mod + 1):
                tags = [
                    DlnirspTag.linearized_frame(),
                    DlnirspTag.task(task_name),
                    DlnirspTag.exposure_time(exp),
                    DlnirspTag.modstate(modstate),
                ]
                assert len(list(task.read(tags=tags))) == 1

    # Observe frames are special because we want to check for mosaic stuff
    for dither_step in range(num_dither):
        for mosaic in range(num_mosaic):
            for X_tile in range(1, num_X_tile + 1):
                for Y_tile in range(1, num_Y_tile + 1):
                    for modstate in range(1, num_mod + 1):
                        tags = [
                            DlnirspTag.linearized_frame(),
                            DlnirspTag.task_observe(),
                            DlnirspTag.exposure_time(obs_exp_time),
                            DlnirspTag.mosaic_num(mosaic),
                            DlnirspTag.mosaic_tile_x(X_tile),
                            DlnirspTag.mosaic_tile_y(Y_tile),
                            DlnirspTag.dither_step(dither_step),
                            DlnirspTag.modstate(modstate),
                        ]
                        assert len(list(task.read(tags=tags))) == num_data_cycles

    # Constants loaded correctly
    assert task.constants._db_dict[DlnirspBudName.wavelength] == 1565.0
    assert task.constants._db_dict[DlnirspBudName.polarimeter_mode] == "Full Stokes"
    assert task.constants._db_dict[DlnirspBudName.num_modstates] == num_mod
    assert task.constants._db_dict[DlnirspBudName.num_mosaic_repeats] == num_mosaic
    assert task.constants._db_dict[DlnirspBudName.num_mosaic_tiles_x] == num_X_tile
    assert task.constants._db_dict[DlnirspBudName.num_mosaic_tiles_y] == num_Y_tile
    assert task.constants._db_dict[DlnirspBudName.num_dither_steps] == num_dither
    assert task.constants._db_dict[DlnirspBudName.lamp_gain_exposure_times] == [lamp_exp_time]
    assert task.constants._db_dict[DlnirspBudName.solar_gain_exposure_times] == [solar_exp_time]
    assert task.constants._db_dict[DlnirspBudName.observe_exposure_times] == [obs_exp_time]
    assert task.constants._db_dict[DlnirspBudName.polcal_exposure_times] == [polcal_exp_time]
    assert task.constants._db_dict[BudName.retarder_name] == "SiO2 OC"
    assert task.constants._db_dict[DlnirspBudName.arm_position_mm] == arm_position
    assert task.constants._db_dict[DlnirspBudName.grating_constant_inverse_mm] == grating_constant
    np.testing.assert_allclose(
        task.constants._db_dict[DlnirspBudName.grating_position_deg], grating_angle, atol=0.01
    )
    assert task.constants._db_dict[DlnirspBudName.solar_gain_ip_start_time] == solar_ip_start_date


def test_crpix_and_spatial_step_association_swapped(
    linearized_parse_task_flip_crpix1_wcs_correction,
):
    """
    Given: A Parse task and a set of observe frames where CRPIX1 corresponds to the "spatial step y" direction
    When: Parsing the mosaic information
    Then: The correct absolute (i.e., CRPIX[12]) mosaic is determined and tagged.
    """
    task = linearized_parse_task_flip_crpix1_wcs_correction

    obs_exp_time = 6.0
    num_mod = 1
    num_dither = 1
    num_mosaic = 1
    num_X_tile = 3
    num_Y_tile = 2
    num_data_cycles = 1

    write_observe_frames_to_task(
        task,
        num_modstates=num_mod,
        num_mosaics=num_mosaic,
        num_X_tiles=num_X_tile,
        num_Y_tiles=num_Y_tile,
        num_data_cycles=num_data_cycles,
        tags=[DlnirspTag.linearized()],
        dither_mode_on=False,
        swap_crpix_values=True,
    )

    task()

    parsed_num_x_tiles = task.constants._db_dict[DlnirspBudName.num_mosaic_tiles_x]
    parsed_num_y_tiles = task.constants._db_dict[DlnirspBudName.num_mosaic_tiles_y]
    # Here we check that the number of tiles is correctly parsed as the swap of what is expected from the spatial step
    # keys
    assert parsed_num_x_tiles == num_Y_tile
    assert parsed_num_y_tiles == num_X_tile

    for dither_step in range(num_dither):
        for mosaic in range(num_mosaic):
            for X_tile in range(1, parsed_num_x_tiles + 1):
                for Y_tile in range(1, parsed_num_y_tiles + 1):
                    for modstate in range(1, num_mod + 1):
                        tags = [
                            DlnirspTag.frame(),
                            DlnirspTag.linearized(),
                            DlnirspTag.task_observe(),
                            DlnirspTag.exposure_time(obs_exp_time),
                            DlnirspTag.mosaic_num(mosaic),
                            DlnirspTag.mosaic_tile_x(X_tile),
                            DlnirspTag.mosaic_tile_y(Y_tile),
                            DlnirspTag.dither_step(dither_step),
                            DlnirspTag.modstate(modstate),
                        ]
                        assert len(list(task.read(tags=tags))) == num_data_cycles


########################
# NOTE ABOUT ABORT TESTS
####
# The following tests ensure that parsing is correct when data collection is aborted.
# Each separate test function represents how many *completed* "things" there are before the abort happens, organized
# (as you read down the file) by loop-level. For example, in the first test, `test_parse_aborted_multiple_mosaics`,
# we test how an abort is handled if it happens after at least one complete mosaic as been observed. We need these
# different tests because the abort logic states that if *any* higher-level loop as completed one cycle then *all* lower
# loops are only used if they are complete (see the `mosaic` parsing module for more information).
#
# Each test is parameterized by the level at which the abort happens because we want to make sure the abort detection
# works no matter where in the process the plug was pulled.
#
# Finally, tests of loops below the "dither" level are additionally parameterized by the direction the field moves in
# an absolute sense (`crpix_delta`). This is because at these levels we use the largest contiguous portion of an
# aborted mosaic, and we need to check that the mosaic step assignment is not thrown off by CRPIX[12] values in mosaic
# tiles that will be thrown away (because they are in a sparse part of the aborted mosaic).
########################


@pytest.mark.parametrize(
    "abort_loop, dither_mode_on, num_X_tiles",
    [
        pytest.param("mosaic", True, 3, id="mosaic"),
        #
        pytest.param("dither", True, 3, id="dither"),
        #
        pytest.param("X_tile", True, 3, id="X_tile"),
        pytest.param("X_tile", False, 3, id="X_tile_single_mosaic"),
        #
        pytest.param("Y_tile", True, 3, id="Y_tile"),
        pytest.param("Y_tile", False, 3, id="Y_tile_single_mosaic"),
        pytest.param("Y_tile", False, 1, id="Y_tile_single_mosaic_X_tile"),
        #
        pytest.param("data_cycle", False, 1, id="data_cycle"),
        pytest.param("modstate", False, 1, id="modstate"),
    ],
)
def test_parse_aborted_multiple_mosaics(
    linearized_parse_task_with_multi_crpix_correction_methods,
    abort_loop,
    dither_mode_on,
    num_X_tiles,
):
    """
    Given: A Parse task and a set of data with multiple mosaics and the last mosaic aborted at various loop levels
    When: Parsing the data
    Then: The number of mosaics is correctly set to the number of *completed* mosaics
    """
    task = linearized_parse_task_with_multi_crpix_correction_methods

    num_mosaics = 3
    num_Y_tiles = 2
    num_data_cycles = 3
    num_modstates = 2
    num_dither = int(dither_mode_on) + 1
    obs_exp_time = 6.0

    frame_generator = ModulatedObserveHeaders(
        num_mosaics=num_mosaics,
        num_X_tiles=num_X_tiles,
        num_Y_tiles=num_Y_tiles,
        num_data_cycles=num_data_cycles,
        num_modstates=num_modstates,
        dither_mode_on=dither_mode_on,
        aborted_loop_level=abort_loop,
        array_shape=(3, 3),
        swap_crpix_values="swap" in task.parameters.wcs_crpix_correction_method,
    )

    write_frames_to_task(
        task=task,
        frame_generator=frame_generator,
        data_func=make_random_data,
        extra_tags=[DlnirspTag.linearized()],
    )

    expected_num_mosaic = num_mosaics - 1

    task()
    assert task.constants._db_dict[DlnirspBudName.num_mosaic_repeats] == expected_num_mosaic
    assert task.constants._db_dict[DlnirspBudName.num_dither_steps] == num_dither
    assert task.constants._db_dict[DlnirspBudName.num_mosaic_tiles_x] == num_X_tiles
    assert task.constants._db_dict[DlnirspBudName.num_mosaic_tiles_y] == num_Y_tiles
    assert task.constants._db_dict[DlnirspBudName.num_modstates] == num_modstates
    for dither_step in range(num_dither):
        for mosaic in range(expected_num_mosaic):
            for X_tile in range(1, num_X_tiles + 1):
                for Y_tile in range(1, num_Y_tiles + 1):
                    for modstate in range(1, num_modstates + 1):
                        tags = [
                            DlnirspTag.frame(),
                            DlnirspTag.linearized(),
                            DlnirspTag.task_observe(),
                            DlnirspTag.exposure_time(obs_exp_time),
                            DlnirspTag.mosaic_num(mosaic),
                            DlnirspTag.mosaic_tile_x(X_tile),
                            DlnirspTag.mosaic_tile_y(Y_tile),
                            DlnirspTag.dither_step(dither_step),
                            DlnirspTag.modstate(modstate),
                        ]
                        assert len(list(task.read(tags=tags))) == num_data_cycles


@pytest.mark.parametrize(
    "abort_loop, num_X_tiles",
    [
        pytest.param("dither", 3, id="dither"),
        #
        pytest.param("X_tile", 3, id="X_tile"),
        #
        pytest.param("Y_tile", 3, id="Y_tile"),
        pytest.param("Y_tile", 1, id="Y_tile_single_X_tile"),
        #
        pytest.param("data_cycle", 1, id="data_cycle"),
        pytest.param("modstate", 1, id="modstate"),
    ],
)
def test_parse_aborted_single_mosaic(
    linearized_parse_task_with_multi_crpix_correction_methods, abort_loop, num_X_tiles
):
    """
    Given: A Parse task and a set of dithered data and the last dither aborted at various loop levels
    When: Parsing the data
    Then: The number of dither steps is always 1 in this case
    """
    task = linearized_parse_task_with_multi_crpix_correction_methods

    num_mosaics = 1
    num_Y_tiles = 2
    num_data_cycles = 3
    num_modstates = 2
    obs_exp_time = 6.0

    frame_generator = ModulatedObserveHeaders(
        num_mosaics=num_mosaics,
        num_X_tiles=num_X_tiles,
        num_Y_tiles=num_Y_tiles,
        num_data_cycles=num_data_cycles,
        num_modstates=num_modstates,
        dither_mode_on=True,
        aborted_loop_level=abort_loop,
        array_shape=(3, 3),
        swap_crpix_values="swap" in task.parameters.wcs_crpix_correction_method,
    )

    write_frames_to_task(
        task=task,
        frame_generator=frame_generator,
        data_func=make_random_data,
        extra_tags=[DlnirspTag.linearized()],
    )

    # Because if we abort when dither mode is on then we get 1, but if dither mode is off it's also 1.
    expected_num_dither = 1

    task()
    assert task.constants._db_dict[DlnirspBudName.num_dither_steps] == expected_num_dither
    assert task.constants._db_dict[DlnirspBudName.num_mosaic_tiles_x] == num_X_tiles
    assert task.constants._db_dict[DlnirspBudName.num_mosaic_tiles_y] == num_Y_tiles
    assert task.constants._db_dict[DlnirspBudName.num_modstates] == num_modstates
    for dither_step in range(expected_num_dither):
        for mosaic in range(num_mosaics):
            for X_tile in range(1, num_X_tiles + 1):
                for Y_tile in range(1, num_Y_tiles + 1):
                    for modstate in range(1, num_modstates + 1):
                        tags = [
                            DlnirspTag.frame(),
                            DlnirspTag.linearized(),
                            DlnirspTag.task_observe(),
                            DlnirspTag.exposure_time(obs_exp_time),
                            DlnirspTag.mosaic_num(mosaic),
                            DlnirspTag.mosaic_tile_x(X_tile),
                            DlnirspTag.mosaic_tile_y(Y_tile),
                            DlnirspTag.dither_step(dither_step),
                            DlnirspTag.modstate(modstate),
                        ]
                        assert len(list(task.read(tags=tags))) == num_data_cycles


@pytest.mark.parametrize(
    "abort_loop",
    [
        pytest.param("X_tile", id="X_tile"),
        pytest.param("Y_tile", id="Y_tile"),
        pytest.param("data_cycle", id="data_cycle"),
        pytest.param("modstate", id="modstate"),
    ],
)
@pytest.mark.parametrize(
    "crpix_delta",
    [
        pytest.param((10.2, 5.1), id="positive_dcrpix"),
        pytest.param((-10.2, 5.1), id="negative_dcrpix1"),
        pytest.param((10.2, -5.1), id="negative_dcrpix2"),
        pytest.param((-10.2, -5.1), id="negative_dcrpix"),
    ],
)
def test_parse_aborted_single_dither(
    linearized_parse_task_with_multi_crpix_correction_methods, abort_loop, crpix_delta
):
    """
    Given: A Parse task and a set of data with a single mosaic and the last X tile aborted at various loop levels
    When: Parsing the data
    Then: The number of X tiles is correctly set to the number of *completed* X tiles
    """
    task = linearized_parse_task_with_multi_crpix_correction_methods

    num_mosaics = 1
    num_dither = 1
    num_X_tiles = 2
    num_Y_tiles = 2
    num_data_cycles = 3
    num_modstates = 2
    obs_exp_time = 6.0

    frame_generator = ModulatedObserveHeaders(
        num_mosaics=num_mosaics,
        num_X_tiles=num_X_tiles,
        num_Y_tiles=num_Y_tiles,
        num_data_cycles=num_data_cycles,
        num_modstates=num_modstates,
        dither_mode_on=False,
        aborted_loop_level=abort_loop,
        array_shape=(3, 3),
        crpix_delta=crpix_delta,
        swap_crpix_values="swap" in task.parameters.wcs_crpix_correction_method,
    )

    write_frames_to_task(
        task=task,
        frame_generator=frame_generator,
        data_func=make_random_data,
        extra_tags=[DlnirspTag.linearized()],
    )

    expected_X_tiles = num_X_tiles - 1

    task()
    assert task.constants._db_dict[DlnirspBudName.num_mosaic_repeats] == num_mosaics
    assert task.constants._db_dict[DlnirspBudName.num_dither_steps] == num_dither
    assert task.constants._db_dict[DlnirspBudName.num_mosaic_tiles_x] == expected_X_tiles
    assert task.constants._db_dict[DlnirspBudName.num_mosaic_tiles_y] == num_Y_tiles
    assert task.constants._db_dict[DlnirspBudName.num_modstates] == num_modstates
    for dither_step in range(num_dither):
        for mosaic in range(num_mosaics):
            for X_tile in range(1, expected_X_tiles + 1):
                for Y_tile in range(1, num_Y_tiles + 1):
                    for modstate in range(1, num_modstates + 1):
                        tags = [
                            DlnirspTag.frame(),
                            DlnirspTag.linearized(),
                            DlnirspTag.task_observe(),
                            DlnirspTag.exposure_time(obs_exp_time),
                            DlnirspTag.mosaic_num(mosaic),
                            DlnirspTag.mosaic_tile_x(X_tile),
                            DlnirspTag.mosaic_tile_y(Y_tile),
                            DlnirspTag.dither_step(dither_step),
                            DlnirspTag.modstate(modstate),
                        ]
                        assert len(list(task.read(tags=tags))) == num_data_cycles


@pytest.mark.parametrize(
    "abort_loop", [pytest.param("Y_tile"), pytest.param("data_cycle"), pytest.param("modstate")]
)
@pytest.mark.parametrize(
    "crpix_delta",
    [
        pytest.param((10.2, 5.1), id="positive_dcrpix"),
        pytest.param((-10.2, 5.1), id="negative_dcrpix1"),
        pytest.param((10.2, -5.1), id="negative_dcrpix2"),
        pytest.param((-10.2, -5.1), id="negative_dcrpix"),
    ],
)
def test_parse_aborted_single_X_tile(
    linearized_parse_task_with_multi_crpix_correction_methods, abort_loop, crpix_delta
):
    """
    Given: A Parse task and a set of data with a single mosaic and X tile and the last Y tile aborted at various loop levels
    When: Parsing the data
    Then: The number of Y tiles is correctly set to the number of *completed* Y tiles
    """
    task = linearized_parse_task_with_multi_crpix_correction_methods

    num_mosaics = 1
    num_dither = 1
    num_X_tiles = 1
    num_Y_tiles = 2
    num_data_cycles = 3
    num_modstates = 2
    obs_exp_time = 6.0

    frame_generator = ModulatedObserveHeaders(
        num_mosaics=num_mosaics,
        num_X_tiles=num_X_tiles,
        num_Y_tiles=num_Y_tiles,
        num_data_cycles=num_data_cycles,
        num_modstates=num_modstates,
        dither_mode_on=False,
        aborted_loop_level=abort_loop,
        array_shape=(3, 3),
        crpix_delta=crpix_delta,
        swap_crpix_values="swap" in task.parameters.wcs_crpix_correction_method,
    )

    write_frames_to_task(
        task=task,
        frame_generator=frame_generator,
        data_func=make_random_data,
        extra_tags=[DlnirspTag.linearized()],
    )

    expected_Y_tiles = num_Y_tiles - 1

    task()
    assert task.constants._db_dict[DlnirspBudName.num_mosaic_repeats] == num_mosaics
    assert task.constants._db_dict[DlnirspBudName.num_mosaic_tiles_x] == num_dither
    assert task.constants._db_dict[DlnirspBudName.num_mosaic_tiles_y] == expected_Y_tiles
    assert task.constants._db_dict[DlnirspBudName.num_modstates] == num_modstates
    for dither_step in range(num_dither):
        for mosaic in range(num_mosaics):
            for X_tile in range(1, num_X_tiles + 1):
                for Y_tile in range(1, expected_Y_tiles + 1):
                    for modstate in range(1, num_modstates + 1):
                        tags = [
                            DlnirspTag.frame(),
                            DlnirspTag.linearized(),
                            DlnirspTag.task_observe(),
                            DlnirspTag.exposure_time(obs_exp_time),
                            DlnirspTag.mosaic_num(mosaic),
                            DlnirspTag.mosaic_tile_x(X_tile),
                            DlnirspTag.mosaic_tile_y(Y_tile),
                            DlnirspTag.dither_step(dither_step),
                            DlnirspTag.modstate(modstate),
                        ]
                        assert len(list(task.read(tags=tags))) == num_data_cycles


@pytest.mark.parametrize(
    "frame_generator_class, error_name",
    [
        pytest.param(
            MissingMosaicStepObserveHeaders,
            "mosaic repeats",
            id="Mosaic",
        ),
        pytest.param(MissingDitherStepObserveHeaders, "dither steps", id="dither"),
        pytest.param(
            MissingXStepObserveHeaders,
            "spatial_step_x's",
            id="X_tile",
        ),
        pytest.param(
            MissingYStepObserveHeaders,
            "spatial_step_y's",
            id="Y_tile",
        ),
    ],
)
def test_parse_aborted_single_loop_failures(
    linearized_parse_task_with_multi_crpix_correction_methods, frame_generator_class, error_name
):
    """
    Given: A Parse task and a set of data where all three of mosaic, X_tile, and Y_tile loops contain missing data
    When: Parsing the data
    Then: The correct error is raised
    """
    task = linearized_parse_task_with_multi_crpix_correction_methods

    frame_generator = frame_generator_class(array_shape=(3, 3))

    write_frames_to_task(
        task=task,
        frame_generator=frame_generator,
        data_func=make_random_data,
        extra_tags=[DlnirspTag.linearized()],
    )

    with pytest.raises(
        ValueError,
        match=f"Not all sequential {error_name} could be found.",
    ):
        task()


@pytest.mark.parametrize(
    "frame_generator_class, frame_generator_args, error_name",
    [
        pytest.param(
            MissingDitherStepObserveHeaders,
            {"num_mosaics": 2},
            "dither steps",
            id="mosaic",
        ),
        pytest.param(
            MissingXStepObserveHeaders,
            {"num_mosaics": 2},
            "spatial_step_x's",
            id="X_tile",
        ),
        pytest.param(
            MissingYStepObserveHeaders,
            {"num_X_tiles": 2},
            "spatial_step_y's",
            id="Y_tile",
        ),
    ],
)
def test_parse_missing_loop_failures(
    linearized_parse_task_with_multi_crpix_correction_methods,
    frame_generator_class,
    frame_generator_args,
    error_name,
):
    """
    Given: A Parse task and a set of data where all three of mosaic, X_tile, and Y_tile loops contain missing data
    When: Parsing the data
    Then: The correct error is raised
    """
    task = linearized_parse_task_with_multi_crpix_correction_methods

    kwargs = {"array_shape": (3, 3)} | frame_generator_args
    frame_generator = frame_generator_class(**kwargs)
    write_frames_to_task(
        task=task,
        frame_generator=frame_generator,
        data_func=make_random_data,
        extra_tags=[DlnirspTag.linearized()],
    )

    with pytest.raises(
        ValueError,
        match=f"Whole {error_name} are missing. This is extremely strange.",
    ):
        task()


@pytest.mark.parametrize(
    "abort_loop, first_XY_loop",
    [
        pytest.param("X_tile", "X", id="X_abort_X_first"),
        pytest.param("Y_tile", "X", id="Y_abort_X_first"),
        pytest.param("X_tile", "Y", id="X_abort_Y_first"),
        pytest.param("Y_tile", "Y", id="Y_abort_Y_first"),
    ],
)
@pytest.mark.parametrize(
    "crpix_delta",
    [
        pytest.param((10.2, 5.1), id="positive_dcrpix"),
        pytest.param((-10.2, 5.1), id="negative_dcrpix1"),
        pytest.param((10.2, -5.1), id="negative_dcrpix2"),
        pytest.param((-10.2, -5.1), id="negative_dcrpix"),
    ],
)
def test_parse_aborted_XY_loop_order(
    linearized_parse_task_with_multi_crpix_correction_methods,
    abort_loop,
    first_XY_loop,
    crpix_delta,
):
    """
    Given: A Parse task and a set of data with a single mosaic and dither where the last X/Y tile is aborted and the X/Y loop order changes
    When: Parsing the data
    Then: The number of the outer loop tiles is one less while the inner loop is all present in the input
    """
    task = linearized_parse_task_with_multi_crpix_correction_methods

    num_mosaics = 1
    num_dither = 1
    num_X_tiles = 2
    num_Y_tiles = 3
    num_data_cycles = 1
    num_modstates = 1
    obs_exp_time = 6.0

    frame_generator = ModulatedObserveHeaders(
        num_mosaics=num_mosaics,
        num_X_tiles=num_X_tiles,
        num_Y_tiles=num_Y_tiles,
        num_data_cycles=num_data_cycles,
        num_modstates=num_modstates,
        dither_mode_on=False,
        aborted_loop_level=abort_loop,
        array_shape=(3, 3),
        first_XY_loop=first_XY_loop,
        crpix_delta=crpix_delta,
        swap_crpix_values="swap" in task.parameters.wcs_crpix_correction_method,
    )

    write_frames_to_task(
        task=task,
        frame_generator=frame_generator,
        data_func=make_random_data,
        extra_tags=[DlnirspTag.linearized()],
    )

    if first_XY_loop == "X":
        expected_X_tiles = num_X_tiles - 1
        expected_Y_tiles = num_Y_tiles
    else:
        expected_X_tiles = num_X_tiles
        expected_Y_tiles = num_Y_tiles - 1

    task()
    assert task.constants._db_dict[DlnirspBudName.num_mosaic_repeats] == num_mosaics
    assert task.constants._db_dict[DlnirspBudName.num_dither_steps] == num_dither
    assert task.constants._db_dict[DlnirspBudName.num_mosaic_tiles_x] == expected_X_tiles
    assert task.constants._db_dict[DlnirspBudName.num_mosaic_tiles_y] == expected_Y_tiles
    assert task.constants._db_dict[DlnirspBudName.num_modstates] == num_modstates
    for dither_step in range(num_dither):
        for mosaic in range(num_mosaics):
            for X_tile in range(1, expected_X_tiles + 1):
                for Y_tile in range(1, expected_Y_tiles + 1):
                    for modstate in range(1, num_modstates + 1):
                        tags = [
                            DlnirspTag.frame(),
                            DlnirspTag.linearized(),
                            DlnirspTag.task_observe(),
                            DlnirspTag.exposure_time(obs_exp_time),
                            DlnirspTag.mosaic_num(mosaic),
                            DlnirspTag.mosaic_tile_x(X_tile),
                            DlnirspTag.mosaic_tile_y(Y_tile),
                            DlnirspTag.dither_step(dither_step),
                            DlnirspTag.modstate(modstate),
                        ]
                        assert len(list(task.read(tags=tags))) == num_data_cycles


def test_locking_cached_property():
    """
    Given: A subclass of `XYMosaicTilesBase` (which contains `locking_cached_properties`)
    When: Trying to call the `setter` (via `update`) after accessing a `locking_cached_property`
    Then: The correct error is raised
    """
    dataset = ModulatedObserveHeaders(
        num_modstates=1,
        num_mosaics=1,
        num_X_tiles=1,
        num_Y_tiles=1,
        num_data_cycles=1,
        array_shape=(2, 2),
        exp_time_ms=1.0,
    )
    fits_obj = DlnirspL0FitsAccess.from_header(translate_spec122_to_spec214_l0(dataset.header()))
    num_tile_bud = NumMosaicXTilesBud(
        crpix_correction_method="flip_crpix1", bin_crpix_to_multiple_of=3
    )

    num_tile_bud.update("foo", fits_obj)
    _ = num_tile_bud.spatial_step_label
    with pytest.raises(
        ValueError, match="State of NumMosaicXTilesBud has been locked. No more setting allowed."
    ):
        num_tile_bud.update("foo2", fits_obj)
