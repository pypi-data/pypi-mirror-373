import json
import os
import shutil
from dataclasses import asdict
from pathlib import Path
from random import randint

import asdf
import numpy as np
from astropy.io import fits
from astropy.table import Table
from dkist_header_validator import spec214_validator
from dkist_processing_common.codecs.basemodel import basemodel_encoder
from dkist_processing_common.manual import ManualProcessing
from dkist_processing_common.models.input_dataset import InputDatasetPartDocumentList
from dkist_processing_common.models.metric_code import MetricCode
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tasks import WorkflowTaskBase
from loguru import logger

from dkist_processing_dlnirsp.models.constants import DlnirspBudName
from dkist_processing_dlnirsp.models.constants import DlnirspConstants
from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.models.task_name import DlnirspTaskName
from dkist_processing_dlnirsp.tasks.dlnirsp_base import DlnirspTaskBase
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingParameters
from dkist_processing_dlnirsp.tests.conftest import FileParameter
from dkist_processing_dlnirsp.tests.local_trial_workflows.local_trial_dev_mockers import (
    transfer_trial_data_locally_task,
)


def get_camera_number(scratch_dir: Path, suffix: str = "FITS", data_ext: int = 1) -> int:
    glob_str = f"*.{suffix}"
    file_list = list(scratch_dir.glob(glob_str))
    logger.info(f"Found {len(file_list)} files in {str(scratch_dir)}")

    header_list = [fits.getheader(f, ext=data_ext) for f in file_list]
    table = Table(header_list)

    camera_IDs = np.unique(table["DLARMID"])
    if camera_IDs.size > 1:
        raise ValueError(f"Found more than one arm in scratch dir. Found {camera_IDs}")

    match camera_IDs[0]:

        case "VIS":
            cam_number = 1

        case "JBand":
            cam_number = 2

        case "HBand":
            cam_number = 3

        case _:
            raise ValueError(f"I don't know about ARMID {camera_IDs[0]}")

    logger.info(f"{camera_IDs[0]} => {cam_number = }")
    return cam_number


def transfer_trial_data_locally(
    trial_output_location: str, processing_run: ManualProcessing
) -> None:
    if trial_output_location == "default":
        trial_output_dir = (
            Path(processing_run.workflow_path) / str(processing_run.recipe_run_id) / "trial_output"
        )
    else:
        trial_output_dir = Path(trial_output_location).absolute()

    logger.info(f"Writing trial output to {trial_output_dir}")
    transfer_local_task = transfer_trial_data_locally_task(trial_dir=trial_output_dir)
    processing_run.run_task(transfer_local_task)


def input_dataset_parameter_task_with_files(param_dir: str | Path):

    if isinstance(param_dir, str):
        param_dir = Path(param_dir)

    parameter_data = DlnirspTestingParameters(
        dlnirsp_geo_spectral_edge_trim=10,
        dlnirsp_group_id_rough_slit_separation_px=300,
        dlnirsp_wcs_crpix_correction_method="flip_crpix1",
    )

    for arm_id in ["vis", "jband", "hband"]:
        static_bad_pixel_map_file_name = f"dlnirsp_static_bad_pixel_map_{arm_id}.dat"
        setattr(
            parameter_data,
            f"dlnirsp_static_bad_pixel_map_{arm_id}",
            FileParameter(object_key=static_bad_pixel_map_file_name),
        )

        group_id_file_name = f"dlnirsp_ifu_id_array_{arm_id}.dat"
        setattr(
            parameter_data,
            f"dlnirsp_group_id_file_{arm_id}",
            FileParameter(object_key=group_id_file_name),
        )

        dispersion_file_name = f"dlnirsp_dispersion_array_{arm_id}.dat"
        setattr(
            parameter_data,
            f"dlnirsp_geo_dispersion_file_{arm_id}",
            FileParameter(object_key=dispersion_file_name),
        )

        ifu_x_pos_file_name = f"dlnirsp_ifu_xpos_array_{arm_id}.dat"
        setattr(
            parameter_data,
            f"dlnirsp_ifu_x_pos_file_{arm_id}",
            FileParameter(object_key=ifu_x_pos_file_name),
        )

        ifu_y_pos_file_name = f"dlnirsp_ifu_ypos_array_{arm_id}.dat"
        setattr(
            parameter_data,
            f"dlnirsp_ifu_y_pos_file_{arm_id}",
            FileParameter(object_key=ifu_y_pos_file_name),
        )

    class CreateInputDatasetParameterDocument(WorkflowTaskBase):
        def run(self) -> None:
            relative_path = "input_dataset_parameters.json"
            self.write(
                data=InputDatasetPartDocumentList(
                    doc_list=self.input_dataset_document_simple_parameters_part
                ),
                relative_path=relative_path,
                tags=DlnirspTag.input_dataset_parameters(),
                encoder=basemodel_encoder,
                overwrite=True,
            )
            logger.info(f"Wrote input dataset parameter doc to {relative_path}")
            self.copy_and_tag_parameter_files(param_dir=param_dir)
            logger.info(f"Copied input dataset parameter files from {param_dir}")

        @property
        def input_dataset_document_simple_parameters_part(self):
            parameters_list = []
            value_id = randint(1000, 2000)
            for pn, pv in asdict(parameter_data).items():
                if isinstance(pv, FileParameter):
                    pv = pv.model_dump()
                values = [
                    {
                        "parameterValueId": value_id,
                        "parameterValue": json.dumps(pv),
                        "parameterValueStartDate": "1946-11-20",
                    }
                ]
                parameter = {"parameterName": pn, "parameterValues": values}
                parameters_list.append(parameter)

            return parameters_list

        def copy_and_tag_parameter_files(self, param_dir=param_dir):
            # Copy parameter files from param_dir to a place where they can be tagged
            destination_dir = Path(self.scratch.workflow_base_path) / "parameters"
            destination_dir.mkdir(parents=True, exist_ok=True)
            for pn, pv in asdict(parameter_data).items():
                if isinstance(pv, FileParameter):
                    file_path = next(param_dir.rglob(pv.file_pointer.object_key))
                    if file_path.parent != destination_dir:
                        shutil.copy(file_path, destination_dir)
                        logger.info(
                            f"Copied parameter file for '{pn}' to {destination_dir / file_path}"
                        )
                        file_path = next(destination_dir.rglob(pv.file_pointer.object_key))
                    self.tag(path=file_path, tags=pv.file_pointer.tag)

    return CreateInputDatasetParameterDocument


class ValidateL1Output(DlnirspTaskBase):
    def run(self) -> None:
        files = self.read(tags=[DlnirspTag.output(), DlnirspTag.frame()])
        for f in files:
            logger.info(f"Validating {f}")
            spec214_validator.validate(f, extra=False)


class SaveLinearizedFiles(WorkflowTaskBase):
    """Save linearized files and their tags to a directory and asdf file."""

    @property
    def relative_save_file(self) -> str:
        return "linearized.asdf"

    def run(self):
        file_tag_dict = dict()
        path_list = self.read(tags=[DlnirspTag.linearized()])
        save_dir = self.scratch.workflow_base_path / Path(self.relative_save_file).stem
        save_dir.mkdir(exist_ok=True)
        for p in path_list:
            copied_path = shutil.move(str(p), save_dir)
            tags = self.tags(p)
            file_tag_dict[copied_path] = tags

        full_save_file = self.scratch.workflow_base_path / self.relative_save_file
        tree = {"file_tag_dict": file_tag_dict}
        af = asdf.AsdfFile(tree)
        af.write_to(full_save_file)
        logger.info(f"Saved linearized tags to {full_save_file}")


class LoadLinearizedFiles(WorkflowTaskBase):
    """Load linearized tags that point to previously saved files."""

    @property
    def relative_save_file(self) -> str:
        return "linearized.asdf"

    def run(self):
        full_save_file = self.scratch.workflow_base_path / self.relative_save_file
        with asdf.open(full_save_file) as af:
            for f, t in af.tree["file_tag_dict"].items():
                # This is so any of the old (un-moved) files still tagged in the db are removed from the db
                current_files = self.read(tags=t)
                for current_file in current_files:
                    self.remove_tags(current_file, t)

                try:
                    self.tag(path=f, tags=t)
                except FileNotFoundError:
                    pass
        logger.info(f"Loaded linearized files entries from {full_save_file}")


def save_parsing_task(
    tag_list: list[str], save_file: str, save_file_tags: bool = True, save_constants: bool = True
):
    class SaveParsing(WorkflowTaskBase):
        """Save the result of parsing (constants and tags) to an asdf file."""

        @property
        def relative_save_file(self) -> str:
            return save_file

        def run(self):
            if save_file_tags:
                file_tag_dict = self.get_input_tags()
            else:
                logger.info("Skipping saving of file tags")
                file_tag_dict = dict()
            if save_constants:
                constant_dict = self.get_constants()
            else:
                logger.info("Skipping saving of constants")
                constant_dict = dict()

            full_save_file = self.scratch.workflow_base_path / self.relative_save_file
            tree = {"file_tag_dict": file_tag_dict, "constants_dict": constant_dict}
            af = asdf.AsdfFile(tree)
            af.write_to(full_save_file)
            logger.info(f"Saved input tags to {full_save_file}")

        def get_input_tags(self) -> dict[str, list[str]]:
            file_tag_dict = dict()
            path_list = self.read(tags=tag_list)
            for p in path_list:
                tags = self.tags(p)
                file_tag_dict[str(p)] = tags

            return file_tag_dict

        def get_constants(self) -> dict[str, str | float | list]:
            constants_dict = dict()
            for c in self.constants._db_dict.keys():
                constants_dict[c] = self.constants._db_dict[c]

            return constants_dict

    return SaveParsing


def load_parsing_task(save_file: str):
    class LoadParsing(WorkflowTaskBase):
        """Load tags and constants into the database."""

        @property
        def relative_save_file(self) -> str:
            return save_file

        def run(self):
            full_save_file = self.scratch.workflow_base_path / self.relative_save_file
            with asdf.open(full_save_file) as af:
                file_tag_dict = af.tree["file_tag_dict"]
                self.tag_input_files(file_tag_dict)

                constants_dict = af.tree["constants_dict"]
                self.populate_constants(constants_dict)

            logger.info(f"Loaded tags and constants from {full_save_file}")

        def tag_input_files(self, file_tag_dict: dict[str, list[str]]):
            for f, t in file_tag_dict.items():
                if not os.path.exists(f):
                    pass
                    # raise FileNotFoundError(f"Expected to find {f}, but it doesn't exist.")
                else:
                    self.tag(path=f, tags=t)

        def populate_constants(self, constants_dict: dict[str, str | int | float]) -> None:
            # First we purge all constants because a previous load might have polluted the DB
            self.constants._purge()
            for c, v in constants_dict.items():
                logger.info(f"Setting value of {c} to {v}")
                self.constants._update({c: v})

    return LoadParsing


class SaveTaskTags(WorkflowTaskBase):
    """Base task for saving all INTERMEDIATE files with the same 'TASK'"""

    @property
    def task_str(self) -> str:
        return "TASK"

    @property
    def relative_save_file(self) -> str:
        return "default_sav.asdf"

    @property
    def tag_lists_to_save(self) -> list[list[str]] | list[str]:
        return [[DlnirspTag.task(self.task_str), DlnirspTag.intermediate()]]

    def run(self):
        file_tag_dict = dict()
        tag_list_list = self.tag_lists_to_save
        if isinstance(tag_list_list[0], str):
            tag_list_list = [tag_list_list]

        for tags_to_save in tag_list_list:
            path_list = self.read(tags=tags_to_save)
            save_dir = self.scratch.workflow_base_path / Path(self.relative_save_file).stem
            save_dir.mkdir(exist_ok=True)
            for p in path_list:
                copied_path = shutil.copy(str(p), save_dir)
                tags = self.tags(p)
                file_tag_dict[copied_path] = tags

        full_save_file = self.scratch.workflow_base_path / self.relative_save_file
        tree = {"file_tag_dict": file_tag_dict}
        af = asdf.AsdfFile(tree)
        af.write_to(full_save_file)
        logger.info(f"Saved {self.task_str} to {full_save_file}")


class LoadTaskTags(WorkflowTaskBase):
    """Base task for loading file/tag associations from a previously saved set."""

    @property
    def relative_save_file(self) -> str:
        return "default_sav.asdf"

    def run(self):
        full_save_file = self.scratch.workflow_base_path / self.relative_save_file
        with asdf.open(full_save_file) as af:
            for f, t in af.tree["file_tag_dict"].items():
                self.tag(path=f, tags=t)
        logger.info(f"Loaded database entries from {full_save_file}")


class SaveDarkCal(SaveTaskTags):
    @property
    def task_str(self) -> str:
        return TaskName.dark.value

    @property
    def tag_lists_to_save(self) -> list[list[str]]:
        return super().tag_lists_to_save + [
            [DlnirspTag.quality("TASK_TYPES"), DlnirspTag.workflow_task("DarkCalibration")]
        ]

    @property
    def relative_save_file(self) -> str:
        return "dark_cal.asdf"


class LoadDarkCal(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "dark_cal.asdf"


class SaveIfuDriftCal(SaveTaskTags):
    @property
    def task_str(self) -> str:
        return DlnirspTaskName.drifted_ifu_group_id.value

    @property
    def tag_lists_to_save(self) -> list[list[str]]:
        return super().tag_lists_to_save + [
            [DlnirspTag.task_drifted_dispersion()],
            [DlnirspTag.task_drifted_ifu_x_pos()],
            [DlnirspTag.task_drifted_ifu_y_pos()],
        ]

    @property
    def relative_save_file(self) -> str:
        return "drift_cal.asdf"


class LoadIfuDriftCal(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "drift_cal.asdf"


class SaveLampCal(SaveTaskTags):
    @property
    def task_str(self) -> str:
        return TaskName.lamp_gain.value

    @property
    def tag_lists_to_save(self) -> list[list[str]]:
        return super().tag_lists_to_save + [
            [DlnirspTag.quality("TASK_TYPES"), DlnirspTag.workflow_task("LampCalibration")]
        ]

    @property
    def relative_save_file(self) -> str:
        return "lamp_cal.asdf"


class LoadLampCal(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "lamp_cal.asdf"


class SaveBadPixelCal(SaveTaskTags):
    @property
    def task_str(self) -> str:
        return DlnirspTaskName.bad_pixel_map.value

    @property
    def relative_save_file(self) -> str:
        return "bad_pixel_cal.asdf"


class LoadBadPixelCal(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "bad_pixel_cal.asdf"


class SaveGeometricCal(SaveTaskTags):
    @property
    def task_str(self) -> str:
        return TaskName.geometric.value

    @property
    def tag_lists_to_save(self) -> list[list[str]]:
        return super().tag_lists_to_save + [
            [DlnirspTag.intermediate(), DlnirspTag.task_dispersion()],
            [DlnirspTag.intermediate_frame(), DlnirspTag.task_avg_unrectified_solar_gain()],
            [DlnirspTag.quality("TASK_TYPES"), DlnirspTag.workflow_task("GeometricCalibration")],
        ]

    @property
    def relative_save_file(self) -> str:
        return "geometric_cal.asdf"


class LoadGeometricCal(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "geometric_cal.asdf"


class SaveWavelengthCal(SaveTaskTags):
    @property
    def task_str(self) -> str:
        return DlnirspTaskName.wavelength_solution.value

    @property
    def tag_lists_to_save(self) -> list[list[str]]:
        return super().tag_lists_to_save + [
            [
                DlnirspTag.quality(MetricCode.wavecal_fit),
                DlnirspTag.workflow_task("WavelengthCalibration"),
            ]
        ]

    @property
    def relative_save_file(self) -> str:
        return "wavelength_cal.asdf"


class LoadWavelengthCal(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "wavelength_cal.asdf"


class SaveSolarCal(SaveTaskTags):
    @property
    def task_str(self) -> str:
        return TaskName.solar_gain.value

    @property
    def tag_lists_to_save(self) -> list[list[str]]:
        return super().tag_lists_to_save + [
            [DlnirspTag.quality("TASK_TYPES"), DlnirspTag.workflow_task("SolarCalibration")]
        ]

    @property
    def relative_save_file(self) -> str:
        return "solar_cal.asdf"


class LoadSolarCal(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "solar_cal.asdf"


class SaveInstPolCal(SaveTaskTags):
    @property
    def task_str(self) -> str:
        return TaskName.demodulation_matrices.value

    @property
    def tag_lists_to_save(self) -> list[list[str]]:
        return super().tag_lists_to_save + [
            [
                DlnirspTag.quality("TASK_TYPES"),
                DlnirspTag.workflow_task("InstrumentPolarizationCalibration"),
            ],
            [DlnirspTag.quality("POLCAL_CONSTANT_PAR_VALS")],
            [DlnirspTag.quality("POLCAL_GLOBAL_PAR_VALS")],
            [DlnirspTag.quality("POLCAL_LOCAL_PAR_VALS")],
            [DlnirspTag.quality("POLCAL_FIT_RESIDUALS")],
            [DlnirspTag.quality("POLCAL_EFFICIENCY")],
        ]

    @property
    def relative_save_file(self) -> str:
        return "inst_pol_cal.asdf"


class LoadInstPolCal(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "inst_pol_cal.asdf"


class SaveCalibratedData(SaveTaskTags):
    @property
    def tag_lists_to_save(self) -> list[str]:
        return [DlnirspTag.frame(), DlnirspTag.calibrated()]

    @property
    def relative_save_file(self) -> str:
        return "calibrated_science.asdf"


class LoadCalibratedData(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "calibrated_science.asdf"


class SavePolCalAsScience(SaveTaskTags):
    @property
    def tag_lists_to_save(self) -> list[str]:
        return [DlnirspTag.task_observe(), DlnirspTag.linearized()]

    @property
    def relative_save_file(self) -> str:
        return "polcal_as_science.asdf"


class LoadPolCalAsScience(LoadTaskTags):
    constants: DlnirspConstants

    @property
    def constants_model_class(self):
        """Get DLNIRSP pipeline constants."""
        return DlnirspConstants

    @property
    def relative_save_file(self) -> str:
        return "polcal_as_science.asdf"

    def run(self):
        super().run()
        self.constants._update(
            {
                DlnirspBudName.num_mosaic_tiles_x.value: 1,
                DlnirspBudName.num_mosaic_tiles_y.value: 1,
                DlnirspBudName.num_mosaic_repeats.value: self.constants.num_cs_steps,
            }
        )


class SaveSolarGainAsScience(SaveTaskTags):
    @property
    def tag_lists_to_save(self) -> list[str]:
        return [DlnirspTag.task_observe(), DlnirspTag.linearized()]

    @property
    def relative_save_file(self) -> str:
        return "solar_gain_as_science.asdf"


def load_solar_gain_as_science_task(force_intensity_only: bool):
    class LoadSolarGainAsScience(LoadTaskTags):
        constants: DlnirspConstants

        @property
        def constants_model_class(self):
            """Get DLNIRSP pipeline constants."""
            return DlnirspConstants

        @property
        def relative_save_file(self) -> str:
            return "solar_gain_as_science.asdf"

        def run(self):
            super().run()
            del self.constants._db_dict[DlnirspBudName.polarimeter_mode.value]
            self.constants._update(
                {
                    DlnirspBudName.num_mosaic_tiles_x.value: 1,
                    DlnirspBudName.num_mosaic_tiles_y.value: 1,
                    DlnirspBudName.num_mosaic_repeats.value: 1,
                    DlnirspBudName.polarimeter_mode.value: "None" if force_intensity_only else "Full Stokes",  # fmt: skip
                }
            )
            logger.info(f"{self.constants.correct_for_polarization = }")

    return LoadSolarGainAsScience
