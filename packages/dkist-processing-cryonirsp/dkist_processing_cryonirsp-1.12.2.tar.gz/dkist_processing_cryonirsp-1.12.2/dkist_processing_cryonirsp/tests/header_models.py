"""
Model header objects
"""

import datetime
import random
import uuid
from random import choice

import numpy as np
import pytest
from astropy.io import fits
from astropy.wcs import WCS
from dkist_data_simulator.dataset import key_function
from dkist_data_simulator.spec122 import Spec122Dataset
from dkist_header_validator import spec122_validator

from dkist_processing_cryonirsp.models.exposure_conditions import AllowableOpticalDensityFilterNames
from dkist_processing_cryonirsp.models.exposure_conditions import ExposureConditions


class CryonirspHeaders(Spec122Dataset):
    def __init__(
        self,
        dataset_shape: tuple[int, ...],
        array_shape: tuple[int, ...],
        time_delta: 10,
        instrument: str = "cryonirsp",
        exp_time: float = 15.0,
        **kwargs,
    ):
        super().__init__(
            dataset_shape=dataset_shape,
            array_shape=array_shape,
            time_delta=time_delta,
            instrument=instrument,
            **kwargs,
        )
        self.add_constant_key("WAVELNTH", 1083.0)
        self.add_constant_key("CUNIT1", "nm")
        self.add_constant_key("CDELT1", 0.2)
        self.add_constant_key("CRVAL1", 1083.0)
        # num modstates
        self.add_constant_key("CRSP_041", 2)
        self.add_constant_key("ID___013", "TEST_PROPOSAL_ID")
        # polarizer_status angle
        self.add_constant_key("PAC__005", "0")
        # retarder_status angle
        self.add_constant_key("PAC__007", "10")
        self.add_constant_key("ID___002", uuid.uuid4().hex)
        self.add_constant_key("CRSP_095", "HeI")
        self.add_constant_key("CRSP_053", 1083.0)
        self.add_constant_key("CRSP_054", 1.0)

        self.add_constant_key("CAM__004", exp_time)

    @key_function("CRSP_042")
    # current modstate
    def current_modstate(self, key: str):
        return choice([1, 2])

    @key_function("CRSP_035")
    # CNM1POS
    def current_m1_position(self, key: str):
        return random.randrange(-150, 150)

    @key_function("CRSP_036")
    # CNM1BPOS
    def current_m1b_position(self, key: str):
        return random.randrange(-150, 150)

    @key_function("CRSP_103")
    # CNM1OFF
    def current_m1_offset(self, key: str):
        return random.randrange(-10, 10)

    @key_function("CRSP_104")
    # CNM1BOFF
    def current_m1b_offset(self, key: str):
        return random.randrange(-10, 10)

    @property
    def fits_wcs(self):
        w = WCS(naxis=self.array_ndim)
        w.wcs.crpix = self.array_shape[2] / 2, self.array_shape[1] / 2, 1
        w.wcs.crval = 1083.0, 0, 0
        w.wcs.cdelt = 0.2, 1, 1
        w.wcs.cunit = "nm", "arcsec", "arcsec"
        w.wcs.ctype = "AWAV", "HPLT-TAN", "HPLN-TAN"
        w.wcs.pc = np.identity(self.array_ndim)
        return w


class CryonirspCIHeaders(CryonirspHeaders):
    @property
    def fits_wcs(self):
        w = WCS(naxis=self.array_ndim)
        w.wcs.crpix = self.array_shape[2] / 2, self.array_shape[1] / 2, 1
        w.wcs.crval = 0, 0, 1083.0
        w.wcs.cdelt = 1, 1, 0.2
        w.wcs.cunit = "arcsec", "arcsec", "nm"
        w.wcs.ctype = "HPLN-TAN", "HPLT-TAN", "AWAV"
        w.wcs.pc = np.identity(self.array_ndim)
        return w


class CryonirspHeadersValidNonLinearizedFrames(CryonirspHeaders):
    def __init__(
        self,
        dataset_shape: tuple[int, ...],
        array_shape: tuple[int, ...],
        camera_readout_mode: str,
        time_delta: float,
        roi_x_origin: int,
        roi_x_size: int,
        roi_y_origin: int,
        roi_y_size: int,
        date_obs: str,
        exposure_time: float,
        arm_id: str,
        **kwargs,
    ):
        super().__init__(dataset_shape, array_shape, time_delta, **kwargs)
        self.add_constant_key("DKIST004", "observe")
        self.add_constant_key("ID___004")
        self.add_constant_key("CRSP_001", arm_id)
        self.add_constant_key("CRSP_060", camera_readout_mode)
        self.add_constant_key("CAM__034", roi_x_origin)
        self.add_constant_key("CAM__035", roi_y_origin)
        self.add_constant_key("CAM__036", roi_x_size)
        self.add_constant_key("CAM__037", roi_y_size)
        self.add_constant_key("DATE-OBS", date_obs)
        self.add_constant_key("TEXPOSUR", exposure_time)
        self.add_constant_key("CNFILTNP", AllowableOpticalDensityFilterNames.G358.value)
        self.add_constant_key("DKIST011", "1999-12-31T23:59:59")

    @key_function("CRSP_063")
    # current frame number in current ramp
    def current_frame_number(self, key: str):
        return self.index

    @key_function("XPOSURE")
    # set the exposure time for each frame in the ramp
    def exposure_time(self, key: float):
        return 100 * self.index * 0.01


class CryonirspHeadersValidDarkFrames(CryonirspHeaders):
    def __init__(
        self,
        dataset_shape: tuple[int, ...],
        array_shape: tuple[int, ...],
        time_delta: float,
        exposure_time: float,
        **kwargs,
    ):
        super().__init__(dataset_shape, array_shape, time_delta, **kwargs)
        # IP task
        self.add_constant_key("DKIST004", "dark")
        # num dsps repeats
        self.add_constant_key("DKIST008", 1)
        # dsps repeat num
        self.add_constant_key("DKIST009", 1)
        # num scan positions
        self.add_constant_key("CRSP_006", 1)
        # current scan pos
        self.add_constant_key("CRSP_007", 1)
        # inst prog id
        self.add_constant_key("ID___004")
        self.add_constant_key(
            "WAVELNTH", 0.0
        )  # Intentionally bad to make sure it doesn't get parsed
        # cam exposure time
        self.add_constant_key("CAM__004", exposure_time)
        # num_modstates and modstate are always 1 for dark frames
        self.add_constant_key("CRSP_041", 1)
        self.add_constant_key("CRSP_042", 1)


class CryonirspHeadersValidLampGainFrames(CryonirspHeaders):
    def __init__(
        self,
        dataset_shape: tuple[int, ...],
        array_shape: tuple[int, ...],
        time_delta: float,
        **kwargs,
    ):
        super().__init__(dataset_shape, array_shape, time_delta, **kwargs)
        # IP task
        self.add_constant_key("DKIST004", "gain")
        # lamp (clear, lamp, undefined)
        self.add_constant_key("PAC__002", "lamp")
        # num dsps repeats
        self.add_constant_key("DKIST008", 1)
        # dsps repeat num
        self.add_constant_key("DKIST009", 1)
        # num scan positions
        self.add_constant_key("CRSP_006", 1)
        # current scan pos
        self.add_constant_key("CRSP_007", 1)
        # lamp status
        self.add_constant_key("PAC__003", "on")
        # inst prog id
        self.add_constant_key("ID___004")
        # num_modstates and modstate are always 1 for gain frames
        self.add_constant_key("CRSP_041", 1)
        self.add_constant_key("CRSP_042", 1)
        # cam exposure time
        self.add_constant_key("CAM__004", 10.0)


class CryonirspHeadersValidCISolarGainFrames(CryonirspHeaders):
    def __init__(
        self,
        dataset_shape: tuple[int, ...],
        array_shape: tuple[int, ...],
        time_delta: float,
        **kwargs,
    ):
        super().__init__(dataset_shape, array_shape, time_delta, **kwargs)
        # IP task
        self.add_constant_key("DKIST004", "gain")
        # num dsps repeats
        self.add_constant_key("DKIST008", 1)
        # dsps repeat num
        self.add_constant_key("DKIST009", 1)
        # num scan positions
        self.add_constant_key("CRSP_006", 1)
        # current scan pos
        self.add_constant_key("CRSP_007", 1)
        # lamp (clear, lamp, undefined)
        self.add_constant_key("PAC__002", "clear")
        self.add_constant_key("TELSCAN", "Raster")
        # inst prog id
        self.add_constant_key("ID___004")
        # num_modstates and modstate are always 1 for gain frames
        self.add_constant_key("CRSP_041", 1)
        self.add_constant_key("CRSP_042", 1)
        # cam exposure time
        self.add_constant_key("CAM__004", 20.0)
        # arm_id
        self.add_constant_key("CRSP_001", "CI")


class CryonirspHeadersValidSPSolarGainFrames(CryonirspHeaders):
    def __init__(
        self,
        dataset_shape: tuple[int, ...],
        array_shape: tuple[int, ...],
        time_delta: float,
        **kwargs,
    ):
        super().__init__(dataset_shape, array_shape, time_delta, **kwargs)
        # IP task
        self.add_constant_key("DKIST004", "gain")
        # num dsps repeats
        self.add_constant_key("DKIST008", 1)
        # dsps repeat num
        self.add_constant_key("DKIST009", 1)
        # num scan positions
        self.add_constant_key("CRSP_006", 1)
        # current scan pos
        self.add_constant_key("CRSP_007", 1)
        # lamp (clear, lamp, undefined)
        self.add_constant_key("PAC__002", "clear")
        self.add_constant_key("TELSCAN", "Raster")
        # inst prog id
        self.add_constant_key("ID___004")
        # num_modstates and modstate are always 1 for gain frames
        self.add_constant_key("CRSP_041", 1)
        self.add_constant_key("CRSP_042", 1)
        # cam exposure time
        self.add_constant_key("CAM__004", 20.0)
        # arm_id
        self.add_constant_key("CRSP_001", "SP")


class CryonirspHeadersValidPolcalFrames(CryonirspHeaders):
    def __init__(
        self,
        dataset_shape: tuple[int, ...],
        array_shape: tuple[int, ...],
        time_delta: float,
        num_modstates: int,
        modstate: int,
        **kwargs,
    ):
        super().__init__(dataset_shape, array_shape, time_delta, **kwargs)
        self.add_constant_key("DKIST004", "polcal")
        self.add_constant_key("DKIST008", 1)
        self.add_constant_key("DKIST009", 1)
        self.add_constant_key("CRSP_006", 1)
        self.add_constant_key("CRSP_007", 1)
        self.add_constant_key("TELSCAN", "Raster")
        self.add_constant_key("ID___004")
        self.add_constant_key("PAC__004", "Sapphire Polarizer")
        self.add_constant_key("PAC__005", "60.")
        self.add_constant_key("PAC__006", "clear")
        self.add_constant_key("PAC__007", "0.0")
        self.add_constant_key("PAC__008", "FieldStop (5arcmin)")
        self.add_constant_key("CRSP_041", num_modstates)
        self.add_constant_key("CRSP_042", modstate)
        self.add_constant_key("CRSP_044", "Continuous")
        self.add_constant_key("CAM__004", 0.01)


class CryonirspHeadersValidObserveFrames(CryonirspHeaders):
    def __init__(
        self,
        dataset_shape: tuple[int, ...],
        array_shape: tuple[int, ...],
        time_delta: float,
        num_map_scans: int,
        map_scan: int,
        num_scan_steps: int,
        scan_step: int,
        num_modstates: int,
        modstate: int,
        num_meas: int,
        meas_num: int,
        arm_id: str,
        num_sub_repeats=1,
        sub_repeat_num=1,
        **kwargs,
    ):
        super().__init__(dataset_shape, array_shape, time_delta, **kwargs)
        self.num_map_scans = num_map_scans
        self.num_scan_steps = num_scan_steps
        self.meas_num = meas_num
        self.add_constant_key("NAXIS1", 2048)
        self.add_constant_key("CRSP_101", num_sub_repeats)
        self.add_constant_key("CRSP_102", sub_repeat_num)
        self.add_constant_key("DKIST004", "observe")
        self.add_constant_key("CRSP_001", arm_id)
        self.add_constant_key("CRSP_006", num_scan_steps)
        self.add_constant_key("CRSP_007", scan_step)
        self.add_constant_key("DKIST008", num_map_scans)
        self.add_constant_key("DKIST009", map_scan)
        self.add_constant_key("ID___004")
        self.add_constant_key("CRSP_041", num_modstates)
        self.add_constant_key("CRSP_042", modstate)
        self.add_constant_key("CRSP_044", "Continuous")
        self.add_constant_key("CRSP_057", num_meas)
        self.add_constant_key("CRSP_058", meas_num)
        self.add_constant_key("WAVELNTH", 1080.2)
        self.add_constant_key("ID___012", "EXPERIMENT ID")

    @key_function("CAM__004")
    def exposure_time(self, key: str) -> float:
        return 0.02 if self.index % 2 == 0 else 0.03


class Cryonirsp122ObserveFrames(CryonirspHeaders):
    def __init__(
        self,
        array_shape: tuple[int, ...],
        num_steps: int = 4,
        num_exp_per_step: int = 1,
        num_map_scans: int = 5,
    ):
        super().__init__(
            array_shape=array_shape,
            time_delta=10,
            dataset_shape=(num_exp_per_step * num_steps * num_map_scans,) + array_shape[-2:],
        )
        self.add_constant_key("DKIST004", "observe")


class SimpleModulatedHeaders(CryonirspHeaders):
    def __init__(
        self,
        num_modstates: int,
        modstate: int,
        array_shape: tuple[int, ...],
        task: str,
        exposure_condition: ExposureConditions = ExposureConditions(
            6.0, AllowableOpticalDensityFilterNames.OPEN.value
        ),
        start_date: str = "2023-01-01T01:23:45",
        modstate_length_sec: float = 0.5,
        center_wavelength: float = 1080.0,
        slit_width: float = 52.0,
    ):
        dataset_shape = (1, *array_shape)
        super().__init__(
            dataset_shape=dataset_shape,
            array_shape=array_shape,
            start_time=datetime.datetime.fromisoformat(start_date),
            time_delta=modstate_length_sec,
        )

        grating_angle_deg = 264984.2432
        grating_littrow_angle = 173832.95442475166
        grating_constant = 770970.3576216539
        CRVAL1 = 1.083e-06
        CRPIX1 = 0.5
        CDELT1 = 2e-10

        self.add_constant_key("DKIST004", task)
        self.add_constant_key("CRSP_041", num_modstates)
        self.add_constant_key("CRSP_042", modstate)
        self.add_constant_key("CAM__004", exposure_condition.exposure_time)
        self.add_constant_key("CRSP_048", exposure_condition.filter_name)
        self.add_constant_key("CRSP_053", center_wavelength)
        self.add_constant_key("CRSP_074", grating_angle_deg)
        self.add_constant_key("CRSP_079", grating_littrow_angle)
        self.add_constant_key("CRSP_077", grating_constant)
        self.add_constant_key("CRSP_082", slit_width)
        self.add_constant_key("CRVAL1", CRVAL1)
        self.add_constant_key("CRPIX1", CRPIX1)
        self.add_constant_key("CDELT1", CDELT1)


class ModulatedLampGainHeaders(SimpleModulatedHeaders):
    def __init__(
        self,
        array_shape: tuple[int, ...],
        exposure_condition: ExposureConditions,
        start_date: str = "2023-01-01T01:23:45",
        modstate_length_sec: float = 0.5,
        num_modstates: int = 1,
        modstate: int = 1,
    ):
        super().__init__(
            num_modstates=num_modstates,
            modstate=modstate,
            array_shape=array_shape,
            task="gain",
            exposure_condition=exposure_condition,
            start_date=start_date,
            modstate_length_sec=modstate_length_sec,
        )

        self.add_constant_key("PAC__002", "lamp")
        self.add_constant_key("PAC__003", "on")
        # num dsps repeats
        self.add_constant_key("DKIST008", 1)
        # dsps repeat num
        self.add_constant_key("DKIST009", 1)
        # num scan positions
        self.add_constant_key("CRSP_006", 1)
        # current scan pos
        self.add_constant_key("CRSP_007", 1)
        self.add_constant_key("ID___004")


class ModulatedSolarGainHeaders(SimpleModulatedHeaders):
    def __init__(
        self,
        array_shape: tuple[int, ...],
        exposure_condition: ExposureConditions,
        start_date: str = "2023-01-01T01:23:45",
        modstate_length_sec: float = 0.5,
        num_modstates: int = 1,
        modstate: int = 1,
        center_wavelength: float = 1080.0,
        slit_width: float = 52.0,
    ):
        super().__init__(
            num_modstates=num_modstates,
            modstate=modstate,
            array_shape=array_shape,
            task="gain",
            exposure_condition=exposure_condition,
            start_date=start_date,
            modstate_length_sec=modstate_length_sec,
            center_wavelength=center_wavelength,
            slit_width=slit_width,
        )

        self.add_constant_key("PAC__002", "clear")
        self.add_constant_key("PAC__003", "undefined")
        self.add_constant_key("TELSCAN", "Raster")
        # num dsps repeats
        self.add_constant_key("DKIST008", 1)
        # dsps repeat num
        self.add_constant_key("DKIST009", 1)
        # num scan positions
        self.add_constant_key("CRSP_006", 1)
        # current scan pos
        self.add_constant_key("CRSP_007", 1)
        # inst prog id
        self.add_constant_key("ID___004")


class ModulatedDarkHeaders(SimpleModulatedHeaders):
    def __init__(
        self,
        array_shape: tuple[int, ...],
        exposure_condition: ExposureConditions,
        start_date: str = "2023-01-01T01:23:45",
        modstate_length_sec: float = 0.5,
        num_modstates: int = 1,
        modstate: int = 1,
    ):
        super().__init__(
            num_modstates=num_modstates,
            modstate=modstate,
            array_shape=array_shape,
            task="dark",
            exposure_condition=exposure_condition,
            start_date=start_date,
            modstate_length_sec=modstate_length_sec,
        )

        # num dsps repeats
        self.add_constant_key("DKIST008", 1)
        # dsps repeat num
        self.add_constant_key("DKIST009", 1)
        # num scan positions
        self.add_constant_key("CRSP_006", 1)
        # current scan pos
        self.add_constant_key("CRSP_007", 1)
        # inst prog id
        self.add_constant_key("ID___004")
        self.add_constant_key("WAVELNTH", 0.0)


class ModulatedPolcalHeaders(SimpleModulatedHeaders):
    def __init__(
        self,
        num_modstates: int,
        modstate: int,
        array_shape: tuple[int, ...],
        exposure_condition: ExposureConditions,
        extra_headers: dict | None = None,
        start_date: str = "2023-01-01T01:23:45",
        modstate_length_sec: float = 0.5,
    ):
        super().__init__(
            num_modstates=num_modstates,
            modstate=modstate,
            array_shape=array_shape,
            task="polcal",
            exposure_condition=exposure_condition,
            start_date=start_date,
            modstate_length_sec=modstate_length_sec,
        )

        self.add_constant_key("DKIST004", "polcal")
        self.add_constant_key("DKIST008", 1)
        self.add_constant_key("DKIST009", 1)
        self.add_constant_key("CRSP_006", 1)
        self.add_constant_key("CRSP_007", 1)
        self.add_constant_key("TELSCAN", "Raster")
        self.add_constant_key("ID___004")
        self.add_constant_key("PAC__005", "60.")
        self.add_constant_key("PAC__007", "0.0")
        self.add_constant_key("CRSP_044", "Continuous")

        default_pac_values = {
            "PAC__004": "Sapphire Polarizer",
            "PAC__006": "clear",
            "PAC__008": "FieldStop (5arcmin)",
        }
        if extra_headers is None:
            extra_headers = dict()
        for header, value in (default_pac_values | extra_headers).items():
            self.add_constant_key(header, value)


class ModulatedObserveHeaders(SimpleModulatedHeaders):
    def __init__(
        self,
        num_modstates: int,
        modstate: int,
        array_shape: tuple[int, ...],
        exposure_condition: ExposureConditions,
        num_map_scans: int,
        num_scan_steps: int,
        scan_step: int,
        map_scan: int,
        num_meas: int,
        num_sub_repeats: int,
        sub_repeat_num: int,
        arm_id: str,
        start_date: str = "2023-01-01T01:23:45",
        modstate_length_sec: float = 0.5,
        meas_num: int = 1,
        center_wavelength: float = 1080.0,
        slit_width: float = 52.0,
    ):
        super().__init__(
            num_modstates=num_modstates,
            modstate=modstate,
            array_shape=array_shape,
            task="observe",
            exposure_condition=exposure_condition,
            start_date=start_date,
            modstate_length_sec=modstate_length_sec,
            center_wavelength=center_wavelength,
            slit_width=slit_width,
        )

        self.num_map_scans = num_map_scans
        self.num_scan_steps = num_scan_steps
        self.meas_num = meas_num
        self.add_constant_key("CRSP_101", num_sub_repeats)
        self.add_constant_key("CRSP_102", sub_repeat_num)
        self.add_constant_key("CRSP_001", arm_id)
        self.add_constant_key("CRSP_006", num_scan_steps)
        self.add_constant_key("CRSP_007", scan_step)
        self.add_constant_key("DKIST008", num_map_scans)
        self.add_constant_key("DKIST009", map_scan)
        self.add_constant_key("ID___004")
        self.add_constant_key("CRSP_044", "Continuous")
        self.add_constant_key("CRSP_057", num_meas)
        self.add_constant_key("CRSP_058", meas_num)
        self.add_constant_key("WAVELNTH", 1080.2)
        self.add_constant_key("ID___012", "EXPERIMENT ID")
