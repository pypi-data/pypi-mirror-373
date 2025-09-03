import numpy as np
import pytest
from astropy.io import fits
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.codecs.fits import fits_hdu_decoder

from dkist_processing_cryonirsp.codecs.fits import cryo_fits_array_decoder
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.tasks.cryonirsp_base import CryonirspTaskBase
from dkist_processing_cryonirsp.tests.conftest import CryonirspConstantsDb
from dkist_processing_cryonirsp.tests.conftest import cryonirsp_testing_parameters_factory

NUM_BEAMS = 2
NUM_MODSTATES = 8
NUM_CS_STEPS = 6
NUM_SCAN_STEPS = 10
WAVE = 1082.0


@pytest.fixture(scope="function")
def cryo_science_task(
    tmp_path, recipe_run_id, assign_input_dataset_doc_to_task, init_cryonirsp_constants_db
):
    class Task(CryonirspTaskBase):
        def run(self): ...

    constants_db = CryonirspConstantsDb(
        NUM_MODSTATES=NUM_MODSTATES,
        NUM_CS_STEPS=NUM_CS_STEPS,
        NUM_SCAN_STEPS=NUM_SCAN_STEPS,
        WAVELENGTH=WAVE,
    )
    init_cryonirsp_constants_db(recipe_run_id, constants_db)
    with Task(
        recipe_run_id=recipe_run_id,
        workflow_name="parse_cryonirsp_input_data",
        workflow_version="VX.Y",
    ) as task:
        try:
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            param_class = cryonirsp_testing_parameters_factory(task)
            assign_input_dataset_doc_to_task(task, param_class())
            yield task
        finally:
            task._purge()


def test_write_intermediate_arrays(cryo_science_task):
    """
    Given: A CryonirspTaskBase task
    When: Writing a single intermediate array
    Then: The array is written and tagged correctly
    """
    data = np.random.random((10, 10))
    head = fits.Header()
    head["TEST"] = "foo"
    cryo_science_task.write(
        data=data,
        header=head,
        tags=[
            CryonirspTag.intermediate_frame(beam=1),
            CryonirspTag.map_scan(2),
            CryonirspTag.scan_step(3),
            CryonirspTag.task("BAR"),
        ],
        encoder=fits_array_encoder,
    )
    loaded_list = list(
        cryo_science_task.read(
            tags=[
                CryonirspTag.intermediate_frame(beam=1),
                CryonirspTag.map_scan(2),
                CryonirspTag.scan_step(3),
                CryonirspTag.task("BAR"),
            ],
            decoder=fits_hdu_decoder,
        )
    )
    assert len(loaded_list) == 1
    hdu = loaded_list[0]
    np.testing.assert_equal(hdu.data, data)
    assert hdu.header["TEST"] == "foo"


def test_write_intermediate_arrays_task_tag(cryo_science_task):
    """
    Given: A CryonirspTaskBase task
    When: Writing a single intermediate array with a formatted task tag input arg
    Then: The array is written and tagged correctly
    """
    data = np.random.random((10, 10))
    head = fits.Header()
    head["TEST"] = "foo"

    # bad_pixel_map chosen for no particular reason
    cryo_science_task.write(
        data=data,
        header=head,
        tags=[CryonirspTag.intermediate_frame(), CryonirspTag.task_bad_pixel_map()],
        encoder=fits_array_encoder,
    )
    loaded_list = list(
        cryo_science_task.read(
            tags=[CryonirspTag.task_bad_pixel_map()],
            decoder=fits_hdu_decoder,
        )
    )
    assert len(loaded_list) == 1
    hdu = loaded_list[0]
    np.testing.assert_equal(hdu.data, data)
    assert hdu.header["TEST"] == "foo"


def test_write_intermediate_arrays_none_header(cryo_science_task):
    """
    Given: A CryonirspTaskBase task
    When: Writing a single intermediate array with no header
    Then: The array is written and tagged correctly
    """
    data = np.random.random((10, 10))
    cryo_science_task.write(
        data=data,
        tags=[
            CryonirspTag.intermediate_frame(beam=1),
            CryonirspTag.map_scan(2),
            CryonirspTag.scan_step(3),
            CryonirspTag.task("BAR"),
        ],
        encoder=fits_array_encoder,
    )
    loaded_list = list(
        cryo_science_task.read(
            tags=[
                CryonirspTag.intermediate_frame(beam=1),
                CryonirspTag.map_scan(2),
                CryonirspTag.scan_step(3),
                CryonirspTag.task("BAR"),
            ],
            decoder=fits_hdu_decoder,
        )
    )
    assert len(loaded_list) == 1
    hdu = loaded_list[0]
    np.testing.assert_equal(hdu.data, data)


@pytest.fixture
def cryo_science_task_with_tagged_intermediates(
    recipe_run_id, tmpdir_factory, init_cryonirsp_constants_db
):
    class Task(CryonirspTaskBase):
        def run(self): ...

    init_cryonirsp_constants_db(recipe_run_id, CryonirspConstantsDb())
    with Task(
        recipe_run_id=recipe_run_id,
        workflow_name="parse_cryo_input_data",
        workflow_version="VX.Y",
    ) as task:
        try:
            task.scratch = WorkflowFileSystem(scratch_base_path=tmpdir_factory.mktemp("data"))
            tag_names = [["beam"], ["exposure_time", "task"], ["modstate"]]
            tag_vals = [[1], [10.23, "dark"], [3]]
            tag_fcns = [[getattr(CryonirspTag, n) for n in nl] for nl in tag_names]
            tag_list = [[f(v) for f, v in zip(fl, vl)] for fl, vl in zip(tag_fcns, tag_vals)]
            for i, tags in enumerate(tag_list):
                hdul = fits.HDUList([fits.PrimaryHDU(data=np.ones((2, 2)) * i)])
                fname = task.scratch.workflow_base_path / f"file{i}.fits"
                hdul.writeto(fname)
                task.tag(fname, tags + CryonirspTag.intermediate_frame())

            yield task, tag_names, tag_vals
        finally:
            task._purge()


def test_load_intermediate_arrays(cryo_science_task_with_tagged_intermediates):
    """
    Given: A task with tagged intermediate frames
    When: Reading intermediate frames
    Then: The correct arrays are returned
    """
    task, tag_names, tag_vals = cryo_science_task_with_tagged_intermediates
    tag_list_list = [
        [getattr(CryonirspTag, n)(v) for n, v in zip(nl, vl)] for nl, vl in zip(tag_names, tag_vals)
    ]
    for i, tags in enumerate(tag_list_list):
        arrays = list(
            task.read(
                tags=[CryonirspTag.intermediate_frame(), tags],
                decoder=cryo_fits_array_decoder,
            )
        )
        assert len(arrays) == 1
        np.testing.assert_equal(arrays[0], np.ones((2, 2)) * i)
