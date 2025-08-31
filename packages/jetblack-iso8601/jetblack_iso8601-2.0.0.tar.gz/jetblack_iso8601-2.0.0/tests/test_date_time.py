"""Tests for JSON serialization"""

from datetime import datetime, timezone, timedelta

from jetblack_iso8601 import (
    iso8601_to_datetime,
    datetime_to_iso8601
)


def test_roundtrip() -> None:
    """Test for iso 8601"""
    for text in [
            '2014-01-01T23:28:56.782Z',
            '2014-02-01T09:28:56.321-10:00',
            '2014-02-01T09:28:56.321+06:00'
    ]:
        timestamp = iso8601_to_datetime(text)
        assert timestamp is not None
        roundtrip = datetime_to_iso8601(timestamp)
        assert text == roundtrip


def test_zulu_tz_winter() -> None:
    """Test for the zulu timezone"""
    timestamp = iso8601_to_datetime('2014-01-01T23:28:56.782Z')
    assert timestamp is not None
    assert timestamp.timetuple() == (2014, 1, 1, 23, 28, 56, 2, 1, -1)
    assert timestamp.tzinfo is timezone.utc


def test_zulu_tz_summer() -> None:
    """Test for the zulu timezone"""
    timestamp = iso8601_to_datetime('2014-08-01T23:28:56.782Z')
    assert timestamp is not None
    assert timestamp.timetuple() == (2014, 8, 1, 23, 28, 56, 4, 213, -1)
    assert timestamp.tzinfo is timezone.utc


def test_tz_offset() -> None:
    """Test for timezone offset"""
    timestamp = iso8601_to_datetime('2014-02-01T09:28:56.321-10:00')
    assert timestamp is not None
    assert timestamp.timetuple() == (2014, 2, 1, 9, 28, 56, 5, 32, -1)
    assert timestamp.tzinfo == timezone(timedelta(hours=-10))


def test_tz_offset_0() -> None:
    """Test for timezone offset"""
    timestamp = iso8601_to_datetime('2014-02-01T09:28:56.321+00:00')
    assert timestamp == datetime(
        2014, 2, 1, 9, 28, 56, 321000,
        timezone(timedelta(hours=0))
    )


def test_nanoseconds() -> None:
    """Test for nanoseconds"""
    timestamp = iso8601_to_datetime('2014-02-01T09:28:56.1234567-05:00')
    assert timestamp == datetime(
        2014, 2, 1, 9, 28, 56, 123456,
        timezone(timedelta(hours=-5))
    )


def test_seconds() -> None:
    """Test for seconds"""
    timestamp = iso8601_to_datetime('2000-01-31T12:15:32.00+00:00')
    assert timestamp == datetime(
        2000, 1, 31, 12, 15, 32, 0,
        timezone(timedelta(hours=0))
    )


def test_reverse_roundtrip() -> None:
    """Test roundtrip starting with datetime object"""
    expected = datetime(2000, 1, 31, 12, 15, 32).astimezone(timezone.utc)
    text = datetime_to_iso8601(expected)
    actual = iso8601_to_datetime(text)
    assert actual == expected
