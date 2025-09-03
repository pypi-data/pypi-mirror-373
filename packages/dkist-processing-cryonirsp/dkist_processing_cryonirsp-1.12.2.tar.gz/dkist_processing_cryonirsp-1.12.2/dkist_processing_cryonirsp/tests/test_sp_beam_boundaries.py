from datetime import datetime

import numpy as np
import pytest
from astropy.io import fits
from dkist_header_validator import spec122_validator
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder

from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.tasks.sp_beam_boundaries import SPBeamBoundariesCalibration
from dkist_processing_cryonirsp.tests.conftest import CryonirspConstantsDb
from dkist_processing_cryonirsp.tests.conftest import cryonirsp_testing_parameters_factory
from dkist_processing_cryonirsp.tests.conftest import fake_gql_client
from dkist_processing_cryonirsp.tests.conftest import generate_fits_frame
from dkist_processing_cryonirsp.tests.header_models import CryonirspHeadersValidSPSolarGainFrames


@pytest.fixture(scope="function")
def compute_beam_boundaries_task(
    tmp_path,
    recipe_run_id,
    assign_input_dataset_doc_to_task,
    init_cryonirsp_constants_db,
):
    arm_id = "SP"
    dataset_shape = (1, 100, 200)
    array_shape = (1, 100, 200)
    constants_db = CryonirspConstantsDb(ARM_ID=arm_id)
    init_cryonirsp_constants_db(recipe_run_id, constants_db)
    with SPBeamBoundariesCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="sp_compute_beam_boundaries",
        workflow_version="VX.Y",
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            param_class = cryonirsp_testing_parameters_factory(task)
            assign_input_dataset_doc_to_task(task, param_class())
            # Create fake bad pixel map
            task.write(
                data=np.zeros(array_shape[1:]),
                tags=[CryonirspTag.intermediate_frame(), CryonirspTag.task_bad_pixel_map()],
                encoder=fits_array_encoder,
            )
            start_time = datetime.now()
            ds = CryonirspHeadersValidSPSolarGainFrames(
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
            # Tweak data to form a beam illumination pattern
            # Data from generate_fits_frame are value 150
            array = hdul[0].data
            # Initial illumination borders that are made up. Precise border depends on the algorithm.
            # [0:0, v_min:v_max, h_min:h_max]
            array[:, 7:-5, 3:-8] = 1000.0
            # Put some large vertical streaks in the image to help the shift measurement converge
            minus_streak_pos = array_shape[2] // 4 - 1
            plus_streak_pos = 3 * array_shape[2] // 4 + 1
            array[:, :, minus_streak_pos - 5 : minus_streak_pos + 5] += 100
            array[:, :, plus_streak_pos - 5 : plus_streak_pos + 5] += 100
            hdul[0].data = array
            task.write(
                data=hdul,
                tags=[
                    CryonirspTag.linearized_frame(),
                    CryonirspTag.task_solar_gain(),
                ],
                encoder=fits_hdulist_encoder,
            )
            yield task, arm_id
        finally:
            task._purge()


def test_compute_beam_boundaries_task(compute_beam_boundaries_task, mocker, fake_gql_client):
    """
    Given: A SPBeamBoundariesCalibration task
    When: Calling the task instance with known input data
    Then: The correct beam boundary values are created and saved as intermediate files
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    # Given
    task, arm_id = compute_beam_boundaries_task
    # When
    task()
    # Then
    beam_1_tags = [CryonirspTag.task_beam_boundaries(), CryonirspTag.beam(1)]
    beam_1_boundary = np.array([7, 94, 10, 88])
    beam_2_tags = [CryonirspTag.task_beam_boundaries(), CryonirspTag.beam(2)]
    beam_2_boundary = np.array([8, 95, 112, 190])
    files_found = list(task.read(tags=beam_1_tags))
    assert len(files_found) == 1
    array1 = fits.open(files_found[0])[0].data
    assert np.array_equal(array1, beam_1_boundary)
    files_found = list(task.read(tags=beam_2_tags))
    assert len(files_found) == 1
    array2 = fits.open(files_found[0])[0].data
    assert np.array_equal(array2, beam_2_boundary)
