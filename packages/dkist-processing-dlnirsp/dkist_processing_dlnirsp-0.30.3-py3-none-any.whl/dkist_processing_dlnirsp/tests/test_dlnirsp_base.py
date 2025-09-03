import pytest

from dkist_processing_dlnirsp.models.constants import DlnirspConstants
from dkist_processing_dlnirsp.models.parameters import DlnirspParameters
from dkist_processing_dlnirsp.tasks.dlnirsp_base import DlnirspTaskBase
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingConstants


@pytest.fixture()
def dummy_arm_id() -> str:
    return "ARMY_MCARMFACE"


@pytest.fixture
def dlnirsp_science_task(session_recipe_run_id, session_link_constants_db, dummy_arm_id):
    class Task(DlnirspTaskBase):
        def run(self) -> None:
            pass

    session_link_constants_db(
        recipe_run_id=session_recipe_run_id,
        constants_obj=DlnirspTestingConstants(ARM_ID=dummy_arm_id),
    )

    with Task(
        recipe_run_id=session_recipe_run_id,
        workflow_name="dlnirsp_base_test",
        workflow_version="x.y.z",
    ) as task:
        yield task
        task._purge()


def test_base_constants_class(dlnirsp_science_task, dummy_arm_id):
    """
    Given: A Science task made from a DL task base
    When: Instantiating the class
    Then: The task's constants object is a DlnirspConstants object
    """
    task = dlnirsp_science_task

    assert type(task.constants) is DlnirspConstants
    assert task.constants.arm_id == dummy_arm_id


def test_base_parameters_class(dlnirsp_science_task, dummy_arm_id):
    """
    Given: A Science task made from a DL task base
    When: Instantiating the class
    Then: DlnirspTaskBase has a DlnirspParameters object and DlnirspLinearityTaskBase doesn't have any parameters
    """
    task = dlnirsp_science_task

    if isinstance(task, DlnirspTaskBase):
        assert type(task.parameters) is DlnirspParameters
        assert task.parameters._arm_id == dummy_arm_id.casefold()
    else:
        with pytest.raises(AttributeError):
            task.parameters
