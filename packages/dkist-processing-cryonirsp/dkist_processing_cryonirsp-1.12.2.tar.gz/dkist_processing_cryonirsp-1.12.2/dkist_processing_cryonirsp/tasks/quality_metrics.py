"""Cryonirsp quality metrics task."""

from dataclasses import dataclass
from dataclasses import field
from typing import Generator
from typing import Iterable

import numpy as np
from astropy.time import Time
from dkist_processing_common.parsers.quality import L1QualityFitsAccess
from dkist_processing_common.tasks import QualityL0Metrics
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_service_configuration.logging import logger

from dkist_processing_cryonirsp.codecs.fits import cryo_fits_access_decoder
from dkist_processing_cryonirsp.models.constants import CryonirspConstants
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.tasks.cryonirsp_base import CryonirspTaskBase

__all__ = ["CryonirspL0QualityMetrics", "CryonirspL1QualityMetrics"]


@dataclass
class _QualityDataPoint:
    """Class for storage of a single Cryonirsp quality data point in a time series."""

    datetime: str | int  # isot | mjd
    value: float


@dataclass
class _QualityData:
    """Class for storage of Cryonirsp time series quality data."""

    data_points: list[_QualityDataPoint] = field(default_factory=list)

    @property
    def datetimes(self) -> list[str | int]:
        """Parse datetimes from list of data points."""
        return [dp.datetime for dp in self.data_points]

    @property
    def values(self) -> list[float]:
        """Parse values from list of data points."""
        return [dp.value for dp in self.data_points]

    def __len__(self):
        return len(self.data_points)


class CryonirspL0QualityMetrics(QualityL0Metrics):
    """
    Task class for collection of Cryonirsp L0 specific quality metrics.

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
    def constants_model_class(self):
        """Class for Cryonirsp constants."""
        return CryonirspConstants

    @property
    def raw_frame_tag(self) -> str:
        """
        Define tag corresponding to L0 data.

        For Cryo it's LINEARIZED.
        """
        return CryonirspTag.linearized()

    @property
    def modstate_list(self) -> Iterable[int] | None:
        """
        Define the list of modstates over which to compute L0 quality metrics.

        If the dataset is non-polarimetric then we just compute all metrics over all modstates at once.
        """
        if self.constants.correct_for_polarization:
            return range(1, self.constants.num_modstates + 1)

        return None


class CryonirspL1QualityMetrics(CryonirspTaskBase, QualityMixin):
    """
    Task class for collection of Cryonirsp L1 specific quality metrics.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs

    """

    def run(self) -> None:
        """Calculate sensitivity and noise quality metrics."""
        if self.constants.correct_for_polarization:
            with self.apm_processing_step(
                "Calculating L1 Sensitivity metrics for all stokes states"
            ):
                self.compute_full_stokes_sensitivity()
            with self.apm_task_step("Calculating L1 Cryonirsp noise metrics for all stokes states"):
                self.compute_full_stokes_noise()
        else:
            with self.apm_processing_step("Calculating L1 Sensitivity metrics for intensity only"):
                self.compute_intensity_only_sensitivity()
            with self.apm_task_step("Calculating L1 Cryonirsp noise metrics for intensity only"):
                self.compute_intensity_only_noise()

    def compute_full_stokes_sensitivity(self):
        """Compute the sensitivities of each map scan for each stokes state."""
        for stokes_state in self.constants.stokes_params:
            with self.apm_processing_step(f"Calculating sensitivity for stokes = {stokes_state}"):
                quality_data = self.calculate_sensitivity_for_stokes_state(
                    stokes_state=stokes_state
                )
            with self.apm_writing_step(f"Writing sensitivity data for stokes = {stokes_state}"):
                self.quality_store_sensitivity(
                    stokes=stokes_state,
                    datetimes=quality_data.datetimes,
                    values=quality_data.values,
                )

    def compute_intensity_only_sensitivity(self):
        """Compute the sensitivities of each map scan for the intensity stokes state only."""
        with self.apm_processing_step(f"Calculating sensitivity for intensity only"):
            quality_data = self.calculate_sensitivity_for_stokes_state(stokes_state="I")
        with self.apm_writing_step("Writing sensitivity data for intensity only"):
            self.quality_store_sensitivity(
                stokes="I", datetimes=quality_data.datetimes, values=quality_data.values
            )

    def compute_full_stokes_noise(self):
        """Compute noise in data broken down by each stokes state."""
        for stokes in self.constants.stokes_params:
            with self.apm_processing_step(f"Compile noise values for {stokes=}"):
                noise_data = self.compile_noise_data(stokes=stokes)
            with self.apm_writing_step(f"Write noise values for {stokes=}"):
                self.quality_store_noise(
                    datetimes=noise_data.datetimes, values=noise_data.values, stokes=stokes
                )

    def compute_intensity_only_noise(self):
        """Compute noise in data for the intensity stokes state only."""
        stokes = "I"
        with self.apm_processing_step(f"Compile noise values for {stokes=}"):
            noise_data = self.compile_noise_data(stokes=stokes)
        with self.apm_writing_step(f"Write noise values for {stokes=}"):
            self.quality_store_noise(
                datetimes=noise_data.datetimes, values=noise_data.values, stokes=stokes
            )

    def calculate_sensitivity_for_stokes_state(self, stokes_state: str) -> _QualityData:
        """Calculate the sensitivities of each map scan for a given stokes state."""
        stokes_sensitivities = _QualityData()
        for map_scan in range(1, self.constants.num_map_scans + 1):
            map_scan_sensitivity_data_point = self.calculate_sensitivity_for_map_scan(
                map_scan=map_scan,
                meas_num=1,
                stokes_state=stokes_state,
            )
            stokes_sensitivities.data_points.append(map_scan_sensitivity_data_point)
        logger.info(
            f"Calculated {len(stokes_sensitivities)} stokes state sensitivities for {stokes_state=}"
        )
        return stokes_sensitivities

    def calculate_sensitivity_for_map_scan(
        self, map_scan: int, meas_num: int, stokes_state: str
    ) -> _QualityDataPoint:
        """Calculate the sensitivity as the standard deviation of a frame divided by median intensity frame averaged over the scan steps for a single map scan."""
        scan_step_sensitivities = self.calculate_sensitivities_per_scan_step(
            map_scan=map_scan, meas_num=meas_num, stokes_state=stokes_state
        )
        map_scan_sensitivity = np.mean(scan_step_sensitivities.values)
        map_scan_average_date = Time(np.mean(scan_step_sensitivities.datetimes), format="mjd").isot
        result = _QualityDataPoint(value=map_scan_sensitivity, datetime=map_scan_average_date)
        logger.info(
            f"Calculated map scan sensitivity for {map_scan=}, {meas_num=}, {stokes_state=}"
            f" as {result} "
        )
        return result

    def calculate_sensitivities_per_scan_step(
        self, map_scan: int, meas_num: int, stokes_state: str
    ) -> _QualityData:
        """Calculate the sensitivities for each scan step in a map scan."""
        scan_step_sensitivities = _QualityData()
        for step in range(1, self.constants.num_scan_steps + 1):
            avg_stokes_i_data_point = self.get_intensity_frame_average(
                map_scan=map_scan, step=step, meas_num=1
            )
            frame = next(
                self.read(
                    tags=[
                        CryonirspTag.calibrated(),
                        CryonirspTag.frame(),
                        CryonirspTag.scan_step(step),
                        CryonirspTag.map_scan(map_scan),
                        CryonirspTag.stokes(stokes_state),
                        CryonirspTag.meas_num(meas_num),
                    ],
                    decoder=cryo_fits_access_decoder,
                    fits_access_class=L1QualityFitsAccess,
                )
            )
            scan_step_sensitivity = np.nanstd(frame.data) / avg_stokes_i_data_point.value
            scan_step_sensitivity_data_point = _QualityDataPoint(
                value=scan_step_sensitivity, datetime=avg_stokes_i_data_point.datetime
            )
            scan_step_sensitivities.data_points.append(scan_step_sensitivity_data_point)
        logger.info(
            f"Calculated {len(scan_step_sensitivities)} scan step sensitivities for {map_scan=}, "
            f"{meas_num=}, and {stokes_state=}"
        )
        return scan_step_sensitivities

    def get_intensity_frame_average(
        self, map_scan: int, step: int, meas_num: int
    ) -> _QualityDataPoint:
        """Calculate the average of an intensity frame."""
        frame: L1QualityFitsAccess = next(
            self.read(
                tags=[
                    CryonirspTag.calibrated(),
                    CryonirspTag.frame(),
                    CryonirspTag.scan_step(step),
                    CryonirspTag.map_scan(map_scan),
                    CryonirspTag.stokes("I"),
                    CryonirspTag.meas_num(meas_num),
                ],
                decoder=cryo_fits_access_decoder,
                fits_access_class=L1QualityFitsAccess,
            )
        )
        median = np.nanmedian(frame.data)
        time_obs_mjd = Time(frame.time_obs).mjd
        mean = np.nanmean(frame.data)
        average = median or mean
        result = _QualityDataPoint(value=average, datetime=time_obs_mjd)
        logger.info(f"Calculated intensity frame average as {result}")
        return result

    def compile_noise_data(self, stokes: str) -> _QualityData:
        """Compile lists of noise values and their observation times."""
        tags = [CryonirspTag.calibrated(), CryonirspTag.frame(), CryonirspTag.stokes(stokes)]
        frames: Generator[L1QualityFitsAccess, None, None] = self.read(
            tags=tags,
            decoder=cryo_fits_access_decoder,
            fits_access_class=L1QualityFitsAccess,
        )
        result = _QualityData()
        logger.info(f"Compiling noise data for {tags = }")
        for frame in frames:
            data_point = _QualityDataPoint(
                value=self.avg_noise(frame.data), datetime=frame.time_obs
            )
            result.data_points.append(data_point)
        return result
