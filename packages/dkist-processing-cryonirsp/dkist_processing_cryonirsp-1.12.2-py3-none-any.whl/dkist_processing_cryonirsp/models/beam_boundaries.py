"""Beam boundary class."""

from dataclasses import dataclass

import numpy as np


@dataclass
class BeamBoundary:
    """Simple dataclass to hold boundary information for the illuminated portion of the beam array."""

    y_min: int
    y_max: int
    x_min: int
    x_max: int

    @property
    def y_slice(self):
        """Return a slice object representing the illumination along the y-axis (numpy 0 axis)."""
        return slice(self.y_min, self.y_max)

    @property
    def x_slice(self):
        """Return a slice object representing the illumination along the x-axis (numpy 1 axis)."""
        return slice(self.x_min, self.x_max)

    @property
    def slices(self):
        """Return a tuple of slices in numpy order representing the illuminated portion of the beam array."""
        return self.y_slice, self.x_slice

    @property
    def beam_boundaries(self):
        """Return a tuple containing the beam boundaries."""
        return self.y_min, self.y_max, self.x_min, self.x_max

    @property
    def beam_boundaries_array(self):
        """Return a tuple containing the beam boundaries."""
        return np.array(self.beam_boundaries)
