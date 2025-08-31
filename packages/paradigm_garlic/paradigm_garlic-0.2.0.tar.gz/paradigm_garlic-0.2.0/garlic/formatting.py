from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    import tooltime


TIMESTAMP_SUFFIX = {
    'NTZ': 'TIMESTAMP_NTZ',
    'LTZ': 'TIMESTAMP_LTZ',
    'TZ': 'TIMESTAMP_TZ',
}


def format_timestamp(
    dt: tooltime.Timestamp,
    *,
    timestamp_type: typing.Literal['NTZ', 'LTZ', 'TZ'] = 'NTZ',
    timezone: str = 'utc',
) -> str:
    """
    Format datetime as a Snowflake timestamp literal:
      '2025-08-30T14:03:22Z'::TIMESTAMP_NTZ

    Rules:
      - If dt is naive and utc=False -> raise.
      - If dt is naive and utc=True  -> tag as UTC.
      - For NTZ/LTZ: convert to UTC and emit 'Z'.
      - For TZ: preserve the original offset if present.
    """
    import datetime
    import tooltime

    if timezone != 'utc':
        raise ValueError("Only timezone='utc' is supported")

    if not isinstance(dt, datetime.datetime):
        dt = tooltime.timestamp_to_datetime(dt)

    if dt.tzinfo is None:
        if timezone != 'utc':
            raise ValueError(
                "datetime has no timezone, either 1) use timezone='utc' or 2) add tz with dt.replace(tzinfo=datetime.timezone.utc)",
            )
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    else:
        if timezone == 'utc' and dt.tzinfo != datetime.timezone.utc:
            raise Exception('utc=True but datetime is not UTC')

    if timestamp_type in ('NTZ', 'LTZ'):
        dt_utc = dt.astimezone(datetime.timezone.utc)
        s = dt_utc.isoformat(timespec='microseconds')
        if s.endswith('+00:00'):
            s = s[:-6] + 'Z'
    elif timestamp_type == 'TZ':
        s = dt.isoformat(timespec='microseconds')
    else:
        raise ValueError(f'Invalid timestamp_type: {timestamp_type!r}')

    return "'" + s + "'::" + TIMESTAMP_SUFFIX[timestamp_type]
