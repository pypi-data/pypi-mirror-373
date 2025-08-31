"""Tests for duration"""

from jetblack_iso8601.duration import (
    iso8601_to_timedelta,
    timedelta_to_iso8601
)


def test_full_with_days() -> None:
    """Test duration"""

    duration = 'P3Y2M1DT12H11M10S'
    value = iso8601_to_timedelta(duration)
    assert value is not None
    roundtrip = timedelta_to_iso8601(value)
    assert roundtrip == duration


def test_full_with_weeks() -> None:
    """Test duration"""

    duration = 'P3Y2M1WT12H11M10S'
    value = iso8601_to_timedelta(duration)
    assert value is not None
    roundtrip = timedelta_to_iso8601(value)
    assert roundtrip == duration


def test_date_only() -> None:
    """Test duration"""

    duration = 'P3Y2M1D'
    value = iso8601_to_timedelta(duration)
    assert value is not None
    roundtrip = timedelta_to_iso8601(value)
    assert roundtrip == duration


def test_time_only() -> None:
    """Test duration"""

    duration = 'PT12H11M10S'
    value = iso8601_to_timedelta(duration)
    assert value is not None
    roundtrip = timedelta_to_iso8601(value)
    assert roundtrip == duration


def test_negative() -> None:
    """Test duration"""

    duration = '-PT10M'
    value = iso8601_to_timedelta(duration)
    assert value is not None
    roundtrip = timedelta_to_iso8601(value)
    assert roundtrip == duration


def test_empty() -> None:
    """Test duration"""

    duration = '-P0Y0M0DT0H0M0S'
    value = iso8601_to_timedelta(duration)
    assert value is not None
    roundtrip = timedelta_to_iso8601(value)
    assert roundtrip == 'P0D'
