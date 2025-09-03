Beam Boundary Computation
============================

Introduction
------------

Raw Cryo-NIRSP frames are not fully illuminated; in some areas, there is no illumination at all.
These areas should not be used for science processing and
must be accounted for. Moreover, the illuminated region(s) will change slightly depending
on the optical alignment of the instrument. Hence, we cannot use a particular set
of beam boundary constants from which to extract the illuminated regions. Instead we need to
compute these regions as part of the calibration process.

The Beam Boundary Algorithm
------------------------------

The basic idea of the algorithm is to use an average solar gain image and apply a segmentation
algorithm to it that separates the image into illuminated pixels and non-illuminated pixels.
(Note: We use solar gain images because they have larger flux than the lamp gain images
and the lamp gain images do not have the same illumination pattern as the solar
gain images. Therefore, in order to make sure the beam boundaries match the on-sky data,
and are as correct as they can be, we must use solar gain images. We only use a single frame because the
illuminated portion of the CCD is always constant.)
The segmentation must be robust enough to have all pixels within a well defined outer boundary
considered to be illuminated. This is sufficient to extract an illuminated region from a single
beam for the Context Imager (CI). For the Spectropolarimeter (SP), however, we need to identify
the separate beam regions and perform an initial alignment prior to computing the final individual
beam boundaries.

Compute the Average Solar Gain Image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We start by computing an average solar gain image. Because we are interested only in identifying
the regions of the sensor that are illuminated, we do not need to perform any dark correction.
Simply averaging the input solar gain images is sufficient.


Correct Bad Pixels Using the Median Filter
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The effects of the bad pixels must be corrected, otherwise they might be mistaken for non-illuminated
regions. We correct these bad pixels using the :doc:`bad pixel calibration algorithm <bad_pixel_calibration>`
and by applying a median filter to only those pixels that are flagged as bad. We use the masked array feature
of numpy to achieve this filtering. For the SP, the correction algorithm is applied only in the spatial
direction along the slit. For the CI, it is applied along both axes. For this application, the
difference does not matter, as all we are doing is identifying illuminated pixels. However, later on when
the solar gain array is computed, the correction must not broaden the spectral lines and so the restriction
is important.


Segment the Image Into Illuminated and Non-Illuminated Regions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Next we smooth the entire array so the image segmentation algorithm does not recognize the absorption
lines as part of the non-illuminated region. The smoothed solar gain array is then used as the input to an
image segmentation algorithm. The `Scikit Image threshold minimum <https://scikit-image.org/docs/stable/api/skimage.filters.html#skimage.filters.threshold_minimum>`_
method is used to find the threshold between light and dark and this threshold is then
used to generate a boolean map describing which pixels are illuminated (True) and which pixels are non-illuminated
(False). However, this map cannot be used to easily extract illuminated regions because it is not guaranteed to be
contiguous. Ideally, we would like to be able to identify a slice that can be used to extract the illuminated
region as a rectangular array.


Split Into Two Separate beam Images
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now that we know the illuminated boundaries, we can identify and extract the largest inscribed rectangular
region within the illuminated map. This is done using the `largestinteriorrectangle package <https://pypi.org/project/largestinteriorrectangle/>`_.
We split the image into two beam images, avoiding a 10% spectral region
surrounding the beam boundary in the middle of the image.

Compute Relative Horizontal Shift of Right Beam to Left Beam
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There is a relative shift between these two images, so we need to determine that shift and compute the
boundaries of each so that they overlap properly to within a single horizontal pixel. Note that the rotational
differences and any additional shifts required to align the images are computed later as part of the geometric
calibration. The horizontal shift of the right beam relative to the left is computed using the
`Scikit Image phase cross correlation <https://scikit-image.org/docs/stable/api/skimage.registration.html#skimage.registration.phase_cross_correlation>`_
method.

Compute Beam Boundaries for Identical Size Overlapping Regions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The final step is to use the shift to adjust the boundaries of each beam image such that both images
have the same horizontal dimension and represent essentially the same spatial and spectral regions
(as mentioned above, final adjustments will come later in the geometric calibration). Moreover the beam
boundaries must be defined so that they represent slices into the original image and can then be used
later to extract each beam from any type of input image (dark, gain, polcal, observe).
