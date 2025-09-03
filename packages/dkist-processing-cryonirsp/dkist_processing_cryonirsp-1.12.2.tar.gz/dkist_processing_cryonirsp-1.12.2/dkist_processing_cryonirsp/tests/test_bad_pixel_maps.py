from datetime import datetime

import numpy as np
import pytest
from astropy.io import fits
from dkist_header_validator import spec122_validator
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_service_configuration.logging import logger

from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.tasks.bad_pixel_map import BadPixelMapCalibration
from dkist_processing_cryonirsp.tests.conftest import CryonirspConstantsDb
from dkist_processing_cryonirsp.tests.conftest import cryonirsp_testing_parameters_factory
from dkist_processing_cryonirsp.tests.conftest import generate_fits_frame
from dkist_processing_cryonirsp.tests.header_models import CryonirspHeadersValidCISolarGainFrames


@pytest.fixture(scope="function", params=["CI", "SP"])
def compute_bad_pixel_map_task(
    tmp_path,
    recipe_run_id,
    assign_input_dataset_doc_to_task,
    init_cryonirsp_constants_db,
    request,
):
    arm_id = request.param
    if arm_id == "SP":
        dataset_shape = (1, 100, 200)
        array_shape = (1, 100, 200)
    else:
        dataset_shape = (1, 100, 100)
        array_shape = (1, 100, 100)
    constants_db = CryonirspConstantsDb(ARM_ID=arm_id)
    init_cryonirsp_constants_db(recipe_run_id, constants_db)
    with BadPixelMapCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="sp_compute_bad_pixel_map",
        workflow_version="VX.Y",
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            param_class = cryonirsp_testing_parameters_factory(task)
            assign_input_dataset_doc_to_task(task, param_class())
            start_time = datetime.now()
            ds = CryonirspHeadersValidCISolarGainFrames(
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
            # Create an array with a random number of zero and hot values
            rng = np.random.default_rng()
            # Generate rabdomly the number of bad pixels to be used in trange(50, 100)
            num_bad_pixels = rng.integers(50, 100)
            # Let 2/3 of the bad pixels be hot
            num_hot_pixels = num_bad_pixels * 2 // 3
            # Let the remaining 1/3 be zero
            num_zero_pixels = num_bad_pixels - num_hot_pixels
            logger.debug(f"{num_bad_pixels = }, {num_hot_pixels = }, {num_zero_pixels = }")
            nelem = np.prod(array_shape)
            array = 1000.0 * np.ones(nelem)
            # Need choice here with replace=False to avoid generating duplicates
            bad_pixel_locs = rng.choice(nelem, size=num_bad_pixels, replace=False)
            hot_pixel_locs = sorted(bad_pixel_locs[:num_hot_pixels])
            zero_pixel_locs = sorted(bad_pixel_locs[num_hot_pixels:])
            array[zero_pixel_locs] = 0.0
            array[hot_pixel_locs] = 2000.0
            array = array.reshape(array_shape[1:])
            hdul[0].data = array
            task.write(
                data=hdul,
                tags=[
                    CryonirspTag.linearized_frame(),
                    CryonirspTag.task_solar_gain(),
                ],
                encoder=fits_hdulist_encoder,
            )
            yield task, num_zero_pixels, num_hot_pixels
        finally:
            task._purge()


def test_compute_bad_pixel_map_task(compute_bad_pixel_map_task, mocker, fake_gql_client):
    """
    Given: An BadPixelMapCalibration task
    When: Calling the task instance with known input data
    Then: The correct beam boundary values are created and saved as intermediate files
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    # Given
    task, num_zeros, num_hot = compute_bad_pixel_map_task
    # When
    task()
    # Then
    tags = [CryonirspTag.task_bad_pixel_map()]
    bad_pixel_map_paths = list(task.read(tags))
    assert len(bad_pixel_map_paths) == 1
    bad_pixel_map_hdul = fits.open(bad_pixel_map_paths[0])
    bad_pixel_map = bad_pixel_map_hdul[0].data
    num_bad_pixels = bad_pixel_map.sum()
    assert num_bad_pixels == num_zeros + num_hot
