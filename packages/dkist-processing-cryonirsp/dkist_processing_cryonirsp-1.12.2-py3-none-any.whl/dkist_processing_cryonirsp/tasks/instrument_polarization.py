"""Cryo instrument polarization task."""

from abc import ABC
from abc import abstractmethod
from collections import defaultdict

import numpy as np
from astropy.io import fits
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_math.arithmetic import divide_arrays_by_array
from dkist_processing_math.arithmetic import subtract_array_from_arrays
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_processing_math.transform.binning import resize_arrays
from dkist_processing_pac.fitter.polcal_fitter import PolcalFitter
from dkist_processing_pac.input_data.drawer import Drawer
from dkist_processing_pac.input_data.dresser import Dresser
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

__all__ = ["CIInstrumentPolarizationCalibration", "SPInstrumentPolarizationCalibration"]


def generate_polcal_quality_label(arm: str, beam: int) -> str:
    """
    Make a quality label given an arm and beam.

    Defined here so we don't have to remember what our labels are in the L1 output data task.
    """
    return f"{arm} Beam {beam}"


class InstrumentPolarizationCalibrationBase(CryonirspTaskBase, ABC):
    """
    Base task class for instrument polarization for a CryoNIRSP calibration run.

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

    @abstractmethod
    def record_polcal_quality_metrics(self, beam: int, polcal_fitter: PolcalFitter):
        """Abstract method to be implemented in subclass."""
        pass

    def run(self) -> None:
        """
        For each beam.

            - Reduce calibration sequence steps
            - Fit reduced data to PAC parameters
            - Compute and save demodulation matrices

        Returns
        -------
        None

        """
        if not self.constants.correct_for_polarization:
            return

        target_exposure_conditions = self.constants.polcal_exposure_conditions_list
        logger.info(f"{target_exposure_conditions = }")

        self.generate_polcal_dark_calibration(target_exposure_conditions)
        self.generate_polcal_gain_calibration(target_exposure_conditions)

        logger.info(
            f"Demodulation matrices will span FOV with shape {(self.parameters.polcal_num_spatial_bins, self.parameters.polcal_num_spatial_bins)}"
        )
        for beam in range(1, self.constants.num_beams + 1):
            with self.apm_processing_step(f"Reducing CS steps for {beam = }"):
                local_reduced_arrays, global_reduced_arrays = self.reduce_cs_steps(beam)

            with self.apm_processing_step(f"Fit CU parameters for {beam = }"):
                local_dresser = Dresser()
                local_dresser.add_drawer(Drawer(local_reduced_arrays))
                global_dresser = Dresser()
                global_dresser.add_drawer(Drawer(global_reduced_arrays))
                pac_fitter = PolcalFitter(
                    local_dresser=local_dresser,
                    global_dresser=global_dresser,
                    fit_mode=self.parameters.polcal_pac_fit_mode,
                    init_set=self.constants.pac_init_set,
                    fit_TM=False,
                )

            with self.apm_processing_step(f"Resampling demodulation matrices for {beam = }"):
                demod_matrices = pac_fitter.demodulation_matrices
                # Reshaping the demodulation matrix to get rid of unit length dimensions
                logger.info(f"Resampling demodulation matrices for {beam = }")
                demod_matrices = self.reshape_demod_matrices(demod_matrices)
                logger.info(
                    f"Shape of resampled demodulation matrices for {beam = }: {demod_matrices.shape}"
                )

            with self.apm_writing_step(f"Writing demodulation matrices for {beam = }"):
                self.write(
                    data=demod_matrices,
                    tags=[
                        CryonirspTag.intermediate_frame(beam=beam),
                        CryonirspTag.task_demodulation_matrices(),
                    ],
                    encoder=fits_array_encoder,
                )

            with self.apm_processing_step("Computing and recording polcal quality metrics"):
                self.record_polcal_quality_metrics(beam, polcal_fitter=pac_fitter)

        with self.apm_processing_step("Computing and logging quality metrics"):
            no_of_raw_polcal_frames: int = self.scratch.count_all(
                tags=[
                    CryonirspTag.linearized_frame(),
                    CryonirspTag.task_polcal(),
                ],
            )

            self.quality_store_task_type_counts(
                task_type=TaskName.polcal.value, total_frames=no_of_raw_polcal_frames
            )

    def reduce_cs_steps(
        self, beam: int
    ) -> tuple[dict[int, list[CryonirspL0FitsAccess]], dict[int, list[CryonirspL0FitsAccess]]]:
        """
        Reduce all of the data for the cal sequence steps for this beam.

        Parameters
        ----------
        beam
            The current beam being processed

        Returns
        -------
        Dict
            A Dict of calibrated and binned arrays for all the cs steps for this beam
        """
        local_reduced_array_dict = defaultdict(list)
        global_reduced_array_dict = defaultdict(list)

        for modstate in range(1, self.constants.num_modstates + 1):
            for exposure_conditions in self.constants.polcal_exposure_conditions_list:
                logger.info(f"Loading dark array for {exposure_conditions = } and {beam = }")
                try:
                    dark_array = next(
                        self.read(
                            tags=[
                                CryonirspTag.intermediate_frame(
                                    beam=beam, exposure_conditions=exposure_conditions
                                ),
                                CryonirspTag.task_polcal_dark(),
                            ],
                            decoder=cryo_fits_array_decoder,
                        )
                    )
                except StopIteration as e:
                    raise ValueError(
                        f"No matching dark array found for {exposure_conditions = }"
                    ) from e

                logger.info(f"Loading gain array for {exposure_conditions = } and {beam = }")
                try:
                    gain_array = next(
                        self.read(
                            tags=[
                                CryonirspTag.intermediate_frame(
                                    beam=beam, exposure_conditions=exposure_conditions
                                ),
                                CryonirspTag.task_polcal_gain(),
                            ],
                            decoder=cryo_fits_array_decoder,
                        )
                    )
                except StopIteration as e:
                    raise ValueError(
                        f"No matching gain array found for {exposure_conditions = }"
                    ) from e

                for cs_step in range(self.constants.num_cs_steps):
                    local_obj, global_obj = self.reduce_single_step(
                        beam,
                        dark_array,
                        gain_array,
                        modstate,
                        cs_step,
                        exposure_conditions,
                    )
                    local_reduced_array_dict[cs_step].append(local_obj)
                    global_reduced_array_dict[cs_step].append(global_obj)

        return local_reduced_array_dict, global_reduced_array_dict

    def reduce_single_step(
        self,
        beam: int,
        dark_array: np.ndarray,
        gain_array: np.ndarray,
        modstate: int,
        cs_step: int,
        exposure_conditions: ExposureConditions,
    ) -> tuple[CryonirspL0FitsAccess, CryonirspL0FitsAccess]:
        """
        Reduce a single calibration step for this beam, cs step and modulator state.

        Parameters
        ----------
        beam : int
            The current beam being processed
        dark_array : np.ndarray
            The dark array for the current beam
        gain_array : np.ndarray
            The gain array for the current beam
        modstate : int
            The current modulator state
        cs_step : int
            The current cal sequence step
        exposure_conditions : ExposureConditions
            The exposure conditions (exposure time, OD filter)

        Returns
        -------
        The final reduced result for this single step
        """
        apm_str = f"{beam = }, {modstate = }, {cs_step = }, and {exposure_conditions = }"
        logger.info(f"Reducing {apm_str}")

        beam_array = next(
            self.read(
                tags=CryonirspTag.intermediate_beam_boundaries(beam=beam),
                decoder=cryo_fits_array_decoder,
            )
        )
        beam_boundary = BeamBoundary(*beam_array)
        polcal_tags = [
            CryonirspTag.linearized_frame(exposure_conditions=exposure_conditions),
            CryonirspTag.cs_step(cs_step),
            CryonirspTag.modstate(modstate),
            CryonirspTag.task_polcal(),
        ]
        polcal_list = list(
            self.read(
                tags=polcal_tags,
                decoder=cryo_fits_access_decoder,
                fits_access_class=CryonirspLinearizedFitsAccess,
                beam_boundary=beam_boundary,
            )
        )

        pol_cal_headers = (obj.header for obj in polcal_list)
        pol_cal_arrays = (obj.data for obj in polcal_list)

        avg_inst_pol_cal_header = next(pol_cal_headers)
        avg_inst_pol_cal_array = average_numpy_arrays(pol_cal_arrays)

        with self.apm_processing_step(f"Apply basic corrections for {apm_str}"):
            dark_corrected_array = subtract_array_from_arrays(avg_inst_pol_cal_array, dark_array)
            gain_corrected_array = next(divide_arrays_by_array(dark_corrected_array, gain_array))

        with self.apm_processing_step(f"Extract macro pixels from {apm_str}"):
            self.set_original_beam_size(gain_corrected_array)
            output_shape = (
                self.parameters.polcal_num_spatial_bins,
                self.parameters.polcal_num_spectral_bins,
            )
            local_binned_array = next(resize_arrays(gain_corrected_array, output_shape))
            global_binned_array = next(resize_arrays(gain_corrected_array, (1, 1)))

        with self.apm_processing_step(f"Create reduced CryonirspL0FitsAccess for {apm_str}"):
            local_result = CryonirspL0FitsAccess(
                fits.ImageHDU(local_binned_array[:, :], avg_inst_pol_cal_header),
                auto_squeeze=False,
            )

            global_result = CryonirspL0FitsAccess(
                fits.ImageHDU(global_binned_array[None, :, :], avg_inst_pol_cal_header),
                auto_squeeze=False,
            )

        return local_result, global_result

    def reshape_demod_matrices(self, demod_matrices: np.ndarray) -> np.ndarray:
        """Upsample demodulation matrices to match the full beam size.

        Given an input set of demodulation matrices with shape (X', Y', 4, M) resample the output to shape
        (X, Y, 4, M), where X' and Y' are the binned size of the beam FOV, X and Y are the full beam shape, M is the
        number of modulator states.

        If only a single demodulation matrix was made then it is returned as a single array with shape (4, M).

        Parameters
        ----------
        demod_matrices
            A set of demodulation matrices with shape (X', Y', 4, M)

        Returns
        -------
        If X' and Y' > 1 then upsampled matrices that are the full beam size (X, Y, 4, M).
        If X' == Y' == 1 then a single matric for the whole FOV with shape (4, M)
        """
        expected_dims = 4
        if len(demod_matrices.shape) != expected_dims:
            raise ValueError(
                f"Expected demodulation matrices to have {expected_dims} dimensions. Got shape {demod_matrices.shape}"
            )

        data_shape = demod_matrices.shape[
            :2
        ]  # The non-demodulation matrix part of the larger array
        demod_shape = demod_matrices.shape[-2:]  # The shape of a single demodulation matrix
        logger.info(f"Demodulation FOV sampling shape: {data_shape}")
        logger.info(f"Demodulation matrix shape: {demod_shape}")
        if data_shape == (1, 1):
            # A single modulation matrix can be used directly, so just return it after removing extraneous dimensions
            logger.info(f"Single demodulation matrix detected")
            return demod_matrices[0, 0, :, :]

        target_shape = self.single_beam_shape + demod_shape
        logger.info(f"Target full-frame demodulation shape: {target_shape}")
        return self.resize_polcal_array(demod_matrices, target_shape)

    def set_original_beam_size(self, array: np.ndarray) -> None:
        """Record the shape of a single beam as a class property."""
        self.single_beam_shape = array.shape

    @staticmethod
    def resize_polcal_array(array: np.ndarray, output_shape: tuple[int, ...]) -> np.ndarray:
        return next(resize_arrays(array, output_shape))

    def generate_polcal_dark_calibration(
        self, target_exposure_conditions_list: [ExposureConditions]
    ):
        """Compute the polcal dark calibration."""
        with self.apm_task_step(
            f"Calculating dark frames for {len(target_exposure_conditions_list)} exp times"
        ):
            for beam in range(1, self.constants.num_beams + 1):
                beam_array = next(
                    self.read(
                        tags=CryonirspTag.intermediate_beam_boundaries(beam=beam),
                        decoder=cryo_fits_array_decoder,
                    )
                )
                beam_boundary = BeamBoundary(*beam_array)
                for exposure_conditions in target_exposure_conditions_list:
                    with self.apm_processing_step(
                        f"Calculating polcal dark array(s) for {exposure_conditions = } and {beam = }"
                    ):
                        linearized_dark_arrays = self.read(
                            tags=[
                                CryonirspTag.linearized_frame(
                                    exposure_conditions=exposure_conditions
                                ),
                                CryonirspTag.task_polcal_dark(),
                            ],
                            decoder=cryo_fits_array_decoder,
                            fits_access_class=CryonirspLinearizedFitsAccess,
                            beam_boundary=beam_boundary,
                        )
                        averaged_dark_array = average_numpy_arrays(linearized_dark_arrays)
                        with self.apm_writing_step(
                            f"Writing dark for {exposure_conditions = } and {beam = }"
                        ):
                            self.write(
                                data=averaged_dark_array,
                                tags=[
                                    CryonirspTag.intermediate_frame(
                                        beam=beam, exposure_conditions=exposure_conditions
                                    ),
                                    CryonirspTag.task_polcal_dark(),
                                ],
                                encoder=fits_array_encoder,
                            )

    def generate_polcal_gain_calibration(self, exposure_conditions_list: [ExposureConditions]):
        """Compute the polcal gain calibration."""
        with self.apm_task_step(
            f"Generate gains for {len(exposure_conditions_list)} exposure conditions"
        ):
            for beam in range(1, self.constants.num_beams + 1):
                beam_array = next(
                    self.read(
                        tags=CryonirspTag.intermediate_beam_boundaries(beam=beam),
                        decoder=cryo_fits_array_decoder,
                    )
                )
                beam_boundary = BeamBoundary(*beam_array)
                for exposure_conditions in exposure_conditions_list:
                    logger.info(
                        f"Load polcal dark array for {exposure_conditions = } and {beam = }"
                    )
                    try:
                        dark_array = next(
                            self.read(
                                tags=[
                                    CryonirspTag.intermediate_frame(
                                        beam=beam, exposure_conditions=exposure_conditions
                                    ),
                                    CryonirspTag.task_polcal_dark(),
                                ],
                                decoder=cryo_fits_array_decoder,
                            )
                        )
                    except StopIteration as e:
                        raise ValueError(
                            f"No matching polcal dark found for {exposure_conditions = } s and {beam = }"
                        ) from e
                    with self.apm_processing_step(
                        f"Calculating polcal gain array(s) for {exposure_conditions = } and {beam = }"
                    ):
                        linearized_gain_arrays = self.read(
                            tags=[
                                CryonirspTag.linearized_frame(
                                    exposure_conditions=exposure_conditions
                                ),
                                CryonirspTag.task_polcal_gain(),
                            ],
                            decoder=cryo_fits_array_decoder,
                            fits_access_class=CryonirspLinearizedFitsAccess,
                            beam_boundary=beam_boundary,
                        )
                        averaged_gain_array = average_numpy_arrays(linearized_gain_arrays)
                        dark_corrected_gain_array = next(
                            subtract_array_from_arrays(averaged_gain_array, dark_array)
                        )

                        bad_pixel_map = next(
                            self.read(
                                tags=[
                                    CryonirspTag.intermediate_frame(),
                                    CryonirspTag.task_bad_pixel_map(),
                                ],
                                decoder=cryo_fits_array_decoder,
                                beam_boundary=beam_boundary,
                            )
                        )
                        bad_pixel_corrected_array = self.corrections_correct_bad_pixels(
                            dark_corrected_gain_array, bad_pixel_map
                        )

                        normalized_gain_array = bad_pixel_corrected_array / np.mean(
                            bad_pixel_corrected_array
                        )

                    with self.apm_writing_step(
                        f"Writing gain array for exposure time {exposure_conditions} and {beam = }"
                    ):
                        self.write(
                            data=normalized_gain_array,
                            tags=[
                                CryonirspTag.intermediate_frame(
                                    beam=beam, exposure_conditions=exposure_conditions
                                ),
                                CryonirspTag.task_polcal_gain(),
                            ],
                            encoder=fits_array_encoder,
                        )


class CIInstrumentPolarizationCalibration(InstrumentPolarizationCalibrationBase):
    """
    Task class for instrument polarization for a CI CryoNIRSP calibration run.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs

    """

    def record_polcal_quality_metrics(self, beam: int, polcal_fitter: PolcalFitter):
        """Record various quality metrics from PolCal fits."""
        self.quality_store_polcal_results(
            polcal_fitter=polcal_fitter,
            label=generate_polcal_quality_label(arm="CI", beam=beam),
            bin_nums=[
                self.parameters.polcal_num_spatial_bins,
                self.parameters.polcal_num_spatial_bins,
            ],
            bin_labels=["spatial", "spatial"],
            skip_recording_constant_pars=False,
        )


class SPInstrumentPolarizationCalibration(InstrumentPolarizationCalibrationBase):
    """Task class for instrument polarization for an SP CryoNIRSP calibration run."""

    def record_polcal_quality_metrics(
        self,
        beam: int,
        polcal_fitter: PolcalFitter,
    ) -> None:
        """Record various quality metrics from PolCal fits."""
        self.quality_store_polcal_results(
            polcal_fitter=polcal_fitter,
            label=generate_polcal_quality_label(arm="SP", beam=beam),
            bin_nums=[
                self.parameters.polcal_num_spatial_bins,
                self.parameters.polcal_num_spectral_bins,
            ],
            bin_labels=["spatial", "spectral"],
            ## This is a bit of a hack and thus needs some explanation
            # By using the ``skip_recording_constant_pars`` switch we DON'T record the "polcal constant parameters" metric
            # for beam 2. This is because both beam 1 and beam 2 will have the same table. The way `*-common` is built
            # it will look for all metrics for both beam 1 and beam 2 so if we did save that metric for beam 2 then the
            # table would show up twice in the quality report. The following line avoids that.
            skip_recording_constant_pars=beam != 1,
        )
