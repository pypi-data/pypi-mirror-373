"""Cryo SP solar gain task."""

import numpy as np
import scipy.ndimage as spnd
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_math.arithmetic import divide_arrays_by_array
from dkist_processing_math.arithmetic import subtract_array_from_arrays
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_service_configuration.logging import logger
from scipy import signal

from dkist_processing_cryonirsp.codecs.fits import cryo_fits_array_decoder
from dkist_processing_cryonirsp.models.beam_boundaries import BeamBoundary
from dkist_processing_cryonirsp.models.exposure_conditions import ExposureConditions
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.models.task_name import CryonirspTaskName
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import (
    CryonirspLinearizedFitsAccess,
)
from dkist_processing_cryonirsp.tasks.cryonirsp_base import CryonirspTaskBase

__all__ = ["SPSolarGainCalibration"]


class SPSolarGainCalibration(CryonirspTaskBase):
    """Task class for generating Solar Gain images for each beam.

    NB: This class does not extend GainCalibrationBase, because it is highly customized
    and incorporates several correction steps as well as solar spectrum removal.

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
        For each beam.

            - Do dark, lamp, and geometric corrections
            - Compute the characteristic spectra
            - Re-apply the spectral curvature to the characteristic spectra
            - Re-apply angle and state offset distortions to the characteristic spectra
            - Remove the distorted characteristic solar spectra from the original spectra
            - Write master solar gain

        Returns
        -------
        None

        """
        target_exposure_conditions = self.constants.solar_gain_exposure_conditions_list

        with self.apm_step(f"Computing SP gain calibrations for {target_exposure_conditions=}"):
            for exposure_conditions in target_exposure_conditions:
                for beam in range(1, self.constants.num_beams + 1):
                    with self.apm_processing_step(
                        f"Perform initial corrections for {beam = } and {exposure_conditions = }"
                    ):
                        spectral_corrected_solar_array = self.do_initial_corrections(
                            beam=beam, exposure_conditions=exposure_conditions
                        )

                    with self.apm_processing_step(
                        f"Compute the characteristic spectrum for {beam = } and {exposure_conditions = }"
                    ):
                        char_spectrum = self.compute_char_spectrum(
                            array=spectral_corrected_solar_array, beam=beam
                        )

                    with self.apm_processing_step(
                        f"Re-apply the spectral and geometric distortions for {beam = } and {exposure_conditions = }"
                    ):
                        distorted_char_spectrum = self.distort_char_spectrum(char_spectrum)

                    with self.apm_processing_step(
                        f"Remove the solar spectrum for {beam = } and {exposure_conditions = }"
                    ):
                        # This is the final gain image, as we do not normalize
                        final_gain = self.remove_solar_signal(
                            char_solar_spectra=distorted_char_spectrum,
                            beam=beam,
                            exposure_conditions=exposure_conditions,
                        )

                    if self.parameters.fringe_correction_on:
                        with self.apm_processing_step(
                            f"Computing final solar gain based on fringe-corrected flux-scaled lamp gain for {beam = } and {exposure_conditions = }"
                        ):
                            # Compute a solar gain based on a fringe-corrected lamp gain
                            final_gain = self.compute_fringe_corrected_gain(
                                beam, exposure_conditions
                            )

                    with self.apm_writing_step(
                        f"Writing the final solar gain array for {beam = } and {exposure_conditions = }"
                    ):
                        self.write_solar_gain_calibration(
                            gain_array=final_gain,
                            beam=beam,
                        )

            with self.apm_processing_step("Computing and logging quality metrics"):
                no_of_raw_solar_frames: int = self.scratch.count_all(
                    tags=[
                        CryonirspTag.linearized_frame(),
                        CryonirspTag.task_solar_gain(),
                    ],
                )
                self.quality_store_task_type_counts(
                    task_type=TaskName.solar_gain.value, total_frames=no_of_raw_solar_frames
                )

    def do_initial_corrections(
        self, beam: int, exposure_conditions: ExposureConditions
    ) -> np.ndarray:
        """
        Perform dark, bad pixel, and lamp corrections on the input solar gain data.

        Parameters
        ----------
        beam
            The beam number

        exposure_conditions
            The exposure conditions

        Returns
        -------
        A solar array with basic and geometric corrections
        """
        # Do the basic dark and bad pixel corrections
        basic_corrected_solar_array = self.do_dark_and_bad_pixel_corrections(
            beam, exposure_conditions
        )
        # Save as intermediate result for final gain computation
        self.write(
            data=basic_corrected_solar_array,
            tags=[
                CryonirspTag.intermediate_frame(beam=beam),
                CryonirspTag.task("SC_DARK_BP_CORRECTED_ONLY"),
            ],
            encoder=fits_array_encoder,
        )
        # Gain correct using the lamp gain. This removes internal optical effects.
        lamp_array = next(
            self.read(
                tags=[CryonirspTag.intermediate_frame(beam=beam), CryonirspTag.task_lamp_gain()],
                decoder=cryo_fits_array_decoder,
            )
        )
        lamp_corrected_solar_array = next(
            divide_arrays_by_array(basic_corrected_solar_array, lamp_array)
        )
        # Do the rotation and spectral corrections
        spectral_corrected_solar_array = self.do_geometric_corrections(
            lamp_corrected_solar_array, beam
        )
        # Save as an intermediate result for science users
        self.write(
            data=spectral_corrected_solar_array,
            tags=[
                CryonirspTag.intermediate_frame(beam=beam),
                CryonirspTag.task(CryonirspTaskName.spectral_corrected_solar_array.value),
            ],
            encoder=fits_array_encoder,
        )
        return spectral_corrected_solar_array

    def do_dark_and_bad_pixel_corrections(
        self, beam: int, exposure_conditions: ExposureConditions
    ) -> np.ndarray:
        """
        Perform dark and bad pixel corrections on the input solar gain data.

        Parameters
        ----------
        beam
            The beam number

        exposure_conditions
            The exposure conditions

        Returns
        -------
        A solar array with dark and bad pixel corrections
        """
        # Load the necessary files
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
        # Compute the avg solar array
        beam_array = next(
            self.read(
                tags=CryonirspTag.intermediate_beam_boundaries(beam=beam),
                decoder=cryo_fits_array_decoder,
            )
        )
        beam_boundary = BeamBoundary(*beam_array)
        linearized_solar_arrays = self.read(
            tags=[
                CryonirspTag.linearized_frame(exposure_conditions=exposure_conditions),
                CryonirspTag.task_solar_gain(),
            ],
            decoder=cryo_fits_array_decoder,
            fits_access_class=CryonirspLinearizedFitsAccess,
            beam_boundary=beam_boundary,
        )
        avg_solar_array = average_numpy_arrays(linearized_solar_arrays)
        # Dark correct it
        dark_corrected_solar_array = next(subtract_array_from_arrays(avg_solar_array, dark_array))
        # Correct for bad pixels
        bad_pixel_map = next(
            self.read(
                tags=[CryonirspTag.intermediate_frame(), CryonirspTag.task_bad_pixel_map()],
                decoder=cryo_fits_array_decoder,
                beam_boundary=beam_boundary,
            )
        )
        bad_pixel_corrected_solar_array = self.corrections_correct_bad_pixels(
            dark_corrected_solar_array, bad_pixel_map
        )
        return bad_pixel_corrected_solar_array

    def do_geometric_corrections(self, lamp_corrected_array: np.ndarray, beam: int) -> np.ndarray:
        """
        Perform geometric corrections on the input solar gain data.

        Parameters
        ----------
        lamp_corrected_array
            A solar array that has had dark, bad pixel and lamp gain corrections

        beam
            The beam number

        Returns
        -------
        An array that has geometric and spectral corrections
        """
        # Get the parameters and save them to self for use later on...
        angle_array = next(
            self.read(
                tags=[
                    CryonirspTag.intermediate_frame(beam=beam),
                    CryonirspTag.task_geometric_angle(),
                ],
                decoder=cryo_fits_array_decoder,
            )
        )
        self.angle = float(angle_array[0])
        self.state_offset = next(
            self.read(
                tags=[
                    CryonirspTag.intermediate_frame(beam=beam),
                    CryonirspTag.task_geometric_offset(),
                ],
                decoder=cryo_fits_array_decoder,
            )
        )
        self.spec_shift = next(
            self.read(
                tags=[
                    CryonirspTag.intermediate_frame(beam=beam),
                    CryonirspTag.task_geometric_spectral_shifts(),
                ],
                decoder=cryo_fits_array_decoder,
            )
        )
        # Correct for rotation and state offset. This does not correct for spectral curvature!
        geo_corrected_solar_array = next(
            self.corrections_correct_geometry(lamp_corrected_array, self.state_offset, self.angle)
        )
        # Remove the spectral curvature
        spectral_corrected_solar_array = next(
            self.corrections_remove_spec_shifts(geo_corrected_solar_array, self.spec_shift)
        )
        return spectral_corrected_solar_array

    def compute_char_spectrum(self, array: np.ndarray, beam: int) -> np.ndarray:
        """
        Estimate the characteristic solar spectrum from the corrected solar gain data.

        Parameters
        ----------
        array
            A corrected solar array image

        Returns
        -------
        A 2D array with the estimate of the characteristic spectrum
        """
        # Normalize data row by row
        pct = self.parameters.solar_characteristic_spatial_normalization_percentile
        array_row_norm = array / np.nanpercentile(array, pct, axis=1)[:, None]
        # Compute characteristic spectrum
        char_spec_1d = np.nanmedian(array_row_norm, axis=0)
        # Expand the 1D median along the columns (along the slit)
        median_char_spec_2d = np.tile(char_spec_1d, (array_row_norm.shape[0], 1))
        self.write(
            data=char_spec_1d,
            tags=[
                CryonirspTag.intermediate_frame(beam=beam),
                CryonirspTag.task_characteristic_spectra(),
            ],
            encoder=fits_array_encoder,
        )
        return median_char_spec_2d

    def distort_char_spectrum(self, char_spec: np.ndarray) -> np.ndarray:
        """
        Re-apply the geometric distortions, that were previously removed, to the characteristic spectrum.

        Parameters
        ----------
        char_spec
            The characteristic spectrum

        Returns
        -------
        The characteristic spectrum with spectral curvature distortion applied
        """
        # Re-distort the characteristic spectrum in the reverse order from the earlier correction
        # 1. Add spectral curvature back
        reshifted_spectrum = next(
            self.corrections_remove_spec_shifts(arrays=char_spec, spec_shift=-self.spec_shift)
        )
        # 2. Add state offset and angular rotation back
        distorted_spectrum = next(
            self.corrections_distort_geometry(
                reshifted_spectrum,
                -self.state_offset,
                -self.angle,
            )
        )
        return distorted_spectrum

    def geo_corrected_data(self, beam: int, exposure_conditions: ExposureConditions) -> np.ndarray:
        """
        Read the intermediate dark and bad-pixel corrected solar data saved previously.

        Parameters
        ----------
        beam
            The beam number

        exposure_conditions
            The exposure conditions

        Returns
        -------
        A dark and bad pixel corrected solar array
        """
        array_generator = self.read(
            tags=[
                CryonirspTag.intermediate_frame(beam=beam),
                CryonirspTag.task("SC_DARK_BP_CORRECTED_ONLY"),
            ],
            decoder=cryo_fits_array_decoder,
        )
        return next(array_generator)

    def remove_solar_signal(
        self,
        char_solar_spectra: np.ndarray,
        beam: int,
        exposure_conditions: ExposureConditions,
    ) -> np.ndarray:
        """
        Remove the (distorted) characteristic solar spectra from the input solar data.

        Parameters
        ----------
        char_solar_spectra
            The characteristic spectrum

        beam
            The beam number

        exposure_conditions
            The exposure conditions

        Returns
        -------
        A geometric and spectrally corrected array with the solar signal removed
        """
        logger.info(
            f"Removing characteristic solar spectra from {beam=} and {exposure_conditions =}"
        )
        input_gain = self.geo_corrected_data(beam=beam, exposure_conditions=exposure_conditions)
        array_with_solar_signal_removed = input_gain / char_solar_spectra
        return array_with_solar_signal_removed

    def write_solar_gain_calibration(self, gain_array: np.ndarray, beam: int) -> None:
        """
        Write the final gain array as a file.

        Parameters
        ----------
        gain_array
            The final gain array

        beam
            The beam number

        Returns
        -------
        None
        """
        logger.info(f"Writing final SolarGain for {beam=}")
        self.write(
            data=gain_array,
            tags=[CryonirspTag.intermediate_frame(beam=beam), CryonirspTag.task_solar_gain()],
            encoder=fits_array_encoder,
        )

    def compute_fringe_corrected_gain(self, beam: int, exposure_conditions: float) -> np.ndarray:
        """
        Compute a solar gain based on a scaled and fringe-removed lamp gain.

        Parameters
        ----------
        beam
            The beam number

        exposure_conditions
            The exposure conditions

        Returns
        -------
        A lamp gain array that has been scaled to the average solar flux and has been fringe-corrected
        """
        apm_str = f"{beam = } and {exposure_conditions = }"

        with self.apm_processing_step(f"Perform initial corrections for {apm_str}"):
            corrected_solar_array = self.do_dark_and_bad_pixel_corrections(
                beam=beam, exposure_conditions=exposure_conditions
            )

        with self.apm_processing_step(f"Compute the flux-scaled lamp gain for {apm_str}"):
            scaled_lamp_array = self.compute_flux_scaled_lamp_gain(corrected_solar_array, beam)

        with self.apm_processing_step(f"Apply spectral filtering for {apm_str}"):
            filtered_lamp_array = self.apply_spectral_and_spatial_filtering(scaled_lamp_array)

        with self.apm_processing_step(f"Isolate and remove fringes for {apm_str}"):
            final_gain_array = self.isolate_and_remove_fringes(
                filtered_lamp_array, scaled_lamp_array
            )

        return final_gain_array

    def compute_flux_scaled_lamp_gain(
        self, corrected_solar_array: np.ndarray, beam: int
    ) -> np.ndarray:
        """
        Scale the lamp gain image to match the flux of the average corrected solar array.

        The average corrected solar array is gain corrected using the lamp gain image.
        The flux ratio of the average corrected solar array relative to the lamp gain is computed
        as the median of the lamp-gain-corrected solar array along the spectral axis.
        The lamp gain is then scaled on a column by column basis by the flux ratio to yield
        a gain image that is similar the average corrected solar array.

        Parameters
        ----------
        corrected_solar_array
            The dark and bad pixel corrected average solar array

        beam
            The beam number

        Returns
        -------
        The scaled lamp array
        """
        lamp_array = next(
            self.read(
                tags=[CryonirspTag.intermediate_frame(beam=beam), CryonirspTag.task_lamp_gain()],
                decoder=cryo_fits_array_decoder,
            )
        )
        lamp_corrected_solar_array = next(divide_arrays_by_array(corrected_solar_array, lamp_array))
        flux_ratio = np.nanmedian(lamp_corrected_solar_array, axis=1)
        scaled_lamp_array = lamp_array * flux_ratio[:, None]
        return scaled_lamp_array

    def apply_spectral_and_spatial_filtering(self, scaled_lamp_array: np.ndarray) -> np.ndarray:
        """
        Apply spectral and spatial filtering to the scaled lamp array.

        Parameters
        ----------
        scaled_lamp_array
            The input scaled lamp array

        Returns
        -------
        The filtered lamp array
        """
        spectral_filter_size = self.parameters.fringe_correction_spectral_filter_size
        spatial_filter_size = self.parameters.fringe_correction_spatial_filter_size
        spectral_filtered_lamp_array = spnd.gaussian_filter(scaled_lamp_array, spectral_filter_size)
        partial_filtered_array = scaled_lamp_array / spectral_filtered_lamp_array
        spatial_filtered_lamp_gain = spnd.gaussian_filter(
            partial_filtered_array, spatial_filter_size
        )
        return spatial_filtered_lamp_gain

    def isolate_and_remove_fringes(
        self, filtered_lamp_array: np.ndarray, scaled_lamp_array: np.ndarray
    ) -> np.ndarray:
        """
        Use a low pass filter to estimate the fringes and then remove them from the scaled lamp array.

        Parameters
        ----------
        filtered_lamp_array
            The filtered lamp gain array

        scaled_lamp_array
            The scaled lamp gain array

        Returns
        -------
        The scaled lamp array with fringes removed.
        """
        # The fringe cutoff is specified as a period so we invert it to get the lowpass cutoff frequency
        cutoff_freq = 1.0 / self.parameters.fringe_correction_lowpass_cutoff_period
        # Compute the Butterworth lowpass filter coefficients
        numerator, denominator = signal.butter(2, cutoff_freq, btype="lowpass", fs=1)
        # Apply the lowpass Butterworth filter and use Gustafsson's method to better preserve the array edges
        low_pass_filtered_array = signal.filtfilt(
            numerator, denominator, filtered_lamp_array, axis=1, method="gust"
        )
        fringe_estimate = filtered_lamp_array / low_pass_filtered_array
        fringe_removed_array = scaled_lamp_array / fringe_estimate
        return fringe_removed_array
