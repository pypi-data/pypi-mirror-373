"""Date & time friendly functions."""

from __future__ import annotations
from datetime import datetime, date, timedelta, timezone
from typing import Optional


def now(tz: Optional[timezone] = None) -> datetime:
    """Return current datetime (tz-aware if tz provided)."""
    return datetime.now(tz=tz)


def today_str(fmt: str = "%Y-%m-%d") -> str:
    return date.today().strftime(fmt)


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    return dt.strftime(fmt)


def to_timestamp(dt: datetime) -> int:
    """Seconds since epoch (int)."""
    if dt.tzinfo is None:
        # assume naive as local
        return int(dt.timestamp())
    return int(dt.astimezone(timezone.utc).timestamp())


def from_timestamp(ts: int, tz: Optional[timezone] = None) -> datetime:
    if tz is None:
        return datetime.fromtimestamp(ts)
    return datetime.fromtimestamp(ts, tz)


def humanize_timedelta(delta: timedelta) -> str:
    seconds = int(delta.total_seconds())
    if seconds < 60:
        return f"{seconds} seconds"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minutes"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hours"
    days = hours // 24
    if days < 30:
        return f"{days} days"
    months = days // 30
    if months < 12:
        return f"{months} months"
    years = months // 12
    return f"{years} years"


def parse_iso(s: str) -> datetime:
    """
    Try to parse ISO-like datetime strings. Falls back to datetime.fromisoformat.
    """
    try:
        return datetime.fromisoformat(s)
    except Exception:
        # last-resort: try common formats
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                continue
        raise
