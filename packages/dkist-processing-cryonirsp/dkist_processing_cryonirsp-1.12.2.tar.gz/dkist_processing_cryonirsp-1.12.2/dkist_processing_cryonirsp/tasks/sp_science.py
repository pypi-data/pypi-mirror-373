"""Cryo SP science calibration task."""

from collections import defaultdict

import numpy as np
from astropy.io import fits
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_service_configuration.logging import logger

from dkist_processing_cryonirsp.codecs.fits import cryo_fits_array_decoder
from dkist_processing_cryonirsp.models.exposure_conditions import ExposureConditions
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import CryonirspL0FitsAccess
from dkist_processing_cryonirsp.tasks.science_base import CalibrationCollection
from dkist_processing_cryonirsp.tasks.science_base import ScienceCalibrationBase

__all__ = ["SPScienceCalibration"]


class SPScienceCalibration(ScienceCalibrationBase):
    """Task class for SP Cryo science calibration of polarized and non-polarized data."""

    def calibrate_and_write_frames(self, calibrations: CalibrationCollection):
        """
        Top-level method to collect frame groupings (map_scan, scan_step, etc.) and send them to be calibrated.

        Then write the calibrated arrays.

        This is also where the polarimetric/non-polarimetric split is made.
        """
        for exposure_conditions in self.constants.observe_exposure_conditions_list:
            for map_scan in range(1, self.constants.num_map_scans + 1):
                for scan_step in range(1, self.constants.num_scan_steps + 1):
                    for meas_num in range(1, self.constants.num_meas + 1):
                        if self.constants.correct_for_polarization:
                            calibrated_object = self.calibrate_polarimetric_beams(
                                exposure_conditions=exposure_conditions,
                                map_scan=map_scan,
                                scan_step=scan_step,
                                meas_num=meas_num,
                                calibrations=calibrations,
                            )
                        else:
                            calibrated_object = self.calibrate_intensity_only_beams(
                                exposure_conditions=exposure_conditions,
                                map_scan=map_scan,
                                scan_step=scan_step,
                                meas_num=meas_num,
                                calibrations=calibrations,
                            )
                        logging_str = f"{exposure_conditions = }, {map_scan = }, {scan_step = } and {meas_num = }"
                        logger.info(f"Writing calibrated array for {logging_str}")
                        self.write_calibrated_object(
                            calibrated_object,
                            map_scan=map_scan,
                            scan_step=scan_step,
                            meas_num=meas_num,
                        )

    def calibrate_polarimetric_beams(
        self,
        *,
        exposure_conditions: ExposureConditions,
        map_scan: int,
        scan_step: int,
        meas_num: int,
        calibrations: CalibrationCollection,
    ) -> CryonirspL0FitsAccess:
        """
        Completely calibrate polarimetric science frames.

        - Apply dark and gain corrections
        - Demodulate
        - Apply geometric correction
        - Apply telescope correction
        - Combine beams
        """
        beam_storage = dict()
        header_storage = dict()
        logging_str = f"{exposure_conditions = }, {map_scan = }, {scan_step = }, {meas_num = }"
        for beam in range(1, self.constants.num_beams + 1):
            logger.info(f"Processing polarimetric observe frames from {logging_str} and {beam = }")
            intermediate_array, intermediate_header = self.correct_and_demodulate(
                beam=beam,
                meas_num=meas_num,
                scan_step=scan_step,
                map_scan=map_scan,
                exposure_conditions=exposure_conditions,
                calibrations=calibrations,
            )

            geo_corrected_array = self.apply_geometric_correction(
                array=intermediate_array, beam=beam, calibrations=calibrations
            )

            beam_storage[CryonirspTag.beam(beam)] = geo_corrected_array
            header_storage[CryonirspTag.beam(beam)] = intermediate_header

        logger.info(f"Combining beams for {logging_str}")
        combined = self.combine_beams_into_fits_access(beam_storage, header_storage)

        logger.info(f"Correcting telescope polarization for {logging_str}")
        calibrated = self.telescope_polarization_correction(combined)

        return calibrated

    def calibrate_intensity_only_beams(
        self,
        *,
        exposure_conditions: ExposureConditions,
        map_scan: int,
        scan_step: int,
        meas_num: int,
        calibrations: CalibrationCollection,
    ) -> CryonirspL0FitsAccess:
        """
        Completely calibrate non-polarimetric science frames.

        - Apply all dark and gain corrections
        - Apply geometric correction
        - Combine beams
        """
        beam_storage = dict()
        header_storage = dict()
        for beam in range(1, self.constants.num_beams + 1):
            logging_str = f"{exposure_conditions = }, {map_scan = }, {scan_step = }, {meas_num = }"
            logger.info(f"Processing Stokes-I observe frames from {logging_str} and {beam = }")
            intermediate_array, intermediate_header = self.apply_basic_corrections(
                beam=beam,
                modstate=1,
                meas_num=meas_num,
                scan_step=scan_step,
                map_scan=map_scan,
                exposure_conditions=exposure_conditions,
                calibrations=calibrations,
            )
            intermediate_header = self.compute_date_keys(intermediate_header)

            intermediate_array = self.add_stokes_dimension_to_intensity_only_array(
                intermediate_array
            )

            geo_corrected_array = self.apply_geometric_correction(
                array=intermediate_array, beam=beam, calibrations=calibrations
            )

            beam_storage[CryonirspTag.beam(beam)] = geo_corrected_array
            header_storage[CryonirspTag.beam(beam)] = intermediate_header

        logger.info(f"Combining beams for {logging_str}")
        calibrated = self.combine_beams_into_fits_access(beam_storage, header_storage)

        return calibrated

    def apply_geometric_correction(
        self, array: np.ndarray, beam: int, calibrations: CalibrationCollection
    ) -> np.ndarray:
        """
        Apply rotation, x/y shift, and spectral shift corrections to an array.

        The input array needs to have a final dimension that corresponds to Stokes parameters (even if it's only length
        1 for I-only).
        """
        corrected_array = np.zeros_like(array)
        num_stokes = array.shape[-1]

        for i in range(num_stokes):
            geo_corrected_array = next(
                self.corrections_correct_geometry(
                    array[:, :, i],
                    calibrations.state_offset[CryonirspTag.beam(beam)],
                    calibrations.angle[CryonirspTag.beam(beam)],
                )
            )

            spectral_corrected_array = next(
                self.corrections_remove_spec_shifts(
                    geo_corrected_array,
                    calibrations.spec_shift[CryonirspTag.beam(beam)],
                )
            )
            # Insert the result into the fully corrected array stack
            corrected_array[:, :, i] = spectral_corrected_array

        return corrected_array

    def combine_beams_into_fits_access(
        self, array_dict: dict, header_dict: dict
    ) -> CryonirspL0FitsAccess:
        """
        Average all beams together.

        Also complain if the inputs are strange.
        """
        headers = list(header_dict.values())
        if len(headers) == 0:
            raise ValueError("No headers provided")
        for h in headers[1:]:
            if fits.HeaderDiff(headers[0], h):
                raise ValueError("Headers are different! This should NEVER happen!")

        if self.constants.correct_for_polarization:
            avg_array = self.combine_polarimetric_beams(array_dict)
        else:
            avg_array = self.combine_spectrographic_beams(array_dict)

        hdu = fits.ImageHDU(data=avg_array, header=headers[0])
        obj = CryonirspL0FitsAccess(hdu=hdu, auto_squeeze=False)

        return obj

    def combine_polarimetric_beams(self, array_dict: dict[str, np.ndarray]) -> np.ndarray:
        """
        Combine polarimetric beams so that polarization states are normalized by the intensity state (Stokes I).

        In other words:

        avg_I = (beam1_I + beam2_I) / 2
        avg_Q = (beam1_Q / beam1_I + beam2_Q / beam2_I) / 2. * avg_I

        ...and the same for U and V
        """
        beam1_data = array_dict[CryonirspTag.beam(1)]
        beam2_data = array_dict[CryonirspTag.beam(2)]

        avg_data = np.zeros_like(beam1_data)
        # Rely on the fact that the Stokes states are in order after demodulation
        avg_I = (beam1_data[:, :, 0] + beam2_data[:, :, 0]) / 2.0
        avg_data[:, :, 0] = avg_I

        for stokes in range(1, 4):
            beam1_norm = beam1_data[:, :, stokes] / beam1_data[:, :, 0]
            beam2_norm = beam2_data[:, :, stokes] / beam2_data[:, :, 0]
            avg_data[:, :, stokes] = avg_I * (beam1_norm + beam2_norm) / 2.0

        return avg_data

    def combine_spectrographic_beams(self, array_dict: dict[str, np.ndarray]) -> np.ndarray:
        """Simply average the two beams together."""
        array_list = []
        for beam in range(1, self.constants.num_beams + 1):
            array_list.append(array_dict[CryonirspTag.beam(beam)])

        avg_array = average_numpy_arrays(array_list)
        return avg_array

    def collect_calibration_objects(self) -> CalibrationCollection:
        """
        Collect *all* calibration for all modstates, and exposure times.

        Doing this once here prevents lots of reads as we reduce the science data.
        """
        dark_dict = defaultdict(dict)
        solar_dict = dict()
        angle_dict = dict()
        state_offset_dict = dict()
        spec_shift_dict = dict()
        demod_dict = dict() if self.constants.correct_for_polarization else None

        for beam in range(1, self.constants.num_beams + 1):
            # Load the dark arrays
            for exposure_conditions in self.constants.observe_exposure_conditions_list:
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
                dark_dict[CryonirspTag.beam(beam)][
                    CryonirspTag.exposure_conditions(exposure_conditions)
                ] = dark_array

            # Load the gain arrays
            solar_dict[CryonirspTag.beam(beam)] = next(
                self.read(
                    tags=[
                        CryonirspTag.intermediate_frame(beam=beam),
                        CryonirspTag.task_solar_gain(),
                    ],
                    decoder=cryo_fits_array_decoder,
                )
            )

            # Load the angle arrays
            angle_array = next(
                self.read(
                    tags=[
                        CryonirspTag.intermediate_frame(beam=beam),
                        CryonirspTag.task_geometric_angle(),
                    ],
                    decoder=cryo_fits_array_decoder,
                )
            )
            angle_dict[CryonirspTag.beam(beam)] = float(angle_array[0])

            # Load the state offsets
            state_offset_dict[CryonirspTag.beam(beam)] = next(
                self.read(
                    tags=[
                        CryonirspTag.intermediate_frame(beam=beam),
                        CryonirspTag.task_geometric_offset(),
                    ],
                    decoder=cryo_fits_array_decoder,
                )
            )

            # Load the spectral shifts
            spec_shift_dict[CryonirspTag.beam(beam)] = next(
                self.read(
                    tags=[
                        CryonirspTag.intermediate_frame(beam=beam),
                        CryonirspTag.task_geometric_spectral_shifts(),
                    ],
                    decoder=cryo_fits_array_decoder,
                )
            )

            # Load the demod matrices
            if self.constants.correct_for_polarization:
                demod_dict[CryonirspTag.beam(beam)] = next(
                    self.read(
                        tags=[
                            CryonirspTag.intermediate_frame(beam=beam),
                            CryonirspTag.task_demodulation_matrices(),
                        ],
                        decoder=cryo_fits_array_decoder,
                    )
                )

        return CalibrationCollection(
            dark=dark_dict,
            solar_gain=solar_dict,
            angle=angle_dict,
            state_offset=state_offset_dict,
            spec_shift=spec_shift_dict,
            demod_matrices=demod_dict,
        )
