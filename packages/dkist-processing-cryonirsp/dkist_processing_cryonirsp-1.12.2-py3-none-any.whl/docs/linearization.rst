Linearization
=============

Introduction
------------

The Cryo-NIRSP camera has an H2RG detector, which has a non-linear response to light with
increasing exposure time. This can vary from pixel to pixel. Because of the non-linear response, the count
values at the final exposure do not accurately represent the light falling on the chip and therefore need to
be corrected. We call this correction ‘linearization’. During an exposure, the camera
reads out multiple frames and saves them while it continues to expose. The accumulated charge on the chip is
not erased when this happens, so they are referred to as Non-Destructive Readouts (NDRs). The NDRs are
saved at a pre-selected rate that is a fraction of the overall desired exposure time for a
complete NDR. A set of NDRs with exposure times varying from 0 to the final desired exposure time are
called a ramp. The linearization process reads all of the NDRs associated with a particular ramp and then
applies an algorithm to compute what the final count values at the desired exposure time should be if the
response of the detector was linear. Basically it takes the ramp set and "linearizes" it to produce a single
NDR that has the correct counts at each pixel.

A ramp can have many frames (anywhere from 10 to as much as 100, or more), and the linearization
algorithm is agnostic to just about everything except the final exposure time. So after linearization, we
have over 10x fewer frames to process, and the pipeline proceeds as though the linearized frames are raw input frames.

The Linearization Algorithm
---------------------------

The Algorithm
^^^^^^^^^^^^^

First, we identify all NDRs from a single exposure of the Cryo-NIRSP cameras (i.e., a ramp set). A ramp is
identified as all the files having the same DATE-OBS value. Note: If a ramp set contains only a single frame,
it is discarded.

Next, we need to identify the NDRs that fall in the “linear” portion of the chip response. These are those
NDRs whose pixel value is below a pre-computed threshold value. I.e., the threshold values define the upper-limit
of the linear response of each pixel.

Then, we linearize this ramp set by normalizing the measured raw flux by the final ramp exposure time of the ramp set.
Essentially, this removes the non-linear response of each pixel in the array. The resulting ramp set is essentially
linear in ADUs v exposure time.

Finally, we normalize the array by converting to counts per second and correct the counts for the Optical Density
filter used during observations.
