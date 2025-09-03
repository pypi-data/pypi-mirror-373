"""Copy of UniqueBud from common that only activates if the frames are polarimetric "observe" or "polcal" task, or non-polarimetric "observe" task."""

from collections import namedtuple
from typing import Type

from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.models.flower_pot import Thorn
from dkist_processing_common.models.task_name import TaskName

from dkist_processing_cryonirsp.models.constants import CryonirspBudName
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import CryonirspL0FitsAccess


class PolarimetricCheckingUniqueBud(Stem):
    """Bud for checking if frames are polarimetric."""

    PolarimetricValueData = namedtuple(
        "PolarimetricValueData", ["task", "num_modstates", "spin_mode", "bud_value"]
    )
    observe_task_name = TaskName.observe.value.casefold()
    polcal_task_name = TaskName.polcal.value.casefold()

    def __init__(self, constant_name: str, metadata_key: str):
        super().__init__(stem_name=constant_name)
        self.metadata_key = metadata_key

    @property
    def observe_tuple_values(self) -> tuple:
        """Return all ingested namedtuples from observe frames."""
        return filter(lambda x: x.task == self.observe_task_name, self.key_to_petal_dict.values())

    @property
    def polcal_tuple_values(self) -> tuple:
        """Return all ingested namedtuples from polcal frames."""
        return filter(lambda x: x.task == self.polcal_task_name, self.key_to_petal_dict.values())

    def is_polarimetric(self) -> bool:
        """Check if data is polarimetric."""
        obs_num_mod_set = set((o.num_modstates for o in self.observe_tuple_values))
        obs_spin_mode_set = set((o.spin_mode for o in self.observe_tuple_values))

        if len(obs_num_mod_set) > 1:
            raise ValueError(
                f"Observe frames have more than one value of NUM_MODSTATES. Set is {obs_num_mod_set}"
            )
        if len(obs_spin_mode_set) > 1:
            raise ValueError(
                f"Observe frames have more than one value of MODULATOR_SPIN_MODE. Set is {obs_spin_mode_set}"
            )

        num_mod = obs_num_mod_set.pop()
        spin_mode = obs_spin_mode_set.pop()
        if num_mod > 1 and spin_mode in [
            "Continuous",
            "Stepped",
        ]:
            return True
        return False

    def setter(self, fits_obj: CryonirspL0FitsAccess) -> Type[SpilledDirt] | tuple:
        """
        Return a `PolarimetricValueData` namedtuple only for OBSERVE and POLCAL frames.

        Parameters
        ----------
        fits_obj:
            A single FitsAccess object
        """
        task = fits_obj.ip_task_type.casefold()

        # Some intensity mode data has the number of modulator states set to 0
        num_modstates = fits_obj.number_of_modulator_states or 1

        if self.metadata_key == "number_of_modulator_states":
            bud_value = num_modstates
        else:
            bud_value = getattr(fits_obj, self.metadata_key)

        if task in [self.observe_task_name, self.polcal_task_name]:
            return self.PolarimetricValueData(
                task=task,
                num_modstates=num_modstates,
                spin_mode=fits_obj.modulator_spin_mode,
                bud_value=bud_value,
            )
        return SpilledDirt

    def getter(self, key: str) -> int | str | Type[Thorn]:
        """
        Return the desired metadata key, with checks.

        If data are from a polarimetric dataset then the values must match between observe and polcal frames.
        In all cases the value returned must be the same across all observe (and potentially polcal) frames.
        """
        obs_value_set = set((o.bud_value for o in self.observe_tuple_values))
        if len(obs_value_set) == 0:
            # For the rare case where we have polcal frames but not observe frames that are being parsed. This only
            # comes up in unit tests.
            return Thorn

        obs_value = obs_value_set.pop()

        if self.is_polarimetric():
            pol_value_set = set((o.bud_value for o in self.polcal_tuple_values))

            if len(pol_value_set) > 1:
                raise ValueError(
                    f"Polcal frames have more than one value of NUM_MODSTATES. Set is {pol_value_set}"
                )

            pol_value = pol_value_set.pop()

            if obs_value != pol_value:
                raise ValueError(
                    f"Polcal and Observe frames have different values for {self.metadata_key}. ({obs_value = }, {pol_value = })"
                )

            return obs_value

        return obs_value
