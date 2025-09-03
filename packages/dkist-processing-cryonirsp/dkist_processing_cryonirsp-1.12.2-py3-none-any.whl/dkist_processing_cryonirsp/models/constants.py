"""CryoNIRSP additions to common constants."""

from enum import Enum
from enum import unique

import astropy.units as u
from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.constants import ConstantsBase

from dkist_processing_cryonirsp.models.exposure_conditions import ExposureConditions


@unique
class CryonirspBudName(Enum):
    """Names to be used for CryoNIRSP buds."""

    arm_id = "ARM_ID"
    num_beams = "NUM_BEAMS"
    num_scan_steps = "NUM_SCAN_STEPS"
    num_map_scans = "NUM_MAP_SCANS"
    num_modstates = "NUM_MODSTATES"
    wavelength = "WAVELENGTH"
    wave_min = "WAVE_MIN"
    wave_max = "WAVE_MAX"
    grating_position_deg = "GRATING_POSITION_DEG"
    grating_littrow_angle_deg = "GRATING_LITTROW_ANGLE_DEG"
    grating_constant = "GRATING_CONSTANT"
    camera_readout_mode = "CAM_READOUT_MODE"
    num_meas = "NUM_MEAS"
    time_obs_list = "TIME_OBS_LIST"
    exposure_conditions_list = "EXPOSURE_CONDITIONS_LIST"
    dark_frame_exposure_conditions_list = "DARK_FRAME_EXPOSURE_CONDITIONS_LIST"
    lamp_gain_exposure_conditions_list = "LAMP_GAIN_EXPOSURE_CONDITIONS_LIST"
    solar_gain_exposure_conditions_list = "SOLAR_GAIN_EXPOSURE_CONDITIONS_LIST"
    polcal_exposure_conditions_list = "POLCAL_EXPOSURE_CONDITIONS_LIST"
    observe_exposure_conditions_list = "OBSERVE_EXPOSURE_CONDITIONS_LIST"
    sp_non_dark_and_non_polcal_task_exposure_conditions_list = (
        "SP_NON_DARK_AND_NON_POLCAL_TASK_EXPOSURE_CONDITIONS_LIST"
    )
    ci_non_dark_and_non_polcal_and_non_lamp_gain_task_exposure_conditions_list = (
        "CI_NON_DARK_AND_NON_POLCAL_AND_NON_LAMP_GAIN_TASK_EXPOSURE_CONDITIONS_LIST"
    )
    picky_dark_exposure_conditions_list = "PICKY_DARK_EXPOSURE_CONDITIONS_LIST"
    ci_picky_dark_exposure_conditions_list = "CI_PICKY_DARK_EXPOSURE_CONDITIONS_LIST"
    sp_picky_dark_exposure_conditions_list = "SP_PICKY_DARK_EXPOSURE_CONDITIONS_LIST"
    modulator_spin_mode = "MODULATOR_SPIN_MODE"
    axis_1_type = "AXIS_1_TYPE"
    axis_2_type = "AXIS_2_TYPE"
    axis_3_type = "AXIS_3_TYPE"
    roi_1_origin_x = "ROI_1_ORIGIN_X"
    roi_1_origin_y = "ROI_1_ORIGIN_Y"
    roi_1_size_x = "ROI_1_SIZE_X"
    roi_1_size_y = "ROI_1_SIZE_Y"
    optical_density_filter_picky_bud = "OPTICAL_DENSITY_FILTER_PICKY_BUD"
    solar_gain_ip_start_time = "SOLAR_GAIN_IP_START_TIME"
    gain_frame_type_list = "GAIN_FRAME_TYPE_LIST"
    lamp_gain_frame_type_list = "LAMP_GAIN_FRAME_TYPE_LIST"
    solar_gain_frame_type_list = "SOLAR_GAIN_FRAME_TYPE_LIST"
    center_wavelength = "CENTER_WAVELENGTH"
    slit_width = "SLIT_WIDTH"


class CryonirspConstants(ConstantsBase):
    """CryoNIRSP specific constants to add to the common constants."""

    @property
    def arm_id(self) -> str:
        """Arm used to record the data, SP or CI."""
        return self._db_dict[CryonirspBudName.arm_id.value]

    @property
    def num_beams(self) -> int:
        """Determine the number of beams present in the data."""
        if self.arm_id == "SP":
            return 2
        else:
            return 1

    @property
    def num_scan_steps(self) -> int:
        """Determine the number of scan steps."""
        return self._db_dict[CryonirspBudName.num_scan_steps.value]

    @property
    def num_map_scans(self) -> int:
        """Determine the number of scan steps."""
        return self._db_dict[CryonirspBudName.num_map_scans.value]

    @property
    def wavelength(self) -> float:
        """Wavelength."""
        return self._db_dict[CryonirspBudName.wavelength.value]

    @property
    def wave_min(self) -> float:
        """Wavelength minimum."""
        return self._db_dict[CryonirspBudName.wave_min.value]

    @property
    def wave_max(self) -> float:
        """Wavelength maximum."""
        return self._db_dict[CryonirspBudName.wave_max.value]

    @property
    def solar_gain_ip_start_time(self) -> str:
        """Solar gain IP start time."""
        return self._db_dict[CryonirspBudName.solar_gain_ip_start_time.value]

    @property
    def grating_position_deg(self) -> float:
        """Grating position angle (deg)."""
        return self._db_dict[CryonirspBudName.grating_position_deg.value]

    @property
    def grating_littrow_angle_deg(self) -> float:
        """Grating littrow angle (deg)."""
        return self._db_dict[CryonirspBudName.grating_littrow_angle_deg.value]

    @property
    def center_wavelength(self) -> float:
        """Center wavelength of the selected filter (nm)."""
        return self._db_dict[CryonirspBudName.center_wavelength.value]

    @property
    def slit_width(self) -> float:
        """Physical width of the selected slit (um)."""
        return self._db_dict[CryonirspBudName.slit_width.value]

    @property
    def grating_constant(self) -> float:
        """Grating constant."""
        return self._db_dict[CryonirspBudName.grating_constant.value] / u.mm

    @property
    def camera_readout_mode(self) -> str:
        """Determine the readout mode of the camera."""
        return self._db_dict[CryonirspBudName.camera_readout_mode.value]

    @property
    def num_meas(self) -> int:
        """Determine the number of measurements in dataset."""
        return self._db_dict[CryonirspBudName.num_meas.value]

    @property
    def time_obs_list(self) -> tuple[str]:
        """Construct a sorted tuple of all the dateobs for this dataset."""
        return self._db_dict[CryonirspBudName.time_obs_list.value]

    @property
    def gain_frame_type_list(self) -> list[str]:
        """Construct a list of all the types of gain frames for this dataset."""
        return self._db_dict[CryonirspBudName.gain_frame_type_list.value]

    @property
    def exposure_conditions_list(self) -> [ExposureConditions]:
        """Construct a list of ExposureConditions tuples for the dataset."""
        raw_conditions: list[list[int, str]] = self._db_dict[
            CryonirspBudName.exposure_conditions.value
        ]
        conditions = [ExposureConditions(*item) for item in raw_conditions]
        return conditions

    @property
    def dark_exposure_conditions_list(self) -> [ExposureConditions]:
        """Construct a list of dark frame ExposureConditions tuples for the dataset."""
        raw_conditions: list[list[int, str]] = self._db_dict[
            CryonirspBudName.dark_frame_exposure_conditions_list.value
        ]
        conditions = [ExposureConditions(*item) for item in raw_conditions]
        return conditions

    @property
    def lamp_gain_exposure_conditions_list(self) -> [ExposureConditions]:
        """Construct a list of lamp gain ExposureConditions tuples for the dataset."""
        raw_conditions: list[list[int, str]] = self._db_dict[
            CryonirspBudName.lamp_gain_exposure_conditions_list.value
        ]
        conditions = [ExposureConditions(*item) for item in raw_conditions]
        return conditions

    @property
    def solar_gain_exposure_conditions_list(self) -> [ExposureConditions]:
        """Construct a list of solar gain ExposureConditions tuples for the dataset."""
        raw_conditions: list[list[int, str]] = self._db_dict[
            CryonirspBudName.solar_gain_exposure_conditions_list.value
        ]
        conditions = [ExposureConditions(*item) for item in raw_conditions]
        return conditions

    @property
    def observe_exposure_conditions_list(self) -> [ExposureConditions]:
        """Construct a list of observe ExposureConditions tuples for the dataset."""
        raw_conditions: list[list[int, str]] = self._db_dict[
            CryonirspBudName.observe_exposure_conditions_list.value
        ]
        conditions = [ExposureConditions(*item) for item in raw_conditions]
        return conditions

    @property
    def polcal_exposure_conditions_list(self) -> [ExposureConditions]:
        """Construct a list of polcal ExposureConditions tuples for the dataset."""
        if self.correct_for_polarization:
            raw_conditions: list[list[int, str]] = self._db_dict[
                CryonirspBudName.polcal_exposure_conditions_list.value
            ]
            conditions = [ExposureConditions(*item) for item in raw_conditions]
            return conditions
        else:
            return []

    @property
    def ci_non_dark_and_non_polcal_and_non_lamp_gain_task_exposure_conditions_list(
        self,
    ) -> [ExposureConditions]:
        """Return a list of all exposure times required for all tasks other than dark, polcal, and lamp gain."""
        raw_conditions: list[list[int, str]] = self._db_dict[
            CryonirspBudName.ci_non_dark_and_non_polcal_and_non_lamp_gain_task_exposure_conditions_list.value
        ]
        conditions = [ExposureConditions(*item) for item in raw_conditions]
        return conditions

    @property
    def sp_non_dark_and_non_polcal_task_exposure_conditions_list(self) -> [ExposureConditions]:
        """Return a list of all exposure times required for all tasks other than dark and polcal."""
        raw_conditions: list[list[int, str]] = self._db_dict[
            CryonirspBudName.sp_non_dark_and_non_polcal_task_exposure_conditions_list.value
        ]
        conditions = [ExposureConditions(*item) for item in raw_conditions]
        return conditions

    @property
    def num_modstates(self) -> int:
        """Find the number of modulation states."""
        return self._db_dict[CryonirspBudName.num_modstates.value]

    @property
    def num_cs_steps(self) -> int:
        """Find the number of calibration sequence steps."""
        return self._db_dict[BudName.num_cs_steps.value]

    @property
    def stokes_I_list(self) -> [str]:
        """List containing only the Stokes-I parameter."""
        return ["I"]

    @property
    def correct_for_polarization(self) -> bool:
        """Correct for polarization."""
        return self.num_modstates > 1 and self._db_dict[
            CryonirspBudName.modulator_spin_mode.value
        ] in ["Continuous", "Stepped"]

    @property
    def pac_init_set(self):
        """Return the label for the initial set of parameter values used when fitting demodulation matrices."""
        retarder_name = self._db_dict[BudName.retarder_name.value]
        match retarder_name:
            case "SiO2 OC":
                return "OCCal_VIS"
            case _:
                raise ValueError(f"No init set known for {retarder_name = }")

    @property
    def axis_1_type(self) -> str:
        """Find the type of the first array axis."""
        return self._db_dict[CryonirspBudName.axis_1_type.value]

    @property
    def axis_2_type(self) -> str:
        """Find the type of the second array axis."""
        return self._db_dict[CryonirspBudName.axis_2_type.value]

    @property
    def axis_3_type(self) -> str:
        """Find the type of the third array axis."""
        return self._db_dict[CryonirspBudName.axis_3_type.value]

    @property
    def roi_1_origin_x(self) -> int:
        """Get the ROI #1 x origin."""
        return self._db_dict[CryonirspBudName.roi_1_origin_x.value]

    @property
    def roi_1_origin_y(self) -> int:
        """Get the ROI #1 y origin."""
        return self._db_dict[CryonirspBudName.roi_1_origin_y.value]

    @property
    def roi_1_size_x(self) -> int:
        """Get the ROI #1 x size."""
        return self._db_dict[CryonirspBudName.roi_1_size_x.value]

    @property
    def roi_1_size_y(self) -> int:
        """Get the ROI #1 y size."""
        return self._db_dict[CryonirspBudName.roi_1_size_y.value]
