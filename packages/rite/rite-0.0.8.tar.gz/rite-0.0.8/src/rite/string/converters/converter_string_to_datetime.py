# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - String - String to Datetime Converter Module
===================================================

Provides functionality to convert strings to datetime values.

"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
from datetime import datetime, timezone
from typing import List, Optional

# Import | Libraries

# Import | Local Modules


# =============================================================================
# Functions
# =============================================================================


def convert_string_to_datetime(
    value: Optional[str],
) -> Optional[datetime]:
    """
    String to Datetime Converter
    ============================

    Convert a string to a timezone-aware datetime object (UTC).

    Parses a timestamp like '2024-12-11 11:42:34.049271+00' or ISO-ish strings.
    Returns None on blank or invalid input.

    Supports ISO 8601 format with optional timezone.
    Naive datetimes are converted to UTC.

    Args:
        value: The string to convert.

    Returns:
        A timezone-aware datetime object in UTC, or None.
    """
    if not value:
        return None

    s = str(value).strip()
    if not s or s.lower() in {"none", "null"}:
        return None

    # Normalize space→T so fromisoformat() accepts it with offset
    s = s.replace(" ", "T", 1) if " " in s and "T" not in s else s

    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        return None


# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "convert_string_to_datetime",
]


# def convert_string_to_datetime(value: Optional[str]) -> Optional[datetime]:
#     """
#     Convert a string to a timezone-aware datetime object.

#     Parse a timestamp like '2024-12-11 11:42:34.049271+00' or ISO-ish strings.
#     Returns None on blank/invalid.

#     Supports ISO 8601 format, optionally naive or UTC.

#     Returns:
#         datetime object or None
#     """
#     if not value or value.strip() == "":
#         return None

#     dt = parse_datetime(value)
#     if not dt:
#         return None

#     if is_naive(dt):
#         # Use current timezone, or utc fallback
#         tz = get_current_timezone()
#         return make_aware(dt, timezone=tz)
#     return dt
