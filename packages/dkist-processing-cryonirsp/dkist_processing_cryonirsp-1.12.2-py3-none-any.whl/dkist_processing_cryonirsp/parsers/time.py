"""Buds to parse exposure time."""

from typing import Hashable
from typing import Type

from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.parsers.task import parse_header_ip_task_with_gains

from dkist_processing_cryonirsp.models.constants import CryonirspBudName
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import CryonirspL0FitsAccess
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import CryonirspRampFitsAccess


class CryonirspSolarGainStartTimeBud(Stem):
    """Bud for finding the start time of the solar gain."""

    def __init__(self):
        self.metadata_key = "time_obs"
        super().__init__(stem_name=CryonirspBudName.solar_gain_ip_start_time.value)

    def setter(self, fits_obj: CryonirspL0FitsAccess) -> Type[SpilledDirt] | int:
        """
        Setter for the bud.

        Parameters
        ----------
        fits_obj:
            A single FitsAccess object
        """
        if parse_header_ip_task_with_gains(fits_obj) != TaskName.solar_gain.value:
            return SpilledDirt
        return getattr(fits_obj, self.metadata_key)

    def getter(self, key: Hashable):
        """Return the first date-obs value."""
        first_date_obs = min(list(self.key_to_petal_dict.values()))
        return first_date_obs


class CryonirspTimeObsBud(Stem):
    """
    Produce a tuple of all time_obs values present in the dataset.

    The time_obs is a unique identifier for all raw frames in a single ramp. Hence, this list identifies all
    the ramps that must be processed in a data set.
    """

    def __init__(self):
        super().__init__(stem_name=CryonirspBudName.time_obs_list.value)

    def setter(self, fits_obj: CryonirspRampFitsAccess):
        """
        Set the time_obs for this fits object.

        Parameters
        ----------
        fits_obj
            The input fits object
        Returns
        -------
        The time_obs value associated with this fits object
        """
        return fits_obj.time_obs

    def getter(self, key: Hashable) -> tuple:
        """
        Get the sorted tuple of time_obs values.

        Parameters
        ----------
        key
            The input key

        Returns
        -------
        A tuple of exposure times
        """
        time_obs_tup = tuple(sorted(set(self.key_to_petal_dict.values())))
        return time_obs_tup
