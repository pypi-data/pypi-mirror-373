# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Master file generation utilities.

Calling enable_generation() on the current pipeline between prepare_acq() and
start_acq() causes the master-file generation procedure to be called when all
processing pipelines finish.
"""

import json
import logging
import os
import time
import traceback
from copy import deepcopy
from typing import NamedTuple, Optional
from enum import Enum, auto
from contextlib import ExitStack

import h5py
import numpy as np

import gevent
import gevent.event

from lima2.client.pipeline import FrameType, Pipeline
from lima2.client.topology import TopologyKind

logger = logging.getLogger(__name__)


class LUTSource(Enum):
    AUTO = auto()
    ROUND_ROBIN = auto()
    FILE_LUT = auto()
    RECV_LUT = auto()


class MasterFileTask:
    def __init__(self, task: gevent.Greenlet, end_event):
        self.task = task
        self.end_event = end_event

    def ready(self):
        return self.task.ready()

    def start(self):
        self.task.start()

    def started(self) -> bool:
        return self.task.started

    def wait(self, timeout):
        finished = gevent.wait([self.task], timeout=timeout)
        return len(finished) > 0

    def stop(self, timeout):
        self.end_event.set()
        self.task.join(timeout=timeout)
        return self.task.ready()

    def kill(self):
        self.task.kill()
        self.task.join()


def check_generation(
    ctrl_params: dict,
    recv_params: dict,
    proc_params: dict,
    topology_kind: TopologyKind,
) -> list[dict]:
    """Check the parameters to be sent to prepare to ensure master file info"""

    # group all active saving subsystems
    active_saving_params: list[dict] = []

    # first check receiver raw saving or SDK saving
    for params in [recv_params, ctrl_params]:
        if "saving" in params and params["saving"]["enabled"]:
            active_saving_params.append(params["saving"])
            break

    # then check the saving streams of the current pipeline
    for source, params in proc_params.items():
        # Skip other subsystems
        if not source.startswith("saving"):
            continue
        # Skip source if channel is disabled
        if params["enabled"]:
            active_saving_params.append(params)

    need_frame_lut = topology_kind == TopologyKind.UNEVEN

    # include detector frame_idx dataset in HDF5 files
    for saving_params in active_saving_params:
        if need_frame_lut and "include_frame_idx" in saving_params:
            saving_params["include_frame_idx"] = True

    # allow retreiving recv-det-frame-idx mapping
    if need_frame_lut and "frame_idx_enabled" in proc_params:
        logger.debug("Enabling frame_idx generation")
        proc_params["frame_idx_enabled"] = True

    return ctrl_params, recv_params, proc_params


def enable_generation(
    pipeline: Pipeline,
    num_frames: int,
    ctrl_params: dict,
    recv_params: dict,
    proc_params: dict,
    topology_kind: TopologyKind,
    rr_offset: int = 0,
    lut_source: LUTSource = LUTSource.AUTO,
) -> dict[str, MasterFileTask]:
    """Enable the generation of a master file for a given pipeline.

    Must be called between Client.prepare_acq() and Client.start_acq(), so that the
    generate_master_file() callback can be registered by the pipeline.

    The processing parameters passed to prepare_acq() are required to be able to
    retrieve data at the save path.

    Args:
        pipeline (Pipeline): current pipeline, before the call to start_acq().
        num_frames (int): total number of frames acquired
        ctrl_params (dict): controller parameters passed to prepare_acq().
        recv_params (dict): receiver parameters passed to prepare_acq().
        proc_params (dict): processing parameters passed to prepare_acq().
        rr_offset (int): expected receiver of frame 0 in the round robin frame dispatching
        lut_source: (LUTSource): requested source for recv frame index LUT generation
    """

    if rr_offset >= len(pipeline._devs):
        raise ValueError(
            f"Round robin offset cannot exceed the last receiver index ({len(pipeline._devs) - 1})."
        )

    generate_params: dict = {}
    """Params passed to generate_master_file for each enabled saving channel"""

    # event used to signal end of master_file generation
    end_event = gevent.event.Event()

    # group all active saving subsystems
    active_saving_params: list[tuple] = []

    # to be used in raw/sdk saving
    frame_info = None

    # first check the saving streams of the current pipeline
    for name, source in pipeline.FRAME_SOURCES.items():
        # Skip non-dense frame sources
        if source.frame_type != FrameType.DENSE:
            continue
        # Keep dense frame_info for raw/sdk
        frame_info = pipeline.channels[name]
        # Skip non-persistent sources
        if source.saving_channel is None:
            continue
        # Skip source if channel is disabled
        if not proc_params[source.saving_channel]["enabled"]:
            continue
        # Also skip if saving (progress) counter is not defined
        cnt_name = source.saving_counter_name
        if cnt_name is None:
            continue

        src = source.saving_channel
        active_saving_params.append((src, frame_info, proc_params[src], cnt_name))

    # also check receiver raw saving
    if "saving" in recv_params and recv_params["saving"].get("enabled", False):
        active_saving_params.append(("raw", None, recv_params["saving"], "source"))

    uuid = pipeline.uuid

    config = dict(
        uuid=str(uuid),
        ctrl_params=ctrl_params,
        recv_params=recv_params,
        proc_params=proc_params,
    )

    need_frame_lut = topology_kind == TopologyKind.UNEVEN

    # Check strict Round-Robin only when needed
    check_strict_rr = topology_kind == TopologyKind.ROUND_ROBIN

    for source, frame_info, saving_params, cnt_name in active_saving_params:
        base_path = saving_params["base_path"]
        filename_prefix = saving_params["filename_prefix"]
        file_exists_policy = saving_params["file_exists_policy"]

        master_file_path = f"{base_path}/{filename_prefix}_master.h5"
        if os.path.exists(master_file_path) and file_exists_policy != "overwrite":
            raise ValueError(
                f"Master file (channel={source}) exists at {master_file_path} "
                f"but {file_exists_policy=}. Cannot enable master file generation."
            )

        # Analyse provided LUT source with available features
        this_lut_source = None
        file_lut = saving_params.get("include_frame_idx", False)
        recv_lut = proc_params.get("frame_idx_enabled", False)
        if file_lut:
            if lut_source in [LUTSource.AUTO, LUTSource.FILE_LUT]:
                this_lut_source = LUTSource.FILE_LUT
        if recv_lut:
            if lut_source in [LUTSource.AUTO, LUTSource.RECV_LUT]:
                this_lut_source = LUTSource.RECV_LUT
        if this_lut_source is None:
            if lut_source in [LUTSource.AUTO, LUTSource.ROUND_ROBIN]:
                this_lut_source = LUTSource.ROUND_ROBIN
        if this_lut_source is None:
            raise ValueError(f"Cannot satisfy {lut_source=}: {file_lut=}, {recv_lut=}")
        elif this_lut_source == LUTSource.ROUND_ROBIN and need_frame_lut:
            raise ValueError(f"Cannot use {this_lut_source} with {topology_kind}")

        logger.info(
            f"Master file (channel={source}) will be generated "
            f"at {master_file_path} [{this_lut_source}]..."
        )

        if frame_info is not None:
            frame_shape = frame_info["shape"]
            pixel_dtype = frame_info["dtype"]
            h5_nb_dims = saving_params.get("nb_dimensions", "dim_3d_or_4d")
            is_3d_dataset = len(frame_shape) == 3 and frame_shape[0] == 1
            if h5_nb_dims == "dim_3d_or_4d" and is_3d_dataset:
                frame_shape = frame_shape[1:]
        else:
            frame_shape = None
            pixel_dtype = None

        # Store the parameters for each saving source
        generate_params[source] = dict(
            num_frames=num_frames,
            frame_shape=frame_shape,
            pixel_dtype=pixel_dtype,
            num_receivers=len(pipeline._devs),
            saving_params=deepcopy(saving_params),
            rr_offset=rr_offset,
            lut_source=this_lut_source,
            pipeline=pipeline,
            end_event=end_event,
            cnt_name=cnt_name,
            config=config,
            check_strict_rr=check_strict_rr,
        )

    lut_sources = [s["lut_source"] for s in generate_params.values()]
    if lut_sources.count(LUTSource.RECV_LUT) > 1:
        raise ValueError("Only one RECV_LUT saving is currently supported")

    if len(generate_params) == 0:
        logger.warning(
            "Master file generation not enabled: no dense frames saving channel enabled."
        )
        return {}

    def master_file_task(src, params) -> None:
        p = MasterFileGeneration.Params(**params)
        gen = MasterFileGeneration(p)
        gen.run()
        logger.debug(f"On finished {src} master file generation")

    tasks: dict[str, MasterFileTask] = {}

    for src, params in generate_params.items():
        task = gevent.Greenlet(master_file_task, src, params)
        tasks[src] = MasterFileTask(task, end_event)

        def log_error(greenlet: gevent.Greenlet) -> None:
            msg = (
                f"Exception in master file task {str(uuid)} (channel '{src}'):\n"
                + "".join(traceback.format_exception(greenlet.exception))
            )
            logger.error(msg)
            print(msg)

        task.link_exception(callback=log_error)

    return tasks


class FrameIdxLUT(NamedTuple):
    master_indices: np.array
    recv_rank: int
    file_idx: int
    target_indices: np.array


class MasterFileGeneration:
    """Generate the master file containing the virtual dataset of ordered frames"""

    class Params(NamedTuple):
        num_frames: int
        frame_shape: Optional[tuple[int, int, int]]
        pixel_dtype: Optional[np.dtype]
        num_receivers: int
        saving_params: dict
        rr_offset: int
        lut_source: LUTSource
        pipeline: Optional[Pipeline] = None
        end_event: Optional[gevent.event.Event] = None
        cnt_name: Optional[str] = None
        config: Optional[dict] = None
        check_strict_rr: bool = False

    def __init__(self, params: Params):
        self._p = params
        self.saving_params.pop("filename_rank")

        self.master_file_path = f"{self.base_path}/{self.filename_prefix}_master.h5"

        self.layout = None
        self.lut_out_queue = None

    def __getattr__(self, name):
        if name in self._p.saving_params:
            return self._p.saving_params[name]
        if hasattr(self._p, name):
            return getattr(self._p, name)
        raise AttributeError(f"MasterFileGeneration has no {name} attr")

    @property
    def num_frames_per_file(self):
        return self.nb_frames_per_file

    @property
    def detector_path(self):
        return f"{self.nx_entry_name}/{self.nx_instrument_name}/{self.nx_detector_name}"

    def gen_filename(self, recv_rank, file_idx):
        return self.filename_format.format(
            file_number=self.start_number + file_idx,
            filename_rank=recv_rank,
            **self.saving_params,
        )

    def pipeline_finished(self):
        return all(self.pipeline.is_finished)

    def is_end(self):
        return self.end_event is not None and self.end_event.ready()

    def wait_pipeline_counter_value(self, value, rank=None):
        """Wait until the specific progress counter of the pipeline reaches a min. value
        The code minimises the number of calls to the pipeline.

        Return: The value of the counter after waiting
        """

        if self.pipeline is None:
            return value

        def counter():
            pc = self.pipeline.progress_counters[f"nb_frames_{self.cnt_name}"]
            return pc.sum if rank is None else pc.counters[rank].value

        while True:
            c = counter()
            if c >= value:
                return c
            elif self.is_end() or self.pipeline_finished():
                return counter()
            gevent.sleep(0.1)

    def get_pipeline_num_acq_frames(self):
        if self.pipeline is None or not self.pipeline_finished():
            return self.num_frames
        else:
            return self.pipeline.progress_counters["nb_frames_source"].sum

    def run(self):
        logger.debug(
            f"Generating master file for dataset at {self.base_path} [{self.lut_source}]..."
        )

        # wait for the first saved frame
        if self.wait_pipeline_counter_value(1) == 0:
            logger.info("Master file generation stopped")
            return

        # read the frame shape or pixel type from file, if needed
        if self.frame_shape is None or self.pixel_dtype is None:
            # wait until the first file from first receiver is ready
            self.wait_pipeline_counter_value(self.num_frames_per_file, 0)
            fname = os.path.join(self.base_path, self.gen_filename(0, 0))
            with ExitStack() as stack:
                f = open_h5_file_for_read(stack, fname)
                dpath = f"{self.detector_path}/data"
                data = f[dpath]
                if self.frame_shape is None:
                    self.frame_shape = data.shape[1:]
                if self.pixel_dtype is None:
                    self.pixel_dtype = data[:1].dtype

        logger.debug(
            f"Creating virtual layout with shape={(self.num_frames, *self.frame_shape)}, "
            f"dtype={self.pixel_dtype}"
        )
        self.layout = h5py.VirtualLayout(
            shape=(self.num_frames, *self.frame_shape),
            dtype=self.pixel_dtype,
        )

        # Queue receiving luts for strict Round-Robin check
        # Note: gevent.queue.Queue does not work across threads, use original Queue
        Queue = gevent.monkey.get_original("queue", "Queue")
        self.lut_out_queue = Queue() if self.check_strict_rr else None

        # Generate the LUTs, preferrably with (iterable) generators
        if self.lut_source == LUTSource.ROUND_ROBIN:
            all_luts = self.generate_round_robin_luts()
        elif self.lut_source == LUTSource.FILE_LUT:
            all_luts = self.read_target_file_luts()
        elif self.lut_source == LUTSource.RECV_LUT:
            assert self.pipeline is not None
            all_luts = self.read_recv_frame_luts()
        else:
            raise RuntimeError(f"Invalid {self.lut_source=}")

        with ExitStack() as stack:
            # spawn round-robin check task in another thread
            if self.check_strict_rr:
                pool = gevent.get_hub().threadpool
                check_fut = pool.spawn(self.check_round_robin)

                def end_check_task():
                    # Signal task and wait
                    self.lut_out_queue.put(None)
                    try:
                        check_fut.get()
                    except Exception as e:
                        logger.error("Strict RR check failed: %s", e)

                stack.callback(end_check_task)

            # Process each LUT as they arrive
            lut_frames = sum(map(self.process_lut, all_luts))

        acq_frames = self.get_pipeline_num_acq_frames()
        if lut_frames < acq_frames:
            logger.warning(
                f"Master file generated {lut_frames} frames, expected {acq_frames}"
            )

        # File taken as reference for Nexus/HDF5 structure
        first_file_path = (
            f"{self.base_path}/{self.filename_prefix}_{self.rr_offset}_00000.h5"
        )
        if not os.path.exists(first_file_path):
            raise ValueError(f"Reference file not found at {first_file_path}")

        self.write_master_file(first_file_path)

        logger.info(
            f"Master file written at {self.master_file_path} [{lut_frames} frames]"
        )

    def process_lut(self, lut):
        """Process each generated lut independently"""

        filename = self.gen_filename(lut.recv_rank, lut.file_idx)
        filepath = os.path.join(self.base_path, filename)
        if not os.path.exists(filepath):
            logger.warning(
                f"Expected file at {filepath} to have been created by receiver {lut.recv_rank}. "
                "Master file might point to invalid location."
            )
        linkpath = os.path.relpath(filepath, os.path.dirname(self.master_file_path))

        nframes_in_file = len(lut.target_indices)
        assert len(lut.master_indices) == nframes_in_file

        # Assign the virtual source to the virtual layout using the obtained frame indices
        vsource = h5py.VirtualSource(
            linkpath,
            f"{self.detector_path}/data",
            shape=(
                nframes_in_file,
                *self.frame_shape,
            ),
        )

        start_idx = np.min(lut.master_indices)
        end_idx = np.max(lut.master_indices) + 1
        logger.debug(
            f"Setting vds {nframes_in_file} frames in [{start_idx}:{end_idx}] to file {filepath}"
        )
        self.layout[lut.master_indices] = vsource[lut.target_indices]

        if self.lut_out_queue is not None:
            self.lut_out_queue.put(lut)

        return nframes_in_file

    def check_round_robin(self):
        """Check that strict Round-Robing order is respected in LUTs"""

        logger.debug("Strict Round-Robin task running ...")
        assert self.lut_out_queue is not None

        global_ok = True
        while (lut := self.lut_out_queue.get()) is not None:
            if not global_ok:
                continue
            recv_idx = self.num_frames_per_file * lut.file_idx + lut.target_indices
            master_expect = (
                lut.recv_rank - self.rr_offset + recv_idx * self.num_receivers
            )
            bad_idx = np.where(lut.master_indices != master_expect)[0]
            if len(bad_idx) > 0:
                got = lut.master_indices[bad_idx]
                expect = master_expect[bad_idx]
                logger.debug(
                    "LUT recv=%s file=%s is not strict RR: ",
                    lut.recv_rank,
                    lut.file_idx,
                )
                logger.debug(
                    "  bad_idx=%s, got=%s, expect=%s",
                    bad_idx,
                    expect,
                    got,
                )
                logger.debug("Skipping strict RR check for following frames")
                global_ok = False

        logger.debug("Strict Round-Robin task ended: global_ok=%s", global_ok)
        if not global_ok:
            logger.warning("Frame LUTs do not follow strict Round-Robin dispatch")

    def write_master_file(self, ref_file_path):
        with h5py.File(name=self.master_file_path, mode="w") as f:
            logger.debug(f"Inheriting metadata from {ref_file_path}")
            copy_metadata(src_path=ref_file_path, dst=f)

            data_path = f"{self.detector_path}/data"
            measurement_path = f"{self.nx_entry_name}/measurement/data"
            plot_path = f"{self.detector_path}/plot/data"

            # Create VDS
            dataset = f.create_virtual_dataset(data_path, layout=self.layout)
            dataset.attrs["interpretation"] = "image"

            # Create links
            f[measurement_path] = f[data_path]
            f[plot_path] = f[data_path]

            # Include Lima2 configuration
            if self.config:
                config_grp = f[self.detector_path].create_group("configuration")
                config_grp.attrs["NX_class"] = "NXnote"
                config_grp["data"] = json.dumps(self.config, indent=2)
                config_grp["type"] = "application/json"
                config_grp["description"] = "Lima2 configuration parameters"

    def generate_luts_from_recv_tasks(self, recv_task_fn, exec_in_threads=False):
        """Generate LUTs from parallel receiver tasks"""

        # Fifo used for passing the LUTs from recv tasks
        queue = gevent.queue.Queue()

        def recv_task(rank):
            try:
                recv_task_fn(queue, rank)
            except Exception as e:
                logger.error("Recv #%s task failed: %s", rank, e)
                queue.put(None)

        with Pool(self.num_receivers, exec_in_threads=exec_in_threads) as pool:
            pool.map_async(recv_task, range(self.num_receivers))

            task_running = self.num_receivers
            while task_running:
                # Read the LUT queue until all tasks are finished: push None
                lut = queue.get()
                if lut is not None:
                    yield lut
                else:
                    task_running -= 1

    def generate_round_robin_luts(self):
        """Generate frame indices LUTs for each receiver file based on strict
        Round-Robin dispatching. Receiver LUTs are generated in parallel
        """

        def recv_task(queue, rank):
            # Effective rank as seen from the dispatcher
            offset_rank = (rank - self.rr_offset) % self.num_receivers

            # Frames are dispatched to each receiver in turn.
            # If self.num_frames is not a multiple of num_receivers, some receivers
            # will get one more frame than the rest.
            def nframes_in_rcv():
                acq_frames = self.get_pipeline_num_acq_frames()
                base, extra = divmod(acq_frames, self.num_receivers)
                return base + (1 if offset_rank < extra else 0)

            logger.debug(f"Recv #{rank}: {nframes_in_rcv()=}")

            # Generate LUTs for this receiver until all frames are published
            rcv_frames = 0
            while (remaining := nframes_in_rcv() - rcv_frames) > 0:
                file_idx = rcv_frames // self.num_frames_per_file
                # Actual number of frames in this file
                nframes_in_file = min(self.num_frames_per_file, remaining)

                start_idx = offset_rank + rcv_frames * self.num_receivers
                end_idx = start_idx + (nframes_in_file - 1) * self.num_receivers + 1

                avail_end_idx = self.wait_pipeline_counter_value(end_idx)
                end_idx = min(end_idx, avail_end_idx)
                nframes_in_file = (end_idx - start_idx - 1) // self.num_receivers + 1
                if nframes_in_file <= 0:
                    break

                master_indices = np.arange(start_idx, end_idx, self.num_receivers)
                target_indices = np.arange(nframes_in_file)
                queue.put(FrameIdxLUT(master_indices, rank, file_idx, target_indices))

                rcv_frames += nframes_in_file

            # Signal that we are done
            queue.put(None)

        return self.generate_luts_from_recv_tasks(recv_task)

    def read_target_file_luts(self):
        """Read frame indices LUTs from each receiver file in parallel"""

        def recv_task(queue, rank):
            file_idx = 0
            # Read all files available from this receiver
            while True:
                end_idx = self.num_frames_per_file * (file_idx + 1)
                end_idx = self.wait_pipeline_counter_value(end_idx, rank)
                if end_idx <= self.num_frames_per_file * file_idx:
                    break

                filename = self.gen_filename(rank, file_idx)
                filepath = os.path.join(self.base_path, filename)
                if not os.path.exists(filepath):
                    logger.warning(
                        f"File {filepath} was not found, stopping master file"
                    )
                    break

                logger.debug(f"Reading frame LUT from {filepath} ...")
                with ExitStack() as stack:
                    f = open_h5_file_for_read(stack, filepath)
                    dpath = f"{self.detector_path}/frame_idx"
                    master_indices = np.array(f[dpath])

                nframes_in_file = len(master_indices)
                target_indices = np.arange(nframes_in_file)
                queue.put(FrameIdxLUT(master_indices, rank, file_idx, target_indices))

                file_idx += 1

            # Signal that we are done
            queue.put(None)

        return self.generate_luts_from_recv_tasks(recv_task)

    def read_recv_frame_luts(self):
        """Get frame indices LUTs from each receiver"""

        # Parallel query to all receivers and publish LUTs as soon as available

        def get_data(rank, from_rcv_idx, cache):
            # get the previously cached data, if any
            if len(cache) > 0:
                return cache.pop(0)

            # query the server: np.array["recv_idx", "det_idx"]
            logger.debug(f"Reading frame LUT from recv #{rank} ...")
            while True:
                if self.is_end():
                    return None
                # ask if finished before retrieving data: ensure nothing is lost
                finished = self.pipeline_finished()
                rcv_frame_idx = self.pipeline.pop_raw_frame_idx(rank)
                if len(rcv_frame_idx) > 0:
                    break
                elif finished:
                    logger.debug(f"Recv #{rank} pipeline finished")
                    return None
                gevent.sleep(0.5)

            # ensure data continuity
            rcv_frames = rcv_frame_idx["recv_idx"]
            block_len = len(rcv_frame_idx)
            expected_frames = np.arange(from_rcv_idx, from_rcv_idx + block_len)
            assert np.all(
                rcv_frames == expected_frames
            ), f"{rcv_frames=} != {expected_frames=}"

            det_frames = rcv_frame_idx["det_idx"]
            logger.debug(
                f"popped {len(det_frames)} frames from recv #{rank}: "
                f"{det_frames[0]}-{det_frames[-1]}"
            )
            return det_frames

        def cache_data(cache, det_frames):
            return cache.insert(0, det_frames)

        def recv_task(queue, rank):
            file_idx = 0
            cache = []
            end = False
            while not end:
                t0 = time.time()

                first_file_frame = self.num_frames_per_file * file_idx
                nframes_in_file = self.num_frames_per_file

                master_indices = np.zeros((nframes_in_file,), np.int32)

                # read server and fill master indices
                filled = 0
                while filled < nframes_in_file:
                    det_frames = get_data(rank, first_file_frame + filled, cache)
                    if det_frames is None:
                        nframes_in_file = filled
                        end = True
                        break
                    to_fill = min(len(det_frames), nframes_in_file - filled)
                    master_indices[filled : filled + to_fill] = det_frames[:to_fill]
                    filled += to_fill
                    if to_fill < len(det_frames):
                        cache_data(cache, det_frames[to_fill:])

                if nframes_in_file > 0:
                    master_indices = np.resize(master_indices, (nframes_in_file,))
                    target_indices = np.arange(nframes_in_file)
                    queue.put(
                        FrameIdxLUT(master_indices, rank, file_idx, target_indices)
                    )

                elapsed = time.time() - t0
                logger.debug(f"Recv #{rank} file #{file_idx} took {elapsed:.3f} sec")

                file_idx += 1

            # Signal that we are done
            queue.put(None)

        return self.generate_luts_from_recv_tasks(recv_task)


def copy_group(src_node: h5py.Group, dst_node: h5py.Group):
    """Recursively copy items of a group, skipping frame datasets."""

    for attr_key, attr_value in src_node.attrs.items():
        logger.debug(f"{dst_node.name}: copying attribute {attr_key} ({attr_value})")
        dst_node.attrs[attr_key] = attr_value

    ignore_datasets = ["data", "frame_idx", "det_frame_idx"]
    for key, value in src_node.items():
        if isinstance(value, h5py.Dataset) and key in ignore_datasets:
            # Skip frame datasets
            logger.debug(f"Skipping {value.name}")
            continue
        elif isinstance(value, h5py.Group):
            # Conservative group copy
            logger.debug(f"Creating group {value.name}")
            grp = dst_node.create_group(name=key)
            copy_group(src_node=value, dst_node=grp)
        else:
            # Plain copy
            logger.debug(f"Copying object {key} into {dst_node.name}")
            src_node.copy(value, dst_node)


def copy_metadata(src_path: str, dst: h5py.File):
    """Copy everything but frame data from one hdf5 file to another."""
    with ExitStack() as stack:
        src = open_h5_file_for_read(stack, src_path)
        copy_group(src_node=src, dst_node=dst)


def open_h5_file_for_read(stack, path, nb_retries=5):
    for r in range(nb_retries):
        try:
            return stack.enter_context(h5py.File(path, "r"))
        except Exception as e:
            error = str(e)
            gevent.sleep(0.5)

    raise RuntimeError(f"Error opening {path} after {nb_retries} retries: {error}")


class Pool:
    def __init__(self, *args, exec_in_threads=False, **kws):
        self._exec_in_threads = exec_in_threads
        self._args = args
        self._kws = kws
        self._pool = None

    def __enter__(self):
        if self._exec_in_threads:
            cls = gevent.threadpool.ThreadPool
        else:
            cls = gevent.pool.Pool
        self._pool = cls(*self._args, **self._kws)
        return self._pool

    def __exit__(self, *args):
        self._pool.join()
