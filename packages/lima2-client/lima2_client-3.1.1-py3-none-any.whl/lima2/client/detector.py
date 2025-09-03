# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""Low level interface to the detector.

Typical usage example:

  import tango
  ctrl = tango.DeviceProxy(ctrl_dev_name)
  recvs = [tango.DeviceProxy(n) for n in recv_dev_names]

  det = Detector(ctrl, recvs)
  det.prepare_acq(...)
  det.start_acq(...)
"""

from __future__ import annotations

import contextlib
import json
import logging
import uuid
from collections.abc import Iterator

import gevent

import tango
from beartype import beartype
from gevent.lock import BoundedSemaphore
from jsonschema_default import create_from

from lima2.client import pipelines
from lima2.client import state_machine as fsm
from lima2.client.state_machine import State
from lima2.client.utils import validate

# Create a logger
_logger = logging.getLogger(__name__)


class CommError(RuntimeError):
    """Communication error with the Detector interface."""

    pass


class Detector:
    """The main Detector interface."""

    def __init__(
        self,
        ctrl_dev: tango.DeviceProxy,
        *recv_devs: tango.DeviceProxy,
        timeout: int,
    ):
        """Construct a Detector object.

        Example:
            >>> ctrl = tango.DeviceProxy(ctrl_dev_name)
            >>> recvs = [tango.DeviceProxy(n) for n in recv_dev_names]
            >>> det = Detector(ctrl, recvs)

        Args:
            ctrl_dev: The control device instance name (aka domain/family/member)
            recv_devs: A list of receiver device instance names (aka domain/family/member)
            timeout: The tango device timeout [second]
        """
        # Preconditions
        if not recv_devs:
            raise ValueError("Must provide at least one receiver")

        self.__ctrl = ctrl_dev
        self.__recvs = list(recv_devs)
        self._state_event_ids: dict[tango.DeviceProxy, int] = {}

        self.ping()

        rank_order = [d.recv_rank for d in recv_devs]
        if not all([r == i for i, r in enumerate(rank_order)]):
            raise ValueError(
                f"Receiver MPI rank order does not match client order: {rank_order}"
            )

        self.__params_schema: dict | None = None
        self.__fsm = fsm.StateMachine(self.__ctrl, self.__recvs)
        self.__fsm_lock = BoundedSemaphore()

        self._register_state_change_handlers()
        self.sync_hard()

        if _logger.getEffectiveLevel() == logging.DEBUG:
            # Log transition of states
            def on_state_change(state):
                _logger.debug(f"on_state_change: transition to {state}")

            self.register_transition_logger(on_state_change)

        for d in self.devs:
            d.set_green_mode(tango.GreenMode.Gevent)
            d.set_timeout_millis(timeout * 1000)

    def unregister_events(self):
        """Unregister all state loggers and tango event handlers.

        This method serves only in specific cases where event handlers must for
        some reason be unregistered. In a normal use case, a Client is
        instantiated once per Lima2 instance, and no cleanup is necessary.
        """
        for device, event_id in self._state_event_ids.items():
            device.unsubscribe_event(event_id)
        self._state_event_ids.clear()

    @contextlib.contextmanager
    def _locked_fsm(self) -> Iterator[fsm.StateMachine]:
        self.__fsm_lock.acquire()
        try:
            yield self.__fsm
        finally:
            self.__fsm_lock.release()

    @property
    def det_info(self) -> dict:
        """
        A dict containing the detector static information such as make, model, serial number,
        detector and pixel dimensions...

        Example:

            >>> det.det_info
            {
                'plugin': 'Dectris',
                'model': 'Dectris EIGER2 CdTe 1M-W',
                'sn': 'E-02-0234',
                'pixel_size': {'x': 0.5, 'y': 0.5},
                'expo_time_range': [1, 10000000],
                'latency_time_range': [0, 1000000],
                'trigger_modes': ['internal', 'software'],
                'dimensions': {'x': 2048, 'y': 2048}
            }

        Group:
            Info
        """
        return json.loads(self.__ctrl.det_info)  # type: ignore

    @property
    def det_status(self) -> dict:
        """
        A dict containing the detector health information such as make, model, serial number,
        detector and pixel dimensions...

        Example:

            >>> det.det_status
            {
                'humidity': 2.78143310546875,
                'temperature': 27.421295166015625,
                'high_voltage_state': 'READY',
                'state': 'idle',
                'time': '2023-01-26T12:32:48+0100'
            }

        Group:
            Status
        """
        return json.loads(self.__ctrl.det_status)  # type: ignore

    @property
    def det_capabilities(self) -> dict:
        """
        A dict containing the detector capabilities...

        Example:

            >>> det.det_capabilities
            {
                'trigger_modes': ['internal', 'software']
            }

        Group:
            Info
        """
        return json.loads(self.__ctrl.det_capabilities)  # type: ignore

    def __get_params_schema(self) -> dict:
        """
        Get the parameters's schema for each devices from the Tango class attribute

        Raises tango.DevFailed if we cannot connect to database at TANGO_HOST.

        If the lima2 server hasn't been started yet, returns a dict of the form:
        {
            d.dev_name(): {"init_params": None, "acq_params": None}
            for d in self.devs
        }
        """
        tango_db = tango.Database()

        res = {}
        for d in self.devs:
            # Use DB only to get device class (device do not need to be exported)
            dev_name = d.dev_name()
            dev_class = tango_db.get_device_info(dev_name).class_name

            def get_schema(dev_class, param):
                prop = tango_db.get_class_attribute_property(dev_class, param)
                # Each attribute property is a StdStringVector with a single value
                if prop[param]:
                    return json.loads(prop[param]["schema"][0])

            res[dev_name] = {
                "init_params": get_schema(dev_class, "init_params"),
                "acq_params": get_schema(dev_class, "acq_params"),
            }

        return res

    @property
    def params_schema(self) -> dict:
        """Returns JSON schemas of init, acquisition and processing parameters.

        Example:

            >>> det.params_schema
            {
                'id00/limacontrol/simulator': {
                    'init_params': {
                        "$schema":"http://json-schema.org/draft-06/schema",
                        "$id":"https://example.com/lima2.schema.json",
                        "title":"init_params"
                    },
                    'acq_params': {...}
                }
                'id00/limareceiver/simulator@1': {
                    'init_params': None,
                    'acq_params': {...}
                },
                ...
            }

        Returns:
            A dict mapping parameters with their JSON schema for each devices.

        Group:
            Parameters
        """
        if self.__params_schema is None:
            self.__params_schema = self.__get_params_schema()

        return self.__params_schema

    @property
    def params_default(self) -> dict:
        """Returns a set of parameters with default values for init, acquisition and processing parameters.

        Example:

            >>> det.params_schema
            {
                'id00/limacontrol/simulator': {
                    'init_params': {
                        "$schema":"http://json-schema.org/draft-06/schema",
                        "$id":"https://example.com/lima2.schema.json",
                        "title":"init_params"
                    },
                    'acq_params': {...}
                }
                'id00/limareceiver/simulator@1': {
                    'init_params': None,
                    'acq_params': {...}
                },
                ...
            }

        Returns:
            A dict mapping parameters with their JSON schema for each devices.

        Group:
            Parameters
        """
        res = {}
        for key, value in self.params_schema.items():
            res[key] = {k: create_from(v) if v else None for k, v in value.items()}

        return res

    def ping(self):
        """
        Ping all the devices of the system.

        Raises:
            CommError if the connection failed.

        Group:
            Status
        """
        for d in self.devs:
            try:
                d.ping()
            except tango.DevFailed as e:
                raise CommError(f"Failed to ping device {d.dev_name()}") from e

    @property
    def devs(self) -> list[tango.DeviceProxy]:
        """
        The list of all the Tango devices.

        Group:
            Devices
        """
        return [self.__ctrl] + self.__recvs

    @property
    def ctrl(self) -> tango.DeviceProxy:
        """
        The control Tango device.

        Group:
            Devices
        """
        return self.__ctrl

    @property
    def recvs(self) -> list[tango.DeviceProxy]:
        """
        The receiver Tango devices.

        Group:
            Devices
        """
        return self.__recvs

    @property
    def state(self) -> State:
        """
        The current state of the client.

        Group:
            State
        """
        with self._locked_fsm() as fsm:
            return fsm.state

    def sync_hard(self):
        """
        Synchronize the current state of the client with the server states.

        Group:
            State
        """
        with self._locked_fsm() as fsm:
            try:
                fsm.sync()
            except Exception as e:
                _logger.warning(f"Unable to sync with server: {e}")

            return fsm.state

    @property
    def dev_states(self):
        """
        A list of the individual states of the devices.

        Group:
            State
        """
        return [dev.acq_state for dev in self.devs]

    def register_transition_logger(self, logger):
        """
        Register a logger function to be notified on FSM transition.

        Args:
            logger: A callback with the following signature.

        Example:

            >>> def on_transition(source, target):
                    print(f"transition from {source} to {target}")
            >>> fsm.register_transition_logger(on_transition)

        Group:
            State
        """
        with self._locked_fsm() as fsm:
            fsm.register_transition_logger(logger)

    def unregister_transition_logger(self, logger):
        """
        Unregister a given transition logger function.

        Args:
            logger: A callback to unregister.

        Group:
            State
        """
        with self._locked_fsm() as fsm:
            fsm.unregister_transition_logger(logger)

    @beartype
    def prepare_acq(
        self, uuid: uuid.UUID, ctrl_params: dict, acq_params: list, proc_params: list
    ):
        """
        Prepare the acquisition with a given UUID.

        Args:
            uuid: The UUID associated with the acquisition
            ctrl_params: A dict of system acquisition params (per controller)
            acq_params: A list of acquisition params (per receivers)
            proc_params: A list of processing params (per receivers)

        Group:
            Control
        """
        _logger.debug(
            f"prepare_acq({uuid}, {ctrl_params}, {acq_params}, {proc_params})"
        )

        def parallel_exec(ctrl_fn, recv_fn):
            tasks = [gevent.spawn(ctrl_fn, self.__ctrl)]
            tasks += [gevent.spawn(recv_fn, i, r) for i, r in enumerate(self.__recvs)]
            gevent.joinall(tasks, raise_error=True)

        def validate_ctrl(ctrl):
            validate(
                instance=ctrl_params,
                schema=self.params_schema[ctrl.name()]["acq_params"],
            )

        def validate_recv(i, recv):
            validate(
                instance=acq_params[i],
                schema=self.params_schema[recv.name()]["acq_params"],
            )

            pipeline_class = pipelines.get_class(proc_params[i]["class_name"])
            validate(instance=proc_params[i], schema=pipeline_class.params_schema)

        parallel_exec(validate_ctrl, validate_recv)

        # Update parameters on the device servers
        def update_ctrl(ctrl):
            # TODO: Rename acq_params to ctrl_params
            ctrl.acq_params = json.dumps(ctrl_params)

        def update_recv(i, recv):
            recv.acq_params = json.dumps(acq_params[i])
            recv.proc_params = json.dumps(proc_params[i])

        parallel_exec(update_ctrl, update_recv)

        # Raises and reverts to IDLE on exception
        with self._locked_fsm() as fsm:
            fsm.prepare(str(uuid))

    def start_acq(self):
        """Start acquisition.

        Group:
            Control
        """

        self._register_on_end_acq_handlers()

        with self._locked_fsm() as fsm:
            fsm.start()

    def trigger(self):
        """Software trigger.

        Group:
            Control
        """
        with self._locked_fsm() as fsm:
            if fsm.state == State.FAULT:
                _logger.warning("Got trigger() while in FAULT state -> ignoring")
            else:
                fsm.trigger()

    def stop_acq(self):
        """
        Stop acquisition.

        Group:
            Control
        """
        with self._locked_fsm() as fsm:
            fsm.stop()
            fsm.close()

    def reset_acq(self):
        """
        Reset acquisition when the detector is in State.FAULT state

        Group:
            Control
        """
        with self._locked_fsm() as fsm:
            fsm.reset_acq()

    def abort_acq(self):
        """
        Abort current acquisition (call Stop on running devices) and go to FAULT state.

        Group:
            Control
        """
        with self._locked_fsm() as fsm:
            fsm.abort()

    @property
    def ctrl_params(self):
        """
        Returns the current set of control params

        Group:
            Parameters
        """
        return json.loads(self.__ctrl.acq_params)

    @property
    def acq_params(self):
        """
        Returns the current set of receiver params

        Group:
            Parameters
        """
        return [json.loads(dev.acq_params) for dev in self.__recvs]

    @property
    def proc_params(self):
        """
        Returns the current set of processing params

        Group:
            Parameters
        """
        return [json.loads(dev.proc_params) for dev in self.__recvs]

    @property
    def nb_frames_acquired(self) -> int:
        """
        The number of acquired frames (on the detector side).

        Returns:
            The number of frames acquired

        Group:
            Status
        """
        return self.__ctrl.nb_frames_acquired  # type: ignore

    @property
    def nb_frames_xferred(self) -> list[int]:
        """
        The number of frames transferred (across all receivers).

        Returns:
            A list of number of frames transferred

        Group:
            Status
        """
        return [recv.nb_frames_xferred for recv in self.__recvs]

    # @contextmanager
    # @beartype
    # def get_processing_resource(self, uuid: uuid.UUID):
    #     """
    #     Yields a Processing instance given a uuid. Example:

    #     with det.get_processing_resource(uuid) as proc:
    #         print(f"counters: {proc.progress_counters()}")
    #         # Processing is erased when leaving this scope

    #     Returns:
    #         a Processing object.
    #     """
    #     try:
    #         yield self.get_processing(self, uuid)
    #     finally:
    #         self.erase_processing(uuid)

    def _register_state_change_handlers(self):
        """Register a "change of acq_state" callback on each device.

        These handlers are responsible for handling receivers entering FAULT state
        (e.g. when the pipeline throws an exception), and for setting the global state
        to DISCONNECTED if we receive errors on the tango event channel.
        """

        disconnected_devices = set()

        def on_acq_state_change(evt: tango.EventData):
            """Handler for state changes of each individual device"""
            nonlocal disconnected_devices

            # Handle disconnect
            if evt.err:
                if evt.device not in disconnected_devices:
                    _logger.error(
                        f"Lost connection to device {evt.device.dev_name()}:\n"
                        + "\n".join([f"- {err.desc}" for err in evt.errors])
                        + "\n"
                    )
                disconnected_devices.add(evt.device)
                with self._locked_fsm() as fsm:
                    fsm.disconnect()
                return

            # Handle FAULT
            AcqState = type(evt.device.acq_state)
            acq_state = AcqState(evt.attr_value.value)
            _logger.debug(f"{evt.device.dev_name()} changed state to {acq_state.name}")

            if acq_state == AcqState.fault:
                _logger.error(
                    f"Device {evt.device.dev_name()} in FAULT state.\n"
                    f"Reason: '{evt.device.last_error}'\n"
                )
                if self.state not in [State.FAULT, State.UNKNOWN]:
                    _logger.error("Aborting acquisition.")
                    with self._locked_fsm() as fsm:
                        fsm.abort()

            # Handle reconnect
            if evt.device in disconnected_devices:
                _logger.info(f"{evt.device.dev_name()} seems back up")
                disconnected_devices.remove(evt.device)

            if self.state == State.DISCONNECTED:
                _logger.info("Trying to sync...")
                with self._locked_fsm() as fsm:
                    try:
                        fsm.sync()
                        disconnected_devices = set()
                        print("Lima2 reconnected.")
                    except Exception as e:
                        _logger.warning(f"Sync failed: {e}")
                    finally:
                        _logger.info(f"Current state: {fsm.state}")

        self._state_event_ids = {
            dev: dev.subscribe_event(
                "acq_state",
                tango.EventType.CHANGE_EVENT,
                on_acq_state_change,
            )
            for dev in self.devs
        }

    def _register_on_end_acq_handlers(self):
        """Register an "end of acquisition" callback on each receiver.

        This handler callback is responsible for calling Close on the control device when
        all receivers are finished transferring frames.
        """
        nb_frames_xferreds = []
        event_ids = {}

        def on_end_acq(evt):
            nonlocal nb_frames_xferreds

            # Filter spurious error events (if the device is restarted)
            if evt.err:
                _logger.error(
                    f"Error on {evt.device.dev_name()} 'nb_frames_xferred' event:\n"
                    + "\n".join([f"- {err.desc}" for err in evt.errors])
                    + "\n"
                )
                for r, e in event_ids.items():
                    r.unsubscribe_event(e)
                return

            nb_frames_xferreds.append(evt)

            if len(nb_frames_xferreds) == len(self.recvs):
                for r, e in event_ids.items():
                    r.unsubscribe_event(e)

                _logger.debug(f"on_end_acq while {self.state}")
                with self._locked_fsm() as fsm:
                    if fsm.state == State.RUNNING:
                        fsm.close()
                    elif fsm.state == State.FAULT:
                        # Acquisition aborted -> do nothing
                        pass
                    else:
                        # Unexpected
                        _logger.info(f"Acquisition ended while in state {fsm.state}")

                nb_frames_xferreds = []

        # On server side, data_ready_event is pushed by each receiver
        # at the end of the acquisition loop.
        event_ids = {
            r: r.subscribe_event(
                "nb_frames_xferred",
                tango.EventType.DATA_READY_EVENT,
                on_end_acq,
            )
            for r in self.recvs
        }
