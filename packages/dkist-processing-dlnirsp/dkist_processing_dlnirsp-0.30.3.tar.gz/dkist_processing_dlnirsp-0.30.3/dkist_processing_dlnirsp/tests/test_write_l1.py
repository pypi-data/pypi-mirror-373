import astropy.units as u
import pytest
from astropy.io import fits
from astropy.time import Time
from dkist_fits_specifications import __version__ as spec_version
from dkist_header_validator import spec214_validator
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.json import json_encoder
from dkist_processing_common.models.wavelength import WavelengthRange
from dkist_spectral_lines import get_closest_spectral_line
from dkist_spectral_lines import get_spectral_lines

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks.write_l1 import DlnirspWriteL1Frame
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingConstants
from dkist_processing_dlnirsp.tests.conftest import write_calibrated_frames_to_task


@pytest.fixture
def write_l1_task(recipe_run_id, tmp_path):
    with DlnirspWriteL1Frame(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)

        yield task
        task._purge()


@pytest.fixture(scope="session")
def wavelength_solution_header() -> dict[str, str | int | float]:
    # None of these values matter
    return {
        "CTYPE3": "AWAV-GRA",
        "CUNIT3": "um",
        "CRPIX3": 34.5,
        "CRVAL3": 1083.0,
        "CDELT3": 0.006,
        "PV3_0": 63.0,
        "PV3_1": 51,
        "PV3_2": 2300,
    }


@pytest.fixture
def wavelength_range():
    return WavelengthRange(min=1564.0 * u.nm, max=1566.0 * u.nm)


@pytest.fixture
def mocked_get_wavelength_range(wavelength_range):
    def get_wavelength_range(self, header):
        return wavelength_range

    return get_wavelength_range


@pytest.mark.parametrize(
    "dither_mode_on",
    [pytest.param(True, id="dither_mode_on"), pytest.param(False, id="dither_mode_off")],
)
@pytest.mark.parametrize(
    "has_multiple_mosaics",
    [pytest.param(True, id="multi_mosaic"), pytest.param(False, id="single_mosaic")],
)
@pytest.mark.parametrize(
    "is_polarimetric",
    [pytest.param(True, id="polarimetric"), pytest.param(False, id="spectrographic")],
)
@pytest.mark.parametrize(
    "is_mosaiced", [pytest.param(True, id="mosaiced"), pytest.param(False, id="no_mosaic")]
)
def test_write_l1(
    write_l1_task,
    has_multiple_mosaics,
    is_polarimetric,
    dither_mode_on,
    is_mosaiced,
    wavelength_range,
    wavelength_solution_header,
    link_constants_db,
    mocked_get_wavelength_range,
    mocker,
    fake_gql_client,
):
    """
    Given: A DlnirspWriteL1Frame task with CALIBRATED frames
    When: Running the task
    Then: The OUTPUT frames are created and have correct headers
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    mocker.patch(
        "dkist_processing_dlnirsp.tasks.write_l1.DlnirspWriteL1Frame.get_wavelength_range",
        mocked_get_wavelength_range,
    )

    num_dither = 2 if dither_mode_on else 1
    num_mosaics = 2 if has_multiple_mosaics else 1
    num_X_tiles = 2 if is_mosaiced else 1
    num_Y_tiles = 2 if is_mosaiced else 1
    stokes_params = ["I"]
    if is_polarimetric:
        stokes_params += ["Q", "U", "V"]
        num_modstates = 8
        pol_mode = "Full Stokes"
    else:
        num_modstates = 1
        pol_mode = "Stokes I"

    expected_spectral_lines = get_spectral_lines(
        wavelength_min=wavelength_range.min,
        wavelength_max=wavelength_range.max,
    )
    expected_waveband = get_closest_spectral_line(
        wavelength=1565.0 * u.nm
    ).name  # From DlnirspHeaders fixture

    task = write_l1_task

    constants_db = DlnirspTestingConstants(
        POLARIMETER_MODE=pol_mode,
        NUM_DITHER_STEPS=num_dither,
        NUM_MOSAIC_REPEATS=num_mosaics,
        NUM_MOSAIC_TILES_X=num_X_tiles,
        NUM_MOSAIC_TILES_Y=num_Y_tiles,
        NUM_MODSTATES=num_modstates,
    )
    link_constants_db(task.recipe_run_id, constants_db)

    write_calibrated_frames_to_task(
        task,
        num_mosaics=num_mosaics,
        num_X_tiles=num_X_tiles,
        num_Y_tiles=num_Y_tiles,
        dither_mode_on=dither_mode_on,
        is_polarimetric=is_polarimetric,
        array_shape=(5, 6, 7),
    )

    task.write(
        data=wavelength_solution_header,
        tags=[DlnirspTag.intermediate(), DlnirspTag.task_wavelength_solution()],
        encoder=json_encoder,
    )

    task()

    for stokes in stokes_params:
        output_files = list(
            task.read(
                tags=[
                    DlnirspTag.output(),
                    DlnirspTag.frame(),
                    DlnirspTag.stokes(stokes),
                ]
            )
        )
        assert len(output_files) == num_mosaics * num_dither * num_X_tiles * num_Y_tiles
        calibrated_files = list(
            task.read(
                tags=[
                    DlnirspTag.frame(),
                    DlnirspTag.calibrated(),
                    DlnirspTag.stokes(stokes),
                ]
            )
        )
        assert len(calibrated_files) == num_mosaics * num_dither * num_X_tiles * num_Y_tiles

        # Make sure we didn't overwrite pre-computed DATE-BEG and DATE-END keys
        cal_headers = [fits.getheader(f) for f in calibrated_files]
        output_headers = [fits.getheader(f, ext=1) for f in output_files]

        assert sorted([h["DATE-BEG"] for h in cal_headers]) == sorted(
            [h["DATE-BEG"] for h in output_headers]
        )
        assert sorted([h["DATE-END"] for h in cal_headers]) == sorted(
            [h["DATE-END"] for h in output_headers]
        )

        for file in output_files:
            assert file.exists()
            assert spec214_validator.validate(file, extra=False)
            hdu_list = fits.open(file)
            header = hdu_list[1].header
            assert len(hdu_list) == 2
            assert type(hdu_list[0]) is fits.PrimaryHDU
            assert type(hdu_list[1]) is fits.CompImageHDU
            # assert header["DNAXIS1"] ==
            assert header["DTYPE1"] == "SPATIAL"
            assert header["DPNAME1"] == "helioprojective longitude"
            assert header["DWNAME1"] == "helioprojective longitude"
            assert header["DUNIT1"] == header["CUNIT1"]
            assert header["DTYPE2"] == "SPATIAL"
            assert header["DPNAME2"] == "helioprojective latitude"
            assert header["DWNAME2"] == "helioprojective latitude"
            assert header["DUNIT2"] == header["CUNIT2"]
            assert header["DTYPE3"] == "SPECTRAL"
            assert header["DPNAME3"] == "dispersion axis"
            assert header["DWNAME3"] == "wavelength"
            assert header["DUNIT3"] == header["CUNIT3"]
            assert header["DAAXES"] == 3

            for k, v in wavelength_solution_header.items():
                assert header[k] == v

            next_axis_num = 4
            if has_multiple_mosaics:
                assert header["DNAXIS4"] == num_mosaics
                assert header["DTYPE4"] == "TEMPORAL"
                assert header["DPNAME4"] == "mosaic repeat number"
                assert header["DWNAME4"] == "time"
                assert header["DUNIT4"] == "s"
                next_axis_num += 1

            if dither_mode_on:
                assert header[f"DNAXIS{next_axis_num}"] == num_dither
                assert header[f"DTYPE{next_axis_num}"] == "TEMPORAL"
                assert header[f"DPNAME{next_axis_num}"] == "dither step"
                assert header[f"DWNAME{next_axis_num}"] == "time"
                assert header[f"DUNIT{next_axis_num}"] == "s"
                assert header[f"DINDEX{next_axis_num}"] in [1, 2]
                next_axis_num += 1

            if is_polarimetric:
                assert header[f"DNAXIS{next_axis_num}"] == 4
                assert header[f"DTYPE{next_axis_num}"] == "STOKES"
                assert header[f"DPNAME{next_axis_num}"] == "polarization state"
                assert header[f"DWNAME{next_axis_num}"] == "polarization state"
                assert header[f"DUNIT{next_axis_num}"] == ""
                assert header[f"DINDEX{next_axis_num}"] == stokes_params.index(stokes) + 1

            if is_mosaiced:
                assert header["MAXIS"] == 2
                assert header["MAXIS1"] == num_X_tiles
                assert header["MAXIS2"] == num_Y_tiles
                # Test of correct MINDEX assignement is in test_science
                assert "MINDEX1" in header
                assert "MINDEX2" in header
            else:
                assert "MAXIS" not in header
                assert "MAXIS1" not in header
                assert "MAXIS2" not in header
                assert "MINDEX1" not in header
                assert "MINDEX2" not in header

            assert header["INFO_URL"] == task.docs_base_url
            assert header["HEADVERS"] == spec_version
            assert (
                header["HEAD_URL"]
                == f"{task.docs_base_url}/projects/data-products/en/v{spec_version}"
            )
            calvers = task.version_from_module_name()
            assert header["CALVERS"] == calvers
            assert (
                header["CAL_URL"]
                == f"{task.docs_base_url}/projects/{task.constants.instrument.lower()}/en/v{calvers}/{task.workflow_name}.html"
            )

            date_avg = (
                (Time(header["DATE-END"], precision=6) - Time(header["DATE-BEG"], precision=6)) / 2
                + Time(header["DATE-BEG"], precision=6)
            ).isot
            assert header["DATE-AVG"] == date_avg
            assert isinstance(header["HLSVERS"], str)
            assert header["PROPID01"] == "PROPID1"
            assert header["PROPID02"] == "PROPID2"
            assert header["EXPRID01"] == "EXPERID1"
            assert header["EXPRID02"] == "EXPERID2"
            assert header["EXPRID03"] == "EXPERID3"
            assert header["WAVEBAND"] == expected_waveband
            assert header["BUNIT"] == ""
            assert (
                header.comments["BUNIT"]
                == "Values are relative to disk center. See calibration docs."
            )
            for i, line in enumerate(expected_spectral_lines, start=1):
                assert header[f"SPECLN{i:02}"] == line.name

            with pytest.raises(KeyError):
                # Make sure no more lines were added
                header[f"SPECLN{i+1:02}"]


def test_get_wavelength_range(write_l1_task):
    """
    Given: A FITS header with WCS information
    When: Passing the header into `get_wavelength_range`
    Then: The correct wavelength range is returned
    """
    # (Because we mocked this method out in the task test above)
    header = fits.Header()
    header["NAXIS3"] = 10
    header["CUNIT3"] = "m"  # To test that the nm conversion happens
    header["CRPIX3"] = 5
    header["CDELT3"] = 2e-9
    header["CRVAL3"] = 0

    result = write_l1_task.get_wavelength_range(header)
    assert isinstance(result, WavelengthRange)
    assert u.allclose(result.min, -10 * u.nm)
    assert u.allclose(result.max, 10 * u.nm)


@pytest.mark.parametrize(
    "is_polarimetric",
    [pytest.param(True, id="polarimetric"), pytest.param(False, id="spectrographic")],
)
@pytest.mark.parametrize(
    "num_X_tiles, num_Y_tiles", [pytest.param(1, 2, id="X_loop"), pytest.param(2, 1, id="Y_loop")]
)
def test_mosaic_loop_as_time(
    write_l1_task,
    num_X_tiles,
    num_Y_tiles,
    is_polarimetric,
    wavelength_solution_header,
    link_constants_db,
    mocker,
    fake_gql_client,
):
    """
    Given: A DlnirspWriteL1Frame task and data where the temporal loop was put into a 1D mosaic
    When: Running the task
    Then: The mosaic loop is correctly used as the temporal axis and the mosaic keys don't exist
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    constants_db = DlnirspTestingConstants(
        NUM_MOSAIC_REPEATS=1,
        NUM_MOSAIC_TILES_X=num_X_tiles,
        NUM_MOSAIC_TILES_Y=num_Y_tiles,
        NUM_MODSTATES=8 if is_polarimetric else 1,
        POLARIMETER_MODE="Full Stokes" if is_polarimetric else "Stokes I",
    )
    task = write_l1_task
    link_constants_db(task.recipe_run_id, constants_db)

    write_calibrated_frames_to_task(
        task,
        num_mosaics=1,
        num_X_tiles=num_X_tiles,
        num_Y_tiles=num_Y_tiles,
        is_polarimetric=is_polarimetric,
        array_shape=(3, 4, 5),
    )

    task.write(
        data=wavelength_solution_header,
        tags=[DlnirspTag.intermediate(), DlnirspTag.task_wavelength_solution()],
        encoder=json_encoder,
    )

    task()

    output_frames = list(task.read([DlnirspTag.output(), DlnirspTag.frame()]))
    assert len(output_frames) > 0
    for file in output_frames:
        hdul = fits.open(file)
        header = hdul[1].header
        assert "MAXIS" not in header
        assert "MAXIS1" not in header
        assert "MAXIS2" not in header
        assert "MINDEX1" not in header
        assert "MINDEX2" not in header
        assert header["DNAXIS4"] == (num_X_tiles if num_X_tiles > 1 else num_Y_tiles)
