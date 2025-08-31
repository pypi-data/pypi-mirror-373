# jetblack-iso8601

Support for ISO8601
(read the [docs](https://rob-blackbourn.github.io/jetblack-iso8601/)).

## Usage

### Timestamps

Timestamps can be parsed with `iso8601_to_datetime` and
converted to a string with `datetime_to_iso8601`.

```python
from jetblack_iso8601 import (
    iso8601_to_datetime,
    datetime_to_iso8601
)

text = '2014-02-01T09:28:56.321-10:00'
timestamp = iso8601_to_datetime(text)
roundtrip = datetime_to_iso8601(timestamp)
assert text == roundtrip
```

### Durations

Timestamps can be parsed with `iso8601_to_timedelta` and
converted to a string with `datetime_to_iso8601`.


```python
from jetblack_iso8601 import (
    iso8601_to_timedelta,
    timedelta_to_iso8601
)

text = 'P3Y2M1DT12H11M10S'
value = iso8601_to_timedelta(text)
roundtrip = timedelta_to_iso8601(value)
assert roundtrip == text
```
