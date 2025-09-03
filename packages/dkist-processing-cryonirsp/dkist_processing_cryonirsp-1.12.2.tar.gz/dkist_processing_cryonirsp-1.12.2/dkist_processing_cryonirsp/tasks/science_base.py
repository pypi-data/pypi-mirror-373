"""Base frameworks for Cryonirsp science calibration."""

from abc import ABC
from abc import abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np
from astropy.io import fits
from astropy.time import Time
from astropy.time import TimeDelta
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_math.arithmetic import divide_arrays_by_array
from dkist_processing_math.arithmetic import subtract_array_from_arrays
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_processing_pac.optics.telescope import Telescope
from dkist_service_configuration.logging import logger

from dkist_processing_cryonirsp.codecs.fits import cryo_fits_access_decoder
from dkist_processing_cryonirsp.codecs.fits import cryo_fits_array_decoder
from dkist_processing_cryonirsp.models.beam_boundaries import BeamBoundary
from dkist_processing_cryonirsp.models.exposure_conditions import ExposureConditions
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import CryonirspL0FitsAccess
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import (
    CryonirspLinearizedFitsAccess,
)
from dkist_processing_cryonirsp.tasks.cryonirsp_base import CryonirspTaskBase


@dataclass
class CalibrationCollection:
    """Dataclass to hold all calibration objects and allow for easy, property-based access."""

    dark: dict
    solar_gain: dict
    angle: dict | None
    state_offset: dict | None
    spec_shift: dict | None
    demod_matrices: dict | None


class ScienceCalibrationBase(CryonirspTaskBase, ABC):
    """
    Task class for Cryonirsp science calibration of polarized and non-polarized data.

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
        Run Cryonirsp science calibration.

        - Collect all calibration objects
        - Calibrate and write all frames
        - Record quality metrics

        Returns
        -------
        None

        """
        with self.apm_task_step("Loading calibration objects"):
            calibrations = self.collect_calibration_objects()

        with self.apm_task_step(
            f"Calibrating Science Frames for "
            f"{self.constants.num_map_scans} map scans and "
            f"{self.constants.num_scan_steps} scan steps"
        ):
            self.calibrate_and_write_frames(calibrations=calibrations)

        with self.apm_processing_step("Computing and logging quality metrics"):
            no_of_raw_science_frames: int = self.scratch.count_all(
                tags=[
                    CryonirspTag.linearized_frame(),
                    CryonirspTag.task_observe(),
                ],
            )

            self.quality_store_task_type_counts(
                task_type=TaskName.observe.value, total_frames=no_of_raw_science_frames
            )

    @abstractmethod
    def calibrate_and_write_frames(self, calibrations: CalibrationCollection):
        """Fully calibrate science data and tag the results with CALIBRATED."""
        pass

    @abstractmethod
    def collect_calibration_objects(self) -> CalibrationCollection:
        """
        Abstract method to be implemented in subclass.

        Collect *all* calibration for all modstates, and exposure times.

        Doing this once here prevents lots of reads as we reduce the science data.
        """
        pass

    def apply_basic_corrections(
        self,
        beam: int,
        modstate: int,
        meas_num: int,
        scan_step: int,
        map_scan: int,
        exposure_conditions: ExposureConditions,
        calibrations: CalibrationCollection,
    ) -> tuple[np.ndarray, fits.Header]:
        """
        Apply basic corrections to a single frame.

        Generally the algorithm is:
            1. Dark correct the array
            2. Solar Gain correct the array

        Parameters
        ----------
        modstate
            The modulator state for this single step
        scan_step
            The slit step for this single step
        map_scan
            The current map scan
        exposure_conditions
            The exposure conditions for this single step
        calibrations
            Collection of all calibration objects

        Returns
        -------
            Corrected array, header
        """
        # Extract calibrations
        dark_array = calibrations.dark[CryonirspTag.beam(beam)][
            CryonirspTag.exposure_conditions(exposure_conditions)
        ]
        gain_array = calibrations.solar_gain[CryonirspTag.beam(beam)]

        # Grab the input observe frame(s)
        beam_array = next(
            self.read(
                tags=CryonirspTag.intermediate_beam_boundaries(beam=beam),
                decoder=cryo_fits_array_decoder,
            )
        )
        beam_boundary = BeamBoundary(*beam_array)
        observe_object_tags = [
            CryonirspTag.linearized_frame(exposure_conditions=exposure_conditions),
            CryonirspTag.map_scan(map_scan),
            CryonirspTag.scan_step(scan_step),
            CryonirspTag.meas_num(meas_num),
            CryonirspTag.modstate(modstate),
            CryonirspTag.task_observe(),
        ]
        observe_object_list = list(
            self.read(
                tags=observe_object_tags,
                decoder=cryo_fits_access_decoder,
                fits_access_class=CryonirspLinearizedFitsAccess,
                beam_boundary=beam_boundary,
            )
        )
        # There can be more than 1 frame if there are sub-repeats
        observe_fits_access = sorted(
            [item for item in observe_object_list],
            key=lambda x: x.time_obs,
        )
        observe_arrays = [item.data for item in observe_fits_access]
        observe_headers = [item.header for item in observe_fits_access]

        # Average over sub-repeats, if there are any
        avg_observe_array = average_numpy_arrays(observe_arrays)
        # Get the header for this frame
        observe_header = observe_headers[0]

        # Dark correction
        dark_corrected_array = next(subtract_array_from_arrays(avg_observe_array, dark_array))

        # Bad pixel correction
        bad_pixel_map = next(
            self.read(
                tags=[CryonirspTag.intermediate_frame(), CryonirspTag.task_bad_pixel_map()],
                decoder=cryo_fits_array_decoder,
                beam_boundary=beam_boundary,
            )
        )
        bad_pixel_corrected_array = self.corrections_correct_bad_pixels(
            dark_corrected_array, bad_pixel_map
        )

        # Gain correction
        gain_corrected_array = next(divide_arrays_by_array(bad_pixel_corrected_array, gain_array))

        return gain_corrected_array, observe_header

    def correct_and_demodulate(
        self,
        beam: int,
        meas_num: int,
        scan_step: int,
        map_scan: int,
        exposure_conditions: ExposureConditions,
        calibrations: CalibrationCollection,
    ) -> tuple[np.ndarray, fits.Header]:
        """
        Process and demodulate a single collection of modulation state data.

        - Apply dark and gain corrections
        - Demodulate
        """
        # Create the 3D stack of corrected modulated arrays
        array_shape = calibrations.dark[CryonirspTag.beam(1)][
            CryonirspTag.exposure_conditions(exposure_conditions)
        ].shape
        array_stack = np.zeros(array_shape + (self.constants.num_modstates,))
        header_stack = []

        with self.apm_processing_step(f"Correcting {self.constants.num_modstates} modstates"):
            for modstate in range(1, self.constants.num_modstates + 1):
                # Correct the arrays
                corrected_array, corrected_header = self.apply_basic_corrections(
                    beam=beam,
                    modstate=modstate,
                    meas_num=meas_num,
                    scan_step=scan_step,
                    map_scan=map_scan,
                    exposure_conditions=exposure_conditions,
                    calibrations=calibrations,
                )
                # Add this result to the 3D stack
                array_stack[:, :, modstate - 1] = corrected_array
                header_stack.append(corrected_header)

        with self.apm_processing_step("Applying instrument polarization correction"):
            intermediate_array = self.polarization_correction(
                array_stack, calibrations.demod_matrices[CryonirspTag.beam(beam)]
            )
            intermediate_header = self.compute_date_keys(header_stack)

        return intermediate_array, intermediate_header

    @staticmethod
    def polarization_correction(array_stack: np.ndarray, demod_matrices: np.ndarray) -> np.ndarray:
        """
        Apply a polarization correction to an array by multiplying the array stack by the demod matrices.

        Parameters
        ----------
        array_stack : np.ndarray
            (x, y, M) stack of corrected arrays with M modulation states

        demod_matrices : np.ndarray
            (x, y, 4, M) stack of demodulation matrices with 4 stokes planes and M modulation states


        Returns
        -------
        np.ndarray
            (x, y, 4) ndarray with the planes being IQUV
        """
        demodulated_array = np.sum(demod_matrices * array_stack[:, :, None, :], axis=3)
        return demodulated_array

    def telescope_polarization_correction(
        self,
        inst_demod_obj: CryonirspL0FitsAccess,
    ) -> CryonirspL0FitsAccess:
        """
        Apply a telescope polarization correction.

        Parameters
        ----------
        inst_demod_obj
            A demodulated, beam averaged frame

        Returns
        -------
        FitsAccess object with telescope corrections applied
        """
        tm = Telescope.from_fits_access(inst_demod_obj)
        mueller_matrix = tm.generate_inverse_telescope_model(
            M12=True, rotate_to_fixed_SDO_HINODE_polarized_frame=True, swap_UV_signs=True
        )
        inst_demod_obj.data = self.polarization_correction(inst_demod_obj.data, mueller_matrix)
        return inst_demod_obj

    def write_calibrated_object(
        self,
        calibrated_object: CryonirspL0FitsAccess,
        map_scan: int,
        scan_step: int,
        meas_num: int,
    ) -> None:
        """
        Write out calibrated science frames.

        For polarized data write out calibrated science frames for all 4 Stokes parameters.
        For non-polarized data write out calibrated science frames for Stokes I only.

        Parameters
        ----------
        calibrated_object
            Corrected frames object

        map_scan
            The current map scan. Needed because it's not a header key

        scan_step
            The current scan step

        meas_num
            The current measurement number
        """
        final_header = self.update_calibrated_header(calibrated_object.header, map_scan=map_scan)
        if self.constants.correct_for_polarization:
            stokes_I_data = calibrated_object.data[:, :, 0]
            for s, stokes_param in enumerate(self.constants.stokes_params):
                stokes_data = calibrated_object.data[:, :, s]
                final_data = self.re_dummy_data(stokes_data)
                pol_header = self.add_L1_pol_headers(final_header, stokes_data, stokes_I_data)
                self.write_calibrated_array(
                    data=final_data,
                    header=pol_header,
                    stokes=stokes_param,
                    meas_num=meas_num,
                    scan_step=scan_step,
                    map_scan=map_scan,
                )

        else:
            final_data = self.re_dummy_data(calibrated_object.data[:, :, 0])
            self.write_calibrated_array(
                data=final_data,
                header=final_header,
                stokes="I",
                meas_num=meas_num,
                scan_step=scan_step,
                map_scan=map_scan,
            )

    @staticmethod
    def wrap_array_and_header_in_fits_access(
        array: np.ndarray, header: fits.Header
    ) -> CryonirspL0FitsAccess:
        """Wrap input array and header in a CryonirspL0FitsAccess object."""
        hdu = fits.ImageHDU(data=array, header=header)
        obj = CryonirspL0FitsAccess(hdu=hdu, auto_squeeze=False)

        return obj

    @staticmethod
    def add_stokes_dimension_to_intensity_only_array(array: np.ndarray) -> np.ndarray:
        """
        Add a length-1 dimension to the end of an array.

        We do this so code that loops over the Stokes dimension still work with I-only data.
        """
        return array[..., None]

    @staticmethod
    def compute_date_keys(headers: Iterable[fits.Header] | fits.Header) -> fits.Header:
        """
        Generate correct DATE-??? header keys from a set of input headers.

        Keys are computed thusly:
        * DATE-BEG - The (Spec-0122) DATE-OBS of the earliest input header
        * DATE-END - The (Spec-0122) DATE-OBS of the latest input header, plus the FPA exposure time

        Returns
        -------
        fits.Header
            A copy of the earliest header, but with correct DATE-??? keys
        """
        if isinstance(headers, fits.Header) or isinstance(
            headers, fits.hdu.compressed.CompImageHeader
        ):
            headers = [headers]

        sorted_obj_list = sorted(
            [CryonirspL0FitsAccess.from_header(h) for h in headers], key=lambda x: Time(x.time_obs)
        )
        date_beg = sorted_obj_list[0].time_obs
        exp_time = TimeDelta(sorted_obj_list[-1].fpa_exposure_time_ms / 1000.0, format="sec")
        date_end = (Time(sorted_obj_list[-1].time_obs) + exp_time).isot

        header = sorted_obj_list[0].header
        header["DATE-BEG"] = date_beg
        header["DATE-END"] = date_end

        return header

    def re_dummy_data(self, data: np.ndarray):
        """
        Add the dummy dimension that we have been secretly squeezing out during processing.

        The dummy dimension is required because its corresponding WCS axis contains important information.

        Parameters
        ----------
        data : np.ndarray
            Corrected data
        """
        logger.info(f"Adding dummy WCS dimension to array with shape {data.shape}")
        return data[None, :, :]

    def update_calibrated_header(self, header: fits.Header, map_scan: int) -> fits.Header:
        """
        Update calibrated headers with any information gleaned during science calibration.

        Right now all this does is put map scan values in the header.

        Parameters
        ----------
        header
            The header to update

        map_scan
            Current map scan

        Returns
        -------
        fits.Header
        """
        # Correct the headers for the number of map_scans due to potential observation aborts
        header["CNNMAPS"] = self.constants.num_map_scans
        header["CNMAP"] = map_scan

        return header

    def add_L1_pol_headers(
        self, input_header: fits.Header, stokes_data: np.ndarray, stokes_I_data: np.ndarray
    ) -> fits.Header:
        """Compute and add 214 header values specific to polarimetric datasets."""
        # Probably not needed, but just to be safe
        output_header = input_header.copy()

        pol_noise = self.compute_polarimetric_noise(stokes_data, stokes_I_data)
        pol_sensitivity = self.compute_polarimetric_sensitivity(stokes_I_data)
        output_header["POL_NOIS"] = pol_noise
        output_header["POL_SENS"] = pol_sensitivity

        return output_header

    def compute_polarimetric_noise(
        self, stokes_data: np.ndarray, stokes_I_data: np.ndarray
    ) -> float:
        r"""
        Compute the polarimetric noise for a single frame.

        The polarimetric noise, :math:`N`, is defined as

        .. math::

            N = stddev(\frac{F_i}{F_I})

        where :math:`F_i` is a full array of values for Stokes parameter :math:`i` (I, Q, U, V), and :math:`F_I` is the
        full frame of Stokes-I. The stddev is computed across the entire frame.
        """
        return float(np.nanstd(stokes_data / stokes_I_data))

    def compute_polarimetric_sensitivity(self, stokes_I_data: np.ndarray) -> float:
        r"""
        Compute the polarimetric sensitivity for a single frame.

        The polarimetric sensitivity is the smallest signal that can be measured based on the values in the Stokes-I
        frame. The sensitivity, :math:`S`, is computed as

        .. math::

            S = \frac{1}{\sqrt{\mathrm{max}(F_I)}}

        where :math:`F_I` is the full frame of values for Stokes-I.
        """
        return float(1.0 / np.sqrt(np.nanmax(stokes_I_data)))

    def write_calibrated_array(
        self,
        data: np.ndarray,
        header: fits.Header,
        stokes: str,
        meas_num: int,
        scan_step: int,
        map_scan: int,
    ) -> None:
        """
        Write out calibrated array.

        Parameters
        ----------
        data : np.ndarray
            calibrated data to write out

        header : fits.Header
            calibrated header to write out

        stokes : str
            Stokes parameter of this step. 'I', 'Q', 'U', or 'V'

        meas_num: int
            The current measurement number

        scan_step : int
            The slit step for this step

        map_scan : int
            The current map scan
        """
        tags = [
            CryonirspTag.calibrated(),
            CryonirspTag.frame(),
            CryonirspTag.stokes(stokes),
            CryonirspTag.meas_num(meas_num),
            CryonirspTag.scan_step(scan_step),
            CryonirspTag.map_scan(map_scan),
        ]
        hdul = fits.HDUList([fits.PrimaryHDU(header=header, data=data)])
        self.write(
            data=hdul,
            tags=tags,
            encoder=fits_hdulist_encoder,
        )

        filename = next(self.read(tags=tags))
        logger.info(f"Wrote calibrated frame for {tags = } to {filename}")
