"""Create Dark calibration objects."""

from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_service_configuration.logging import logger

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks.dlnirsp_base import DlnirspTaskBase

__all__ = ["DarkCalibration"]


class DarkCalibration(DlnirspTaskBase, QualityMixin):
    """
    Task class for calculation of the averaged dark frame for a Dl calibration run.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs
    """

    record_provenance = True

    def run(self):
        """
        For each beam.

            - Gather input dark frames
            - Calculate master dark
            - Write master dark
            - Record quality metrics

        Returns
        -------
        None

        """
        target_exp_times = self.constants.non_dark_task_exposure_times
        logger.info(f"{target_exp_times = }")
        with self.apm_task_step(
            f"Calculating dark frames for {self.constants.num_beams} beams and {len(target_exp_times)} exp times"
        ):
            total_dark_frames_used = 0
            for exp_time in target_exp_times:
                logger.info(f"Gathering input dark frames for {exp_time = }")
                dark_tags = [
                    DlnirspTag.linearized_frame(),
                    DlnirspTag.task_dark(),
                    DlnirspTag.exposure_time(exp_time),
                ]
                current_exp_dark_count = self.scratch.count_all(tags=dark_tags)
                if current_exp_dark_count == 0:
                    raise ValueError(f"Could not find any darks for {exp_time = }")
                total_dark_frames_used += current_exp_dark_count
                input_dark_arrays = self.read(tags=dark_tags, decoder=fits_array_decoder)

                with self.apm_processing_step(f"Calculating dark for {exp_time = }"):
                    logger.info(f"Calculating dark for {exp_time = }")
                    averaged_dark_array = average_numpy_arrays(input_dark_arrays)

                with self.apm_writing_step(f"Writing dark for {exp_time = }"):
                    logger.info(f"Writing dark for {exp_time = }")
                    self.write(
                        data=averaged_dark_array,
                        tags=DlnirspTag.intermediate_frame_dark(exposure_time=exp_time),
                        encoder=fits_array_encoder,
                    )

        with self.apm_processing_step("Computing and logger quality metrics"):
            no_of_raw_dark_frames: int = self.scratch.count_all(
                tags=[
                    DlnirspTag.linearized_frame(),
                    DlnirspTag.task_dark(),
                ],
            )
            unused_count = int(no_of_raw_dark_frames - total_dark_frames_used)
            self.quality_store_task_type_counts(
                task_type=TaskName.dark.value,
                total_frames=no_of_raw_dark_frames,
                frames_not_used=unused_count,
            )
