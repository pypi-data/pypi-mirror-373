"""CryoNIRSP dark calibration task."""

from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_service_configuration.logging import logger

from dkist_processing_cryonirsp.codecs.fits import cryo_fits_array_decoder
from dkist_processing_cryonirsp.models.beam_boundaries import BeamBoundary
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import (
    CryonirspLinearizedFitsAccess,
)
from dkist_processing_cryonirsp.tasks.cryonirsp_base import CryonirspTaskBase

__all__ = ["DarkCalibration"]


class DarkCalibration(CryonirspTaskBase):
    """Task class for calculation of the averaged dark frame for a CryoNIRSP calibration run.

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

        - Gather input dark frames
        - Calculate average dark
        - Write average dark
        - Record quality metrics

        Returns
        -------
        None

        """
        arm = self.constants.arm_id

        if arm == "CI":
            target_exposure_conditions = (
                self.constants.ci_non_dark_and_non_polcal_and_non_lamp_gain_task_exposure_conditions_list
            )
        if arm == "SP":
            target_exposure_conditions = (
                self.constants.sp_non_dark_and_non_polcal_task_exposure_conditions_list
            )

        logger.info(f"{target_exposure_conditions = }")
        with self.apm_task_step(
            f"Calculating dark frames for {self.constants.num_beams} beams and {len(target_exposure_conditions)} exp times"
        ):
            total_dark_frames_used = 0

            for beam in range(1, self.constants.num_beams + 1):
                beam_array = next(
                    self.read(
                        tags=CryonirspTag.intermediate_beam_boundaries(beam=beam),
                        decoder=cryo_fits_array_decoder,
                    )
                )
                beam_boundary = BeamBoundary(*beam_array)

                for exposure_conditions in target_exposure_conditions:
                    logger.info(
                        f"Gathering input dark frames for {exposure_conditions = } and {beam = }"
                    )
                    dark_tags = [
                        CryonirspTag.linearized_frame(exposure_conditions=exposure_conditions),
                        CryonirspTag.task_dark(),
                    ]
                    current_exp_dark_count = self.scratch.count_all(tags=dark_tags)
                    total_dark_frames_used += current_exp_dark_count

                    linearized_dark_arrays = self.read(
                        tags=dark_tags,
                        decoder=cryo_fits_array_decoder,
                        fits_access_class=CryonirspLinearizedFitsAccess,
                        beam_boundary=beam_boundary,
                    )

                    with self.apm_processing_step(
                        f"Calculating dark for {exposure_conditions = } and {beam = }"
                    ):
                        averaged_dark_array = average_numpy_arrays(linearized_dark_arrays)

                    with self.apm_writing_step(
                        f"Writing dark for {exposure_conditions = } {beam = }"
                    ):
                        self.write(
                            data=averaged_dark_array,
                            tags=[
                                CryonirspTag.intermediate_frame(
                                    beam=beam, exposure_conditions=exposure_conditions
                                ),
                                CryonirspTag.task_dark(),
                            ],
                            encoder=fits_array_encoder,
                        )

        with self.apm_processing_step("Computing and logging quality metrics"):
            no_of_raw_dark_frames: int = self.scratch.count_all(
                tags=[
                    CryonirspTag.linearized_frame(),
                    CryonirspTag.task_dark(),
                ],
            )
            unused_count = int(
                no_of_raw_dark_frames - (total_dark_frames_used // self.constants.num_beams)
            )
            self.quality_store_task_type_counts(
                task_type=TaskName.dark.value,
                total_frames=no_of_raw_dark_frames,
                frames_not_used=unused_count,
            )
