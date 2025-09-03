from typing import Literal

import numpy as np
import pytest
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.tasks import WorkflowTaskBase

from dkist_processing_cryonirsp.models.constants import CryonirspConstants
from dkist_processing_cryonirsp.tasks.mixin.corrections import CorrectionsMixin
from dkist_processing_cryonirsp.tests.conftest import CryonirspConstantsDb
from dkist_processing_cryonirsp.tests.conftest import cryonirsp_testing_parameters_factory

base_bad_pixel_map = np.zeros(shape=(10, 10))

normal_bad_pixel_map = base_bad_pixel_map.copy()
normal_bad_pixel_map[1, 6] = 1

column_error_bad_pixel_map = base_bad_pixel_map.copy()
column_error_bad_pixel_map[:, 6] = 1


class BadPixelMapTask(WorkflowTaskBase, CorrectionsMixin):
    constants: CryonirspConstants

    @property
    def constants_model_class(self):
        """Get CryoNIRSP pipeline constants."""
        return CryonirspConstants

    def run(self):
        pass


@pytest.fixture(params=["CI", "SP"])
def bad_pixel_mask_task(
    tmp_path,
    recipe_run_id,
    assign_input_dataset_doc_to_task,
    mocker,
    fake_gql_client,
    request,
    init_cryonirsp_constants_db,
):
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    constants_db = CryonirspConstantsDb(
        ARM_ID=request.param,
    )
    init_cryonirsp_constants_db(recipe_run_id, constants_db)
    with BadPixelMapTask(
        recipe_run_id=recipe_run_id,
        workflow_name="bad_pixel_mask",
        workflow_version="VX.Y",
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task.scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            param_class = cryonirsp_testing_parameters_factory(task)
            assign_input_dataset_doc_to_task(task, param_class())
            yield task
        finally:
            task._purge()


def contrive_bad_px_neighborhood(
    array: np.ndarray, bad_px_location: tuple[int, int], kernel_size: int, desired_median: float
) -> np.array:
    """
    Adjust array values so the neighborhood around a bad pixel results in a known value being used to replace that pixel.
    """
    # Sticking with the y, x convention used by `corrections_correct_bad_pixels`.
    y, x = bad_px_location
    half_kernel_size = kernel_size // 2
    num_y, num_x = array.shape

    y_slice = slice(max(y - half_kernel_size, 0), min(y + half_kernel_size + 1, num_y))
    x_slice = slice(max(x - half_kernel_size, 0), min(x + half_kernel_size + 1, num_x))

    array[y_slice, x_slice] = desired_median

    return array


@pytest.mark.parametrize(
    "bad_pixel_map, algorithm_type",
    [
        pytest.param(normal_bad_pixel_map, "normal", id="normal algorithm"),
        pytest.param(column_error_bad_pixel_map, "fast", id="fast algorithm"),
    ],
)
def test_corrections_correct_bad_pixels(bad_pixel_map, algorithm_type, bad_pixel_mask_task):
    t = bad_pixel_mask_task
    bad_pixel_x = 1
    bad_pixel_y = 6

    # Create a data array. Adding 10 ensures that 0 will be a valid sentinel value of bad-ness
    rng = np.random.default_rng()
    array_to_fix = rng.random((10, 10), dtype=float) * 100 + 10.0

    # Assign a single bad pixel to check against
    if algorithm_type == "normal":
        expected_corrected_value = rng.random() * 100 + 10
        array_to_fix = contrive_bad_px_neighborhood(
            array=array_to_fix,
            bad_px_location=(1, 6),
            kernel_size=t.parameters.corrections_bad_pixel_median_filter_size,
            desired_median=expected_corrected_value,
        )
    array_to_fix[bad_pixel_x, bad_pixel_y] = 0

    corrected_array = t.corrections_correct_bad_pixels(
        array_to_fix=array_to_fix, bad_pixel_map=bad_pixel_map
    )
    if algorithm_type == "fast":
        for val in corrected_array[:, bad_pixel_y]:
            assert val == np.nanmedian(array_to_fix)
        assert corrected_array[bad_pixel_x, bad_pixel_y] == np.nanmedian(array_to_fix)

    if algorithm_type == "normal":
        x, y = np.meshgrid(np.arange(10), np.arange(10))
        idx = np.where((x != bad_pixel_x) | (y != bad_pixel_y))
        np.testing.assert_array_equal(corrected_array[idx], array_to_fix[idx])
        assert corrected_array[bad_pixel_x, bad_pixel_y] == expected_corrected_value
