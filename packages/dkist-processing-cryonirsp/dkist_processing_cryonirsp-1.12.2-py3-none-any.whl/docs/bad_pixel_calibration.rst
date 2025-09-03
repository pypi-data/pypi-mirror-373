Bad Pixel Calibration
============================

Introduction
------------

Both of the Cryo-NIRSP instrument cameras are known to have significant numbers of bad pixels.
The effects of these are made worse by the linearization algorithm, which can force some pixels
to be exactly zero. The algorithm described below is used to identify bad pixels and create a map
of their locations. The map is an integer array of the same size as the camera output array, with
zeros for pixels that are good and ones for the pixels that are bad.

The Bad Pixel Map Algorithm
------------------------------

Compute Average Solar Gain Image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First we will compute an average solar gain image. The solar gain is used because it has high flux
and the beam illumination pattern is the same as during normal observing.

Smooth the Average Gain Image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We can remove the effects of any bad pixels by smoothing the average gain image using a median filter method,
filtering only along the spatial axis of the slit for SP data so as to not broaden the spectral lines, and
filtering along both the spatial and spectral axes for CI data. After the gain image has been smoothed,
the bad pixel areas should no longer be visible.

Threshold the Difference Image to Find Bad Pixels
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Next, we subtract the smoothed image from the average gain image. Doing this allows us to identify all
pixels in the difference image whose absolute value is larger than a set threshold value times the standard
deviation of the average image (i.e., a difference larger than N standard deviations of the original image is
considered a bad pixel). The threshold value is a pipeline settable parameter and was derived
empirically. With a too-low threshold, we start to pick up the solar spectrum in the bad pixel image. With a
too-large threshold, we start to miss bad pixels. Moreover, we currently use bad pixel corrections only for the
gain images and not for the observe images, so any potential impacts are limited. This may change in the
future.

Apply Bad Pixel Map
^^^^^^^^^^^^^^^^^^^

This bad pixel map is then applied to the lamp gain and solar gain by replacing the identified
bad pixels with the median value of the input image over a specified region. This prevents the
gain image from causing “hot” or “cold” pixels in the resulting gain corrected input images.
