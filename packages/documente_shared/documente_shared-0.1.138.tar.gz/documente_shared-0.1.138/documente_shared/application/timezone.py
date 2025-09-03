from datetime import datetime, timezone


def ensure_timezone(dt: datetime, tz=timezone.utc) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=tz)
    return dt
