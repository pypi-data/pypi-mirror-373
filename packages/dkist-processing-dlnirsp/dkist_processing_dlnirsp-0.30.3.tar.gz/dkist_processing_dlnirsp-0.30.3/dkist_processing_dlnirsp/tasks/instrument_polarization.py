"""Create demodulation matrices. See :doc:`this page </polarization_calibration>` for more information."""

from collections import defaultdict
from itertools import chain
from typing import Literal

import numpy as np
from astropy.io import fits
from astropy.modeling import fitting
from astropy.modeling import polynomial
from astropy.stats import sigma_clip
from dkist_processing_common.codecs.asdf import asdf_encoder
from dkist_processing_common.codecs.fits import fits_access_decoder
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_processing_math.arithmetic import divide_arrays_by_array
from dkist_processing_math.arithmetic import subtract_array_from_arrays
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_processing_pac.fitter.fitting_core import fill_modulation_matrix
from dkist_processing_pac.fitter.fitting_core import generate_model_I
from dkist_processing_pac.fitter.fitting_core import generate_S
from dkist_processing_pac.fitter.polcal_fitter import PolcalFitter
from dkist_processing_pac.input_data.drawer import Drawer
from dkist_processing_pac.input_data.dresser import Dresser
from dkist_service_configuration.logging import logger

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.parsers.dlnirsp_l0_fits_access import DlnirspL0FitsAccess
from dkist_processing_dlnirsp.tasks.dlnirsp_base import DlnirspTaskBase

__all__ = ["InstrumentPolarizationCalibration"]


class InstrumentPolarizationCalibration(DlnirspTaskBase, QualityMixin):
    """
    Task class for computing "instrument polarization calibration" objects.

    AKA demodulation matrices.
    """

    record_provenance = True

    def run(self) -> None:
        """
        Create demodulation matrices.

        1. Create polcal dark and gain calibration objects

        2. Apply dark, gain, and bad pixel map calibration objects to all POLCAL frames (including dark and clear steps)

        3. Sort all spectra by IFU group and beam

        4. Send IFU group data for each beam to `dkist-processing-pac` for demodulation calculation

        5. Fit demodulation matrix elements along the spatial dimension for each IFU group

        6. Write full demodulation matrices
        """
        if not self.constants.correct_for_polarization:
            return

        polcal_exposure_times = self.constants.polcal_exposure_times
        if len(polcal_exposure_times) > 1:
            logger.info(
                "WARNING: More than one polcal exposure time detected. "
                "Everything *should* still work, but this is a weird condition that may produce "
                "strange results."
            )
        logger.info(f"{polcal_exposure_times = }")

        with self.apm_processing_step("Generate polcal DARK frame"):
            logger.info("Generating polcal dark frame")
            self.generate_polcal_dark_calibration(exp_times=polcal_exposure_times)

        with self.apm_processing_step("Generate polcal GAIN frame"):
            logger.info("Generating polcal gain frame")
            self.generate_polcal_gain_calibration(exp_times=polcal_exposure_times)

        with self.apm_task_step("Process CS steps"):
            logger.info("Processing CS steps")
            local_data_dict, global_data_dict = self.process_cs_steps()

        beam_results_dict = dict()
        for beam in [1, 2]:
            with self.apm_processing_step(f"Fit CU parameters for beam {beam}"):
                logger.info(f"Fitting CU parameters for {beam = }")

                remove_I_trend = self.parameters.pac_remove_linear_I_trend
                local_dresser = Dresser()
                local_dresser.add_drawer(
                    Drawer(local_data_dict[beam], remove_I_trend=remove_I_trend)
                )
                global_dresser = Dresser()
                global_dresser.add_drawer(
                    Drawer(global_data_dict[beam], remove_I_trend=remove_I_trend)
                )
                pac_fitter = PolcalFitter(
                    local_dresser=local_dresser,
                    global_dresser=global_dresser,
                    fit_mode=self.parameters.pac_fit_mode,
                    init_set=self.constants.pac_init_set,
                    # TODO: Check that we want to leave this as True for DL
                    inherit_global_vary_in_local_fit=True,
                    suppress_local_starting_values=True,
                    fit_TM=False,
                )

            self.save_intermediate_polcal_files(polcal_fitter=pac_fitter, beam=beam)
            beam_results_dict[beam] = pac_fitter

        with self.apm_processing_step("Resample demodulation matrices"):
            raw_demod_dict = {
                beam: beam_results.demodulation_matrices
                for beam, beam_results in beam_results_dict.items()
            }
            logger.info("Organizing spatial pixels by group")
            beam_group_demod_dict = self.group_spatial_px_by_group(raw_demod_dict)

            self.write(
                data=beam_group_demod_dict,
                tags=[DlnirspTag.debug(), DlnirspTag.task("GROUPED_DEMODS")],
                encoder=asdf_encoder,
            )

            logger.info("Fitting demodulation matrices spatially along each group")
            beam_group_fit_demod_dict = self.fit_demodulation_matrices_by_group(
                beam_group_demod_dict
            )

            self.write(
                data=beam_group_fit_demod_dict,
                tags=[DlnirspTag.debug(), DlnirspTag.task("FIT_GROUPED_DEMODS")],
                encoder=asdf_encoder,
            )

            logger.info("Resampling demodulation matrices to full frame")
            full_array_shape = self.get_full_array_shape()
            final_demod = self.reshape_demodulation_matrices(
                beam_group_fit_demod_dict, full_array_shape
            )

        with self.apm_writing_step("Write full-frame demodulation matrices"):
            logger.info("Writing full-frame demodulation matrices")
            self.write(
                data=final_demod,
                encoder=fits_array_encoder,
                tags=[
                    DlnirspTag.intermediate_frame(),
                    DlnirspTag.task_demodulation_matrices(),
                ],
            )

        with self.apm_processing_step("Computing and recording polcal quality metrics"):
            self.record_polcal_quality_metrics(polcal_fitter_dict=beam_results_dict)

        with self.apm_processing_step("Computing and recording frame count quality metrics"):
            no_of_raw_lamp_frames: int = self.scratch.count_all(
                tags=[DlnirspTag.linearized_frame(), DlnirspTag.task_polcal()],
            )

            self.quality_store_task_type_counts(
                task_type=TaskName.polcal.value, total_frames=no_of_raw_lamp_frames
            )

    def generate_polcal_dark_calibration(self, exp_times: list[float] | tuple[float]) -> None:
        """Compute an average polcal dark array for all polcal exposure times."""
        for exp_time in exp_times:
            logger.info(f"Computing polcal dark for  {exp_time = }")

            dark_arrays = self.read(
                tags=[
                    DlnirspTag.linearized_frame(),
                    DlnirspTag.task_polcal_dark(),
                    DlnirspTag.exposure_time(exp_time),
                ],
                decoder=fits_array_decoder,
            )

            avg_array = average_numpy_arrays(dark_arrays)
            self.write(
                data=avg_array,
                tags=[
                    DlnirspTag.intermediate_frame(),
                    DlnirspTag.task_polcal_dark(),
                    DlnirspTag.exposure_time(exp_time),
                ],
                encoder=fits_array_encoder,
            )

    def generate_polcal_gain_calibration(self, exp_times: list[float] | tuple[float]) -> None:
        """
        Average 'clear' polcal frames to produce a polcal gain calibration.

        The polcal dark calibration is applied prior to averaging.
        """
        for exp_time in exp_times:
            logger.info(f"Computing polcal gain for {exp_time = }")

            dark_array = next(
                self.read(
                    tags=[
                        DlnirspTag.intermediate_frame(),
                        DlnirspTag.task_polcal_dark(),
                        DlnirspTag.exposure_time(exp_time),
                    ],
                    decoder=fits_array_decoder,
                )
            )

            gain_arrays = self.read(
                tags=[
                    DlnirspTag.linearized_frame(),
                    DlnirspTag.task_polcal_gain(),
                    DlnirspTag.exposure_time(exp_time),
                ],
                decoder=fits_array_decoder,
            )

            dark_corrected_arrays = subtract_array_from_arrays(
                arrays=gain_arrays, array_to_subtract=dark_array
            )

            avg_array = average_numpy_arrays(dark_corrected_arrays)
            self.write(
                data=avg_array,
                tags=[
                    DlnirspTag.intermediate_frame(),
                    DlnirspTag.task_polcal_gain(),
                    DlnirspTag.exposure_time(exposure_time_s=exp_time),
                ],
                encoder=fits_array_encoder,
            )

    def process_cs_steps(
        self,
    ) -> tuple[
        dict[int, dict[int, list[DlnirspL0FitsAccess]]],
        dict[int, dict[int, list[DlnirspL0FitsAccess]]],
    ]:
        """
        Start with raw, linearized POLCAL frames and produce data to be sent to `dkist-processing-pac`.

        Namely, the linearized frames first have dark and gain/clear corrections applied. They are then binned into
        a "global" and "local" set of data for each beam (see `dkist-processing-pac` for more information on the
        difference between these two data).
        """
        global_dict = {1: defaultdict(list), 2: defaultdict(list)}
        local_dict = {1: defaultdict(list), 2: defaultdict(list)}

        with self.apm_task_step("Collect dark, gain, and bad pixel arrays"):
            dark_array_dict = self.collect_polcal_calibrations_by_exp_time(
                TaskName.polcal_dark.value
            )
            gain_array_dict = self.collect_polcal_calibrations_by_exp_time(
                TaskName.polcal_gain.value
            )
            bad_pixel_map = next(
                self.read(
                    tags=[
                        DlnirspTag.intermediate_frame(),
                        DlnirspTag.task_bad_pixel_map(),
                    ],
                    decoder=fits_array_decoder,
                )
            )

        with self.apm_processing_step("Correct and extract polcal data"):
            for cs_step in range(self.constants.num_cs_steps):
                for modstate in range(1, self.constants.num_modstates + 1):
                    log_str = f"{cs_step = }, {modstate = }"
                    logger.info(f"Applying basic corrections to {log_str}")
                    data, header = self.apply_basic_corrections(
                        cs_step=cs_step,
                        modstate=modstate,
                        dark_array_dict=dark_array_dict,
                        gain_array_dict=gain_array_dict,
                        bad_pixel_map=bad_pixel_map,
                    )

                    logger.info(f"Extracting bins from {log_str}")
                    for beam in [1, 2]:
                        global_binned_data = self.bin_global_data(data, beam)
                        global_hdu = fits.PrimaryHDU(data=global_binned_data, header=header)
                        global_obj = DlnirspL0FitsAccess(hdu=global_hdu)
                        global_dict[beam][cs_step].append(global_obj)

                        local_binned_data = self.bin_local_data(data, beam)
                        local_hdu = fits.PrimaryHDU(data=local_binned_data, header=header)
                        local_obj = DlnirspL0FitsAccess(hdu=local_hdu)
                        local_dict[beam][cs_step].append(local_obj)

        return local_dict, global_dict

    def apply_basic_corrections(
        self,
        cs_step: int,
        modstate: int,
        dark_array_dict: dict[float, np.ndarray],
        gain_array_dict: dict[float, np.ndarray],
        bad_pixel_map: np.ndarray,
    ) -> tuple[np.ndarray, fits.Header]:
        """Apply polcal dark and gain/clear corrections to all POLCAL data."""
        # Grab ANY header. We only care about the modstate and GOS configuration (CS Step)
        tags = [
            DlnirspTag.linearized_frame(),
            DlnirspTag.task_polcal(),
            DlnirspTag.modstate(modstate),
            DlnirspTag.cs_step(cs_step),
        ]
        any_access_obj = next(
            self.read(
                tags=tags,
                decoder=fits_access_decoder,
                fits_access_class=DlnirspL0FitsAccess,
            )
        )
        header = any_access_obj.header

        exp_time_corrected_list = []
        for exp_time in self.constants.polcal_exposure_times:
            cs_step_arrays = self.read(
                tags=tags + [DlnirspTag.exposure_time(exp_time)], decoder=fits_array_decoder
            )
            dark_corrected_arrays = subtract_array_from_arrays(
                arrays=cs_step_arrays, array_to_subtract=dark_array_dict[exp_time]
            )

            gain_corrected_arrays = divide_arrays_by_array(
                arrays=dark_corrected_arrays, array_to_divide_by=gain_array_dict[exp_time]
            )
            exp_time_corrected_list.append(gain_corrected_arrays)

        all_corrected_arrays = chain(*exp_time_corrected_list)
        avg_array = average_numpy_arrays(all_corrected_arrays)

        avg_array[bad_pixel_map == 1] = np.nan

        return avg_array, header

    def collect_polcal_calibrations_by_exp_time(self, task: str) -> dict[float, np.ndarray]:
        """Pre-load a dictionary of calibration frames organized by exposure time."""
        cal_dict = dict()
        for exp_time in self.constants.polcal_exposure_times:
            cal_tags = [
                DlnirspTag.intermediate_frame(),
                DlnirspTag.task(task),
                DlnirspTag.exposure_time(exp_time),
            ]
            cal_array = next(self.read(tags=cal_tags, decoder=fits_array_decoder))
            cal_dict[exp_time] = cal_array

        return cal_dict

    def bin_global_data(self, data: np.ndarray, beam: Literal[1, 2]) -> np.ndarray:
        """Convert full array into "global" polcal data by averaging the entire beam."""
        idx = self.group_id_drifted_id_array % 2 == beam - 1
        global_data = np.nanmedian(data[idx])[None]
        return global_data

    def bin_local_data(self, data: np.ndarray, beam: Literal[1, 2]) -> np.ndarray:
        """Convert full array into "local" polcal data by binning each group in the beam."""
        binned_group_arrays = []
        for group in range(beam - 1, self.group_id_num_groups, 2):
            group_array = self.bin_single_group(data, group)
            binned_group_arrays.append(group_array)

        return np.hstack(binned_group_arrays)

    def bin_single_group(self, data: np.ndarray, group_id: int) -> np.ndarray:
        """Bin a single IFU group."""
        group_data = self.group_id_get_data(data=data, group_id=group_id)
        return np.nanmedian(group_data, axis=1)

    def group_spatial_px_by_group(
        self, binned_demod_dict: dict[int, np.ndarray]
    ) -> dict[int, dict[int, np.ndarray]]:
        """
        Organize arrays of all spatial pixels for each beam by their group IDs.

        In other words, if beam 1 has 13 spatial pixels across 4 groups, the output of this method will place each
        spatial pixel into its corresponding group. We use dictionaries because the groups may not all have the same
        number of spatial pixels.

        The output format is::

          {beam:
            {group_id: np.ndarray[spatial_px, stokes, modstate],
             ...
            },
          ...
          }

        """
        beam_raw_px_start_idx = {1: 0, 2: 0}
        grouped_data = {1: dict(), 2: dict()}

        for group in range(self.group_id_num_groups):
            # Beam `1` is the even-group beam, beam `2` is the odd-group beam
            beam = (group % 2) + 1

            group_idx = self.group_id_get_idx(group_id=group)
            group_spatial_size = np.unique(group_idx[0]).size
            raw_slice_start = beam_raw_px_start_idx[beam]
            raw_slice_stop = raw_slice_start + group_spatial_size

            group_data = binned_demod_dict[beam][raw_slice_start:raw_slice_stop]
            grouped_data[beam][group] = group_data

            beam_raw_px_start_idx[beam] = raw_slice_stop

        # Check to make sure all spatial pixels were sorted into a group
        for beam in [1, 2]:
            if beam_raw_px_start_idx[beam] != binned_demod_dict[beam].shape[0]:
                raise ValueError(
                    f"Did not use all spatial pixels from beam {beam}. "
                    f"Ended at {beam_raw_px_start_idx[beam]}, but there are {binned_demod_dict[beam].size}"
                    f" spatial pixels."
                )

        return grouped_data

    def fit_demodulation_matrices_by_group(
        self, beam_group_demod_dict: dict[int, dict[int, np.ndarray]]
    ) -> dict[int, dict[int, np.ndarray]]:
        """
        Fit demodulation matrices along the spatial axis of each IFU group.

        The result has the same format as the input demodulation matrices. See `group_spatial_px_by_group` for more
        information.
        """
        fit_beam_group_dict = {b: dict() for b in beam_group_demod_dict.keys()}

        poly_fit_order = self.parameters.polcal_demodulation_spatial_poly_fit_order
        if poly_fit_order == -1:
            logger.info("Poly fit order set to -1. Skipping spatial fit.")
            return beam_group_demod_dict

        num_mod = self.constants.num_modstates
        sig_clip_amount = self.parameters.polcal_demodulation_fit_sig_clip
        max_niter = self.parameters.polcal_demodulation_fit_max_niter

        for beam in beam_group_demod_dict.keys():
            for group, group_demod in beam_group_demod_dict[beam].items():

                fit_group_demod = np.zeros_like(group_demod)
                for s in range(4):  # Always 4 stokes parameters
                    for m in range(num_mod):
                        demod_entry = group_demod[:, s, m]
                        fit_group_demod[:, s, m] = self.fit_single_demodulation_matrix_entry(
                            raw_demod_entry=demod_entry,
                            sig_clip_amount=sig_clip_amount,
                            poly_fit_order=poly_fit_order,
                            max_niter=max_niter,
                        )

                fit_beam_group_dict[beam][group] = fit_group_demod

        return fit_beam_group_dict

    @staticmethod
    def fit_single_demodulation_matrix_entry(
        raw_demod_entry: np.ndarray, poly_fit_order: int, sig_clip_amount: float, max_niter: int
    ) -> np.ndarray:
        """
        Fit the spatial variation of the demodulation matrix for a single IFU group.

        Fits are performed with an iterative sigma clipping algorithm and have the form of a polynomial
        whose order is a pipeline parameter.
        """
        spatial_px = np.arange(raw_demod_entry.size)

        good_idx = np.isfinite(raw_demod_entry)

        poly_fitter = fitting.LinearLSQFitter()
        outlier_rejection_fitter = fitting.FittingWithOutlierRemoval(
            fitter=poly_fitter,
            outlier_func=sigma_clip,
            sigma=sig_clip_amount,
            niter=max_niter,
            cenfunc="median",
            stdfunc="std",
        )
        poly_model = polynomial.Polynomial1D(degree=poly_fit_order)

        fit_poly, _ = outlier_rejection_fitter(
            model=poly_model, x=spatial_px[good_idx], y=raw_demod_entry[good_idx]
        )

        return fit_poly(spatial_px)

    def get_full_array_shape(self) -> tuple[int, ...]:
        """Return the shape of the full DL-NIRSP frame."""
        return self.unrectified_array_shape

    def reshape_demodulation_matrices(
        self, binned_demod_dict: dict[int, dict[int, np.ndarray]], final_shape: tuple[int, ...]
    ) -> np.ndarray:
        """Populate a full frame from a set of demodulation matrices that are organized by binned IFU group."""
        beam1_num_groups = len(binned_demod_dict[1])
        beam2_num_groups = len(binned_demod_dict[2])

        beam1_num_spatial_px = sum([g.shape[0] for g in binned_demod_dict[1].values()])
        beam2_num_spatial_px = sum([g.shape[0] for g in binned_demod_dict[2].values()])

        if beam1_num_groups != beam2_num_groups:
            raise ValueError(
                f"Demodulation matrices have different a different number of groups for each beam "
                f"({beam1_num_groups}, {beam2_num_groups})"
            )

        if beam1_num_spatial_px != beam2_num_spatial_px:
            raise ValueError(
                f"Demodulation matrices have different total spatial px for each beam "
                f"({beam1_num_spatial_px}, {beam2_num_spatial_px})"
            )

        # The shape of a single demodulation matrix
        demod_shape = binned_demod_dict[1][0].shape[-2:]
        full_demod_matrices = np.zeros(final_shape + demod_shape)

        logger.info(
            f"Each beam has {beam1_num_spatial_px} spatial pixels over {beam1_num_groups} groups."
        )
        logger.info(f"Demodulation matrix shape: {demod_shape}")
        logger.info(f"Output demodulation matrices shape: {full_demod_matrices.shape}")

        for group in range(self.group_id_num_groups):
            beam = (group % 2) + 1
            group_demod = binned_demod_dict[beam][group]
            self.place_group_in_full_array(
                group_data=group_demod, group_id=group, full_array=full_demod_matrices
            )

        return full_demod_matrices

    def place_group_in_full_array(
        self, group_data: np.ndarray, group_id: int, full_array: np.ndarray
    ) -> None:
        """Upsample a single IFU group into the full DL-NIRSP array."""
        group_idx = self.group_id_get_idx(group_id=group_id, rectified=False)
        group_2d_slice = self.group_id_convert_idx_to_2d_slice(group_idx)
        full_array[group_2d_slice] = group_data[:, None]  # None is the dummy wavelength dimension

    def save_intermediate_polcal_files(self, polcal_fitter: PolcalFitter, beam: int) -> None:
        """
        Save intermediate files for science-team analysis.

        This method is only useful in local trail and PROD trial workflows.
        """
        dresser = polcal_fitter.local_objects.dresser
        ## Input flux
        #############
        input_flux_tags = [
            DlnirspTag.frame(),
            DlnirspTag.debug(),
            DlnirspTag.beam(beam),
            DlnirspTag.task("INPUT_FLUX"),
        ]

        # Put all flux into a single array
        fov_shape = dresser.shape
        socc_shape = (dresser.numdrawers, dresser.drawer_step_list[0], self.constants.num_modstates)
        flux_shape = fov_shape + socc_shape
        input_flux = np.zeros(flux_shape, dtype=np.float64)
        for i in range(np.prod(fov_shape)):
            idx = np.unravel_index(i, fov_shape)
            I_cal, _ = dresser[idx]
            input_flux[idx] = I_cal.T.reshape(socc_shape)

        with self.apm_writing_step("Writing input flux"):
            path = self.write(data=input_flux, tags=input_flux_tags, encoder=fits_array_encoder)
            logger.info(f"Wrote input flux with tags {input_flux_tags = } to {str(path)}")

        ## Calibration Unit best fit parameters
        #######################################
        cmp_tags = [
            DlnirspTag.frame(),
            DlnirspTag.debug(),
            DlnirspTag.beam(beam),
            DlnirspTag.task("CU_FIT_PARS"),
        ]
        with self.apm_writing_step("Writing CU fit parameters"):
            cu_dict = defaultdict(lambda: np.zeros(fov_shape) * np.nan)
            for i in range(np.prod(fov_shape)):
                idx = np.unravel_index(i, fov_shape)
                values_dict = polcal_fitter.fit_parameters[idx].valuesdict()
                for k, v in values_dict.items():
                    cu_dict[k][idx] = v

            path = self.write(data=cu_dict, tags=cmp_tags, encoder=asdf_encoder)
            logger.info(f"Wrote CU fits with {cmp_tags = } to {str(path)}")

        ## Best-fix flux
        ################
        fit_flux_tags = [
            DlnirspTag.frame(),
            DlnirspTag.debug(),
            DlnirspTag.beam(beam),
            DlnirspTag.task("BEST_FIT_FLUX"),
        ]
        with self.apm_processing_step("Computing best-fit flux"):
            best_fit_flux = self.compute_best_fit_flux(polcal_fitter)

        with self.apm_writing_step("Writing best-fit flux"):
            path = self.write(data=best_fit_flux, tags=fit_flux_tags, encoder=fits_array_encoder)
            logger.info(f"Wrote best-fit flux with {fit_flux_tags = } to {str(path)}")

    def compute_best_fit_flux(self, polcal_fitter: PolcalFitter) -> np.ndarray:
        """
        Calculate the best-fit SoCC flux from a set of fit parameters.

        The best-fit flux is needed to compute certain quality metrics.

        The output array has shape (1, num_spectral_bins, num_spatial_bins, 1, 4, num_modstate)
        """
        dresser = polcal_fitter.local_objects.dresser
        fov_shape = dresser.shape
        socc_shape = (dresser.numdrawers, dresser.drawer_step_list[0], self.constants.num_modstates)
        flux_shape = fov_shape + socc_shape
        best_fit_flux = np.zeros(flux_shape, dtype=np.float64)
        num_points = np.prod(fov_shape)
        for i in range(num_points):
            idx = np.unravel_index(i, fov_shape)
            I_cal, _ = dresser[idx]
            CM = polcal_fitter.local_objects.calibration_unit
            TM = polcal_fitter.local_objects.telescope
            par_vals = polcal_fitter.fit_parameters[idx].valuesdict()
            CM.load_pars_from_dict(par_vals)
            TM.load_pars_from_dict(par_vals)
            S = generate_S(TM=TM, CM=CM, use_M12=True)
            O = fill_modulation_matrix(par_vals, np.zeros((dresser.nummod, 4)))
            I_mod = generate_model_I(O, S)

            # Save all data to associated arrays
            best_fit_flux[idx] = I_mod.T.reshape(socc_shape)

        return best_fit_flux

    def record_polcal_quality_metrics(self, polcal_fitter_dict: dict[int, PolcalFitter]):
        """Record various quality metrics from PolCal fits."""
        for beam, fitter in polcal_fitter_dict.items():
            num_points = int(np.prod(fitter.local_objects.dresser.shape))
            self.quality_store_polcal_results(
                polcal_fitter=fitter,
                label=f"Beam {beam}",
                bin_nums=[num_points],
                bin_labels=["spatial"],
                num_points_to_sample=self.parameters.polcal_metrics_num_sample_points,
                ## The setting of `skip_recording_constant_pars` is a bit of a hack and thus needs some explanation
                # By using the ``skip_recording_constant_pars`` switch we DON'T record the "polcal constant parameters"
                # metric for beam 2. This is because both beam 1 and beam 2 will have the same table. The way `*-common`
                # is built it will look for all metrics for both beam 1 and beam 2 so if we did save that metric for
                # beam 2 then the table would show up twice in the quality report. The following line avoids that.
                skip_recording_constant_pars=beam != 1,
            )
