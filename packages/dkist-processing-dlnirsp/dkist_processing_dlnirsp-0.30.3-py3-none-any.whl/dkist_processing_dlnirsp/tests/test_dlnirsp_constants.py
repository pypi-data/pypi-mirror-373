from dataclasses import asdict
from dataclasses import dataclass

import astropy.units as u
import pytest

from dkist_processing_dlnirsp.tasks.dlnirsp_base import DlnirspTaskBase


@dataclass
class test_constants:
    arm_id: str = "Arm"
    obs_ip_start_time: str = "2020-03-15"
    num_dither_steps: int = 1
    num_mosaic_repeats: int = 4
    num_mosaic_tiles_x: int = 3
    num_mosaic_tiles_y: int = 2
    time_obs_list: tuple[float] = (10.0,)
    wavelength: float = 1083.2
    lamp_gain_exposure_times: tuple[float] = (1.0,)
    solar_gain_exposure_times: tuple[float] = (2.0,)
    polcal_exposure_times: tuple[float] = (3.0,)
    observe_exposure_times: tuple[float] = (4.0,)
    num_modstates: int = 8
    polarimeter_mode: str = "Full Stokes"
    retarder_name: str = "SiO2 OC"
    solar_gain_ip_start_time: str = "2023-03-14"
    arm_position_mm: float = 39.2
    grating_constant_inverse_mm: float = 19.0
    grating_position_deg: float = 87.4
    # We don't need all the common ones, but let's put one just to check
    instrument: str = "CHECK_OUT_THIS_INSTRUMENT"


@pytest.fixture(scope="session")
def simple_constant_names():
    return [
        "arm_id",
        "num_dither_steps",
        "num_mosaic_repeats",
        "num_mosaic_tiles_x",
        "num_mosaic_tiles_y",
        "time_obs_list",
        "wavelength",
        "lamp_gain_exposure_times",
        "solar_gain_exposure_times",
        "observe_exposure_times",
        "num_modstates",
        "solar_gain_ip_start_time",
        "instrument",
    ]


@pytest.fixture(scope="session")
def unit_constant_names_and_units() -> list[tuple[str, u.Unit]]:
    return [
        ("grating_position_deg", u.deg),
        ("grating_constant_inverse_mm", 1 / u.mm),
        ("arm_position_mm", u.mm),
    ]


def make_upper_case_dict(data_obj) -> dict:
    lower_dict = asdict(data_obj)
    return {k.upper(): v for k, v in lower_dict.items()}


@pytest.fixture(scope="session")
def expected_constant_dict() -> dict:
    return make_upper_case_dict(test_constants())


@pytest.fixture(scope="function")
def dlnirsp_science_task_with_constants(recipe_run_id, expected_constant_dict, link_constants_db):
    class Task(DlnirspTaskBase):
        def run(self): ...

    link_constants_db(recipe_run_id, expected_constant_dict)
    task = Task(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="VX.Y",
    )

    yield task
    task._purge()


def test_simple_dlnirsp_constants(
    dlnirsp_science_task_with_constants, expected_constant_dict, simple_constant_names
):
    """
    Given: A Task class with DlnirspConstants as the constants class and a populated constant `_db_dict`
    When: Accessing the "simple" constants (i.e., those that just return a value directly from the db)
    Then: The correct values are returned
    """
    task = dlnirsp_science_task_with_constants
    for constant_name in simple_constant_names:
        expected_value = expected_constant_dict[constant_name.upper()]
        if type(expected_value) is tuple:
            expected_value = list(expected_value)
        assert getattr(task.constants, constant_name) == expected_value

    assert task.constants.num_beams == 2
    assert task.constants.num_slits == 4


def test_constants_with_units(
    dlnirsp_science_task_with_constants, expected_constant_dict, unit_constant_names_and_units
):
    """
    Given: A Task class with `DlnirspConstants` as the constants class and a populated constant `_db_dict`.
    When: Accessing constants that have associated units
    Then: The correct value with the correct unit are returned
    """
    task = dlnirsp_science_task_with_constants
    for constant_name, constant_unit in unit_constant_names_and_units:
        expected_value = expected_constant_dict[constant_name.upper()] * constant_unit
        assert getattr(task.constants, constant_name) == expected_value


@pytest.mark.parametrize(
    "is_polarimetric",
    [pytest.param(True, id="polarimetric"), pytest.param(False, id="spectrographic")],
)
def test_polcal_constants(dlnirsp_science_task_with_constants, is_polarimetric, link_constants_db):
    """
    Given: A Task class with DlnirspConstants as the constants class and a populated constant `_db_dict`
    When: Accessing constants that depend on whether the dataset is polarimetric or not
    Then: The correct values are returned
    """
    constants = test_constants(polarimeter_mode="Full Stokes" if is_polarimetric else "Stokes I")
    constants_dict = make_upper_case_dict(constants)

    task = dlnirsp_science_task_with_constants
    link_constants_db(task.recipe_run_id, constants_dict)

    if is_polarimetric:
        assert task.constants.correct_for_polarization
        assert task.constants.polcal_exposure_times == list(constants.polcal_exposure_times)
    else:
        assert not task.constants.correct_for_polarization
        assert task.constants.polcal_exposure_times == []
    assert task.constants.pac_init_set == "OCCal_VIS"


@pytest.mark.parametrize(
    "arm_id, is_IR",
    [
        pytest.param("VIS", False, id="VIS"),
        pytest.param("JBand", True, id="JBand"),
        pytest.param("HBand", True, id="HBand"),
    ],
)
def test_arm_constants(dlnirsp_science_task_with_constants, arm_id, is_IR, link_constants_db):
    """
    Given: A Task class with DlnirspConstants as the constants class and a populated constant `_db_dict`
    When: Accessing constants that depend on the arm id
    Then: The correct value is returned
    """
    constants = make_upper_case_dict(test_constants(arm_id=arm_id))
    task = dlnirsp_science_task_with_constants

    link_constants_db(task.recipe_run_id, constants)
    assert task.constants.is_ir_data is is_IR


def test_bad_arm_id(dlnirsp_science_task_with_constants, link_constants_db):
    """
    Given: A Task class with DlnirspConstants as the constants class and a `_db_dict` with an unexpected arm id
    When: Accessing constants that depend on the arm id
    Then: The correct error is raised
    """
    bad_arm = "SOMETHING_WRONG"
    constants = make_upper_case_dict(test_constants(arm_id=bad_arm))
    task = dlnirsp_science_task_with_constants

    link_constants_db(task.recipe_run_id, constants)
    with pytest.raises(
        ValueError, match=f"Unable to determine the camera type of Arm ID {bad_arm}"
    ):
        task.constants.is_ir_data
