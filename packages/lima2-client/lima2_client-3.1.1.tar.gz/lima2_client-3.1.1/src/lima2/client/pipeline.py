# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""Pipeline base class.

An instance of Pipeline represents one processing pipeline, possibly distributed across multiple
Lima2 receivers. It has knowledge of the topology, and therefore can fetch a frame given a global
frame index, and provide aggregated progress counters during/after an acquisition.
"""

import json
import logging
import traceback
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum, auto
from uuid import UUID

import numpy as np
import tango
from jsonschema_default import create_from

from lima2.client import progress_counter, utils
from lima2.client.convert import frame_info_to_shape_dtype
from lima2.client.devencoded import (
    dense_frame,
    sparse_frame,
    smx_sparse_frame,
    structured_array,
)
from lima2.client.progress_counter import ProgressCounter, SingleCounter
from lima2.client.topology import (
    RoundRobinTopology,
    SingleTopology,
    Topology,
    TopologyKind,
    UnevenTopology,
)
from lima2.client.utils import classproperty

logger = logging.getLogger(__name__)


class FrameType(Enum):
    DENSE = auto()
    SPARSE = auto()
    SMX_SPARSE = auto()


decoder_by_type: dict[FrameType, Callable] = {
    FrameType.DENSE: dense_frame.decode,
    FrameType.SPARSE: sparse_frame.decode,
    FrameType.SMX_SPARSE: smx_sparse_frame.decode_sparse_frame,
}
"""Mapping from frame type to associated decode function"""


@dataclass
class FrameSource:
    """Specifies the name of a getter and a frame type for a given frame source.

    From these two attributes, it is possible to fetch a frame from a processing tango
    device and then decode it.
    """

    getter_name: str
    """Name of the getter method to call on the tango device to fetch the data"""

    frame_type: FrameType
    """Frame type"""

    saving_channel: str | None
    """Name of the associated saving_params object in the proc_params struct.

    Can be None for sources without persistency.
    """

    label: str | None
    """Name of corresponding frame stream in the processing device: progress_counters, etc."""

    saving_counter_name: str | None = None
    """Name of corresponding saving field in the progress_counters"""


class Pipeline:
    """A base class for all processing pipelines."""

    FRAME_SOURCES: dict[str, FrameSource]
    """Map of available frame source names to a corresponding FrameSource descriptor.

    Definition in child classes is enforced by __init_subclass__().
    """

    BYPRODUCT_CACHE_LIMIT = 30 * 1000
    """Maximum number of cached entries for each processing by-product.

    This value corresponds to a number of frames, not a number of array elements.
    Cache entries are discarded only if a receiver is ahead of another by this many frames.
    """

    tango_class: str
    """Class name as defined on server side.

    Definition in child classes is enforced by __init_subclass__().
    """

    ####################################################################################
    # Class properties
    ####################################################################################

    @classproperty
    def params_schema(cls) -> dict:
        """Processing parameters schema. Retrieved from the tango db on first access."""
        schema = getattr(cls, "_params_schema", None)
        if schema is None:
            schema = cls.fetch_params_schema()
            setattr(cls, "_params_schema", schema)
        return schema

    @classproperty
    def params_default(cls) -> dict:
        """Default processing param dict."""
        proc_params: dict = create_from(cls.params_schema)
        return proc_params

    ####################################################################################
    # Class methods
    ####################################################################################

    @classmethod
    def fetch_params_schema(cls) -> dict:
        """Fetch proc_params schema from the server."""
        try:
            tango_db = tango.Database()
        except tango.DevFailed as e:
            raise ValueError("Unable to open tango database from TANGO_HOST.\n") from e

        prop = tango_db.get_class_attribute_property(cls.tango_class, "proc_params")
        # Each attribute property is a StdStringVector with a single value
        try:
            schema_json = prop["proc_params"]["schema"][0]
        except KeyError as e:
            raise ValueError(
                f"Schema for 'proc_params' not found for processing class '{cls.tango_class}'"
            ) from e

        schema: dict = json.loads(schema_json)
        return schema

    @staticmethod
    def distribute_acq(
        cls,
        ctl_params: dict,
        acq_params: list[dict],
        proc_params: list[dict],
        topology_kind: TopologyKind,
    ) -> tuple[dict, list[dict], list[dict]]:
        """Initialize pipeline-specific parameters for distributed acquisition
        It is implemented as static method so base classes can access to the
        derived class implemtation
        """
        for i, proc in enumerate(proc_params):
            # Assign unique filename rank per receiver
            for source in cls.FRAME_SOURCES.values():
                if source.saving_channel is not None:
                    proc[source.saving_channel]["filename_rank"] = i

        return ctl_params, acq_params, proc_params

    @classmethod
    def __init_subclass__(cls) -> None:
        """Initialize a pipeline subclass."""
        if not hasattr(cls, "FRAME_SOURCES"):
            raise ValueError(
                f"Pipeline subclass {cls} must define a FRAME_SOURCES class member"
            )

        if not hasattr(cls, "tango_class"):
            raise ValueError(
                f"Pipeline subclass {cls} must define a tango_class class member"
            )

    def __init__(
        self,
        uuid: UUID,
        proc_devs: list[tango.DeviceProxy],
        topology_kind: TopologyKind,
        timeout: int,
    ):
        """Construct a Pipeline object.

        Args:
            uuid: Unique identifer of the acquisition
            proc_devs: Variable length processing device instances
            topology_kind: Receiver topology
        """
        # Preconditions
        if not proc_devs:
            raise ValueError("Must provide at least one processing")

        self.__uuid = uuid
        self._devs = proc_devs
        self.topology: Topology

        self.byproduct_cache: dict[str, tuple[int, np.ndarray]] = {}
        """Local cache of processing byproducts.

        Used in pop_roi_statistics() and pop_roi_profiles() to return
        contiguous byproducts despite differences in receivers' processing
        speed.
        """

        self.event_info: dict[
            str, tuple[list[Callable], dict[tango.DeviceProxy, int]]
        ] = {}
        """Dictionary holding the Tango event IDs per attribute, per receiver & the callbacks"""

        if topology_kind == TopologyKind.SINGLE:
            self.topology = SingleTopology()

        elif topology_kind == TopologyKind.ROUND_ROBIN:
            # TODO(mdu) In strict round robin, obtain the actual ordering / first receiver index
            rcv_ordering = list(range(len(proc_devs)))

            self.topology = RoundRobinTopology(
                num_receivers=len(proc_devs), ordering=rcv_ordering
            )

        elif topology_kind == TopologyKind.UNEVEN:
            self.topology = UnevenTopology(num_receivers=len(proc_devs))

        else:
            raise NotImplementedError()

        for d in self._devs:
            d.set_green_mode(tango.GreenMode.Gevent)
            d.set_timeout_millis(timeout * 1000)

    @property
    def uuid(self):
        """Return the UUID of the pipeline"""
        return self.__uuid

    @property
    def input_frame_info(self):
        """Return the dtype and shape of the input frame for each receivers"""
        return [
            frame_info_to_shape_dtype(json.loads(dev.input_frame_info))
            for dev in self._devs
        ]

    @property
    def processed_frame_info(self):
        """Return the dtype and shape of the processed frame for each receivers"""
        return [
            frame_info_to_shape_dtype(json.loads(dev.processed_frame_info))
            for dev in self._devs
        ]

    def get_frame(self, frame_idx: int, source: str = "frame"):
        """Get and decode frame by index given source specifier.

        Raises:
          - ValueError: if the source is invalid.
          - RuntimeError: if the latest frame is requested but no receiver has any frames.
          - RuntimeError: if fetching the frame raises a DevFailed exception.

        """
        try:
            frame_source = self.FRAME_SOURCES[source]
        except KeyError:
            raise ValueError(
                f"Invalid source name {source}. "
                f"Available ones are: {list(self.FRAME_SOURCES.keys())}"
            )

        try:
            decode = decoder_by_type[frame_source.frame_type]
        except KeyError as e:
            raise NotImplementedError(
                f"Frame type {frame_source.frame_type} decoder missing"
            ) from e

        num_rcvs = len(self._devs)

        if num_rcvs == 1 or frame_idx >= 0:
            # In single-receiver topology or multi-receiver with a valid index
            # just pass the request to the topology layer
            effective_frame_idx = frame_idx
        else:
            # If asked for the last frame in multi-receiver, try to get its index
            effective_frame_idx = self.get_last_frame_idx(source=frame_source)
            if effective_frame_idx < 0:
                raise RuntimeError(
                    f"Cannot get the latest <{source}> frame: no frames available from any receiver"
                )

        logger.debug(f"Getting <{source}> frame: {effective_frame_idx}")

        getters = [getattr(dev, frame_source.getter_name) for dev in self._devs]

        # We should get a valid frame idx for multi-receiver
        try:
            frame = self.topology.lookup(frame_idx=effective_frame_idx, getters=getters)
        except tango.DevFailed:
            raise RuntimeError(f"Unable to get frame '{source}' {effective_frame_idx}")
        return decode(frame)

    def cache_byproduct(self, key: str, idx_data: tuple[int, np.ndarray]) -> None:
        """Store `(last_idx, data)` into `self.byproduct_cache[key]`.

        Assumes `data` is a structured array with a "frame_idx" column.

        If `data` exceeds BYPRODUCT_CACHE_LIMIT (in number of frames),
        entries corresponding to the excess frames will be discarded
        (starting from the oldest data).
        """
        last_idx, data = idx_data
        frame_indices = np.unique(data["frame_idx"])
        num_frames = frame_indices.size
        excess_frames = num_frames - self.BYPRODUCT_CACHE_LIMIT
        if excess_frames > 0:
            logger.warning(
                f"BYPRODUCT_CACHE_LIMIT ({self.BYPRODUCT_CACHE_LIMIT}) exceeded "
                f"for '{key}': data discarded for {excess_frames} frames."
            )
            # Filter out data whose frame_idx is smaller than the last excess frame's
            data = data[data["frame_idx"] >= frame_indices[excess_frames]]

        self.byproduct_cache[key] = (last_idx, data)

    def get_cached_byproduct(
        self, key: str, default: tuple[int, np.ndarray]
    ) -> tuple[int, np.ndarray]:
        return self.byproduct_cache.get(key, default)

    @property
    def nb_roi_statistics(self) -> ProgressCounter:
        """Get the number of roi statistics fetchable by `pop_roi_statistics`."""
        return progress_counter.aggregate(
            single_counters=[
                progress_counter.SingleCounter(
                    name="nb_roi_statistics",
                    value=dev.nb_roi_statistics,
                    source=dev.name(),
                )
                for dev in self._devs
            ]
        )

    def pop_roi_statistics(self) -> list[tuple[np.ndarray, np.ndarray]] | None:
        """Fetch new roi statistics from the server, return them listed by roi index.

        Returns:
            A list, by roi index, of stats for every roi and for each frame available
            from the server at the time of calling. Each element of the list is a
            tuple (frame_indices, stats), where:
            - frame_indices is a ndarray of frame indices for each stats
            - stats is a structured ndarray of stats (min, max, avg, std, sum)
        """

        dtype = [
            ("frame_idx", "i4"),
            ("recv_idx", "i4"),
            ("min", "f4"),
            ("max", "f4"),
            ("avg", "f4"),
            ("std", "f4"),
            ("sum", "f8"),
        ]

        # Use cached data from previous call
        last_idx, cache = self.get_cached_byproduct(
            "roi_statistics", default=(-1, np.array([], dtype=dtype))
        )

        # Pop stats for new frames from each receiver and concatenate, mixing in cached data.
        # Data comes from server as 1D array with size (num_frames * num_rois)
        def pop_data(dev) -> np.ndarray:
            return structured_array.decode(dev.popRoiStatistics(), dtype)

        num_rcvs = len(self._devs)
        with ThreadPoolExecutor(max_workers=num_rcvs) as pool:
            flat_cache = [cache.flatten()]
            new_data = np.concatenate(flat_cache + list(pool.map(pop_data, self._devs)))

        # Guess number of frames from the data
        num_frames = np.unique(new_data["frame_idx"]).size
        if num_frames == 0:
            return None

        # Reshape into (num_frames, num_rois)
        new_data = new_data.reshape((num_frames, -1))
        num_rois = new_data.shape[1]

        logger.debug(f"Received roi stats for {num_frames=}, {num_rois=}")

        frame_indices = new_data["frame_idx"][:, 0]
        frame_order = np.argsort(frame_indices)
        last_idx, first_gap = utils.find_first_gap(last_idx, frame_indices[frame_order])

        # Sort data by frame order
        data = new_data[frame_order]

        # Cache any data after the first frame gap for later
        self.cache_byproduct("roi_statistics", (last_idx, data[first_gap:]))

        # If did not receive the expected frame return empty dataset
        if first_gap == 0:
            return None

        # Now our data is contiguous
        data = data[:first_gap]

        logger.debug(f"Returning roi stats for frames: {data['frame_idx'][:, 0]}")

        return [
            (data[:, i]["frame_idx"], data[:, i][["min", "max", "avg", "std", "sum"]])
            for i in range(num_rois)
        ]

    @property
    def nb_roi_profiles(self) -> ProgressCounter:
        """Get the number of roi profiles fetchable by `pop_roi_profiles()`."""
        return progress_counter.aggregate(
            single_counters=[
                progress_counter.SingleCounter(
                    name="nb_roi_profiles",
                    value=dev.nb_roi_profiles,
                    source=dev.name(),
                )
                for dev in self._devs
            ]
        )

    def pop_roi_profiles(
        self, roi_lengths: list[int]
    ) -> list[tuple[np.ndarray, np.ndarray]] | None:
        """Fetch new roi profiles from the server, return them listed by roi index.

        Args:
            roi_lengths: number of elements in each defined roi profile.

        Returns:
            A list, by roi index, of profile data for each frame available from the
            server at the time of calling. Each element of the list is a tuple
            (frame_indices, profile_elements), where:
            - frame_indices is a ndarray of frame indices for each profile
            - profile_elements is a structured ndarray of profile data
        """

        dtype = [
            ("frame_idx", "i4"),
            ("recv_idx", "i4"),
            ("min", "f4"),
            ("max", "f4"),
            ("avg", "f4"),
            ("std", "f4"),
            ("sum", "f8"),
        ]

        num_rois = len(roi_lengths)

        logger.debug(f"Fetching {num_rois} roi profiles with {roi_lengths=}")

        # Use cached data from previous call
        last_idx, cache = self.get_cached_byproduct(
            "roi_profiles", default=(-1, np.array([], dtype=dtype))
        )

        # Pop profiles for new frames from each receiver and concatenate, mixing in cached data.
        # Data comes from server as 1D array with size (num_frames * sum(roi_lengths))
        def pop_data(dev) -> np.ndarray:
            return structured_array.decode(dev.popRoiProfiles(), dtype)

        num_rcvs = len(self._devs)
        with ThreadPoolExecutor(max_workers=num_rcvs) as pool:
            flat_cache = [cache.flatten()]
            new_data = np.concatenate(flat_cache + list(pool.map(pop_data, self._devs)))

        # Reshape into (num_frames, sum(roi_lengths))
        new_data = new_data.reshape((-1, sum(roi_lengths)))
        num_frames = new_data.shape[0]
        if num_frames == 0:
            return None

        logger.debug(f"Received roi profile data for {num_frames} frames")

        frame_indices = new_data["frame_idx"][:, 0]
        frame_order = np.argsort(frame_indices)
        last_idx, first_gap = utils.find_first_gap(last_idx, frame_indices[frame_order])

        # Sort data by frame order
        data = new_data[frame_order]

        # Cache any data after the first frame gap for later
        self.cache_byproduct("roi_profiles", (last_idx, data[first_gap:]))

        # If did not receive the expected frame return empty dataset
        if first_gap == 0:
            return None

        # Now our data is contiguous
        data = data[:first_gap]

        ret_profiles: list[np.ndarray] = []

        # Cut the data into individual rois using roi_lengths
        for roi_idx in range(num_rois):
            element_offset = sum(roi_lengths[:roi_idx])

            # shape = (num_frames, roi_length)
            roi_data = data[:, element_offset : element_offset + roi_lengths[roi_idx]]

            ret_profiles.append(roi_data)

        logger.debug(f"Returning profiles for frames {data['frame_idx'][:, 0]}")

        return [
            (
                ret_profiles[i]["frame_idx"][:, 0],
                ret_profiles[i][["min", "max", "avg", "std", "sum"]],
            )
            for i in range(num_rois)
        ]

    def pop_raw_frame_idx(self, recv_idx) -> np.ndarray:
        """Pop recv_idx-2-det_idx frame mapping from one receiver

        The structured array we decode and return contains a list
        of pairs <recv_idx, det_idx> for all the frames acquired since the last call.

        Returns:
            A ndarray with <recv_idx, det_idx>
        """
        dtype = [
            ("recv_idx", "i4"),
            ("det_idx", "i4"),
        ]

        dev = self._devs[recv_idx]
        recv_frame_idx = structured_array.decode(dev.popFrameIdx(), dtype)

        logger.debug(
            f"Popped recv {recv_idx} recv_idx-2-det_idx mapping: {recv_frame_idx}"
        )

        return recv_frame_idx

    def pop_frame_idx(self) -> tuple[np.ndarray, np.ndarray] | None:
        """Pop recv_idx-2-det_idx frame mapping

        For each receiver, the structured array we receive contains a list
        of pairs <recv_frame_idx, det_frame_idx> for all the frames acquired since the last call.

        Returns:
            A tuple (frame_indices, recv_local_indices), where:
            - frame_indices is a ndarray of detector frame indices
            - recv_local_indices is a ndarray of the corresponding <recv_idx, local_idx>
        """
        new_dtype = [
            ("frame_idx", "i4"),
            ("recv_idx", "i4"),
            ("local_idx", "i4"),
        ]

        # Use cached data from previous call
        last_idx, cache = self.get_cached_byproduct(
            "frame_idx", default=(-1, np.array([], dtype=new_dtype))
        )

        # Pop mapping for new frames from each receiver and concatenate, mixing in cached data.
        # Data is popped from server as 1D array, to be converted to new_dtype
        new_data_list = []
        for recv_idx, dev in enumerate(self._devs):
            recv_data = self.pop_raw_frame_idx(recv_idx)
            new_data = np.zeros((len(recv_data),), new_dtype)
            new_data["frame_idx"] = recv_data["det_idx"]
            new_data["local_idx"] = recv_data["recv_idx"]
            new_data["recv_idx"] = int(dev.name().split("@")[-1])
            new_data_list.append(new_data)

        new_data = np.concatenate([cache] + new_data_list)

        logger.debug(
            f"Received recv_idx-2-det_idx mapping for num_frames={len(new_data_list)}"
        )

        frame_indices = new_data["frame_idx"]
        frame_order = np.argsort(frame_indices)
        last_idx, first_gap = utils.find_first_gap(last_idx, frame_indices[frame_order])

        # Sort data by frame order
        data = new_data[frame_order]

        # Cache any data after the first frame gap for later
        self.cache_byproduct("frame_idx", (last_idx, data[first_gap:]))

        # If did not receive the expected frame return empty dataset
        if first_gap == 0:
            return None

        # Now our data is contiguous
        data = data[:first_gap]

        logger.debug(f"Returning recv_idx-2-det_idx for frames: {data['frame_idx']}")

        return (data["frame_idx"], data[["recv_idx", "local_idx"]])

    @property
    def progress_counters(self) -> dict[str, ProgressCounter]:
        """Get the list of aggregated progress counters"""
        pcs_by_rcv = [json.loads(dev.progress_counters) for dev in self._devs]

        # Set of unique progress counter names
        pc_keys = set()
        for rcv_pcs in pcs_by_rcv:
            for k in rcv_pcs.keys():
                pc_keys.add(k)

        # Sanity check: all receivers have the same progress counters (assume homogeneous)
        # Perhaps not true in all future topologies
        for rcv in pcs_by_rcv:
            for key in pc_keys:
                assert key in rcv.keys()

        aggregated_pcs: dict[str, ProgressCounter] = {}
        for pc_key in pc_keys:
            single_counters = []
            for dev, pcs in zip(self._devs, pcs_by_rcv):
                single_counters.append(
                    SingleCounter(name=pc_key, value=pcs[pc_key], source=dev.name())
                )

            aggregated_pcs[pc_key] = progress_counter.aggregate(
                single_counters=single_counters
            )

        return aggregated_pcs

    def get_last_frame_idx(self, source: FrameSource) -> int:
        """Get the last available frame index from a given source.

        Raises:
            ValueError: if progress counter associated with the source is missing
        """

        if source.label is None:
            raise ValueError(
                f"Cannot guess last frame index for {source.getter_name}: "
                "no associated label"
            )

        def last_frames(rcv_idx: int) -> int:
            last_frames_str = self._devs[rcv_idx].last_frames
            return int(json.loads(last_frames_str)[f"{source.label}_idx"])

        num_rcvs = len(self._devs)
        with ThreadPoolExecutor(max_workers=num_rcvs) as pool:
            return max(pool.map(last_frames, range(num_rcvs)))

    def ping(self):
        """
        Ping all the devices of the system.

        Raises:
            tango.ConnectionFailed: if the connection failed.

        """
        for d in self._devs:
            d.ping()

    @property
    def is_finished(self):
        """A list of `is_finished` for each devices."""
        return [dev.is_finished for dev in self._devs]

    def register_on_finished(self, cbk: Callable[[], None]) -> None:
        """
        Register a callback function to be notified when all pipelines are finished.

        Arg:
            cbk: A callback called when all receivers are done
              processing frames.
        """

        self.finished_devs: set[tango.DeviceProxy] = set()
        """Set of processing devices that have finished."""

        attr_name = "is_finished"

        # Get the event information
        cb_list, event_ids = self.event_info.setdefault(attr_name, ([], {}))
        if cbk not in cb_list:
            cb_list.append(cbk)
        else:
            logger.warning(f"{attr_name}: callback {cbk} already registered")

        # Skip registration if already done
        if event_ids:
            return

        all_devs = {dev for dev in self._devs}

        def dev_finished(evt: tango.DataReadyEventData):
            if evt.err:
                self._on_tango_event_error(evt)
                return

            logger.debug(f"{evt.device.dev_name()} {attr_name} event received")

            self.finished_devs.add(evt.device)
            if self.finished_devs != all_devs:
                return

            # All done. Call registered callbacks and report any exceptions.
            for cbk in cb_list:
                try:
                    cbk()
                except Exception:
                    logger.error(
                        "Exception raised in pipeline on_finished callback:\n"
                        f"{traceback.format_exc()}"
                    )

        for dev in self._devs:
            event_ids[dev] = dev.subscribe_event(
                attr_name,
                tango.EventType.DATA_READY_EVENT,
                dev_finished,
            )

    @property
    def last_error(self):
        """A list of `last_error` for each devices."""
        return [dev.last_error for dev in self._devs]

    def register_on_error(self, cbk):
        """
        Register a callback function to be notified on pipeline error

        Arg:
            cbk: A callback `on_error(evt: Tango.Event)` called for each receivers

        Returns:
            A dict mapping the pipeline instance name with the event id
        """

        attr_name = "last_error"

        cb_list, event_ids = self.event_info.setdefault(attr_name, ([], {}))
        if cbk not in cb_list:
            cb_list.append(cbk)
        else:
            logger.warning(f"{attr_name}: callback {cbk} already registered")

        # Skip registration if already done
        if event_ids:
            return

        def dev_error(evt: tango.DataReadyEventData):
            if evt.err:
                self._on_tango_event_error(evt)
                return

            logger.debug(f"{evt.device.dev_name()} {attr_name} event received")

            for cbk in cb_list:
                try:
                    cbk(evt)
                except Exception:
                    logger.error(
                        "Exception raised in pipeline dev_error callback:\n"
                        f"{traceback.format_exc()}"
                    )

            self._unsubscribe_event(evt.device, event_ids[evt.device])

        for dev in self._devs:
            event_ids[dev] = dev.subscribe_event(
                attr_name, tango.EventType.DATA_READY_EVENT, dev_error
            )

    def _on_tango_event_error(self, evt):
        """Called when an error is reported in the Tango event layer"""

        attr_name = evt.attr_name

        # skip connection lost-related messages
        connection_lost = any(
            ["Event channel is not responding anymore" in err for err in evt.errors]
        )
        if not connection_lost:
            logger.error(
                f"Error on {evt.device.dev_name()} '{attr_name}' event:\n"
                + "\n".join([f"- {err.desc}" for err in evt.errors])
                + "\n"
            )
        # something went wrong, disconnect all events
        self.unregister_events()

    def unregister_events(self):
        active_attrs = list(self.event_info.keys())
        for attr_name in active_attrs:
            self._unsubscribe_attr_events(attr_name)

    def _unsubscribe_attr_events(self, attr_name):
        """Unsubscribe from the Tango events of a given attribute on all devices"""
        cb_list, event_ids = self.event_info.pop(attr_name, {})
        if event_ids:
            logger.debug(f"Unsubscribing {attr_name} events")
            for dev, event_id in event_ids.items():
                self._unsubscribe_event(dev, event_id)

    def _unsubscribe_event(self, dev: tango.DeviceProxy, event_id: int):
        """Unsubscribe from the Tango event"""
        logger.debug(f"Unsubscribing from {event_id} on {dev.dev_name()}")
        dev.unsubscribe_event(event_id)

    def __repr__(self) -> str:
        return "\n".join(
            [
                f"Pipeline {self.tango_class} ({self.uuid}):",
                *[f" - {counter}" for counter in self.progress_counters.values()],
            ]
        )
