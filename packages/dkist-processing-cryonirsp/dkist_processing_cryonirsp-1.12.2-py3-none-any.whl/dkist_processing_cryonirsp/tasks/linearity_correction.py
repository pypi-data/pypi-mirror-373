"""CryoNIRSP Linearity Correction Task."""

from dataclasses import dataclass
from typing import Generator

import numpy as np
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_service_configuration.logging import logger
from numba import njit
from numba import prange

from dkist_processing_cryonirsp.codecs.fits import cryo_fits_access_decoder
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.parsers.cryonirsp_l0_fits_access import CryonirspRampFitsAccess
from dkist_processing_cryonirsp.tasks.cryonirsp_base import CryonirspTaskBase

GB_TO_BYTES: int = 1_000_000_000

__all__ = ["LinearityCorrection"]


@dataclass
class _RampSet:
    current_ramp_set_num: int
    time_obs: str
    num_frames_in_ramp: int
    exposure_times_ms: np.ndarray
    frame_shape: tuple[int]
    last_frame_name: str
    last_frame_fits_access: CryonirspRampFitsAccess
    frames_to_process: np.ndarray
    index_offset_to_first_frame: int


class LinearityCorrection(CryonirspTaskBase):
    """Task class for performing linearity correction on all input frames, regardless of task type."""

    record_provenance = True

    def run(self):
        """
        Run method for this task.

        Steps to be performed:
        - Iterate through frames by ramp set (identified by date-obs)
        - Identify the frames in the ramp set and populate the ramp set data structure
        - Perform linearity correction on the ramp set, minimizing the memory footprint based on a maximum memory limit for the ramp set
        - Collate tags for linearity corrected frame(s)
        - Write linearity corrected frame with updated tags

        Returns
        -------
        None
        """
        num_ramp_sets = len(self.constants.time_obs_list)
        for ramp_set in self.identify_ramp_sets():
            time_obs = ramp_set.time_obs
            ramp_set_num = ramp_set.current_ramp_set_num
            logger.info(
                f"Processing frames from {time_obs}: ramp set {ramp_set_num} of {num_ramp_sets}"
            )
            output_array = self.reduce_ramp_set(
                ramp_set=ramp_set,
                mode="LookUpTable",
                camera_readout_mode=self.constants.camera_readout_mode,
                lin_curve=self.parameters.linearization_polyfit_coeffs,
                thresholds=self.parameters.linearization_thresholds,
            )
            # Normalize by the exposure time and correct for the Optical Density filter
            exposure_corrected_output_array = self.apply_exposure_corrections(
                output_array, ramp_set
            )
            # Set the tags for the linearized output frame
            tags = [
                CryonirspTag.linearized_frame(),
                CryonirspTag.time_obs(time_obs),
            ]
            # The last frame in the ramp is used for the header
            self.write(
                data=exposure_corrected_output_array,
                header=ramp_set.last_frame_fits_access.header,
                tags=tags,
                encoder=fits_array_encoder,
            )

    def identify_ramp_sets(self) -> Generator[_RampSet, None, None]:
        """
        Identify all the ramp sets present in the input data.

        Returns
        -------
        A generator of _RampSet objects

        A ramp set consists of all the non-destructive readouts (NDRs) that form a single
        exposure for the Cryonirsp cameras. All the frames from a single ramp must be processed
        together. A ramp is identified as all the files having the same DATE-OBS value. Although
        a ramp number header key exists, this value is not a unique identifier for a ramp set when
        frames from multiple subtasks are combined into an input dataset in  a single scratch dir.

        If a ramp set contains only a single frame, it is discarded with a log note.

        Returns
        -------
        Generator which yields _RampSet instances
        """
        for ramp_set_num, time_obs in enumerate(self.constants.time_obs_list):
            input_objects = list(
                self.read(
                    tags=[
                        CryonirspTag.input(),
                        CryonirspTag.frame(),
                        CryonirspTag.time_obs(time_obs),
                    ],
                    decoder=cryo_fits_access_decoder,
                    fits_access_class=CryonirspRampFitsAccess,
                )
            )

            if not self.is_ramp_valid(input_objects):
                continue

            ramp_set = self.populate_ramp_set(time_obs, ramp_set_num)
            yield ramp_set

    def is_ramp_valid(self, ramp_object_list: list[CryonirspRampFitsAccess]) -> bool:
        """
        Check if a given ramp is valid.

        Current validity checks are:

          1. All frames in the ramp have the same value for NUM_FRAMES_IN_RAMP
          2. The value of NUM_FRAMES_IN_RAMP equals the length of actual frames found

        If a ramp is not valid then warnings are logged and `False` is returned.
        """
        frames_in_ramp_set = {o.num_frames_in_ramp for o in ramp_object_list}
        task_type = ramp_object_list[0].ip_task_type

        if len(frames_in_ramp_set) > 1:
            logger.info(
                f"Not all frames have the same FRAMES_IN_RAMP value. Set is {frames_in_ramp_set}. Ramp is task {task_type}. Skipping ramp."
            )
            return False

        num_frames_in_ramp = frames_in_ramp_set.pop()
        num_ramp_objects = len(ramp_object_list)
        if num_ramp_objects != num_frames_in_ramp:
            logger.info(
                f"Missing some ramp frames. Expected {num_frames_in_ramp} from header value, but only have {num_ramp_objects}. Ramp is task {task_type}. Skipping ramp."
            )
            return False

        return True

    @staticmethod
    def tag_list_for_single_ramp_frame(time_obs: str, frame_num: int) -> list[CryonirspTag]:
        """Return the tag list required to identify a single ramp frame."""
        tags = [
            CryonirspTag.input(),
            CryonirspTag.frame(),
            CryonirspTag.time_obs(time_obs),
            CryonirspTag.curr_frame_in_ramp(frame_num),
        ]
        return tags

    def read_single_ramp_frame(self, time_obs: str, frame_num: int) -> CryonirspRampFitsAccess:
        """
        Read a single file from a single ramp set based on the observe time and frame number.

        Parameters
        ----------
        time_obs
            The DATE-OBS header value identifying the desired ramp set
        frame_num
            The frame number on the ramp to be accessed. This number is 1-based and is used to
            generate the curr frame in ramp tag that identifies the desired frame

        Returns
        -------
        A CryonirspRampFitsAccess object containing the desired frame

        """
        tags = self.tag_list_for_single_ramp_frame(time_obs, frame_num)
        fits_obj_list = list(
            self.read(
                tags=tags,
                decoder=cryo_fits_access_decoder,
                fits_access_class=CryonirspRampFitsAccess,
            )
        )
        if len(fits_obj_list) != 1:
            raise RuntimeError(f"Multiple files or no files for {tags =}")
        fits_obj = fits_obj_list[0]
        return fits_obj

    def get_ordered_exposure_time_list(self, time_obs: str, num_frames_in_ramp: int) -> np.ndarray:
        """
        Return a list of exposure times for this ramp, ordered by frame in ramp.

        Parameters
        ----------
        time_obs
            The DATE-OBS value identifying the ramp
        num_frames_in_ramp
            The number of frames in the ramp

        Returns
        -------
        np.ndarray of the exposure times for the NDRs in the ramp set.

        This method iterates through all the frames in the ramp to construct the list. While this could
        be incorporated into other methods that iterate through a ramp set, it is kept separate for clarity.
        We read one frame at a time to not have all the frames in memory simultaneously.
        """
        exp_time_list = []
        for frame_num in range(1, num_frames_in_ramp + 1):
            fits_obj = self.read_single_ramp_frame(time_obs, frame_num)
            exp_time_list.append(fits_obj.fpa_exposure_time_ms)
        return np.array(exp_time_list, dtype=np.float32)

    def populate_ramp_set(self, time_obs: str, idx: int) -> _RampSet | None:
        """
        Populate a _RampSet dataclass for the ramp identified by time_obs.

        Parameters
        ----------
        time_obs
            The DATE-OBS value identifying the ramp
        idx
            The index number representing this ramp set out of the total number of ramp sets (zero-based)

        Returns
        -------
        A populated _RampSet object representing the specified ramp in the input data set

        The last frame in the set is read to access the shape of the data frame.
        """
        actual_num_frames_in_ramp = self.count(CryonirspTag.time_obs(time_obs))
        exp_times = self.get_ordered_exposure_time_list(time_obs, actual_num_frames_in_ramp)
        last_frame = self.read_single_ramp_frame(time_obs, actual_num_frames_in_ramp)
        ramp_set_num = idx + 1
        # The default list of curr_frame_in_ramp tag numbers to use, which may be altered later on
        frames_to_process = np.array(range(1, actual_num_frames_in_ramp + 1), dtype=int)
        ramp_set = _RampSet(
            current_ramp_set_num=ramp_set_num,
            time_obs=time_obs,
            num_frames_in_ramp=actual_num_frames_in_ramp,
            exposure_times_ms=exp_times,
            frame_shape=last_frame.data.shape,
            last_frame_name=last_frame.name,
            last_frame_fits_access=CryonirspRampFitsAccess.from_header(last_frame.header),
            frames_to_process=frames_to_process,
            # initial offset from zero-based array index to 1-based frame in ramp number
            index_offset_to_first_frame=1,
        )
        return ramp_set

    def apply_exposure_corrections(self, input_array: np.ndarray, ramp_set: _RampSet) -> np.ndarray:
        """
        Normalize the array by converting to counts per second and correcting for Optical Density filter attenuation.

        Parameters
        ----------
        input_array
            The linearized array top be normalized
        ramp_set
            The _RampSet object associated with the linearized array

        Returns
        -------
            The normalized output array

        """
        # Normalize the array by the final ramp exposure time converted to seconds
        # This makes the output units counts per sec
        exposure_normalized_array = input_array / (ramp_set.exposure_times_ms[-1] / 1000.0)
        # Correct the counts for the Optical Density filter used
        log_od_filter_attenuation = self.parameters.linearization_filter_attenuation_dict[
            ramp_set.last_frame_fits_access.filter_name
        ]
        od_filter_attenuation = 10**log_od_filter_attenuation
        return exposure_normalized_array / od_filter_attenuation

    def reduce_ramp_set(
        self,
        ramp_set: _RampSet,
        mode: str = None,
        camera_readout_mode: str = None,
        lin_curve: np.ndarray = None,
        thresholds: np.ndarray = None,
    ) -> np.ndarray:
        """
        Process a single ramp from a set of input frames.

        Parameters
        ----------
        ramp_set
            The _RampSet data structure for the current ramp

        mode
            'LookUpTable','FastCDS','FitUpTheRamp' (ignored if data is line by line)

        camera_readout_mode
            ‘FastUpTheRamp, ‘SlowUpTheRamp’, or 'LineByLine’

        lin_curve
            The lincurve array is the set of coefficients for a 3rd order polynomial which represents the overall
            non-linear response of the detector pixels to exposure time. The cubic is evaluated for each measured
            pixel value and then used to correct the measured pixel value by dividing out the non-linear
            response.

        thresholds
            The threshold array represents the flux value for each pixel above which the measured flux is
            inaccurate and starts to decrease with increasing exposure time. This is used in the linearization
            algorithm to mask off values in a ramp that exceed the threshold and use only the values below
            the threshold to estimate the linear flux per non-destructive readout.

        Returns
        -------
        processed array
        """
        # NB: The threshold table is originally constructed for the full sensor size (2k x 2k)
        # Extract the portion of the thresholds that corresponds to the ROI used in the camera.
        roi_1_origin_x = self.constants.roi_1_origin_x
        roi_1_origin_y = self.constants.roi_1_origin_y
        roi_1_size_x = self.constants.roi_1_size_x
        roi_1_size_y = self.constants.roi_1_size_y
        thresh_roi = thresholds[
            roi_1_origin_y : (roi_1_origin_y + roi_1_size_y),
            roi_1_origin_x : (roi_1_origin_x + roi_1_size_x),
        ]

        if mode == "LookUpTable" and camera_readout_mode == "FastUpTheRamp":
            return self.reduce_ramp_set_for_lookup_table_and_fast_up_the_ramp(
                ramp_set=ramp_set,
                lin_curve=lin_curve,
                thresholds=thresh_roi,
            )
        raise ValueError(
            f"Linearization mode {mode} and camera readout mode {camera_readout_mode} is currently not supported."
        )

    def reduce_ramp_set_for_lookup_table_and_fast_up_the_ramp(
        self,
        ramp_set: _RampSet,
        lin_curve: np.ndarray,
        thresholds: np.ndarray,
    ) -> np.ndarray:
        """Process a single ramp from a set of input frames whose mode is 'LookUpTable' and camera readout mode is 'FastUpTheRamp'."""
        # In this mode we toss the first frame in the ramp
        ramp_set.num_frames_in_ramp -= 1
        ramp_set.frames_to_process = ramp_set.frames_to_process[1:]
        ramp_set.exposure_times_ms = ramp_set.exposure_times_ms[1:]
        ramp_set.index_offset_to_first_frame += 1
        processed_frame = self.linearize_fast_up_the_ramp_with_lookup_table(
            ramp_set=ramp_set,
            lin_curve=lin_curve,
            thresholds=thresholds,
        )
        return processed_frame

    def linearize_fast_up_the_ramp_with_lookup_table(
        self,
        ramp_set: _RampSet,
        lin_curve: np.ndarray,
        thresholds: np.ndarray,
    ) -> np.ndarray:
        """
        Perform linearization on a set of ramp frames.

        Parameters
        ----------
        ramp_set
            The _RampSet object for the ramp set to be linearized
        lin_curve
            The linearity coefficient array used in the algorithm
        thresholds
            The threshold array used in the algorithm

        Returns
        -------
        The linearized array for this ramp set

        The algorithm proceeds as follows:
            1. The number of chunks required to process the full ramp chunk_stack is computed
            2. Iterate over the number of chunks and do the following:
                a. Compute the size of the current chunk (the last chunk may be smaller than the others)
                b. Compute the slice object representing the portion of the frames to be extracted into the chunk
                c. Load the frame slices into the chunk chunk_stack
                d. Linearize the chunk chunk_stack
                e. Store the linearized chunk in the proper location in the final linearized array
            3. Return the linearized ramp, reshaping it to the original frame shape
        """
        thresholds_flattened = thresholds.flatten()
        frame_shape = ramp_set.frame_shape
        linearized_frame = np.zeros(np.prod(frame_shape), dtype=np.float32)
        num_frame_size_elements = int(np.prod(frame_shape))
        chunk_size_nelem = self.compute_linear_chunk_size(
            num_frame_size_elements, ramp_set.num_frames_in_ramp
        )
        # num_chunks = num full chunks + a single partial chunk, if needed
        num_chunks = num_frame_size_elements // chunk_size_nelem + int(
            (num_frame_size_elements % chunk_size_nelem) > 0
        )
        logger.info(
            f"{num_chunks = }, {chunk_size_nelem = }, in bytes = {chunk_size_nelem * ramp_set.num_frames_in_ramp * np.dtype(np.float32).itemsize}"
        )

        # Iterate over all the chunks
        elements_remaining = int(num_frame_size_elements)
        offset = 0
        for chunk in range(1, num_chunks + 1):
            logger.info(f"Processing chunk {chunk} of {num_chunks}")
            current_chunk_size_nelem = min(chunk_size_nelem, elements_remaining)
            current_slice = slice(offset, offset + current_chunk_size_nelem)
            chunk_stack = self.load_chunk_stack(
                ramp_set, current_chunk_size_nelem, ramp_set.num_frames_in_ramp, current_slice
            )
            linearized_frame[current_slice] = self.linearize_chunk(
                chunk_stack,
                lin_curve,
                thresholds_flattened[current_slice],
                ramp_set.exposure_times_ms,
            )
            offset += chunk_size_nelem
            elements_remaining -= chunk_size_nelem

        return linearized_frame.reshape(frame_shape)

    def load_chunk_stack(
        self,
        ramp_set: _RampSet,
        current_chunk_size: int,
        trimmed_frames_in_ramp: int,
        current_slice: slice,
    ) -> np.ndarray:
        """
        Load a chunk's worth of the ramp chunk_stack into an array and return it.

        Parameters
        ----------
        ramp_set
            The ramp_set from which to load the chunk chunk_stack
        current_chunk_size
            The size in linear elements of the chunk chunk_stack (the number of pixel stacks in the chunk)
        trimmed_frames_in_ramp
            The final number of frames in the ramp set
        current_slice
            The slice of the frames to load into the chunk_stack

        Returns
        -------
        The chunk chunk_stack for the specified ramp set and slice

        Notes
        -----
        The files are read one at a time to minimize memory use. The frame_num loop variable is used
        to identify the desired frame to read. It is one-based and is used to generate the curr_frame_in_ramp
        tag. We tossed the first frame of the ramp, so we must start with 2. Conversely, the offset into the
        array is zero-based and is 2 less than the frame number.
        """
        chunk_stack = np.zeros((current_chunk_size, trimmed_frames_in_ramp), np.float32)
        for frame_num in ramp_set.frames_to_process:
            frame = self.read_single_ramp_frame(ramp_set.time_obs, frame_num).data
            frame_pos_in_stack = frame_num - ramp_set.index_offset_to_first_frame
            chunk_stack[:current_chunk_size, frame_pos_in_stack] = frame.flatten()[current_slice]
        return chunk_stack

    def compute_linear_chunk_size(self, frame_size_nelem: int, num_frames_in_ramp: int) -> int:
        """
        Compute the number of pixel stacks that constitute a 'chunk'.

        Parameters
        ----------
        frame_size_nelem
            The size of a data frame expressed as the total number of elements
        num_frames_in_ramp
            The number of frames in a ramp set. If any frames are to be tossed initially,
            this number represents the final frame count after any discards.

        Returns
        -------
        The number of pixel stacks in a chunk

        A chunk is the largest linear stack of frame pixels that can be handled by the linearization
        algorithm in one calculation without exceeding the task worker memory limitations. The algorithm
        must hold essentially twice the size of the linear stack in memory. We assume we can safely
        use 80% of the available memory for this processing.

        The variables listed below are either in number of bytes or number of elements,
        as indicated by their suffixes
        """
        ramp_size_in_bytes = frame_size_nelem * np.dtype(np.float32).itemsize * num_frames_in_ramp
        available_memory_in_gb = self.parameters.linearization_max_memory_gb
        max_chunk_size_in_bytes = round(0.8 * available_memory_in_gb * GB_TO_BYTES // 2)
        chunk_size_nelem = round(
            min(max_chunk_size_in_bytes, ramp_size_in_bytes)
            // np.dtype(np.float32).itemsize
            // num_frames_in_ramp
        )
        return chunk_size_nelem

    def linearize_chunk(
        self, chunk_stack: np.ndarray, linc: np.ndarray, thresh: np.ndarray, exptimes: np.ndarray
    ) -> np.ndarray:
        """
        Linearize a portion (chunk) of the entire ramp stack.

        Parameters
        ----------
        chunk_stack
            The portion (chunk) of the overall ramp stack to be linearized
        linc
            The linearity coefficient array used in the algorithm
        thresh
            The threshold array used ion the algorithm
        exptimes
            The list of exposure times for the frames in the stack

        Returns
        -------
        An array containing a linearized slice of the full ramp stack

        """
        raw_data = self.lin_correct(chunk_stack, linc)
        slopes = self.get_slopes(exptimes, raw_data, thresh)
        # Scale the slopes by the exposure time to convert to counts
        processed_frame = slopes * np.nanmax(exptimes)
        return processed_frame

    # The methods below are derived versions of the same codes in Tom Schad's h2rg.py
    @staticmethod
    @njit(parallel=False)
    def lin_correct(raw_data: np.ndarray, linc: np.ndarray) -> np.ndarray:
        """
        Correct the measured raw fluence to normalized flux per non-destructive readout (NDR).

        Uses a 3rd order polynomial based on measured lamp calibration data to remove the non-linear
        response of each pixel in the array. The resulting ramp is essentially linear in ADUs vs exposure time.
        """
        return raw_data / (
            linc[0] + raw_data * (linc[1] + raw_data * (linc[2] + raw_data * linc[3]))
        )

    @staticmethod
    @njit(parallel=False)
    def get_slopes(exptimes: np.ndarray, data: np.ndarray, thresholds: np.ndarray):
        """
        Compute the weighted least squares estimate of the normalized flux per exposure time increment for a single ramp.

        The threshold array represents the flux value for each pixel above which the measured flux is
        inaccurate and starts to decrease with increasing exposure time. The threshold is used to set the weight for
        a particular non-destructive readout (NDR) to zero if the pixel value exceeds the threshold. The thresholded
        weights are then used to compute the weighted least squares estimate of the flux per NDR, which is the slope
        of the ramp.
        """
        num_pix, num_ramps = data.shape
        slopes = np.zeros(num_pix)

        for i in prange(num_pix):
            px_data = data[i, :]
            weights = np.sqrt(px_data)
            weights[px_data > thresholds[i]] = 0.0

            # If there are more than 2 NDRs that are below the threshold
            if np.sum(weights > 0) >= 2:
                weight_sum = np.sum(weights)

                exp_time_weighted_mean = np.dot(weights, exptimes) / weight_sum
                px_data_weighted_mean = np.dot(weights, px_data) / weight_sum

                corrected_exp_times = exptimes - exp_time_weighted_mean
                corrected_px_data = px_data - px_data_weighted_mean

                weighted_exp_times = weights * corrected_exp_times
                slopes[i] = np.dot(weighted_exp_times, corrected_px_data) / np.dot(
                    weighted_exp_times, corrected_exp_times
                )

        return slopes
