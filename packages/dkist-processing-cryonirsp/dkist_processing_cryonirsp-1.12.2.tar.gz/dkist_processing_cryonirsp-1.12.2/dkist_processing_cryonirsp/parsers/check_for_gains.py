"""Pickybud to check for lamp gain and solar gain frames."""

from typing import Hashable
from typing import Type

from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.models.flower_pot import Thorn
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.parsers.task import parse_header_ip_task_with_gains

from dkist_processing_cryonirsp.models.constants import CryonirspBudName
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import CryonirspL0FitsAccess


class CheckGainFramesPickyBudBase(Stem):
    """Pickybud to check for gain frames."""

    def __init__(self, stem_name: str, task_name: str):
        super().__init__(stem_name=stem_name)
        self.task_name = task_name.casefold()

    def setter(self, fits_obj: CryonirspL0FitsAccess) -> Type[SpilledDirt] | str:
        """
        Set the calibration frame type for this fits object.

        Parameters
        ----------
        fits_obj
            The input fits object
        Returns
        -------
        The calibration frame object associated with this fits object
        """
        return parse_header_ip_task_with_gains(fits_obj).casefold()

    def getter(self, key: Hashable) -> Type[Thorn]:
        """
        Check that the specific gain exists. If it does, return a Thorn.

        Parameters
        ----------
        key
            The input key

        Returns
        -------
        Thorn
        """
        task_types = list(self.key_to_petal_dict.values())

        if self.task_name not in task_types:
            raise ValueError(f"{self.task_name} frames not found.")
        return Thorn


class CheckSolarGainFramesPickyBud(CheckGainFramesPickyBudBase):
    """Pickybud to check for solar gain frames."""

    def __init__(self):
        super().__init__(
            stem_name=CryonirspBudName.solar_gain_frame_type_list.value,
            task_name=TaskName.solar_gain.value,
        )


class CheckLampGainFramesPickyBud(CheckGainFramesPickyBudBase):
    """Pickybud to check for lamp gain frames."""

    def __init__(self):
        super().__init__(
            stem_name=CryonirspBudName.lamp_gain_frame_type_list.value,
            task_name=TaskName.lamp_gain.value,
        )
