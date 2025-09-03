from datetime import datetime

import numpy as np
import pytest
from astropy.io import fits
from dkist_header_validator import spec122_validator
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.codecs.json import json_decoder

from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.tasks.sp_wavelength_calibration import SPWavelengthCalibration
from dkist_processing_cryonirsp.tests.conftest import CryonirspConstantsDb
from dkist_processing_cryonirsp.tests.conftest import cryonirsp_testing_parameters_factory
from dkist_processing_cryonirsp.tests.conftest import generate_fits_frame
from dkist_processing_cryonirsp.tests.header_models import CryonirspHeadersValidSPSolarGainFrames


@pytest.fixture(scope="function")
def sp_dispersion_axis_correction_task(
    tmp_path,
    recipe_run_id,
    assign_input_dataset_doc_to_task,
    init_cryonirsp_constants_db,
):
    num_map_scans = 2
    num_beams = 2
    num_scan_steps = 2
    num_modstates = 2
    array_shape = (1, 30, 60)
    char_spec_shape = (916,)
    grating_position_deg = 62.505829779431224
    grating_littrow_angle = -5.5
    grating_constant = 31.6
    dataset_shape = (num_beams * num_map_scans * num_scan_steps * num_modstates,) + array_shape[1:]

    constants_db = CryonirspConstantsDb(
        NUM_BEAMS=num_beams,
        GRATING_POSITION_DEG=grating_position_deg,
        GRATING_LITTROW_ANGLE_DEG=grating_littrow_angle,
        GRATING_CONSTANT=grating_constant,
        SOLAR_GAIN_IP_START_TIME="2021-01-01T00:00:00",
    )
    init_cryonirsp_constants_db(recipe_run_id, constants_db)
    with SPWavelengthCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="sp_dispersion_axis_correction",
        workflow_version="VX.Y",
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            all_ones = np.ones(char_spec_shape)
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            param_class = cryonirsp_testing_parameters_factory(task)
            assign_input_dataset_doc_to_task(task, param_class())

            # Create fake solar charcteristic spectra
            for beam in range(1, num_beams + 1):
                char_spec_hdul = fits.HDUList([fits.PrimaryHDU(data=all_ones)])
                task.write(
                    data=char_spec_hdul,
                    tags=[
                        CryonirspTag.intermediate_frame(beam=beam),
                        CryonirspTag.task_characteristic_spectra(),
                        CryonirspTag.beam(beam),
                    ],
                    encoder=fits_hdulist_encoder,
                )

                # And a beam border intermediate array
                task.write(
                    data=np.array([0, 30, ((beam - 1) * 30), (30 + (beam - 1) * 30)]),
                    tags=[
                        CryonirspTag.intermediate_frame(beam=beam),
                        CryonirspTag.task_beam_boundaries(),
                    ],
                    encoder=fits_array_encoder,
                )

                # Create fake linearized solar gain array with headers
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
                header = hdul[0].header
                # set the slit width to a realistic Cryo value
                header["CNSLITW"] = 175
                task.write(
                    data=hdul,
                    tags=[
                        CryonirspTag.linearized_frame(beam=beam),
                        CryonirspTag.task_solar_gain(),
                    ],
                    encoder=fits_hdulist_encoder,
                )

            yield task, header
        except:
            raise
        finally:
            task._purge()


def test_sp_dispersion_axis_correction(sp_dispersion_axis_correction_task, mocker, fake_gql_client):
    """
    Given: A SPDispersionAxisCorrection task
    When: Calling the task instance
    Then: There are the expected number of intermediate fit frames with the correct tags applied and the values have been correctly fit
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )

    task, original_header = sp_dispersion_axis_correction_task
    task()
    tags = [
        CryonirspTag.task_spectral_fit(),
        CryonirspTag.intermediate(),
    ]
    fit_result = next(task.read(tags=tags, decoder=json_decoder))

    # make sure that the values have changed
    assert original_header["CRVAL1"] != fit_result["CRVAL1"]
    assert original_header["CDELT1"] != fit_result["CDELT1"]
    assert original_header["CRVAL1A"] != fit_result["CRVAL1A"]
    assert original_header["CDELT1A"] != fit_result["CDELT1A"]
