"""Turn the many date formats ATS APIs use into a plain ISO date."""

from __future__ import annotations

from datetime import date, datetime, timezone
from email.utils import parsedate_to_datetime


def to_date(value: str | float | None) -> str | None:
    """Return YYYY-MM-DD for ISO strings, RFC 822 dates or Unix times (s or ms), else None."""
    if value is None or value == "":
        return None
    text = str(value).strip()
    if text.isdigit():
        stamp = int(text)
        if stamp > 10**11:  # milliseconds (Lever)
            stamp //= 1000
        try:
            return datetime.fromtimestamp(stamp, tz=timezone.utc).date().isoformat()
        except (OverflowError, OSError, ValueError):
            return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        pass
    try:
        return date.fromisoformat(text[:10]).isoformat()
    except ValueError:
        pass
    try:
        return parsedate_to_datetime(text).date().isoformat()
    except (TypeError, ValueError, IndexError):
        return None
