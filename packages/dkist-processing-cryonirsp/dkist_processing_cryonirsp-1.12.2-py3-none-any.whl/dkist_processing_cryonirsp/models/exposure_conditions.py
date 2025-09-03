"""Support classes for exposure conditions."""

from collections import namedtuple
from enum import StrEnum

# Number of digits used to round the exposure when creating the ExposureConditions tuple in fits_access
CRYO_EXP_TIME_ROUND_DIGITS: int = 3

"""Base class to hold a tuple of exposure time and filter name."""
ExposureConditionsBase = namedtuple("ExposureConditions", ["exposure_time", "filter_name"])


class ExposureConditions(ExposureConditionsBase):
    """Define str to make tags look reasonable."""

    def __str__(self):
        return f"{self.exposure_time}_{self.filter_name}"


class AllowableOpticalDensityFilterNames(StrEnum):
    """Enum to implement list of allowable Optical Density Filter names."""

    G278 = "G278"
    G358 = "G358"
    G408 = "G408"
    OPEN = "OPEN"
    NONE = "NONE"
