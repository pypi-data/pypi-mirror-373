"""Test the linearity correction task."""

import re
from dataclasses import dataclass
from datetime import datetime

import numpy as np
import pytest
from astropy.io import fits
from dkist_header_validator import spec122_validator
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.models.tags import Tag
from dkist_service_configuration.logging import logger

from dkist_processing_cryonirsp.models.constants import CryonirspBudName
from dkist_processing_cryonirsp.models.exposure_conditions import AllowableOpticalDensityFilterNames
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.tasks.linearity_correction import LinearityCorrection
from dkist_processing_cryonirsp.tests.conftest import CryonirspConstantsDb
from dkist_processing_cryonirsp.tests.conftest import cryonirsp_testing_parameters_factory
from dkist_processing_cryonirsp.tests.conftest import generate_fits_frame
from dkist_processing_cryonirsp.tests.header_models import CryonirspHeadersValidNonLinearizedFrames


@pytest.fixture(scope="function")
def linearity_correction(
    tmp_path,
    recipe_run_id,
    assign_input_dataset_doc_to_task,
    init_cryonirsp_constants_db,
    arm_id,
    frames_in_ramp,
    filter_name,
):
    #                    time        y   x
    dataset_shape = (frames_in_ramp, 10, 10)
    #              z   y   x
    array_shape = (1, 10, 10)
    time_delta = 0.1
    start_time = datetime.now()
    expected_num_frames_in_ramp = 10
    constants_db = CryonirspConstantsDb(
        TIME_OBS_LIST=(str(start_time),),
        ARM_ID=arm_id,
        ROI_1_SIZE_X=array_shape[2],
        ROI_1_SIZE_Y=array_shape[1],
    )
    init_cryonirsp_constants_db(recipe_run_id, constants_db)
    with LinearityCorrection(
        recipe_run_id=recipe_run_id,
        workflow_name="linearity_correction",
        workflow_version="VX.Y",
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            param_class = cryonirsp_testing_parameters_factory(task)
            assign_input_dataset_doc_to_task(task, param_class())
            ds = CryonirspHeadersValidNonLinearizedFrames(
                arm_id=arm_id,
                camera_readout_mode="FastUpTheRamp",
                dataset_shape=dataset_shape,
                array_shape=array_shape,
                time_delta=time_delta,
                roi_x_origin=0,
                roi_y_origin=0,
                roi_x_size=array_shape[2],
                roi_y_size=array_shape[1],
                date_obs=start_time.isoformat("T"),
                exposure_time=time_delta,
            )
            # Initial header creation...
            header_generator = (
                spec122_validator.validate_and_translate_to_214_l0(
                    d.header(), return_type=fits.HDUList
                )[0].header
                for d in ds
            )
            # Patch the headers for non-linearized Cryo data...
            header_list = []
            exp_time = 0.0
            counter = 0
            for header in header_generator:
                # Set the integrated exposure time for this NDR
                # This is a range from 0 to 90 in 10 steps
                header["XPOSURE"] = 100 * counter * time_delta
                # Set the current frame in ramp, 1-based
                header["CNCNDR"] = counter + 1
                header["CNNNDR"] = expected_num_frames_in_ramp
                header["CNFILTNP"] = filter_name
                header_list.append(header)
                counter += 1
            # Step on the old one with the new one
            header_generator = (header for header in header_list)
            # Iterate through the headers and create the frames...
            for _ in header_list:
                hdul = generate_fits_frame(header_generator=header_generator, shape=array_shape)
                # Now tweak the data...
                for hdu in hdul:
                    header = hdu.header
                    exp_time = header["XPOSURE"]
                    # Create a simple perfectly linear ramp
                    hdu.data.fill(exp_time)
                    task.write(
                        data=hdul,
                        tags=[
                            CryonirspTag.input(),
                            CryonirspTag.frame(),
                            CryonirspTag.curr_frame_in_ramp(header["CNCNDR"]),
                            # All frames in a ramp have the same date-obs
                            CryonirspTag.time_obs(str(start_time)),
                            Tag.readout_exp_time(exp_time),
                        ],
                        encoder=fits_hdulist_encoder,
                    )
            task.constants._update({CryonirspBudName.camera_readout_mode.value: "FastUpTheRamp"})
            yield task, filter_name, expected_num_frames_in_ramp
        finally:
            task._purge()


@pytest.mark.parametrize(
    "filter_name",
    [
        pytest.param(AllowableOpticalDensityFilterNames.G358.value),
        pytest.param(AllowableOpticalDensityFilterNames.OPEN.value),
    ],
)
@pytest.mark.parametrize(
    "frames_in_ramp",
    [pytest.param(10, id="Full ramp"), pytest.param(5, id="Bad ramp")],
)
@pytest.mark.parametrize(
    "arm_id",
    [pytest.param("CI", id="CI"), pytest.param("SP", id="SP")],
)
@pytest.mark.parametrize(
    "num_chunks",
    [pytest.param(1, id="1 chunk"), pytest.param(2, id="2 chunks")],
)
def test_linearity_correction(
    linearity_correction,
    mocker,
    fake_gql_client,
    arm_id,
    frames_in_ramp,
    num_chunks,
    filter_name,
):
    """
    Given: A LinearityCorrection task
    When: Calling the task instance with known input data
    Then: The non-linearized frames are linearized and produce the correct results.
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    if num_chunks == 2:
        mocker.patch(
            "dkist_processing_cryonirsp.tasks.linearity_correction.LinearityCorrection.compute_linear_chunk_size",
            new=lambda self, frame_size, num_frames_in_ramp: frame_size // 2,
        )
    # Given
    task, filter_name, expected_num_frames_in_ramp = linearity_correction
    # When
    task()
    # Then
    tags = CryonirspTag.linearized_frame()
    # We used a perfect linear ramp from 0 to 90, where the ramp value is equal to the exposure time in ms
    # The algorithm normalizes the linearized frame by the exposure time in seconds, so the expected value is:
    # 90 / (90 / 1000) = 1000 / attenuation, where attenuation is the multiplicative attenuation due to the
    # filter in use
    attenuation = 10 ** (task.parameters.linearization_filter_attenuation_dict[filter_name])
    expected_data = np.ones((10, 10)) * 1000.0 / attenuation
    files_found = list(task.read(tags=tags))
    if frames_in_ramp == expected_num_frames_in_ramp:
        assert len(files_found) == 1
        hdul = fits.open(files_found[0])
        data = hdul[0].data
        assert np.allclose(data, expected_data)
    else:
        assert len(files_found) == 0


@pytest.fixture
def simple_linearity_correction_task(recipe_run_id, arm_id, init_cryonirsp_constants_db, tmp_path):
    constants_db = CryonirspConstantsDb(
        ARM_ID=arm_id,
    )
    init_cryonirsp_constants_db(recipe_run_id, constants_db)
    with LinearityCorrection(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(recipe_run_id=recipe_run_id, scratch_base_path=tmp_path)

        yield task

        task._purge()


@dataclass
class DummyRampFitsAccess:
    """Just a class that has the one property that is checked during ramp validation."""

    num_frames_in_ramp: int
    ip_task_type: str = "TASK"


@pytest.mark.parametrize(
    "arm_id",
    [pytest.param("CI", id="CI"), pytest.param("SP", id="SP")],
)
@pytest.mark.parametrize(
    "ramp_list, valid, message",
    [
        pytest.param(
            [
                DummyRampFitsAccess(num_frames_in_ramp=2),
                DummyRampFitsAccess(num_frames_in_ramp=3),
            ],
            False,
            "Not all frames have the same FRAMES_IN_RAMP value. Set is {2, 3}. Ramp is task TASK. Skipping ramp.",
            id="num_frames_mismatch_actual_frames",
        ),
        pytest.param(
            [
                DummyRampFitsAccess(num_frames_in_ramp=8),
            ],
            False,
            "Missing some ramp frames. Expected 8 from header value, but only have 1. Ramp is task TASK. Skipping ramp.",
            id="num_frames_in_set_mismatch",
        ),
    ],
)
def test_is_ramp_valid(simple_linearity_correction_task, ramp_list, valid, message, caplog):
    logger.add(caplog.handler)
    assert simple_linearity_correction_task.is_ramp_valid(ramp_list) is valid
    if not valid:
        assert re.search(message, caplog.text)
