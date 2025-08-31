"""Serialization"""

from datetime import datetime, timezone, timedelta
import re
from typing import Optional

TZ_PATTERN = r'(?P<zulu>Z)|((?P<tz_sign>[+-])(?P<tz_hours>\d{2}):?(?P<tz_minutes>\d{2}))'
TIME_PATTERN = r'(?P<hours>\d{2}):(?P<minutes>\d{2}):(?P<seconds>\d{2})(\.(?P<fractions>\d+))?'
DATE_PATTERN = r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})'
PATTERN = re.compile(f'^{DATE_PATTERN}(T{TIME_PATTERN}({TZ_PATTERN})?)?$')


def iso8601_to_datetime(value: str) -> Optional[datetime]:
    """Parse an ISO 8601 datetime.

    Args:
        value (str): The ISO 8601 date string

    Returns:
        Optional[datetime]: A timestamp if the value could be parsed, otherwise
            None.
    """
    match = PATTERN.match(value)
    if match is None:
        return None

    parts = match.groupdict()

    year, month, day = (
        int(parts['year']), int(parts['month']), int(parts['day'])
    )

    hour, minute, second = (
        (0, 0, 0) if parts['hours'] is None
        else (
            int(parts['hours']), int(parts['minutes']), int(parts['seconds'])
        )
    )

    microsecond = (
        0 if parts['fractions'] is None
        else int(parts['fractions'][:6].ljust(6, '0'))
    )

    if parts['zulu']:
        tzinfo = timezone.utc
    elif parts['tz_sign']:
        offset = timedelta(
            hours=int(parts['tz_hours']),
            minutes=int(parts['tz_minutes'])
        )
        tzinfo = (
            timezone(offset) if parts['tz_sign'] == '+'
            else timezone(-offset)
        )
    else:
        tzinfo = None

    return datetime(
        year, month, day,
        hour, minute, second, microsecond,
        tzinfo
    )


def datetime_to_iso8601(timestamp: datetime) -> str:
    """Convert datetime to ISO 8601

    Args:
        timestamp (datetime): The timestamp

    Returns:
        str: The stringified ISO 8601 version of the timestamp
    """
    # pylint: disable=consider-using-f-string
    date_part = "{year:04d}-{month:02d}-{day:02d}".format(
        year=timestamp.year, month=timestamp.month, day=timestamp.day,
    )
    time_part = "{hour:02d}:{minute:02d}:{second:02d}.{millis:02d}".format(
        hour=timestamp.hour, minute=timestamp.minute, second=timestamp.second,
        millis=timestamp.microsecond // 1000
    )
    # pylint: enable=consider-using-f-string

    utcoffset = timestamp.utcoffset()
    if utcoffset is None or timestamp.tzinfo is timezone.utc:
        return f"{date_part}T{time_part}Z"

    tz_seconds = utcoffset.total_seconds()
    tz_sign = '-' if tz_seconds < 0 else '+'
    tz_minutes = int(abs(tz_seconds)) // 60
    tz_hours = tz_minutes // 60
    tz_minutes %= 60
    return f"{date_part}T{time_part}{tz_sign}{tz_hours:02d}:{tz_minutes:02d}"
