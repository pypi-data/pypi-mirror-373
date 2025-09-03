"""Copies of UniqueBud and SingleValueSingleKeyFlower from common that only activate if the frames are "observe" task."""

from typing import Hashable
from typing import Type

from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.parsers.single_value_single_key_flower import (
    SingleValueSingleKeyFlower,
)

from dkist_processing_cryonirsp.models.constants import CryonirspBudName
from dkist_processing_cryonirsp.models.tags import CryonirspStemName
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import CryonirspL0FitsAccess
from dkist_processing_cryonirsp.parsers.scan_step import NumberOfScanStepsBase


class NumberOfMeasurementsBud(NumberOfScanStepsBase):
    """Bud for finding the total number of measurements per scan step."""

    def __init__(self):
        self.metadata_key = "num_meas"
        super().__init__(stem_name=CryonirspBudName.num_meas.value)

    def getter(self, key: Hashable) -> Hashable:
        """
        Search all scan steps to find the maximum number of measurements in a step.

        This maximum number should be the same for all measurements, with the possible exception of the last one in
        an abort.

        Abort possibilities:
        * if a measurement is missing in the last scan step of a multi-scan, multi-map observation, it will be handled
        as an incomplete scan step and truncated by the scan step abort handler.
        * if a measurement is missing in a single-map, single-scan observation then the number of measurements will be
        given by the last measurement value that had as many frames as the maximum number of frames of any
        measurement.
        This is a formality for intensity mode observations but is an important check for polarimetric data as the
        abort may have happened in the middle of the modulator state sequence.
        """
        measurements_in_scan_steps = []
        for meas_dict in self.scan_step_dict.values():
            measurements_in_scan_steps.append(len(meas_dict))
        return max(
            measurements_in_scan_steps
        )  # if there are incomplete measurements, they should be at the end and will be truncated by an incomplete scan step


class MeasurementNumberFlower(SingleValueSingleKeyFlower):
    """Flower for a measurement number."""

    def __init__(self):
        super().__init__(tag_stem_name=CryonirspStemName.meas_num.value, metadata_key="meas_num")

    def setter(self, fits_obj: CryonirspL0FitsAccess) -> Type[SpilledDirt] | int:
        """
        Setter for a flower.

        Parameters
        ----------
        fits_obj:
            A single FitsAccess object
        """
        if fits_obj.ip_task_type != "observe":
            return SpilledDirt
        return super().setter(fits_obj)
