CI L1 Science Calibration
=========================

Introduction
------------

The `~dkist_processing_cryonirsp.tasks.ci_science` module takes L0 input science frames and fully calibrates
them into L1 science products. This page describes the basic steps in this processes as well as important
features of the Cryo-NIRSP Context Imager (CI) algorithm that may not be obvious.

Important Features
------------------

Pixel Units
^^^^^^^^^^^

The gain arrays used to correct science data are *not* normalized; they retain their original input values.
As a result, pixel values in the L1 data will be normalized to the average solar signal at disk center on the day calibrations
were acquired (usually the same day as science acquisition). Note that this is **NOT** intended to be an accurate photometric calibration.

L1 Coordinate System
^^^^^^^^^^^^^^^^^^^^

The final step of the science pipeline places L1 data into a coordinate frame that matches the coordinates used by
SDO/HMI and HINDOE-SP. Namely, -Q and +Q will be aligned parallel and perpendicular to the central meridian of the Sun,
respectively.

Algorithm
---------

Input CI science data is processed into L1 science data via the following steps:


#.  Dark signals are subtracted from linearized input data.

#.  :doc:`Bad Pixel correction <bad_pixel_calibration>` is done.

#.  A solar gain calibration frame is divided from the data.

#.  If data is polarimetric, demodulation matricies are applied.

#.  If data is polarimetric, the Telescope Polarization is removed. This removes the polarization effects of all DKIST mirrors upstream
    of Cryo-NIRSP. This step also includes the rotation into the coordinate frame described above.
