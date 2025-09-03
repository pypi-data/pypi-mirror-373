"""Helper for CRYO-Nirsp array corrections."""

from collections.abc import Generator
from collections.abc import Iterable

import numpy as np
import scipy.ndimage as spnd
from dkist_processing_math.transform import affine_transform_arrays
from dkist_processing_math.transform import rotate_arrays_about_point


class CorrectionsMixin:
    """Mixin to provide support for various array corrections used by the workflow tasks."""

    @staticmethod
    def corrections_correct_geometry(
        arrays: Iterable[np.ndarray] | np.ndarray,
        shift: np.ndarray = np.zeros(2),
        angle: float = 0.0,
    ) -> Generator[np.ndarray, None, None]:
        """
        Shift and then rotate data.

        It applies the inverse of the given shift and angle.

        Parameters
        ----------
        arrays
            2D array(s) containing the data for the un-shifted beam

        shift
            The measured shift offset in the spectral dimension
            between beams or between modulator states in a single beam.

        angle
            The angle between the slit and pixel axes.

        Returns
        -------
        Generator
            2D array(s) containing the data of the rotated and shifted beam
        """
        arrays = [arrays] if isinstance(arrays, np.ndarray) else arrays
        for array in arrays:
            # Need to recast type to fix endianness issue caused by `fits`
            array = array.astype(np.float64)
            array[np.where(array == np.inf)] = np.max(array[np.isfinite(array)])
            array[np.where(array == -np.inf)] = np.min(array[np.isfinite(array)])
            array[np.isnan(array)] = np.nanmedian(array)
            translated = affine_transform_arrays(array, translation=-shift, mode="edge", order=1)
            # rotate_arrays_about_point rotates the wrong way, so no negative sign here
            yield next(rotate_arrays_about_point(translated, angle=angle, mode="edge", order=1))

    @staticmethod
    def corrections_distort_geometry(
        arrays: Iterable[np.ndarray] | np.ndarray,
        shift: np.ndarray = np.zeros(2),
        angle: float = 0.0,
    ) -> Generator[np.ndarray, None, None]:
        """
        Rotate and then shift data.

        It applies the inverse of the given shift and angle.

        Parameters
        ----------
        arrays
            2D array(s) containing the data for the un-shifted beam

        shift
            The measured shift offset in the spectral dimension
            between beams or between modulator states in a single beam.

        angle
            The angle between the slit and pixel axes.

        Returns
        -------
        Generator
            2D array(s) containing the data of the rotated and shifted beam
        """
        arrays = [arrays] if isinstance(arrays, np.ndarray) else arrays
        for array in arrays:
            # Need to recast type to fix endianness issue caused by `fits`
            array = array.astype(np.float64)
            array[np.where(array == np.inf)] = np.max(array[np.isfinite(array)])
            array[np.where(array == -np.inf)] = np.min(array[np.isfinite(array)])
            array[np.isnan(array)] = np.nanmedian(array)
            # rotate_arrays_about_point rotates the wrong way, so no negative sign here
            rotated = rotate_arrays_about_point(array, angle=angle, mode="edge")
            yield next(affine_transform_arrays(rotated, translation=-shift, mode="edge"))

    @staticmethod
    def corrections_remove_spec_shifts(
        arrays: Iterable[np.ndarray] | np.ndarray, spec_shift: np.ndarray
    ) -> Generator[np.ndarray, None, None]:
        """
        Remove spectral curvature.

        This is a pretty simple function that simply undoes the computed spectral shifts.

        Parameters
        ----------
        arrays
            2D array(s) containing the data for the un-distorted beam

        spec_shift : np.ndarray
            Array with shape (X), where X is the number of pixels in the spatial dimension.
            This dimension gives the spectral shift.

        Returns
        -------
        Generator
            2D array(s) containing the data of the corrected beam

        """
        arrays = [arrays] if isinstance(arrays, np.ndarray) else arrays
        for array in arrays:
            numx = array.shape[0]
            array_output = np.zeros(array.shape)
            for j in range(numx):
                array_output[j, :] = spnd.shift(array[j, :], -spec_shift[j], mode="nearest")
            yield array_output

    def corrections_correct_bad_pixels(
        self,
        array_to_fix: np.ndarray,
        bad_pixel_map: np.ndarray,
    ) -> np.ndarray:
        """
        Correct bad pixels in an array using a median filter.

        Corrects only the bad pixels identified by the bad pixel map.

        If enough pixels are found to suggest readout errors (> a given fraction of the array),
        a global replacement value is used instead.

        Parameters
        ----------
        array_to_fix
            The array to be corrected

        bad_pixel_map
            The bad_pixel_map to use for the correction
            An array of zeros with bad pixel locations set to 1

        Returns
        -------
        ndarray
            The corrected array
        """
        bad_pixel_fraction = np.sum(bad_pixel_map) / bad_pixel_map.size
        if bad_pixel_fraction > self.parameters.corrections_bad_pixel_fraction_threshold:
            global_median = np.nanmedian(array_to_fix)
            array_to_fix[bad_pixel_map == 1] = global_median
            return array_to_fix

        kernel_size = self.parameters.corrections_bad_pixel_median_filter_size
        half_kernel_size = kernel_size // 2

        masked_array = np.ma.array(array_to_fix, mask=bad_pixel_map)

        y_locs, x_locs = np.nonzero(bad_pixel_map)
        num_y = bad_pixel_map.shape[0]
        num_x = bad_pixel_map.shape[1]
        for x, y in zip(x_locs, y_locs):
            y_slice = slice(max(y - half_kernel_size, 0), min(y + half_kernel_size + 1, num_y))
            x_slice = slice(max(x - half_kernel_size, 0), min(x + half_kernel_size + 1, num_x))

            if self.constants.arm_id == "SP":
                # Only compute median in spatial dimension so we don't blur things spectrally
                med = np.ma.median(masked_array[y_slice, x])
            else:
                med = np.ma.median(masked_array[y_slice, x_slice])

            masked_array[y, x] = med

        return masked_array.data
