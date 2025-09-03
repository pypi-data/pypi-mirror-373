"""Cryonirsp make movie frames task."""

from abc import ABC
from abc import abstractmethod

import numpy as np
from astropy.io import fits
from astropy.visualization import ZScaleInterval
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_service_configuration.logging import logger

from dkist_processing_cryonirsp.codecs.fits import cryo_fits_access_decoder
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.parsers.cryonirsp_l1_fits_access import CryonirspL1FitsAccess
from dkist_processing_cryonirsp.tasks.cryonirsp_base import CryonirspTaskBase

__all__ = ["MakeCryonirspMovieFrames", "SPMakeCryonirspMovieFrames"]


class MakeCryonirspMovieFramesBase(CryonirspTaskBase, ABC):
    """Create CryoNIRSP movie frames common functionality for the Context Imager (CI) and Spectropolarimeter (SP)."""

    def run(self):
        """Create movie frames using all stokes states if they exist, otherwise only use intensity."""
        if self.constants.correct_for_polarization:
            with self.apm_task_step("Make full stokes movie"):
                self.make_full_stokes_movie_frames()
        else:
            with self.apm_task_step("Make intensity only movie"):
                self.make_intensity_movie_frames()

    @abstractmethod
    def make_full_stokes_movie_frames(self):
        """Make a movie that combines each of the stokes frames into a single movie frame."""

    @abstractmethod
    def make_intensity_movie_frames(self):
        """Make a movie out of stokes I frames."""

    @staticmethod
    def scale_for_rendering(data: np.ndarray):
        """Scale the calibrated frame data using a normalization function to facilitate display as a movie frame."""
        zscale = ZScaleInterval()
        return zscale(data)

    @staticmethod
    def grid_movie_frame(
        top_left: np.ndarray,
        top_right: np.ndarray,
        bottom_left: np.ndarray,
        bottom_right: np.ndarray,
    ) -> np.ndarray:
        """Combine multiple arrays into a 2x2 grid."""
        result = np.concatenate(
            (
                np.concatenate((top_left, top_right), axis=1),
                np.concatenate((bottom_left, bottom_right), axis=1),
            ),
            axis=0,
        )
        return result

    def get_movie_header(
        self, map_scan: int, scan_step: int, meas_num: int, stokes_state: str
    ) -> fits.Header:
        """Create a header to use on a movie frame based on a calibrated frame."""
        calibrated_frame = next(
            self.read(
                tags=[
                    CryonirspTag.frame(),
                    CryonirspTag.calibrated(),
                    CryonirspTag.stokes(stokes_state),
                    CryonirspTag.meas_num(meas_num),
                    CryonirspTag.map_scan(map_scan),
                    CryonirspTag.scan_step(scan_step),
                ],
                decoder=cryo_fits_access_decoder,
                fits_access_class=CryonirspL1FitsAccess,
            )
        )
        header = calibrated_frame.header
        return header


# See note below on `SPMakeCryonirspMovieFrames`
class MakeCryonirspMovieFrames(MakeCryonirspMovieFramesBase):
    """Make CryoNIRSP movie frames for the Context Imager and tag with CryonirspTag.movie_frame()."""

    def make_full_stokes_movie_frames(self):
        """Make a movie that combines each of the stokes frames into a single movie frame."""
        self.make_intensity_movie_frames()

    def make_intensity_movie_frames(self):
        """Make a movie out of stokes I frames."""
        for map_scan in range(1, self.constants.num_map_scans + 1):
            for scan_step in range(1, self.constants.num_scan_steps + 1):
                logger.info(f"Generate Stokes-I movie frame for {map_scan=} and {scan_step=}")
                movie_frame_hdu = self.make_intensity_frame(map_scan=map_scan, scan_step=scan_step)
                logger.info(f"Writing Stokes-I movie frame for {map_scan=} and {scan_step=}")
                self.write(
                    data=fits.HDUList([movie_frame_hdu]),
                    tags=[
                        CryonirspTag.map_scan(map_scan),
                        CryonirspTag.scan_step(scan_step),
                        CryonirspTag.movie_frame(),
                    ],
                    encoder=fits_hdulist_encoder,
                )

    def make_full_stokes_frame(self, map_scan: int, scan_step: int) -> fits.PrimaryHDU:
        """Create a movie frame (data + header) with the stokes frames (IQUV) combined into top left, top right, bottom left, bottom right quadrants respectively."""
        meas_num = 1  # Use only the first measurement if there are multiple measurements.
        stokes_i = self.get_movie_frame(
            map_scan=map_scan, scan_step=scan_step, meas_num=meas_num, stokes_state="I"
        )
        stokes_q = self.get_movie_frame(
            map_scan=map_scan, scan_step=scan_step, meas_num=meas_num, stokes_state="Q"
        )
        stokes_u = self.get_movie_frame(
            map_scan=map_scan, scan_step=scan_step, meas_num=meas_num, stokes_state="U"
        )
        stokes_v = self.get_movie_frame(
            map_scan=map_scan, scan_step=scan_step, meas_num=meas_num, stokes_state="V"
        )
        movie_frame = self.grid_movie_frame(
            top_left=stokes_i,
            top_right=stokes_q,
            bottom_left=stokes_u,
            bottom_right=stokes_v,
        )
        movie_header = self.get_movie_header(
            map_scan=map_scan, scan_step=scan_step, meas_num=meas_num, stokes_state="I"
        )
        return fits.PrimaryHDU(header=movie_header, data=movie_frame)

    def make_intensity_frame(self, map_scan: int, scan_step: int) -> fits.PrimaryHDU:
        """Create a movie frame (data + header) with just the stokes I frames."""
        meas_num = 1  # Use only the first measurement if there are multiple measurements.
        stokes_i = self.get_movie_frame(
            map_scan=map_scan, scan_step=scan_step, meas_num=meas_num, stokes_state="I"
        )
        movie_header = self.get_movie_header(
            map_scan=map_scan, scan_step=scan_step, meas_num=meas_num, stokes_state="I"
        )
        return fits.PrimaryHDU(header=movie_header, data=stokes_i)

    def get_movie_frame(
        self, map_scan: int, scan_step: int, meas_num: int, stokes_state: str
    ) -> np.ndarray:
        """Retrieve the calibrated frame data for the first frame which matches the input parameters and transform it into a movie frame (i.e. normalize the values)."""
        calibrated_frame = next(
            self.read(
                tags=[
                    CryonirspTag.frame(),
                    CryonirspTag.calibrated(),
                    CryonirspTag.stokes(stokes_state),
                    CryonirspTag.meas_num(meas_num),
                    CryonirspTag.map_scan(map_scan),
                    CryonirspTag.scan_step(scan_step),
                ],
                decoder=cryo_fits_access_decoder,
                fits_access_class=CryonirspL1FitsAccess,
            )
        )
        movie_frame = self.scale_for_rendering(calibrated_frame.data)
        return movie_frame


# NOTE:
# This task isn't used right now because the SP movies need some better handling of the wavelength dimension.
# For the time being both arms use the `MakeCryonirspMovieFrames` task above.
# See PR #91 for more information.
class SPMakeCryonirspMovieFrames(MakeCryonirspMovieFramesBase):
    """Make CryoNIRSP movie frames for the Spectropolarimeter and tag with CryonirspTag.movie_frame()."""

    def make_full_stokes_movie_frames(self):
        """Make a movie that combines each of the stokes frames into a single movie frame."""
        for map_scan in range(1, self.constants.num_map_scans + 1):
            logger.info(f"Generate full stokes movie frame for {map_scan=}")
            movie_frame_hdu = self.make_full_stokes_frame(map_scan=map_scan)

            logger.info(f"Writing full stokes movie frame for {map_scan=}")
            self.write(
                data=fits.HDUList([movie_frame_hdu]),
                tags=[
                    CryonirspTag.map_scan(map_scan),
                    CryonirspTag.movie_frame(),
                ],
                encoder=fits_hdulist_encoder,
            )

    def make_intensity_movie_frames(self):
        """Make a movie out of stokes I frames."""
        for map_scan in range(1, self.constants.num_map_scans + 1):
            logger.info(f"Generate intensity movie frame for {map_scan=}")
            movie_frame_hdu = self.make_intensity_frame(map_scan=map_scan)

            logger.info(f"Writing intensity movie frame for {map_scan=}")
            self.write(
                data=fits.HDUList([movie_frame_hdu]),
                tags=[
                    CryonirspTag.map_scan(map_scan),
                    CryonirspTag.movie_frame(),
                ],
                encoder=fits_hdulist_encoder,
            )

    def make_full_stokes_frame(self, map_scan: int) -> fits.PrimaryHDU:
        """Create a movie frame (data + header) with the stokes frames (IQUV) combined into top left, top right, bottom left, bottom right quadrants respectively."""
        meas_num = 1  # Use only the first measurement if there are multiple measurements.
        stokes_i = self.get_movie_frame(map_scan=map_scan, meas_num=meas_num, stokes_state="I")
        stokes_q = self.get_movie_frame(map_scan=map_scan, meas_num=meas_num, stokes_state="Q")
        stokes_u = self.get_movie_frame(map_scan=map_scan, meas_num=meas_num, stokes_state="U")
        stokes_v = self.get_movie_frame(map_scan=map_scan, meas_num=meas_num, stokes_state="V")
        movie_frame = self.grid_movie_frame(
            top_left=stokes_i,
            top_right=stokes_q,
            bottom_left=stokes_u,
            bottom_right=stokes_v,
        )
        # Here we make the full map have the same header as the first scan step.
        movie_header = self.get_movie_header(
            map_scan=map_scan, scan_step=1, meas_num=meas_num, stokes_state="I"
        )
        return fits.PrimaryHDU(header=movie_header, data=movie_frame)

    def make_intensity_frame(self, map_scan: int) -> fits.PrimaryHDU:
        """Create a movie frame (data + header) with just the stokes I frames."""
        meas_num = 1  # Use only the first measurement if there are multiple measurements.
        stokes_i = self.get_movie_frame(map_scan=map_scan, meas_num=meas_num, stokes_state="I")
        movie_header = self.get_movie_header(
            map_scan=map_scan, scan_step=1, meas_num=meas_num, stokes_state="I"
        )
        return fits.PrimaryHDU(header=movie_header, data=stokes_i)

    def get_movie_frame(self, map_scan: int, meas_num: int, stokes_state: str) -> np.ndarray:
        """Retrieve the calibrated frame data for the first frame which matches the input parameters and transform it into a movie frame (i.e. normalize the values)."""
        if self.constants.num_scan_steps == 1:
            calibrated_frame = self.get_spectral_calibrated_frame(
                map_scan=map_scan, meas_num=meas_num, stokes_state=stokes_state
            )
        else:
            calibrated_frame = self.get_integrated_calibrated_frame(
                map_scan=map_scan, meas_num=meas_num, stokes_state=stokes_state
            )
        movie_frame = self.scale_for_rendering(calibrated_frame.data)
        return movie_frame

    def get_spectral_calibrated_frame(
        self, map_scan: int, meas_num: int, stokes_state: str
    ) -> np.ndarray:
        """Retrieve a calibrated frame for a single scan step (no integration)."""
        scan_step = 1  # There is only a single scan step in a spectral movie
        calibrated_frame = next(
            self.read(
                tags=[
                    CryonirspTag.frame(),
                    CryonirspTag.calibrated(),
                    CryonirspTag.stokes(stokes_state),
                    CryonirspTag.meas_num(meas_num),
                    CryonirspTag.map_scan(map_scan),
                    CryonirspTag.scan_step(scan_step),
                ],
                decoder=cryo_fits_access_decoder,
                fits_access_class=CryonirspL1FitsAccess,
            )
        )
        return calibrated_frame.data

    def get_integrated_calibrated_frame(
        self, map_scan: int, meas_num: int, stokes_state: str
    ) -> np.ndarray:
        """Retrieve a frame that has been integrated across scan steps."""
        data = self.get_spectral_calibrated_frame(
            map_scan=map_scan, meas_num=meas_num, stokes_state=stokes_state
        )
        integrated_data = self.integrate_spectral_frame(data)
        integrated_arrays = [integrated_data]
        for scan_step in range(2, self.constants.num_scan_steps + 1):
            calibrated_frame = next(
                self.read(
                    tags=[
                        CryonirspTag.frame(),
                        CryonirspTag.calibrated(),
                        CryonirspTag.stokes(stokes_state),
                        CryonirspTag.meas_num(meas_num),
                        CryonirspTag.map_scan(map_scan),
                        CryonirspTag.scan_step(scan_step),
                    ],
                    decoder=cryo_fits_access_decoder,
                    fits_access_class=CryonirspL1FitsAccess,
                )
            )
            integrated_data = self.integrate_spectral_frame(calibrated_frame.data)
            integrated_arrays.append(integrated_data)
        full_frame = np.vstack(integrated_arrays)
        return full_frame

    @staticmethod
    def integrate_spectral_frame(data: np.ndarray) -> np.ndarray:
        """Integrate spectral frame."""
        wavelength_integrated_data = np.sum(np.abs(data), axis=1)
        return wavelength_integrated_data
