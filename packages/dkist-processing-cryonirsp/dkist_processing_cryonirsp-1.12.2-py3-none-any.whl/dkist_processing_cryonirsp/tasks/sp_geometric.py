"""Cryo SP geometric task."""

import math

import numpy as np
import peakutils as pku
import scipy.ndimage as spnd
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_math.arithmetic import divide_arrays_by_array
from dkist_processing_math.arithmetic import subtract_array_from_arrays
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_service_configuration.logging import logger
from scipy.optimize import minimize

from dkist_processing_cryonirsp.codecs.fits import cryo_fits_array_decoder
from dkist_processing_cryonirsp.models.beam_boundaries import BeamBoundary
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import (
    CryonirspLinearizedFitsAccess,
)
from dkist_processing_cryonirsp.tasks.cryonirsp_base import CryonirspTaskBase
from dkist_processing_cryonirsp.tasks.mixin.shift_measurements import SPATIAL
from dkist_processing_cryonirsp.tasks.mixin.shift_measurements import SPECTRAL
from dkist_processing_cryonirsp.tasks.mixin.shift_measurements import ShiftMeasurementsMixin

__all__ = ["SPGeometricCalibration"]


class SPGeometricCalibration(CryonirspTaskBase, ShiftMeasurementsMixin):
    """Task class for computing the spectral geometry. Geometry is represented by three quantities.

      - angle - The angle (in radians) between slit hairlines and pixel axes. A one dimensional array with two elements- one for each beam.

      - beam offset - The [x, y] shift of beam 2 relative to beam 1 (the reference beam). Two beam offset values are computed.

      - spectral shift - The shift in the spectral dimension for each beam for every spatial position needed to "straighten" the spectra so a single wavelength is at the same pixel for all slit positions.Task class for computing the spectral geometry for a SP CryoNIRSP calibration run.

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
        Run method for the task.

        For each beam.

            - Gather dark corrected frames
            - Calculate spectral tilt (angle)
            - Remove spectral tilt
            - Using the angle corrected array, find the beam offset
            - Write beam offset
            - Calculate the spectral skew and curvature (spectral shifts)
            - Write the spectral skew and curvature


        Returns
        -------
        None

        """
        # The basic corrections are done outside the loop structure below as it makes these loops much
        # simpler than they would be otherwise. See the comments in do_basic_corrections for more details.
        with self.apm_processing_step("Basic corrections"):
            self.do_basic_corrections()

        for beam in range(1, self.constants.num_beams + 1):
            with self.apm_task_step(f"Generating geometric calibrations for {beam = }"):
                with self.apm_processing_step(f"Computing and writing angle for {beam = }"):
                    angle = self.compute_beam_angle(beam=beam)
                    self.write_angle(angle=angle, beam=beam)

                with self.apm_processing_step(f"Removing angle from {beam = }"):
                    angle_corr_array = self.remove_beam_angle(angle=angle, beam=beam)

                with self.apm_processing_step(f"Computing offset for {beam = }"):
                    beam_offset = self.compute_offset(
                        array=angle_corr_array,
                        beam=beam,
                    )
                    self.write_beam_offset(offset=beam_offset, beam=beam)

                with self.apm_processing_step(f"Removing offset for {beam = }"):
                    self.remove_beam_offset(
                        array=angle_corr_array,
                        offset=beam_offset,
                        beam=beam,
                    )

                with self.apm_processing_step(f"Computing spectral shifts for {beam = }"):
                    spec_shifts = self.compute_spectral_shifts(beam=beam)

                with self.apm_writing_step(f"Writing spectral shifts for {beam = }"):
                    self.write_spectral_shifts(shifts=spec_shifts, beam=beam)

        with self.apm_processing_step("Computing and logging quality metrics"):
            no_of_raw_geo_frames: int = self.scratch.count_all(
                tags=[
                    CryonirspTag.linearized_frame(),
                    CryonirspTag.task_solar_gain(),
                ],
            )

            self.quality_store_task_type_counts(
                task_type=TaskName.geometric.value, total_frames=no_of_raw_geo_frames
            )

    def basic_gain_corrected_data(self, beam: int) -> np.ndarray:
        """
        Get dark and lamp gain corrected data array for a single beam.

        Parameters
        ----------
        beam : int
            The current beam being processed

        Returns
        -------
        np.ndarray
            Dark corrected data array
        """
        array_generator = self.read(
            tags=[
                CryonirspTag.intermediate_frame(beam=beam),
                CryonirspTag.task("GC_BASIC_GAIN_CORRECTED"),
            ],
            decoder=cryo_fits_array_decoder,
        )
        return average_numpy_arrays(array_generator)

    def basic_dark_bp_corrected_data(self, beam: int) -> np.ndarray:
        """
        Get dark and bad pixel corrected data array for a single beam.

        Parameters
        ----------
        beam : int
            The current beam being processed

        Returns
        -------
        np.ndarray
            Dark and bad pixel corrected data array
        """
        array_generator = self.read(
            tags=[
                CryonirspTag.intermediate_frame(beam=beam),
                CryonirspTag.task("GC_BASIC_DARK_BP_CORRECTED"),
            ],
            decoder=cryo_fits_array_decoder,
        )
        return average_numpy_arrays(array_generator)

    def offset_corrected_data(self, beam: int) -> np.ndarray:
        """
        Array for a single beam that has been corrected for the x/y beam offset.

        Parameters
        ----------
        beam
            The current beam being processed

        Returns
        -------
        np.ndarray
            Offset corrected data array
        """
        array_generator = self.read(
            tags=[CryonirspTag.intermediate_frame(beam=beam), CryonirspTag.task("GC_OFFSET")],
            decoder=cryo_fits_array_decoder,
        )
        return average_numpy_arrays(array_generator)

    def do_basic_corrections(self):
        """Apply dark, bad pixel and lamp gain corrections to all data that will be used for Geometric Calibration."""
        # There is likely only a single exposure conditions tuple in the list, but we iterate over the list
        # in case there are multiple exposure conditions tuples. We also need a specific exposure conditions tag
        # to ensure we get the proper dark arrays to use in the correction.
        for beam in range(1, self.constants.num_beams + 1):
            beam_array = next(
                self.read(
                    tags=CryonirspTag.intermediate_beam_boundaries(beam=beam),
                    decoder=cryo_fits_array_decoder,
                )
            )
            beam_boundary = BeamBoundary(*beam_array)

            for exposure_conditions in self.constants.solar_gain_exposure_conditions_list:
                logger.info(f"Starting basic reductions for {exposure_conditions = } and {beam = }")
                try:
                    dark_array = next(
                        self.read(
                            tags=[
                                CryonirspTag.intermediate_frame(
                                    beam=beam, exposure_conditions=exposure_conditions
                                ),
                                CryonirspTag.task_dark(),
                            ],
                            decoder=cryo_fits_array_decoder,
                        )
                    )
                except StopIteration as e:
                    raise ValueError(f"No matching dark found for {exposure_conditions = }") from e

                lamp_gain_array = next(
                    self.read(
                        tags=[
                            CryonirspTag.intermediate_frame(beam=beam),
                            CryonirspTag.task_lamp_gain(),
                        ],
                        decoder=cryo_fits_array_decoder,
                    )
                )

                input_solar_arrays = self.read(
                    tags=[
                        CryonirspTag.linearized_frame(exposure_conditions=exposure_conditions),
                        CryonirspTag.task_solar_gain(),
                    ],
                    decoder=cryo_fits_array_decoder,
                    fits_access_class=CryonirspLinearizedFitsAccess,
                    beam_boundary=beam_boundary,
                )

                avg_solar_array = average_numpy_arrays(input_solar_arrays)

                dark_corrected_solar_array = next(
                    subtract_array_from_arrays(arrays=avg_solar_array, array_to_subtract=dark_array)
                )

                bad_pixel_map = next(
                    self.read(
                        tags=[CryonirspTag.intermediate_frame(), CryonirspTag.task_bad_pixel_map()],
                        decoder=cryo_fits_array_decoder,
                        beam_boundary=beam_boundary,
                    )
                )
                bad_pixel_corrected_array = self.corrections_correct_bad_pixels(
                    dark_corrected_solar_array, bad_pixel_map
                )
                logger.info(f"Writing bad pixel corrected data for {beam=}")
                self.write(
                    data=bad_pixel_corrected_array,
                    tags=[
                        CryonirspTag.intermediate_frame(beam=beam),
                        CryonirspTag.task("GC_BASIC_DARK_BP_CORRECTED"),
                    ],
                    encoder=fits_array_encoder,
                )
                gain_corrected_solar_array = next(
                    divide_arrays_by_array(bad_pixel_corrected_array, lamp_gain_array)
                )
                logger.info(f"Writing gain corrected data for {beam=}")
                self.write(
                    data=gain_corrected_solar_array,
                    tags=[
                        CryonirspTag.intermediate_frame(beam=beam),
                        CryonirspTag.task("GC_BASIC_GAIN_CORRECTED"),
                    ],
                    encoder=fits_array_encoder,
                )

    def compute_beam_angle(self, beam: int) -> float:
        """
        Compute the angle between dispersion and pixel axes for a given beam.

        The algorithm works as follows:

        1. Load the corrected solar array for this beam
        2. Compute a gradient array by shifting the array along the spatial axis (along the slit) and
           calculating a normalized finite difference with the original array.
        3. Compute 2D slices for two strips that are on either side of the spectral center.
        4. Extract the spatial strips as arrays and compute the median values along their spectral axis.
        5. Compute the relative shift of the right strip to the left strip (this is the shift along the spatial axis)
        6. Compute the angular rotation of the beam relative to the array axes from the shift
           and the separation of the strips along the spectral axis

        Returns
        -------
        The beam rotation angle in radians
        """
        # Step 1
        # Do not use a gain corrected image here, as it will cancel out the slit structure
        # that is used for the shift measurement computations
        gain_array = next(
            self.read(
                tags=[CryonirspTag.intermediate_frame(beam=beam), CryonirspTag.task_lamp_gain()],
                decoder=cryo_fits_array_decoder,
            )
        )

        full_spatial_size, full_spectral_size = gain_array.shape

        # Get the params for the strips
        spectral_offset = math.ceil(
            full_spectral_size * self.parameters.geo_strip_spectral_offset_size_fraction
        )

        # Steps 2-5:
        shift = self.shift_measurements_compute_shift_along_axis(
            axis=SPATIAL,
            array_1=gain_array,
            array_2=gain_array,
            array_1_offset=(0, -spectral_offset),
            array_2_offset=(0, spectral_offset),
            upsample_factor=self.parameters.geo_upsample_factor,
        )

        logger.info(f"Measured shift of beam {beam} = {shift}")

        # Step 6
        beam_angle = np.arctan(shift / (2 * spectral_offset))

        logger.info(f"Measured angle for beam {beam} = {np.rad2deg(beam_angle):0.3f} deg")

        return beam_angle

    def remove_beam_angle(self, angle: float, beam: int) -> np.ndarray:
        """
        De-rotate the beam array using the measured angle to align the slit with the array axes.

        Parameters
        ----------
        angle : float
            The measured beam rotation angle (in radians)
        beam : int
            The current beam being processed

        Returns
        -------
        np.ndarray
            The corrected array
        """
        rotated_array = self.basic_gain_corrected_data(beam=beam)
        corrected_array = next(self.corrections_correct_geometry(rotated_array, angle=angle))
        return corrected_array

    def compute_offset(self, array: np.ndarray, beam: int) -> np.ndarray:
        """
        Higher-level helper function to compute the (x, y) offset between beams.

        Sets beam 1 as the reference beam or computes the offset of beam 2 relative to beam 1.

        Parameters
        ----------
        array : np.ndarray
            Beam data
        beam : int
            The current beam being processed

        Returns
        -------
        np.ndarray
            (x, y) offset between beams
        """
        if beam == 1:
            self.reference_array = array
            return np.zeros(2)

        spatial_shift = self.shift_measurements_compute_shift_along_axis(
            SPATIAL,
            self.reference_array,
            array,
            upsample_factor=self.parameters.geo_upsample_factor,
        )
        spectral_shift = self.shift_measurements_compute_shift_along_axis(
            SPECTRAL,
            self.reference_array,
            array,
            upsample_factor=self.parameters.geo_upsample_factor,
        )
        shift = np.array([spatial_shift, spectral_shift])
        logger.info(f"Offset for {beam = } is {np.array2string(shift, precision=3)}")
        return shift

    def remove_beam_offset(self, array: np.ndarray, offset: np.ndarray, beam: int) -> None:
        """
        Shift an array by some offset (to make it in line with the reference array).

        Parameters
        ----------
        array : np.ndarray
            Beam data
        offset : np.ndarray
            The beam offset for the current beam
        beam : int
            The current beam being processed

        Returns
        -------
        None

        """
        corrected_array = next(self.corrections_correct_geometry(array, shift=offset))
        self.write(
            data=corrected_array,
            tags=[CryonirspTag.intermediate_frame(beam=beam), CryonirspTag.task("GC_OFFSET")],
            encoder=fits_array_encoder,
        )

    def compute_spectral_shifts(self, beam: int) -> np.ndarray:
        """
        Compute the spectral 'curvature'.

        I.e., the spectral shift at each slit position needed to have wavelength be constant across a single spatial
        pixel. Generally, the algorithm is:

         1. Identify the reference array spectrum as the center of the slit
         2. For each slit position, make an initial guess of the shift via correlation
         3. Take the initial guesses and use them in a chisq minimizer to refine the shifts
         4. Interpolate over those shifts identified as too large
         5. Remove the mean shift so the total shift amount is minimized

        Parameters
        ----------
        beam
            The current beam being processed

        Returns
        -------
        np.ndarray
            Spectral shift for a single beam
        """
        logger.info(f"Computing spectral shifts for beam {beam}")
        beam_array = self.offset_corrected_data(beam=beam)
        spatial_size = beam_array.shape[0]

        if beam == 1:
            # Use the same reference spectrum for both beams.
            # We pick the spectrum from the center of the slit, with a buffer of 10 pixels on either side
            middle_row = spatial_size // 2
            self.ref_spec = np.nanmedian(beam_array[middle_row - 10 : middle_row + 10, :], axis=0)

        beam_shifts = np.empty(spatial_size) * np.nan
        for i in range(spatial_size):
            target_spec = beam_array[i, :]

            initial_guess = self.compute_initial_spec_shift_guess(
                ref_spec=self.ref_spec, target_spec=target_spec, beam=beam, pos=i
            )

            shift = self.compute_single_spec_shift(
                ref_spec=self.ref_spec,
                target_spec=target_spec,
                initial_guess=initial_guess,
                beam=beam,
                pos=i,
            )

            beam_shifts[i] = shift

        # Subtract the average so we shift my a minimal amount
        if beam == 1:
            # Use the same mean shift for both beams to avoid any relative shifts between the two.
            self.mean_shifts = np.nanmean(beam_shifts)
            logger.info(f"Mean of spectral shifts = {self.mean_shifts}")

        beam_shifts -= self.mean_shifts
        self.write(
            data=beam_shifts,
            tags=[
                CryonirspTag.intermediate_frame(beam=beam),
                CryonirspTag.task("GC_RAW_SPECTRAL_SHIFTS"),
            ],
            encoder=fits_array_encoder,
        )

        # Finally, fit the shifts and return the resulting polynomial. Any "bad" fits were set to NaN and will be
        # interpolated over.
        poly_fit_order = self.parameters.geo_poly_fit_order
        nan_idx = np.isnan(beam_shifts)
        poly = np.poly1d(
            np.polyfit(np.arange(spatial_size)[~nan_idx], beam_shifts[~nan_idx], poly_fit_order)
        )

        return poly(np.arange(spatial_size))

    def compute_initial_spec_shift_guess(
        self, *, ref_spec: np.ndarray, target_spec: np.ndarray, beam: int, pos: int
    ) -> float:
        """
        Make a rough guess for the offset between two spectra.

        A basic correlation is performed and the location of the peak sets the initial guess. If more than one strong
        peak is found then the peak locations are averaged together.
        """
        corr = np.correlate(
            target_spec - np.nanmean(target_spec),
            ref_spec - np.nanmean(ref_spec),
            mode="same",
        )
        # Truncate the correlation to contain only allowable shifts
        max_shift = self.parameters.geo_max_shift
        mid_position = corr.size // 2
        start = mid_position - max_shift
        stop = mid_position + max_shift + 1
        truncated_corr = corr[start:stop]

        # This min_dist ensures we only find a single peak in each correlation signal
        pidx = pku.indexes(truncated_corr, min_dist=truncated_corr.size)
        initial_guess = 1 * (pidx - truncated_corr.size // 2)

        # These edge-cases are very rare, but do happen sometimes
        if initial_guess.size == 0:
            logger.info(
                f"Spatial position {pos} in {beam=} doesn't have a correlation peak. Initial guess set to 0"
            )
            initial_guess = 0.0

        elif initial_guess.size > 1:
            logger.info(
                f"Spatial position {pos} in {beam=} has more than one correlation peak ({initial_guess}). Initial guess set to mean ({np.nanmean(initial_guess)})"
            )
            initial_guess = np.nanmean(initial_guess)

        return initial_guess

    def compute_single_spec_shift(
        self,
        *,
        ref_spec: np.ndarray,
        target_spec: np.ndarray,
        initial_guess: float,
        beam: int,
        pos: int,
    ) -> float:
        """
        Refine the 1D offset between two spectra.

        A 1-parameter minimization is performed where the goodness-of-fit parameter is simply the Chisq difference
        between the reference spectrum and shifted target spectrum.
        """
        shift = minimize(
            self.shift_chisq,
            np.atleast_1d(initial_guess),
            args=(ref_spec, target_spec),
            method="nelder-mead",
        ).x[0]

        max_shift = self.parameters.geo_max_shift
        if np.abs(shift) > max_shift:
            # Didn't find a good peak
            logger.info(
                f"shift in {beam = } at spatial pixel {pos} out of range ({shift} > {max_shift})"
            )
            shift = np.nan

        return shift

    @staticmethod
    def shift_chisq(par: np.ndarray, ref_spec: np.ndarray, spec: np.ndarray) -> float:
        """
        Goodness of fit calculation for a simple shift. Uses simple chisq as goodness of fit.

        Less robust than SPGainCalibration's `refine_shift`, but much faster.

        Parameters
        ----------
        par : np.ndarray
            Spectral shift being optimized

        ref_spec : np.ndarray
            Reference spectra

        spec : np.ndarray
            Spectra being fitted

        Returns
        -------
        float
            Sum of chisquared fit

        """
        shift = par[0]
        shifted_spec = spnd.shift(spec, -shift, mode="constant", cval=np.nan)
        chisq = np.nansum((ref_spec - shifted_spec) ** 2 / ref_spec)
        return chisq

    def write_angle(self, angle: float, beam: int) -> None:
        """
        Write the angle component of the geometric calibration for a single beam.

        Parameters
        ----------
        angle : float
            The beam angle (radians) for the current beam

        beam : int
            The current beam being processed

        Returns
        -------
        None
        """
        array = np.array([angle])
        self.write(
            data=array,
            tags=[CryonirspTag.intermediate_frame(beam=beam), CryonirspTag.task_geometric_angle()],
            encoder=fits_array_encoder,
        )

    def write_beam_offset(self, offset: np.ndarray, beam: int) -> None:
        """
        Write the beam offset component of the geometric calibration for a single beam.

        Parameters
        ----------
        offset : np.ndarray
            The beam offset for the current beam

        beam : int
            The current beam being processed

        Returns
        -------
        None

        """
        self.write(
            data=offset,
            tags=[CryonirspTag.intermediate_frame(beam=beam), CryonirspTag.task_geometric_offset()],
            encoder=fits_array_encoder,
        )

    def write_spectral_shifts(self, shifts: np.ndarray, beam: int) -> None:
        """
        Write the spectral shift component of the geometric calibration for a single beam.

        Parameters
        ----------
        shifts : np.ndarray
            The spectral shifts for the current beam

        beam : int
            The current beam being processed

        Returns
        -------
        None

        """
        self.write(
            data=shifts,
            tags=[
                CryonirspTag.intermediate_frame(beam=beam),
                CryonirspTag.task_geometric_spectral_shifts(),
            ],
            encoder=fits_array_encoder,
        )
