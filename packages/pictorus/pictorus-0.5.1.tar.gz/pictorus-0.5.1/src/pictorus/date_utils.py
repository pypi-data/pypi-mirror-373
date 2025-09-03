from typing import Union
from datetime import datetime, timezone


def utc_timestamp_ms(dt: Union[datetime, None] = None):
    if dt is None:
        dt = datetime.now(timezone.utc)

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return int(round(dt.timestamp() * 1000))
