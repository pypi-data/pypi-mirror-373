import pytest
from astropy.io import fits
from dkist_header_validator.translator import translate_spec122_to_spec214_l0

from dkist_processing_dlnirsp.parsers.dlnirsp_l0_fits_access import DlnirspL0FitsAccess
from dkist_processing_dlnirsp.parsers.dlnirsp_l0_fits_access import DlnirspRampFitsAccess
from dkist_processing_dlnirsp.tests.conftest import DlnirspHeaders


@pytest.fixture
def ramp_header(arm_id):
    dataset = DlnirspHeaders(
        dataset_shape=(2, 2, 2), array_shape=(1, 2, 2), time_delta=1.0, arm_id=arm_id
    )
    translated_header = fits.Header(translate_spec122_to_spec214_l0(dataset.header()))
    return translated_header


@pytest.fixture
def dither_header(dither_mode_on, dither_step):
    dataset = DlnirspHeaders(
        dataset_shape=(2, 2, 2),
        array_shape=(1, 2, 2),
        time_delta=1.0,
        dither_mode_on=dither_mode_on,
        dither_step=dither_step,
    )
    translated_header = fits.Header(translate_spec122_to_spec214_l0(dataset.header()))
    return translated_header


@pytest.mark.parametrize(
    "arm_id", [pytest.param("JBand"), pytest.param("HBand"), pytest.param("VIS")]
)
def test_dlnirsp_ramp_fits_access(ramp_header, arm_id):
    """
    Given: A header that may or may not contain IR camera-specific header keys
    When: Parsing the header with `DlnirspRampFitsAccess`
    Then: If the data are IR then the header values are parsed, and if the data are VIS then dummy values are returned
          for the IR-only keys.
    """
    fits_obj = DlnirspRampFitsAccess.from_header(ramp_header)

    assert fits_obj.arm_id == arm_id
    if arm_id == "VIS":
        assert fits_obj.camera_readout_mode == "DEFAULT_VISIBLE_CAMERA"
        assert fits_obj.num_frames_in_ramp == -99
        assert fits_obj.current_frame_in_ramp == -88

    else:
        assert fits_obj.camera_readout_mode == ramp_header["DLCAMSMD"]
        assert fits_obj.num_frames_in_ramp == ramp_header["DLCAMNS"]
        assert fits_obj.current_frame_in_ramp == ramp_header["DLCAMCUR"]


@pytest.mark.parametrize(
    "dither_mode_on",
    [pytest.param(False, id="dither_mode_off"), pytest.param(True, id="dither_mode_on")],
)
@pytest.mark.parametrize(
    "dither_step",
    [pytest.param(True, id="dither_step_true"), pytest.param(False, id="dither_step_false")],
)
def test_dlnirsp_l0_fits_access(dither_header, dither_mode_on, dither_step):
    """
    Given: A header with dither-related keys
    When: Parsing the header with `DlnirspL0FitsAccess`
    Then: The parsed properties are correct and `dither_step` is always 0 if `num_dither_steps` is 1.
    """
    fits_obj = DlnirspL0FitsAccess.from_header(dither_header)

    assert fits_obj.num_dither_steps is dither_mode_on + 1
    if not dither_mode_on:
        assert fits_obj.dither_step is 0
    else:
        assert fits_obj.dither_step == int(dither_step)
