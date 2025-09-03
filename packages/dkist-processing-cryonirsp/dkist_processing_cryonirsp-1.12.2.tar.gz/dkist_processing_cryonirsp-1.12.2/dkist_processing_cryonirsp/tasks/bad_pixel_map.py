"""Task class for bad pixel map computation."""

import numpy as np
import scipy.ndimage as spnd
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_service_configuration.logging import logger

from dkist_processing_cryonirsp.codecs.fits import cryo_fits_array_decoder
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import (
    CryonirspLinearizedFitsAccess,
)
from dkist_processing_cryonirsp.tasks.cryonirsp_base import CryonirspTaskBase

__all__ = ["BadPixelMapCalibration"]


class BadPixelMapCalibration(CryonirspTaskBase):
    """
    Task class for calculation of the bad pixel map for later use during calibration.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs

    """

    record_provenance = True

    def run(self):
        """
        Compute the bad pixel map by analyzing a set of solar gain images.

        Steps:
        1. Compute the average gain image
        2. Smooth the array with a median filter
        3. Calculate the difference between the smoothed and input arrays
        4. Threshold the difference array on both ends to determine good and bad pixels
        5. Save the bad pixel map as a fits file

        Returns
        -------
        None

        """
        with self.apm_task_step(f"Compute average uncorrected solar gain image"):
            average_solar_gain_array = self.compute_average_gain_array()

        with self.apm_task_step(f"Compute the bad pixel map"):
            with self.apm_processing_step("Smooth array with median filter"):
                filter_size = self.parameters.bad_pixel_map_median_filter_size
                filtered_array = spnd.median_filter(
                    average_solar_gain_array,
                    size=filter_size,
                    mode="constant",
                    cval=np.nanmedian(average_solar_gain_array),
                )

            with self.apm_processing_step("Identify bad pixels"):
                thresh = self.parameters.bad_pixel_map_threshold_factor

                diff = filtered_array - average_solar_gain_array
                bad_pixel_map = np.array((np.abs(diff) > thresh * diff.std()), dtype=int)

                # Find and fix any residual zeros that slipped through the bad pixel map.
                zeros = np.where(average_solar_gain_array == 0.0)
                bad_pixel_map[zeros] = 1

        with self.apm_writing_step("Writing bad pixel map"):
            self.write(
                data=bad_pixel_map,
                tags=[CryonirspTag.intermediate_frame(), CryonirspTag.task_bad_pixel_map()],
                encoder=fits_array_encoder,
            )

    def compute_average_gain_array(self) -> np.ndarray:
        """
        Compute an average of uncorrected solar gain arrays.

        We are computing the overall illumination pattern for one (CI) or both (SP) beams
        simultaneously, so no dark correction is required and no beam splitting is used at
        this point. Solar gain images are used because of their higher flux levels and they
        more accurately represent the illuminated beam seen in solar images.

        Returns
        -------
        The average gain array
        """
        lin_corr_gain_arrays = self.read(
            tags=[CryonirspTag.linearized_frame(), CryonirspTag.task_solar_gain()],
            decoder=cryo_fits_array_decoder,
            fits_access_class=CryonirspLinearizedFitsAccess,
        )

        averaged_gain_data = average_numpy_arrays(lin_corr_gain_arrays)
        return averaged_gain_data
