import json

import numpy as np
import pytest
from astropy.io import fits
from dkist_header_validator import spec122_validator
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder

from dkist_processing_cryonirsp.models.exposure_conditions import AllowableOpticalDensityFilterNames
from dkist_processing_cryonirsp.models.exposure_conditions import ExposureConditions
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.tasks.dark import DarkCalibration
from dkist_processing_cryonirsp.tests.conftest import CryonirspConstantsDb
from dkist_processing_cryonirsp.tests.conftest import cryonirsp_testing_parameters_factory
from dkist_processing_cryonirsp.tests.conftest import generate_fits_frame
from dkist_processing_cryonirsp.tests.header_models import CryonirspHeadersValidDarkFrames


@pytest.fixture(scope="function")
def sp_dark_calibration_task(
    tmp_path, assign_input_dataset_doc_to_task, init_cryonirsp_constants_db, recipe_run_id
):
    # Make sure we test cases where either the exp time or filter are the same, but the other value is
    # different
    exposure_conditions = (
        ExposureConditions(100.0, AllowableOpticalDensityFilterNames.OPEN.value),
        ExposureConditions(1.0, AllowableOpticalDensityFilterNames.G278.value),
        ExposureConditions(0.01, AllowableOpticalDensityFilterNames.NONE.value),
        ExposureConditions(100.0, AllowableOpticalDensityFilterNames.G278.value),
    )
    unused_exposure_condition = ExposureConditions(
        200.0, AllowableOpticalDensityFilterNames.NONE.value
    )
    constants_db = CryonirspConstantsDb(
        SP_NON_DARK_AND_NON_POLCAL_TASK_EXPOSURE_CONDITIONS_LIST=exposure_conditions,
        ARM_ID="SP",
    )
    init_cryonirsp_constants_db(recipe_run_id, constants_db)
    with DarkCalibration(
        recipe_run_id=recipe_run_id, workflow_name="dark_calibration", workflow_version="VX.Y"
    ) as task:
        illuminated_beam_shape = (6, 4)
        num_beams = 2
        num_exp_cond = len(exposure_conditions) + 1  # +1 for the unused condition
        num_frames_per_condition = 3
        array_shape = (1, 10, 20)
        dataset_shape = (num_exp_cond * num_frames_per_condition, 20, 10)
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            param_class = cryonirsp_testing_parameters_factory(task)
            assign_input_dataset_doc_to_task(task, param_class())

            # Create fake beam border intermediate arrays
            for beam in range(1, num_beams + 1):
                spectral_starting_pixel = 5 + ((beam - 1) * 10)
                beam_boundaries = np.array(
                    [
                        3,
                        3 + illuminated_beam_shape[0],
                        spectral_starting_pixel,
                        spectral_starting_pixel + illuminated_beam_shape[1],
                    ]
                )
                task.write(
                    data=beam_boundaries,
                    tags=[
                        CryonirspTag.intermediate_frame(beam=beam),
                        CryonirspTag.task_beam_boundaries(),
                    ],
                    encoder=fits_array_encoder,
                )

            ds = CryonirspHeadersValidDarkFrames(
                dataset_shape=dataset_shape,
                array_shape=array_shape,
                time_delta=10,
                exposure_time=1.0,
            )
            header_generator = (
                spec122_validator.validate_and_translate_to_214_l0(
                    d.header(), return_type=fits.HDUList
                )[0].header
                for d in ds
            )

            for condition in exposure_conditions + (unused_exposure_condition,):
                for _ in range(num_frames_per_condition):
                    hdul = generate_fits_frame(header_generator=header_generator, shape=array_shape)
                    hdul[0].data.fill(condition.exposure_time)
                    task.write(
                        data=hdul,
                        tags=[
                            CryonirspTag.linearized_frame(exposure_conditions=condition),
                            CryonirspTag.task_dark(),
                        ],
                        encoder=fits_hdulist_encoder,
                    )
            yield task, num_beams, exposure_conditions, unused_exposure_condition, illuminated_beam_shape
        finally:
            task._purge()


@pytest.fixture(scope="function")
def ci_dark_calibration_task(
    tmp_path, assign_input_dataset_doc_to_task, init_cryonirsp_constants_db, recipe_run_id
):
    # Make sure we test cases where either the exp time or filter are the same, but the other value is
    # different
    exposure_conditions = (
        ExposureConditions(100.0, AllowableOpticalDensityFilterNames.OPEN.value),
        ExposureConditions(1.0, AllowableOpticalDensityFilterNames.G278.value),
        ExposureConditions(0.01, AllowableOpticalDensityFilterNames.NONE.value),
        ExposureConditions(100.0, AllowableOpticalDensityFilterNames.G278.value),
    )
    unused_exposure_condition = ExposureConditions(
        200.0, AllowableOpticalDensityFilterNames.NONE.value
    )

    constants_db = CryonirspConstantsDb(
        CI_NON_DARK_AND_NON_POLCAL_AND_NON_LAMP_GAIN_TASK_EXPOSURE_CONDITIONS_LIST=exposure_conditions,
        ARM_ID="CI",
    )
    init_cryonirsp_constants_db(recipe_run_id, constants_db)
    with DarkCalibration(
        recipe_run_id=recipe_run_id, workflow_name="dark_calibration", workflow_version="VX.Y"
    ) as task:
        num_exp_cond = len(exposure_conditions) + 1  # +1 for the unused condition
        num_frames_per_condition = 3
        array_shape = (1, 10, 10)
        dataset_shape = (num_exp_cond * num_frames_per_condition, 20, 10)
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            param_class = cryonirsp_testing_parameters_factory(task)
            assign_input_dataset_doc_to_task(task, param_class())

            # Need a beam boundary file
            task.write(
                data=np.array([0, 10, 0, 10]),
                tags=[CryonirspTag.intermediate_frame(beam=1), CryonirspTag.task_beam_boundaries()],
                encoder=fits_array_encoder,
            )

            ds = CryonirspHeadersValidDarkFrames(
                dataset_shape=dataset_shape,
                array_shape=array_shape,
                time_delta=10,
                exposure_time=1.0,
            )
            header_generator = (
                spec122_validator.validate_and_translate_to_214_l0(
                    d.header(), return_type=fits.HDUList
                )[0].header
                for d in ds
            )
            for condition in exposure_conditions + (unused_exposure_condition,):
                for _ in range(num_frames_per_condition):
                    hdul = generate_fits_frame(header_generator=header_generator, shape=array_shape)
                    hdul[0].data.fill(condition.exposure_time)
                    task.write(
                        data=hdul,
                        tags=[
                            CryonirspTag.linearized_frame(exposure_conditions=condition),
                            CryonirspTag.task_dark(),
                        ],
                        encoder=fits_hdulist_encoder,
                    )
            yield task, exposure_conditions, unused_exposure_condition
        finally:
            task._purge()


def test_sp_dark_calibration_task(sp_dark_calibration_task, mocker, fake_gql_client):
    """
    Given: A DarkCalibration task with multiple task exposure times
    When: Calling the task instance
    Then: Only one average intermediate dark frame exists for each exposure time and unused times are not made
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    # When
    (
        task,
        num_beams,
        exp_conditions,
        unused_condition,
        illuminated_beam_shape,
    ) = sp_dark_calibration_task
    task()
    # Then
    for condition in exp_conditions:
        for b in range(num_beams):
            files = list(
                task.read(
                    tags=[
                        CryonirspTag.task_dark(),
                        CryonirspTag.intermediate_frame(beam=b + 1),
                        CryonirspTag.exposure_conditions(condition),
                    ]
                )
            )
            assert len(files) == 1
            expected = np.ones(illuminated_beam_shape) * condition.exposure_time
            hdul = fits.open(files[0])
            np.testing.assert_equal(expected, hdul[0].data)
            hdul.close()

    unused_time_read = task.read(
        tags=[
            CryonirspTag.task_dark(),
            CryonirspTag.intermediate_frame(),
            CryonirspTag.exposure_conditions(unused_condition),
        ]
    )
    assert len(list(unused_time_read)) == 0

    quality_files = task.read(tags=[CryonirspTag.quality("TASK_TYPES")])
    for file in quality_files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert data["total_frames"] == task.scratch.count_all(
                tags=[CryonirspTag.linearized_frame(), CryonirspTag.task_dark()]
            )
            assert data["frames_not_used"] == 3


def test_ci_dark_calibration_task(ci_dark_calibration_task, mocker, fake_gql_client):
    """
    Given: A DarkCalibration task with multiple task exposure times
    When: Calling the task instance
    Then: Only one average intermediate dark frame exists for each exposure time and unused times are not made
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    # When
    task, exp_conditions, unused_condition = ci_dark_calibration_task
    task()
    # Then
    for condition in exp_conditions:
        files = list(
            task.read(
                tags=[
                    CryonirspTag.task_dark(),
                    CryonirspTag.intermediate_frame(beam=1, exposure_conditions=condition),
                ]
            )
        )
        assert len(files) == 1
        expected = np.ones((10, 10)) * condition.exposure_time
        hdul = fits.open(files[0])
        np.testing.assert_equal(expected, hdul[0].data)
        hdul.close()

    unused_time_read = task.read(
        tags=[
            CryonirspTag.task_dark(),
            CryonirspTag.intermediate_frame(exposure_conditions=unused_condition),
        ]
    )
    assert len(list(unused_time_read)) == 0

    quality_files = task.read(tags=[CryonirspTag.quality("TASK_TYPES")])
    for file in quality_files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert data["total_frames"] == task.scratch.count_all(
                tags=[CryonirspTag.linearized_frame(), CryonirspTag.task_dark()]
            )
            assert data["frames_not_used"] == 3
