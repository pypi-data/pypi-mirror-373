import subprocess
import threading
import weakref
from collections import defaultdict
from typing import Any, Callable, Dict

from ._types import PIAInformationType
from ._utils import parse


class PIAMonitors:
    def __init__(self, pia):
        self._pia = pia

        self._monitors: Dict[PIAInformationType, subprocess.Popen[str]] = {}
        self._observers: Dict[
            PIAInformationType, weakref.WeakSet[Callable[[Any], None]]
        ] = defaultdict(weakref.WeakSet)

        self._lock = threading.RLock()

    def _start_monitor(self, info_type: PIAInformationType):
        cmd = (
            [self._pia._config.executable_path]
            + self._pia._constants.monitor_cmd
            + [info_type.value]
        )

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )

        self._monitors[info_type] = process

        def monitor_loop():
            if not process.stdout:
                raise Exception("Subprocess has no standard output stream!")

            for line in process.stdout:
                value = parse(line.strip(), info_type)

                # Copy observers with lock acquired
                with self._lock:
                    observers = list(self._observers[info_type])

                for observer in observers:
                    observer(value)

        threading.Thread(target=monitor_loop, daemon=True).start()

    def attach(
        self,
        info_type: PIAInformationType,
        observer: Callable[
            [Any],
            None,
        ],
    ):
        """
        Register the given observer to receive updates whenever
        the specified information changes.

        Map from `PIAInformationType` to the type of the value that
        the observer will be updated with (see `PIA`'s `get` method
        for more information):
        - `ALLOW_LAN`, `DEBUG_LOGGING`, `REQUEST_PORT_FORWARD` ->
        `bool`
        - `CONNECTION_STATE` -> `PIAConnectionState`
        - `PORT_FORWARD` -> `int` or `PIAPortForwardStatus`
        - `PROTOCOL` -> `PIAProtocol`
        - `PUB_IP`, `VPN_IP` -> `ipaddress.IPv4Address` or `None`
        - `REGION` -> `str`

        Returns the current value for the given information type.
        Returns `None` if the given information type is `REGIONS`,
        as `REGIONS` is not monitorable.
        """

        if info_type is PIAInformationType.REGIONS:
            return None

        with self._lock:
            if info_type not in self._monitors:
                self._start_monitor(info_type)

            self._observers[info_type].add(observer)

        return self._pia.get(info_type).data

    def _stop_monitor(self, info_type: PIAInformationType):
        if process := self._monitors.get(info_type):
            process.terminate()
            process.wait()
            del self._monitors[info_type]

    def detach(
        self,
        info_type: PIAInformationType,
        observer: Callable[
            [Any],
            None,
        ],
    ):
        """
        Unregisters the given observer for the given information type,
        meaning it will no longer be updated when the specified
        information changes.
        """

        with self._lock:
            self._observers[info_type].discard(observer)

            # Clean up monitor if no observers left
            if not self._observers[info_type] and info_type in self._monitors:
                self._stop_monitor(info_type)
