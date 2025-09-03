"""Mixin to support array shift calculations."""

import math
from dataclasses import dataclass

import numpy as np
import skimage.registration as skir
from dkist_service_configuration.logging import logger

SPATIAL = "SPATIAL"
SPECTRAL = "SPECTRAL"
ALLOWABLE_AXES = SPATIAL, SPECTRAL


@dataclass
class AxisParams:
    """
    Dataclass to support shift computations along an axis.

    Parameters
    ----------
    axis
        The axis along which a shift is to be computed
    long_axis
        The axis number that represents the long axis of the strip
    axis_0_size
        The size of the numpy 0 axis
    axis_1_size:
        The size of the numpy 1 axis
    axis_0_offset
        The offset from the center of the 0 axis about which to align the center of the strip
    axis_1_offset
        The offset from the center of the 1 axis about which to align the center of the strip
    """

    axis: str
    long_axis: int
    axis_0_size: int
    axis_1_size: int
    axis_0_offset: int = 0
    axis_1_offset: int = 0


class ShiftMeasurementsMixin:
    """Methods to support array shift computations along a specified axis."""

    def shift_measurements_compute_shift_along_axis(
        self,
        axis: str,
        array_1: np.ndarray,
        array_2: np.ndarray,
        array_1_offset: tuple[int, int] = (0, 0),
        array_2_offset: tuple[int, int] = (0, 0),
        # Use no upsampling unless specified
        upsample_factor: int = 1,
    ) -> float:
        """
        Compute the relative shift between two images along a specified axis.

        This method computes the relative shift of two images along an axis by extracting
        two long, narrow strips, one from each image, computing the median along the narrow
        axis, and then correlating the two signals to find the relative shift between them.

        The long axis of the strip is the axis along which the shift measurement is to be made.
        The narrow axis is the opposite axis (orthogonal axis) from the measurement axis.

        Parameters
        ----------
        axis
            The axis along which to measure the shift, SPATIAL or SPECTRAL
        array_1
            The reference, or non-moving array
        array_2
            The array whose shift is to be measured, or the moving array
        array_1_offset
            The offsets to be applied to each axis of array_1 when defining the strip slice
        array_2_offset
            The offsets to be applied to each axis of array_2 when defining the strip slice
        upsample_factor
            The upsample factor to be used when computing the correlation of the two signals.

        Returns
        -------
        shift
            The measured displacement of array_2 relative to array_1
        """
        # "axis" is the axis along which we compute the gradient
        # SPECTRAL means along the spectral axis, axis 1 in numpy, horizontal axis
        # SPATIAL means along the spatial axis, axis 0 in numpy, vertical axis

        array_1_axis_params = self.shift_measurements_get_axis_params(
            axis, array_1.shape, array_1_offset
        )
        array_2_axis_params = self.shift_measurements_get_axis_params(
            axis, array_2.shape, array_2_offset
        )

        array_1_axis_0_slice, array_1_axis_1_slice = self.shift_measurements_get_strip_slices(
            array_1_axis_params, array_num=1
        )
        array_2_axis_0_slice, array_2_axis_1_slice = self.shift_measurements_get_strip_slices(
            array_2_axis_params, array_num=2
        )

        # Make sure long axis slices start and end at same point.
        long_axis = array_1_axis_params.long_axis
        if long_axis == 0:
            new_min = max(array_1_axis_0_slice.start, array_1_axis_0_slice.start)
            new_max = min(array_1_axis_0_slice.stop, array_1_axis_0_slice.stop)
            long_axis_slice = slice(new_min, new_max)
            array_1_strip = array_1[long_axis_slice, array_1_axis_1_slice]
            array_2_strip = array_2[long_axis_slice, array_2_axis_1_slice]
        else:
            new_min = max(array_1_axis_1_slice.start, array_1_axis_1_slice.start)
            new_max = min(array_1_axis_1_slice.stop, array_1_axis_1_slice.stop)
            long_axis_slice = slice(new_min, new_max)
            array_1_strip = array_1[array_1_axis_0_slice, long_axis_slice]
            array_2_strip = array_2[array_2_axis_0_slice, long_axis_slice]

        array_1_gradient = self.shift_measurements_compute_gradient(
            array_1_strip, axis=array_1_axis_params.long_axis
        )
        array_2_gradient = self.shift_measurements_compute_gradient(
            array_2_strip, axis=array_2_axis_params.long_axis
        )

        if axis == SPECTRAL:
            # Chop 10% off of the edges of the spectra to remove known edge effects before determining shift.
            tenth_of_length = array_1_gradient.shape[0] // 10
            array_1_gradient = array_1_gradient[tenth_of_length:-tenth_of_length]
            array_2_gradient = array_2_gradient[tenth_of_length:-tenth_of_length]

        # Correlate the gradient signals to get the shift of array 2 relative to array 1
        shift_array, error, phasediff = skir.phase_cross_correlation(
            reference_image=array_1_gradient,
            moving_image=array_2_gradient,
            upsample_factor=upsample_factor,
        )
        # Flip the sign to convert from correction to measurement.
        shift = -shift_array[0]
        logger.info(f"Measured shift of array 2 relative to array 1 in {axis} axis = {shift}")

        return shift

    @staticmethod
    def shift_measurements_get_axis_params(
        axis: str, array_shape: tuple[int, ...], offset: tuple[int, ...]
    ) -> AxisParams:
        """
        Populate an AxisParams dataclass with information about this axis.

        Parameters
        ----------
        axis
            The axis along which the measurement is to be made, SPATIAL or SPECTRAL
        array_shape
            The numpy shape tuple for the array
        offset
            The offset along each axis where the extracted strip is to be centered

        Returns
        -------
        AxisParams
            An AxisParams object, populated for the requested array and axis.
        """
        long_axis = None
        if axis in ALLOWABLE_AXES:
            if axis == SPECTRAL:
                long_axis = 1
            elif axis == SPATIAL:
                long_axis = 0
            return AxisParams(
                axis=axis,
                long_axis=long_axis,
                axis_0_size=array_shape[0],
                axis_1_size=array_shape[1],
                axis_0_offset=offset[0],
                axis_1_offset=offset[1],
            )
        raise ValueError(f"Unknown value for {axis = }, allowable values are {ALLOWABLE_AXES}")

    def shift_measurements_get_strip_slices(
        self, axis_params: AxisParams, array_num: int
    ) -> tuple[slice, slice]:
        """
        Return the axis slices for the desired strip based on the AxisParams object.

        Parameters
        ----------
        axis_params
            The AxisParams object defining the desired strip

        Returns
        -------
        slice, slice
            A tuple of slice objects for extracting the desired srtip from the array
        """
        long_axis_fraction = self.parameters.geo_strip_long_axis_size_fraction
        short_axis_fraction = self.parameters.geo_strip_short_axis_size_fraction

        if axis_params.axis == SPECTRAL:
            axis_0_fraction = short_axis_fraction
            axis_1_fraction = long_axis_fraction
        else:
            axis_0_fraction = long_axis_fraction
            axis_1_fraction = short_axis_fraction

        # Compute the strip sizes
        axis_0_strip_size = math.ceil(axis_0_fraction * axis_params.axis_0_size)
        if not axis_0_strip_size % 2 == 0:
            axis_0_strip_size += 1
        axis_1_strip_size = math.ceil(axis_1_fraction * axis_params.axis_1_size)
        if not axis_1_strip_size % 2 == 0:
            axis_1_strip_size += 1

        # compute the slices from the strip sizes
        axis_0_slice_idx = (
            np.array([-axis_0_strip_size, axis_0_strip_size]) + axis_params.axis_0_size
        ) // 2 + axis_params.axis_0_offset
        axis_1_slice_idx = (
            np.array([-axis_1_strip_size, axis_1_strip_size]) + axis_params.axis_1_size
        ) // 2 + axis_params.axis_1_offset

        axis_0_slice = slice(*axis_0_slice_idx)
        axis_1_slice = slice(*axis_1_slice_idx)

        logger.info(
            f"Slice results: array {array_num}, axis: {axis_params.axis}, axis 0: {axis_0_slice}, axis 1: {axis_1_slice}"
        )

        return axis_0_slice, axis_1_slice

    def shift_measurements_compute_gradient(self, strip: np.ndarray, axis: int) -> np.ndarray:
        """
        Compute the gradient of the strip.

        This method computes a normalized difference array (essentially a gradient) along the
        long axis of the strip. The difference array is computed by subtracting a shifted version
        of the strip along a desired axis. The shift is accomplished using the np.roll() method.
        The difference is normalized by dividing by the sum of the strip and the shifted strip.

        The gradient computation looks like this::

            numerator = np.roll(strip, roll_amount, axis=axis) - np.roll(strip, -roll_amount, axis=axis)
            denominator = np.roll(strip, roll_amount, axis=axis) + np.roll(strip, -roll_amount, axis=axis)
            gradient = numerator / denominator

        Finally, the ends are trimmed to remove edge effects from the partial overlap.

        Parameters
        ----------
        strip
            The array strip to be processed
        axis
            The numpy axis along which the difference is to be computed.

        Returns
        -------
        The normalized difference array

        """
        roll_amount = self.parameters.geo_long_axis_gradient_displacement
        numerator = np.roll(strip, roll_amount, axis=axis) - np.roll(strip, -roll_amount, axis=axis)
        denominator = np.roll(strip, roll_amount, axis=axis) + np.roll(
            strip, -roll_amount, axis=axis
        )
        gradient = numerator / denominator
        # Take the median along the opposite axis from which we compute the gradient.
        gradient_median = np.nanmedian(gradient, axis=self.shift_measurements_opposite_axis(axis))
        # Trim the ends by twice the roll amount to remove edge effects resulting from the edge wrap.
        trim_amount = 2 * roll_amount
        trimmed_gradient = gradient_median[trim_amount:-trim_amount]
        return trimmed_gradient

    @staticmethod
    def shift_measurements_opposite_axis(current_axis: int) -> int:
        """
        Return the opposite axis relative to the one in use.

        We assume a 2D coordinate system in numpy, with axes 0 and 1
        This method returns the "other" or "opposite" axis from the one being
        used, which is the current_axis.

        Truth table::

            current axis   opposite axis
                  0              1
                  1              0

        The bitwise exclusive or (XOR)  operator '^' is used to flip the axis::

            0 ^ 1 = 1
            1 ^ 1 = 0
            opposite_axis = current_axis ^ 1

        Parameters
        ----------
        current_axis

        Returns
        -------
        int representing the opposite axis
        """
        return current_axis ^ 1
