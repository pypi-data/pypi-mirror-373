"""List of intermediate task names."""

from enum import Enum


class CryonirspTaskName(str, Enum):
    """Controlled list of CryoNirsp task tag names."""

    beam_boundaries = "BEAM_BOUNDARIES"
    bad_pixel_map = "BAD_PIXEL_MAP"
    polcal_dark = "POLCAL_DARK"
    polcal_gain = "POLCAL_GAIN"
    spectral_corrected_solar_array = "SPECTRAL_CORRECTED_SOLAR_ARRAY"
    spectral_fit = "SPECTRAL_FIT"
    solar_char_spec = "SOLAR_CHAR_SPEC"
