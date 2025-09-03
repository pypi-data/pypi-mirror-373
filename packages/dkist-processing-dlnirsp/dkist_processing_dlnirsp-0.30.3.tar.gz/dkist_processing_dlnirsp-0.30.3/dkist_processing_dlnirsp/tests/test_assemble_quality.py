from unittest.mock import MagicMock

import pytest

from dkist_processing_dlnirsp.tasks.l1_output_data import DlnirspAssembleQualityData


@pytest.fixture
def dlnirsp_assemble_quality_data_task(tmp_path, recipe_run_id) -> DlnirspAssembleQualityData:

    with DlnirspAssembleQualityData(
        recipe_run_id=recipe_run_id,
        workflow_name="dlnirsp_assemble_quality",
        workflow_version="VX.Y",
    ) as task:
        yield task
        task._purge()


@pytest.fixture
def dummy_quality_data() -> list[dict]:
    return [{"dummy_key": "dummy_value"}]


@pytest.fixture
def quality_assemble_data_mock(mocker, dummy_quality_data) -> MagicMock:
    yield mocker.patch(
        "dkist_processing_common.tasks.mixin.quality.QualityMixin.quality_assemble_data",
        return_value=dummy_quality_data,
        autospec=True,
    )


def test_correct_polcal_label_list(
    dlnirsp_assemble_quality_data_task, polcal_quality_beam_labels, quality_assemble_data_mock
):
    """
    Given: A DlnirspAssembleQualityData task
    When: Calling the task
    Then: The correct polcal_label_list property is passed to .quality_assemble_data
    """
    task = dlnirsp_assemble_quality_data_task

    task()
    quality_assemble_data_mock.assert_called_once_with(
        task, polcal_label_list=polcal_quality_beam_labels
    )
