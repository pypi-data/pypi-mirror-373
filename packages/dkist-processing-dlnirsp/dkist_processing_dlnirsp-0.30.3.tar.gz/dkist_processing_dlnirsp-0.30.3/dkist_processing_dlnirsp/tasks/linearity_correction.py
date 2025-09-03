"""Task to linearize raw input data. See :doc:`this page </linearization>` for more information."""

import re
from functools import cache
from functools import cached_property
from functools import partial

import numpy as np
from astropy.io import fits
from dkist_processing_common.codecs.fits import fits_access_decoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_service_configuration.logging import logger
from numba import njit

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.parsers.dlnirsp_l0_fits_access import DlnirspRampFitsAccess
from dkist_processing_dlnirsp.tasks.dlnirsp_base import DlnirspTaskBase

cached_info_logger = cache(logger.info)
__all__ = ["LinearityCorrection"]

ALLOWED_CAMERA_READOUT_MODES = ["UpTheRamp", "SubFrame"]
ALLOWED_MODULATOR_SPIN_MODES = ["Continuous", "Discrete"]


class LinearityCorrection(DlnirspTaskBase):
    """Task class for performing linearity correction on all input frames, regardless of task type."""

    record_provenance = True

    camera_sequence_regex: re.Pattern = re.compile(r"(\d*)line,(\d*)read")
    """
    regex pattern used to parse line-read-line values for a single coadd.

    This is where we decide that camera sequences are one or more coadd sequences, where each coadd sequence is
    "Xline,Yread". The total sequence may be padded with ",Zline" reset frames, which are not captured by this regex.
    """

    def run(self):
        """
        Linearize IR camera frames or tag VIS camera frames as LINEARIZED.

        Returns
        -------
        None
        """
        if self.constants.is_ir_data:
            with self.apm_task_step("Linearizing input IR frames"):
                self.linearize_IR_data()
                return

        with self.apm_task_step("Tagging non-IR frames as LINEARIZED"):
            self.tag_VIS_data_as_linearized()

    def tag_VIS_data_as_linearized(self):
        """Tag all INPUT frames as LINEARIZED and remove their INPUT tag."""
        for path in self.read(tags=[DlnirspTag.frame(), DlnirspTag.input()]):
            self.remove_tags(path, DlnirspTag.input())
            self.tag(path, tags=DlnirspTag.linearized())

    def linearize_IR_data(self):
        """
        Linearize data from IR cameras.

        Steps to be performed:
            - Gather all input ramps
            - Iterate through each ramp:
                - Split ramp by coadd
                - Linearize each coadd
                - Average coadds together to final linearized frame
                - Write linearity corrected frame
        """
        num_frames = len(self.constants.time_obs_list)
        for frame_num, time_obs in enumerate(self.constants.time_obs_list, start=1):
            logger.info(f"Processing frames from {time_obs} ({frame_num}/{num_frames})")
            input_tags = [DlnirspTag.input(), DlnirspTag.frame(), DlnirspTag.time_obs(time_obs)]
            input_objects_generator = self.read(
                tags=input_tags,
                decoder=fits_access_decoder,
                fits_access_class=DlnirspRampFitsAccess,
            )
            input_objects = list(input_objects_generator)

            if not self.is_ramp_valid(input_objects):
                continue

            sorted_input_objects = sorted(input_objects, key=lambda x: x.current_frame_in_ramp)
            linearized_hdu = self.linearize_single_ramp(sorted_input_objects)
            self.write_and_tag_linearized_frame(linearized_hdu, time_obs)

        logger.info(f"Processed {frame_num} frames")

    def linearize_single_ramp(self, ramp_obj_list: list[DlnirspRampFitsAccess]) -> fits.PrimaryHDU:
        """
        Convert a group of exposures from the same ramp into a single, linearized array.

        Steps to be performed:
             - Split "CAM_SAMPLE_SEQUENCE" for ramp into line-read indices
             - Identify coadds
             - Linearize each coadd
             - Average all coadds together

        The header of the linearized frame is taken from the last "read" frame.

        The specific linearization algorithm used depends on the camera readout and modulator spin modes used to aquire
        the ramp. See the `linearize_{READOUT_MODE}_{SPIN_MODE}_coadd` methods for the details of each algorithm.
        """
        coadd_sequence_nums_list = self.parse_camera_sample_sequence(
            ramp_obj_list[0].camera_sample_sequence
        )
        num_coadds = len(coadd_sequence_nums_list)

        line_read_line_indices = coadd_sequence_nums_list[0]
        num_bias, num_read = line_read_line_indices[:2]

        ndr_per_coadd = num_bias + num_read

        # In `is_ramp_valid` we already confirmed that all NDRs have the same values and that they are one of the
        # expected values
        camera_readout_mode = ramp_obj_list[0].camera_readout_mode
        modulator_spin_mode = ramp_obj_list[0].modulator_spin_mode
        match camera_readout_mode:
            case "UpTheRamp":
                match modulator_spin_mode:
                    case "Continuous":
                        linearization_func = partial(
                            self.linearize_uptheramp_continuous_coadd, num_bias=num_bias
                        )

                    case "Discrete":
                        read_abscissa = np.arange(num_read, dtype=float) + 1.0
                        linearization_func = partial(
                            self.linearize_uptheramp_discrete_coadd,
                            read_abscissa=read_abscissa,
                            num_bias=num_bias,
                        )

            case "SubFrame":
                linearization_func = self.linearize_subframe_coadd

        coadd_stack = np.zeros((num_coadds, *ramp_obj_list[0].data.shape))
        for coadd_num in range(num_coadds):
            coadd_start_idx = coadd_num * ndr_per_coadd
            coadd_end_idx = coadd_start_idx + ndr_per_coadd
            coadd_obj_list = ramp_obj_list[coadd_start_idx:coadd_end_idx]
            coadd_stack[coadd_num] = linearization_func(coadd_obj_list=coadd_obj_list)

        linearized_array = np.nanmean(coadd_stack, axis=0)

        last_read_idx = (num_bias + num_read) * num_coadds - 1
        last_read_header = ramp_obj_list[last_read_idx].header

        linearized_hdu = fits.PrimaryHDU(data=linearized_array, header=last_read_header)

        return linearized_hdu

    def linearize_subframe_coadd(
        self, *, coadd_obj_list: list[DlnirspRampFitsAccess]
    ) -> np.ndarray:
        r"""
        Linearize a single coadd taken in "SubFrame" camera readout mode. This method applies to all modulator spin modes.

        The final, linearized coadd, :math:`\mathrm{ADU}_{lin}` is

        .. math::
            \mathrm{ADU}_{lin} = f(\mathrm{ADU}_{raw,last\_read})

        where :math:`f(x)` is the `correction polynomial <apply_correction_polynomial>` and
        :math:`\mathrm{ADU}_{raw,last\_read}` is the last read frame in the coadd.
        """
        # Need to cast as float because raw are uint16 and will thus explode for values below 0
        last_read = coadd_obj_list[-1].data.astype(float)
        return self.apply_correction_polynomial(last_read)

    def linearize_uptheramp_continuous_coadd(
        self, *, coadd_obj_list: list[DlnirspRampFitsAccess], num_bias: int
    ) -> np.ndarray:
        r"""
        Linearize a single coadd taken with "UpTheRamp" camera readout mode and "Continuous" modulator spin mode.

        The final, linearized coadd, :math:`\mathrm{ADU}_{lin}` is

        .. math::
            \mathrm{ADU}_{lin} = f(\mathrm{ADU}_{raw,last\_read}) - f(\mathrm{ADU}_{raw,last\_bias})

        where :math:`f(x)` is the `correction polynomial <apply_correction_polynomial>` and
        :math:`\mathrm{ADU}_{raw,last\_read}` and :math:`\mathrm{ADU}_{raw,last\_bias}` are the last read and bias
        frames in the coadd, respectively.
        """
        # Need to cast as float because raw are uint16 and will thus explode for values below 0
        last_bias = coadd_obj_list[num_bias - 1].data.astype(float)
        last_read = coadd_obj_list[-1].data.astype(float)

        corrected_read = self.apply_correction_polynomial(last_read)
        corrected_bias = self.apply_correction_polynomial(last_bias)
        linearized_frame = corrected_read - corrected_bias

        return linearized_frame

    def linearize_uptheramp_discrete_coadd(
        self,
        *,
        coadd_obj_list: list[DlnirspRampFitsAccess],
        read_abscissa: np.ndarray,
        num_bias: int,
    ) -> np.ndarray:
        r"""
        Linearize a single coadd taken with "UpTheRamp" camera readout mode and "Discrete" modulator spin mode.

        To compute the final, linearized coadd, :math:`\mathrm{ADU}_{lin}`, we first correct all "read" frames in the
        ramp, :math:`\mathrm{ADU}_{raw,read,n}`, such that

        .. math::
            \mathrm{ADU}_{corr,n} = f(\mathrm{ADU}_{raw,read,n}) - f(\mathrm{ADU}_{raw,last\_bias})

        where :math:`n` refers to the :math:`n^{th}` read frame, :math:`f(x)` is the
        `correction polynomial <apply_correction_polynomial>`, and :math:`\mathrm{ADU}_{raw,last\_bias}` is the last
        bias frame in the coadd.
        Next, we compute the slope of the count value as a function of read frame for each pixel, :math:`p`. The slope
        is computed with a linear regression via

        .. math::
            a_p = \frac{\Sigma_{i=1}^N(n_i - \bar{n})(\mathrm{ADU_{corr,p,i}} - \overline{\mathrm{ADU_{corr,p}}})} {\Sigma_{i=1}^N(n_i - \bar{n})^2}

        where :math:`\bar{x}` represents the mean *over all read frames* and :math:`N` is the total number of read frames
        in the coadd. The final, linearized value of each pixel is then

        .. math::
            \mathrm{ADU}_{lin,p} = a_p N.

        Any NaN values in :math:`\mathrm{ADU}_{corr,n}` are ignored in subsequent computations. Any pixels that have
        fewer than 2 non-NaN read frames are forced to have :math:`\mathrm{ADU}_{lin,p} = \mathrm{ADU}_{corr,p,0}`, where
        :math:`\mathrm{ADU}_{corr,p,0}` may also be NaN.
        """
        last_bias = coadd_obj_list[num_bias - 1].data
        corrected_bias = self.apply_correction_polynomial(last_bias)

        # Stack along the last axis so the NDR axis is contiguous, which speeds up dot products in numba
        read_stack = np.stack([o.data for o in coadd_obj_list[num_bias:]], axis=-1)

        if read_stack.shape[0] == 1:
            cached_info_logger("Ramp only contains a single read frame. Returning that frame.")
            return read_stack[0]

        linearized_ramp = numba_linearize_discrete_ramp(
            read_abscissa=read_abscissa,
            ramp_stack=read_stack,
            bias=corrected_bias,
            poly_coeffs=self.parameters.linearization_poly_coeffs,
            saturation_threshold=self.parameters.linearization_saturation_threshold,
        )

        return linearized_ramp

    def apply_correction_polynomial(self, array: np.ndarray) -> np.ndarray:
        r"""
        Apply the correction polynomial to a single frame from a ramp.

        The correction is:

        .. math::
            \mathrm{ADU}_{corrected} = \frac{\mathrm{ADU}_{raw}}{a_0 + a_1\mathrm{ADU}_{raw} + a_2\mathrm{ADU}_{raw}^2 + ... + a_n\mathrm{ADU}_{raw}^n}

        where the polynomial coefficients :math:`a_0, a_1, ..., a_n` are pipeline parameters provided by the instrument team.

        Pixels deemed to be saturated *in the raw frame* are set to NaN. The saturation level is constant for all pixels
        and is provided by the instrument team.
        """
        correction = self.correction_polynomial(array)

        corrected_array = array / correction
        corrected_array[array > self.parameters.linearization_saturation_threshold] = np.nan
        return corrected_array

    @cached_property
    def correction_polynomial(self) -> np.poly1d:
        """Return the polynomial used to correct raw ramp frames."""
        return np.poly1d(self.parameters.linearization_poly_coeffs)

    def parse_camera_sample_sequence(self, camera_sample_sequence: str) -> list[list[int]]:
        """
        Identify and parse coadd sequences in the camera sample sequence.

        Reset "line" frames padding out the end of a sequence are ignored.

        Two examples of outputs given an input camera sample sequence

        "2line,3read"
            `[[2, 3]]`

        "3line,45read,3line,45read,2line"
            `[[3, 45], [3, 45]]`

        Returns
        -------
        A list of lists. Top-level list contains an item for each coadd. These items are themselves lists of
        length 2. The numbers in these inner lists correspond to the number of bias and read frames in that coadd,
        respectively.
        """
        coadd_matches = self.camera_sequence_regex.findall(camera_sample_sequence)
        coadd_sequence_numbers = [
            [int(num) for num in coadd_match] for coadd_match in coadd_matches
        ]

        return coadd_sequence_numbers

    def is_ramp_valid(self, ramp_object_list: list[DlnirspRampFitsAccess]) -> bool:
        r"""
        Check if a given ramp is valid.

        Current validity checks are:

          1. All frames in the ramp have the same value for NUM_FRAMES_IN_RAMP
          2. All frames in the ramp have the same value for CAMERA_READOUT_MODE
          3. All frames in the ramp have the same value for MODULATOR_SPIN_MODE
          4. The CAMERA_READOUT and MODULATOR_SPIN modes have expected values
          5. The value of NUM_FRAMES_IN_RAMP equals the length of actual frames found
          6. All frames in the ramp have the same value for CAMERA_SAMPLE_SEQUENCE
          7. The camera sample sequence has the expected form ('(,?\d*line,\d*read)*(,\d*line)?')
          8. All coadds in the ramp have the same camera sample sequence
          9. The ramp length is equal to the expected length from the camera sample sequence

        If a ramp is not valid then the reason is logged and `False` is returned.
        """
        frames_in_ramp_set = {o.num_frames_in_ramp for o in ramp_object_list}
        task_type = ramp_object_list[0].ip_task_type
        common_status_str = f"Ramp is task {task_type}. Skipping ramp."

        if len(frames_in_ramp_set) > 1:
            logger.info(
                f"Not all frames have the same FRAMES_IN_RAMP value. Set is {frames_in_ramp_set}. "
                f"{common_status_str}"
            )
            return False

        num_frames_in_ramp = frames_in_ramp_set.pop()
        num_ramp_objects = len(ramp_object_list)
        if num_ramp_objects != num_frames_in_ramp:
            logger.info(
                f"Missing some ramp frames. Expected {num_frames_in_ramp} from header value, but only "
                f"have {num_ramp_objects}. "
                f"{common_status_str}"
            )
            return False

        camera_readout_mode_set = {o.camera_readout_mode for o in ramp_object_list}
        if len(camera_readout_mode_set) > 1:
            logger.info(
                f"Not all frames have the same CAMERA_READOUT_MODE value. Set is {camera_readout_mode_set}. "
                f"{common_status_str}"
            )
            return False

        if (bad_camera_mode := camera_readout_mode_set.pop()) not in ALLOWED_CAMERA_READOUT_MODES:
            logger.info(
                f"Camera readout mode {bad_camera_mode} is unknown. Expected it to be in {ALLOWED_CAMERA_READOUT_MODES}. "
                f"{common_status_str}"
            )
            return False

        modulator_spin_mode_set = {o.modulator_spin_mode for o in ramp_object_list}
        if len(modulator_spin_mode_set) > 1:
            logger.info(
                f"Not all frames have the same MODULATOR_SPIN_MODE value. Set is {modulator_spin_mode_set}. "
                f"{common_status_str}"
            )
            return False

        if (bad_spin_mode := modulator_spin_mode_set.pop()) not in ALLOWED_MODULATOR_SPIN_MODES:
            logger.info(
                f"Modulator spin mode {bad_spin_mode} is unknown. Expected it to be in {ALLOWED_MODULATOR_SPIN_MODES}. "
                f"{common_status_str}"
            )
            return False

        camera_sample_sequence_set = {o.camera_sample_sequence for o in ramp_object_list}
        if len(camera_sample_sequence_set) > 1:
            logger.info(
                f"Not all frames have the same camera sample sequence. Set is {camera_sample_sequence_set}. "
                f"{common_status_str}"
            )
            return False

        camera_sample_sequence = camera_sample_sequence_set.pop()
        if re.search(r"\d*line,\d*line", camera_sample_sequence):
            logger.info(
                f"Malformed camera sample sequence: '{camera_sample_sequence}'. "
                f"{common_status_str}"
            )
            return False

        coadd_sequence_nums_list = self.parse_camera_sample_sequence(camera_sample_sequence)
        if not all([s == coadd_sequence_nums_list[0] for s in coadd_sequence_nums_list]):
            logger.info(
                f"Sample sequence is not the same for all coadds. "
                f"Sequence is {camera_sample_sequence} => {coadd_sequence_nums_list}. "
                f"{common_status_str}"
            )
            return False

        num_frames_in_sample_sequence = sum(
            [int(i) for i in re.findall(r"(\d+)", camera_sample_sequence)]
        )
        if num_frames_in_sample_sequence != num_ramp_objects:
            logger.info(
                f"Missing some ramp frames. Expected {num_frames_in_sample_sequence} from sample sequence "
                f"('{camera_sample_sequence}'), but found {num_ramp_objects}. "
                f"{common_status_str}"
            )
            return False

        return True

    def write_and_tag_linearized_frame(self, hdu: fits.PrimaryHDU, time_obs: str) -> None:
        """Write a linearized HDU and tag with LINEARIZED and FRAME."""
        hdu_list = fits.HDUList([hdu])

        tags = [DlnirspTag.linearized_frame(), DlnirspTag.time_obs(time_obs)]
        self.write(data=hdu_list, tags=tags, encoder=fits_hdulist_encoder)


@njit
def numba_linearize_discrete_ramp(
    read_abscissa: np.ndarray,
    ramp_stack: np.ndarray,
    bias: np.ndarray,
    poly_coeffs: np.ndarray,
    saturation_threshold: float,
) -> np.ndarray:
    """
    Linearize a single coadd taken with the discrete modulator spin mode.

    See `~LinearityCorrection.linearize_uptheramp_discrete_coadd` for more details on the specific algorithm.
    """
    nx, ny, num_read = ramp_stack.shape
    output = np.zeros_like(bias)
    for i in range(nx):
        for j in range(ny):
            bias_value = bias[i, j]
            if np.isnan(bias_value):
                output[i, j] = np.nan
                continue

            weights = np.ones(num_read, dtype=float)
            raw_data = ramp_stack[i, j, :]

            ###
            # Apply the correction polynomial and remove bias signal
            poly_data = np.zeros(num_read, dtype=float)
            for k in range(num_read):
                px_value = raw_data[k]
                if px_value > saturation_threshold:
                    weights[k] = 0.0
                    continue

                correction = numba_polynomial_value(px_value, poly_coeffs)
                corrected_px = px_value / correction
                poly_data[k] = corrected_px - bias_value

            ###
            # Check for conditions that let us bypass the regression calculation
            #
            # 1. If all reads are NaN then the final value is NaN
            weight_sum = np.sum(weights)
            if weight_sum == 0:
                output[i, j] = np.nan
                continue

            # 2. If there are fewer than 2 non-NaN reads then the final value is the value of the first read
            #    (which still may be NaN)
            if weight_sum < 2:
                if weights[0]:
                    output[i, j] = poly_data[0]
                else:
                    output[i, j] = np.nan
                continue

            ###
            # Compute the slope of px value w.r.t. read number
            x_mean = np.dot(read_abscissa, weights) / weight_sum
            y_mean = np.dot(poly_data, weights) / weight_sum
            X = read_abscissa - x_mean
            Y = poly_data - y_mean
            weighted_X = X * weights
            slope = np.dot(weighted_X, Y) / np.dot(weighted_X, X)

            # Final value is the total number of reads times the slope
            output[i, j] = num_read * slope

    return output


@njit
def numba_polynomial_value(x: float, poly_coeffs: np.ndarray) -> float:
    """
    Evaluate a polynomial at a given point, quickly with `numba` and Horner's method.

    Coefficients must be given in *descending* powers.
    """
    result = 0.0
    for c in poly_coeffs:
        result = x * result + c

    return result
