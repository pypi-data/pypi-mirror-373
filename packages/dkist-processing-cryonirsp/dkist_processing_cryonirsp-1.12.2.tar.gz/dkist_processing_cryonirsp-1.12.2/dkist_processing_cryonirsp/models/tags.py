"""CryoNIRSP tags."""

from enum import Enum

from dkist_processing_common.models.tags import StemName
from dkist_processing_common.models.tags import Tag

from dkist_processing_cryonirsp.models.exposure_conditions import ExposureConditions
from dkist_processing_cryonirsp.models.task_name import CryonirspTaskName


class CryonirspStemName(str, Enum):
    """Controlled list of Tag Stems."""

    linearized = "LINEARIZED"
    beam = "BEAM"
    scan_step = "SCAN_STEP"
    curr_frame_in_ramp = "CURR_FRAME_IN_RAMP"
    time_obs = "TIME_OBS"
    meas_num = "MEAS_NUM"
    map_scan = "MAP_SCAN"
    exposure_conditions = "EXPOSURE_CONDITIONS"


class CryonirspTag(Tag):
    """CryoNIRSP specific tag formatting."""

    @classmethod
    def beam(cls, beam_num: int) -> str:
        """
        Tags by beam number.

        Parameters
        ----------
        beam_num
            The beam number

        Returns
        -------
        The formatted tag string
        """
        return cls.format_tag(CryonirspStemName.beam, beam_num)

    @classmethod
    def scan_step(cls, scan_step: int) -> str:
        """
        Tags by the current scan step number.

        Parameters
        ----------
        scan_step
            The current scan step number

        Returns
        -------
        The formatted tag string
        """
        return cls.format_tag(CryonirspStemName.scan_step, scan_step)

    @classmethod
    def map_scan(cls, map_scan: int) -> str:
        """
        Tags by the current scan step number.

        Parameters
        ----------
        map_scan
            The current map_scan number

        Returns
        -------
        The formatted tag string
        """
        return cls.format_tag(CryonirspStemName.map_scan, map_scan)

    @classmethod
    def linearized(cls) -> str:
        """
        Tags for linearized frames.

        Returns
        -------
        The formatted tag string
        """
        return cls.format_tag(CryonirspStemName.linearized)

    @classmethod
    def curr_frame_in_ramp(cls, curr_frame_in_ramp: int) -> str:
        """
        Tags based on the current frame number in the ramp.

        Parameters
        ----------
        curr_frame_in_ramp
            The current frame number for this ramp

        Returns
        -------
        The formatted tag string
        """
        return cls.format_tag(CryonirspStemName.curr_frame_in_ramp, curr_frame_in_ramp)

    @classmethod
    def time_obs(cls, time_obs: str) -> str:
        """
        Tags by the observe date.

        Parameters
        ----------
        time_obs
            The observe time

        Returns
        -------
        The formatted tag string
        """
        return cls.format_tag(CryonirspStemName.time_obs, time_obs)

    @classmethod
    def meas_num(cls, meas_num: int) -> str:
        """
        Tags by the measurement number.

        Parameters
        ----------
        meas_num
            The current measurement number

        Returns
        -------
        The formatted tag string
        """
        return cls.format_tag(CryonirspStemName.meas_num, meas_num)

    @classmethod
    def exposure_conditions(cls, exposure_conditions: ExposureConditions) -> str:
        """
        Tags by the measurement number.

        Parameters
        ----------
        exposure_conditions
            A tuple of (exposure time, filter name)

        Returns
        -------
        The formatted tag string
        """
        return cls.format_tag(CryonirspStemName.exposure_conditions, exposure_conditions)

    @classmethod
    def task_beam_boundaries(cls) -> str:
        """Tags intermediate beam boundary calibration objects."""
        return cls.format_tag(StemName.task, CryonirspTaskName.beam_boundaries.value)

    @classmethod
    def task_bad_pixel_map(cls) -> str:
        """Tags intermediate bad pixel map objects."""
        return cls.format_tag(StemName.task, CryonirspTaskName.bad_pixel_map.value)

    @classmethod
    def task_spectral_fit(cls) -> str:
        """Tags spectral fit solution."""
        return cls.format_tag(StemName.task, CryonirspTaskName.spectral_fit.value)

    @classmethod
    def task_characteristic_spectra(cls) -> str:
        """Tags 1D intermediate characteristic spectra."""
        return cls.format_tag(StemName.task, CryonirspTaskName.solar_char_spec.value)

    ##################
    # COMPOSITE TAGS #
    ##################
    @classmethod
    def intermediate_frame(
        cls, beam: int | None = None, exposure_conditions: ExposureConditions | None = None
    ) -> list[str]:
        """Tag by intermediate and frame, and optionally by beam and exposure_conditions."""
        tag_list = [cls.intermediate(), cls.frame()]
        if beam is not None:
            tag_list += [cls.beam(beam)]
        if exposure_conditions is not None:
            tag_list += [cls.exposure_conditions(exposure_conditions)]
        return tag_list

    @classmethod
    def linearized_frame(
        cls, beam: int | None = None, exposure_conditions: ExposureConditions | None = None
    ) -> list[str]:
        """Tag by linearized, by frame, by beam, and optionally by exposure_conditions."""
        tag_list = [cls.linearized(), cls.frame()]
        if beam is not None:
            tag_list += [cls.beam(beam)]
        if exposure_conditions is not None:
            tag_list += [cls.exposure_conditions(exposure_conditions)]
        return tag_list

    @classmethod
    def intermediate_beam_boundaries(cls, beam: int) -> list[str]:
        """Tag list for retrieving beam boundaries."""
        tag_list = cls.intermediate_frame(beam=beam)
        tag_list += [cls.task_beam_boundaries()]
        return tag_list
