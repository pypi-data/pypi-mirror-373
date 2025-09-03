# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""Finite state machine definition for the detector.
"""

import logging
from concurrent.futures import ThreadPoolExecutor
from enum import Enum, auto
from collections.abc import Callable

import tango

import finite_state_machine as fsm
from finite_state_machine import transition

# Create a logger
_logger = logging.getLogger(__name__)


class State(Enum):
    """The possible states of the Detector state machine."""

    # Enum values for '<enum 'State'>' must start at 0 and increment by 1.
    IDLE = 0
    PREPARED = auto()
    RUNNING = auto()
    STOPPED = auto()
    CLOSING = auto()  # TODO(mdu): Unused (kept for backward compat with bliss 2.2)
    FAULT = auto()
    UNKNOWN = auto()
    DISCONNECTED = auto()


# Conditions
def trigger_mode_software(fsm):
    # TODO
    return True


class StateMachine(fsm.StateMachine):
    """Detector Finite State Machine."""

    def __init__(self, ctrl: tango.DeviceProxy, recvs: list[tango.DeviceProxy]):
        """
        Construct a StateMachine that control the state of the detector.

        Args:
            ctrl: Control tango device
            recvs: list of Receiver tango devices
        """
        self._state = State.UNKNOWN
        self.ctrl = ctrl
        self.recvs = recvs
        self.__loggers: list[Callable] = []
        super().__init__()

    def sync(self):
        """Synchronize the local state with the server states.

        Raises if:
        - we cannot ping one of the devices
        - states are not identical across all devices

        Returns the synchronized state.
        """

        for device in [self.ctrl] + self.recvs:
            device.ping()
        states = [d.acq_state for d in [self.ctrl] + self.recvs]
        ctl_state = states[0]

        ServerState = type(ctl_state)

        if all(s == ctl_state for s in states):
            map = {
                ServerState.idle: State.IDLE,
                ServerState.prepared: State.PREPARED,
                ServerState.running: State.RUNNING,
                ServerState.stopped: State.IDLE,
            }
            self.state = map[ctl_state]
        elif all(s in [ServerState.idle, ServerState.prepared] for s in states):
            # Tolerate a mix of prepared and idle devices. In this case,
            # the global state shall be IDLE (forcing user to prepare again).
            self.state = State.IDLE
        elif any(s == ServerState.fault for s in states):
            self.state = State.FAULT
        else:
            # States are divergent, sync cannot be done
            self._state = State.UNKNOWN
            raise RuntimeError(f"Cannot sync: inconsistent server states ({states})")

        return self.state

    @property
    def devs(self):
        return [self.ctrl] + self.recvs

    @property
    def state(self) -> State:
        return self._state

    @state.setter
    def state(self, value: State) -> None:
        if self._state != value:
            self._state = value
            self.on_state_change(value)

    @transition(
        source=[State.IDLE, State.PREPARED],
        target=State.PREPARED,
        on_error=State.IDLE,
        reraise=True,
    )
    def prepare(self, uuid: str) -> None:
        """Prepare all devices.

        Reverts to IDLE and raises if at least one device threw an exception.
        """

        # Collect potential tango errors so we can print them nicely
        tango_errors: dict[tango.DeviceProxy, list[str]] = {
            dev: [] for dev in self.devs
        }

        def prepare_dev(d, uuid):
            try:
                d.Prepare(uuid)
            except tango.DevFailed as e:
                for arg in e.args:
                    tango_errors[d].append(arg.desc)
            # Let other exception types propagate

        # Any exception in prepare_dev other than DevFailed will be raised here
        with ThreadPoolExecutor(max_workers=len(self.devs)) as executor:
            list(executor.map(prepare_dev, self.devs, [uuid] * len(self.devs)))

        if any([len(tango_errors[dev]) > 0 for dev in self.devs]):
            raise RuntimeError(
                "Prepare failed:\n- "
                + "\n- ".join(
                    [
                        f"{dev.dev_name()}: {error}"
                        for dev in self.devs
                        for error in tango_errors[dev]
                    ]
                )
                + "\nReverting to IDLE"
            )

    @transition(source=State.PREPARED, target=State.RUNNING)
    def start(self) -> None:
        def start_device(dev: tango.DeviceProxy) -> None:
            dev.Start()

        with ThreadPoolExecutor(max_workers=len(self.devs)) as executor:
            list(executor.map(start_device, self.devs))

    @transition(
        source=State.RUNNING, target=State.RUNNING, conditions=[trigger_mode_software]
    )
    def trigger(self):
        self.ctrl.Trigger()

    @transition(source=State.RUNNING, target=State.STOPPED)
    def stop(self):
        def stop_device(dev: tango.DeviceProxy) -> None:
            dev.Stop()

        with ThreadPoolExecutor(max_workers=len(self.devs)) as executor:
            list(executor.map(stop_device, self.devs))

    @transition(source=[State.RUNNING, State.STOPPED], target=State.IDLE)
    def close(self):
        self.ctrl.Close()

    @transition(source=State.FAULT, target=State.IDLE)
    def reset_acq(self):
        def reset_device(dev: tango.DeviceProxy) -> None:
            dev.Reset()

        with ThreadPoolExecutor(max_workers=len(self.devs)) as executor:
            list(executor.map(reset_device, self.devs))

    @transition(
        source=[state for state in list(State)],
        target=State.FAULT,
        on_error=State.FAULT,
    )
    def abort(self):
        """Called when a device enters FAULT state."""
        self.ctrl.Stop()

        def stop_recv(dev: tango.DeviceProxy) -> None:
            _logger.debug(
                f"stopping recv {dev.dev_name()} ({dev.acq_state}, {dev.acq_state.name})"
            )
            if dev.acq_state.name == "running":
                dev.Stop()

        # Stop acquisition on receivers that are running
        with ThreadPoolExecutor(max_workers=len(self.recvs)) as executor:
            list(executor.map(stop_recv, self.recvs))

        self.ctrl.Close()

    @transition(
        source=[state for state in list(State)],
        target=State.DISCONNECTED,
    )
    def disconnect(self):
        pass

    def register_transition_logger(self, logger):
        """
        Register a logger to be notified on transition.

        Args:
            logger: A callback with the following signature.

        Example:
            def on_transition(source, target):
                print(f"transition from {source} to {target}")

            fsm.register_transition_logger(on_transition)
        """
        self.__loggers.append(logger)

    def unregister_transition_logger(self, logger):
        """
        Unregister a given transition logger function.

        Args:
            logger: A callback to unregister.
        """
        if logger in self.__loggers:
            self.__loggers.remove(logger)

    def clear_transition_loggers(self):
        self.__loggers.clear()

    def on_state_change(self, state):
        _logger.debug(f"on_state_change {state}")
        futures = []
        with ThreadPoolExecutor(max_workers=len(self.__loggers) or 1) as executor:
            for logger in self.__loggers:
                futures.append(executor.submit(logger, state))

        # Raise exceptions in the calling thread
        for f in futures:
            f.result()
