"""Datetime utilities for the inventory tool."""

from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo


def format_utc_to_timezone(
    utc_timestamp: str, target_timezone: Optional[str] = None
) -> str:
    """Convert UTC timestamp to specified or local timezone for display.

    Args:
        utc_timestamp: UTC timestamp string in ISO format
        target_timezone: Optional timezone name (e.g., 'Australia/Sydney').
                        If None, uses local timezone.

    Returns:
        Formatted timestamp string in target or local timezone

    Raises:
        ValueError: If timestamp format is invalid
        ZoneInfoNotFoundError: If timezone is invalid
        AttributeError: If timestamp is None
    """
    # Parse the UTC timestamp
    utc_dt = datetime.fromisoformat(utc_timestamp)

    # Convert to target timezone or local timezone
    if target_timezone:
        target_dt = utc_dt.astimezone(ZoneInfo(target_timezone))
    else:
        target_dt = utc_dt.astimezone()

    # Format for display
    return target_dt.strftime('%Y-%m-%d %H:%M:%S %Z')


def format_utc_to_local(utc_timestamp: str) -> str:
    """Convert UTC timestamp to local timezone for display.

    Args:
        utc_timestamp: UTC timestamp string in ISO format

    Returns:
        Formatted timestamp string in local timezone
    """
    return format_utc_to_timezone(utc_timestamp)
