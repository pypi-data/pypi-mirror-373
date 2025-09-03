"""
Machinery for sorting files based on scan step.

Also includes base classes that can be used to sort files based on map scan.
"""

######################
# HOW THIS ALL WORKS #
######################
#
# By analogy
#
# Something to know: Spruce, Pine, and Fir all have pretty similar physical properties (like density). This is why
# framing lumber is often sold as "SPF"; it could be any of these three woods because they're similar enough for
# building.
#
# Now, the analogy of how we sort and figure out how many map scans and scan steps there are...
#
# We will be sorting wooden blocks. These blocks have 2 characteristics that we can directly observe: shape and color.
# We know that the factory only makes two shapes of blocks: spheres and cubes.
# We know that the factory only uses three colors: red, green, and blue.
# The blocks can be made of different woods: spruce, pine, or fir. Unfortunately we *can't* tell which wood is which
# via direct observation (especially after they have been painted).
# Additionally, the factory stamps a serial number on every block. These numbers are continuously increasing and never
# repeat.
#
# The problem is that we need to sort blocks based on the type of wood used.
#
# Fortunately we know how the factory makes these blocks:
#
# o They make exactly 6 blocks (2 shapes * 3 colors) from each board of wood
# o They use exactly 3 boards of wood each day (it's not a very big factory)
# o They *always* start with a board of spruce, then a board of pine, and finally a board of fir
# o When processing a single board, the sequence is:
#   1. Make 3 spheres
#   2. Color a sphere red. This block is done so stamp it with a serial number.
#   3. Color a sphere blue. This block is done so stamp it with a serial number.
#   4. Color the last sphere green. This block is done so stamp it with a serial number.
#   5. Repeat steps 1-4 but with cubes instead of spheres.
#
# With all of this information we can easily sort the blocks by wood type. The algorithm works like this.
#
# 1. Choose a (shape, color) combination. For this example we'll use green spheres
# 2. Collect all green spheres
# 3. Sort the green spheres by their serial numbers. They won't be in sequence, but that doesn't matter.
# 4. The lowest serial number came from the first board of the day (spruce), the middle number comes from the second
#    (pine) board, and the largest number comes from the last (fir) board.
# 5. Start a new set of piles for spruce, pine, and fir, and place the sorted green spheres into these piles.
# 6. Repeat steps 1-5 for all other (shape, color) combinations.
#
# And there you go! We now have correctly sorted the blocks by type of wood.
# We have used our knowledge of the GENERATING PROCESS and OBSERVABLE PROPERTIES to sort by an UNOBSERVABLE PROPERTY.
#
# Analogy over.
#
# We want to sort frames by map_scan. This is the UNOBSERVABLE PROPERTY (like wood type).
# Each frame has many OBSERVABLE PROPERTIES (like color, shape, and serial #). In reality, we have 5 such properties:
#  1. Current scan step
#  2. Current measurement
#  3. Current modstate
#  4. Current sub repeat
#  5. Obs time
#
# Obs time is monotonically increasing and never repeats. It is the serial number in the analogy.
#
# A single frame gets ingested into a `SingleScanStep`. This is just a convenience container for the OBSERVABLE
# PROPERTIES we care about. A `SingleScanStep` is like a single block in the analogy.
#
# `MapScanStepStemBase.scan_step_dict` is how we sort frames based on their OBSERVABLE PROPERTIES. Instead of a pile
# of green spheres imagine a bag labeled "spheres" containing 3 sub-bags, each labeled by color. Each bag in that
# analogy is a level of the `scan_step_dict` dictionary; one for each of the OBSERVABLE PROPERTIES.
# If we go to the innermost level of that dictionary we will find a list of `SingleScanStep` objects. This is like
# going into the "sphere" bag, then the "green" bag and finding 3 blocks (for the three different woods)*.
#
# The number of `SingleScanStep` objects at the innermost level of `scan_step_dict` is the number of map scans.
#
# We can also use the `scan_step_dict` to figure out which map scan a frame comes from. This is what
# `MapScanStepStemBase.get_map_scan_for_key()` does. It sorts the innermost list by obs time and then figures out
# where in the resulting order the current frame belongs.
#
# Finally, once we can segregate frames (i.e., `SingleScanStep` objects) by map scan, we are able to figure out
# the number of scan steps in each map scan. This is what the methods in `NumberOfScanStepsBud` do and they allow us
# to account for aborts.
# Back to the analogy, we don't want different numbers of, e.g., green spheres and red cubes. If the factory stops after
# processing at least one full board (map scan) then we only accept blocks that come from complete boards because we
# have at least one full set of (color, shape) blocks. If, however, the factory aborts during the first board then we
# will be OK with a complete set of blocks of the same shape (scan step). So if the factory stops while making the
# green cube then we'll just take all the spheres throw away all the cubes.
#
#########
#
# Hopefully this helps you understand how we are able to sort by map scan even though there is no header key for it.
# We use our knowledge the loops that produce the data (GENERATING PROCESS) and the header values for scan step,
# measurement, modstate, sub repeat, and obs time (OBSERVABLE PROPERTIES) to infer the map scan (UNOBSERVABLE PROPERTY).
#
#
# *(We actually could make just single flat "piles" of blocks instead of nested bags/dictionaries. This would mean using
#   keys like `f"{obj.scan_step}_{obj.measurement}_{obj.modstate}_{obj.sub_repeat}"`, which is pretty weird from a
#   coding perspective).
from __future__ import annotations

from abc import ABC
from collections import defaultdict
from functools import cached_property
from typing import Type

from astropy.time import Time
from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.parsers.single_value_single_key_flower import (
    SingleValueSingleKeyFlower,
)

from dkist_processing_cryonirsp.models.constants import CryonirspBudName
from dkist_processing_cryonirsp.models.tags import CryonirspStemName
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import CryonirspL0FitsAccess


def zero_size_scan_step_test(fits_obj) -> bool:
    """Test if the dual internal scan loop trick is being used."""
    if fits_obj.num_cn2_scan_steps > 0 and fits_obj.cn2_step_size == 0:
        return fits_obj.cn2_step_size == 0
    return False


def single_scan_step_key(fits_obj: CryonirspL0FitsAccess):
    """Return the single_step_key based on how the scanning is being done."""
    if zero_size_scan_step_test(fits_obj):
        return "cn1_scan_step"
    return "scan_step"


def total_num_key(fits_obj: CryonirspL0FitsAccess):
    """Return the total_num_key based on how the scanning is being done."""
    if zero_size_scan_step_test(fits_obj):
        return "num_cn1_scan_steps"
    return "num_scan_steps"


class SingleScanStep:
    """
    An object that uniquely defines a (scan_step, meas_num, modstate, sub_rep, time_obs) tuple from any number of dsps repeat repeats.

    This is just a fancy tuple.

    Basically, it just hashes the (scan_step, meas_num, modstate, sub_rep, time_obs) tuple so these objects can easily be compared.
    Also uses the time_obs property so that multiple dsps repeats of the same (scan_step, meas_num, modstate, sub_rep) can be sorted.
    """

    def __init__(self, fits_obj: CryonirspL0FitsAccess):
        """Read relevant values from a FitsAccess object."""
        self.num_scan_steps = self.get_num_scan_steps_value(fits_obj)
        self.scan_step = self.get_scan_step_value(fits_obj)
        self.meas_num = fits_obj.meas_num
        self.modulator_state = fits_obj.modulator_state
        self.sub_repeat_num = fits_obj.sub_repeat_num
        self.date_obs = Time(fits_obj.time_obs)

        # For __repr__
        self._fits_obj = fits_obj

    @staticmethod
    def get_scan_step_value(fits_obj: CryonirspL0FitsAccess) -> int:
        """Return the scan_step based on how the scanning is being done."""
        return getattr(fits_obj, single_scan_step_key(fits_obj))

    @staticmethod
    def get_num_scan_steps_value(fits_obj: CryonirspL0FitsAccess) -> int:
        """Return the header value for the total number of scan steps while accounting for different modes of scanning."""
        return getattr(fits_obj, total_num_key(fits_obj))

    def __repr__(self):
        return f"{self.__class__.__name__}({self._fits_obj!r})"

    def __str__(self):
        return (
            f"SingleScanStep with {self.date_obs = }, "
            f"{self.num_scan_steps = }, "
            f"{self.scan_step = }, "
            f"{self.meas_num = }, "
            f"{self.modulator_state = }, "
            f"and {self.sub_repeat_num = }"
        )

    def __eq__(self, other: SingleScanStep) -> bool:
        """
        Two frames are equal if they have the same (scan_step, meas_num, modstate, sub_rep) tuple.

        Doesn't account for num_scan_steps because it *should* be the same for all objects and the test of that
        singularity exists elsewhere (i.e., we don't want a bad num_scan_steps value to affect comparison of these
        objects).
        """
        if not isinstance(other, SingleScanStep):
            raise TypeError(f"Cannot compare ScanStep with type {type(other)}")

        for attr in ["scan_step", "modulator_state", "date_obs", "meas_num", "sub_repeat_num"]:
            if getattr(self, attr) != getattr(other, attr):
                return False

        return True

    def __lt__(self, other: SingleScanStep) -> bool:
        """Only sort on date_obs."""
        return self.date_obs < other.date_obs

    def __hash__(self) -> int:
        """
        Not strictly necessary, but does allow for using set() on these objects.

        Doesn't account for num_scan_steps because it *should* be the same for all objects and the test of that
        singularity exists elsewhere (i.e., we don't want a bad num_scan_steps value to affect comparison of these
        objects).
        """
        return hash(
            (
                self.scan_step,
                self.meas_num,
                self.modulator_state,
                self.sub_repeat_num,
                self.date_obs,
            )
        )


class MapScanStepStemBase(Stem, ABC):
    """Base class for Stems that determine the sorting of map scans and scan steps."""

    # This only here so type-hinting of this complex dictionary will work.
    key_to_petal_dict: dict[str, SingleScanStep]

    def setter(self, fits_obj: CryonirspL0FitsAccess) -> SingleScanStep | Type[SpilledDirt]:
        """Ingest observe frames as SingleScanStep objects."""
        if fits_obj.ip_task_type != "observe":
            return SpilledDirt
        return SingleScanStep(fits_obj=fits_obj)

    @cached_property
    def scan_step_dict(self) -> dict[int, dict[int, dict[int, dict[int, list[SingleScanStep]]]]]:
        """Nested dictionary that contains a SingleScanStep for each ingested frame.

        Dictionary structure is::

            {scan_step:
              {measurement:
                {modstate:
                  {sub_repeat:
                    [SingleScanStep1, SingleScanStep2, ...]
                  }
                }
              }
            }

        """
        scan_step_dict = defaultdict(
            lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        )

        for scan_step_obj in self.key_to_petal_dict.values():
            scan_step_dict[scan_step_obj.scan_step][scan_step_obj.meas_num][
                scan_step_obj.modulator_state
            ][scan_step_obj.sub_repeat_num].append(scan_step_obj)

        return scan_step_dict

    @cached_property
    def number_of_complete_map_scans(self) -> int:
        """Compute the total number of complete map scans.

        In a multi-map dataset a complete map scan is defined as a map scan that contains a complete
        set of scan steps. In other words, each scan step will be present in the same number of
        *complete* map scans when the entire set of scan steps is considered.

        The map scan in a dataset with a single map scan is condsidered complete by default. (If it is missing
        scan steps it will simply be truncated).

        Assumes the incomplete map_scan is always the last one due to summit abort or cancellation.
        """
        map_scans_per_scan_step = []
        for meas_dict in self.scan_step_dict.values():
            for mod_dict in meas_dict.values():
                for sub_repeat_dict in mod_dict.values():
                    files_per_subrepeat = []
                    for file_list in sub_repeat_dict.values():
                        files_per_subrepeat.append(len(file_list))

                    # Using `max` here makes us somewhat resistant to aborted-then-continued data
                    # (or just missing frames).
                    map_scans_per_scan_step.append(max(files_per_subrepeat))

        if max(map_scans_per_scan_step) - min(map_scans_per_scan_step) > 1:
            raise ValueError("More than one incomplete map exists in the data.")

        return min(map_scans_per_scan_step)

    def get_map_scan_for_key(self, key) -> int:
        """Compute the map scan number for a single frame.

        The frame implies a SingleScanStep. That object is then compared to the sorted list of objects for a single
        (raster_step, meas_num, modstate, sub_repeat) tuple. The location within that sorted list is the map scan number.
        """
        scan_step_obj = self.key_to_petal_dict[key]
        step_list: list[SingleScanStep] = sorted(
            self.scan_step_dict[scan_step_obj.scan_step][scan_step_obj.meas_num][
                scan_step_obj.modulator_state
            ][scan_step_obj.sub_repeat_num]
        )

        num_exp = step_list.count(scan_step_obj)
        if num_exp > 1:
            raise ValueError(
                f"More than one exposure detected for a single map scan of a single map step. (Randomly chosen step has {num_exp} exposures)."
            )
        return step_list.index(scan_step_obj) + 1  # Here we decide that map scan indices start at 1


class NumberOfScanStepsBase(MapScanStepStemBase, ABC):
    """Base class for managing scan steps."""

    def __init__(self, stem_name: CryonirspBudName):
        super().__init__(stem_name=stem_name)

    @cached_property
    def map_scan_to_obj_dict(self) -> dict[int, list[SingleScanStep]]:
        """Sort SingleScanStep objects by what map scan they belong to."""
        map_scan_to_obj_dict = defaultdict(list)
        for key, single_step_obj in self.key_to_petal_dict.items():
            map_scan = self.get_map_scan_for_key(key)
            map_scan_to_obj_dict[map_scan].append(single_step_obj)

        return map_scan_to_obj_dict

    def steps_in_map_scan(self, map_scan: int) -> int:
        """
        Compute the number of scan steps in the given map scan.

        First we check how many files (i.e., `SingleScanStep` objects) belong to each scan step. The number of files
        in a completed scan step is assumed to be the maximum of this set. Any scan steps with fewer than this number
        are discarded, and finally we check that the remaining scan steps (i.e., those that have completed) are
        continuous. This check ensures that any aborted scan steps were at the end of a sequence.
        """
        objs_in_map_scan_list = self.map_scan_to_obj_dict[map_scan]

        scan_step_to_objs_dict = defaultdict(list)
        for obj in objs_in_map_scan_list:
            scan_step_to_objs_dict[obj.scan_step].append(obj)

        # Using the dict keys ensures there are no repeats
        sorted_steps = sorted(scan_step_to_objs_dict.keys())
        files_per_step = [len(scan_step_to_objs_dict[step]) for step in sorted_steps]

        completed_step_size = max(files_per_step)  # A relatively safe assumption
        indices_of_completed_steps = [
            idx for idx, num_files in enumerate(files_per_step) if num_files == completed_step_size
        ]

        # Now check that all the steps we expect are present
        # Incomplete steps are allowed *only at the end of the sequence*. I.e., if an incomplete step is followed
        # by a complete step then the ValueError will be triggered.
        completed_steps = [sorted_steps[i] for i in indices_of_completed_steps]
        if completed_steps != list(range(1, max(completed_steps) + 1)):
            raise ValueError(f"Not all sequential steps could be found. Found {completed_steps}")

        return len(completed_steps)


class NumberOfScanStepsBud(NumberOfScanStepsBase):
    """Bud for finding the total number of scan steps."""

    def __init__(self):
        super().__init__(stem_name=CryonirspBudName.num_scan_steps.value)

    def getter(self, key):
        """
        Compute the number of complete scan steps.

        In cases where there is only a single map scan the number of scan steps is equal to the number of completed
        scan steps. In cases where there multiple map scans, only completed map scans are considered and an Error is
        raised if they each have a different number of scan steps.

        An error is also raised if the set of values of the "CNNUMSCN" header key (number of scan steps) contains more
        than one value.
        """
        # We still want to check that all files have the same value for NUM_SCAN_STEPS
        num_steps_set = set(v.num_scan_steps for v in self.key_to_petal_dict.values())
        if len(num_steps_set) > 1:
            raise ValueError(f"Multiple {self.stem_name} values found. Values: {num_steps_set}")

        steps_per_map_scan_set = set(
            self.steps_in_map_scan(map_scan)
            for map_scan in range(1, self.number_of_complete_map_scans + 1)
        )
        if len(steps_per_map_scan_set) > 1:
            raise ValueError(
                "The set of non-aborted maps have varying numbers of scan steps. This is very strange "
                "and likely indicates a failure to parse the aborted map scans."
            )

        return steps_per_map_scan_set.pop()


class ScanStepNumberFlower(SingleValueSingleKeyFlower):
    """Flower for a scan step."""

    def __init__(self):
        super().__init__(tag_stem_name=CryonirspStemName.scan_step.value, metadata_key="")

    def setter(self, fits_obj: CryonirspL0FitsAccess):
        """
        Setter for a flower.

        Parameters
        ----------
        fits_obj:
            A single FitsAccess object
        """
        if fits_obj.ip_task_type != "observe":
            return SpilledDirt
        # Set the meta-data key, which isn't known at object creation time.
        self.metadata_key = single_scan_step_key(fits_obj)
        return super().setter(fits_obj)
