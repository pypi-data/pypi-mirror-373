from dataclasses import dataclass
from abc import ABC, abstractmethod
import threading
import time
from typing import Dict, List, Union

from pictorus.command import CmdType, Command, CommandResult, DeployTarget, StatusCode
from pictorus.comms.comms_handler import CommsConfig, CommsHandler, TelemData
from pictorus.comms.data_queue import DataQueue, QueueConfig
from pictorus.constants import THREAD_SLEEP_TIME_S
from pictorus.logging_utils import get_logger
from pictorus.types import LogMessage

logger = get_logger()


@dataclass
class StreamingCommsConfig(CommsConfig):
    telem_publish_interval_s: float
    telem_batch_size: int
    telem_max_queue_size: int
    log_publish_interval_s: float
    log_batch_size: int
    log_max_queue_size: int


def _insert_telemetry(target_data: Dict[str, List], new_data: Dict[str, List]):
    for key, value in new_data.items():
        if key not in target_data:
            target_data[key] = []

        target_data[key].append(value)


def _trim_telemetry(target_data: Dict[str, List], max_size: int):
    for key in target_data:
        if len(target_data[key]) > max_size:
            target_data[key] = target_data[key][-max_size:]  # Keep only the last `max_size` entries


def _insert_logs(logs: List[LogMessage], new_logs: List[LogMessage]):
    logs.extend(new_logs)


def _trim_logs(logs: List[LogMessage], max_size: int):
    if len(logs) > max_size:
        logs[:] = logs[-max_size:]  # Keep only the last `max_size` entries


TelemQueueData = Dict[str, List]
LogQueueData = List[LogMessage]


class StreamingCommsHandler(CommsHandler, ABC):
    def __init__(self, config: StreamingCommsConfig) -> None:
        super().__init__(config)

        self._telem_data = DataQueue[TelemQueueData](
            QueueConfig[TelemQueueData](
                publish_interval_s=config.telem_publish_interval_s,
                publish_queue_size=config.telem_batch_size,
                max_queue_size=config.telem_max_queue_size,
                default_factory=dict,
                append_data=_insert_telemetry,
                # All telem should have a "utctime" key, so grab the length of that
                get_length=lambda data: len(data.get("utctime", [])),
                trim_data=_trim_telemetry,
            )
        )

        self._log_data = DataQueue[LogQueueData](
            QueueConfig[LogQueueData](
                publish_interval_s=config.log_publish_interval_s,
                publish_queue_size=config.log_batch_size,
                max_queue_size=config.log_max_queue_size,
                default_factory=list,
                append_data=_insert_logs,
                get_length=len,
                trim_data=_trim_logs,
            )
        )

        self._complete = threading.Event()

    def add_telemetry(self, data: TelemData) -> None:
        data.data["utctime"] = data.utc_time_ms
        self._telem_data.add_data(data.target_id, data.data)

    def add_log(self, log: LogMessage, target_id: str):
        self._log_data.add_data(target_id, [log])

    def close(self):
        self._complete.set()
        self._publish_all_logs()

    @abstractmethod
    def _publish_logs(self, target_id: str, logs: List[LogMessage]):
        """Publish logs over the communication channel."""
        pass

    @abstractmethod
    def _publish_telemetry(self, target_id: str, data: Dict[str, List]):
        """Publish telemetry data over the communication channel."""
        pass

    @abstractmethod
    def _publish_cmd_result(self, result: CommandResult, stream_id: Union[str, None] = None):
        """Publish command result over the communication channel."""
        pass

    @abstractmethod
    def _process_internal_cmd(
        self, cmd: Command, stream_id: Union[str, None] = None
    ) -> CommandResult:
        """Process an internal command intended for the handler itself."""
        pass

    def _check_publish_data(self):
        self._check_publish_telem()
        self._check_publish_logs()

        time.sleep(THREAD_SLEEP_TIME_S)

    def _check_publish_logs(self):
        should_publish = self._log_data.check_publish()
        if not should_publish:
            return

        self._publish_all_logs()

    def _publish_all_logs(self):
        try:
            for target_id in self._log_data.target_ids():
                if not self._is_ttl_active(target_id):
                    continue

                log_entries = self._log_data.load_data(target_id)
                if not log_entries:
                    logger.debug("No logs to publish")
                    continue

                logger.debug("Publishing %s logs", len(log_entries))
                self._publish_logs(target_id, log_entries)
        except Exception as e:
            logger.error("Error publishing logs: %s", e, exc_info=True)

    def _check_publish_telem(self):
        should_publish = self._telem_data.check_publish()
        if not should_publish:
            return

        for target_id in self._telem_data.target_ids():
            if not self._is_ttl_active(target_id):
                continue

            data = self._telem_data.load_data(target_id)
            if not data:
                continue

            self._publish_telemetry(target_id, data)

    def _on_cmd_request(self, cmd_data: dict, stream_id: Union[str, None] = None):
        logger.info("Received command request: %s", cmd_data)
        try:
            cmd = Command.from_dict(cmd_data)
            target_data = cmd_data.get("target")
            target = DeployTarget(target_data) if target_data else None
        except Exception as e:
            logger.error("Failed to parse command: %s", e, exc_info=True)
            result = CommandResult(
                id=cmd_data.get("id") or "",
                type=cmd_data.get("type") or CmdType.UNKNOWN,
                status=StatusCode.ERROR,
            )
        else:
            if cmd.type == CmdType.SET_TELEMETRY_TLL:
                result = self._process_internal_cmd(cmd, stream_id=stream_id)
            else:
                result = self._config.process_cmd(cmd, target)

        logger.info("Command result: %s", result)
        if result:
            self._publish_cmd_result(result, stream_id=stream_id)
