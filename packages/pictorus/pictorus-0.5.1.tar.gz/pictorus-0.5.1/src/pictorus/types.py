"""Shared type definitions"""

from typing import Dict, Optional, Union
from enum import Enum
from dataclasses import dataclass, asdict


class AppLogLevel(Enum):
    """Log levels that can be set for pictorus apps"""

    OFF = "off"
    ERROR = "error"
    WARN = "warn"
    INFO = "info"
    DEBUG = "debug"


@dataclass
class LogMessage:
    message: str
    timestamp: int
    level: Optional[str] = None


@dataclass
class ErrorLog:
    """Error log structure for pictorus apps"""

    err_type: Optional[str]
    message: Optional[str]

    def copy(self) -> "ErrorLog":
        """Create a copy of the ErrorLog instance."""
        return ErrorLog(err_type=self.err_type, message=self.message)


@dataclass
class TargetState:
    error_log: Optional[ErrorLog] = None
    run_app: Optional[bool] = None
    build_hash: Optional[str] = None
    params_hash: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Union[str, bool]]) -> "TargetState":
        """Initialize TargetState from a dictionary."""
        state = cls()
        err_log_data = data.get("error_log", {})
        if isinstance(err_log_data, dict):
            state.error_log = ErrorLog(
                err_type=err_log_data.get("err_type"), message=err_log_data.get("message")
            )

        run_app = data.get("run_app")
        if isinstance(run_app, bool):
            state.run_app = bool(run_app)

        build_hash = data.get("build_hash")
        if isinstance(build_hash, str):
            state.build_hash = build_hash

        params_hash = data.get("params_hash")
        if isinstance(params_hash, str):
            state.params_hash = params_hash

        return state


@dataclass
class NetworkData:
    ip_address: Optional[str]
    hostname: str


@dataclass
class DeviceState:
    connected: Optional[bool] = None
    version: Optional[str] = None
    cached_version: Optional[str] = None
    network: Optional[NetworkData] = None
    target_states: Optional[Dict[str, Union[TargetState, None]]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Union[str, bool, Dict]]) -> "DeviceState":
        """Initialize DeviceState from a dictionary."""
        state = cls()
        connected = data.get("connected")
        if isinstance(connected, bool):
            state.connected = connected

        version = data.get("version")
        if isinstance(version, str):
            state.version = version

        cached_version = data.get("cached_version")
        if isinstance(cached_version, str):
            state.cached_version = cached_version

        network_data = data.get("network")
        if isinstance(network_data, dict):
            ip_addr = network_data.get("ip_address")
            ip_addr_valid = isinstance(ip_addr, str) or ip_addr is None

            hostname = network_data.get("hostname")
            hostname_valid = isinstance(hostname, str)
            if ip_addr_valid and hostname_valid:
                state.network = NetworkData(ip_address=ip_addr, hostname=hostname)

        targets_data = data.get("target_states", {})
        if isinstance(targets_data, dict):
            state.target_states = {
                target: TargetState.from_dict(state) if state else None
                for target, state in targets_data.items()
            }

        return state

    def to_desired_dict(self) -> Union[dict, None]:
        """
        Return a dict to be used in the desired shadow state.

        This differs from the standard dict representation in that it
        only includes fields that are set.
        """
        pruned = _remove_none_values(asdict(self))
        if not pruned:
            return None

        return pruned


def _remove_none_values(data: dict) -> dict:
    """Recursively remove none values from a dict."""
    pruned = {}
    for key, value in data.items():
        if isinstance(value, dict):
            inner_pruned = _remove_none_values(value)
            # Omit empty dicts
            if inner_pruned:
                pruned[key] = inner_pruned

        elif value is not None:
            pruned[key] = value

    return pruned
