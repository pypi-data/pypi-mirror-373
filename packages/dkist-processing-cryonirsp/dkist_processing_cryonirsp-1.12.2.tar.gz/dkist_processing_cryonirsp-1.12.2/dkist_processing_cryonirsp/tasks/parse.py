"""Parse CryoNIRSP data."""

from typing import TypeVar

from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.parsers.cs_step import CSStepFlower
from dkist_processing_common.parsers.cs_step import NumCSStepBud
from dkist_processing_common.parsers.near_bud import TaskNearFloatBud
from dkist_processing_common.parsers.retarder import RetarderNameBud
from dkist_processing_common.parsers.single_value_single_key_flower import (
    SingleValueSingleKeyFlower,
)
from dkist_processing_common.parsers.task import PolcalTaskFlower
from dkist_processing_common.parsers.task import TaskTypeFlower
from dkist_processing_common.parsers.task import parse_header_ip_task_with_gains
from dkist_processing_common.parsers.time import ObsIpStartTimeBud
from dkist_processing_common.parsers.unique_bud import TaskUniqueBud
from dkist_processing_common.parsers.unique_bud import UniqueBud
from dkist_processing_common.tasks import ParseDataBase
from dkist_processing_common.tasks import default_constant_bud_factory
from dkist_processing_common.tasks import default_tag_flower_factory

from dkist_processing_cryonirsp.models.constants import CryonirspBudName
from dkist_processing_cryonirsp.models.parameters import CryonirspParsingParameters
from dkist_processing_cryonirsp.models.tags import CryonirspStemName
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.parsers.check_for_gains import CheckLampGainFramesPickyBud
from dkist_processing_cryonirsp.parsers.check_for_gains import CheckSolarGainFramesPickyBud
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import CryonirspL0FitsAccess
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import CryonirspRampFitsAccess
from dkist_processing_cryonirsp.parsers.exposure_conditions import (
    CryonirspCIConditionalTaskExposureConditionsBud,
)
from dkist_processing_cryonirsp.parsers.exposure_conditions import (
    CryonirspCIPickyDarkExposureConditionsBud,
)
from dkist_processing_cryonirsp.parsers.exposure_conditions import (
    CryonirspSPConditionalTaskExposureConditionsBud,
)
from dkist_processing_cryonirsp.parsers.exposure_conditions import (
    CryonirspSPPickyDarkExposureConditionsBud,
)
from dkist_processing_cryonirsp.parsers.exposure_conditions import (
    CryonirspTaskExposureConditionsBud,
)
from dkist_processing_cryonirsp.parsers.map_repeats import MapScanFlower
from dkist_processing_cryonirsp.parsers.map_repeats import NumMapScansBud
from dkist_processing_cryonirsp.parsers.measurements import MeasurementNumberFlower
from dkist_processing_cryonirsp.parsers.measurements import NumberOfMeasurementsBud
from dkist_processing_cryonirsp.parsers.modstates import ModstateNumberFlower
from dkist_processing_cryonirsp.parsers.optical_density_filters import OpticalDensityFiltersPickyBud
from dkist_processing_cryonirsp.parsers.polarimetric_check import PolarimetricCheckingUniqueBud
from dkist_processing_cryonirsp.parsers.scan_step import NumberOfScanStepsBud
from dkist_processing_cryonirsp.parsers.scan_step import ScanStepNumberFlower
from dkist_processing_cryonirsp.parsers.time import CryonirspSolarGainStartTimeBud
from dkist_processing_cryonirsp.parsers.time import CryonirspTimeObsBud
from dkist_processing_cryonirsp.parsers.wavelength import ObserveWavelengthBud

__all__ = [
    "ParseL0CryonirspRampData",
    "ParseL0CryonirspLinearizedData",
    "ParseL0CryonirspCILinearizedData",
    "ParseL0CryonirspSPLinearizedData",
]
S = TypeVar("S", bound=Stem)


class ParseL0CryonirspRampData(ParseDataBase):
    """
    Parse CryoNIRSP ramp data (raw Cryo data) to prepare for Linearity Correction, after which the rest of the common parsing will occur.

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
    def fits_parsing_class(self):
        """FITS access class to be used with this task."""
        return CryonirspRampFitsAccess

    @property
    def constant_buds(self) -> list[S]:
        """Add CryoNIRSP specific constants to common constants."""
        return [
            UniqueBud(
                constant_name=CryonirspBudName.camera_readout_mode.value,
                metadata_key="camera_readout_mode",
            ),
            # Time Obs is the unique identifier for each ramp in the data set
            CryonirspTimeObsBud(),
            # This is used to determine which set of linearity correction tables to use.
            UniqueBud(constant_name=CryonirspBudName.arm_id.value, metadata_key="arm_id"),
            # Need wavelength to do filter compensation
            ObserveWavelengthBud(),
            # Need the optical density filter name for early failure detection
            OpticalDensityFiltersPickyBud(),
            # Need IP start time to support parameter access
            ObsIpStartTimeBud(),
            # Get the ROI 1 size and origin
            UniqueBud(
                constant_name=CryonirspBudName.roi_1_origin_x.value, metadata_key="roi_1_origin_x"
            ),
            UniqueBud(
                constant_name=CryonirspBudName.roi_1_origin_y.value, metadata_key="roi_1_origin_y"
            ),
            UniqueBud(
                constant_name=CryonirspBudName.roi_1_size_x.value, metadata_key="roi_1_size_x"
            ),
            UniqueBud(
                constant_name=CryonirspBudName.roi_1_size_y.value, metadata_key="roi_1_size_y"
            ),
        ]

    @property
    def tag_flowers(self) -> list[S]:
        """Add CryoNIRSP specific tags to common tags."""
        return [
            SingleValueSingleKeyFlower(
                tag_stem_name=CryonirspStemName.curr_frame_in_ramp.value,
                metadata_key="curr_frame_in_ramp",
            ),
            # time_obs is a unique identifier for all raw frames in a single ramp
            SingleValueSingleKeyFlower(
                tag_stem_name=CryonirspStemName.time_obs.value,
                metadata_key="time_obs",
            ),
        ]

    @property
    def tags_for_input_frames(self) -> list[Tag]:
        """Tags for the input data to parse."""
        return [Tag.input(), Tag.frame()]


class ParseL0CryonirspLinearizedData(ParseDataBase):
    """
    Parse linearity corrected CryoNIRSP input data to add common and Cryonirsp specific constants.

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
        self.parameters = CryonirspParsingParameters(scratch=self.scratch)

    @property
    def fits_parsing_class(self):
        """FITS access class to be used in this task."""
        return CryonirspL0FitsAccess

    @property
    def tags_for_input_frames(self) -> list[Tag]:
        """Tags for the linearity corrected input frames."""
        return [CryonirspTag.linearized(), CryonirspTag.frame()]

    @property
    def constant_buds(self) -> list[S]:
        """Add CryoNIRSP specific constants to common constants."""
        return default_constant_bud_factory() + [
            NumMapScansBud(),
            NumberOfScanStepsBud(),
            NumberOfMeasurementsBud(),
            CryonirspSolarGainStartTimeBud(),
            CheckSolarGainFramesPickyBud(),
            NumCSStepBud(self.parameters.max_cs_step_time_sec),
            CryonirspTaskExposureConditionsBud(
                stem_name=CryonirspBudName.dark_frame_exposure_conditions_list.value,
                ip_task_type=TaskName.dark.value,
            ),
            CryonirspTaskExposureConditionsBud(
                stem_name=CryonirspBudName.solar_gain_exposure_conditions_list.value,
                ip_task_type=TaskName.solar_gain.value,
            ),
            CryonirspTaskExposureConditionsBud(
                stem_name=CryonirspBudName.observe_exposure_conditions_list.value,
                ip_task_type=TaskName.observe.value,
            ),
            CryonirspTaskExposureConditionsBud(
                stem_name=CryonirspBudName.polcal_exposure_conditions_list.value,
                ip_task_type=TaskName.polcal.value,
            ),
            UniqueBud(constant_name=CryonirspBudName.axis_1_type.value, metadata_key="axis_1_type"),
            UniqueBud(constant_name=CryonirspBudName.axis_2_type.value, metadata_key="axis_2_type"),
            UniqueBud(constant_name=CryonirspBudName.axis_3_type.value, metadata_key="axis_3_type"),
            PolarimetricCheckingUniqueBud(
                constant_name=CryonirspBudName.num_modstates.value,
                metadata_key="number_of_modulator_states",
            ),
            PolarimetricCheckingUniqueBud(
                constant_name=CryonirspBudName.modulator_spin_mode.value,
                metadata_key="modulator_spin_mode",
            ),
            RetarderNameBud(),
        ]

    @property
    def tag_flowers(self) -> list[S]:
        """Add CryoNIRSP specific tags to common tags."""
        return default_tag_flower_factory() + [
            TaskTypeFlower(header_task_parsing_func=parse_header_ip_task_with_gains),
            PolcalTaskFlower(),
            MapScanFlower(),
            ModstateNumberFlower(),
            CSStepFlower(max_cs_step_time_sec=self.parameters.max_cs_step_time_sec),
            ScanStepNumberFlower(),
            MeasurementNumberFlower(),
            SingleValueSingleKeyFlower(
                tag_stem_name=CryonirspStemName.exposure_conditions.value,
                metadata_key="exposure_conditions",
            ),
        ]


class ParseL0CryonirspSPLinearizedData(ParseL0CryonirspLinearizedData):
    """Parse linearity corrected CryoNIRSP-SP input data with SP arm specific constants."""

    @property
    def constant_buds(self) -> list[S]:
        """Add CryoNIRSP-SP specific constants to common constants."""
        return super().constant_buds + [
            TaskNearFloatBud(
                constant_name=CryonirspBudName.grating_position_deg.value,
                metadata_key="grating_position_deg",
                ip_task_types=[TaskName.observe.value, TaskName.solar_gain.value],
                task_type_parsing_function=parse_header_ip_task_with_gains,
                tolerance=0.01,
            ),
            TaskNearFloatBud(
                constant_name=CryonirspBudName.grating_littrow_angle_deg.value,
                metadata_key="grating_littrow_angle_deg",
                ip_task_types=[TaskName.observe.value, TaskName.solar_gain.value],
                task_type_parsing_function=parse_header_ip_task_with_gains,
                tolerance=0.01,
            ),
            TaskUniqueBud(
                constant_name=CryonirspBudName.grating_constant.value,
                metadata_key="grating_constant",
                ip_task_types=[TaskName.observe.value, TaskName.solar_gain.value],
                task_type_parsing_function=parse_header_ip_task_with_gains,
            ),
            TaskUniqueBud(
                constant_name=CryonirspBudName.wave_min.value,
                metadata_key="wave_min",
                ip_task_types=TaskName.solar_gain.value,
                task_type_parsing_function=parse_header_ip_task_with_gains,
            ),
            TaskUniqueBud(
                constant_name=CryonirspBudName.wave_max.value,
                metadata_key="wave_max",
                ip_task_types=TaskName.solar_gain.value,
                task_type_parsing_function=parse_header_ip_task_with_gains,
            ),
            TaskUniqueBud(
                constant_name=CryonirspBudName.center_wavelength.value,
                metadata_key="center_wavelength",
                ip_task_types=[TaskName.observe.value, TaskName.solar_gain.value],
                task_type_parsing_function=parse_header_ip_task_with_gains,
            ),
            TaskUniqueBud(
                constant_name=CryonirspBudName.slit_width.value,
                metadata_key="slit_width",
                ip_task_types=[TaskName.observe.value, TaskName.solar_gain.value],
                task_type_parsing_function=parse_header_ip_task_with_gains,
            ),
            CheckLampGainFramesPickyBud(),
            CryonirspTaskExposureConditionsBud(
                stem_name=CryonirspBudName.lamp_gain_exposure_conditions_list.value,
                ip_task_type=TaskName.lamp_gain.value,
            ),
            CryonirspSPConditionalTaskExposureConditionsBud(),
            CryonirspSPPickyDarkExposureConditionsBud(),
        ]


class ParseL0CryonirspCILinearizedData(ParseL0CryonirspLinearizedData):
    """Parse linearity corrected CryoNIRSP-CI input data with CI arm specific constants."""

    @property
    def constant_buds(self) -> list[S]:
        """Add CryoNIRSP-CI specific constants to common constants."""
        return super().constant_buds + [
            CryonirspCIConditionalTaskExposureConditionsBud(),
            CryonirspCIPickyDarkExposureConditionsBud(),
        ]
