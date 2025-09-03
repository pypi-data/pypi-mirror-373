import json
import re
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from typing import Callable
from typing import Type

import pytest
from astropy.io import fits
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.constants import BudName
from dkist_processing_common.tasks import WorkflowTaskBase

from dkist_processing_cryonirsp.models.constants import CryonirspBudName
from dkist_processing_cryonirsp.models.exposure_conditions import AllowableOpticalDensityFilterNames
from dkist_processing_cryonirsp.models.exposure_conditions import ExposureConditions
from dkist_processing_cryonirsp.models.parameters import CryonirspParsingParameters
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.parsers.polarimetric_check import PolarimetricCheckingUniqueBud
from dkist_processing_cryonirsp.tasks.parse import ParseL0CryonirspCILinearizedData
from dkist_processing_cryonirsp.tasks.parse import ParseL0CryonirspRampData
from dkist_processing_cryonirsp.tasks.parse import ParseL0CryonirspSPLinearizedData
from dkist_processing_cryonirsp.tests.conftest import _write_frames_to_task
from dkist_processing_cryonirsp.tests.conftest import cryonirsp_testing_parameters_factory
from dkist_processing_cryonirsp.tests.header_models import CryonirspHeaders
from dkist_processing_cryonirsp.tests.header_models import CryonirspHeadersValidNonLinearizedFrames
from dkist_processing_cryonirsp.tests.header_models import ModulatedDarkHeaders
from dkist_processing_cryonirsp.tests.header_models import ModulatedLampGainHeaders
from dkist_processing_cryonirsp.tests.header_models import ModulatedObserveHeaders
from dkist_processing_cryonirsp.tests.header_models import ModulatedPolcalHeaders
from dkist_processing_cryonirsp.tests.header_models import ModulatedSolarGainHeaders


def write_dark_frames_to_task(
    task: Type[WorkflowTaskBase],
    exposure_condition: ExposureConditions,
    array_shape=(2, 2, 1),
    tags: list[str] | None = None,
    num_modstates: int = 1,
):
    num_frames = 0
    for modstate in range(1, num_modstates + 1):
        frame_generator = ModulatedDarkHeaders(
            array_shape=array_shape,
            exposure_condition=exposure_condition,
            num_modstates=num_modstates,
            modstate=modstate,
        )
        num_frames += _write_frames_to_task(
            task=task, frame_generator=frame_generator, extra_tags=tags
        )

    return num_frames


def write_lamp_gain_frames_to_task(
    task: Type[WorkflowTaskBase],
    exposure_condition: ExposureConditions,
    array_shape=(2, 2, 1),
    tags: list[str] | None = None,
    tag_func: Callable[[CryonirspHeaders], list[str]] = lambda x: [],
    num_modstates: int = 1,
):
    num_frames = 0
    for modstate in range(1, num_modstates + 1):
        frame_generator = ModulatedLampGainHeaders(
            array_shape=array_shape,
            exposure_condition=exposure_condition,
            num_modstates=num_modstates,
            modstate=modstate,
        )

        num_frames += _write_frames_to_task(
            task=task,
            frame_generator=frame_generator,
            extra_tags=tags,
            tag_func=tag_func,
        )

    return num_frames


def write_solar_gain_frames_to_task(
    task: Type[WorkflowTaskBase],
    exposure_condition: ExposureConditions,
    array_shape=(2, 2, 1),
    tags: list[str] | None = None,
    num_modstates: int = 1,
    center_wavelength: float = 1080.0,
    slit_width: float = 52.0,
):
    num_frames = 0
    for modstate in range(1, num_modstates + 1):
        frame_generator = ModulatedSolarGainHeaders(
            array_shape=array_shape,
            exposure_condition=exposure_condition,
            num_modstates=num_modstates,
            modstate=modstate,
            center_wavelength=center_wavelength,
            slit_width=slit_width,
        )

        num_frames += _write_frames_to_task(
            task=task, frame_generator=frame_generator, extra_tags=tags
        )

    return num_frames


def write_polcal_frames_to_task(
    task: Type[WorkflowTaskBase],
    num_modstates: int,
    num_map_scans: int,
    extra_headers: dict,
    exposure_condition: ExposureConditions,
    array_shape=(2, 2, 1),
    tags: list[str] | None = None,
):
    num_frames = 0

    modstates = [0] if num_modstates == 0 else range(1, num_modstates + 1)

    for map_scan in range(1, num_map_scans + 1):
        for mod_state in modstates:
            frame_generator = ModulatedPolcalHeaders(
                num_modstates=num_modstates,
                modstate=mod_state,
                array_shape=array_shape,
                exposure_condition=exposure_condition,
                extra_headers={"PAC__006": "clear" if num_frames % 2 else "Cool retarder"}
                | extra_headers,
            )

            _write_frames_to_task(task=task, frame_generator=frame_generator, extra_tags=tags)
            num_frames += 1

    return num_frames


def write_observe_frames_to_task(
    task: Type[WorkflowTaskBase],
    num_modstates: int,
    num_scan_steps: int,
    num_map_scans: int,
    num_sub_repeats: int,
    num_measurements: int,
    arm_id: str,
    exposure_condition: ExposureConditions,
    change_translated_headers: Callable[[fits.Header | None], fits.Header] = lambda x: x,
    array_shape=(2, 2, 1),
    center_wavelength: float = 1080.0,
    slit_width: float = 52.0,
    tags: list[str] | None = None,
):
    num_frames = 0

    modstates = [0] if num_modstates == 0 else range(1, num_modstates + 1)

    start_time = datetime.now()
    frame_delta_time = timedelta(seconds=10)
    for map_scan in range(1, num_map_scans + 1):
        for scan_step in range(1, num_scan_steps + 1):
            for measurement in range(1, num_measurements + 1):
                for mod_state in modstates:
                    for repeat in range(1, num_sub_repeats + 1):
                        frame_generator = ModulatedObserveHeaders(
                            start_date=start_time.isoformat(),
                            num_modstates=num_modstates,
                            modstate=mod_state,
                            num_map_scans=num_map_scans,
                            map_scan=map_scan,
                            num_sub_repeats=num_sub_repeats,
                            sub_repeat_num=repeat,
                            array_shape=array_shape,
                            exposure_condition=exposure_condition,
                            num_scan_steps=num_scan_steps,
                            scan_step=scan_step,
                            num_meas=num_measurements,
                            meas_num=measurement,
                            arm_id=arm_id,
                            center_wavelength=center_wavelength,
                            slit_width=slit_width,
                        )
                        start_time += frame_delta_time

                        _write_frames_to_task(
                            task=task,
                            frame_generator=frame_generator,
                            extra_tags=tags,
                            change_translated_headers=change_translated_headers,
                        )

                        num_frames += 1

    return num_frames


def write_non_linearized_frames(
    task: Type[WorkflowTaskBase],
    arm_id: str,
    start_time: str,
    camera_readout_mode: str,
    change_translated_headers: Callable[[fits.Header | None], fits.Header] = lambda x: x,
    tags: list[str] | None = None,
):
    frame_generator = CryonirspHeadersValidNonLinearizedFrames(
        arm_id=arm_id,
        camera_readout_mode=camera_readout_mode,
        dataset_shape=(2, 2, 2),
        array_shape=(1, 2, 2),
        time_delta=10,
        roi_x_origin=0,
        roi_y_origin=0,
        roi_x_size=2,
        roi_y_size=2,
        date_obs=start_time,
        exposure_time=0.01,
    )

    def tag_ramp_frames(translated_header):
        ramp_tags = [
            CryonirspTag.curr_frame_in_ramp(translated_header["CNCNDR"]),
        ]

        return ramp_tags

    for frame in frame_generator:
        _write_frames_to_task(
            task=task,
            frame_generator=frame,
            change_translated_headers=change_translated_headers,
            extra_tags=tags,
            tag_ramp_frames=tag_ramp_frames,
        )


def make_linearized_test_frames(
    task,
    arm_id: str,
    dark_exposure_conditions: list[ExposureConditions],
    num_modstates: int,
    num_scan_steps: int,
    change_translated_headers: Callable[[fits.Header | None], fits.Header] = lambda x: x,
    lamp_exposure_condition: ExposureConditions = ExposureConditions(
        10.0, AllowableOpticalDensityFilterNames.OPEN.value
    ),
    solar_exposure_condition: ExposureConditions = ExposureConditions(
        5.0, AllowableOpticalDensityFilterNames.OPEN.value
    ),
    polcal_exposure_condition: ExposureConditions = ExposureConditions(
        7.0, AllowableOpticalDensityFilterNames.OPEN.value
    ),
    observe_exposure_condition: ExposureConditions = ExposureConditions(
        6.0, AllowableOpticalDensityFilterNames.OPEN.value
    ),
    num_map_scans: int = 1,
    num_sub_repeats: int = 1,
    num_measurements: int = 1,
    center_wavelength: float = 1080.0,
    slit_width: float = 52.0,
    extra_headers: dict | None = None,
):
    if extra_headers is None:
        extra_headers = dict()
    num_dark = 0
    num_polcal = 0
    num_obs = 0
    lin_tag = [CryonirspTag.linearized()]

    for condition in dark_exposure_conditions:
        num_dark += write_dark_frames_to_task(
            task,
            exposure_condition=condition,
            tags=lin_tag,
            num_modstates=num_modstates or 1,  # We *always* need dark frames
        )

    num_lamp = write_lamp_gain_frames_to_task(
        task,
        tags=lin_tag,
        exposure_condition=lamp_exposure_condition,
        num_modstates=num_modstates or 1,  # We *always* need lamp frames
    )
    num_solar = write_solar_gain_frames_to_task(
        task,
        tags=lin_tag,
        exposure_condition=solar_exposure_condition,
        num_modstates=num_modstates or 1,  # We *always* need solar frames
        center_wavelength=center_wavelength,
        slit_width=slit_width,
    )

    num_polcal += write_polcal_frames_to_task(
        task,
        num_modstates=num_modstates,
        num_map_scans=num_map_scans,
        tags=lin_tag,
        extra_headers=extra_headers,
        exposure_condition=polcal_exposure_condition,
    )
    num_obs += write_observe_frames_to_task(
        task,
        arm_id=arm_id,
        num_scan_steps=num_scan_steps,
        num_map_scans=num_map_scans,
        num_sub_repeats=num_sub_repeats,
        num_modstates=num_modstates,
        exposure_condition=observe_exposure_condition,
        num_measurements=num_measurements,
        tags=lin_tag,
        change_translated_headers=change_translated_headers,
        center_wavelength=center_wavelength,
        slit_width=slit_width,
    )

    return num_dark, num_lamp, num_solar, num_polcal, num_obs


def make_non_linearized_test_frames(
    task,
    change_translated_headers: Callable[[fits.Header | None], fits.Header] = lambda x: x,
):
    arm_id = "SP"
    camera_readout_mode = "FastUpTheRamp"

    start_time = datetime(1946, 11, 20).isoformat("T")

    extra_tags = [
        CryonirspTag.input(),
        # All frames in a ramp have the same date-obs
        CryonirspTag.time_obs(str(start_time)),
    ]

    write_non_linearized_frames(
        task,
        start_time=start_time,
        arm_id=arm_id,
        camera_readout_mode=camera_readout_mode,
        tags=extra_tags,
        change_translated_headers=change_translated_headers,
    )


@pytest.fixture
def parse_linearized_task(
    tmp_path, recipe_run_id, assign_input_dataset_doc_to_task, mocker, fake_gql_client, arm_id
):
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    if arm_id == "CI":
        parsing_class = ParseL0CryonirspCILinearizedData
    if arm_id == "SP":
        parsing_class = ParseL0CryonirspSPLinearizedData
    with parsing_class(
        recipe_run_id=recipe_run_id,
        workflow_name="parse_cryonirsp_input_data",
        workflow_version="VX.Y",
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            param_dataclass = cryonirsp_testing_parameters_factory(task)
            assign_input_dataset_doc_to_task(
                task,
                param_dataclass(),
                parameter_class=CryonirspParsingParameters,
                obs_ip_start_time=None,
            )
            yield task
        finally:
            task._purge()


@pytest.fixture
def parse_non_linearized_task(tmp_path, recipe_run_id, mocker, fake_gql_client):
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    with ParseL0CryonirspRampData(
        recipe_run_id=recipe_run_id,
        workflow_name="parse_cryonirsp_input_data",
        workflow_version="VX.Y",
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            yield task
        finally:
            task._purge()


def test_parse_cryonirsp_non_linearized_data(parse_non_linearized_task):
    """
    Given: A ParseCryonirspRampData task
    When: Calling the task instance
    Then: All tagged files exist and individual task tags are applied
    """

    task = parse_non_linearized_task
    make_non_linearized_test_frames(task)

    task()

    filepaths = list(task.read(tags=[CryonirspTag.input(), CryonirspTag.frame()]))
    cncndr_list = []
    for i, filepath in enumerate(filepaths):
        assert filepath.exists()
        hdul = fits.open(filepath)
        cncndr_list.append(hdul[0].header["CNCNDR"])
    assert len(filepaths) == 2
    assert sorted(cncndr_list) == [1, 2]
    assert task.constants._db_dict[CryonirspBudName.camera_readout_mode.value] == "FastUpTheRamp"
    assert task.constants._db_dict[CryonirspBudName.arm_id.value] == "SP"
    assert len(task.constants._db_dict[CryonirspBudName.time_obs_list]) == 1
    assert task.constants._db_dict[CryonirspBudName.wavelength.value] == 1083.0
    assert task.constants._db_dict[CryonirspBudName.time_obs_list][0] == datetime(
        1946, 11, 20
    ).isoformat("T")
    assert task.constants._db_dict[BudName.obs_ip_start_time.value] == "1999-12-31T23:59:59"


def test_parse_cryonirsp_non_linearized_data_bad_filter_name(parse_non_linearized_task):
    """
    Given: A ParseCryonirspRampData task with a bad filter name in the headers
    When: Calling the task instance
    Then: The task fails with a ValueError exception
    """

    task = parse_non_linearized_task

    def insert_bad_filter_name_into_header(translated_header: fits.Header):
        translated_header["CNFILTNP"] = "BAD_FILTER_NAME"
        return translated_header

    make_non_linearized_test_frames(
        task, change_translated_headers=insert_bad_filter_name_into_header
    )

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Unknown Optical Density Filter Name(s): bad_filter_names = {'BAD_FILTER_NAME'}"
        ),
    ):
        task()


@pytest.mark.parametrize("number_of_modstates", [0, 1, 8])
@pytest.mark.parametrize("arm_id", ["CI", "SP"])
def test_parse_cryonirsp_linearized_data(parse_linearized_task, arm_id, number_of_modstates):
    """
    Given: A ParseCryonirspInputData task
    When: Calling the task instance
    Then: All tagged files exist and individual task tags are applied
    """

    task = parse_linearized_task

    lamp_exp_cond = ExposureConditions(10.0, AllowableOpticalDensityFilterNames.OPEN.value)
    solar_exp_cond = ExposureConditions(5.0, AllowableOpticalDensityFilterNames.OPEN.value)
    obs_exp_cond = ExposureConditions(6.0, AllowableOpticalDensityFilterNames.OPEN.value)
    polcal_exp_cond = ExposureConditions(7.0, AllowableOpticalDensityFilterNames.OPEN.value)
    dark_exp_conditions = [
        lamp_exp_cond,
        solar_exp_cond,
        obs_exp_cond,
        polcal_exp_cond,
    ]

    num_dark, num_lamp, num_solar, num_polcal, num_obs = make_linearized_test_frames(
        task,
        arm_id,
        dark_exposure_conditions=dark_exp_conditions,
        num_modstates=number_of_modstates,
        num_scan_steps=3,
        num_map_scans=1,
        num_sub_repeats=1,
        lamp_exposure_condition=lamp_exp_cond,
        solar_exposure_condition=solar_exp_cond,
        observe_exposure_condition=obs_exp_cond,
        polcal_exposure_condition=polcal_exp_cond,
    )

    task()
    num_actual_modstates = number_of_modstates or 1
    for modstate in range(1, num_actual_modstates + 1):
        assert (
            len(
                list(
                    task.read(
                        tags=[
                            CryonirspTag.linearized(),
                            CryonirspTag.task_dark(),
                            CryonirspTag.modstate(modstate),
                        ]
                    )
                )
            )
            == num_dark / num_actual_modstates
        )

        assert (
            len(
                list(
                    task.read(
                        tags=[
                            CryonirspTag.linearized(),
                            CryonirspTag.task_lamp_gain(),
                            CryonirspTag.modstate(modstate),
                        ]
                    )
                )
            )
            == num_lamp / num_actual_modstates
        )

        assert (
            len(
                list(
                    task.read(
                        tags=[
                            CryonirspTag.linearized(),
                            CryonirspTag.task_solar_gain(),
                            CryonirspTag.modstate(modstate),
                        ]
                    )
                )
            )
            == num_solar / num_actual_modstates
        )

        assert (
            len(
                list(
                    task.read(
                        tags=[
                            CryonirspTag.linearized(),
                            CryonirspTag.task_polcal(),
                            CryonirspTag.modstate(modstate),
                        ]
                    )
                )
            )
            == num_polcal / num_actual_modstates
        )

        assert (
            len(
                list(
                    task.read(
                        tags=[
                            CryonirspTag.linearized(),
                            CryonirspTag.task_observe(),
                            CryonirspTag.modstate(modstate),
                        ]
                    )
                )
            )
            == num_obs / num_actual_modstates
        )


@pytest.mark.parametrize("arm_id", ["CI", "SP"])
def test_parse_cryonirsp_linearized_data_mismatched_darks(parse_linearized_task, arm_id):
    """
    Given: A parse task with dark data that have mismatched exposure times
    When: Calling the Parse task
    Then: Raise the correct error
    """

    task = parse_linearized_task

    lamp_exp_cond = ExposureConditions(10.0, AllowableOpticalDensityFilterNames.OPEN.value)
    solar_exp_cond = ExposureConditions(5.0, AllowableOpticalDensityFilterNames.OPEN.value)
    obs_exp_cond = ExposureConditions(6.0, AllowableOpticalDensityFilterNames.OPEN.value)
    polcal_exp_cond = ExposureConditions(7.0, AllowableOpticalDensityFilterNames.OPEN.value)

    # Make all of them differ by only one aspect of the exposure condition
    dark_exp_conditions = [
        ExposureConditions(11.0, AllowableOpticalDensityFilterNames.OPEN.value),
        ExposureConditions(5.0, AllowableOpticalDensityFilterNames.NONE.value),
        ExposureConditions(7.0, AllowableOpticalDensityFilterNames.G278.value),
    ]

    make_linearized_test_frames(
        task,
        arm_id,
        dark_exposure_conditions=dark_exp_conditions,
        num_modstates=8,
        num_scan_steps=3,
        num_map_scans=2,
        num_sub_repeats=1,
        lamp_exposure_condition=lamp_exp_cond,
        solar_exposure_condition=solar_exp_cond,
        polcal_exposure_condition=polcal_exp_cond,
        observe_exposure_condition=obs_exp_cond,
    )

    with pytest.raises(
        ValueError, match="Exposure conditions required in the set of dark frames not found.*"
    ):
        task()


@pytest.mark.parametrize("arm_id", ["CI", "SP"])
def test_parse_cryonirsp_linearized_data_multi_num_scan_steps(parse_linearized_task, arm_id):
    """
    Given: A parse task with data that has muliple num_scan_step values
    When: Calling the Parse task
    Then: Raise the correct error
    """

    task = parse_linearized_task

    lamp_exp_cond = ExposureConditions(10.0, AllowableOpticalDensityFilterNames.OPEN.value)
    solar_exp_cond = ExposureConditions(5.0, AllowableOpticalDensityFilterNames.OPEN.value)
    obs_exp_cond = ExposureConditions(6.0, AllowableOpticalDensityFilterNames.OPEN.value)
    polcal_exp_cond = ExposureConditions(7.0, AllowableOpticalDensityFilterNames.OPEN.value)
    dark_exp_conditions = [
        lamp_exp_cond,
        solar_exp_cond,
        obs_exp_cond,
        polcal_exp_cond,
    ]

    def make_multi_num_scans(translated_header: fits.Header):
        translated_header["CNNUMSCN"] = translated_header["CNCURSCN"] % 3
        return translated_header

    make_linearized_test_frames(
        task,
        arm_id,
        dark_exposure_conditions=dark_exp_conditions,
        num_modstates=8,
        num_scan_steps=4,
        num_map_scans=4,
        num_sub_repeats=2,
        change_translated_headers=make_multi_num_scans,
        lamp_exposure_condition=lamp_exp_cond,
        solar_exposure_condition=solar_exp_cond,
        polcal_exposure_condition=polcal_exp_cond,
        observe_exposure_condition=obs_exp_cond,
    )

    with pytest.raises(ValueError, match="Multiple NUM_SCAN_STEPS values found.*"):
        task()


@pytest.mark.parametrize("arm_id", ["CI", "SP"])
@pytest.mark.parametrize(
    "abort_loop_name",
    [
        pytest.param("scan_step", id="Missing_step"),
        pytest.param("measurement", id="Missing_measurement"),
        pytest.param("modstate", id="Missing_modstate"),
        pytest.param("sub_repeat", id="Missing_sub_repeat"),
    ],
)
def test_parse_cryonirsp_linearized_incomplete_final_map(
    parse_linearized_task, arm_id, abort_loop_name
):
    """
    Given: A parse task with data that has complete raster scans along with an incomplete raster scan
    When: Calling the Parse task
    Then: The correct number of scan steps and maps are found
    """

    task = parse_linearized_task

    exp_cond = ExposureConditions(6.0, AllowableOpticalDensityFilterNames.OPEN.value)
    lin_tag = [CryonirspTag.linearized()]

    num_map_scans = 3
    num_scan_steps = 3
    num_measurements = 2
    num_modstates = 2
    num_sub_repeats = 2

    # Needed so the picky buds are happy
    write_dark_frames_to_task(task, exposure_condition=exp_cond, tags=lin_tag)
    write_solar_gain_frames_to_task(task, exposure_condition=exp_cond, tags=lin_tag)
    if arm_id == "SP":
        write_lamp_gain_frames_to_task(task, exposure_condition=exp_cond, tags=lin_tag)

    # Needed so the pol checking buds are happy
    write_polcal_frames_to_task(
        task,
        num_modstates=num_modstates,
        num_map_scans=num_map_scans,
        tags=lin_tag,
        extra_headers=dict(),
        exposure_condition=exp_cond,
    )

    # Make all test frames except for last map scan
    write_observe_frames_to_task(
        task,
        arm_id=arm_id,
        num_scan_steps=num_scan_steps,
        num_map_scans=num_map_scans - 1,
        num_sub_repeats=num_sub_repeats,
        num_modstates=num_modstates,
        num_measurements=num_measurements,
        tags=lin_tag,
        exposure_condition=exp_cond,
    )

    # Make incomplete final map scan. The "abort_loop_name" sets the level of the instrument loop that has the abort.
    final_map_scan_number = num_map_scans
    aborted = False
    for scan_step in range(1, num_scan_steps + 1):
        if aborted or (abort_loop_name == "scan_step" and scan_step == num_scan_steps):
            aborted = True
            break

        for measurement in range(1, num_measurements + 1):
            if aborted or (abort_loop_name == "measurement" and measurement == num_measurements):
                aborted = True
                break

            for mod_state in range(1, num_modstates + 1):
                if aborted or (abort_loop_name == "modstate" and mod_state == num_modstates):
                    aborted = True
                    break

                for repeat in range(1, num_sub_repeats + 1):
                    if aborted or (abort_loop_name == "sub_repeat" and repeat == num_sub_repeats):
                        aborted = True
                        break

                    frame_generator = ModulatedObserveHeaders(
                        num_modstates=num_modstates,
                        modstate=mod_state,
                        num_map_scans=num_map_scans,
                        map_scan=final_map_scan_number,
                        num_sub_repeats=num_sub_repeats,
                        sub_repeat_num=repeat,
                        array_shape=(1, 2, 2),
                        exposure_condition=exp_cond,
                        num_scan_steps=num_scan_steps,
                        scan_step=scan_step,
                        num_meas=num_measurements,
                        meas_num=measurement,
                        arm_id=arm_id,
                    )

                    _write_frames_to_task(
                        task=task,
                        frame_generator=frame_generator,
                        extra_tags=[CryonirspTag.linearized()],
                    )

    task()
    assert task.constants._db_dict[CryonirspBudName.num_scan_steps.value] == num_scan_steps
    assert task.constants._db_dict[CryonirspBudName.num_map_scans.value] == num_map_scans - 1


@pytest.mark.parametrize("arm_id", ["CI", "SP"])
@pytest.mark.parametrize(
    "abort_loop_name",
    [
        pytest.param("scan_step", id="Missing_step"),
        pytest.param("measurement", id="Missing_measurement"),
        pytest.param("modstate", id="Missing_modstate"),
        pytest.param("sub_repeat", id="Missing_sub_repeat"),
    ],
)
def test_parse_cryonirsp_linearized_incomplete_final_map_error(
    parse_linearized_task, arm_id, abort_loop_name
):
    """
    Given: A parse task with data that containing multiple aborted maps
    When: Calling the Parse task
    Then: The correct Error is raised
    """

    task = parse_linearized_task

    exp_cond = ExposureConditions(4.0, AllowableOpticalDensityFilterNames.OPEN.value)
    lin_tag = [CryonirspTag.linearized()]

    num_map_scans = 3
    num_scan_steps = 3
    num_measurements = 2
    num_modstates = 2
    num_sub_repeats = 2

    # Needed so the pol checking buds are happy
    write_polcal_frames_to_task(
        task,
        num_modstates=num_modstates,
        num_map_scans=num_map_scans,
        tags=lin_tag,
        extra_headers=dict(),
        exposure_condition=exp_cond,
    )

    # Make one complete map
    write_observe_frames_to_task(
        task,
        arm_id=arm_id,
        num_scan_steps=1,
        num_map_scans=num_map_scans,
        num_sub_repeats=num_sub_repeats,
        num_modstates=num_modstates,
        num_measurements=num_measurements,
        tags=lin_tag,
        exposure_condition=exp_cond,
    )

    # Make 2 incomplete maps. The "abort_loop_name" sets the level of the instrument loop that has the abort.
    final_map_scan_number = num_map_scans
    for map_scan in range(2, num_map_scans + 1):
        aborted = False
        for scan_step in range(1, num_scan_steps + 1):
            if aborted or (abort_loop_name == "scan_step" and scan_step == num_scan_steps):
                aborted = True
                break

            for measurement in range(1, num_measurements + 1):
                if aborted or (
                    abort_loop_name == "measurement" and measurement == num_measurements
                ):
                    aborted = True
                    break

                for mod_state in range(1, num_modstates + 1):
                    if aborted or (abort_loop_name == "modstate" and mod_state == num_modstates):
                        aborted = True
                        break

                    for repeat in range(1, num_sub_repeats + 1):
                        if aborted or (
                            abort_loop_name == "sub_repeat" and repeat == num_sub_repeats
                        ):
                            aborted = True
                            break

                        frame_generator = ModulatedObserveHeaders(
                            num_modstates=num_modstates,
                            modstate=mod_state,
                            num_map_scans=num_map_scans,
                            map_scan=final_map_scan_number,
                            num_sub_repeats=num_sub_repeats,
                            sub_repeat_num=repeat,
                            array_shape=(1, 2, 2),
                            exposure_condition=exp_cond,
                            num_scan_steps=num_scan_steps,
                            scan_step=scan_step,
                            num_meas=num_measurements,
                            meas_num=measurement,
                            arm_id=arm_id,
                        )

                        _write_frames_to_task(
                            task=task,
                            frame_generator=frame_generator,
                            extra_tags=[CryonirspTag.linearized()],
                        )

    with pytest.raises(ValueError, match="More than one incomplete map exists in the data."):
        task()


@pytest.mark.parametrize("arm_id", ["CI", "SP"])
@pytest.mark.parametrize(
    "abort_loop_name",
    [
        pytest.param("scan_step", id="Missing_step"),
        pytest.param("measurement", id="Missing_measurement"),
        pytest.param("modstate", id="Missing_modstate"),
        pytest.param("sub_repeat", id="Missing_sub_repeat"),
    ],
)
def test_parse_cryonirsp_linearized_incomplete_raster_scan(
    parse_linearized_task, arm_id, abort_loop_name
):
    """
    Given: A parse task with data that has an incomplete raster scan
    When: Calling the parse task
    Then: The correct number of scan steps and maps are found
    """

    task = parse_linearized_task

    exp_cond = ExposureConditions(6.0, AllowableOpticalDensityFilterNames.OPEN.value)
    lin_tag = [CryonirspTag.linearized()]

    num_scan_steps = 4
    num_map_scans = 1
    num_scan_steps = 3
    num_measurements = 2
    num_modstates = 2
    num_sub_repeats = 2

    # Needed so the frames from the complete and incomplete maps have the same value for
    # CNNUMSCN (the number of scan steps)
    def set_constant_num_scan_steps(translated_header):
        translated_header["CNNUMSCN"] = num_scan_steps
        return translated_header

    # Needed so the picky buds are happy
    write_dark_frames_to_task(task, exposure_condition=exp_cond, tags=lin_tag)
    write_solar_gain_frames_to_task(task, exposure_condition=exp_cond, tags=lin_tag)
    if arm_id == "SP":
        write_lamp_gain_frames_to_task(task, exposure_condition=exp_cond, tags=lin_tag)

    # Needed so the pol checking buds are happy
    write_polcal_frames_to_task(
        task,
        num_modstates=num_modstates,
        num_map_scans=num_map_scans,
        tags=lin_tag,
        extra_headers=dict(),
        exposure_condition=exp_cond,
    )

    # Make all the complete scan steps
    write_observe_frames_to_task(
        task,
        arm_id=arm_id,
        num_scan_steps=num_scan_steps - 1,
        num_map_scans=num_map_scans,
        num_sub_repeats=num_sub_repeats,
        num_modstates=num_modstates,
        num_measurements=num_measurements,
        tags=lin_tag,
        exposure_condition=exp_cond,
        change_translated_headers=set_constant_num_scan_steps,
    )

    # Now make the final scan step, which will be aborted at various points
    final_scan_step_number = num_scan_steps

    # If abort_loop_name == "scan_step" then don't make *any* files for the last step
    if abort_loop_name != "scan_step":
        aborted = False
        for measurement in range(1, num_measurements + 1):
            if aborted or (abort_loop_name == "measurement" and measurement == num_measurements):
                aborted = True
                break

            for mod_state in range(1, num_modstates + 1):
                if aborted or (abort_loop_name == "modstate" and mod_state == num_modstates):
                    aborted = True
                    break

                for repeat in range(1, num_sub_repeats + 1):
                    if aborted or (abort_loop_name == "sub_repeat" and repeat == num_sub_repeats):
                        aborted = True
                        break

                    frame_generator = ModulatedObserveHeaders(
                        num_modstates=num_modstates,
                        modstate=mod_state,
                        num_map_scans=num_map_scans,
                        map_scan=1,
                        num_sub_repeats=num_sub_repeats,
                        sub_repeat_num=repeat,
                        array_shape=(1, 2, 2),
                        exposure_condition=exp_cond,
                        num_scan_steps=num_scan_steps,
                        scan_step=final_scan_step_number,
                        num_meas=num_measurements,
                        meas_num=measurement,
                        arm_id=arm_id,
                    )

                    _write_frames_to_task(
                        task=task,
                        frame_generator=frame_generator,
                        extra_tags=[CryonirspTag.linearized()],
                    )

    task()

    assert task.constants._db_dict[CryonirspBudName.num_scan_steps.value] == num_scan_steps - 1
    assert task.constants._db_dict[CryonirspBudName.num_map_scans.value] == num_map_scans
    assert task.constants._db_dict[CryonirspBudName.num_meas.value] == 2


@pytest.mark.parametrize("arm_id", ["CI", "SP"])
@pytest.mark.parametrize(
    "abort_loop_name",
    [
        pytest.param("scan_step", id="Missing_step"),
        pytest.param("measurement", id="Missing_measurement"),
        pytest.param("modstate", id="Missing_modstate"),
        pytest.param("sub_repeat", id="Missing_sub_repeat"),
    ],
)
def test_parse_cryonirsp_linearized_incomplete_raster_scan_error(
    parse_linearized_task, arm_id, abort_loop_name
):
    """
    Given: A parse task with data representing a single map scan that was aborted and then continued
    When: Calling the parse task
    Then: The correct Error is raised
    """
    task = parse_linearized_task

    num_map_scans = 1
    num_scan_steps = 3
    num_measurements = 2
    num_modstates = 2
    num_sub_repeats = 2

    lin_tag = [CryonirspTag.linearized()]
    exp_cond = ExposureConditions(6.0, AllowableOpticalDensityFilterNames.OPEN.value)

    # Needed so the frames from the complete and incomplete maps have the same value for
    # CNNUMSCN (the number of scan steps)
    def set_constant_num_scan_steps(translated_header):
        translated_header["CNNUMSCN"] = num_scan_steps
        return translated_header

    # Needed so the dark picky bud is happy
    write_dark_frames_to_task(task, exposure_condition=exp_cond, tags=lin_tag)

    # Needed so the pol checking buds are happy
    write_polcal_frames_to_task(
        task,
        num_modstates=num_modstates,
        num_map_scans=num_map_scans,
        tags=lin_tag,
        extra_headers=dict(),
        exposure_condition=exp_cond,
    )

    # Make the first complete scan step
    write_observe_frames_to_task(
        task,
        arm_id=arm_id,
        num_scan_steps=1,
        num_map_scans=num_map_scans,
        num_sub_repeats=num_sub_repeats,
        num_modstates=num_modstates,
        num_measurements=num_measurements,
        tags=lin_tag,
        exposure_condition=exp_cond,
        change_translated_headers=set_constant_num_scan_steps,
    )

    def set_last_scan_step(translated_header):
        translated_header["CNNUMSCN"] = num_scan_steps
        translated_header["CNCURSCN"] = 4
        return translated_header

    # Make the final complete scan step
    write_observe_frames_to_task(
        task,
        arm_id=arm_id,
        num_scan_steps=1,
        num_map_scans=num_map_scans,
        num_sub_repeats=num_sub_repeats,
        num_modstates=num_modstates,
        num_measurements=num_measurements,
        tags=lin_tag,
        exposure_condition=exp_cond,
        change_translated_headers=set_last_scan_step,
    )

    # Now make 2 scan steps that are aborted at various points
    for scan_step in [2, 3]:  # Abort the middle 2 scan steps
        aborted = False

        # If we're aborting at the "scan_step" level we don't need any frames at all
        if abort_loop_name != "scan_step":
            for measurement in range(1, num_measurements + 1):
                if aborted or (
                    abort_loop_name == "measurement" and measurement == num_measurements
                ):
                    aborted = True
                    break

                for mod_state in range(1, num_modstates + 1):
                    if aborted or (abort_loop_name == "modstate" and mod_state == num_modstates):
                        aborted = True
                        break

                    for repeat in range(1, num_sub_repeats + 1):
                        if aborted or (
                            abort_loop_name == "sub_repeat" and repeat == num_sub_repeats
                        ):
                            aborted = True
                            break

                        frame_generator = ModulatedObserveHeaders(
                            num_modstates=num_modstates,
                            modstate=mod_state,
                            num_map_scans=num_map_scans,
                            map_scan=1,
                            num_sub_repeats=num_sub_repeats,
                            sub_repeat_num=repeat,
                            array_shape=(1, 2, 2),
                            exposure_condition=exp_cond,
                            num_scan_steps=num_scan_steps,
                            scan_step=scan_step,
                            num_meas=num_measurements,
                            meas_num=measurement,
                            arm_id=arm_id,
                        )

                        _write_frames_to_task(
                            task=task,
                            frame_generator=frame_generator,
                            extra_tags=[CryonirspTag.linearized()],
                        )

    # We aborted steps 2 and 3 so [1, 4] is the expected sequence of complete steps
    with pytest.raises(
        ValueError, match=re.escape("Not all sequential steps could be found. Found [1, 4]")
    ):
        task()


@pytest.mark.parametrize("arm_id", ["CI", "SP"])
def test_parse_cryonirsp_linearized_polcal_task_types(parse_linearized_task, arm_id):
    """
    Given: A Parse task with associated polcal files that include polcal gain and dark
    When: Tagging the task of each file
    Then: Polcal gain and darks are identified and tagged correctly
    """

    task = parse_linearized_task

    lamp_exp_cond = ExposureConditions(10.0, AllowableOpticalDensityFilterNames.OPEN.value)
    solar_exp_cond = ExposureConditions(5.0, AllowableOpticalDensityFilterNames.OPEN.value)
    obs_exp_cond = ExposureConditions(6.0, AllowableOpticalDensityFilterNames.OPEN.value)
    polcal_exp_cond = ExposureConditions(7.0, AllowableOpticalDensityFilterNames.OPEN.value)
    dark_exp_conditions = [
        lamp_exp_cond,
        solar_exp_cond,
        obs_exp_cond,
        polcal_exp_cond,
    ]

    num_scan_steps = 0
    num_map_scans = 7
    num_modstates = 8
    num_sub_repeats = 1

    polcal_dark_headers = {"PAC__008": "DarkShutter", "PAC__006": "clear", "PAC__004": "clear"}
    polcal_gain_headers = {"PAC__008": "FieldStopFoo", "PAC__006": "clear", "PAC__004": "clear"}
    polcal_data_headers = {
        "PAC__008": "FieldStopFoo",
        "PAC__006": "SiO2 SAR",
        "PAC__004": "Sapphire Polarizer",
    }

    extra_headers = [polcal_dark_headers, polcal_gain_headers, polcal_data_headers]

    for headers in extra_headers:
        make_linearized_test_frames(
            task,
            arm_id,
            dark_exposure_conditions=dark_exp_conditions,
            num_modstates=num_modstates,
            num_scan_steps=num_scan_steps,
            num_map_scans=num_map_scans,
            num_sub_repeats=num_sub_repeats,
            extra_headers=headers,
            lamp_exposure_condition=lamp_exp_cond,
            solar_exposure_condition=solar_exp_cond,
            polcal_exposure_condition=polcal_exp_cond,
            observe_exposure_condition=obs_exp_cond,
        )

    task()

    assert (
        task.scratch.count_all(tags=[CryonirspTag.task("POLCAL_DARK")])
        == num_map_scans * num_modstates
    )
    assert (
        task.scratch.count_all(tags=[CryonirspTag.task("POLCAL_GAIN")])
        == num_map_scans * num_modstates
    )
    assert (
        task.scratch.count_all(tags=[CryonirspTag.task("POLCAL")])
        == (num_map_scans * num_modstates) * 3
    )


@pytest.mark.parametrize("number_of_modulator_states", [0, 1, 8])
@pytest.mark.parametrize("arm_id", ["CI", "SP"])
def test_parse_cryonirsp_linearized_data_constants(
    parse_linearized_task, arm_id, number_of_modulator_states
):
    """
    Given: A ParseCryonirspInputData task
    When: Calling the task instance
    Then: Constants are in the constants object as expected
    """

    task = parse_linearized_task

    lamp_exp_cond = ExposureConditions(10.0, AllowableOpticalDensityFilterNames.OPEN.value)
    solar_exp_cond = ExposureConditions(5.0, AllowableOpticalDensityFilterNames.OPEN.value)
    obs_exp_cond = ExposureConditions(6.0, AllowableOpticalDensityFilterNames.OPEN.value)
    polcal_exp_cond = ExposureConditions(7.0, AllowableOpticalDensityFilterNames.OPEN.value)
    dark_exp_conditions = [
        lamp_exp_cond,
        solar_exp_cond,
        obs_exp_cond,
        polcal_exp_cond,
    ]

    num_modstates = number_of_modulator_states
    num_scan_steps = 3
    num_map_scans = 2
    num_sub_repeats = 2
    center_wavelength = 1234.0
    slit_width = 6.28

    make_linearized_test_frames(
        task,
        arm_id,
        dark_exposure_conditions=dark_exp_conditions,
        num_modstates=num_modstates,
        num_scan_steps=num_scan_steps,
        num_map_scans=num_map_scans,
        num_sub_repeats=num_sub_repeats,
        lamp_exposure_condition=lamp_exp_cond,
        solar_exposure_condition=solar_exp_cond,
        polcal_exposure_condition=polcal_exp_cond,
        observe_exposure_condition=obs_exp_cond,
        center_wavelength=center_wavelength,
        slit_width=slit_width,
    )

    task()

    if num_modstates == 0:
        assert task.constants._db_dict[CryonirspBudName.num_modstates.value] == 1
    else:
        assert task.constants._db_dict[CryonirspBudName.num_modstates.value] == num_modstates
    assert task.constants._db_dict[CryonirspBudName.num_map_scans.value] == num_map_scans
    assert task.constants._db_dict[CryonirspBudName.num_scan_steps.value] == num_scan_steps
    assert task.constants._db_dict[CryonirspBudName.modulator_spin_mode.value] == "Continuous"

    assert sorted(task.constants._db_dict["DARK_FRAME_EXPOSURE_CONDITIONS_LIST"]) == sorted(
        [json.loads(json.dumps(condition)) for condition in dark_exp_conditions]
    )
    if arm_id == "SP":
        assert task.constants._db_dict["LAMP_GAIN_EXPOSURE_CONDITIONS_LIST"] == [
            json.loads(json.dumps(lamp_exp_cond))
        ]
    assert task.constants._db_dict["SOLAR_GAIN_EXPOSURE_CONDITIONS_LIST"] == [
        json.loads(json.dumps(solar_exp_cond))
    ]
    assert task.constants._db_dict["POLCAL_EXPOSURE_CONDITIONS_LIST"] == [
        json.loads(json.dumps(polcal_exp_cond))
    ]
    assert task.constants._db_dict["OBSERVE_EXPOSURE_CONDITIONS_LIST"] == [
        json.loads(json.dumps(obs_exp_cond))
    ]

    assert task.constants._db_dict["INSTRUMENT"] == "CRYO-NIRSP"
    assert task.constants._db_dict["AVERAGE_CADENCE"] == 10
    assert task.constants._db_dict["MAXIMUM_CADENCE"] == 10
    assert task.constants._db_dict["MINIMUM_CADENCE"] == 10
    assert task.constants._db_dict["VARIANCE_CADENCE"] == 0
    assert task.constants._db_dict[BudName.retarder_name] == "Cool retarder"
    if arm_id == "SP":
        assert (
            task.constants._db_dict[CryonirspBudName.center_wavelength.value] == center_wavelength
        )
        assert task.constants._db_dict[CryonirspBudName.slit_width.value] == slit_width
        assert (
            task.constants._db_dict[CryonirspBudName.grating_constant.value] == 770970.3576216539
        )  # From `SimpleModulatedHeaders`


@pytest.mark.parametrize("arm_id", ["SP"])
def test_parse_cryonirsp_linearized_data_internal_scan_loops_as_map_scan_and_scan_step(
    parse_linearized_task,
):
    """
    Given: A parse task for an SP dataset where the internal scan loops are being used as a proxy for
           map scans and scan steps.
    When: Calling the task instance
    Then: All tagged files exist and individual task tags are applied. Specifically test that the
          internal scan loop parameters map to num_map_scans and num_scan_steps.
    """

    task = parse_linearized_task

    lamp_exp_cond = ExposureConditions(10.0, AllowableOpticalDensityFilterNames.OPEN.value)
    solar_exp_cond = ExposureConditions(5.0, AllowableOpticalDensityFilterNames.OPEN.value)
    obs_exp_cond = ExposureConditions(6.0, AllowableOpticalDensityFilterNames.OPEN.value)
    polcal_exp_cond = ExposureConditions(7.0, AllowableOpticalDensityFilterNames.OPEN.value)
    dark_exp_conditions = [
        lamp_exp_cond,
        solar_exp_cond,
        obs_exp_cond,
        polcal_exp_cond,
    ]

    num_map_scans = 1
    num_scan_steps = 6
    num_alt_maps = 2
    num_alt_scan_steps = 3

    def make_dual_scan_loop_headers(translated_header):
        translated_header["CNP2DSS"] = (
            0.0  # This triggers the parsing of the dual internal scan loops
        )
        translated_header["CNP1DNSP"] = num_alt_scan_steps  # inner loop -- becomes num scan steps
        translated_header["CNP2DNSP"] = num_alt_maps  # outer loop -- becomes num map scans
        translated_header["CNP1DCUR"] = (translated_header["CNCURSCN"] - 1) % num_alt_scan_steps + 1
        translated_header["CNP2DCUR"] = (
            translated_header["CNCURSCN"] - 1
        ) // num_alt_scan_steps + 1
        return translated_header

    num_dark, num_lamp, num_solar, num_polcal, num_obs = make_linearized_test_frames(
        task,
        "SP",
        dark_exposure_conditions=dark_exp_conditions,
        num_modstates=1,
        num_scan_steps=num_scan_steps,
        num_map_scans=num_map_scans,
        change_translated_headers=make_dual_scan_loop_headers,
        lamp_exposure_condition=lamp_exp_cond,
        solar_exposure_condition=solar_exp_cond,
        polcal_exposure_condition=polcal_exp_cond,
        observe_exposure_condition=obs_exp_cond,
    )

    task()

    assert task.constants._db_dict[CryonirspBudName.num_scan_steps.value] == num_alt_scan_steps
    assert task.constants._db_dict[CryonirspBudName.num_map_scans.value] == num_alt_maps


@pytest.mark.parametrize("arm_id", ["CI", "SP"])
def test_parse_cryonirsp_not_polarimetric_obs(parse_linearized_task, arm_id):
    """
    Given: A ParseCryonirspInputData task
    When: Calling the task instance with non-polarimetric observe frames as input
    Then: PolarimetricCheckingUniqueBud has set the constants correctly
    """

    task = parse_linearized_task

    lin_tag = [CryonirspTag.linearized()]
    obs_exp_cond = ExposureConditions(6.0, AllowableOpticalDensityFilterNames.OPEN.value)
    polcal_exp_cond = ExposureConditions(7.0, AllowableOpticalDensityFilterNames.OPEN.value)
    dark_exp_conditions = [
        obs_exp_cond,
        polcal_exp_cond,
    ]

    num_steps = 3
    num_map_scans = 2
    num_sub_repeats = 2

    for condition in dark_exp_conditions:
        write_dark_frames_to_task(task, exposure_condition=condition, tags=lin_tag)
        write_solar_gain_frames_to_task(task, exposure_condition=condition, tags=lin_tag)
        if arm_id == "SP":
            write_lamp_gain_frames_to_task(task, exposure_condition=condition, tags=lin_tag)

    write_polcal_frames_to_task(
        task,
        num_modstates=8,
        num_map_scans=num_map_scans,
        tags=lin_tag,
        extra_headers=dict(),
        exposure_condition=polcal_exp_cond,
    )
    write_observe_frames_to_task(
        task,
        arm_id=arm_id,
        num_scan_steps=num_steps,
        num_map_scans=num_map_scans,
        num_sub_repeats=num_sub_repeats,
        num_modstates=1,
        exposure_condition=obs_exp_cond,
        num_measurements=1,
        tags=lin_tag,
    )

    task()

    assert task.constants._db_dict[CryonirspBudName.num_modstates.value] == 1
    assert task.constants._db_dict[CryonirspBudName.modulator_spin_mode.value] == "Continuous"


@pytest.fixture
def dummy_fits_obj():
    @dataclass
    class DummyFitsObj:
        ip_task_type: str
        number_of_modulator_states: int
        modulator_spin_mode: str

    return DummyFitsObj


def test_polarimetric_checking_unique_bud(dummy_fits_obj):
    """
    Given: A PolarimetricCheckingUniqueBud
    When: Ingesting various polcal and observe frames
    Then: The Bud functions as expected
    """
    pol_frame1 = dummy_fits_obj(
        ip_task_type="POLCAL", number_of_modulator_states=8, modulator_spin_mode="Continuous"
    )
    pol_frame2 = dummy_fits_obj(
        ip_task_type="POLCAL", number_of_modulator_states=3, modulator_spin_mode="Continuous"
    )

    obs_frame1 = dummy_fits_obj(
        ip_task_type="OBSERVE", number_of_modulator_states=8, modulator_spin_mode="Continuous"
    )
    obs_frame2 = dummy_fits_obj(
        ip_task_type="OBSERVE", number_of_modulator_states=2, modulator_spin_mode="Continuous"
    )

    nonpol_obs_frame1 = dummy_fits_obj(
        ip_task_type="OBSERVE", number_of_modulator_states=1, modulator_spin_mode="Continuous"
    )
    nonpol_obs_frame2 = dummy_fits_obj(
        ip_task_type="OBSERVE", number_of_modulator_states=1, modulator_spin_mode="Bad"
    )

    # Test failures in `is_polarimetric
    Bud = PolarimetricCheckingUniqueBud("dummy_constant", "number_of_modulator_states")
    Bud.update("key1", obs_frame1)
    Bud.update("key2", obs_frame2)
    with pytest.raises(
        ValueError, match="Observe frames have more than one value of NUM_MODSTATES."
    ):
        Bud.is_polarimetric()

    Bud = PolarimetricCheckingUniqueBud("dummy_constant", "number_of_modulator_states")
    Bud.update("key1", nonpol_obs_frame1)
    Bud.update("key2", nonpol_obs_frame2)
    with pytest.raises(
        ValueError, match="Observe frames have more than one value of MODULATOR_SPIN_MODE."
    ):
        Bud.is_polarimetric()

    # Test correct operation of `is_polarimetric`
    Bud = PolarimetricCheckingUniqueBud("dummy_constant", "number_of_modulator_states")
    Bud.update("key1", nonpol_obs_frame1)
    assert not Bud.is_polarimetric()

    Bud = PolarimetricCheckingUniqueBud("dummy_constant", "number_of_modulator_states")
    Bud.update("key1", obs_frame1)
    assert Bud.is_polarimetric()

    # Test non-unique polcal values
    Bud = PolarimetricCheckingUniqueBud("dummy_constant", "number_of_modulator_states")
    Bud.update("key1", obs_frame1)
    Bud.update("key2", pol_frame1)
    Bud.update("key3", pol_frame2)
    with pytest.raises(ValueError, match="Polcal frames have more than one value of NUM_MODSTATES"):
        Bud.getter("key1")

    # Test for correct error if polcal and observe frames have different values for polarimetric data
    Bud = PolarimetricCheckingUniqueBud("dummy_constant", "number_of_modulator_states")
    Bud.update("key1", obs_frame1)
    Bud.update("key2", pol_frame2)
    with pytest.raises(ValueError, match="Polcal and Observe frames have different values for"):
        Bud.getter("key1")

    # Test that polcal and observe frames having different values doesn't matter for non-polarimetric datra
    Bud = PolarimetricCheckingUniqueBud("dummy_constant", "modulator_spin_mode")
    Bud.update("key1", nonpol_obs_frame2)
    Bud.update("key2", pol_frame2)
    assert Bud.getter("key1") == "Bad"


@pytest.mark.parametrize("arm_id", ["CI", "SP"])
def test_missing_solar_gain_frames(parse_linearized_task, arm_id):
    """
    Given: A dataset missing solar gain frames
    When: Parsing
    Then: The 'CheckGainFramesPickyBud' raises an error
    """
    task = parse_linearized_task

    lin_tag = [CryonirspTag.linearized()]
    gain_exposure_condition = ExposureConditions(
        10.0, AllowableOpticalDensityFilterNames.OPEN.value
    )
    dark_exp_condition = ExposureConditions(10.0, AllowableOpticalDensityFilterNames.OPEN.value)

    # Needed so the dark picky bud is happy
    write_dark_frames_to_task(task, exposure_condition=dark_exp_condition, tags=lin_tag)

    write_lamp_gain_frames_to_task(
        task,
        tags=lin_tag,
        exposure_condition=gain_exposure_condition,
        num_modstates=1,
    )

    with pytest.raises(ValueError, match="solar_gain frames not found."):
        task()


@pytest.mark.parametrize("arm_id", ["SP"])
def test_missing_lamp_gain_frames(parse_linearized_task, arm_id):
    """
    Given: A dataset missing lamp gain frames
    When: Parsing
    Then: The 'CheckGainFramesPickyBud' raises an error
    """
    task = parse_linearized_task

    lin_tag = [CryonirspTag.linearized()]
    gain_exposure_condition = ExposureConditions(
        10.0, AllowableOpticalDensityFilterNames.OPEN.value
    )
    dark_exp_condition = ExposureConditions(10.0, AllowableOpticalDensityFilterNames.OPEN.value)

    # Needed so the dark picky bud is happy
    write_dark_frames_to_task(task, exposure_condition=dark_exp_condition, tags=lin_tag)

    write_solar_gain_frames_to_task(
        task,
        tags=lin_tag,
        exposure_condition=gain_exposure_condition,
        num_modstates=1,
    )

    with pytest.raises(ValueError, match="lamp_gain frames not found."):
        task()


@pytest.mark.parametrize("arm_id", ["CI"])
def test_wrong_exposure_time_lamp_gain_dark(parse_linearized_task, arm_id):
    """
    Given: lamp gain frames with a different exposure time than the dark frames
    When: parsing data where the lamp gain has no matching exposure time
    Then: everything is fine because CRYO-CI ignores lamp gains
    """
    task = parse_linearized_task
    lin_tag = [CryonirspTag.linearized()]
    solar_gain_exposure_condition = ExposureConditions(
        10.0, AllowableOpticalDensityFilterNames.OPEN.value
    )
    write_solar_gain_frames_to_task(
        task,
        tags=lin_tag,
        exposure_condition=solar_gain_exposure_condition,
        num_modstates=1,
    )
    lamp_gain_exposure_condition = ExposureConditions(
        1000.0, AllowableOpticalDensityFilterNames.OPEN.value
    )
    write_lamp_gain_frames_to_task(
        task,
        tags=lin_tag,
        exposure_condition=lamp_gain_exposure_condition,
        num_modstates=1,
    )
    dark_exp_condition = ExposureConditions(10.0, AllowableOpticalDensityFilterNames.OPEN.value)
    write_dark_frames_to_task(task, exposure_condition=dark_exp_condition, tags=lin_tag)

    task()

    assert task.constants._db_dict["DARK_FRAME_EXPOSURE_CONDITIONS_LIST"] == [[10.0, "OPEN"]]
    assert task.constants._db_dict["SOLAR_GAIN_EXPOSURE_CONDITIONS_LIST"] == [[10.0, "OPEN"]]
    assert task.constants._db_dict[
        "CI_NON_DARK_AND_NON_POLCAL_AND_NON_LAMP_GAIN_TASK_EXPOSURE_CONDITIONS_LIST"
    ] == [[10.0, "OPEN"]]
    with pytest.raises(KeyError):
        assert task.constants._db_dict["LAMP_GAIN_EXPOSURE_CONDITIONS_LIST"]
