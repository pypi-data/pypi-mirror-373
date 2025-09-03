"""CryoNIRSP FITS access for L0 data."""

import numpy as np
from astropy.io import fits
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess

from dkist_processing_cryonirsp.models.exposure_conditions import CRYO_EXP_TIME_ROUND_DIGITS
from dkist_processing_cryonirsp.models.exposure_conditions import ExposureConditions


class CryonirspRampFitsAccess(L0FitsAccess):
    """
    Class to provide easy access to L0 headers for non-linearized (raw) files.

    i.e. instead of <CryonirspL0FitsAccess>.header['key'] this class lets us use <CryonirspL0FitsAccess>.key instead

    Parameters
    ----------
    hdu :
        Fits L0 header object

    name : str
        The name of the file that was loaded into this FitsAccess object

    auto_squeeze : bool
        When set to True, dimensions of length 1 will be removed from the array
    """

    def __init__(
        self,
        hdu: fits.ImageHDU | fits.PrimaryHDU | fits.CompImageHDU,
        name: str | None = None,
        auto_squeeze: bool = True,
    ):
        super().__init__(hdu=hdu, name=name, auto_squeeze=auto_squeeze)

        self.camera_readout_mode = self.header["CNCAMMD"]
        self.curr_frame_in_ramp: int = self.header["CNCNDR"]
        self.num_frames_in_ramp: int = self.header["CNNNDR"]
        self.arm_id: str = self.header["CNARMID"]
        self.filter_name = self.header["CNFILTNP"].upper()
        self.roi_1_origin_x = self.header["HWROI1OX"]
        self.roi_1_origin_y = self.header["HWROI1OY"]
        self.roi_1_size_x = self.header["HWROI1SX"]
        self.roi_1_size_y = self.header["HWROI1SY"]
        self.obs_ip_start_time = self.header["DKIST011"]


class CryonirspL0FitsAccess(L0FitsAccess):
    """
    Class to provide easy access to L0 headers for linearized (ready for processing) files.

    i.e. instead of <CryonirspL0FitsAccess>.header['key'] this class lets us use <CryonirspL0FitsAccess>.key instead

    Parameters
    ----------
    hdu :
        Fits L0 header object

    name : str
        The name of the file that was loaded into this FitsAccess object

    auto_squeeze : bool
        When set to True, dimensions of length 1 will be removed from the array
    """

    def __init__(
        self,
        hdu: fits.ImageHDU | fits.PrimaryHDU | fits.CompImageHDU,
        name: str | None = None,
        auto_squeeze: bool = True,
    ):
        super().__init__(hdu=hdu, name=name, auto_squeeze=auto_squeeze)

        self.arm_id: str = self.header["CNARMID"]
        self.number_of_modulator_states: int = self.header["CNMODNST"]
        self.modulator_state: int = self.header["CNMODCST"]
        self.scan_step: int = self.header["CNCURSCN"]
        self.num_scan_steps: int = self.header["CNNUMSCN"]
        self.num_cn1_scan_steps: int = self.header["CNP1DNSP"]
        self.num_cn2_scan_steps: int = self.header["CNP2DNSP"]
        self.cn2_step_size: float = self.header["CNP2DSS"]
        self.meas_num: int = self.header["CNCMEAS"]
        self.num_meas: int = self.header["CNNMEAS"]
        self.sub_repeat_num = self.header["CNCSREP"]
        self.num_sub_repeats: int = self.header["CNSUBREP"]
        self.modulator_spin_mode: str = self.header["CNSPINMD"]
        self.axis_1_type: str = self.header["CTYPE1"]
        self.axis_2_type: str = self.header["CTYPE2"]
        self.axis_3_type: str = self.header["CTYPE3"]
        self.wave_min: float = round(
            self.header["CRVAL1"] - (self.header["CRPIX1"] * self.header["CDELT1"]), 1
        )
        self.wave_max: float = round(
            self.header["CRVAL1"]
            + ((self.header["NAXIS1"] - self.header["CRPIX1"]) * self.header["CDELT1"]),
            1,
        )
        self.grating_position_deg: float = self.header["CNGRTPOS"]
        self.grating_littrow_angle_deg: float = self.header["CNGRTLAT"]
        self.grating_constant: float = self.header["CNGRTCON"]
        self.obs_ip_start_time = self.header["DKIST011"]
        # The ExposureConditions are a combination of the exposure time and the OD filter name:
        self.exposure_conditions = ExposureConditions(
            round(self.fpa_exposure_time_ms, CRYO_EXP_TIME_ROUND_DIGITS),
            self.header["CNFILTNP"].upper(),
        )
        self.solar_gain_ip_start_time = self.header["DATE-OBS"]
        self.center_wavelength = self.header["CNCENWAV"]
        self.slit_width = self.header["CNSLITW"]

    @property
    def cn1_scan_step(self):
        """Convert the inner loop step number from float to int."""
        return int(self.header["CNP1DCUR"])


class CryonirspLinearizedFitsAccess(CryonirspL0FitsAccess):
    """
    Class to access to linearized CryoNIRSP data.

    Flip the dispersion axis of the SP arm.
    Cryo's wavelength decreases from left to right, so we flip it here to match the other instruments.

    Parameters
    ----------
    hdu :
        Fits L0 header object

    name : str
        The name of the file that was loaded into this FitsAccess object

    auto_squeeze : bool
        When set to True, dimensions of length 1 will be removed from the array
    """

    @property
    def data(self):
        """Override parent method to flip the SP arm array."""
        parent_data = super().data
        if self.arm_id == "SP":
            return np.flip(parent_data, 1)
        return parent_data

    @data.setter
    def data(self, value: np.array):
        """Override parent setter method to unflip the SP arm array."""
        if self.arm_id == "SP":
            value = np.flip(value, 1)
        super(CryonirspL0FitsAccess, type(self)).data.__set__(self, value)
