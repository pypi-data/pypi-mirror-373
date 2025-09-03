from datetime import datetime
from unittest.mock import ANY
from unittest.mock import patch

import numpy as np
import pytest
from astropy.io import fits
from dkist_header_validator import spec122_validator
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_pac.fitter.polcal_fitter import PolcalFitter
from dkist_processing_pac.input_data.dresser import Dresser

from dkist_processing_cryonirsp.models.exposure_conditions import AllowableOpticalDensityFilterNames
from dkist_processing_cryonirsp.models.exposure_conditions import ExposureConditions
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.tasks.instrument_polarization import (
    CIInstrumentPolarizationCalibration,
)
from dkist_processing_cryonirsp.tasks.instrument_polarization import (
    SPInstrumentPolarizationCalibration,
)
from dkist_processing_cryonirsp.tests.conftest import CryonirspConstantsDb
from dkist_processing_cryonirsp.tests.conftest import cryonirsp_testing_parameters_factory
from dkist_processing_cryonirsp.tests.conftest import generate_fits_frame
from dkist_processing_cryonirsp.tests.header_models import CryonirspHeadersValidPolcalFrames


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
        with patch("dkist_processing_pac.fitter.polcal_fitter.FitObjects"):
            with patch("dkist_processing_pac.fitter.polcal_fitter.PolcalFitter.check_dressers"):
                super().__init__(
                    local_dresser=local_dresser,
                    global_dresser=global_dresser,
                    fit_mode="use_M12_I_sys_per_step",
                    init_set="OCCal_VIS",
                    _dont_fit=True,
                )

        self.num_modstates = local_dresser.nummod

    @property
    def demodulation_matrices(self) -> np.ndarray:
        return np.ones((1, 1, 4, self.num_modstates))


def _create_polcal_dark_or_gain_array(
    task, array_shape, num_mod, exposure_conditions, polcal_type, start_time
):
    ds = CryonirspHeadersValidPolcalFrames(
        # Using array_shape here for dataset_shape so only 1 frame is created:
        dataset_shape=array_shape,
        array_shape=array_shape,
        time_delta=10,
        num_modstates=1,
        modstate=1,
        start_time=start_time,
    )
    header_generator = (
        spec122_validator.validate_and_translate_to_214_l0(d.header(), return_type=fits.HDUList)[
            0
        ].header
        for d in ds
    )
    hdul = generate_fits_frame(header_generator=header_generator, shape=array_shape)
    cs_step = 1 if polcal_type == TaskName.polcal_gain.value else 0
    for m in range(1, num_mod + 1):
        task.write(
            data=hdul,
            tags=[
                CryonirspTag.task(polcal_type),
                CryonirspTag.task_polcal(),
                CryonirspTag.modstate(m),
                CryonirspTag.cs_step(cs_step),
                CryonirspTag.linearized_frame(exposure_conditions=exposure_conditions),
            ],
            encoder=fits_hdulist_encoder,
        )


def _create_polcal_arrays(
    task,
    dataset_shape,
    array_shape,
    exposure_conditions,
    start_time,
    num_modstates,
    num_cs_steps,
):
    for modstate in range(1, num_modstates + 1):
        # Create polcal input frames for this modstate
        ds = CryonirspHeadersValidPolcalFrames(
            dataset_shape=dataset_shape,
            array_shape=array_shape,
            time_delta=10,
            num_modstates=num_modstates,
            modstate=modstate,
            start_time=start_time,
        )
        header_generator = (
            spec122_validator.validate_and_translate_to_214_l0(
                d.header(), return_type=fits.HDUList
            )[0].header
            for d in ds
        )
        # cs_step does not map to a single keyword, so not needed in the fake headers
        # We start at 2 because dark and gain are 0 and 1
        for cs_step in range(2, num_cs_steps):
            hdul = generate_fits_frame(header_generator=header_generator, shape=array_shape)
            task.write(
                data=hdul,
                tags=[
                    CryonirspTag.task_polcal(),
                    CryonirspTag.modstate(modstate),
                    CryonirspTag.cs_step(cs_step),
                    CryonirspTag.linearized_frame(exposure_conditions=exposure_conditions),
                ],
                encoder=fits_hdulist_encoder,
            )


@pytest.fixture(scope="function")
def ci_instrument_polarization_calibration_task(
    tmp_path,
    recipe_run_id,
    assign_input_dataset_doc_to_task,
    init_cryonirsp_constants_db,
    mocker,
):
    num_beams = 1
    num_modstates = 2
    num_cs_steps = 2
    num_spatial_steps = 1
    exposure_time = 0.01  # From CryoHeadersValidPolcalFrames fixture (Check this value)
    exposure_conditions = ExposureConditions(
        exposure_time, AllowableOpticalDensityFilterNames.OPEN.value
    )
    # intermediate_shape = (10, 10)
    dataset_shape = (num_cs_steps, 20, 10)
    array_shape = (1, 20, 10)
    constants_db = CryonirspConstantsDb(
        NUM_MODSTATES=num_modstates,
        NUM_BEAMS=num_beams,
        NUM_CS_STEPS=num_cs_steps,
        POLCAL_EXPOSURE_CONDITIONS_LIST=(exposure_conditions,),
        ARM_ID="CI",
        NUM_SPATIAL_STEPS=num_spatial_steps,
    )
    init_cryonirsp_constants_db(recipe_run_id, constants_db)
    with CIInstrumentPolarizationCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="ci_instrument_polarization_calibration",
        workflow_version="VX.Y",
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            param_class = cryonirsp_testing_parameters_factory(task)
            assign_input_dataset_doc_to_task(task, param_class())
            mocker.patch(
                "dkist_processing_cryonirsp.tasks.instrument_polarization.PolcalFitter",
                new=DummyPolcalFitter,
            )

            # Don't test place-holder QA stuff for now
            quality_metric_mocker = mocker.patch(
                "dkist_processing_cryonirsp.tasks.instrument_polarization.CIInstrumentPolarizationCalibration.quality_store_polcal_results",
                autospec=True,
            )

            # Create beam border intermediate array that is consistent with a single pixel array
            task.write(
                data=np.array([0, 1, 0, 1]),
                tags=[CryonirspTag.intermediate_frame(beam=1), CryonirspTag.task_beam_boundaries()],
                encoder=fits_array_encoder,
            )

            # Create fake bad pixel map
            task.write(
                data=np.zeros((1, 1)),
                tags=[CryonirspTag.intermediate_frame(), CryonirspTag.task_bad_pixel_map()],
                encoder=fits_array_encoder,
            )

            start_time = datetime.now()
            # Create a single fake polcal raw dark array
            _create_polcal_dark_or_gain_array(
                task,
                array_shape,
                num_modstates,
                exposure_conditions,
                TaskName.polcal_dark.value,
                start_time,
            )

            # Create a single fake polcal gain array
            _create_polcal_dark_or_gain_array(
                task,
                array_shape,
                num_modstates,
                exposure_conditions,
                TaskName.polcal_gain.value,
                start_time,
            )

            # Create a set of full polcal frames
            _create_polcal_arrays(
                task,
                dataset_shape,
                array_shape,
                exposure_conditions,
                start_time,
                num_modstates,
                num_cs_steps,
            )

            yield task, quality_metric_mocker
        finally:
            task._purge()


@pytest.fixture(scope="function")
def ci_instrument_polarization_calibration_task_with_no_data(
    tmp_path, recipe_run_id, assign_input_dataset_doc_to_task, init_cryonirsp_constants_db
):
    init_cryonirsp_constants_db(recipe_run_id, CryonirspConstantsDb())
    with CIInstrumentPolarizationCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="ci_instrument_polarization_calibration",
        workflow_version="VX.Y",
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            param_class = cryonirsp_testing_parameters_factory(task)
            assign_input_dataset_doc_to_task(task, param_class())
            yield task
        finally:
            task._purge()


@pytest.fixture(scope="function")
def sp_instrument_polarization_calibration_task(
    tmp_path,
    recipe_run_id,
    assign_input_dataset_doc_to_task,
    init_cryonirsp_constants_db,
    mocker,
):
    num_beams = 2
    num_modstates = 2
    num_cs_steps = 2
    num_spatial_steps = 1
    exposure_time = 0.01  # From CryoHeadersValidPolcalFrames fixture (Check this value)
    exposure_conditions = ExposureConditions(
        exposure_time, AllowableOpticalDensityFilterNames.OPEN.value
    )
    # intermediate_shape = (10, 10)
    dataset_shape = (num_cs_steps, 20, 10)
    array_shape = (1, 20, 10)
    constants_db = CryonirspConstantsDb(
        NUM_MODSTATES=num_modstates,
        NUM_BEAMS=num_beams,
        NUM_CS_STEPS=num_cs_steps,
        POLCAL_EXPOSURE_CONDITIONS_LIST=(exposure_conditions,),
        ARM_ID="SP",
        NUM_SPATIAL_STEPS=num_spatial_steps,
    )
    init_cryonirsp_constants_db(recipe_run_id, constants_db)
    with SPInstrumentPolarizationCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="sp_instrument_polarization_calibration",
        workflow_version="VX.Y",
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            param_class = cryonirsp_testing_parameters_factory(task)
            assign_input_dataset_doc_to_task(task, param_class())
            mocker.patch(
                "dkist_processing_cryonirsp.tasks.instrument_polarization.PolcalFitter",
                new=DummyPolcalFitter,
            )

            # Don't test place-holder QA stuff for now
            quality_metric_mocker = mocker.patch(
                "dkist_processing_cryonirsp.tasks.instrument_polarization.SPInstrumentPolarizationCalibration.quality_store_polcal_results",
                autospec=True,
            )

            # Create beam border intermediate arrays that are consistent with a single pixel array
            for beam in range(1, num_beams + 1):
                task.write(
                    data=np.array([0, 1, 0, 1]),
                    tags=[
                        CryonirspTag.intermediate_frame(beam=beam),
                        CryonirspTag.task_beam_boundaries(),
                    ],
                    encoder=fits_array_encoder,
                )

            # Create fake bad pixel map
            task.write(
                data=np.zeros((1, 1)),
                tags=[CryonirspTag.intermediate_frame(), CryonirspTag.task_bad_pixel_map()],
                encoder=fits_array_encoder,
            )

            start_time = datetime.now()
            # Create a single fake polcal raw dark array
            _create_polcal_dark_or_gain_array(
                task,
                array_shape,
                num_modstates,
                exposure_conditions,
                TaskName.polcal_dark.value,
                start_time,
            )

            # Create a single fake polcal gain array
            _create_polcal_dark_or_gain_array(
                task,
                array_shape,
                num_modstates,
                exposure_conditions,
                TaskName.polcal_gain.value,
                start_time,
            )

            # Create a set of full polcal frames
            _create_polcal_arrays(
                task,
                dataset_shape,
                array_shape,
                exposure_conditions,
                start_time,
                num_modstates,
                num_cs_steps,
            )

            yield task, quality_metric_mocker
        finally:
            task._purge()


@pytest.fixture(scope="function")
def sp_instrument_polarization_calibration_task_with_no_data(
    tmp_path, recipe_run_id, assign_input_dataset_doc_to_task, init_cryonirsp_constants_db
):
    init_cryonirsp_constants_db(recipe_run_id, CryonirspConstantsDb())
    with SPInstrumentPolarizationCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="sp_instrument_polarization_calibration",
        workflow_version="VX.Y",
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            param_class = cryonirsp_testing_parameters_factory(task)
            assign_input_dataset_doc_to_task(task, param_class())
            yield task
        finally:
            task._purge()


@pytest.fixture()
def full_beam_shape() -> tuple[int, int]:
    return (100, 256)


@pytest.fixture()
def single_demodulation_matrix() -> np.ndarray:
    return np.arange(40).reshape(1, 1, 4, 10)


@pytest.fixture()
def multiple_demodulation_matrices() -> np.ndarray:
    return np.arange(2 * 3 * 4 * 10).reshape(2, 3, 4, 10)


def test_ci_instrument_polarization_calibration_task(
    ci_instrument_polarization_calibration_task,
    mocker,
    fake_gql_client,
):
    """
    Given: An InstrumentPolarizationCalibration task
    When: Calling the task instance
    Then: A demodulation matrix for each beam is produced and the correct call to the quality storage system was made
    """

    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )

    # When
    task, quality_mocker = ci_instrument_polarization_calibration_task
    task()

    # Then
    for beam in [1]:
        tags = [
            CryonirspTag.intermediate(),
            CryonirspTag.task_demodulation_matrices(),
            CryonirspTag.beam(beam),
        ]
        assert len(list(task.read(tags=tags))) == 1

        quality_mocker.assert_any_call(
            task,
            polcal_fitter=ANY,
            label=f"CI Beam {beam}",
            bin_nums=[
                task.parameters.polcal_num_spatial_bins,
                task.parameters.polcal_num_spatial_bins,
            ],
            bin_labels=["spatial", "spatial"],
            skip_recording_constant_pars=False,
        )


def test_sp_instrument_polarization_calibration_task(
    sp_instrument_polarization_calibration_task,
    mocker,
    fake_gql_client,
):
    """
    Given: An InstrumentPolarizationCalibration task
    When: Calling the task instance
    Then: A demodulation matrix for each beam is produced and the correct call to the quality storage system was made
    """

    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )

    # When
    task, quality_mocker = sp_instrument_polarization_calibration_task
    task()

    # Then
    for beam in [1, 2]:
        tags = [
            CryonirspTag.intermediate(),
            CryonirspTag.task_demodulation_matrices(),
            CryonirspTag.beam(beam),
        ]
        assert len(list(task.read(tags=tags))) == 1

        quality_mocker.assert_any_call(
            task,
            polcal_fitter=ANY,
            label=f"SP Beam {beam}",
            bin_nums=[
                task.parameters.polcal_num_spatial_bins,
                task.parameters.polcal_num_spectral_bins,
            ],
            bin_labels=["spatial", "spectral"],
            skip_recording_constant_pars=beam == 2,
        )


def test_reshape_ci_demod_matrices(
    ci_instrument_polarization_calibration_task_with_no_data,
    multiple_demodulation_matrices,
    full_beam_shape,
):
    """
    Given: An InstrumentPolarizationCalibration task and a set of demodulation matrices sampled over the full FOV
    When: Up-sampling the demodulation matrices
    Then: The final set of demodulation matrices has the correct, full-FOV shape
    """
    ci_instrument_polarization_calibration_task_with_no_data.single_beam_shape = full_beam_shape
    result = ci_instrument_polarization_calibration_task_with_no_data.reshape_demod_matrices(
        multiple_demodulation_matrices
    )
    assert result.shape == full_beam_shape + (4, 10)


def test_reshape_sp_demod_matrices(
    sp_instrument_polarization_calibration_task_with_no_data,
    multiple_demodulation_matrices,
    full_beam_shape,
):
    """
    Given: An InstrumentPolarizationCalibration task and a set of demodulation matrices sampled over the full FOV
    When: Up-sampling the demodulation matrices
    Then: The final set of demodulation matrices has the correct, full-FOV shape
    """
    sp_instrument_polarization_calibration_task_with_no_data.single_beam_shape = full_beam_shape
    result = sp_instrument_polarization_calibration_task_with_no_data.reshape_demod_matrices(
        multiple_demodulation_matrices
    )
    assert result.shape == full_beam_shape + (4, 10)


def test_reshape_single_ci_demod_matrix(
    ci_instrument_polarization_calibration_task_with_no_data,
    single_demodulation_matrix,
    full_beam_shape,
):
    """
    Given: An InstrumentPolarizationCalibration task and a single demodulation matrix for the whole FOV
    When: Up-sampling the demodulation matrices
    Then: The final set of demodulation matrices still only has a single matrix
    """
    ci_instrument_polarization_calibration_task_with_no_data.single_beam_shape = full_beam_shape
    result = ci_instrument_polarization_calibration_task_with_no_data.reshape_demod_matrices(
        single_demodulation_matrix
    )
    assert result.shape == (4, 10)


def test_reshape_single_sp_demod_matrix(
    sp_instrument_polarization_calibration_task_with_no_data,
    single_demodulation_matrix,
    full_beam_shape,
):
    """
    Given: An InstrumentPolarizationCalibration task and a single demodulation matrix for the whole FOV
    When: Up-sampling the demodulation matrices
    Then: The final set of demodulation matrices still only has a single matrix
    """
    sp_instrument_polarization_calibration_task_with_no_data.single_beam_shape = full_beam_shape
    result = sp_instrument_polarization_calibration_task_with_no_data.reshape_demod_matrices(
        single_demodulation_matrix
    )
    assert result.shape == (4, 10)
