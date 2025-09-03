"""Create Lamp Gain Calibration objects."""

import numpy as np
from astropy.convolution import Gaussian2DKernel
from astropy.convolution import interpolate_replace_nans
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_processing_math.arithmetic import subtract_array_from_arrays
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_service_configuration.logging import logger
from scipy.ndimage import median_filter

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks.dlnirsp_base import DlnirspTaskBase

__all__ = ["LampCalibration"]


class LampCalibration(DlnirspTaskBase, QualityMixin):
    """
    Task class for calculation of the averaged lamp gain frame for a DLNIRSP calibration run.

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
        Compute demodulated lamp images.

        1. Average all lamp frames together.

        2. Subtract a dark signal from average gain.

        3. De-spike data to remove spurious pixels.

        4. Save.

        Returns
        -------
        None

        """
        with self.apm_task_step(
            f"Generate lamp gains for {len(self.constants.lamp_gain_exposure_times)} exposure times"
        ):
            all_exp_time_gains = []
            for exp_time in self.constants.lamp_gain_exposure_times:
                logger.info(f"Load dark for {exp_time = }")
                try:
                    dark_array = next(
                        self.read(
                            tags=[DlnirspTag.intermediate_frame_dark(exposure_time=exp_time)],
                            decoder=fits_array_decoder,
                        )
                    )
                except RuntimeError:
                    raise ValueError(f"No matching dark found for {exp_time = } s")

                logger.info(f"Calculating average lamp gain for {exp_time = }")
                basic_gain = self.compute_lamp_gain(
                    dark_array=dark_array,
                    exp_time=exp_time,
                )

                # 8.7.23: We're currently not cleaning because a) Tetsu doesn't do it (cleaning algorithm came from
                #  older scripts from Sarah), and b) the cleaning removes large parts of the image (which might just
                #  be a parameter value thing).

                # cleaned_gain = self.despike_gain(basic_gain)

                all_exp_time_gains.append(basic_gain)

            logger.info(
                f"Averaging gains from {len(self.constants.lamp_gain_exposure_times)} exposure times together."
            )
            final_gain_array = average_numpy_arrays(all_exp_time_gains)

            with self.apm_writing_step(f"Writing lamp gain"):
                logger.info(f"Writing lamp gain")
                self.write(
                    data=final_gain_array,
                    tags=[DlnirspTag.intermediate_frame(), DlnirspTag.task_lamp_gain()],
                    encoder=fits_array_encoder,
                )

        with self.apm_processing_step("Computing and logging quality metrics"):
            no_of_raw_lamp_frames: int = self.scratch.count_all(
                tags=[DlnirspTag.linearized_frame(), DlnirspTag.task_lamp_gain()],
            )

            self.quality_store_task_type_counts(
                task_type=TaskName.lamp_gain.value, total_frames=no_of_raw_lamp_frames
            )

    def compute_lamp_gain(self, exp_time: float, dark_array: np.ndarray) -> np.ndarray:
        """Average lamp frames for a given exp time then subtract a dark frame."""
        lamp_gain_tags = [
            DlnirspTag.linearized_frame(),
            DlnirspTag.task_lamp_gain(),
            DlnirspTag.exposure_time(exp_time),
        ]
        lamp_gain_arrays = self.read(tags=lamp_gain_tags, decoder=fits_array_decoder)

        averaged_gain_array_generator = average_numpy_arrays(lamp_gain_arrays)
        dark_subtracted_gain_array = next(
            subtract_array_from_arrays(averaged_gain_array_generator, dark_array)
        )

        return dark_subtracted_gain_array

    def despike_gain(self, gain_array: np.ndarray) -> np.ndarray:
        """Apply basic despiking algorithm to remove hot pixels."""
        # Almost verbatim from Sarah's dlnirsp.py:despike()

        # Identify spikes
        median_array = median_filter(gain_array, size=self.parameters.lamp_despike_kernel)
        spikes = np.abs((gain_array - median_array) / np.nanmedian(gain_array))
        spike_idx = np.argwhere(spikes > self.parameters.lamp_despike_threshold)

        # Interpolate over spikes
        gain_array[spike_idx] = np.nan
        gauss_kernel = Gaussian2DKernel(*self.parameters.lamp_despike_kernel)

        gain_array = interpolate_replace_nans(gain_array, gauss_kernel)

        return gain_array
