import json
import re
from dataclasses import dataclass
from itertools import chain
from typing import Callable
from unittest.mock import MagicMock
from uuid import uuid4

import numpy as np
import pytest
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.json import json_decoder
from dkist_processing_common.tasks import AssembleQualityData
from dkist_quality.report import ReportMetric
from pandas import DataFrame

from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.tasks.l1_output_data import CIAssembleQualityData
from dkist_processing_cryonirsp.tasks.l1_output_data import SPAssembleQualityData
from dkist_processing_cryonirsp.tests.conftest import CryonirspConstantsDb


@pytest.fixture(scope="function", params=["CI", "SP"])
def cryo_assemble_quality_data_task(
    tmp_path, recipe_run_id, init_cryonirsp_constants_db, request
) -> AssembleQualityData:
    arm_id = request.param
    init_cryonirsp_constants_db(
        recipe_run_id=recipe_run_id, constants_obj=CryonirspConstantsDb(ARM_ID=arm_id)
    )
    if arm_id == "CI":
        with CIAssembleQualityData(
            recipe_run_id=recipe_run_id,
            workflow_name="cryonirsp_submit_quality",
            workflow_version="VX.Y",
        ) as task:
            yield task, arm_id
            task._purge()
    elif arm_id == "SP":
        with SPAssembleQualityData(
            recipe_run_id=recipe_run_id,
            workflow_name="cryonirsp_submit_quality",
            workflow_version="VX.Y",
        ) as task:
            yield task, arm_id
            task._purge()
    else:
        raise RuntimeError(f"Invalid cryo-nirsp arm_id: {arm_id!r}")


@pytest.fixture
def dummy_quality_data() -> list[dict]:
    return [{"dummy_key": "dummy_value"}]


@pytest.fixture
def quality_assemble_data_mock(mocker, dummy_quality_data) -> MagicMock:
    yield mocker.patch(
        "dkist_processing_common.tasks.mixin.quality.QualityMixin.quality_assemble_data",
        return_value=dummy_quality_data,
        autospec=True,
    )


@dataclass
class Metric:
    value: dict | list
    tags: list[str]

    @property
    def value_bytes(self) -> bytes:
        return json.dumps(self.value).encode()

    @property
    def file_name(self) -> str:
        # always include the metric in the filename
        metric = re.sub("[ _]", "-", self.tags[0])
        # if a second tag is present, include it in the filename
        second_tag = re.sub("[ _]", "-", self.tags[1]) if len(self.tags) > 1 else None
        if second_tag:
            return f"{metric}_{second_tag}_{uuid4().hex[:6]}.dat"
        return f"{metric}_{uuid4().hex[:6]}.dat"


@pytest.fixture()
def dataframe_json() -> str:
    """Random dataframe for raincloud_plot"""
    nummod = 3
    numstep = 10
    numpoints = 100
    points = np.random.randn(numpoints * numstep * nummod)
    mods = np.hstack([np.arange(nummod) + 1 for i in range(numstep * numpoints)])
    steps = np.hstack([np.arange(numstep) + 1 for i in range(nummod * numpoints)])
    data = np.vstack((points, mods, steps)).T
    return DataFrame(data=data, columns=["Flux residual", "Modstate", "CS Step"]).to_json()


@pytest.fixture()
def quality_metrics(dataframe_json) -> list[Metric]:
    """
    Quality metric data
    """
    metrics = [
        Metric(
            {
                "x_values": ["2021-01-01T01:01:01", "2021-01-01T02:01:01"],
                "y_values": [1, 2],
                "series_name": "",
            },
            ["QUALITY_FRAME_AVERAGE", "QUALITY_TASK_DARK"],
        ),
        Metric(
            {
                "x_values": ["2021-01-01T01:01:01", "2021-01-01T02:01:01"],
                "y_values": [3, 4],
                "series_name": "",
            },
            ["QUALITY_FRAME_AVERAGE", "QUALITY_TASK_GAIN"],
        ),
        Metric(
            {
                "x_values": ["2021-01-01T01:01:01", "2021-01-01T02:01:01"],
                "y_values": [5, 6],
                "series_name": "",
            },
            ["QUALITY_FRAME_RMS", "QUALITY_TASK_DARK"],
        ),
        Metric(
            {
                "x_values": ["2021-01-01T01:01:01", "2021-01-01T02:01:01"],
                "y_values": [7, 8],
                "series_name": "",
            },
            ["QUALITY_FRAME_RMS", "QUALITY_TASK_GAIN"],
        ),
        Metric(
            {"task_type": "gain", "frame_averages": [6, 7, 8, 9, 10]}, ["QUALITY_DATASET_AVERAGE"]
        ),
        Metric(
            {"task_type": "dark", "frame_averages": [1, 2, 3, 4, 5]}, ["QUALITY_DATASET_AVERAGE"]
        ),
        Metric(
            {"task_type": "dark", "frame_averages": [6, 7, 8, 9, 10]}, ["QUALITY_DATASET_AVERAGE"]
        ),
        Metric({"task_type": "dark", "frame_rms": [1, 2, 3, 4, 5]}, ["QUALITY_DATASET_RMS"]),
        Metric({"task_type": "dark", "frame_rms": [6, 7, 8, 8, 10]}, ["QUALITY_DATASET_RMS"]),
        Metric({"task_type": "gain", "frame_rms": [2, 4, 6, 8, 10]}, ["QUALITY_DATASET_RMS"]),
        Metric(
            {
                "x_values": ["2021-01-01T01:01:01", "2021-01-01T02:01:01"],
                "y_values": [1, 2],
                "series_name": "",
            },
            ["QUALITY_FRIED_PARAMETER"],
        ),
        Metric(
            {
                "x_values": ["2021-01-01T01:01:01", "2021-01-01T02:01:01"],
                "y_values": [3, 4],
                "series_name": "",
            },
            ["QUALITY_LIGHT_LEVEL"],
        ),
        Metric(["Good", "Good", "Good", "Good", "Good", "Ill"], ["QUALITY_HEALTH_STATUS"]),
        Metric([1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0], ["QUALITY_AO_STATUS"]),
        Metric(
            {
                "x_values": ["2021-01-01T01:01:01", "2021-01-01T02:01:01"],
                "y_values": [5, 6],
                "series_name": "",
            },
            ["QUALITY_NOISE"],
        ),
        Metric(
            {
                "x_values": ["2021-01-01T01:01:01", "2021-01-01T02:01:01"],
                "y_values": [1, 2],
                "series_name": "I",
            },
            ["QUALITY_SENSITIVITY", "STOKES_I"],
        ),
        Metric(
            {
                "x_values": ["2021-01-01T01:01:01", "2021-01-01T02:01:01"],
                "y_values": [3, 4],
                "series_name": "Q",
            },
            ["QUALITY_SENSITIVITY", "STOKES_Q"],
        ),
        Metric(
            {
                "x_values": ["2021-01-01T01:01:01", "2021-01-01T02:01:01"],
                "y_values": [5, 6],
                "series_name": "U",
            },
            ["QUALITY_SENSITIVITY", "STOKES_U"],
        ),
        Metric(
            {
                "x_values": ["2021-01-01T01:01:01", "2021-01-01T02:01:01"],
                "y_values": [7, 8],
                "series_name": "V",
            },
            ["QUALITY_SENSITIVITY", "STOKES_V"],
        ),
        Metric(
            {"task_type": "dark", "total_frames": 100, "frames_not_used": 7}, ["QUALITY_TASK_TYPES"]
        ),
        Metric(
            {"task_type": "gain", "total_frames": 100, "frames_not_used": 0}, ["QUALITY_TASK_TYPES"]
        ),
        Metric(
            {
                "param_names": ["foo"],
                "param_vary": [True],
                "param_init_vals": [1],
                "param_fit_vals": [2],
                "param_diffs": [1],
                "param_ratios": [1],
                "warnings": ["A warning"],
            },
            ["QUALITY_POLCAL_GLOBAL_PAR_VALS", "QUALITY_TASK_CI BEAM 1"],
        ),
        Metric(
            {
                "label": "Beam foo",
                "modmat_list": np.random.randn(8, 4, 100).tolist(),
                "free_param_dict": {
                    "I_sys_CS00_step00": {"fit_values": [1, 2, 3.0], "init_value": 0.3},
                    "I_sys_CS00_step01": {"fit_values": [10, 20, 30.0], "init_value": 0.33},
                    "param_X": {"fit_values": [5, 6, 7.0], "init_value": 99},
                },
                "bin_strs": ["bin1", "bin2"],
                "total_bins": 100,
                "sampled_bins": 20,
                "num_varied_I_sys": 2,
            },
            ["QUALITY_POLCAL_LOCAL_PAR_VALS", "QUALITY_TASK_CI BEAM 1"],
        ),
        Metric(
            {
                "bin_strs": ["bin1", "bin2"],
                "total_bins": 100,
                "sampled_bins": 20,
                "red_chi_list": [1, 2, 3],
                "residual_json": dataframe_json,
            },
            ["QUALITY_POLCAL_FIT_RESIDUALS", "QUALITY_TASK_CI BEAM 1"],
        ),
        Metric(
            {
                "bin_strs": ["bin1", "bin2"],
                "total_bins": 100,
                "sampled_bins": 20,
                "efficiency_list": ((np.random.randn(4, 100) - 0.5) * 0.3).tolist(),
                "warnings": ["A warning"],
            },
            ["QUALITY_POLCAL_EFFICIENCY", "QUALITY_TASK_CI BEAM 1"],
        ),
        Metric({"name": "metric 1", "warnings": ["warning 1"]}, ["QUALITY_RANGE"]),
        Metric({"name": "metric 2", "warnings": ["warning 2"]}, ["QUALITY_RANGE"]),
        Metric({"name": "metric 3", "warnings": ["warning 3"]}, ["QUALITY_RANGE"]),
        Metric({"name": "hist 1", "value": 7, "warnings": None}, ["QUALITY_HISTORICAL"]),
        Metric({"name": "hist 2", "value": "abc", "warnings": None}, ["QUALITY_HISTORICAL"]),
        Metric(
            {"name": "hist 3", "value": 9.35, "warnings": "warning for historical metric 3"},
            ["QUALITY_HISTORICAL"],
        ),
    ]
    return metrics


@pytest.fixture()
def plot_data_expected() -> Callable[[str], bool]:
    """
    Tightly coupled with quality_metrics fixture and resultant report metric name
    """
    # names where plot_data is expected to be populated
    names = {
        "Average Across Frame - DARK",
        "Average Across Frame - GAIN",
        "Root Mean Square (RMS) Across Frame - DARK",
        "Root Mean Square (RMS) Across Frame - GAIN",
        "Fried Parameter",
        "Light Level",
        "Noise Estimation",
        "Sensitivity",
    }

    def expected(name: str) -> bool:
        return name in names

    return expected


@pytest.fixture()
def table_data_expected() -> Callable[[str], bool]:
    """
    Tightly coupled with quality_metrics fixture and resultant report metric name
    """
    # names where table_data is expected to be populated
    names = {
        "Average Across Dataset",
        "Dataset RMS",
        "Data Source Health",
        "Frame Counts",
        "PolCal Global Calibration Unit Fit - CI Beam 1",
        "Historical Comparisons",
    }

    def expected(name: str) -> bool:
        return name in names

    return expected


@pytest.fixture()
def modmat_data_expected() -> Callable[[str], bool]:
    """
    Tightly coupled with quality_metrics fixture and resultant report metric name
    """
    # names where modmat_data is expected to be populated
    names = {
        "PolCal Local Bin Fits - CI Beam 1",
    }

    def expected(name: str) -> bool:
        return name in names

    return expected


@pytest.fixture()
def histogram_data_expected() -> Callable[[str], bool]:
    """
    Tightly coupled with quality_metrics fixture and resultant report metric name
    """
    # names where histogram_data is expected to be populated
    names = {
        "PolCal Local Bin Fits - CI Beam 1",
        "PolCal Fit Residuals - CI Beam 1",
    }

    def expected(name: str) -> bool:
        return name in names

    return expected


@pytest.fixture()
def raincloud_data_expected() -> Callable[[str], bool]:
    """
    Tightly coupled with quality_metrics fixture and resultant report metric name
    """
    # names where raincloud_data is expected to be populated
    names = {
        "PolCal Fit Residuals - CI Beam 1",
    }

    def expected(name: str) -> bool:
        return name in names

    return expected


@pytest.fixture()
def efficiency_data_expected() -> Callable[[str], bool]:
    """
    Tightly coupled with quality_metrics fixture and resultant report metric name
    """
    # names where efficiency_data is expected to be populated
    names = {
        "PolCal Modulation Efficiency - CI Beam 1",
    }

    def expected(name: str) -> bool:
        return name in names

    return expected


@pytest.fixture()
def statement_expected() -> Callable[[str], bool]:
    """
    Tightly coupled with quality_metrics fixture and resultant report metric name
    """
    # names where statement is expected to be populated
    names = {
        "Fried Parameter",
        "Light Level",
        "Adaptive Optics Status",
    }

    def expected(name: str) -> bool:
        return name in names

    return expected


@pytest.fixture()
def warnings_expected() -> Callable[[str], bool]:
    """
    Tightly coupled with quality_metrics fixture and resultant report metric name
    """
    # names where warnings is expected to be populated
    names = {
        "Data Source Health",
        "Frame Counts",
        "PolCal Global Calibration Unit Fit - CI Beam 1",
        "PolCal Modulation Efficiency - CI Beam 1",
        "Range checks",
        "Historical Comparisons",
    }

    def expected(name: str) -> bool:
        return name in names

    return expected


@pytest.fixture()
def scratch_with_quality_metrics(recipe_run_id, tmp_path, quality_metrics) -> WorkflowFileSystem:
    """Scratch instance for a recipe run id with tagged quality metrics."""
    scratch = WorkflowFileSystem(
        recipe_run_id=recipe_run_id,
        scratch_base_path=tmp_path,
    )
    for metric in quality_metrics:
        scratch.write(metric.value_bytes, tags=metric.tags, relative_path=metric.file_name)
    return scratch


@pytest.fixture
def assemble_quality_data_task(
    tmp_path, recipe_run_id, scratch_with_quality_metrics, init_cryonirsp_constants_db
):
    constants_db = CryonirspConstantsDb(NUM_MODSTATES=2)
    init_cryonirsp_constants_db(recipe_run_id, constants_db)
    with CIAssembleQualityData(
        recipe_run_id=recipe_run_id,
        workflow_name="ci_assemble_quality",
        workflow_version="ci_assemble_quality_version",
    ) as task:
        task.scratch = WorkflowFileSystem(
            recipe_run_id=recipe_run_id,
            scratch_base_path=tmp_path,
        )
        task.scratch = scratch_with_quality_metrics
        yield task
        task._purge()


def test_assemble_quality_data(
    assemble_quality_data_task,
    recipe_run_id,
    plot_data_expected,
    table_data_expected,
    modmat_data_expected,
    histogram_data_expected,
    raincloud_data_expected,
    efficiency_data_expected,
    statement_expected,
    warnings_expected,
):
    """
    :Given: An instance of CIAssembleQualityData with tagged quality metrics
    :When: CIAssembleQualityData is run
    :Then: A json quality data file for the dataset gets saved and tagged
    """
    task = assemble_quality_data_task

    # When
    task()
    # Then
    # each quality_data file is a list - this will combine the elements of multiple lists into a single list
    quality_data = list(
        chain.from_iterable(task.read(tags=CryonirspTag.quality_data(), decoder=json_decoder))
    )
    # 19 with polcal
    assert len(quality_data) == 19
    for metric_data in quality_data:
        rm: ReportMetric = ReportMetric.from_dict(metric_data)
        assert isinstance(rm.name, str)
        assert isinstance(rm.description, str)
        if plot_data_expected(rm.name):
            assert rm.plot_data
        if table_data_expected(rm.name):
            assert rm.table_data
        if modmat_data_expected(rm.name):
            assert rm.modmat_data
        if histogram_data_expected(rm.name):
            assert rm.histogram_data
        if raincloud_data_expected(rm.name):
            assert rm.raincloud_data
        if efficiency_data_expected(rm.name):
            assert rm.efficiency_data
        if statement_expected(rm.name):
            assert rm.statement
        if warnings_expected(rm.name):
            assert rm.warnings


def test_correct_polcal_label_list(cryo_assemble_quality_data_task, quality_assemble_data_mock):
    """
    Given: A CIAssembleQualityData task
    When: Calling the task
    Then: The correct polcal_label_list property is passed to .quality_assemble_data
    """
    task, arm_id = cryo_assemble_quality_data_task

    task()

    if arm_id == "SP":
        quality_assemble_data_mock.assert_called_once_with(
            task, polcal_label_list=["SP Beam 1", "SP Beam 2"]
        )
    elif arm_id == "CI":
        quality_assemble_data_mock.assert_called_once_with(task, polcal_label_list=["CI Beam 1"])
    else:
        raise RuntimeError(f"Invalid cryo-nirsp arm_id: {arm_id!r}")
