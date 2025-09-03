import argparse
import json
import os
import sys
from pathlib import Path

from astropy.io import fits
from dkist_header_validator import spec122_validator
from dkist_processing_common.manual import ManualProcessing
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_service_configuration.logging import logger

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks.linearity_correction import LinearityCorrection
from dkist_processing_dlnirsp.tasks.parse import ParseL0DlnirspRampData
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_dev_mockers import (
    SetObserveIpStartTime,
)
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import (
    SaveLinearizedFiles,
)
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import (
    input_dataset_parameter_task_with_files,
)
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import (
    load_parsing_task,
)
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import (
    save_parsing_task,
)


def translate_task(suffix: str):
    class Translate122To214L0(WorkflowTaskBase):
        def run(self) -> None:
            raw_dir = Path(self.scratch.scratch_base_path) / f"DLNIRSP{self.recipe_run_id:03n}"
            if not self.scratch.workflow_base_path.exists():
                self.scratch.workflow_base_path.mkdir(parents=True, exist_ok=False)

            if not raw_dir.exists():
                raise FileNotFoundError(
                    f"Expected to find a raw DLNIRSP{self.recipe_run_id:03n} folder in {self.scratch.scratch_base_path}"
                )

            for file in raw_dir.glob(f"*.{suffix}"):
                translated_file_name = self.scratch.workflow_base_path / os.path.basename(file)
                logger.info(f"Translating {file} -> {translated_file_name}")
                hdl = fits.open(file)
                # Handle both compressed and uncompressed files...
                if len(hdl) > 1:
                    hdl_header = hdl[1].header
                    hdl_data = hdl[1].data
                else:
                    hdl_header = hdl[0].header
                    hdl_data = hdl[0].data
                header = spec122_validator.validate_and_translate_to_214_l0(
                    hdl_header, return_type=fits.HDUList
                )[0].header

                comp_hdu = fits.CompImageHDU(header=header, data=hdl_data)
                comp_hdl = fits.HDUList([fits.PrimaryHDU(), comp_hdu])
                comp_hdl.writeto(translated_file_name, overwrite=True)

                hdl.close()
                del hdl
                comp_hdl.close()
                del comp_hdl

    return Translate122To214L0


def tag_inputs_task(suffix: str):
    class TagInputs(WorkflowTaskBase):
        def run(self) -> None:
            logger.info(f"Looking in {self.scratch.workflow_base_path.absolute()}")
            input_file_list = list(self.scratch.workflow_base_path.glob(f"*.{suffix}"))
            if len(input_file_list) == 0:
                raise FileNotFoundError(
                    f"Did not find any files matching '*.{suffix}' in {self.scratch.workflow_base_path}"
                )
            for file in input_file_list:
                logger.info(f"Found {file}")
                self.tag(path=file, tags=[DlnirspTag.input(), DlnirspTag.frame()])

    return TagInputs


def setup_APM_config() -> None:
    mesh_config = {
        "system-monitoring-log-apm": {
            "mesh_address": "system-monitoring-log-apm.service.sim.consul",
            "mesh_port": 8200,
        },
        "automated-processing-scratch-inventory": {"mesh_address": "localhost", "mesh_port": 6379},
        "internal-api-gateway": {"mesh_address": "localhost", "mesh_port": 80},
    }
    apm_options = {"TRANSACTION_MAX_SPANS": 10000}
    os.environ["MESH_CONFIG"] = json.dumps(mesh_config)
    os.environ["ELASTIC_APM_ENABLED"] = "true"
    os.environ["ELASTIC_APM_OTHER_OPTIONS"] = json.dumps(apm_options)


def main(
    scratch_path: str,
    suffix: str = "FITS",
    recipe_run_id: int = 2,
    param_dir: str = "parameter_files",
    skip_translation: bool = False,
    only_translate: bool = False,
    load_input_parsing: bool = False,
    cals_only: bool = False,
    use_apm: bool = False,
):
    if use_apm:
        setup_APM_config()
    with ManualProcessing(
        workflow_path=Path(scratch_path),
        recipe_run_id=recipe_run_id,
        testing=True,
        workflow_name="dlnirsp-l0-to-l1",
        workflow_version="GROGU",
    ) as manual_processing_run:
        if not skip_translation:
            manual_processing_run.run_task(task=translate_task(suffix))
        if only_translate:
            return

        manual_processing_run.run_task(task=input_dataset_parameter_task_with_files(param_dir))

        manual_processing_run.run_task(task=tag_inputs_task(suffix))

        if load_input_parsing:
            manual_processing_run.run_task(task=load_parsing_task(save_file="input_parsing.asdf"))
        else:
            manual_processing_run.run_task(task=ParseL0DlnirspRampData)
            manual_processing_run.run_task(
                task=save_parsing_task(
                    tag_list=[DlnirspTag.input(), DlnirspTag.frame()],
                    save_file="input_parsing.asdf",
                    save_file_tags=True,
                )
            )

        if cals_only:
            manual_processing_run.run_task(task=SetObserveIpStartTime)

        manual_processing_run.run_task(task=LinearityCorrection)
        manual_processing_run.run_task(task=SaveLinearizedFiles)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run an end-to-end test of the DLNirsp DC Science pipeline"
    )
    parser.add_argument("scratch_path", help="Location to use as the DC 'scratch' disk")
    parser.add_argument(
        "-i",
        "--run-id",
        help="Which subdir to use. This will become the recipe run id",
        type=int,
        default=4,
    )
    parser.add_argument("--suffix", help="File suffix to treat as INPUT frames", default="FITS")
    parser.add_argument(
        "-T",
        "--skip-translation",
        help="Skip the translation of raw 122 l0 frames to 214 l0",
        action="store_true",
    )
    parser.add_argument(
        "-t", "--only-translate", help="Do ONLY the translation step", action="store_true"
    )
    parser.add_argument(
        "--cals-only",
        help="For if data are missing observe frame. Will mock the OBS_IP_START_TIME constant.",
        action="store_true",
    )
    parser.add_argument(
        "-I",
        "--load-input-parsing",
        help="Load tags and constants on input files",
        action="store_true",
    )
    parser.add_argument("-A", "--use-apm", help="Send APM spans to SIM", action="store_true")
    parser.add_argument(
        "-p",
        "--param-dir",
        help="Path to parameter directory",
        type=str,
        default=None,
    )

    args = parser.parse_args()
    sys.exit(
        main(
            scratch_path=args.scratch_path,
            suffix=args.suffix,
            recipe_run_id=args.run_id,
            param_dir=args.param_dir,
            skip_translation=args.skip_translation,
            only_translate=args.only_translate,
            load_input_parsing=args.load_input_parsing,
            cals_only=args.cals_only,
            use_apm=args.use_apm,
        )
    )
