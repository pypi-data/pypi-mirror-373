import json

import numpy as np
import pytest
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_math import transform

from dkist_processing_cryonirsp.codecs.fits import cryo_fits_array_decoder
from dkist_processing_cryonirsp.models.exposure_conditions import AllowableOpticalDensityFilterNames
from dkist_processing_cryonirsp.models.exposure_conditions import ExposureConditions
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.tasks.sp_geometric import SPGeometricCalibration
from dkist_processing_cryonirsp.tests.conftest import CryonirspConstantsDb
from dkist_processing_cryonirsp.tests.conftest import cryonirsp_testing_parameters_factory
from dkist_processing_cryonirsp.tests.conftest import generate_214_l0_fits_frame
from dkist_processing_cryonirsp.tests.header_models import CryonirspHeadersValidSPSolarGainFrames


@pytest.fixture(scope="function")
def geometric_calibration_task_that_completes(
    tmp_path, recipe_run_id, assign_input_dataset_doc_to_task, init_cryonirsp_constants_db
):
    # This fixture makes data that look enough like real data that all of the feature detection stuff at least runs
    # through (mostly this is an issue for the angle calculation). It would be great to contrive data that
    # produce a geometric calibration with real numbers that can be checked, but for now we'll rely on the grogu
    # tests for that. In other words, this fixture just tests if the machinery of the task completes and some object
    # (ANY object) is written correctly.
    number_of_modstates = 1
    number_of_beams = 2
    exposure_time = 20.0  # From CryonirspHeadersValidSolarGainFrames fixture
    exposure_conditions = ExposureConditions(
        exposure_time, AllowableOpticalDensityFilterNames.OPEN.value
    )
    data_shape_int = 100, 98
    data_shape_raw = 100, 196
    dataset_shape = 1, *data_shape_raw
    constants_db = CryonirspConstantsDb(
        NUM_MODSTATES=number_of_modstates,
        SOLAR_GAIN_EXPOSURE_CONDITIONS_LIST=(exposure_conditions,),
        ARM_ID="SP",
    )
    init_cryonirsp_constants_db(recipe_run_id, constants_db)
    with SPGeometricCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="sp_geometric_calibration",
        workflow_version="VX.Y",
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            param_class = cryonirsp_testing_parameters_factory(task)
            assign_input_dataset_doc_to_task(task, param_class())

            task.angles = [0.0, 0.0]
            task.offsets = np.zeros((number_of_beams, 2))
            task.shifts = np.zeros(data_shape_int[0])

            # Create the intermediate frames needed
            # Create fake bad pixel map
            task.write(
                data=np.zeros(data_shape_raw),
                tags=[CryonirspTag.intermediate_frame(), CryonirspTag.task_bad_pixel_map()],
                encoder=fits_array_encoder,
            )

            for beam in range(1, number_of_beams + 1):
                dark_cal = np.ones(data_shape_int) * 3.0
                task.write(
                    data=dark_cal,
                    tags=[
                        CryonirspTag.intermediate_frame(
                            beam=beam, exposure_conditions=exposure_conditions
                        ),
                        CryonirspTag.task_dark(),
                    ],
                    encoder=fits_array_encoder,
                )

                # Need a lamp for each beam
                lamp_gain = np.ones(data_shape_int)
                task.write(
                    data=lamp_gain,
                    tags=[
                        CryonirspTag.intermediate_frame(
                            beam=beam, exposure_conditions=exposure_conditions
                        ),
                        CryonirspTag.task_lamp_gain(),
                    ],
                    encoder=fits_array_encoder,
                )

                # And a beam border intermediate array
                border = data_shape_raw[1] // 2
                task.write(
                    data=np.array(
                        [
                            0,
                            data_shape_int[0],
                            ((beam - 1) * border),
                            (border + (beam - 1) * border),
                        ]
                    ),
                    tags=[
                        CryonirspTag.intermediate_frame(beam=beam),
                        CryonirspTag.task_beam_boundaries(),
                    ],
                    encoder=fits_array_encoder,
                )

            # Create the raw data, which is based on two beams per frame
            beam1 = 1
            beam2 = 2
            ds = CryonirspHeadersValidSPSolarGainFrames(
                dataset_shape=dataset_shape,
                array_shape=dataset_shape,
                time_delta=10,
            )
            header = ds.header()
            # Create each beam of the solar gain image, rotate and translate them, and then combine them into one
            true_solar_1 = np.ones(data_shape_int)
            true_solar_1[data_shape_int[0] // 2, :] += 5
            true_solar_1[:, data_shape_int[1] // 2] += 5
            true_solar_2 = np.copy(true_solar_1)
            # Now add the beam number to each beam in the array
            true_solar_1 += beam1
            true_solar_2 += beam2
            translated_solar_1 = next(
                transform.translate_arrays(arrays=true_solar_1, translation=task.offsets[0])
            )
            translated_solar_2 = next(
                transform.translate_arrays(arrays=true_solar_2, translation=task.offsets[1])
            )
            distorted_solar_1 = next(
                transform.rotate_arrays_about_point(arrays=translated_solar_1, angle=task.angles[0])
            )
            distorted_solar_2 = next(
                transform.rotate_arrays_about_point(arrays=translated_solar_2, angle=task.angles[1])
            )

            raw_solar_1 = distorted_solar_1 + dark_cal
            raw_solar_2 = distorted_solar_2 + dark_cal
            raw_solar = np.concatenate((raw_solar_1, raw_solar_2), axis=1)
            solar_hdul = generate_214_l0_fits_frame(data=raw_solar, s122_header=header)
            task.write(
                data=solar_hdul,
                tags=[
                    CryonirspTag.linearized_frame(
                        beam=beam, exposure_conditions=exposure_conditions
                    ),
                    CryonirspTag.task_solar_gain(),
                ],
                encoder=fits_hdulist_encoder,
            )

            yield task, data_shape_int
        finally:
            task._purge()


@pytest.fixture(scope="function")
def geometric_calibration_task_with_simple_raw_data(
    tmp_path, recipe_run_id, assign_input_dataset_doc_to_task, init_cryonirsp_constants_db
):
    number_of_modstates = 1
    number_of_beams = 2
    exposure_time = 20.0  # From CryonirspHeadersValidSolarGainFrames fixture
    exposure_conditions = ExposureConditions(
        exposure_time, AllowableOpticalDensityFilterNames.OPEN.value
    )
    data_shape_int = 100, 98
    data_shape_raw = 100, 196
    constants_db = CryonirspConstantsDb(
        NUM_MODSTATES=number_of_modstates,
        SOLAR_GAIN_EXPOSURE_CONDITIONS_LIST=(exposure_conditions,),
        ARM_ID="SP",
    )
    init_cryonirsp_constants_db(recipe_run_id, constants_db)
    with SPGeometricCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="sp_geometric_calibration",
        workflow_version="VX.Y",
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            param_class = cryonirsp_testing_parameters_factory(task)
            assign_input_dataset_doc_to_task(task, param_class())

            # Create the intermediate frames needed
            # Create a fake bad pixel map
            task.write(
                data=np.zeros(data_shape_raw),
                tags=[CryonirspTag.intermediate_frame(), CryonirspTag.task_bad_pixel_map()],
                encoder=fits_array_encoder,
            )
            for beam in range(1, number_of_beams + 1):
                dark_cal = np.ones(data_shape_int) * 3.0
                task.write(
                    data=dark_cal,
                    tags=[
                        CryonirspTag.intermediate_frame(
                            beam=beam, exposure_conditions=exposure_conditions
                        ),
                        CryonirspTag.task_dark(),
                    ],
                    encoder=fits_array_encoder,
                )

                # Need a lamp for each beam
                lamp_gain = np.ones(data_shape_int)
                task.write(
                    data=lamp_gain,
                    tags=[
                        CryonirspTag.intermediate_frame(
                            beam=beam, exposure_conditions=exposure_conditions
                        ),
                        CryonirspTag.task_lamp_gain(),
                    ],
                    encoder=fits_array_encoder,
                )

                # And a beam border intermediate array
                border = data_shape_raw[1] // 2
                task.write(
                    data=np.array(
                        [
                            0,
                            data_shape_int[0],
                            ((beam - 1) * border),
                            (border + (beam - 1) * border),
                        ]
                    ),
                    tags=[
                        CryonirspTag.intermediate_frame(beam=beam),
                        CryonirspTag.task_beam_boundaries(),
                    ],
                    encoder=fits_array_encoder,
                )

                # Let's write a dark with the wrong exposure time, just to make sure it doesn't get used
                task.write(
                    data=np.ones(data_shape_int) * 1e6,
                    tags=[
                        CryonirspTag.intermediate_frame(
                            beam=beam,
                            exposure_conditions=ExposureConditions(
                                exposure_time**2, AllowableOpticalDensityFilterNames.OPEN.value
                            ),
                        ),
                        CryonirspTag.task_dark(),
                    ],
                    encoder=fits_array_encoder,
                )

            # Create the raw data, which is based on two beams per frame
            beam1 = 1
            beam2 = 2
            dark_cal_two_beams = np.concatenate((dark_cal, dark_cal), axis=1)
            ds = CryonirspHeadersValidSPSolarGainFrames(
                dataset_shape=(1,) + data_shape_raw,
                array_shape=(1,) + data_shape_raw,
                time_delta=10,
            )
            header = ds.header()
            true_solar = np.ones(data_shape_raw)
            # Now add the beam number to each beam in the array
            true_solar[:, : data_shape_int[1]] += beam1
            true_solar[:, data_shape_int[1] :] += beam2
            raw_solar = true_solar + dark_cal_two_beams
            solar_hdul = generate_214_l0_fits_frame(data=raw_solar, s122_header=header)
            task.write(
                data=solar_hdul,
                tags=[
                    CryonirspTag.linearized_frame(exposure_conditions=exposure_conditions),
                    CryonirspTag.task_solar_gain(),
                ],
                encoder=fits_hdulist_encoder,
            )

            yield task, data_shape_int, true_solar
        finally:
            task._purge()


def test_geometric_task(geometric_calibration_task_that_completes, mocker, fake_gql_client):
    """
    Given: A set of raw solar gain images and necessary intermediate calibrations
    When: Running the geometric task
    Then: The damn thing runs and makes outputs that at least are the right type
    """
    # See the note in the fixture above: this test does NOT test for accuracy of the calibration
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task, beam_shape = geometric_calibration_task_that_completes
    task()
    for beam in range(1, task.constants.num_beams + 1):
        angle_array = next(
            task.read(
                tags=[
                    CryonirspTag.intermediate_frame(beam=beam),
                    CryonirspTag.task_geometric_angle(),
                ],
                decoder=cryo_fits_array_decoder,
            )
        )
        assert type(float(angle_array[0])) is float
        spec_shift_array = next(
            task.read(
                tags=[
                    CryonirspTag.intermediate_frame(beam=beam),
                    CryonirspTag.task_geometric_spectral_shifts(),
                ],
                decoder=cryo_fits_array_decoder,
            )
        )
        assert spec_shift_array.shape[0] == beam_shape[0]
        state_offset_array = next(
            task.read(
                tags=[
                    CryonirspTag.intermediate_frame(beam=beam),
                    CryonirspTag.task_geometric_offset(),
                ],
                decoder=cryo_fits_array_decoder,
            )
        )
        assert state_offset_array.shape == (2,)

    quality_files = task.read(tags=[CryonirspTag.quality("TASK_TYPES")])
    for file in quality_files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert data["total_frames"] == task.scratch.count_all(
                tags=[
                    CryonirspTag.linearized_frame(),
                    CryonirspTag.task_solar_gain(),
                ]
            )


def test_basic_corrections(geometric_calibration_task_with_simple_raw_data):
    """
    Given: A set of raw solar gain images and necessary intermediate calibrations
    When: Doing basic dark and lamp gain corrections
    Then: The corrections are applied correctly
    """
    task, beam_shape, true_solar = geometric_calibration_task_with_simple_raw_data
    flipped_true_solar = np.flip(true_solar, axis=1)
    task.do_basic_corrections()

    # Positive test on the flipped true solar image
    for beam in range(1, task.constants.num_beams + 1):
        if beam == 1:
            expected = flipped_true_solar[:, 0 : beam_shape[1]]
        else:
            expected = flipped_true_solar[:, beam_shape[1] :]
        array = task.basic_dark_bp_corrected_data(beam=beam)
        np.testing.assert_equal(expected, array)

    # Negative test on the original true solar image
    for beam in range(1, task.constants.num_beams + 1):
        if beam == 1:
            expected = true_solar[:, 0 : beam_shape[1]]
        else:
            expected = true_solar[:, beam_shape[1] :]
        array = task.basic_dark_bp_corrected_data(beam=beam)
        with pytest.raises(AssertionError):
            np.testing.assert_equal(expected, array)
