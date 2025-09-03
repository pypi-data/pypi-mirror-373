import json
from unittest.mock import ANY
from unittest.mock import patch

import numpy as np
import pytest
from astropy.io import fits
from dkist_header_validator.translator import translate_spec122_to_spec214_l0
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_pac.fitter.polcal_fitter import PolcalFitter
from dkist_processing_pac.input_data.dresser import Dresser

from dkist_processing_dlnirsp.models.tags import DlnirspTag
from dkist_processing_dlnirsp.parsers.dlnirsp_l0_fits_access import DlnirspL0FitsAccess
from dkist_processing_dlnirsp.tasks.instrument_polarization import InstrumentPolarizationCalibration
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingConstants
from dkist_processing_dlnirsp.tests.conftest import DlnirspTestingParameters
from dkist_processing_dlnirsp.tests.conftest import ModulatedCSStepHeaders
from dkist_processing_dlnirsp.tests.conftest import write_calibration_sequence_frames


@pytest.fixture
def dark_signal() -> float:
    return 5.0


@pytest.fixture
def clear_signal() -> float:
    return 10.0


@pytest.fixture
def polcal_task(
    tmp_path,
    recipe_run_id,
    small_calibration_sequence,
    link_constants_db,
    assign_input_dataset_doc_to_task,
    dark_signal,
    clear_signal,
    jband_group_id_array,
    jband_static_bad_pix_array,
    write_drifted_group_ids_to_task,
):
    polcal_exp_time = 7.0
    array_shape = jband_group_id_array.shape
    pol_status, pol_theta, ret_status, ret_theta, dark_status = small_calibration_sequence
    link_constants_db(
        recipe_run_id=recipe_run_id,
        constants_obj=DlnirspTestingConstants(
            POLCAL_EXPOSURE_TIMES=(polcal_exp_time,), NUM_CS_STEPS=len(pol_theta)
        ),
    )
    with InstrumentPolarizationCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        assign_input_dataset_doc_to_task(
            task=task,
            parameters=DlnirspTestingParameters(),
        )
        write_drifted_group_ids_to_task(task)
        task.write(
            data=jband_static_bad_pix_array.astype(np.int8),
            tags=[DlnirspTag.intermediate_frame(), DlnirspTag.task_bad_pixel_map()],
            encoder=fits_array_encoder,
        )
        num_polcal_frames = write_calibration_sequence_frames(
            task=task,
            pol_status=pol_status,
            pol_theta=pol_theta,
            ret_status=ret_status,
            ret_theta=ret_theta,
            dark_status=dark_status,
            dark_signal=dark_signal,
            clear_signal=clear_signal,
            array_shape=array_shape,
            tags=[DlnirspTag.linearized(), DlnirspTag.exposure_time(polcal_exp_time)],
        )

        yield task, polcal_exp_time, array_shape, num_polcal_frames
        task._purge()


@pytest.fixture
def polcal_task_no_data(
    tmp_path,
    recipe_run_id,
    link_constants_db,
    assign_input_dataset_doc_to_task,
    write_drifted_group_ids_to_task,
):
    num_cs_steps = 3
    num_modstates = 2
    link_constants_db(
        recipe_run_id=recipe_run_id,
        constants_obj=DlnirspTestingConstants(
            NUM_CS_STEPS=num_cs_steps, NUM_MODSTATES=num_modstates
        ),
    )
    with InstrumentPolarizationCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        assign_input_dataset_doc_to_task(
            task=task,
            parameters=DlnirspTestingParameters(),
        )
        write_drifted_group_ids_to_task(task)

        yield task, num_cs_steps, num_modstates
        task._purge()


@pytest.fixture
def write_calibrated_polcal_to_task(group_id_array, num_groups):
    array_shape = group_id_array.shape
    base_data = np.ones(array_shape) * 5e6

    for group in range(num_groups):
        idx = np.where(group_id_array == group)
        spatial_index, spectral_index = idx
        spatial_slice = slice(spatial_index.min(), spatial_index.max() + 1)
        spectral_slice = slice(spectral_index.min(), spectral_index.max() + 1)
        spatial_size = np.unique(spatial_index).size
        spectral_size = np.unique(spectral_index).size
        group_data = (
            np.ones((spatial_size, spectral_size)) * group * 10 + np.arange(spatial_size)[:, None]
        )
        base_data[spatial_slice, spectral_slice] = group_data

    beam1_base_avg = float(np.median(base_data[group_id_array % 2 == 0]))
    beam2_base_avg = float(np.median(base_data[group_id_array % 2 == 1]))

    def write_to_task(task, num_cs_steps, num_modstates):
        # First, write the bad pixel map. Make it all zeros so our math to check the correct values doesn't get messed
        # up from missing values.
        task.write(
            data=np.zeros(array_shape),
            tags=[DlnirspTag.intermediate_frame(), DlnirspTag.task_bad_pixel_map()],
            encoder=fits_array_encoder,
        )

        # Then write some dummy polcal dark and gain frames
        exp_time = task.constants.polcal_exposure_times[0]
        dark_array = np.zeros(array_shape)
        task.write(
            data=dark_array,
            encoder=fits_array_encoder,
            tags=[
                DlnirspTag.intermediate_frame(),
                DlnirspTag.task("POLCAL_DARK"),
                DlnirspTag.exposure_time(exp_time),
            ],
        )
        gain_array = np.ones(array_shape)
        task.write(
            data=gain_array,
            encoder=fits_array_encoder,
            tags=[
                DlnirspTag.intermediate_frame(),
                DlnirspTag.task("POLCAL_GAIN"),
                DlnirspTag.exposure_time(exp_time),
            ],
        )

        for cs_step in range(num_cs_steps):
            dataset = ModulatedCSStepHeaders(
                num_modstates=num_modstates,
                pol_status="foo",
                pol_theta=1000.0 * cs_step,
                ret_status="bar",
                ret_theta=100.0 * cs_step,
                dark_status="baz",
                cs_step_num=cs_step,
                array_shape=array_shape,
                exp_time_ms=7.0,
            )
            for modstate, frame in enumerate(dataset, start=1):
                header = fits.Header(translate_spec122_to_spec214_l0(frame.header()))
                data = base_data + 1000.0 * cs_step + 100.0 * modstate

                hdu_list = fits.HDUList(
                    [fits.PrimaryHDU(), fits.ImageHDU(data=data, header=header)]
                )
                task.write(
                    data=hdu_list,
                    encoder=fits_hdulist_encoder,
                    tags=[
                        DlnirspTag.linearized_frame(),
                        DlnirspTag.modstate(modstate),
                        DlnirspTag.cs_step(cs_step),
                        DlnirspTag.task_polcal(),
                        DlnirspTag.exposure_time(exp_time),
                    ],
                )

    return write_to_task, beam1_base_avg, beam2_base_avg


@pytest.fixture
def raw_binned_demod_data(num_spatial_px_per_beam, num_groups, num_spatial_px_per_group):
    beam1_data = np.hstack(
        [np.arange(num_spatial_px_per_group) + g for g in range(0, num_groups, 2)]
    )
    beam2_data = np.hstack(
        [np.arange(num_spatial_px_per_group) + g for g in range(1, num_groups, 2)]
    )

    raw_demod_data = {1: beam1_data, 2: beam2_data}

    return raw_demod_data


@pytest.fixture
def binned_and_grouped_demodulation_matrices(
    num_spatial_px_per_beam, num_groups, num_spatial_px_per_group
) -> dict[int, dict[int, np.ndarray]]:
    beam1_grouped_demod = {
        g: np.ones((num_spatial_px_per_group, 4, 8))
        * np.arange(num_spatial_px_per_group)[:, None, None]
        + g
        for g in range(0, num_groups, 2)
    }
    beam2_grouped_demod = {
        g: np.ones((num_spatial_px_per_group, 4, 8))
        * np.arange(num_spatial_px_per_group)[:, None, None]
        + g
        for g in range(1, num_groups, 2)
    }
    demod_dict = {1: beam1_grouped_demod, 2: beam2_grouped_demod}
    return demod_dict


@pytest.fixture
def noisy_demod_data(
    polcal_task_no_data,
) -> tuple[dict[int, dict[int, np.ndarray]], dict[int, dict[int, list]]]:
    # Just made these up
    poly_coeffs = {1: {0: [0.03, 0.4, 2]}, 2: {1: [0, -0.02, -3.4]}}
    sigma = 0.1
    num_spatial_px = 60
    x = np.arange(60)
    rng = np.random.default_rng()

    num_mod = polcal_task_no_data[0].constants.num_modstates

    data_dict = {1: dict(), 2: dict()}
    for beam in [1, 2]:
        for group, coeffs in poly_coeffs[beam].items():
            data = np.poly1d(coeffs)(x)
            noise = rng.normal(loc=0, scale=sigma, size=num_spatial_px)
            data_dict[beam][group] = (
                np.ones((num_spatial_px, 4, num_mod)) * (data + noise)[:, None, None]
            )

    return data_dict, poly_coeffs


@pytest.fixture
def num_spatial_px_per_beam(group_id_array, num_groups):
    num_spatial_px = 0
    for group in range(num_groups):
        num_spatial_px_in_group = np.unique(np.where(group_id_array == group)[0]).size
        num_spatial_px += num_spatial_px_in_group

    return num_spatial_px // 2  # Because two beams


@pytest.fixture
def num_spatial_px_per_group(num_spatial_px_per_beam, num_groups) -> int:
    return num_spatial_px_per_beam * 2 // num_groups


@pytest.fixture
def dummy_fit_objects(num_spatial_px_per_beam):
    class DummyFitterObjects:
        def __init__(self, *args, **kwargs):
            pass

        @property
        def dresser(self):
            # Needed so we can get the correct `num_points` when setting the size of the bins
            return np.arange(num_spatial_px_per_beam)

    return DummyFitterObjects


@pytest.fixture
def dummy_polcal_fitter(num_spatial_px_per_beam, dummy_fit_objects):
    class DummyPolcalFitter(PolcalFitter):
        def __init__(
            self,
            *,
            local_dresser: Dresser,
            global_dresser: Dresser,
            fit_mode: str,
            init_set: str,
            fit_TM: bool = False,
            threads: int = 1,
            super_name: str = "",
            _dont_fit: bool = False,
            **fit_kwargs,
        ):
            with patch(
                "dkist_processing_pac.fitter.polcal_fitter.FitObjects", new=dummy_fit_objects
            ):
                super().__init__(
                    local_dresser=local_dresser,
                    global_dresser=global_dresser,
                    fit_mode="use_M12",
                    init_set="OCCal_VIS",
                    _dont_fit=True,
                )

            self.num_modstates = local_dresser.nummod

        @property
        def demodulation_matrices(self) -> np.ndarray:
            return np.ones((num_spatial_px_per_beam, 4, self.num_modstates))

    return DummyPolcalFitter


def test_generate_calibration_frames(polcal_task, dark_signal, clear_signal):
    """
    Given: An InstrumentPolarizationCalibration task with tagged, linearized polcal frames
    When: Computing the POLCAL_DARK and POLCAL_GAIN calibrations
    Then: The correct calibration objects are produced
    """
    task, exp_time, _, _ = polcal_task

    task.generate_polcal_dark_calibration(exp_times=[exp_time])
    task.generate_polcal_gain_calibration(exp_times=[exp_time])

    dark_arrays = list(
        task.read(
            tags=[
                DlnirspTag.intermediate(),
                DlnirspTag.task_polcal_dark(),
                DlnirspTag.exposure_time(exp_time),
            ],
            decoder=fits_array_decoder,
        )
    )
    assert len(dark_arrays) == 1
    assert np.all(dark_arrays[0] == dark_signal)

    # Because the signal of a raw clear frame is `clear_signal + modstate`. See `make_cs_data` in conftest.
    # Then all modstate for all clears are averaged to make a single value, hence the `np.mean`
    expected_gain_value = np.mean(np.arange(1, task.constants.num_modstates + 1) + clear_signal)

    gain_arrays = list(
        task.read(
            tags=[
                DlnirspTag.intermediate(),
                DlnirspTag.task_polcal_gain(),
                DlnirspTag.exposure_time(exp_time),
            ],
            decoder=fits_array_decoder,
        )
    )

    assert len(gain_arrays) == 1
    np.testing.assert_array_equal(gain_arrays[0], expected_gain_value)


def test_apply_basic_corrections(
    polcal_task, dark_signal, clear_signal, jband_static_bad_pix_array
):
    """
    Given: A InstrumentPolarizationCalibration task with tagged, linearized POLCAL frames
    When: Applying dark and clear corrections
    Then: The correct dictionary structure is returned with correctly calibrated polcal frames
    """
    task, exp_time, array_shape, _ = polcal_task
    num_modstates = task.constants.num_modstates

    # Make intermediate polcal cal products
    dark_array = np.ones(array_shape) * dark_signal
    dark_dict = {exp_time: dark_array}

    gain_value = 6.28
    gain_array = np.ones(array_shape) * gain_value
    gain_dict = {exp_time: gain_array}

    for cs_step in range(task.constants.num_cs_steps):
        for m in range(1, num_modstates + 1):
            data, header = task.apply_basic_corrections(
                cs_step=cs_step,
                modstate=m,
                dark_array_dict=dark_dict,
                gain_array_dict=gain_dict,
                bad_pixel_map=jband_static_bad_pix_array,
            )
            fits_obj = DlnirspL0FitsAccess.from_header(header)
            if fits_obj.gos_level0_status == "DarkShutter":
                expected_value = 0.0
            elif (
                fits_obj.gos_polarizer_status == "clear" and fits_obj.gos_retarder_status == "clear"
            ):
                expected_value = (clear_signal + m) / gain_value
            else:
                # Because the signal of the "gain" that gets applied to the polcal data `clear_signal + modstate`.
                # See `make_cs_data` in conftest. It is DIFFERENT than our dummy "gain_value" that we contrived above.
                # This ensures that we don't get cancellations in the math that hide potential test failures.
                expected_value = (cs_step * 10000.0 + m * 100.0) * (clear_signal + m) / gain_value
            assert data.shape == array_shape
            assert np.round(np.nanmean(data), 6) == np.round(expected_value, 6)
            assert np.sum(np.isnan(data)) == np.sum(jband_static_bad_pix_array)


def test_process_cs_steps(
    polcal_task_no_data, write_calibrated_polcal_to_task, num_groups, num_spatial_px_per_beam
):
    """
    Given: An InstrumentPolarizationTask with associated raw polcal frames and polcal dark and gain frames
    When: Processing the polcal frames and extracting their bins
    Then: Bins of the correct shape and value are returned
    """
    # Note, this test is mostly of the bin-extracting portion `process_cs_steps`. See
    # test_apply_basic_corrections above for the corrections portion.
    data_writer, beam1_base_avg, beam2_base_avg = write_calibrated_polcal_to_task
    task, num_cs_steps, num_modstates = polcal_task_no_data
    num_spatial_px_per_group = num_spatial_px_per_beam * 2 // num_groups

    data_writer(task, num_cs_steps, num_modstates)

    local_dict, global_dict = task.process_cs_steps()

    assert len(local_dict) == len(global_dict) == 2
    assert len(local_dict[1]) == len(global_dict[1]) == num_cs_steps
    assert len(local_dict[2]) == len(global_dict[2]) == num_cs_steps
    assert local_dict.keys() == global_dict.keys()
    for beam, expected_global_value_base in zip([1, 2], [beam1_base_avg, beam2_base_avg]):
        for cs_step in range(num_cs_steps):
            assert (
                len(local_dict[beam][cs_step]) == len(global_dict[beam][cs_step]) == num_modstates
            )

            for modstate, (local_obj, global_obj) in enumerate(
                zip(local_dict[beam][cs_step], global_dict[beam][cs_step]), start=1
            ):
                global_data = global_obj.data
                assert global_obj.gos_polarizer_angle == 1000.0 * cs_step
                assert global_obj.gos_retarder_angle == 100.0 * cs_step
                assert global_data.shape == (1,)
                assert (
                    global_data[0]
                    == cs_step * 1000.0 + modstate * 100.0 + expected_global_value_base
                )

                local_data = local_obj.data
                assert local_obj.gos_polarizer_angle == 1000.0 * cs_step
                assert local_obj.gos_retarder_angle == 100.0 * cs_step
                assert local_data.shape == (num_spatial_px_per_beam,)
                for local_idx in range(local_data.shape[0]):
                    group = local_idx // num_spatial_px_per_group * 2 + (beam - 1) % 2
                    spatial_px_in_group = local_idx % num_spatial_px_per_group
                    assert (
                        local_data[local_idx]
                        == cs_step * 1000.0 + modstate * 100.0 + group * 10.0 + spatial_px_in_group
                    )


def test_reshape_demodulation_matrices(
    polcal_task_no_data,
    binned_and_grouped_demodulation_matrices,
    group_id_array,
    num_groups,
    num_spatial_px_per_group,
):
    """
    Given: An InstrumentPolarizationTask and raw demodulation matrices from `dkist-processing-pac`
    When: Reshaping the demodulation matrices to the full DL frame
    Then: The correct result is returned
    """
    task, _, _ = polcal_task_no_data
    array_shape = group_id_array.shape
    demod_dict = binned_and_grouped_demodulation_matrices

    full_demod = task.reshape_demodulation_matrices(demod_dict, array_shape)
    assert full_demod.shape == array_shape + (4, 8)
    for group in range(num_groups):
        data = task.group_id_get_data(data=full_demod, group_id=group)
        np.testing.assert_equal(
            np.mean(data, axis=(1, 2, 3)), np.arange(num_spatial_px_per_group) + group
        )


def test_group_spatial_px_by_group(
    polcal_task_no_data, raw_binned_demod_data, num_groups, num_spatial_px_per_group
):
    """
    Given: An InstrumentPolarizationCalibration task and the raw output of the pac fitter
    When: Organizing all the spatial pixels into their corresponding IFU groups
    Then: The raw data are organized correctly
    """
    task, _, _ = polcal_task_no_data

    raw_data = raw_binned_demod_data
    num_groups_per_beam = num_groups // 2
    grouped_demod = task.group_spatial_px_by_group(raw_data)
    for beam in [1, 2]:
        assert len(grouped_demod[beam]) == num_groups_per_beam
        for group, demod_data in grouped_demod[beam].items():
            np.testing.assert_equal(demod_data, np.arange(num_spatial_px_per_group) + group)


@pytest.mark.parametrize("fit_order", [pytest.param(2, id="fit"), pytest.param(-1, id="no_fit")])
def test_fit_demodulation_matrices_by_group(
    polcal_task_no_data, noisy_demod_data, fit_order, assign_input_dataset_doc_to_task
):
    """
    Given: An InstrumentPolarizationCalibration task and demod matrices binned by beam and group
    When: Fitting polynomials to each entry in the demod matrices
    Then: The matrix elements are well fit
    """
    noisy_demod_dict, poly_coeff_dict = noisy_demod_data
    task, _, _ = polcal_task_no_data
    assign_input_dataset_doc_to_task(
        task, DlnirspTestingParameters(dlnirsp_polcal_demodulation_spatial_poly_fit_order=fit_order)
    )

    fit_demod_dict = task.fit_demodulation_matrices_by_group(noisy_demod_dict)

    assert sorted(noisy_demod_dict.keys()) == sorted(fit_demod_dict.keys())
    for beam in noisy_demod_dict.keys():
        assert sorted(noisy_demod_dict[beam].keys()) == sorted(fit_demod_dict[beam].keys())
        for group in noisy_demod_dict[beam].keys():
            # grab [0,0] because we made the whole demod matrix the same in the `noisy_demod_data` fixture
            fit_data = fit_demod_dict[beam][group][:, 0, 0]
            if fit_order == -1:
                np.testing.assert_equal(fit_data, noisy_demod_dict[beam][group][:, 0, 0])
            else:
                fit_coeffs = np.polyfit(
                    np.arange(fit_data.size),
                    fit_data,
                    task.parameters.polcal_demodulation_spatial_poly_fit_order,
                )
                np.testing.assert_allclose(
                    fit_coeffs, poly_coeff_dict[beam][group], atol=0.05, rtol=0.05
                )


def test_instrument_polarization_task(
    polcal_task,
    dummy_polcal_fitter,
    polcal_quality_beam_labels,
    num_spatial_px_per_beam,
    polcal_quality_skip_constants,
    mocker,
    fake_gql_client,
):
    """
    Given: An InstrumentPolarizationTask with tagged, linearized POLCAL frames
    When: Running the task
    Then: The task completes and the expected outputs exist
    """
    # This test tests everything not covered specifically by the preceding tests. AKA, all the glue stuff.
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    mocker.patch(
        "dkist_processing_dlnirsp.tasks.instrument_polarization.PolcalFitter",
        new=dummy_polcal_fitter,
    )
    mocker.patch(
        "dkist_processing_dlnirsp.tasks.instrument_polarization.InstrumentPolarizationCalibration.save_intermediate_polcal_files"
    )

    quality_metric_mocker = mocker.patch(
        "dkist_processing_dlnirsp.tasks.instrument_polarization.InstrumentPolarizationCalibration.quality_store_polcal_results",
        autospec=True,
    )

    task, _, array_shape, num_polcal_frames = polcal_task

    task()

    demod_array = list(
        task.read(
            tags=[
                DlnirspTag.intermediate_frame(),
                DlnirspTag.task_demodulation_matrices(),
            ],
            decoder=fits_array_decoder,
        )
    )
    assert len(demod_array) == 1
    assert demod_array[0].shape == array_shape + (4, 8)

    quality_files = list(task.read(tags=[DlnirspTag.quality("TASK_TYPES")]))
    assert len(quality_files) == 1
    file = quality_files[0]
    with file.open() as f:
        data = json.load(f)
        assert isinstance(data, dict)
        assert data["task_type"] == TaskName.polcal.value
        assert data["total_frames"] == num_polcal_frames
        assert data["frames_not_used"] == 0

    for label, skip_constants in zip(polcal_quality_beam_labels, polcal_quality_skip_constants):
        quality_metric_mocker.assert_any_call(
            task,
            polcal_fitter=ANY,
            label=label,
            bin_nums=[num_spatial_px_per_beam],
            bin_labels=["spatial"],
            num_points_to_sample=task.parameters.polcal_metrics_num_sample_points,
            skip_recording_constant_pars=skip_constants,
        )
