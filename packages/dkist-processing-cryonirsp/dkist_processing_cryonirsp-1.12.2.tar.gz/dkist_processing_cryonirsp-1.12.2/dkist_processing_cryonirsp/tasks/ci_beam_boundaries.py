"""Cryonirsp CI beam boundaries task."""

import largestinteriorrectangle as lir
import numpy as np
from dkist_service_configuration.logging import logger

from dkist_processing_cryonirsp.models.beam_boundaries import BeamBoundary
from dkist_processing_cryonirsp.tasks.beam_boundaries_base import BeamBoundariesCalibrationBase

__all__ = ["CIBeamBoundariesCalibration"]


class CIBeamBoundariesCalibration(BeamBoundariesCalibrationBase):
    """Task class for calculation of the CI beam boundaries for later use during calibration."""

    def split_beams(self, array: np.ndarray) -> list[np.ndarray]:
        """
        Return the input array, as there is no beam split for CI.

        This is just a pass-through method to facilitate using the same processing
        steps in the base run method.

        Parameters
        ----------
        array
            The input array

        Returns
        -------
        [array]
            The input array embedded in a list
        """
        return [array]

    def compute_final_beam_boundaries(
        self, smoothed_solar_gain_array: np.ndarray, illuminated_boundaries: list[BeamBoundary]
    ):
        """
        Compute the final beam boundaries to be used when accessing CI beam images from the input dual-beam arrays.

        Note: For CI, the illuminated beam boundaries ARE the final beam boundaries.
        This method is simply a pass-through that allows both SP and CI to use the processing sequence.

        Parameters
        ----------
        smoothed_solar_gain_array
            The smoothed solar gain array for a single CI beam.
        illuminated_boundaries
            A list with a single BeamBoundary object for the illuminated CI beam.

        Returns
        -------
        [BeamBoundary]
            The CI BeamBoundary object embedded in a list.
        """
        return illuminated_boundaries
