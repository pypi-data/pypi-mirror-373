Beam Angle Computation
============================

Introduction
------------

As part of the geometric calibration, the angular rotation of the slit relative to the image axes
must be computed and then corrected. There is no fiducial mark or hairline present in the Cryo-NIRSP
images, so some other method must be used. The angular rotation is derived from the lamp gain images using
the algorithm described below. It is described for only a single beam, but is equally applicable to use for both
beams.

The Beam Angle Algorithm
------------------------------

Compute Average Lamp Gain Image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We start by using the normalized lamp gain image that is computed as part of the lamp gain calibration.
The image has been corrected for bad pixels (hot or cold) using the bad pixel map derived from average
solar gain images (See :doc:`bad pixel calibration <bad_pixel_calibration>`).

Compute the Normalized Spatial Gradient Image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The normalized lamp gain image contains some some faint horizontal (i.e. along the spectral axis) lines. These are the result of slight
imperfections in the slit and in the grating optics, and they can be used to derive the rotation of the slit axis
relative to the image axes. By computing a normalized spatial gradient along the spatial axis (along the slit),
we can enhance the faint horizontal lines to make them more pronounced. The gradient is computed by shifting the
image along the spatial axis in both the + and - directions, computing the difference of the two images, and
normalizing by the sum of the two at each pixel position. The resulting gradient image contains horizontal
lines that are more emphasized.

Compute the Angular Rotation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Next we identify two long, narrow regions, or strips along the spatial axis. The length of each of the strips
is one half of the slit length in pixels and they are centered about the mid-point of the length of the slit
as seen on the sensor.

We then compute the median value along the spectral axis (or rows). This condenses each strip into a 1D signal
that represents the static fluctuations in the image along the spatial axis. The next step is to compute the
cross correlation of the right signal relative to the left signal (the reference). The result is the measured
shift of the right signal relative to the left. Using the measured shift between the signals and the known
separation along the spectral axis between the midpoints of the strips, we can then compute the angular
rotation using a simple arc-tangent.

Correcting the Rotational Offset
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Finally, we can remove this rotational offset. The slit axis is now aligned with the spatial axis of the image.
The angular rotation measured here using the lamp gain image is then used to correct all of the
observe images as part of the geometric corrections.
