from __future__ import annotations

from datetime import datetime, timezone

ISO_FMT = "%Y-%m-%d"


def parse_cutoff(date_str: str) -> datetime:
    """Parse YYYY-MM-DD or ISO 8601. Naive dates => end of day UTC.

    Raises ValueError for invalid inputs.
    """
    s = date_str.strip()
    # Try simple date
    try:
        d = datetime.strptime(s[:10], ISO_FMT).replace(tzinfo=timezone.utc)
        if len(s) <= 10:  # naive date only
            return d.replace(hour=23, minute=59, second=59, microsecond=999999)
        # If there's time info, parse via ISO after normalizing Z
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        # last resort: fromisoformat
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)  # will raise ValueError if bad
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt


def is_prerelease(version: str) -> bool:
    from packaging.version import Version

    return Version(version).is_prerelease
