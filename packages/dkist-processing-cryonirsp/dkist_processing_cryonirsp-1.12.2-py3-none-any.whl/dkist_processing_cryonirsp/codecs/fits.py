"""Encoders and decoders for writing and reading Cryo-NIRSP FITS files."""

from pathlib import Path

import numpy as np
from dkist_processing_common.codecs.fits import fits_access_decoder as common_fits_access_decoder
from dkist_processing_common.models.fits_access import FitsAccessBase

from dkist_processing_cryonirsp.models.beam_boundaries import BeamBoundary


def cryo_fits_access_decoder(
    path: Path,
    fits_access_class: FitsAccessBase = FitsAccessBase,
    beam_boundary: BeamBoundary | None = None,
    **fits_access_kwargs,
) -> FitsAccessBase:
    """
    Read a Path with `fits`, ingest into a `FitsAccessBase`-type object, then slice out the beam.

    Cryo-specific replacement for method from `dkist-processing-common` with the same name.
    """
    frame = common_fits_access_decoder(
        path, fits_access_class=fits_access_class, **fits_access_kwargs
    )

    if beam_boundary is not None:
        frame.data = frame.data[beam_boundary.slices]

    return frame


def cryo_fits_array_decoder(
    path: Path,
    fits_access_class: FitsAccessBase = FitsAccessBase,
    beam_boundary: BeamBoundary | None = None,
    auto_squeeze: bool = True,
    **fits_access_kwargs,
) -> np.array:
    """
    Read a Path with `fits` and return the `.data` from `fits_access_decoder`.

    Cryo-specific replacement for method from `dkist-processing-common` with the same name.
    Unlike the version in `-common`, this method allows a fits_access_class parameter.
    """
    frame = cryo_fits_access_decoder(
        path,
        fits_access_class=fits_access_class,
        beam_boundary=beam_boundary,
        auto_squeeze=auto_squeeze,
        **fits_access_kwargs,
    )
    return frame.data
