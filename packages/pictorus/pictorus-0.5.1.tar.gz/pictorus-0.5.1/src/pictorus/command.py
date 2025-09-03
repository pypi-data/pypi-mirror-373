from dataclasses import asdict, dataclass
from typing import Optional, Union
from enum import Enum

from .logging_utils import get_logger

logger = get_logger()


class DeployTargetType(Enum):
    """Supported deployment targets for pictorus apps"""

    PROCESS = "process"
    EMBEDDED = "embedded"


class CmdType(Enum):
    """Supported commands for the device command topic"""

    UPDATE_APP = "UPDATE_APP"
    SET_LOG_LEVEL = "SET_LOG_LEVEL"
    UPLOAD_LOGS = "UPLOAD_LOGS"
    SET_TELEMETRY_TLL = "SET_TELEMETRY_TTL"
    WEBRTC_OFFER = "WEBRTC_OFFER"
    RUN_APP = "RUN_APP"
    UNKNOWN = "UNKNOWN"


class DeployTarget:
    """Base class for command targets"""

    def __init__(self, data: dict):
        if "type" not in data or "id" not in data:
            logger.warning("Received invalid command target: %s", data)
            raise ValueError("Invalid command target")

        self.id = data["id"]
        self.type = DeployTargetType(data["type"])
        self.options = data.get("options", {})

    def to_dict(self):
        return {"id": self.id, "type": self.type.value, "options": self.options}


@dataclass
class Command:
    type: CmdType
    data: dict
    target_id: str
    id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Command":
        if "type" not in data or "data" not in data:
            logger.warning("Received invalid command: %s", data)
            raise ValueError("Invalid command: missing type or data")

        id = data.get("id")
        if not isinstance(id, str) and id is not None:
            logger.warning("Command id is not a string: %s", id)
            raise ValueError(f"Invalid command id: {id}")

        type = CmdType(data["type"])
        payload_data = data["data"]
        if not isinstance(payload_data, dict):
            logger.warning("Command data is not a dictionary: %s", payload_data)
            raise ValueError("Invalid command data")

        # Targets can be passed in as a full object or just an id
        target_id: Union[str, None] = None
        if "target" in data:
            target_id = data["target"].get("id")
        else:
            target_id = data.get("target_id")

        if target_id is None:
            logger.warning("Received command with no target")
            raise ValueError("Invalid command: missing target_id")

        return cls(id=id, type=type, data=payload_data, target_id=target_id)

    def to_dict(self) -> dict:
        # We need special to_dict methods for some of these dataclasses to ensure
        # that the enum values are serialized as strings. If we keep running into
        # this we could use a custom JSON encoder instead.

        data = asdict(self)
        data["type"] = self.type.value
        return data


class StatusCode(Enum):
    """Status of a command result"""

    SUCCESS = "OK"
    ERROR = "ERR"


@dataclass
class CommandResult:
    type: CmdType  # Type of the command that originated this result
    status: StatusCode
    id: Optional[str] = None  # ID of the command that originated this result
    data: Optional[dict] = None

    def to_dict(self) -> dict:
        data = asdict(self)
        data["status"] = self.status.value
        data["type"] = self.type.value
        return data
