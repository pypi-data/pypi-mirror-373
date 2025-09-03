"""Subclasses of AssembleQualityData that cause the correct polcal metrics to build."""

from typing import Type

from dkist_processing_common.tasks import AssembleQualityData

__all__ = ["CIAssembleQualityData", "SPAssembleQualityData"]

from dkist_processing_cryonirsp.models.constants import CryonirspConstants
from dkist_processing_cryonirsp.tasks.instrument_polarization import generate_polcal_quality_label


class CIAssembleQualityData(AssembleQualityData):
    """Subclass just so that the polcal_label_list can be populated."""

    @property
    def constants_model_class(self) -> Type[CryonirspConstants]:
        """Grab the Cryo constants so we can have the number of beams."""
        return CryonirspConstants

    @property
    def polcal_label_list(self) -> list[str]:
        """Return label(s) for Cryo CI."""
        return [
            generate_polcal_quality_label(arm="CI", beam=beam)
            for beam in range(1, self.constants.num_beams + 1)
        ]


class SPAssembleQualityData(AssembleQualityData):
    """Subclass just so that the polcal_label_list can be populated."""

    @property
    def constants_model_class(self) -> Type[CryonirspConstants]:
        """Grab the Cryo constants so we can have the number of beams."""
        return CryonirspConstants

    @property
    def polcal_label_list(self) -> list[str]:
        """Return labels for beams 1 and 2."""
        return [
            generate_polcal_quality_label(arm="SP", beam=beam)
            for beam in range(1, self.constants.num_beams + 1)
        ]
