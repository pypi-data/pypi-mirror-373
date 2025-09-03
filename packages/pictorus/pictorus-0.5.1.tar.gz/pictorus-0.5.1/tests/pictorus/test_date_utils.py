from datetime import datetime, timedelta, timezone
from pictorus.date_utils import utc_timestamp_ms


def test_time_utils_with_none():
    timestamp = utc_timestamp_ms()
    assert isinstance(timestamp, int)
    assert len(str(timestamp)) == 13  # Should be a 13-digit number representing milliseconds


def test_utc_timestamp_ms_with_specific_datetime():
    dt = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert utc_timestamp_ms(dt) == 1672531200000


def test_utc_timestamp_ms_with_naive_datetime():
    dt = datetime(2023, 1, 1, 0, 0, 0)
    assert utc_timestamp_ms(dt) == 1672531200000


def test_utc_timestamp_ms_with_different_timezone():
    dt = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone(timedelta(hours=-5)))
    assert utc_timestamp_ms(dt) == 1672549200000
