from datetime import (
    date,
    datetime,
    time,
    timedelta,
    timezone,
)
from dateutil.relativedelta import relativedelta
from struct import (
    pack,
    unpack,
    unpack_from,
)

from ..enums import PGOid
from .nullables import (
    read_nullable,
    write_nullable,
)


@read_nullable
def to_date(binary_data: bytes) -> date:
    """Unpack date value."""

    default_date = date(2000, 1, 1)

    return default_date + timedelta(
        days=unpack("!i", binary_data)[0]
    )


@write_nullable
def from_date(dtype_value: date, pg_oid: PGOid) -> bytes:
    """Pack date value."""

    return pack("!i", (dtype_value - date(2000, 1, 1)).days)


@read_nullable
def to_timestamp(binary_data: bytes) -> datetime:
    """Unpack timestamp value."""

    default_date = datetime(2000, 1, 1)

    return default_date + timedelta(
        microseconds=unpack("!q", binary_data)[0]
    )


@write_nullable
def from_timestamp(dtype_value: datetime, pg_oid: PGOid) -> bytes:
    """Pack timestamp value."""

    return unpack(
        "!q",
        int((dtype_value - datetime(2000, 1, 1)).total_seconds() * 1_000_000),
    )


@read_nullable
def to_timestamptz(binary_data: bytes) -> datetime:
    """Unpack timestamptz value."""

    return to_timestamp(binary_data).replace(
        tzinfo=timezone.utc
    )


@write_nullable
def from_timestamptz(dtype_value: datetime, pg_oid: PGOid) -> bytes:
    """Unpack timestamptz value."""

    return from_timestamp(dtype_value.astimezone(timezone.utc))


@read_nullable
def to_time(binary_data: bytes) -> time:
    """Unpack time value."""

    microseconds: int = unpack_from("!q", binary_data)[0]
    seconds, microsecond = divmod(microseconds, 1_000_000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    hours = hours % 24

    return time(
        hour=hours,
        minute=minutes,
        second=seconds,
        microsecond=microsecond,
    )


@write_nullable
def from_time(dtype_value: time, pg_oid: PGOid) -> bytes:
    """Pack time value to pgcopy binary format."""

    total_microseconds = (
        dtype_value.hour * 3600 * 1_000_000 +
        dtype_value.minute * 60 * 1_000_000 +
        dtype_value.second * 1_000_000 +
        dtype_value.microsecond
    )

    return pack("!q", total_microseconds)


@read_nullable
def to_timetz(binary_data: bytes) -> time:
    """Unpack timetz value."""

    time_notz: time = to_time(binary_data)
    tz_offset_sec: int = unpack("!i", binary_data[-4:])[0]
    tz_offset = timedelta(seconds=tz_offset_sec)

    return time_notz.replace(tzinfo=timezone(tz_offset))


@write_nullable
def from_timetz(dtype_value: time, pg_oid: PGOid) -> bytes:
    """Pack timetz value."""

    if dtype_value.tzinfo is None:
        raise ValueError("Time value must have timezone information")

    time_microseconds = (
        dtype_value.hour * 3600 * 1_000_000 +
        dtype_value.minute * 60 * 1_000_000 +
        dtype_value.second * 1_000_000 +
        dtype_value.microsecond
    )

    tz_offset = dtype_value.tzinfo.utcoffset(None)

    if tz_offset is None:
        raise ValueError("Cannot determine timezone offset")

    return pack("!qi", time_microseconds, int(tz_offset.total_seconds()))


@read_nullable
def to_interval(binary_data: bytes) -> relativedelta:
    """Unpack interval value."""

    microseconds, days, months = unpack("!qii", binary_data)

    return relativedelta(
        months=months,
        days=days,
        microseconds=microseconds
    )


@write_nullable
def from_interval(dtype_value: relativedelta, pg_oid: PGOid) -> bytes:
    """Pack interval value."""

    hours = dtype_value.hours or 0
    minutes = dtype_value.minutes or 0
    seconds = dtype_value.seconds or 0
    microseconds = dtype_value.microseconds or 0

    total_microseconds = (
        hours * 3600 * 1_000_000 +
        minutes * 60 * 1_000_000 +
        seconds * 1_000_000 +
        microseconds
    )

    return pack(
        "!qii",
        total_microseconds,
        dtype_value.days or 0,
        dtype_value.months or 0,
    )
