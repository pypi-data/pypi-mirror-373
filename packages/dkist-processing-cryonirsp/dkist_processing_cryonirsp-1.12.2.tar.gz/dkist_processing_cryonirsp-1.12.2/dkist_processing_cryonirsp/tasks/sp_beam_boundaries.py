"""Cryonirsp SP beam boundaries task."""

import math

import numpy as np
from dkist_service_configuration.logging import logger

from dkist_processing_cryonirsp.models.beam_boundaries import BeamBoundary
from dkist_processing_cryonirsp.tasks.beam_boundaries_base import BeamBoundariesCalibrationBase
from dkist_processing_cryonirsp.tasks.mixin.shift_measurements import SPATIAL
from dkist_processing_cryonirsp.tasks.mixin.shift_measurements import SPECTRAL
from dkist_processing_cryonirsp.tasks.mixin.shift_measurements import ShiftMeasurementsMixin

__all__ = ["SPBeamBoundariesCalibration"]


class SPBeamBoundariesCalibration(BeamBoundariesCalibrationBase, ShiftMeasurementsMixin):
    """Task class for calculation of the SP beam boundaries for later use during calibration."""

    def split_beams(self, array: np.ndarray) -> list[np.ndarray]:
        """
        Split the SP image into two beams, leaving out the predefined split boundary region.

        Parameters
        ----------
        array
            The input dual-beam SP array

        Returns
        -------
        [beam_1, beam_2]
            A list containing the split beam images.
        """
        self.split_boundary = self.compute_split_boundary(array)
        beam_1 = array[:, : self.split_boundary[0]]
        beam_2 = array[:, self.split_boundary[1] :]
        return [beam_1, beam_2]

    def compute_final_beam_boundaries(
        self, arrays: list[np.ndarray], boundaries: list[BeamBoundary]
    ):
        """
        Compute the final SP beam boundaries from the illuminated beams.

        Parameters
        ----------
        arrays
            A list of smoothed solar gain arrays, ready for beam identification
        boundaries
            A list of the illuminated region BeamBoundary objects for each beam [beam_1_boundaries, beam_2_boundaries]

        Returns
        -------
        [beam_1_boundaries, beam_2_boundaries]
        A list of final adjusted BeamBoundary objects, one for each beam
        """
        # Step 7.:
        beam_1_array = arrays[0][boundaries[0].y_slice, boundaries[0].x_slice]
        beam_2_array = arrays[1][boundaries[1].y_slice, boundaries[1].x_slice]

        # Step 8:
        spectral_shift, spatial_shift = self.compute_offset(beam_1_array, beam_2_array)

        # Step 9:
        new_beam_boundaries = self.compute_shared_boundaries_from_overlapping_beams(
            boundaries, spectral_shift, spatial_shift
        )
        return new_beam_boundaries

    def compute_split_boundary(self, average_solar_gain_array: np.ndarray) -> list[int]:
        """
        Compute the split boundary for an SP dual-beam image.

        The split boundary is a transition region in the middle of the spectral axis between the two beams
        and is not used for processing.

        Parameters
        ----------
        average_solar_gain_array
            An average solar gain array over the full ROI odf the detector

        Returns
        -------
        list[region_start, region_end]
        """
        spectral_center = average_solar_gain_array.shape[1] // 2
        transition_region_size = round(
            average_solar_gain_array.shape[1]
            * self.parameters.beam_boundaries_sp_beam_transition_region_size_fraction
        )

        split_boundary = [
            spectral_center - transition_region_size,
            spectral_center + transition_region_size,
        ]
        return split_boundary

    def compute_offset(self, beam_1: np.ndarray, beam_2: np.ndarray) -> list[int]:
        """
        Higher-level helper function to compute the (x, y) offset between beams.

        Parameters
        ----------
        beam_1
            The beam_1 image array
        beam_2
            The beam_2 image array

        Returns
        -------
        [x, y]
            integer pixel offset between beams along eacj axis
        """
        raw_spatial_shift = self.shift_measurements_compute_shift_along_axis(
            SPATIAL, beam_1, beam_2, upsample_factor=10
        )
        raw_spectral_shift = self.shift_measurements_compute_shift_along_axis(
            SPECTRAL, beam_1, beam_2, upsample_factor=10
        )
        # Round these values to the nearest integer.
        # When rounding up (to a larger abs value), round away from zero
        spatial_shift = int(math.copysign(round(abs(raw_spatial_shift)), raw_spatial_shift))
        spectral_shift = int(math.copysign(round(abs(raw_spectral_shift)), raw_spectral_shift))
        shift = [spectral_shift, spatial_shift]
        logger.info(f"Offset for beam 2 relative to beam 1, [SPECTRAL, SPATIAL] = {shift}")
        return shift

    def compute_shared_boundaries_from_overlapping_beams(
        self,
        boundaries: list[BeamBoundary],
        spectral_shift: int,
        spatial_shift: int,
    ) -> list[BeamBoundary]:
        """
        Adjust the boundaries of each beam to align the beams based on the input shift parameters.

        The shift values represent the measured shift of beam 2 relative to beam 1
        A negative shift means that beam 2 is shifted to either to the left of, or below, beam 1, depending
        on the particular axis involved, and must be shifted to the right, or up, to align the images.
        Conversely, a positive shift means that beam 2 is shifted to the right of, or above, beam 1 and
        must be shifted to the left, or down, to align the images. The images must also be cropped along
        each axis as well, so that both images have the same dimensions and represent the same spectral and
        spatial region.
        Note: we are computing and shifting to integer pixel values here solely for the purpose of determining
        the beam boundaries. We will compute sub-pixel adjustments later in the geometric task.

        Parameters
        ----------
        boundaries
            The boundaries of the illuminated regions of each beam.

        spectral_shift
            The shift required to align the two beam images along the spectral (horizontal or x) axis

        spatial_shift
            The shift required to align the two beam images along the spatial (vertical or y) axis

        Returns
        -------
        [beam_1_boundaries, beam_2_boundaries]
            A list of BeamBoundary objects representing the final beam boundaries
        """
        # These values are relative to the images AFTER they have been split, based on the illumination boundaries
        (
            beam_1_spatial_min,
            beam_1_spatial_max,
            beam_1_spectral_min,
            beam_1_spectral_max,
        ) = boundaries[0].beam_boundaries
        (
            beam_2_spatial_min,
            beam_2_spatial_max,
            beam_2_spectral_min,
            beam_2_spectral_max,
        ) = boundaries[1].beam_boundaries

        # Now adjust these values to align the beams based on the shift parameters
        (
            beam_1_spectral_min_new,
            beam_1_spectral_max_new,
            beam_2_spectral_min_new,
            beam_2_spectral_max_new,
        ) = self.adjust_boundaries(
            beam_1_spectral_min,
            beam_1_spectral_max,
            beam_2_spectral_min,
            beam_2_spectral_max,
            spectral_shift,
        )
        (
            beam_1_spatial_min_new,
            beam_1_spatial_max_new,
            beam_2_spatial_min_new,
            beam_2_spatial_max_new,
        ) = self.adjust_boundaries(
            beam_1_spatial_min,
            beam_1_spatial_max,
            beam_2_spatial_min,
            beam_2_spatial_max,
            spatial_shift,
        )

        # Now the beams are aligned, and we must translate the boundaries back to
        # the original dual beam image. This impacts only the beam 2 spectral boundaries
        beam_2_spectral_min_new += self.split_boundary[1]
        beam_2_spectral_max_new += self.split_boundary[1]

        beam_1_boundaries = BeamBoundary(
            beam_1_spatial_min_new,
            beam_1_spatial_max_new,
            beam_1_spectral_min_new,
            beam_1_spectral_max_new,
        )
        beam_2_boundaries = BeamBoundary(
            beam_2_spatial_min_new,
            beam_2_spatial_max_new,
            beam_2_spectral_min_new,
            beam_2_spectral_max_new,
        )

        logger.info(f"{beam_1_boundaries = }")
        logger.info(f"{beam_2_boundaries = }")

        # NB: The upper bounds are exclusive, ready to be used in array slicing
        return [beam_1_boundaries, beam_2_boundaries]

    @staticmethod
    def adjust_boundaries(
        b1_curr_min, b1_curr_max, b2_curr_min, b2_curr_max: int, shift: int
    ) -> tuple[int, ...]:
        """
        Adjust the beam boundaries along an axis based on the shift required to align them.

        The resulting boundaries will have the same dimensions (max - min) after the adjustment.

        Parameters
        ----------
        b1_curr_min
            The current minimum index for beam 1 on this axis
        b1_curr_max
            The current maximum index for beam 1 on this axis
        b2_curr_min
            The current minimum index for beam 2 on this axis
        b2_curr_max
            The current maximum index for beam 2 on this axis
        shift
            The amount beam 2 must be shifted to align to beam 1 on this axis
        Returns
        -------
        A tuple containing the adjusted boundaries for this axis.

        """
        if shift < 0:
            beam_1_new_min = b1_curr_min - shift
            beam_2_new_min = b2_curr_min
            beam_1_new_max = b1_curr_max
            beam_2_new_max = b2_curr_max + shift

        else:
            beam_1_new_min = b1_curr_min
            beam_2_new_min = b2_curr_min + shift
            beam_1_new_max = b1_curr_max - shift
            beam_2_new_max = b2_curr_max

        # Now trim where needed to make both the same size
        beam_1_extent = beam_1_new_max - beam_1_new_min
        beam_2_extent = beam_2_new_max - beam_2_new_min
        new_extent = min(beam_1_extent, beam_2_extent)
        beam_1_new_max = beam_1_new_min + new_extent
        beam_2_new_max = beam_2_new_min + new_extent
        return beam_1_new_min, beam_1_new_max, beam_2_new_min, beam_2_new_max
