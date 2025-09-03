"""CryoNIRSP calibration pipeline parameters."""

from datetime import datetime
from functools import cached_property

import astropy.units as u
import numpy as np
from dkist_processing_common.models.parameters import ParameterArmIdMixin
from dkist_processing_common.models.parameters import ParameterBase
from dkist_processing_common.models.parameters import ParameterWavelengthMixin
from solar_wavelength_calibration import DownloadConfig

from dkist_processing_cryonirsp.models.exposure_conditions import AllowableOpticalDensityFilterNames


class CryonirspParsingParameters(ParameterBase):
    """
    Parameters specifically (and only) for the Parse task.

    Needed because the Parse task doesn't yet know about arm id, wavelength, or obs_ip_start_time, which are all
    required to initialize the main parameter class.
    """

    @property
    def max_cs_step_time_sec(self):
        """Time window within which CS steps with identical GOS configurations are considered to be the same."""
        return self._find_most_recent_past_value(
            "cryonirsp_max_cs_step_time_sec", start_date=datetime.now()
        )


class CryonirspParameters(ParameterBase, ParameterWavelengthMixin, ParameterArmIdMixin):
    """Put all CryoNIRSP parameters parsed from the input dataset document in a single property."""

    @property
    def geo_upsample_factor(self) -> int:
        """Pixel precision (1/upsample_factor) to use during phase matching of beam/modulator images."""
        return self._find_most_recent_past_value("cryonirsp_geo_upsample_factor")

    @property
    def geo_max_shift(self) -> int:
        """Max allowed pixel shift when computing spectral curvature."""
        return self._find_most_recent_past_value("cryonirsp_geo_max_shift")

    @property
    def geo_poly_fit_order(self) -> int:
        """Order of polynomial used to fit spectral shift as a function of slit position."""
        return self._find_most_recent_past_value("cryonirsp_geo_poly_fit_order")

    @property
    def geo_long_axis_gradient_displacement(self) -> int:
        """Number of pixels to shift along the long axis of a strip when computing a gradient."""
        return self._find_most_recent_past_value("cryonirsp_geo_long_axis_gradient_displacement")

    @property
    def geo_strip_long_axis_size_fraction(self) -> float:
        """Fraction of full array size for the long axis of the strips used to find the beam angle."""
        return self._find_most_recent_past_value("cryonirsp_geo_strip_long_axis_size_fraction")

    @property
    def geo_strip_short_axis_size_fraction(self) -> float:
        """Fraction of full array size for the short axis of the strips used to find the beam angle."""
        return self._find_most_recent_past_value("cryonirsp_geo_strip_short_axis_size_fraction")

    @property
    def geo_strip_spectral_offset_size_fraction(self) -> float:
        """Fraction of full spectral size to set as the +/- offset from spectral center for the two strips used to find the beam angle."""
        return self._find_most_recent_past_value(
            "cryonirsp_geo_strip_spectral_offset_size_fraction"
        )

    @property
    def polcal_num_spectral_bins(self) -> int:
        """Return Number of demodulation matrices to compute across the entire FOV in the spectral dimension."""
        return self._find_most_recent_past_value("cryonirsp_polcal_num_spectral_bins")

    @property
    def polcal_num_spatial_bins(self) -> int:
        """Return Number of demodulation matrices to compute across the entire FOV in the spatial dimension."""
        return self._find_most_recent_past_value("cryonirsp_polcal_num_spatial_bins")

    @property
    def polcal_pac_fit_mode(self):
        """Name of set of fitting flags to use during PAC Calibration Unit parameter fits."""
        return self._find_most_recent_past_value("cryonirsp_polcal_pac_fit_mode")

    @property
    def beam_boundaries_smoothing_disk_size(self) -> int:
        """Return the size of the smoothing disk (in pixels) to be used in the beam boundaries computation."""
        return self._find_most_recent_past_value("cryonirsp_beam_boundaries_smoothing_disk_size")

    @property
    def beam_boundaries_upsample_factor(self) -> int:
        """Return the upsample factor to be used in the beam boundaries cross correlation computation."""
        return self._find_most_recent_past_value("cryonirsp_beam_boundaries_upsample_factor")

    @property
    def beam_boundaries_sp_beam_transition_region_size_fraction(self) -> float:
        """
        Fraction of full spectral size to use as the size of the transition region between the two SP beams.

        A region with size = (this parameter * full spectral size) and centered at the center of the spectral dimension
        will be ignored when extracting the beams.
        """
        return self._find_most_recent_past_value(
            "cryonirsp_beam_boundaries_sp_beam_transition_region_size_fraction"
        )

    @property
    def bad_pixel_map_median_filter_size(self) -> list[int, int]:
        """Return the smoothing disk size to be used in the bad pixel map computation."""
        filter_size = self._find_parameter_for_arm("cryonirsp_bad_pixel_map_median_filter_size")
        return filter_size

    @property
    def bad_pixel_map_threshold_factor(self) -> float:
        """Return the threshold multiplicative factor to be used in the bad pixel map computation."""
        return self._find_most_recent_past_value("cryonirsp_bad_pixel_map_threshold_factor")

    @property
    def corrections_bad_pixel_median_filter_size(self) -> int:
        """Return the size of the median filter to be used for bad pixel correction."""
        return self._find_most_recent_past_value(
            "cryonirsp_corrections_bad_pixel_median_filter_size"
        )

    @cached_property
    def corrections_bad_pixel_fraction_threshold(self) -> float:
        """
        Return the fraction of the bad pixel mask.

        If exceeded, will cause the fallback to a faster but worse algorithm.
        """
        return self._find_most_recent_past_value(
            "cryonirsp_corrections_bad_pixel_fraction_threshold"
        )

    @cached_property
    def linearization_thresholds(self) -> np.ndarray:
        """Name of parameter associated with the linearization thresholds."""
        param_obj = self._find_parameter_for_arm("cryonirsp_linearization_thresholds")
        value = self._load_param_value_from_numpy_save(param_obj=param_obj)
        # float64 data can blow up the memory required for linearization - convert to float32
        if np.issubdtype(value.dtype, np.float64):
            value = value.astype(np.float32, casting="same_kind")
        return value

    @cached_property
    def linearization_polyfit_coeffs(self) -> np.ndarray:
        """Name of parameter associated with the linearization polyfit coefficients."""
        param_value = self._find_parameter_for_arm("cryonirsp_linearization_polyfit_coeffs")
        return np.asarray(param_value, dtype=np.float32)

    @cached_property
    def linearization_max_memory_gb(self) -> float:
        """Get the maximum amount of memory in GB available to the linearity correction task worker."""
        mem_size = self._find_most_recent_past_value("cryonirsp_linearization_max_memory_gb")
        return mem_size

    @property
    def solar_characteristic_spatial_normalization_percentile(self) -> float:
        """Percentile to pass to `np.nanpercentile` when normalizing each spatial position of the characteristic spectra."""
        return self._find_most_recent_past_value(
            "cryonirsp_solar_characteristic_spatial_normalization_percentile"
        )

    @property
    def fringe_correction_on(self) -> bool:
        """Return True if fringe correction should be performed."""
        return self._find_most_recent_past_value(
            "cryonirsp_fringe_correction_on",
            start_date=self._obs_ip_start_datetime,
        )

    @property
    def fringe_correction_spectral_filter_size(self) -> list[int, int]:
        """Get the filter kernel size for the spectral filtering in the fringe removal process."""
        return self._find_most_recent_past_value("cryonirsp_fringe_correction_spectral_filter_size")

    @property
    def fringe_correction_spatial_filter_size(self) -> list[int, int]:
        """Get the filter kernel size for the spatial filtering in the fringe removal process."""
        return self._find_most_recent_past_value("cryonirsp_fringe_correction_spatial_filter_size")

    @property
    def fringe_correction_lowpass_cutoff_period(self) -> float:
        """Get the lowpass filter cutoff period in pixels for the fringe removal process."""
        return self._find_most_recent_past_value(
            "cryonirsp_fringe_correction_lowpass_cutoff_period"
        )

    @cached_property
    def linearization_filter_attenuation_dict(self) -> dict:
        """Return a dict that maps the filter name to its attenuation parameter."""
        filter_attenuation_dict = {
            AllowableOpticalDensityFilterNames.G278.value: self._linearization_optical_density_filter_attenuation_g278,
            AllowableOpticalDensityFilterNames.G358.value: self._linearization_optical_density_filter_attenuation_g358,
            AllowableOpticalDensityFilterNames.G408.value: self._linearization_optical_density_filter_attenuation_g408,
            AllowableOpticalDensityFilterNames.OPEN.value: self._linearization_optical_density_filter_attenuation_open,
            AllowableOpticalDensityFilterNames.NONE.value: self._linearization_optical_density_filter_attenuation_none,
        }
        return filter_attenuation_dict

    @cached_property
    def _linearization_optical_density_filter_attenuation_g278(self) -> float:
        """Return the attenuation value for the G278 filter."""
        return self._find_parameter_closest_wavelength(
            "cryonirsp_linearization_optical_density_filter_attenuation_g278"
        )

    @cached_property
    def _linearization_optical_density_filter_attenuation_g358(self) -> float:
        """Return the attenuation value for the G358 filter."""
        return self._find_parameter_closest_wavelength(
            "cryonirsp_linearization_optical_density_filter_attenuation_g358"
        )

    @cached_property
    def _linearization_optical_density_filter_attenuation_g408(self) -> float:
        """Return the attenuation value for the G408 filter."""
        return self._find_parameter_closest_wavelength(
            "cryonirsp_linearization_optical_density_filter_attenuation_g408"
        )

    @cached_property
    def _linearization_optical_density_filter_attenuation_none(self) -> float:
        """Return the attenuation value for a filter of 'none'."""
        return 0.0

    @cached_property
    def _linearization_optical_density_filter_attenuation_open(self) -> float:
        """Return the attenuation value for a filter of 'Open'."""
        return 0.0

    @property
    def cryo_instrument_alignment_angle(self) -> u.Quantity:
        """Return the CryoNIRSP instrument alignment angle."""
        alignment_angle = -91.0 * u.deg
        return alignment_angle

    @property
    def ci_spatial_scale_along_slit(self) -> u.Quantity:
        """Return the CryoNIRSP CI spatial scale along the slit."""
        spatial_scale_along_slit = 0.05308 * u.arcsec / u.pix
        return spatial_scale_along_slit

    @property
    def sp_spatial_scale_along_slit(self) -> u.Quantity:
        """Return the CryoNIRSP SP spatial scale along the slit."""
        spatial_scale_along_slit = 0.12 * u.arcsec / u.pix
        return spatial_scale_along_slit

    @property
    def mirror_scan_recalibration_constant(self) -> float:
        """Return the CryoNIRSP mirror scan recalibration constant."""
        mirror_scan_recalibration_constant = 0.466 / 0.5
        return mirror_scan_recalibration_constant

    @property
    def camera_mirror_focal_length_mm(self) -> u.Quantity:
        """Return the CryoNIRSP camera mirror focal length."""
        return (
            self._find_most_recent_past_value("cryonirsp_camera_mirror_focal_length_mm")
            * u.millimeter
        )

    @property
    def pixel_pitch_micron(self) -> u.Quantity:
        """Return the CryoNIRSP pixel pitch."""
        return self._find_most_recent_past_value("cryonirsp_pixel_pitch_micron") * u.micron

    @property
    def wavecal_atlas_download_config(self) -> DownloadConfig:
        """Define the `~solar_wavelength_calibration.DownloadConfig` used to grab the Solar atlas used for wavelength calibration."""
        config_dict = self._find_most_recent_past_value("cryonirsp_wavecal_atlas_download_config")
        return DownloadConfig.model_validate(config_dict)

    @cached_property
    def wavecal_fraction_of_unweighted_edge_pixels(self) -> int:
        """Return the fraction of edge pixels to weight to zero during the wavelength calibration."""
        return self._find_most_recent_past_value(
            "cryonirsp_wavecal_fraction_of_unweighted_edge_pixels"
        )
