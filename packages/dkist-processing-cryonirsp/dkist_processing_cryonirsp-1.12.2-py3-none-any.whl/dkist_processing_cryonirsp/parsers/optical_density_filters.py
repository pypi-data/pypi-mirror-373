"""PickyBud to implement early parsing of Optical Density Filter Names."""

from typing import Hashable

from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.models.flower_pot import Thorn

from dkist_processing_cryonirsp.models.exposure_conditions import AllowableOpticalDensityFilterNames
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import CryonirspRampFitsAccess

ALLOWABLE_OPTICAL_DENSITY_FILTERS = {f for f in AllowableOpticalDensityFilterNames}


class OpticalDensityFiltersPickyBud(Stem):
    """PickyBud to implement early parsing of Optical Density Filter Names."""

    def __init__(self):
        super().__init__(stem_name="OpticalDensityFilterNamePickyBud")

    def setter(self, fits_obj: CryonirspRampFitsAccess):
        """
        Set the optical density filter name for this fits object.

        Parameters
        ----------
        fits_obj
            The input fits obj

        Returns
        -------
        The optical density filter name associated with this fits object
        """
        return fits_obj.filter_name.upper()

    def getter(self, key: Hashable) -> Thorn:
        """Return a Thorn for valid names or raise an exception for bad names."""
        filter_names = set(self.key_to_petal_dict.values())
        bad_filter_names = filter_names.difference(ALLOWABLE_OPTICAL_DENSITY_FILTERS)
        if bad_filter_names:
            raise ValueError(f"Unknown Optical Density Filter Name(s): {bad_filter_names = }")
        return Thorn
