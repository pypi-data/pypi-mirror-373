import pytest
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.bytes import bytes_decoder
from dkist_processing_common.codecs.quality import quality_data_encoder
from dkist_processing_common.tasks import CreateTrialQualityReport

from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.tests.conftest import CryonirspConstantsDb


@pytest.fixture()
def quality_data_warning_only() -> list[dict]:
    """Simple quality data that can be used to create a quality report in pdf format"""
    return [
        {
            "name": "Range checks",
            "description": "This metric is checking that certain input and calculated parameters"
            " fall within a valid data range. If no parameters are listed here,"
            " all pipeline parameters were measured to be in range",
            "statement": "This is a test quality report with no data",
            "plot_data": None,
            "histogram_data": None,
            "table_data": None,
            "modmat_data": None,
            "efficiency_data": None,
            "raincloud_data": None,
            "warnings": ["warning 1", "warning 2"],
        }
    ]


@pytest.fixture
def create_trial_quality_report_task(
    tmp_path,
    recipe_run_id,
    init_cryonirsp_constants_db,
    quality_data_warning_only,
) -> CreateTrialQualityReport:
    constants_db = CryonirspConstantsDb()
    init_cryonirsp_constants_db(recipe_run_id, constants_db)
    with CreateTrialQualityReport(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(
            recipe_run_id=recipe_run_id,
            scratch_base_path=tmp_path,
        )
        task.write(
            quality_data_warning_only,
            tags=CryonirspTag.quality_data(),
            encoder=quality_data_encoder,
            relative_path=f"{task.constants.dataset_id}_quality_data.json",
        )

        yield task
        task._purge()


def test_create_trial_quality_report(create_trial_quality_report_task):
    """
    :Given: An instance of CreateTrialQualityReport with tagged quality data
    :When: CreateTrialQualityReport is run
    :Then: A quality report pdf file gets created and tagged
    """
    task = create_trial_quality_report_task
    # When
    task()
    # Then
    paths = list(task.read(tags=[CryonirspTag.output(), CryonirspTag.quality_report()]))
    assert len(paths) == 1
    quality_report = next(
        task.read(
            tags=[CryonirspTag.output(), CryonirspTag.quality_report()], decoder=bytes_decoder
        )
    )
    assert isinstance(quality_report, bytes)
    assert b"%PDF" == quality_report[:4]
