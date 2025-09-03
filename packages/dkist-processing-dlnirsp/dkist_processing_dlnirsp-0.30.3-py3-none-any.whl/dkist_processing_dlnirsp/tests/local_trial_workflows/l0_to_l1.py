import argparse
import json
import os
import sys
from pathlib import Path

from astropy.io import fits
from dkist_header_validator import spec122_validator
from dkist_processing_common.manual import ManualProcessing
from dkist_processing_common.tasks import CreateTrialAsdf
from dkist_processing_common.tasks import CreateTrialQualityReport
from dkist_processing_common.tasks import QualityL1Metrics
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_service_configuration.logging import logger

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks.assemble_movie import AssembleDlnirspMovie
from dkist_processing_dlnirsp.tasks.bad_pixel_map import BadPixelCalibration
from dkist_processing_dlnirsp.tasks.dark import DarkCalibration
from dkist_processing_dlnirsp.tasks.geometric import GeometricCalibration
from dkist_processing_dlnirsp.tasks.ifu_drift import IfuDriftCalibration
from dkist_processing_dlnirsp.tasks.instrument_polarization import InstrumentPolarizationCalibration
from dkist_processing_dlnirsp.tasks.l1_output_data import DlnirspAssembleQualityData
from dkist_processing_dlnirsp.tasks.lamp import LampCalibration
from dkist_processing_dlnirsp.tasks.linearity_correction import LinearityCorrection
from dkist_processing_dlnirsp.tasks.make_movie_frames import MakeDlnirspMovieFrames
from dkist_processing_dlnirsp.tasks.parse import ParseL0DlnirspLinearizedData
from dkist_processing_dlnirsp.tasks.parse import ParseL0DlnirspRampData
from dkist_processing_dlnirsp.tasks.quality_metrics import DlnirspL0QualityMetrics
from dkist_processing_dlnirsp.tasks.quality_metrics import DlnirspL1QualityMetrics
from dkist_processing_dlnirsp.tasks.science import ScienceCalibration
from dkist_processing_dlnirsp.tasks.solar import SolarCalibration
from dkist_processing_dlnirsp.tasks.wavelength_calibration import WavelengthCalibration
from dkist_processing_dlnirsp.tasks.write_l1 import DlnirspWriteL1Frame
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import LoadBadPixelCal
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import (
    LoadCalibratedData,
)
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import LoadDarkCal
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import (
    LoadGeometricCal,
)
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import LoadIfuDriftCal
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import LoadInstPolCal
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import LoadLampCal
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import (
    LoadLinearizedFiles,
)
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import LoadSolarCal
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import (
    LoadWavelengthCal,
)
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import SaveBadPixelCal
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import (
    SaveCalibratedData,
)
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import SaveDarkCal
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import (
    SaveGeometricCal,
)
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import SaveIfuDriftCal
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import SaveInstPolCal
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import SaveLampCal
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import (
    SaveLinearizedFiles,
)
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import SaveSolarCal
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import (
    SaveWavelengthCal,
)
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import (
    ValidateL1Output,
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
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_helpers import (
    transfer_trial_data_locally,
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


def tag_linearized_task(suffix: str):
    class TagLinearized(WorkflowTaskBase):
        def run(self) -> None:
            logger.info(f"Looking in {self.scratch.workflow_base_path.absolute()}")
            input_file_list = list(self.scratch.workflow_base_path.glob(f"*.{suffix}"))
            if len(input_file_list) == 0:
                raise FileNotFoundError(
                    f"Did not find any files matching '*.{suffix}' in {self.scratch.workflow_base_path}"
                )
            for file in input_file_list:
                logger.info(f"Found {file}")
                self.tag(path=file, tags=[DlnirspTag.linearized_frame()])

    return TagLinearized


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
    load_linearized: bool = False,
    load_linearized_parsing: bool = False,
    load_dark: bool = False,
    load_drift: bool = False,
    load_lamp: bool = False,
    load_bad_pixel: bool = False,
    load_geometric: bool = False,
    load_wavelength_calibration: bool = False,
    load_solar: bool = False,
    load_inst_polcal: bool = False,
    load_calibrated_data: bool = False,
    transfer_trial_data: str | None = None,
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

        if not load_linearized:
            manual_processing_run.run_task(task=tag_inputs_task(suffix))

        if load_input_parsing or load_linearized:
            manual_processing_run.run_task(task=load_parsing_task(save_file="input_parsing.asdf"))
        else:
            manual_processing_run.run_task(task=ParseL0DlnirspRampData)
            manual_processing_run.run_task(
                task=save_parsing_task(
                    tag_list=[DlnirspTag.input(), DlnirspTag.frame()],
                    save_file="input_parsing.asdf",
                    save_file_tags=False,
                )
            )

        if load_linearized:
            manual_processing_run.run_task(task=LoadLinearizedFiles)
        else:
            manual_processing_run.run_task(task=LinearityCorrection)
            manual_processing_run.run_task(task=SaveLinearizedFiles)
            manual_processing_run.run_task(task=LoadLinearizedFiles)

        if load_linearized_parsing:
            manual_processing_run.run_task(
                task=load_parsing_task(save_file="linearized_parsing.asdf")
            )
        else:
            manual_processing_run.run_task(task=ParseL0DlnirspLinearizedData)
            manual_processing_run.run_task(
                task=save_parsing_task(
                    tag_list=[DlnirspTag.linearized_frame()],
                    save_file="linearized_parsing.asdf",
                )
            )

        if load_dark:
            manual_processing_run.run_task(task=LoadDarkCal)
        else:
            manual_processing_run.run_task(task=DarkCalibration)
            manual_processing_run.run_task(task=SaveDarkCal)

        if load_drift:
            manual_processing_run.run_task(task=LoadIfuDriftCal)
        else:
            manual_processing_run.run_task(task=IfuDriftCalibration)
            manual_processing_run.run_task(task=SaveIfuDriftCal)

        if load_lamp:
            manual_processing_run.run_task(task=LoadLampCal)
        else:
            manual_processing_run.run_task(task=LampCalibration)
            manual_processing_run.run_task(task=SaveLampCal)

        if load_bad_pixel:
            manual_processing_run.run_task(task=LoadBadPixelCal)
        else:
            manual_processing_run.run_task(task=BadPixelCalibration)
            manual_processing_run.run_task(task=SaveBadPixelCal)

        if load_geometric:
            manual_processing_run.run_task(task=LoadGeometricCal)
        else:
            manual_processing_run.run_task(task=GeometricCalibration)
            manual_processing_run.run_task(task=SaveGeometricCal)

        if load_wavelength_calibration:
            manual_processing_run.run_task(task=LoadWavelengthCal)
        else:
            manual_processing_run.run_task(task=WavelengthCalibration)
            manual_processing_run.run_task(task=SaveWavelengthCal)

        if load_solar:
            manual_processing_run.run_task(task=LoadSolarCal)
        else:
            manual_processing_run.run_task(task=SolarCalibration)
            manual_processing_run.run_task(task=SaveSolarCal)

        if load_inst_polcal:
            manual_processing_run.run_task(task=LoadInstPolCal)
        else:
            manual_processing_run.run_task(task=InstrumentPolarizationCalibration)
            manual_processing_run.run_task(task=SaveInstPolCal)

        if load_calibrated_data:
            manual_processing_run.run_task(task=LoadCalibratedData)
        else:
            manual_processing_run.run_task(task=ScienceCalibration)
            manual_processing_run.run_task(task=SaveCalibratedData)

        manual_processing_run.run_task(task=DlnirspWriteL1Frame)
        manual_processing_run.run_task(task=ValidateL1Output)
        manual_processing_run.run_task(task=MakeDlnirspMovieFrames)
        manual_processing_run.run_task(task=AssembleDlnirspMovie)

        manual_processing_run.run_task(task=DlnirspL0QualityMetrics)
        manual_processing_run.run_task(task=DlnirspL1QualityMetrics)
        manual_processing_run.run_task(task=QualityL1Metrics)
        manual_processing_run.run_task(task=DlnirspAssembleQualityData)

        manual_processing_run.run_task(task=CreateTrialQualityReport)

        manual_processing_run.run_task(task=CreateTrialAsdf)

        if transfer_trial_data:
            transfer_trial_data_locally(
                trial_output_location=transfer_trial_data, processing_run=manual_processing_run
            )

        if any(
            [load_linearized, load_dark, load_lamp, load_geometric, load_solar, load_inst_polcal]
        ):
            logger.info("NOT counting provenance records because some tasks were skipped")
        else:
            manual_processing_run.count_provenance()


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
        "-X",
        "--transfer-trial-data",
        help="Transfer trial data to a different location.",
        metavar="trial_output_location",
        nargs="?",
        const="default",
        default=None,
    )
    parser.add_argument(
        "-I",
        "--load-input-parsing",
        help="Load tags and constants on input files",
        action="store_true",
    )
    parser.add_argument(
        "-Z",
        "--load-linearized",
        help="Load linearized tags from a previous run",
        action="store_true",
    )
    parser.add_argument(
        "-R",
        "--load-linearized-parsing",
        help="Load tags and constants from linearized files",
        action="store_true",
    )
    parser.add_argument(
        "-D",
        "--load-dark",
        help="Load dark calibration from previously saved run",
        action="store_true",
    )
    parser.add_argument(
        "-F",
        "--load-drift",
        help="Load IFU drift calibration from previously saved run",
        action="store_true",
    )
    parser.add_argument(
        "-L",
        "--load-lamp",
        help="Load lamp calibration from previously saved run",
        action="store_true",
    )
    parser.add_argument(
        "-M",
        "--load-bad-pixel",
        help="Load bad pixel calibration from previously saved run",
        action="store_true",
    )
    parser.add_argument(
        "-G",
        "--load-geometric",
        help="Load geometric calibration from previously saved run",
        action="store_true",
    )
    parser.add_argument(
        "-W",
        "--load-wavelength-calibration",
        help="Load wavelength calibration solution from previously saved run",
        action="store_true",
    )
    parser.add_argument(
        "-S",
        "--load-solar",
        help="Load solar calibration from previously saved run",
        action="store_true",
    )
    parser.add_argument(
        "-P",
        "--load-inst-polcal",
        help="Load instrument polarization calibration from previously saved run",
        action="store_true",
    )
    parser.add_argument(
        "-C", "--load-calibrated-data", help="Load CALIBRATED science frames", action="store_true"
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
            load_linearized=args.load_linearized,
            load_linearized_parsing=args.load_linearized_parsing,
            load_dark=args.load_dark,
            load_drift=args.load_drift,
            load_lamp=args.load_lamp,
            load_bad_pixel=args.load_bad_pixel,
            load_geometric=args.load_geometric,
            load_wavelength_calibration=args.load_wavelength_calibration,
            load_solar=args.load_solar,
            load_inst_polcal=args.load_inst_polcal,
            load_calibrated_data=args.load_calibrated_data,
            transfer_trial_data=args.transfer_trial_data,
            use_apm=args.use_apm,
        )
    )
