"""Script for showing the slitbeam assignment based on a group_id array."""

from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np
from astropy.io import fits
from dkist_processing_common.models.input_dataset import InputDatasetParameterValue
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_service_configuration.logging import logger

from dkist_processing_dlnirsp.models.parameters import DlnirspParameters
from dkist_processing_dlnirsp.tasks.mixin.group_id import GroupIdMixin


class BlankTaskWithGroupId(WorkflowTaskBase, GroupIdMixin):
    """We just need this so we can use the group id mixin"""

    def run(self) -> None:
        pass


def mark_slitbeams(task: BlankTaskWithGroupId) -> np.ndarray:
    """Produce an array where each pixel's value is its slitbeam ID."""
    group_id_array = task.group_id_drifted_id_array
    slitbeam_group_dict = task.group_id_slitbeam_group_dict

    slitbeam_id_array = np.empty(group_id_array.shape) * np.nan
    for slitbeam, groups_in_slitbeam in slitbeam_group_dict.items():
        for group_id in groups_in_slitbeam:
            group_idx = task.group_id_get_idx(group_id=group_id)
            slitbeam_id_array[group_idx] = slitbeam

    return slitbeam_id_array


def create_parameter_dict(
    group_id_file_path: str | Path, slit_separation_px: int, arm_id: str
) -> dict[str, list[InputDatasetParameterValue]]:
    """Create a dictionary that can be used to instantiate a DlnirspParameters object."""
    param_dict = defaultdict(list)
    date = datetime(1946, 11, 20)
    param_dict["dlnirsp_group_id_rough_slit_separation_px"].append(
        InputDatasetParameterValue(
            parameter_value=slit_separation_px,
            parameter_value_id=0,
            parameter_value_start_date=date,
        )
    )
    file_param_dict = {"param_path": str(group_id_file_path.absolute()), "is_file": True}
    param_dict[f"dlnirsp_group_id_file_{arm_id.casefold()}"].append(
        InputDatasetParameterValue(
            parameter_value=file_param_dict, parameter_value_id=1, parameter_value_start_date=date
        )
    )

    return param_dict


def main(
    group_id_file_path: str | Path,
    output_file_name: str,
    arm_id: str,
    rough_slit_separation_px: int = 300,
) -> int:
    """Use provided group id file to make a slitbeam id file."""
    if isinstance(group_id_file_path, str):
        group_id_file_path = Path(group_id_file_path)

    logger.info("Setting up task and parameters")
    task = BlankTaskWithGroupId(
        recipe_run_id=0, workflow_name="test_group_id_assignment", workflow_version="0.0.0b1rc0"
    )

    loaded_parameter_dict = create_parameter_dict(
        group_id_file_path, rough_slit_separation_px, arm_id=arm_id
    )
    task.parameters = DlnirspParameters(
        loaded_parameter_dict, wavelength=1.0, arm_id=arm_id  # TODO: This won't work anymore
    )  # Wavelength doesn't matter

    logger.info("Creating slitbeam id array")
    slitbeam_array = mark_slitbeams(task)

    fits.PrimaryHDU(slitbeam_array).writeto(output_file_name, overwrite=True)
    logger.info(f"Slitbeam id array saved to {output_file_name}")

    return 0


def command_line():
    """Entry point for main() from command line."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Produce a FITS file showing the slitbeam each pixel is assigned to."
    )
    parser.add_argument(
        "-s",
        "--slit-separation-px",
        help="Rough distance between 2 DL slits (NOT slitbeams)",
        type=int,
        default=300,
    )
    parser.add_argument("-a", "--arm-id", help="Dlnirsp arm", type=str, default="JBand")
    parser.add_argument("group_id_file", help="Path to a group_id FITS file")
    parser.add_argument("output_file", help="Where to save slitbeam assignment file")

    args = parser.parse_args()
    sys.exit(
        main(
            group_id_file_path=args.group_id_file,
            output_file_name=args.output_file,
            rough_slit_separation_px=args.slit_separation_px,
            arm_id=args.arm_id,
        )
    )
