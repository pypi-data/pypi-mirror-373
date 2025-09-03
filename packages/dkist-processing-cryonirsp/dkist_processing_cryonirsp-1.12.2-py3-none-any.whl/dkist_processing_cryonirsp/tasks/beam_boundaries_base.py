"""CryoNIRSP compute beam boundary task."""

from abc import abstractmethod

import numpy as np
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_service_configuration.logging import logger
from largestinteriorrectangle import lir
from skimage import filters
from skimage.exposure import rescale_intensity
from skimage.morphology import disk
from skimage.util import img_as_ubyte

from dkist_processing_cryonirsp.codecs.fits import cryo_fits_array_decoder
from dkist_processing_cryonirsp.models.beam_boundaries import BeamBoundary
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import (
    CryonirspLinearizedFitsAccess,
)
from dkist_processing_cryonirsp.tasks.cryonirsp_base import CryonirspTaskBase

__all__ = ["BeamBoundariesCalibrationBase"]


class BeamBoundariesCalibrationBase(CryonirspTaskBase):
    """
    Task class for calculation of the beam boundaries for later use during calibration.

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
        Compute the beam boundaries by analyzing a set of solar gain images.

        Steps:
        1. Compute the average gain image
        2. Correct any bad pixels
        3. Smooth the image using a median filter
        4. Split the beam along the horizontal axis (SP only)
        5. Use a bimodal threshold filter to segment the image into illuminated and non-illuminated regions
        6. Compute the boundaries of the illuminated region
        7. Extract the illuminated portion of the beam images
        8. Find the horizontal shift between the two images
        9. Identify the boundaries of the overlap
        10. Save the boundaries as a fits file (json?)

        Returns
        -------
        None

        """
        # Step 1:
        with self.apm_processing_step(f"Compute average solar gain image"):
            average_solar_gain_array = self.compute_average_gain_array()

        # Step 2:
        with self.apm_task_step(f"Retrieve bad pixel map"):
            bad_pixel_map = next(
                self.read(
                    tags=[CryonirspTag.intermediate_frame(), CryonirspTag.task_bad_pixel_map()],
                    decoder=cryo_fits_array_decoder,
                )
            )
            corrected_solar_gain_array = self.corrections_correct_bad_pixels(
                average_solar_gain_array, bad_pixel_map
            )

        # Step 3
        with self.apm_processing_step(f"Smooth the array to get good segmentation"):
            smoothed_solar_gain_array = self.smooth_gain_array(corrected_solar_gain_array)

        # Step 4
        with self.apm_processing_step(f"Split the beam horizontally"):
            split_beams = self.split_beams(smoothed_solar_gain_array)

        # Step 5
        with self.apm_processing_step(
            f"Segment the beams into illuminated and non-illuminated pixels"
        ):
            segmented_beams = self.segment_arrays(split_beams)

        # Step 6:
        with self.apm_processing_step(
            f"Compute the inscribed rectangular extents of the illuminated portions of the sensor"
        ):
            illuminated_boundaries = self.compute_boundaries_of_beam_illumination_regions(
                segmented_beams
            )

        # Steps 7 - 9:
        with self.apm_processing_step(f"Compute the boundaries of the illuminated beams"):
            split_beams_float = [split_beam.astype(float) for split_beam in split_beams]
            boundaries = self.compute_final_beam_boundaries(
                split_beams_float, illuminated_boundaries
            )

        # Step 10:
        with self.apm_writing_step("Writing beam boundaries"):
            for beam, bounds in enumerate(boundaries, start=1):
                self.write(
                    data=bounds.beam_boundaries_array,
                    tags=[
                        CryonirspTag.intermediate_frame(beam=beam),
                        CryonirspTag.task_beam_boundaries(),
                    ],
                    encoder=fits_array_encoder,
                )

    def compute_average_gain_array(self) -> np.ndarray:
        """
        Compute an average of uncorrected solar gain arrays.

        We are computing the overall illumination pattern for both beams simultaneously,
        so no dark correction is required and no beam splitting is used at this point.
        Solar gain images are used because they have larger flux than the lamp gain images
        and the lamp gain images do not have the same illumination pattern as the solar
        gain images.

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

    def smooth_gain_array(self, array: np.ndarray) -> np.ndarray:
        """
        Smooth the input array with morphological filtering using a disk shape.

        The array is smoothed to help eliminate artifacts in the image segmentation step.

        Parameters
        ----------
        array
            The input array to be smoothed

        Returns
        -------
        The smoothed output array
        """
        # skimage.filters requires ubyte arrays and float->ubyte conversion only works with float in range [-1, 1]
        norm_gain = img_as_ubyte(rescale_intensity(array, out_range=(0, 1.0)))

        disk_size = self.parameters.beam_boundaries_smoothing_disk_size
        norm_gain = filters.rank.median(norm_gain, disk(disk_size))
        return norm_gain

    @abstractmethod
    def split_beams(self, input_array: np.ndarray) -> list[np.ndarray]:
        """
        Split the beams along the horizontal axis.

        We use an abstract method so that the processing sequence is the same for both SP and CI
        although the processing steps may be different.

        Parameters
        ----------
        input_array
            The array to be split

        Returns
        -------
        [array, ...]
            A list of arrays after the split
        """
        pass

    @staticmethod
    def segment_arrays(arrays: list[np.ndarray]) -> list[np.ndarray]:
        """
        Segment the arrays into illuminated (True) and non-illuminated (False) regions.

        Parameters
        ----------
        arrays
            The arrays to be segmented

        Returns
        -------
        [array, ...]
            The boolean segmented output arrays
        """
        segmented_arrays = []
        for beam_num, beam_array in enumerate(arrays, start=1):
            thresh = filters.threshold_minimum(beam_array)
            logger.info(f"Segmentation threshold for beam {beam_num} = {thresh}")
            segmented_arrays.append((beam_array > thresh).astype(bool))
        return segmented_arrays

    def compute_boundaries_of_beam_illumination_regions(
        self, arrays: list[np.ndarray]
    ) -> list[BeamBoundary]:
        """
        Compute the rectangular boundaries describing the illuminated regions of the beam images.

        Parameters
        ----------
        arrays
            A list of segmented boolean arrays over which the boundaries are to be computed

        Returns
        -------
        [BeamBoundary, ...]
        A list of the BeamBoundary objects representing the illuminated region(s) of the beam image(s)
        """
        boundaries = []
        for beam, array in enumerate(arrays, start=1):
            # Find the largest interior rectangle that inscribes the illuminated region for this beam
            x_min, y_min, x_range, y_range = lir(array)
            # Compute the new image bounds, the maximums are exclusive and can be used in slices
            y_max = y_min + y_range
            x_max = x_min + x_range

            # Make sure all pixels are 1s
            if not np.all(array[y_min:y_max, x_min:x_max]):
                raise RuntimeError(
                    f"Unable to compute illuminated image boundaries for beam {beam}"
                )

            boundaries.append(
                BeamBoundary(np.int64(y_min), np.int64(y_max), np.int64(x_min), np.int64(x_max))
            )

        return boundaries

    @abstractmethod
    def compute_final_beam_boundaries(
        self,
        smoothed_solar_gain_arrays: list[np.ndarray],
        illuminated_boundaries: list[BeamBoundary],
    ) -> list[BeamBoundary]:
        """
        Compute the final beam boundaries to be used when accessing individual beam images from the input dual-beam arrays.

        Parameters
        ----------
        smoothed_solar_gain_arrays
            Smoothed solar gain arrays to be used for coarsely aligning the individual beam images.
        illuminated_boundaries
            A list of BeamBoundary objects representing the illuminated regions of each beam image.

        Returns
        -------
        A list of BeamBoundary objects describing the final beam boundaries for each beam.
        """
        pass
