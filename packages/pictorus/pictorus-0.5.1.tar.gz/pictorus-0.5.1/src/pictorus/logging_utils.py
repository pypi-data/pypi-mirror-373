"""Logger utilities"""

from enum import Enum
import logging
from datetime import datetime
import re

from pictorus.date_utils import utc_timestamp_ms
from pictorus.types import LogMessage

try:
    from backports.datetime_fromisoformat import MonkeyPatch  # pyright: ignore

    # Patch fromisoformat for Python < 3.7
    MonkeyPatch.patch_fromisoformat()
except ImportError:
    pass

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] - %(message)s", datefmt="%Y-%m-%dT%H:%M:%S%z"
)

# This is duplicated in the backend. Not sure if we want to do this here or
# just upload the raw logs and parse them in the backend.
LOG_PATTERN = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+(?:Z|[+-]\d{2}:\d{2})?) \[(?P<log_level>\w+)\] - (?P<message>.*)"  # noqa: E501
)

# The embedded log pattern for logging messages lacks the timestamp
EMBEDDED_LOG_PATTERN = re.compile(r"\[(?P<log_level>\w+)\] - (?P<message>.*)")  # noqa: E501


class TextFormat(Enum):
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


def printf(message: str, fmt: TextFormat):
    print(f"{fmt.value}{message}{TextFormat.ENDC.value}")


def get_logger():
    """Get logger with common formatting"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    return logger


def format_log_level(log_level: str):
    if log_level == "WARN":
        log_level = "warning"

    return log_level.lower()


def parse_log_entry(
    line: str, date_now: datetime, client_id: str, embedded_log: bool = False
) -> LogMessage:
    # The Linux log expects utc time as the first element, but this isn't available on
    # embedded systems, so package the date_now instead.
    # See initialize_logging() in udp_data_logger.rs in the main Pictorus repo
    # for more information about log formatting.
    match = EMBEDDED_LOG_PATTERN.match(line) if embedded_log else LOG_PATTERN.match(line)

    if match:
        log_entry = match.groupdict()
        timestamp = log_entry["timestamp"] if embedded_log is False else date_now.isoformat()
        # Older versions of datetime don't support the Z suffix
        if timestamp.endswith("Z"):
            timestamp = timestamp[:-1] + "+00:00"

        dt = datetime.fromisoformat(timestamp)
        return LogMessage(
            timestamp=utc_timestamp_ms(dt),
            level=format_log_level(log_entry["log_level"]),
            message=log_entry["message"],
        )

    return LogMessage(
        timestamp=utc_timestamp_ms(date_now),
        message=line,
    )
