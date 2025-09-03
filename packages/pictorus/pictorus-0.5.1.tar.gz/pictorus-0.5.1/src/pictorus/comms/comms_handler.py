from abc import ABC, abstractmethod
from dataclasses import dataclass
from time import time
from typing import Callable, Union

from pictorus.command import Command, CommandResult, DeployTarget
from pictorus.logging_utils import get_logger
from pictorus.types import DeviceState, LogMessage

logger = get_logger()


@dataclass
class CommsConfig:
    """Configuration for communication handlers."""

    process_cmd: Callable[[Command, Union[DeployTarget, None]], Union[CommandResult, None]]
    sync_device_state: Callable[[], None]


@dataclass
class TelemData:
    """Telemetry data structure for pictorus apps."""

    utc_time_ms: int
    build_id: Union[str, None]
    data: dict
    target_id: str


class CommsHandler(ABC):
    """Abstract base class for communication handlers."""

    def __init__(self, config: CommsConfig) -> None:
        self._config = config
        self._target_ttls = {}

    @abstractmethod
    def add_telemetry(self, data: TelemData) -> None:
        """Add telemetry data to the communication queue."""
        pass

    @abstractmethod
    def add_log(self, log: LogMessage, target_id: str) -> None:
        """Add log entry to the communication queue."""
        pass

    @abstractmethod
    def update_device_state(
        self, reported_state: DeviceState, desired_state: Union[DeviceState, None] = None
    ):
        """Update the device state in the communication queue."""
        pass

    @abstractmethod
    def close(self):
        """Close the communication handler and clean up resources."""
        pass

    def set_ttl(self, ttl_s: int, target_id: str):
        """Set the telemetry TTL"""
        new_ttl = time() + ttl_s
        self._target_ttls[target_id] = new_ttl
        logger.debug("Updated TTL to: %s for target: %s", new_ttl, target_id)

    def _is_ttl_active(self, target_id: str) -> bool:
        """Check if the TTL is still active for the target."""
        if target_id not in self._target_ttls:
            return False

        return time() < self._target_ttls[target_id]
