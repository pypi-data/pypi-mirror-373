"""Tasks for computing dataset-wide quality metrics."""

from dataclasses import dataclass
from dataclasses import field
from typing import Iterable
from typing import Literal

import numpy as np
from astropy.time import Time
from dkist_processing_common.codecs.fits import fits_access_decoder
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.parsers.quality import L1QualityFitsAccess
from dkist_processing_common.tasks import QualityL0Metrics
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_service_configuration.logging import logger

from dkist_processing_dlnirsp.models.constants import DlnirspConstants
from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.tasks.dlnirsp_base import DlnirspTaskBase

__all__ = ["DlnirspL0QualityMetrics", "DlnirspL1QualityMetrics"]


@dataclass
class QualityDataPoint:
    """Class for storage of a single DLNIRSP quality data point in a time series."""

    datetime: str | int  # AKA isot | mjd
    value: float


@dataclass
class QualityTimeSeries:
    """Class for storage of DLNIRSP time series quality data."""

    data_points: list[QualityDataPoint] = field(default_factory=list)

    @property
    def datetimes(self) -> list[str | int]:
        """Parse datetimes from list of data points."""
        return [dp.datetime for dp in self.data_points]

    @property
    def values(self) -> list[float]:
        """Parse values from list of data points."""
        return [dp.value for dp in self.data_points]

    def __len__(self):
        return len(self.data_points)


class DlnirspL0QualityMetrics(QualityL0Metrics):
    """
    Task class for collection of DLNIRSP L0 specific quality metrics.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs

    """

    @property
    def constants_model_class(self):
        """Class for DLNIRSP constants."""
        return DlnirspConstants

    @property
    def raw_frame_tag(self) -> str:
        """
        Define tag corresponding to L0 data.

        For DL it's LINEARIZED.
        """
        return DlnirspTag.linearized()

    @property
    def modstate_list(self) -> Iterable[int] | None:
        """
        Define the list of modstates over which to compute L0 quality metrics.

        If the dataset is non-polarimetric then we just compute all metrics over all modstates at once.
        """
        if self.constants.correct_for_polarization:
            return list(range(1, self.constants.num_modstates + 1))

        return None


class DlnirspL1QualityMetrics(DlnirspTaskBase, QualityMixin):
    """Task class for computing of L1 specific dataset metrics."""

    def run(self):
        """
        Calculate L1 metrics for the whole dataset.

        The dataset metrics include polarimetric sensitivity and noise per frame.
        """
        if self.constants.correct_for_polarization:
            stokes_params = self.constants.stokes_params
        else:
            stokes_params = self.constants.stokes_params[:1]

        for stokes in stokes_params:
            with self.apm_processing_step(f"Computing L1 quality metrics for Stokes {stokes}"):
                with self.apm_processing_step("Computing noise and sensitivity"):
                    sensitivity_data, noise_data = self.compile_sensitivity_and_noise_data(
                        stokes=stokes
                    )

                with self.apm_writing_step(f"Writing sensitivity"):
                    self.quality_store_sensitivity(
                        datetimes=sensitivity_data.datetimes,
                        values=sensitivity_data.values,
                        stokes=stokes,
                    )

                with self.apm_writing_step(f"Writing noise"):
                    self.quality_store_noise(
                        datetimes=noise_data.datetimes, values=noise_data.values, stokes=stokes
                    )

    def compile_sensitivity_and_noise_data(
        self, stokes: Literal["I", "Q", "U", "V"]
    ) -> tuple[QualityTimeSeries, QualityTimeSeries]:
        r"""
        Compute the sensitivity and noise for every OUTPUT frame in a dataset.

        We compute them both in one method so we don't have to read every file twice.

        Sensitivity, :math:`s`, is defined as:

        .. math::

            s = stddev(F_i)/\left<F_I\right>

        where :math:`F_i` is a full array of values for Stokes parameter :math:`i` (I, Q, U, V), and :math:`F_I` is the
        full frame of Stokes-I. The stddev is computed across the entire frame and :math:`\left< \right>` denote the
        frame average.

        The noise is defined as the average of the stddev of various sub-regions of the output array, taken around the
        edges of the frame.
        """
        sensitivity_data = QualityTimeSeries()
        noise_data = QualityTimeSeries()
        for mosaic in range(self.constants.num_mosaic_repeats):
            for X_tile in range(1, self.constants.num_mosaic_tiles_x + 1):
                for Y_tile in range(1, self.constants.num_mosaic_tiles_y + 1):
                    # Sensitivity
                    non_stokes_tags = [
                        DlnirspTag.calibrated(),
                        DlnirspTag.frame(),
                        DlnirspTag.mosaic_num(mosaic),
                        DlnirspTag.mosaic_tile_x(X_tile),
                        DlnirspTag.mosaic_tile_y(Y_tile),
                    ]
                    stokes_I_data = next(
                        self.read(
                            tags=non_stokes_tags + [DlnirspTag.stokes("I")],
                            decoder=fits_array_decoder,
                        )
                    )
                    stokes_I_avg = np.nanmedian(stokes_I_data) or np.nanmean(stokes_I_data)

                    stokes_frame = next(
                        self.read(
                            tags=non_stokes_tags + [DlnirspTag.stokes(stokes)],
                            decoder=fits_access_decoder,
                            fits_access_class=L1QualityFitsAccess,
                        )
                    )

                    sensitivity = (
                        np.nanstd(stokes_frame.data[np.isfinite(stokes_frame.data)]) / stokes_I_avg
                    )
                    time_str = Time(stokes_frame.time_obs).fits
                    sensitivity_data_point = QualityDataPoint(value=sensitivity, datetime=time_str)
                    sensitivity_data.data_points.append(sensitivity_data_point)

                    # Noise
                    non_inf_data = np.copy(stokes_frame.data)
                    non_inf_data[~np.isfinite(non_inf_data)] = np.nan
                    avg_noise = self.avg_noise(non_inf_data)
                    noise_data_point = QualityDataPoint(value=avg_noise, datetime=time_str)
                    noise_data.data_points.append(noise_data_point)

        logger.info(f"Calculated {len(sensitivity_data)} sensitivities and noise values")

        return sensitivity_data, noise_data
