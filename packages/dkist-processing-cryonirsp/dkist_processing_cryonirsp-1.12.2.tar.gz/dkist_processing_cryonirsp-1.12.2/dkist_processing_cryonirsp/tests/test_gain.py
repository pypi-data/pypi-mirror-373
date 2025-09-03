import json
from datetime import datetime

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
from dkist_processing_cryonirsp.tasks.gain import CISolarGainCalibration
from dkist_processing_cryonirsp.tasks.gain import LampGainCalibration
from dkist_processing_cryonirsp.tests.conftest import CryonirspConstantsDb
from dkist_processing_cryonirsp.tests.conftest import cryonirsp_testing_parameters_factory
from dkist_processing_cryonirsp.tests.conftest import generate_fits_frame
from dkist_processing_cryonirsp.tests.header_models import CryonirspHeadersValidLampGainFrames


@pytest.fixture
def ci_solar_gain_calibration_task(
    tmp_path,
    recipe_run_id,
    assign_input_dataset_doc_to_task,
    init_cryonirsp_constants_db,
):
    dataset_shape = (1, 10, 10)
    array_shape = (1, 10, 10)
    intermediate_shape = (10, 10)
    constants_db = CryonirspConstantsDb(NUM_MODSTATES=1, ARM_ID="CI")
    exposure_conditions = constants_db.SOLAR_GAIN_EXPOSURE_CONDITIONS_LIST[0]
    init_cryonirsp_constants_db(recipe_run_id, constants_db)
    with CISolarGainCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="ci_solar_gain_calibration",
        workflow_version="VX.Y",
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            param_class = cryonirsp_testing_parameters_factory(task)
            assign_input_dataset_doc_to_task(task, param_class())
            # Need a beam boundary file
            task.write(
                data=np.array([0, intermediate_shape[0], 0, intermediate_shape[1]]),
                tags=[CryonirspTag.intermediate_frame(beam=1), CryonirspTag.task_beam_boundaries()],
                encoder=fits_array_encoder,
            )
            # Create fake bad pixel map
            task.write(
                data=np.zeros(array_shape[1:]),
                tags=[CryonirspTag.intermediate_frame(), CryonirspTag.task_bad_pixel_map()],
                encoder=fits_array_encoder,
            )
            dark_signal = 3.0
            start_time = datetime.now()
            # Make intermediate dark frame
            dark_cal = np.ones(intermediate_shape) * dark_signal
            task.write(
                data=dark_cal,
                tags=[
                    CryonirspTag.intermediate_frame(
                        beam=1, exposure_conditions=exposure_conditions
                    ),
                    CryonirspTag.task_dark(),
                ],
                encoder=fits_array_encoder,
            )

            solar_signal = 6.28
            ds = CryonirspHeadersValidLampGainFrames(
                dataset_shape=dataset_shape,
                array_shape=array_shape,
                time_delta=10,
                start_time=start_time,
            )
            header_generator = (
                spec122_validator.validate_and_translate_to_214_l0(
                    d.header(), return_type=fits.HDUList
                )[0].header
                for d in ds
            )
            hdul = generate_fits_frame(header_generator=header_generator, shape=array_shape)

            hdul[0].data.fill(solar_signal + dark_signal)
            tags = [
                CryonirspTag.linearized_frame(exposure_conditions=exposure_conditions),
                CryonirspTag.task_solar_gain(),
            ]
            task.write(
                data=hdul,
                tags=tags,
                encoder=fits_hdulist_encoder,
            )
            yield task, solar_signal
        finally:
            task._purge()


@pytest.fixture(scope="function")
def lamp_calibration_task(
    tmp_path,
    recipe_run_id,
    assign_input_dataset_doc_to_task,
    init_cryonirsp_constants_db,
    number_of_beams,
):
    exposure_conditions = ExposureConditions(100.0, AllowableOpticalDensityFilterNames.OPEN.value)
    dataset_shape = (1, 10, 20)
    array_shape = (1, 10, 20)
    intermediate_shape = (10, 10)
    constants_db = CryonirspConstantsDb(
        NUM_MODSTATES=1,
        ARM_ID="SP" if number_of_beams > 1 else "CI",
    )
    init_cryonirsp_constants_db(recipe_run_id, constants_db)
    with LampGainCalibration(
        recipe_run_id=recipe_run_id, workflow_name="sp_gain_calibration", workflow_version="VX.Y"
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            param_class = cryonirsp_testing_parameters_factory(task)
            assign_input_dataset_doc_to_task(task, param_class())
            # Need a beam boundary file
            task.write(
                data=np.array([0, intermediate_shape[0], 0, intermediate_shape[1]]),
                tags=[CryonirspTag.intermediate_frame(beam=1), CryonirspTag.task_beam_boundaries()],
                encoder=fits_array_encoder,
            )
            # Create fake bad pixel map
            task.write(
                data=np.zeros(array_shape[1:]),
                tags=[CryonirspTag.intermediate_frame(), CryonirspTag.task_bad_pixel_map()],
                encoder=fits_array_encoder,
            )
            dark_signal = 3.0
            start_time = datetime.now()
            # Make intermediate dark frame
            dark_cal = np.ones(intermediate_shape) * dark_signal

            # Need a dark for each beam
            for b in range(number_of_beams):
                task.write(
                    data=dark_cal,
                    tags=[
                        CryonirspTag.intermediate_frame(
                            beam=b + 1, exposure_conditions=exposure_conditions
                        ),
                        CryonirspTag.task_dark(),
                    ],
                    encoder=fits_array_encoder,
                )

                # Create fake beam border intermediate arrays
                task.write(
                    data=np.array([0, 10, (b * 10), 10 + (b * 10)]),
                    tags=[
                        CryonirspTag.intermediate_frame(beam=b + 1),
                        CryonirspTag.task_beam_boundaries(),
                    ],
                    encoder=fits_array_encoder,
                )

                # does this need to be in the beam loop as well?
                ds = CryonirspHeadersValidLampGainFrames(
                    dataset_shape=dataset_shape,
                    array_shape=array_shape,
                    time_delta=10,
                    start_time=start_time,
                )
                header_generator = (
                    spec122_validator.validate_and_translate_to_214_l0(
                        d.header(), return_type=fits.HDUList
                    )[0].header
                    for d in ds
                )
                hdul = generate_fits_frame(
                    header_generator=header_generator, shape=array_shape
                )  # Tweak data so that beam sides are slightly different
                # Use data != 1 to check normalization in test
                hdul[0].data.fill(1.1)
                tags = [
                    CryonirspTag.beam(b + 1),
                    CryonirspTag.task_lamp_gain(),
                    CryonirspTag.linearized_frame(exposure_conditions=exposure_conditions),
                ]
                task.write(
                    data=hdul,
                    tags=tags,
                    encoder=fits_hdulist_encoder,
                )
            yield task
        finally:
            task._purge()


def test_ci_solar_gain_calibration_task(ci_solar_gain_calibration_task, mocker, fake_gql_client):
    """
    Given: A CISolarGainCalibration task
    When: Calling the task instance
    Then: The correct number of output solar gain frames exists, are tagged correctly, and are not normalized
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    # When
    task, solar_signal = ci_solar_gain_calibration_task
    task()
    # Then
    tags = [
        CryonirspTag.task_solar_gain(),
        CryonirspTag.intermediate_frame(beam=1),
    ]
    files = list(task.read(tags=tags))
    num_files = len(files)
    assert num_files == 1  # Because only 1 beam in CI

    hdu = fits.open(files[0])[0]
    expected_results = np.ones((10, 10)) * solar_signal
    np.testing.assert_allclose(hdu.data, expected_results)

    tags = [
        CryonirspTag.task_lamp_gain(),
        CryonirspTag.intermediate(),
    ]
    for filepath in task.read(tags=tags):
        assert filepath.exists()

    quality_files = task.read(tags=[CryonirspTag.quality("TASK_TYPES")])
    for file in quality_files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert data["total_frames"] == num_files


@pytest.mark.parametrize("number_of_beams", [pytest.param(1, id="CI"), pytest.param(2, id="SP")])
def test_lamp_calibration_task(lamp_calibration_task, number_of_beams, mocker, fake_gql_client):
    """
    Given: A LampGainCalibration task
    When: Calling the task instance
    Then: The correct number of output lamp gain frames exists, are tagged correctly, and are normalized
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    # When
    task = lamp_calibration_task
    task()
    # Then
    tags = [
        CryonirspTag.task_lamp_gain(),
        CryonirspTag.intermediate(),
    ]
    num_files = task.scratch.count_all(tags)
    assert num_files == number_of_beams

    for j in range(number_of_beams):
        tags = [
            CryonirspTag.task_lamp_gain(),
            CryonirspTag.intermediate(),
            CryonirspTag.beam(j + 1),
        ]
        files = list(task.read(tags=tags))
        assert len(files) == 1
        hdu = fits.open(files[0])[0]
        expected_results = np.ones((10, 10))  # Because lamps are normalized
        np.testing.assert_allclose(hdu.data, expected_results)

    tags = [
        CryonirspTag.task_lamp_gain(),
        CryonirspTag.intermediate(),
    ]
    for filepath in task.read(tags=tags):
        assert filepath.exists()

    quality_files = task.read(tags=[CryonirspTag.quality("TASK_TYPES")])
    for file in quality_files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert data["total_frames"] == num_files
