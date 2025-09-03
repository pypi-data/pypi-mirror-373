"""Cryonirsp write L1 task."""

from abc import ABC
from abc import abstractmethod
from functools import cached_property
from typing import Callable
from typing import Literal

import astropy.units as u
import numpy as np
from astropy.coordinates.builtin_frames.altaz import AltAz
from astropy.coordinates.sky_coordinate import SkyCoord
from astropy.io import fits
from astropy.time.core import Time
from dkist_processing_common.codecs.json import json_decoder
from dkist_processing_common.models.dkist_location import location_of_dkist
from dkist_processing_common.models.wavelength import WavelengthRange
from dkist_processing_common.tasks import WriteL1Frame
from sunpy.coordinates import GeocentricEarthEquatorial
from sunpy.coordinates import Helioprojective

from dkist_processing_cryonirsp.models.constants import CryonirspConstants
from dkist_processing_cryonirsp.models.parameters import CryonirspParameters
from dkist_processing_cryonirsp.models.tags import CryonirspTag

__all__ = ["CIWriteL1Frame", "SPWriteL1Frame"]


class CryonirspWriteL1Frame(WriteL1Frame, ABC):
    """
    Task class for writing out calibrated l1 CryoNIRSP frames.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs
    """

    def __init__(
        self,
        recipe_run_id: int,
        workflow_name: str,
        workflow_version: str,
    ):
        super().__init__(
            recipe_run_id=recipe_run_id,
            workflow_name=workflow_name,
            workflow_version=workflow_version,
        )
        self.parameters = CryonirspParameters(
            scratch=self.scratch,
            obs_ip_start_time=self.constants.obs_ip_start_time,
            wavelength=self.constants.wavelength,
            arm_id=self.constants.arm_id,
        )

    @property
    def constants_model_class(self):
        """Get Cryonirsp pipeline constants."""
        return CryonirspConstants

    def add_dataset_headers(
        self, header: fits.Header, stokes: Literal["I", "Q", "U", "V"]
    ) -> fits.Header:
        """
        Add the Cryonirsp specific dataset headers to L1 FITS files.

        Parameters
        ----------
        header : fits.Header
            calibrated data header

        stokes :
            stokes parameter

        Returns
        -------
        fits.Header
            calibrated header with correctly written l1 headers
        """
        first_axis = 1
        next_axis = self.add_first_axis(header, axis_num=first_axis)
        next_axis = self.add_second_axis(header, axis_num=next_axis)
        multiple_measurements = self.constants.num_meas > 1
        if multiple_measurements:
            next_axis = self.add_measurement_axis(header, next_axis)
        next_axis = self.add_scan_step_axis(header, axis_num=next_axis)
        if self.constants.num_map_scans > 1:
            next_axis = self.add_map_scan_axis(header, axis_num=next_axis)
        if self.constants.correct_for_polarization:
            next_axis = self.add_stokes_axis(header, stokes=stokes, axis_num=next_axis)
        last_axis = next_axis - 1
        self.add_common_headers(header, num_axes=last_axis)
        self.flip_spectral_axis(header)
        boresight_coordinates = self.get_boresight_coords(header)
        self.correct_spatial_wcs_info(header, boresight_coordinates)
        self.update_spectral_headers(header)
        self.add_wavelength_headers(header)

        return header

    @property
    @abstractmethod
    def latitude_pixel_name(self) -> str:
        """Return the descriptive name for the longitudinal axis."""
        pass

    @property
    @abstractmethod
    def add_first_axis(self) -> Callable:
        """Return the add method for the first axis."""
        pass

    @property
    @abstractmethod
    def add_second_axis(self) -> Callable:
        """Return the add method for the second axis."""
        pass

    def flip_spectral_axis(self, header: fits.Header):
        """Adjust header values corresponding to axis flip."""
        pass

    def add_helioprojective_latitude_axis(self, header: fits.Header, axis_num: int) -> int:
        """Add header keys for the spatial helioprojective latitude axis."""
        header[f"DNAXIS{axis_num}"] = header[f"NAXIS{axis_num}"]
        header[f"DTYPE{axis_num}"] = "SPATIAL"
        header[f"DPNAME{axis_num}"] = self.latitude_pixel_name
        header[f"DWNAME{axis_num}"] = "helioprojective latitude"
        header[f"CNAME{axis_num}"] = "helioprojective latitude"
        header[f"DUNIT{axis_num}"] = header[f"CUNIT{axis_num}"]
        next_axis = axis_num + 1
        return next_axis

    def add_measurement_axis(self, header: fits.Header, axis_num: int) -> int:
        """Add header keys related to multiple measurements."""
        header[f"DNAXIS{axis_num}"] = self.constants.num_meas
        header[f"DTYPE{axis_num}"] = "TEMPORAL"
        header[f"DPNAME{axis_num}"] = "measurement number"
        header[f"DWNAME{axis_num}"] = "time"
        header[f"DUNIT{axis_num}"] = "s"
        # DINDEX and CNCMEAS are both one-based
        header[f"DINDEX{axis_num}"] = header["CNCMEAS"]
        next_axis = axis_num + 1
        return next_axis

    @abstractmethod
    def add_scan_step_axis(self, header: fits.Header, axis_num: int) -> int:
        pass

    def add_map_scan_axis(self, header: fits.Header, axis_num: int) -> int:
        """Add header keys for the temporal map scan axis."""
        header["CNNMAPS"] = self.constants.num_map_scans
        header[f"DNAXIS{axis_num}"] = self.constants.num_map_scans
        header[f"DTYPE{axis_num}"] = "TEMPORAL"
        header[f"DPNAME{axis_num}"] = "map scan number"
        header[f"DWNAME{axis_num}"] = "time"
        header[f"DUNIT{axis_num}"] = "s"
        # Temporal position in dataset
        # DINDEX and CNMAP are both one-based
        header[f"DINDEX{axis_num}"] = header["CNMAP"]
        next_axis = axis_num + 1
        return next_axis

    def add_stokes_axis(
        self, header: fits.Header, stokes: Literal["I", "Q", "U", "V"], axis_num: int
    ) -> int:
        """Add header keys for the stokes polarization axis."""
        header[f"DNAXIS{axis_num}"] = 4  # I, Q, U, V
        header[f"DTYPE{axis_num}"] = "STOKES"
        header[f"DPNAME{axis_num}"] = "polarization state"
        header[f"DWNAME{axis_num}"] = "polarization state"
        header[f"DUNIT{axis_num}"] = ""
        # Stokes position in dataset - stokes axis goes from 1-4
        header[f"DINDEX{axis_num}"] = self.constants.stokes_params.index(stokes.upper()) + 1
        next_axis = axis_num + 1
        return next_axis

    def add_wavelength_headers(self, header: fits.Header) -> None:
        """Add header keys related to the observing wavelength."""
        # The wavemin and wavemax assume that all frames in a dataset have identical wavelength axes
        header["WAVEUNIT"] = -9  # nanometers
        header["WAVEREF"] = "Air"
        wavelength_range = self.get_wavelength_range(header)
        header["WAVEMIN"] = wavelength_range.min.to(u.nm).value
        header["WAVEMAX"] = wavelength_range.max.to(u.nm).value

    @staticmethod
    def add_common_headers(header: fits.Header, num_axes: int) -> None:
        """Add header keys that are common to both SP and CI."""
        header["DNAXIS"] = num_axes
        header["DAAXES"] = 2  # Spatial, spatial
        header["DEAXES"] = num_axes - 2  # Total - detector axes
        header["LEVEL"] = 1
        # Binning headers
        header["NBIN1"] = 1
        header["NBIN2"] = 1
        header["NBIN3"] = 1
        header["NBIN"] = header["NBIN1"] * header["NBIN2"] * header["NBIN3"]

        # Values don't have any units because they are relative to disk center
        header["BUNIT"] = ("", "Values are relative to disk center. See calibration docs.")

    def calculate_date_end(self, header: fits.Header) -> str:
        """
        In CryoNIRSP, the instrument specific DATE-END keyword is calculated during science calibration.

        Check that it exists.

        Parameters
        ----------
        header
            The input fits header
        """
        try:
            return header["DATE-END"]
        except KeyError as e:
            raise KeyError(
                f"The 'DATE-END' keyword was not found. "
                f"Was supposed to be inserted during science calibration."
            ) from e

    def l1_filename(self, header: fits.Header, stokes: Literal["I", "Q", "U", "V"]):
        """
        Use a FITS header to derive its filename in the following format.

        instrument_arm_datetime_wavelength__stokes_datasetid_L1.fits.

        This is done by taking the base filename and changing the instrument name to include the arm.

        Example
        -------
        "CRYO-NIRSP_CI_2020_03_13T00_00_00_000_01080000_Q_DATID_L1.fits"

        Parameters
        ----------
        header
            The input fits header
        stokes
            The stokes parameter

        Returns
        -------
        The L1 filename including the arm ID
        """
        base_l1_filename = super().l1_filename(header, stokes)
        return base_l1_filename.replace(
            self.constants.instrument, f"{self.constants.instrument}_{self.constants.arm_id}"
        )

    @abstractmethod
    def get_boresight_coords(self, header: fits.Header) -> tuple[float, float]:
        """Get boresight coordinates to use in spatial correction."""
        pass

    def correct_spatial_wcs_info(
        self, header: fits.Header, boresight_coordinates: tuple[float, float]
    ) -> None:
        """
        Correct spatial WCS info.

        CryoNIRSP is not exactly where it thinks it is in space, resulting in the spatial coordinates being off.

        Steps:
        1. Get target coordinates from boresight coordinates.
        2. Find the solar orientation at the time of observation by finding the angle
        between the zenith and solar north at the center boresight pointing.
        3. Find the instrument slit orientation at the time of observation by finding the
        sun center azimuth and elevation, and calculate the slit orientation angle using those values.
        4. Correct and update the helioprojective headers.
        5. Correct and update the equatorial headers.

        Returns
        -------
        None
        """
        t0 = Time(header["DATE-BEG"])
        sky_coordinates = SkyCoord(
            boresight_coordinates[0] * u.arcsec,
            boresight_coordinates[1] * u.arcsec,
            obstime=t0,
            observer=location_of_dkist.get_itrs(t0),
            frame="helioprojective",
        )

        frame_altaz = AltAz(obstime=t0, location=location_of_dkist)

        # Find angle between zenith and solar north at the center boresight pointing
        solar_orientation_angle = self.get_solar_orientation_angle(
            boresight_coordinates, t0, sky_coordinates, frame_altaz
        )

        # get sun center azimuth and elevation and calculate the slit orientation angle using that value
        slit_orientation_angle = self.get_slit_orientation_angle(
            header, sky_coordinates, frame_altaz, solar_orientation_angle
        )

        # correct coordinates
        (
            observed_pix_x_rotated,
            observed_pix_y_rotated,
            cdelt_updated,
            pix_off_updated,
            crpix_updated,
            pcij_updated,
        ) = self.correct_helioprojective_coords(header, slit_orientation_angle.value)
        self.update_helioprojective_headers(
            header, pcij_updated, crpix_updated, cdelt_updated.value
        )

        x, y, wci_updated_eq, crval_eq = self.get_arm_specific_coords(
            header, t0, observed_pix_x_rotated, observed_pix_y_rotated
        )

        pcij_update_eq, cdelt_eq = self.correct_equatorial_coords(
            cdelt_updated, pix_off_updated, crval_eq, wci_updated_eq
        )
        self.update_equatorial_headers(
            header, pcij_update_eq, crpix_updated, cdelt_eq, slit_orientation_angle.value
        )

    def get_solar_orientation_angle(
        self,
        boresight_coordinates: tuple[float, float],
        t0: Time,
        sky_coordinates: SkyCoord,
        frame_altaz: AltAz,
    ) -> u.Quantity:
        """
        Get orientation of sun at time of observation.

        1. Given target coordinates, create a vector pointing 1 arcsec to solar north and transform that into the
        altaz frame.
        2. Create a second vector pointing 1 arcsec to zenith.
        3. Project and normalize the zenith vector and the target vector onto sky.
        4. Finally, calculate the angle between the two vectors to get the solar orientation.

        Returns
        -------
        float
            The solar orientation at the time of the observation.
        """
        # Vector pointing 1 arcsec to solar north
        sky_coord_north = SkyCoord(
            boresight_coordinates[0] * u.arcsec,
            (boresight_coordinates[1] + 1) * u.arcsec,
            obstime=t0,
            observer=location_of_dkist.get_itrs(t0),
            frame="helioprojective",
        )

        # transform to altaz frame and get the third coordinate of a point towards the zenith (i.e. alitude of boresight + a small angle)
        with Helioprojective.assume_spherical_screen(sky_coordinates.observer):
            sky_altaz = sky_coordinates.transform_to(frame_altaz)
            sky_coord_north_altaz = sky_coord_north.transform_to(frame_altaz)
            zenith_altaz = SkyCoord(
                sky_altaz.az,
                sky_altaz.alt + 1 * u.arcsec,
                sky_altaz.distance,
                frame=frame_altaz,
            )

            # Use cross products to obtain the sky projections of the two vectors (rotated by 90 deg)
            sky_normal = sky_altaz.data.to_cartesian()
            sky_coord_north_normal = sky_coord_north_altaz.data.to_cartesian()
            zenith_normal = zenith_altaz.data.to_cartesian()

            # Project zenith direction and direction to observed point into sky
            zenith_in_sky = zenith_normal.cross(sky_normal)
            sky_coord_north_in_sky = sky_coord_north_normal.cross(sky_normal)

            # Normalize directional vectors
            sky_normal /= sky_normal.norm()
            sky_coord_north_normal /= sky_coord_north_normal.norm()
            sky_coord_north_in_sky /= sky_coord_north_in_sky.norm()
            zenith_in_sky /= zenith_in_sky.norm()

            # Calculate the signed angle between the two projected vectors (angle between zenith and target)
            cos_theta = sky_coord_north_in_sky.dot(zenith_in_sky)
            sin_theta = sky_coord_north_in_sky.cross(zenith_in_sky).dot(sky_normal)

            solar_orientation_angle = np.rad2deg(np.arctan2(sin_theta, cos_theta))

            return solar_orientation_angle

    def get_slit_orientation_angle(
        self,
        header: fits.Header,
        sky_coordinates: SkyCoord,
        frame_altaz: AltAz,
        solar_orientation_angle: float,
    ) -> u.Quantity:
        """Get CryoNIRSP slit orientation measured relative to solar north at time of observation."""
        with Helioprojective.assume_spherical_screen(sky_coordinates.observer):
            sc_alt = sky_coordinates.transform_to(frame_altaz)
            coude_minus_azimuth_elevation = header["TTBLANGL"] * u.deg - (
                (sc_alt.az.deg - sc_alt.alt.deg) * u.deg
            )
            cryo_instrument_alignment_angle = self.parameters.cryo_instrument_alignment_angle
            slit_orientation_angle = (
                coude_minus_azimuth_elevation
                + cryo_instrument_alignment_angle
                + solar_orientation_angle
            )

            return slit_orientation_angle

    @abstractmethod
    def correct_helioprojective_coords(
        self, header: fits.header, slit_orientation_angle: float
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Correct helioprojective coordinates."""
        pass

    @abstractmethod
    def update_helioprojective_headers(
        self,
        header: fits.header,
        pcij_updated: np.ndarray,
        crpix_updated: np.ndarray,
        cdelt_updated: np.ndarray,
    ) -> None:
        """Update helioprojective headers."""
        pass

    @abstractmethod
    def get_arm_specific_coords(
        self,
        header: fits.Header,
        t0: Time,
        observed_pix_x_rotated: np.ndarray,
        observed_pix_y_rotated: np.ndarray,
    ) -> tuple[float, float, np.ndarray, np.ndarray]:
        """Get SP or CI specific coordinates to use in equatorial coordinate correction."""
        pass

    def correct_equatorial_coords(
        self,
        cdelt_updated: np.ndarray,
        pix_off_updated: np.ndarray,
        crval_eq: np.ndarray,
        wci_updated_eq: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Correct equatorial coordinates for SP or CI arm."""
        cdelt_eq = cdelt_updated.to(u.deg / u.pixel).value
        pcij_updated_eq = (
            (wci_updated_eq - crval_eq[:, None])
            @ np.linalg.pinv(pix_off_updated[:, :])
            / cdelt_eq[:, None]
        )

        return pcij_updated_eq, cdelt_eq

    @abstractmethod
    def update_equatorial_headers(
        self,
        header: fits.Header,
        pcij_updateEq: np.ndarray,
        crpix_updated: np.ndarray,
        cdelt_eq: np.ndarray,
        slit_orientation_angle: float,
    ) -> None:
        """Update equatorial headers."""
        pass

    def update_spectral_headers(self, header: fits.Header):
        """Update spectral headers after spectral correction."""
        pass

    def add_timing_headers(self, header: fits.Header) -> fits.Header:
        """
        Add timing headers to the FITS header.

        This method adds or updates headers related to frame timings.
        """
        # The source data is based on L0 data but L1 data takes L0 cadence * modstates * number of measurements to obtain.
        # This causes the cadence to be num_modstates * num_measurements times longer.
        # This causes the exposure time to be num_modstates times longer.
        header["CADENCE"] = (
            self.constants.average_cadence * self.constants.num_modstates * self.constants.num_meas
        )
        header["CADMIN"] = (
            self.constants.minimum_cadence * self.constants.num_modstates * self.constants.num_meas
        )
        header["CADMAX"] = (
            self.constants.maximum_cadence * self.constants.num_modstates * self.constants.num_meas
        )
        header["CADVAR"] = (
            self.constants.variance_cadence * self.constants.num_modstates * self.constants.num_meas
        )
        header["XPOSURE"] = header["XPOSURE"] * self.constants.num_modstates
        return header


class CIWriteL1Frame(CryonirspWriteL1Frame):
    """
    Task class for writing out calibrated L1 CryoNIRSP-CI frames.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs
    """

    @property
    def latitude_pixel_name(self) -> str:
        """CI has latitude along the xaxis of the detector."""
        return "detector x axis"

    @property
    def add_first_axis(self) -> Callable:
        """The first axis in the data is helioprojective longitude."""
        return self.add_helioprojective_longitude_axis

    @property
    def add_second_axis(self) -> Callable:
        """The first axis in the data is helioprojective latitude."""
        return self.add_helioprojective_latitude_axis

    @staticmethod
    def add_helioprojective_longitude_axis(header: fits.Header, axis_num: int) -> int:
        """Add header keys for the spatial helioprojective longitude axis."""
        header[f"DNAXIS{axis_num}"] = header[f"NAXIS{axis_num}"]
        header[f"DTYPE{axis_num}"] = "SPATIAL"
        header[f"DWNAME{axis_num}"] = "helioprojective longitude"
        header[f"CNAME{axis_num}"] = "helioprojective longitude"
        header[f"DUNIT{axis_num}"] = header[f"CUNIT{axis_num}"]
        header[f"DPNAME{axis_num}"] = "detector y axis"
        next_axis = axis_num + 1
        return next_axis

    def add_scan_step_axis(self, header: fits.Header, axis_num: int) -> int:
        """Add header keys for the scan step axis."""
        header[f"DNAXIS{axis_num}"] = self.constants.num_scan_steps
        header[f"DTYPE{axis_num}"] = "TEMPORAL"
        header[f"DPNAME{axis_num}"] = "scan step number"
        header[f"DWNAME{axis_num}"] = "time"
        if axis_num == 3:
            header[f"CNAME{axis_num}"] = "time"
        header[f"DUNIT{axis_num}"] = "s"
        # DINDEX and CNCURSCN are both one-based
        header[f"DINDEX{axis_num}"] = header["CNCURSCN"]
        next_axis = axis_num + 1
        return next_axis

    def flip_spectral_axis(self, header: fits.Header):
        """Adjust header values corresponding to axis flip."""
        pass

    def get_wavelength_range(self, header: fits.Header) -> WavelengthRange:
        """
        Return the wavelength range of this frame.

        Range is the wavelengths at the edges of the filter full width half maximum.
        """
        filter_central_wavelength = header["CNCENWAV"] * u.nm
        filter_fwhm = header["CNFWHM"] * u.nm
        return WavelengthRange(
            min=filter_central_wavelength - (filter_fwhm / 2),
            max=filter_central_wavelength + (filter_fwhm / 2),
        )

    def get_boresight_coords(self, header: fits.Header) -> tuple[float, float]:
        """Get boresight coordinates to use in CI spatial correction."""
        boresight_coordinates = header["CRVAL1"], header["CRVAL2"]

        return boresight_coordinates

    def correct_helioprojective_coords(
        self, header: fits.Header, slit_orientation_angle: float
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Correct CI helioprojective coordinates.

        1. Update CDELT to be static and squared over data.
        2. Update CRPIX to change according to the offset from the boresight coordinates.
        3. Update the WCI info:
            a. Perform a slit center scale correction.
            b. Get the angular values of the observed pixels in the frame of the instrument.
            c. Rotate the angular values into the solar frame by accounting for the telescope geometry.
        4. Update the PCij values.
        """
        # update cdelt to be static over the data and squared
        ##################################################################################
        spatial_scale_along_slit = self.parameters.ci_spatial_scale_along_slit
        cdelt_updated = np.stack((spatial_scale_along_slit, spatial_scale_along_slit))
        ##################################################################################

        # update crpix to change according to offset from boresight coordinates
        ##################################################################################
        mirror_scan_recalibration = (
            self.parameters.mirror_scan_recalibration_constant
        )  # recalibration to the scale of the field steering mirror scanning.
        # Instrument controller applies a 0.5 arcsec step, but in reality, it is 0.466 on sky
        header["CNM1BOFF"] = 8.0
        header["CNM1OFF"] = -2.75
        crpix1_new = (
            1108
            - (-(header["CNM1POS"] - header["CNM1OFF"]))
            * mirror_scan_recalibration
            / cdelt_updated.value[0]
        )
        crpix2_new = (
            1010
            - (-(header["CNM1BPOS"] - header["CNM1BOFF"]))
            * mirror_scan_recalibration
            / cdelt_updated.value[1]
        )
        crpix_updated = np.array([crpix1_new, crpix2_new])

        xpix = (
            np.hstack(
                (
                    np.linspace(0, header["NAXIS1"], header["NAXIS1"]),
                    np.linspace(header["NAXIS1"], 0, header["NAXIS1"]),
                )
            )
            + 1
        )  ## plus 1 due to 1-indexed standard
        ypix = (
            np.hstack(
                (
                    np.linspace(0, header["NAXIS2"], header["NAXIS1"]),
                    np.linspace(0, header["NAXIS2"], header["NAXIS1"]),
                )
            )
            + 1
        )  ## plus 1 due to 1-indexed standard
        pix = np.stack((xpix, ypix))

        pix_off_updated = pix - crpix_updated[:, None]
        #################################################################################

        # update WCI information
        #################################################################################
        slit_center_x = (
            (-(header["CNM1POS"] - header["CNM1OFF"]))
        ) * mirror_scan_recalibration  # SCALE CORRECTION
        slit_center_y = (
            -(header["CNM1BPOS"] - header["CNM1BOFF"])
        ) * mirror_scan_recalibration  # SCALE CORRECTION.

        # angular values of observed pixels in frame of instrument
        observed_pix_y = slit_center_y + (ypix - 1010) * cdelt_updated.value[1]
        observed_pix_x = slit_center_x + (xpix - 1108) * cdelt_updated.value[0]

        # angular values of observed pixels rotated into the solar frame by accounting for the telescope geometry
        theta = np.deg2rad(slit_orientation_angle)
        observed_pix_x_rotated = np.cos(theta) * observed_pix_x - np.sin(theta) * observed_pix_y
        observed_pix_y_rotated = np.sin(theta) * observed_pix_x + np.cos(theta) * observed_pix_y
        observed_pix_x_rotated += header["CRVAL1"]
        observed_pix_y_rotated += header["CRVAL2"]
        wci_updated = np.stack((observed_pix_x_rotated, observed_pix_y_rotated))
        ##################################################################################

        # correct pcij values
        ##################################################################################
        crval = np.array([header["CRVAL1"], header["CRVAL2"]])
        pcij_updated = (
            (wci_updated - crval[:, None])
            @ np.linalg.pinv(pix_off_updated[:, :])
            / cdelt_updated.value[:, None]
        )
        ##################################################################################

        return (
            observed_pix_x_rotated,
            observed_pix_y_rotated,
            cdelt_updated,
            pix_off_updated,
            crpix_updated,
            pcij_updated,
        )

    def update_helioprojective_headers(
        self,
        header: fits.Header,
        pcij_updated: np.ndarray,
        crpix_updated: np.ndarray,
        cdelt_updated: np.ndarray,
    ) -> None:
        """Update the helioprojective headers with corrected helioprojective coordinates for CI arm."""
        # UPDATE VALUES FOR HPLT-TAN / HPLN-TAN axes
        header["CNM1BOFF"] = 8.0
        header["CNM1OFF"] = -2.75
        header["PC1_1"] = pcij_updated[0, 0]
        header["PC1_2"] = pcij_updated[0, 1]
        header["PC1_3"] = 0
        header["PC2_1"] = pcij_updated[1, 0]
        header["PC2_2"] = pcij_updated[1, 1]
        header["PC2_3"] = 0
        header["PC3_1"] = 0
        header["PC3_2"] = 0
        header["PC3_3"] = 1
        header["CRPIX1"] = crpix_updated[0]
        header["CRPIX2"] = crpix_updated[1]
        header["CDELT1"] = cdelt_updated[0]
        header["CDELT2"] = cdelt_updated[1]

        return

    def get_arm_specific_coords(
        self,
        header: fits.Header,
        t0: Time,
        observed_pix_x_rotated: np.ndarray,
        observed_pix_y_rotated: np.ndarray,
    ) -> tuple[float, float, np.ndarray, np.ndarray]:
        """Get CI specific coordinates to use in equatorial coordinate correction."""
        x, y = header["CRVAL1"], header["CRVAL2"]

        sky_coord = SkyCoord(
            observed_pix_x_rotated * u.arcsec,
            observed_pix_y_rotated * u.arcsec,
            obstime=t0,
            observer=location_of_dkist.get_itrs(t0),
            frame="helioprojective",
        )

        with Helioprojective.assume_spherical_screen(sky_coord.observer):
            sky_coord_earth_equatorial = sky_coord.transform_to(GeocentricEarthEquatorial)
        wci_updated_eq = np.stack(
            (sky_coord_earth_equatorial.lon.value, sky_coord_earth_equatorial.lat.value)
        )

        sky_coord = SkyCoord(
            x * u.arcsec,
            y * u.arcsec,
            obstime=t0,
            observer=location_of_dkist.get_itrs(t0),
            frame="helioprojective",
        )
        with Helioprojective.assume_spherical_screen(sky_coord.observer):
            sky_coord_earth_equatorial = sky_coord.transform_to(GeocentricEarthEquatorial)
        crval_eq = np.stack(
            (sky_coord_earth_equatorial.lon.value, sky_coord_earth_equatorial.lat.value)
        )

        return x, y, wci_updated_eq, crval_eq

    def update_equatorial_headers(
        self,
        header: fits.Header,
        pcij_updated_eq: np.ndarray,
        crpix_updated: np.ndarray,
        cdelt_eq: np.ndarray,
        slit_orientation_angle: float,
    ) -> None:
        """Update the equatorial headers with corrected equatorial coordinates for CI arm."""
        header["PC1_1A"] = pcij_updated_eq[0, 0]
        header["PC1_2A"] = pcij_updated_eq[0, 1]
        header["PC1_3A"] = 0
        header["PC2_1A"] = pcij_updated_eq[1, 0]
        header["PC2_2A"] = pcij_updated_eq[1, 1]
        header["PC2_3A"] = 0
        header["PC3_1A"] = 0
        header["PC3_2A"] = 0
        header["PC3_3A"] = 1
        header["CRPIX1A"] = crpix_updated[0]
        header["CRPIX2A"] = crpix_updated[1]
        header["CDELT1A"] = cdelt_eq[0]
        header["CDELT2A"] = cdelt_eq[1]
        header["SLITORI"] = slit_orientation_angle

        return


class SPWriteL1Frame(CryonirspWriteL1Frame):
    """
    Task class for writing out calibrated L1 CryoNIRSP-SP frames.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs
    """

    @property
    def latitude_pixel_name(self) -> str:
        """SP has latitude along the spectrograph slit."""
        return "spatial along slit"

    @property
    def add_first_axis(self) -> Callable:
        """The first axis in the data is spectral."""
        return self.add_spectral_axis

    @property
    def add_second_axis(self) -> Callable:
        """The second axis in the data is helioprojective latitude."""
        return self.add_helioprojective_latitude_axis

    @staticmethod
    def add_spectral_axis(header: fits.Header, axis_num: int) -> int:
        """Add header keys for the spectral dispersion axis."""
        header[f"DNAXIS{axis_num}"] = header[f"NAXIS{axis_num}"]
        header[f"DTYPE{axis_num}"] = "SPECTRAL"
        header[f"DPNAME{axis_num}"] = "dispersion axis"
        header[f"DWNAME{axis_num}"] = "wavelength"
        header[f"CNAME{axis_num}"] = "wavelength"
        header[f"DUNIT{axis_num}"] = header[f"CUNIT{axis_num}"]
        next_axis = axis_num + 1
        return next_axis

    def flip_spectral_axis(self, header: fits.Header):
        """Adjust header values corresponding to axis flip."""
        # Fix the dispersion value to always be positive (Cryo gives it to us negative, which is wrong)
        header["CDELT1"] = np.abs(header["CDELT1"])
        # re-set the value of the reference pixel after the axis flip
        header["CRPIX1"] = header["NAXIS1"] - header["CRPIX1"]

    def add_scan_step_axis(self, header: fits.Header, axis_num: int) -> int:
        """Add header keys for the spatial scan step axis."""
        header[f"DNAXIS{axis_num}"] = self.constants.num_scan_steps
        header[f"DTYPE{axis_num}"] = "SPATIAL"
        header[f"DPNAME{axis_num}"] = "scan step number"
        header[f"DWNAME{axis_num}"] = "helioprojective longitude"
        if axis_num == 3:
            header[f"CNAME{axis_num}"] = "helioprojective longitude"
        # NB: CUNIT axis number is hard coded here
        header[f"DUNIT{axis_num}"] = header[f"CUNIT3"]
        # DINDEX and CNCURSCN are both one-based
        header[f"DINDEX{axis_num}"] = header["CNCURSCN"]
        next_axis = axis_num + 1
        return next_axis

    def get_wavelength_range(self, header: fits.Header) -> WavelengthRange:
        """
        Return the wavelength range of this frame.

        Range is the wavelength values of the pixels at the ends of the wavelength axis.
        """
        axis_types = [
            self.constants.axis_1_type,
            self.constants.axis_2_type,
            self.constants.axis_3_type,
        ]
        wavelength_axis = axis_types.index("AWAV") + 1  # FITS axis numbering is 1-based, not 0
        wavelength_unit = header[f"CUNIT{wavelength_axis}"]

        minimum = header[f"CRVAL{wavelength_axis}"] - (
            header[f"CRPIX{wavelength_axis}"] * header[f"CDELT{wavelength_axis}"]
        )
        maximum = header[f"CRVAL{wavelength_axis}"] + (
            (header[f"NAXIS{wavelength_axis}"] - header[f"CRPIX{wavelength_axis}"])
            * header[f"CDELT{wavelength_axis}"]
        )
        return WavelengthRange(
            min=u.Quantity(minimum, unit=wavelength_unit),
            max=u.Quantity(maximum, unit=wavelength_unit),
        )

    def get_boresight_coords(self, header: fits.Header) -> tuple[float, float]:
        """Get boresight coordinates to use in SP spatial correction."""
        boresight_coordinates = header["CRVAL3"], header["CRVAL2"]

        return boresight_coordinates

    def correct_helioprojective_coords(
        self, header: fits.Header, slit_orientation_angle: float
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Correct SP helioprojective coordinates.

        1. Update CDELT to be static and squared over data.
        2. Update CRPIX to change according to the offset from the boresight coordinates.
        3. Update the WCI info:
            a. Perform a slit center scale correction.
            b. Get the angular values of the observed pixels in the frame of the instrument.
            c. Rotate the angular values into the solar frame by accounting for the telescope geometry.
        4. Update the PCij values.
        """
        # update cdelt to be static over the data and squared
        ##################################################################################
        pix_along_slit = np.arange(header["NAXIS2"])
        pix = (
            np.stack((pix_along_slit, 0 * pix_along_slit)) + 1
        )  # FITS axis numbering is 1-based, not 0
        spatial_scale_along_slit = self.parameters.sp_spatial_scale_along_slit
        cdelt_updated = np.stack((spatial_scale_along_slit, spatial_scale_along_slit))
        ##################################################################################

        # update crpix to change according to offset from boresight coordinates
        ##################################################################################
        mirror_scan_recalibration = (
            self.parameters.mirror_scan_recalibration_constant
        )  # recalibration to the scale of the field steering mirror scanning.
        # Instrument controller applies a 0.5 arcsec step, but in reality, it is 0.466 on sky

        crpix3_new = (
            (-(header["CNM1POS"] - header["CNM1OFF"]))
            * mirror_scan_recalibration
            / cdelt_updated.value[1]
        )
        crpix_updated = np.array([header["NAXIS2"] // 2, crpix3_new])  # y x order
        pix_off_updated = pix - crpix_updated[:, None]
        #################################################################################

        # update WCI information
        #################################################################################
        slit_center_x = (
            -(header["CNM1POS"] - header["CNM1OFF"])
        ) * mirror_scan_recalibration  # SCALE CORRECTION
        slit_center_y = (
            (header["CNM1BPOS"] - header["CNM1BOFF"])
        ) * mirror_scan_recalibration  # SCALE CORRECTION.

        # angular values of observed pixels in frame of instrument
        observed_pix_y = (
            np.linspace(-header["NAXIS2"] / 2, header["NAXIS2"] / 2, header["NAXIS2"])
            * spatial_scale_along_slit.value
            + slit_center_y
        )
        observed_pix_x = np.zeros(header["NAXIS2"]) + slit_center_x

        # angular values of observed pixels rotated into the solar frame by accounting for the telescope geometry
        theta = np.deg2rad(slit_orientation_angle)
        observed_pix_x_rotated = np.cos(theta) * observed_pix_x - np.sin(theta) * observed_pix_y
        observed_pix_y_rotated = np.sin(theta) * observed_pix_x + np.cos(theta) * observed_pix_y
        observed_pix_x_rotated += header["CRVAL3"]
        observed_pix_y_rotated += header["CRVAL2"]
        wci_updated = np.stack((observed_pix_y_rotated, observed_pix_x_rotated))
        ##################################################################################

        # correct pcij values
        ##################################################################################
        # CRVAL remains fixed
        crval = np.array([header["CRVAL2"], header["CRVAL3"]])
        pcij_updated = (
            (wci_updated - crval[:, None])
            @ np.linalg.pinv(pix_off_updated[:, :])
            / cdelt_updated.value[:, None]
        )
        ##################################################################################

        return (
            observed_pix_x_rotated,
            observed_pix_y_rotated,
            cdelt_updated,
            pix_off_updated,
            crpix_updated,
            pcij_updated,
        )

    def update_helioprojective_headers(
        self,
        header: fits.Header,
        pcij_updated: np.ndarray,
        crpix_updated: np.ndarray,
        cdelt_updated: np.ndarray,
    ) -> None:
        """Update the helioprojective headers with corrected helioprojective coordinates for the SP arm."""
        # UPDATE VALUES FOR HPLT-TAN / HPLN-TAN axes
        header["PC1_1"] = 1.0
        header["PC1_2"] = 0.0
        header["PC1_3"] = 0.0
        header["PC3_1"] = 0.0
        header["PC2_1"] = 0.0
        header["PC2_2"] = pcij_updated[0, 0]
        header["PC2_3"] = pcij_updated[0, 1]
        header["PC3_2"] = pcij_updated[1, 0]
        header["PC3_3"] = pcij_updated[1, 1]
        header["CRPIX3"] = crpix_updated[1]
        header["CRPIX2"] = crpix_updated[0]
        header["CDELT3"] = cdelt_updated[1]
        header["CDELT2"] = cdelt_updated[0]

        return

    def get_arm_specific_coords(
        self,
        header: fits.Header,
        t0: Time,
        observed_pix_x_rotated: np.ndarray,
        observed_pix_y_rotated: np.ndarray,
    ) -> tuple[float, float, np.ndarray, np.ndarray]:
        """Get SP specific coordinates to use in equatorial coordinate correction."""
        x, y = header["CRVAL3"], header["CRVAL2"]

        sky_coord = SkyCoord(
            observed_pix_x_rotated * u.arcsec,
            observed_pix_y_rotated * u.arcsec,
            obstime=t0,
            observer=location_of_dkist.get_itrs(t0),
            frame="helioprojective",
        )
        with Helioprojective.assume_spherical_screen(sky_coord.observer):
            sky_coord_earth_equatorial = sky_coord.transform_to(GeocentricEarthEquatorial)
        wci_updated_eq = np.stack(
            (sky_coord_earth_equatorial.lat.value, sky_coord_earth_equatorial.lon.value)
        )

        sky_coord = SkyCoord(
            x * u.arcsec,
            y * u.arcsec,
            obstime=t0,
            observer=location_of_dkist.get_itrs(t0),
            frame="helioprojective",
        )
        with Helioprojective.assume_spherical_screen(sky_coord.observer):
            sky_coord_earth_equatorial = sky_coord.transform_to(GeocentricEarthEquatorial)
        crval_eq = np.stack(
            (sky_coord_earth_equatorial.lat.value, sky_coord_earth_equatorial.lon.value)
        )

        return x, y, wci_updated_eq, crval_eq

    def update_equatorial_headers(
        self,
        header: fits.Header,
        pcij_updated_eq: np.ndarray,
        crpix_updated: np.ndarray,
        cdelt_eq: np.ndarray,
        slit_orientation_angle: float,
    ) -> None:
        """Update the equatorial headers with corrected equatorial coordinates for SP arm."""
        header["PC1_1A"] = 1.0
        header["PC1_2A"] = 0.0
        header["PC1_3A"] = 0.0
        header["PC3_1A"] = 0.0
        header["PC2_1A"] = 0.0
        header["PC3_3A"] = pcij_updated_eq[1, 1]
        header["PC2_2A"] = pcij_updated_eq[0, 0]
        header["PC2_3A"] = pcij_updated_eq[0, 1]
        header["PC3_2A"] = pcij_updated_eq[1, 0]
        header["CRPIX3A"] = crpix_updated[1]
        header["CRPIX2A"] = crpix_updated[0]
        header["CDELT3A"] = cdelt_eq[1]
        header["CDELT2A"] = cdelt_eq[0]
        header["SLITORI"] = slit_orientation_angle

        return

    @cached_property
    def spectral_fit_results(self) -> dict:
        """Get the spectral fit results from disk."""
        return next(
            self.read(
                tags=[CryonirspTag.intermediate(), CryonirspTag.task_spectral_fit()],
                decoder=json_decoder,
            )
        )

    def update_spectral_headers(self, header: fits.Header):
        """Update spectral headers after spectral correction."""
        header.update(self.spectral_fit_results)
