"""Cryonirsp CI science calibration task."""

from collections import defaultdict

from dkist_service_configuration.logging import logger

from dkist_processing_cryonirsp.codecs.fits import cryo_fits_array_decoder
from dkist_processing_cryonirsp.models.exposure_conditions import ExposureConditions
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import CryonirspL0FitsAccess
from dkist_processing_cryonirsp.tasks.science_base import CalibrationCollection
from dkist_processing_cryonirsp.tasks.science_base import ScienceCalibrationBase

__all__ = ["CIScienceCalibration"]


class CIScienceCalibration(ScienceCalibrationBase):
    """Task class for Cryonirsp CI science calibration of polarized and non-polarized data."""

    CI_BEAM = 1

    def calibrate_and_write_frames(self, calibrations: CalibrationCollection):
        """
        Completely calibrate all science frames.

        - Apply dark and gain corrections
        - Demodulate if needed
        - Apply telescope correction, if needed
        - Write calibrated arrays
        """
        for exposure_conditions in self.constants.observe_exposure_conditions_list:
            for map_scan in range(1, self.constants.num_map_scans + 1):
                for scan_step in range(1, self.constants.num_scan_steps + 1):
                    for meas_num in range(1, self.constants.num_meas + 1):
                        if self.constants.correct_for_polarization:
                            calibrated_object = self.calibrate_polarimetric_frames(
                                exposure_conditions=exposure_conditions,
                                map_scan=map_scan,
                                scan_step=scan_step,
                                meas_num=meas_num,
                                calibrations=calibrations,
                            )
                        else:
                            calibrated_object = self.calibrate_intensity_only_frames(
                                exposure_conditions=exposure_conditions,
                                map_scan=map_scan,
                                scan_step=scan_step,
                                meas_num=meas_num,
                                calibrations=calibrations,
                            )

                        logging_str = f"{exposure_conditions = }, {map_scan = }, {scan_step = } and {meas_num = }"
                        logger.info(f"Writing calibrated arrays for {logging_str}")
                        self.write_calibrated_object(
                            calibrated_object,
                            map_scan=map_scan,
                            scan_step=scan_step,
                            meas_num=meas_num,
                        )

    def calibrate_polarimetric_frames(
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
        - Apply telescope correction
        """
        logging_str = f"{exposure_conditions = }, {map_scan = }, {scan_step = } and {meas_num = }"
        logger.info(f"Processing polarimetric observe frames from {logging_str}")

        intermediate_array, intermediate_header = self.correct_and_demodulate(
            beam=self.CI_BEAM,
            meas_num=meas_num,
            scan_step=scan_step,
            map_scan=map_scan,
            exposure_conditions=exposure_conditions,
            calibrations=calibrations,
        )

        intermediate_object = self.wrap_array_and_header_in_fits_access(
            intermediate_array, intermediate_header
        )

        logger.info(f"Correcting telescope polarization for {logging_str}")
        calibrated_object = self.telescope_polarization_correction(intermediate_object)

        return calibrated_object

    def calibrate_intensity_only_frames(
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

        - Apply dark and gain corrections
        """
        logging_str = f"{exposure_conditions = }, {map_scan = }, {scan_step = } and {meas_num = }"
        logger.info(f"Processing Stokes-I observe frames from {logging_str}")
        intermediate_array, intermediate_header = self.apply_basic_corrections(
            beam=self.CI_BEAM,
            modstate=1,
            meas_num=meas_num,
            scan_step=scan_step,
            map_scan=map_scan,
            exposure_conditions=exposure_conditions,
            calibrations=calibrations,
        )
        intermediate_header = self.compute_date_keys(intermediate_header)

        intermediate_array = self.add_stokes_dimension_to_intensity_only_array(intermediate_array)

        calibrated_object = self.wrap_array_and_header_in_fits_access(
            intermediate_array, intermediate_header
        )

        return calibrated_object

    def collect_calibration_objects(self) -> CalibrationCollection:
        """
        Collect *all* calibration for all modstates, and exposure times.

        Doing this once here prevents lots of reads as we reduce the science data.
        """
        dark_dict = defaultdict(dict)
        solar_dict = dict()
        demod_dict = dict() if self.constants.correct_for_polarization else None

        beam = self.CI_BEAM
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
                tags=[CryonirspTag.intermediate_frame(beam=beam), CryonirspTag.task_solar_gain()],
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
            angle=None,
            spec_shift=None,
            state_offset=None,
            solar_gain=solar_dict,
            demod_matrices=demod_dict,
        )
