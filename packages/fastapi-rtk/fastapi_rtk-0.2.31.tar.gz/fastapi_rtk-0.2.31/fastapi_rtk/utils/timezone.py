from datetime import datetime, timezone

__all__ = ["ensure_tz_info", "validate_utc"]


def ensure_tz_info(dt: datetime | str) -> datetime:
    """Ensure that the datetime has a timezone info."""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def validate_utc(dt: datetime) -> datetime:
    """Validate that the datetime is in UTC."""
    if dt.tzinfo.utcoffset(dt) != timezone.utc.utcoffset(dt):
        raise ValueError("Timezone must be UTC")
    return dt
