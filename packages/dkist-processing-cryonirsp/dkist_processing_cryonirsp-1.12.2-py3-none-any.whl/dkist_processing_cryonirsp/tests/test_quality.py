import json

import numpy as np
import pytest
from astropy.io import fits
from dkist_header_validator import spec122_validator
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.models.task_name import TaskName

from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.tasks.quality_metrics import CryonirspL0QualityMetrics
from dkist_processing_cryonirsp.tasks.quality_metrics import CryonirspL1QualityMetrics
from dkist_processing_cryonirsp.tests.conftest import CryonirspConstantsDb
from dkist_processing_cryonirsp.tests.conftest import generate_214_l1_fits_frame
from dkist_processing_cryonirsp.tests.header_models import Cryonirsp122ObserveFrames
from dkist_processing_cryonirsp.tests.header_models import CryonirspHeaders


@pytest.fixture
def cryonirsp_l0_quality_task(recipe_run_id, num_modstates, init_cryonirsp_constants_db, tmp_path):
    constants = CryonirspConstantsDb(
        NUM_MODSTATES=num_modstates,
        MODULATOR_SPIN_MODE="Stepped" if num_modstates > 1 else "Off",
    )
    init_cryonirsp_constants_db(recipe_run_id, constants)

    with CryonirspL0QualityMetrics(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)

        yield task
        task._purge()


@pytest.fixture()
def l0_quality_task_types() -> list[str]:
    # The tasks types we want to build l0 metrics for
    return [TaskName.lamp_gain.value, TaskName.dark.value]


@pytest.fixture()
def dataset_task_types(l0_quality_task_types) -> list[str]:
    # The task types that exist in the dataset. I.e., a larger set than we want to build metrics for.
    return l0_quality_task_types + [TaskName.solar_gain.value, TaskName.observe.value]


@pytest.fixture
def write_l0_task_frames_to_task(num_modstates, dataset_task_types):
    array_shape = (1, 4, 4)
    data = np.ones(array_shape)

    def writer(task):
        for task_type in dataset_task_types:
            ds = CryonirspHeaders(
                dataset_shape=(num_modstates,) + array_shape[-2:],
                array_shape=array_shape,
                time_delta=1.0,
                file_schema="level0_spec214",
            )
            for modstate, frame in enumerate(ds, start=1):
                header = frame.header()
                task.write(
                    data=data,
                    header=header,
                    tags=[
                        CryonirspTag.linearized_frame(),
                        CryonirspTag.task(task_type),
                        CryonirspTag.modstate(modstate),
                    ],
                    encoder=fits_array_encoder,
                )

    return writer


@pytest.fixture(scope="function")
def cryo_l1_quality_task(tmp_path, recipe_run_id, init_cryonirsp_constants_db):
    num_map_scans = 3
    num_scan_steps = 1
    constants_db = CryonirspConstantsDb(
        NUM_MAP_SCANS=num_map_scans,
        NUM_SCAN_STEPS=num_scan_steps,
    )
    init_cryonirsp_constants_db(recipe_run_id, constants_db)
    with CryonirspL1QualityMetrics(
        recipe_run_id=recipe_run_id, workflow_name="science_calibration", workflow_version="VX.Y"
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path)

        # Create fake stokes frames
        for map_scan in range(1, num_map_scans + 1):
            for scan_step in range(1, num_scan_steps + 1):
                for stokes_param, index in zip(("I", "Q", "U", "V"), (1, 2, 3, 4)):
                    ds = Cryonirsp122ObserveFrames(
                        array_shape=(1, 10, 10),
                        num_steps=num_scan_steps,
                        num_map_scans=num_map_scans,
                    )
                    header_generator = (
                        spec122_validator.validate_and_translate_to_214_l0(
                            d.header(), return_type=fits.HDUList
                        )[0].header
                        for d in ds
                    )

                    hdul = generate_214_l1_fits_frame(s122_header=next(header_generator))
                    hdul[1].header["DINDEX5"] = index
                    task.write(
                        data=hdul,
                        tags=[
                            CryonirspTag.calibrated(),
                            CryonirspTag.frame(),
                            CryonirspTag.stokes(stokes_param),
                            CryonirspTag.scan_step(scan_step),
                            CryonirspTag.map_scan(map_scan),
                            CryonirspTag.meas_num(1),
                        ],
                        encoder=fits_hdulist_encoder,
                    )

        yield task
        task._purge()


@pytest.mark.parametrize(
    "num_modstates", [pytest.param(4, id="polarimetric"), pytest.param(1, id="intensity")]
)
def test_l0_quality_task(
    cryonirsp_l0_quality_task, num_modstates, write_l0_task_frames_to_task, l0_quality_task_types
):
    """
    Given: A `CryonirspL0QualityMetrics` task and some INPUT frames tagged with their task type and modstate
    When: Running the task
    Then: The expected L0 quality metric files exist
    """
    # NOTE: We rely on the unit tests in `*-common` to verify the correct format/data of the metric files
    task = cryonirsp_l0_quality_task
    write_l0_task_frames_to_task(task)

    task()

    task_metric_names = ["FRAME_RMS", "FRAME_AVERAGE"]
    for metric_name in task_metric_names:
        for modstate in range(1, num_modstates + 1):
            for task_type in l0_quality_task_types:
                tags = [CryonirspTag.quality(metric_name), CryonirspTag.quality_task(task_type)]
                if num_modstates > 1:
                    tags.append(CryonirspTag.modstate(modstate))
                files = list(task.read(tags))
                assert len(files) == 1

    global_metric_names = ["DATASET_AVERAGE", "DATASET_RMS"]
    for metric_name in global_metric_names:
        files = list(task.read(tags=[CryonirspTag.quality(metric_name)]))
        assert len(files) > 0


def test_l1_quality_task(cryo_l1_quality_task, mocker, fake_gql_client):
    """
    Given: A CryonirspL1QualityMetrics task
    When: Calling the task instance
    Then: A single sensitivity measurement and datetime is recorded for each map scan for each Stokes Q, U, and V,
            and a single noise measurement and datetime is recorded for L1 file for each Stokes Q, U, and V
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    # When
    task = cryo_l1_quality_task
    task()
    # Then
    num_map_scans = task.constants.num_map_scans
    num_steps = task.constants.num_scan_steps
    sensitivity_files = list(task.read(tags=[CryonirspTag.quality("SENSITIVITY")]))
    assert len(sensitivity_files) == 4
    for file in sensitivity_files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            for time in data["x_values"]:
                assert isinstance(time, str)
            for sensitivity in data["y_values"]:
                assert isinstance(sensitivity, float)
            assert len(data["x_values"]) == len(data["y_values"]) == num_map_scans

    noise_files = list(task.read(tags=[CryonirspTag.quality("NOISE")]))
    assert len(noise_files) == 4
    for file in noise_files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            for time in data["x_values"]:
                assert isinstance(time, str)
            for noise in data["y_values"]:
                assert isinstance(noise, float)
            assert len(data["x_values"]) == len(data["y_values"]) == num_map_scans * num_steps
