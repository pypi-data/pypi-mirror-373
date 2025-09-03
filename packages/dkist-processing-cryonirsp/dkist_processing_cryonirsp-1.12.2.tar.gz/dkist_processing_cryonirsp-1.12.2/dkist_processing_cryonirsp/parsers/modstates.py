"""Copy of SingleValueSingleKeyFlower from common that only activates if the frames are "observe" task."""

from typing import Type

from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.tags import StemName
from dkist_processing_common.parsers.single_value_single_key_flower import (
    SingleValueSingleKeyFlower,
)

from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import CryonirspL0FitsAccess


class ModstateNumberFlower(SingleValueSingleKeyFlower):
    """Flower for a modstate number."""

    def __init__(self):
        super().__init__(tag_stem_name=StemName.modstate.value, metadata_key="modulator_state")

    def setter(self, fits_obj: CryonirspL0FitsAccess) -> Type[SpilledDirt] | int:
        """
        Setter for a flower.

        Parameters
        ----------
        fits_obj:
            A single FitsAccess object
        """
        # Some intensity data incorrectly has modulator state = 0
        if getattr(fits_obj, self.metadata_key) == 0:
            return 1
        return super().setter(fits_obj)
