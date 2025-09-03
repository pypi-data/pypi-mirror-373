# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""SMX pipeline subclass."""

import logging
from uuid import UUID

import numpy as np
import tango

from lima2.client import utils
from lima2.client.devencoded import (
    dense_frame,
    structured_array,
)
from lima2.client.pipeline import FrameSource, FrameType, Pipeline
from lima2.client.topology import TopologyKind

# Create a logger
logger = logging.getLogger(__name__)


class Smx(Pipeline):
    tango_class = "LimaProcessingSmx"

    FRAME_SOURCES = {
        "frame": FrameSource(
            getter_name="getFrame",
            frame_type=FrameType.DENSE,
            saving_channel="saving_dense",
            label="input",
            saving_counter_name="dense_saved",
        ),
        "sparse_frame": FrameSource(
            getter_name="getSparseFrame",
            frame_type=FrameType.SMX_SPARSE,
            saving_channel="saving_sparse",
            label="sparse",
            saving_counter_name=None,
        ),
        "acc_corrected": FrameSource(
            getter_name="getAccCorrected",
            frame_type=FrameType.DENSE,
            saving_channel="saving_accumulation_corrected",
            label=None,
            saving_counter_name=None,
        ),
        "acc_peaks": FrameSource(
            getter_name="getAccPeaks",
            frame_type=FrameType.DENSE,
            saving_channel="saving_accumulation_peak",
            label=None,
            saving_counter_name=None,
        ),
    }
    """Available frame sources."""

    @staticmethod
    def distribute_acq(
        cls,
        ctl_params: dict,
        acq_params: list[dict],
        proc_params: list[dict],
        topology_kind: TopologyKind,
    ) -> tuple[dict, list[dict], list[dict]]:
        """Initialize pipeline-specific parameters for distributed acquisition"""
        ctl_params, acq_params, proc_params = Pipeline.distribute_acq(
            cls, ctl_params, acq_params, proc_params, topology_kind
        )

        num_receivers = len(proc_params)

        def correct_acc_frames(proc, param):
            fai = proc["fai"]
            nb_frames = fai[param]
            if nb_frames % num_receivers != 0:
                raise ValueError(
                    f"FAI {param}={nb_frames} is not multiple of {num_receivers=}"
                )
            fai[param] //= num_receivers

        for i, proc in enumerate(proc_params):
            # Correct FAI accumulation parameters
            correct_acc_frames(proc, "acc_nb_frames_reset")
            correct_acc_frames(proc, "acc_nb_frames_xfer")

        return ctl_params, acq_params, proc_params

    def __init__(
        self,
        uuid: UUID,
        proc_devs: list[tango.DeviceProxy],
        topology_kind: TopologyKind,
        timeout: int,
    ):
        super().__init__(
            uuid=uuid, proc_devs=proc_devs, topology_kind=topology_kind, timeout=timeout
        )

    @property
    def radius1d(self):
        """Returns the radius1d"""
        return [dense_frame.decode(dev.radius1d).data for dev in self._devs]

    @property
    def radius2d_mask(self):
        """Returns the radius2d_mask as np.array"""
        return [dense_frame.decode(dev.radius2d_mask).data for dev in self._devs]

    def pop_peak_counters(self) -> tuple[np.ndarray, np.ndarray] | None:
        """Pop peak counters from the server, return them ordered by frame index.

        Returns:
            A tuple (frame_indices, peak_counts) for each frame available from the server
            at the time of calling, where:
            - frame_indices is a ndarray of frame indices for each peak_count
            - peak_counts is a ndarray (of the same size) of the number of peaks on a frame
        """
        dtype = [
            ("frame_idx", "i4"),
            ("recv_idx", "i4"),
            ("nb_peaks", "i4"),
        ]

        # Use cached data from previous call
        last_idx, cache = self.get_cached_byproduct(
            "peak_counters", default=(-1, np.array([], dtype=dtype))
        )

        # Pop counters for new frames from each receiver and concatenate, mixing in cached data.
        # Data comes from server as 1D array with size (num_frames)
        new_data = np.concatenate(
            [cache.flatten()]
            + [
                structured_array.decode(dev.popPeakCounters(), dtype)
                for dev in self._devs
            ]
        )

        num_frames = new_data.shape[0]
        if num_frames == 0:
            return None

        logger.debug(f"Received peak counters for {num_frames} frames")

        frame_indices = new_data["frame_idx"]
        frame_order = np.argsort(frame_indices)
        last_idx, first_gap = utils.find_first_gap(last_idx, frame_indices[frame_order])

        # Sort data by frame order
        data = new_data[frame_order]

        # Cache any data after the first frame gap for later
        self.cache_byproduct("peak_counters", (last_idx, data[first_gap:]))

        # If did not receive the expected frame return empty dataset
        if first_gap == 0:
            return None

        # Now our data is contiguous
        data = data[:first_gap]

        logger.debug(f"Returning peak counters for frames: {data['frame_idx']}")

        return (data["frame_idx"], data["nb_peaks"])

    @property
    def channels(self):
        """Return the channel descriptions"""
        return {
            "frame": self.input_frame_info[0],
            "sparse_frame": self.processed_frame_info[0],
            "acc_corrected": self.processed_frame_info[0],
            "acc_peaks": self.processed_frame_info[0],
        }
