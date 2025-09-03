"""Cryo SP wavelength calibration task. See :doc:`this page </wavelength_calibration>` for more information."""

import math

import astropy.units as u
import numpy as np
from astropy.time import Time
from astropy.wcs import WCS
from dkist_processing_common.codecs.json import json_encoder
from dkist_processing_common.models.dkist_location import location_of_dkist
from dkist_service_configuration.logging import logger
from solar_wavelength_calibration import Atlas
from solar_wavelength_calibration import WavelengthCalibrationFitter
from solar_wavelength_calibration.fitter.parameters import AngleBoundRange
from solar_wavelength_calibration.fitter.parameters import BoundsModel
from solar_wavelength_calibration.fitter.parameters import DispersionBoundRange
from solar_wavelength_calibration.fitter.parameters import LengthBoundRange
from solar_wavelength_calibration.fitter.parameters import UnitlessBoundRange
from solar_wavelength_calibration.fitter.parameters import WavelengthCalibrationParameters
from solar_wavelength_calibration.fitter.wavelength_fitter import WavelengthParameters
from solar_wavelength_calibration.fitter.wavelength_fitter import calculate_initial_crval_guess
from sunpy.coordinates import HeliocentricInertial

from dkist_processing_cryonirsp.codecs.fits import cryo_fits_array_decoder
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.tasks.cryonirsp_base import CryonirspTaskBase

__all__ = ["SPWavelengthCalibration"]


class SPWavelengthCalibration(CryonirspTaskBase):
    """Task class for correcting the dispersion axis wavelength values.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs

    """

    record_provenance = True

    def run(self) -> None:
        """
        Run method for the task.

        - Gather 1D characteristic spectrum. This will be the initial spectrum.
        - Get a header from a solar gain frame for initial wavelength estimation.
        - Compute the theoretical dispersion, order, and incident light angle.
        - Compute the input wavelength vector from the spectrum and header.
        - Get the Doppler velocity and resolving power.
        - Define fitting bounds and initialize model parameters.
        - Set and normalize spectral weights, zeroing edges.
        - Fit the profile using WavelengthCalibrationFitter.
        - Write fit results to disk.

        Returns
        -------
        None
        """
        with self.apm_processing_step("Load input spectrum and wavelength"):
            logger.info("Loading input spectrum")
            input_spectrum = next(
                self.read(
                    tags=[
                        CryonirspTag.intermediate_frame(beam=1),
                        CryonirspTag.task_characteristic_spectra(),
                    ],
                    decoder=cryo_fits_array_decoder,
                )
            )

            logger.info(
                "Computing instrument specific dispersion, order, and incident light angle."
            )
            (
                dispersion,
                order,
                incident_light_angle,
            ) = self.get_theoretical_dispersion_order_light_angle()

            logger.info("Computing initial wavelength vector.")
            input_wavelength_vector = self.compute_input_wavelength_vector(
                spectrum=input_spectrum,
                dispersion=dispersion,
                order=order,
                incident_light_angle=incident_light_angle,
            )

        # Get the doppler velocity
        doppler_velocity = self.get_doppler_velocity()
        logger.info(f"{doppler_velocity = !s}")

        # Get the resolving power
        resolving_power = self.get_resolving_power()
        logger.info(f"{resolving_power = }")

        with self.apm_processing_step("Compute brute-force CRVAL initial guess"):
            atlas = Atlas(config=self.parameters.wavecal_atlas_download_config)
            crval = calculate_initial_crval_guess(
                input_wavelength_vector=input_wavelength_vector,
                input_spectrum=input_spectrum,
                atlas=atlas,
                negative_limit=-2 * u.nm,
                positive_limit=2 * u.nm,
                num_steps=550,
            )
            logger.info(f"{crval = !s}")

        with self.apm_task_step("Set up wavelength fit"):
            logger.info("Setting bounds")
            bounds = BoundsModel(
                crval=LengthBoundRange(min=crval - (5 * u.nm), max=crval + (5 * u.nm)),
                dispersion=DispersionBoundRange(
                    min=dispersion - (0.05 * u.nm / u.pix), max=dispersion + (0.05 * u.nm / u.pix)
                ),
                incident_light_angle=AngleBoundRange(
                    min=incident_light_angle - (180 * u.deg),
                    max=incident_light_angle + (180 * u.deg),
                ),
                resolving_power=UnitlessBoundRange(
                    min=resolving_power - (resolving_power * 0.1),
                    max=resolving_power + (resolving_power * 0.1),
                ),
                opacity_factor=UnitlessBoundRange(min=0.0, max=10.0),
                straylight_fraction=UnitlessBoundRange(min=0.0, max=0.4),
            )

            logger.info("Initializing parameters")
            input_parameters = WavelengthCalibrationParameters(
                crval=crval,
                dispersion=dispersion,
                incident_light_angle=incident_light_angle,
                resolving_power=resolving_power,
                opacity_factor=5.0,
                straylight_fraction=0.2,
                grating_constant=self.constants.grating_constant,
                doppler_velocity=doppler_velocity,
                order=order,
                bounds=bounds,
            )

            # Define spectral weights to apply
            weights = np.ones_like(input_spectrum)
            # Set edge weights to zero to mitigate flat field artifacts (inner and outer 10% of array)
            num_pixels = len(weights)
            weights[: num_pixels // self.parameters.wavecal_fraction_of_unweighted_edge_pixels] = 0
            weights[-num_pixels // self.parameters.wavecal_fraction_of_unweighted_edge_pixels :] = 0

            fitter = WavelengthCalibrationFitter(
                input_parameters=input_parameters,
                atlas=atlas,
            )

            logger.info(f"Input parameters: {input_parameters.lmfit_parameters.pretty_repr()}")

        with self.apm_processing_step("Run wavelength solution fit"):
            fit_result = fitter(
                input_wavelength_vector=input_wavelength_vector,
                input_spectrum=input_spectrum,
                spectral_weights=weights,
            )

        with self.apm_writing_step("Save wavelength solution and quality metrics"):
            self.write(
                data=fit_result.wavelength_parameters.to_header(
                    axis_num=1, add_alternate_keys=True
                ),
                tags=[CryonirspTag.task_spectral_fit(), CryonirspTag.intermediate()],
                encoder=json_encoder,
            )
            self.quality_store_wavecal_results(
                input_wavelength=input_wavelength_vector,
                input_spectrum=input_spectrum,
                fit_result=fit_result,
                weights=weights,
            )

    def get_theoretical_dispersion_order_light_angle(self) -> tuple[u.Quantity, int, u.Quantity]:
        # TODO: Make this docstring correct (we use grating constant, not grating spacing) and show calculation of all values.
        r"""
        Compute theoretical dispersion, spectral order, and incident light angle.

        The incident light angle, :math:`\alpha`, is computed as

        .. math::
            \alpha = \phi + \theta_L

        where :math:`\phi`, the grating position, and :math:`\theta_L`, the Littrow angle, come from L0 headers.

        From the grating equation, the spectral order, :math:`m`, is

        .. math::
            m = \frac{\sin\alpha + \sin\beta}{\sigma\lambda}

        where :math:`\sigma` is the grating constant (lines per mm), :math:`\beta` is the diffracted light angle,
        and :math:`\lambda` is the wavelength. The wavelength comes from L0 headers and :math:`\beta = \phi - \theta_L`.

        Finally, the linear dispersion (nm / px) is

        .. math::
            \frac{d\lambda}{dl} = \frac{\mu \cos\beta}{m \sigma f}

        where :math:`\mu` is the detector pixel pitch and :math:`f` is the camera focal length, both of which come from
        L0 headers.
        """
        wavelength = self.constants.wavelength * u.nanometer
        grating_position_angle_phi = self.constants.grating_position_deg * u.deg
        grating_littrow_angle_theta = self.constants.grating_littrow_angle_deg * u.deg
        incident_light_angle = grating_position_angle_phi + grating_littrow_angle_theta
        beta = grating_position_angle_phi - grating_littrow_angle_theta
        order = int(
            (np.sin(incident_light_angle) + np.sin(beta))
            / (wavelength * self.constants.grating_constant)
        )
        camera_mirror_focal_length = self.parameters.camera_mirror_focal_length_mm
        pixpitch = self.parameters.pixel_pitch_micron
        linear_disp = (
            order * (self.constants.grating_constant / np.cos(beta)) * camera_mirror_focal_length
        )
        theoretical_dispersion = (pixpitch / linear_disp).to(u.nanometer) / u.pix

        logger.info(f"{theoretical_dispersion = !s}")
        logger.info(f"{order = }")
        logger.info(f"{incident_light_angle = !s}")

        return theoretical_dispersion, order, incident_light_angle

    def compute_input_wavelength_vector(
        self,
        *,
        spectrum: np.ndarray,
        dispersion: u.Quantity,
        order: int,
        incident_light_angle: u.Quantity,
    ) -> u.Quantity:
        """Compute the expected wavelength vector based on the header information."""
        num_wave_pix = spectrum.size
        wavelength_parameters = WavelengthParameters(
            crpix=num_wave_pix // 2 + 1,
            crval=self.constants.wavelength,
            dispersion=dispersion.to_value(u.nm / u.pix),
            grating_constant=self.constants.grating_constant.to_value(1 / u.mm),
            order=order,
            incident_light_angle=incident_light_angle.to_value(u.deg),
            cunit="nm",
        )
        header = wavelength_parameters.to_header(axis_num=1)
        wcs = WCS(header)
        input_wavelength_vector = wcs.spectral.pixel_to_world(np.arange(num_wave_pix)).to(u.nm)

        return input_wavelength_vector

    def get_doppler_velocity(self) -> u.Quantity:
        """Find the speed at which DKIST is moving relative to the Sun's center.

        Positive values refer to when DKIST is moving away from the sun.
        """
        coord = location_of_dkist.get_gcrs(obstime=Time(self.constants.solar_gain_ip_start_time))
        heliocentric_coord = coord.transform_to(
            HeliocentricInertial(obstime=Time(self.constants.solar_gain_ip_start_time))
        )
        obs_vr_kms = heliocentric_coord.d_distance
        return obs_vr_kms

    def get_resolving_power(self) -> int:
        """Find the resolving power for the slit and filter center wavelength used during observation."""
        # Map of (center wavelength) → (slit width) → resolving power
        resolving_power_map = {1080.0: {175: 39580, 52: 120671}, 1430.0: {175: 42943, 52: 133762}}

        center_wavelength = self.constants.center_wavelength
        slit_width = self.constants.slit_width

        # Find the closest matching key within tolerance
        matched_wavelength = next(
            (
                key
                for key in resolving_power_map
                if math.isclose(center_wavelength, key, abs_tol=10)
            ),
            None,
        )

        if matched_wavelength is None:
            raise ValueError(
                f"{center_wavelength} not a valid filter center wavelength. "
                f"Should be within 10 nm of one of {', '.join(str(k) for k in resolving_power_map)} nm."
            )

        slit_dict = resolving_power_map[matched_wavelength]
        if slit_width not in slit_dict:
            raise ValueError(
                f"{slit_width} not a valid slit width. "
                f"Should be one of {', '.join(str(k) for k in slit_dict)} µm."
            )

        return slit_dict[slit_width]
