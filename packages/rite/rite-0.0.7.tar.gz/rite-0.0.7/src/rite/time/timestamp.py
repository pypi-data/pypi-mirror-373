# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Timestamp Module
================

This module provides the `Timestamp` class for handling and manipulating
timestamps in Python. It supports functionalities such as:
- Creating timestamps.
- Converting timestamps to and from UNIX format.
- Parsing timestamps from string representations.
- Adding or subtracting durations.
- Calculating differences between timestamps.

Dependencies:
- Standard Library: `datetime` for handling date and time.

"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
from datetime import datetime
from typing import Optional

# Import | Local Modules
from .duration import Duration
from .timezone import Timezone

# =============================================================================
# Classes
# =============================================================================


class Timestamp:
    """
    Timestamp Class
    ===============

    Represents a specific point in time with utilities for formatting,
    manipulation, and conversion.

    Attributes
    ----------
    -----------
    datetime : datetime
        The datetime object representing the timestamp.
    timezone : Timezone
        The `Timezone` object for handling timezone-specific operations.

    Methods
    -------
    --------
    to_unix() -> int:
        Converts the timestamp to UNIX format.
    from_unix(timestamp: int) -> "Timestamp":
        Creates a `Timestamp` object from a UNIX timestamp.
    parse(date_string: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> "Timestamp":
        Parses a date string into a `Timestamp` object based on the given
        format.
    add_duration(duration: "Duration") -> "Timestamp":
        Adds a `Duration` object to the timestamp.
    subtract_duration(duration: "Duration") -> "Timestamp":
        Subtracts a `Duration` object from the timestamp.
    difference(other: "Timestamp") -> "Duration":
        Calculates the difference between this timestamp and another as a
        `Duration`.
    to_iso8601() -> str:
        Converts the timestamp to an ISO 8601 formatted string.
    """

    def __init__(
        self,
        dt: Optional[datetime] = None,
        tz: Optional[str] = "UTC",
    ) -> None:
        """
        Initializes the `Timestamp` object.

        Parameters:
        -----------
        dt : Optional[datetime]
            A `datetime` object to initialize the timestamp. If not provided,
            the current date and time is used.
        tz : Optional[str]
            The timezone name (e.g., "UTC", "Europe/Amsterdam").
            Defaults to UTC.
        """
        self.timezone = Timezone(tz)
        self.datetime: datetime = (dt or datetime.now()).astimezone(
            self.timezone.timezone
        )

    def __str__(self) -> str:
        """
        Returns the ISO 8601 string representation of the timestamp.

        Returns
        -------
        --------
        str:
            ISO 8601 formatted string of the timestamp.
        """
        return self.to_iso8601()

    def to_iso8601(self) -> str:
        """
        Converts the timestamp to an ISO 8601 formatted string.

        Returns
        -------
        --------
        str:
            ISO 8601 formatted string of the timestamp.
        """
        return self.datetime.isoformat()

    def to_unix(self) -> int:
        """
        Converts the timestamp to UNIX format.

        Returns
        -------
        --------
        int
            The UNIX timestamp (seconds since the epoch).
        """
        return int(self.datetime.timestamp())

    @staticmethod
    def from_unix(
        timestamp: int,
        tz: Optional[str] = "UTC",
    ) -> "Timestamp":
        """
        Creates a `Timestamp` object from a UNIX timestamp.

        Parameters:
        -----------
        timestamp : int
            The UNIX timestamp to convert.
        tz : Optional[str]
            The timezone for the new `Timestamp` object (default: "UTC").

        Returns
        -------
        --------
        Timestamp
            A new `Timestamp` object.

        Raises:
        -------
        ValueError:
            If the timestamp is not valid.
        """
        if not isinstance(timestamp, int):
            raise ValueError("UNIX timestamp must be an integer.")
        try:
            dt = datetime.fromtimestamp(timestamp, Timezone(tz).timezone)
            return Timestamp(dt, tz)
            # return Timestamp(datetime.fromtimestamp(timestamp))
        except OverflowError as exc:
            raise ValueError("Timestamp out of valid range.") from exc

    @staticmethod
    def parse(
        date_string: str,
        fmt: str = "%Y-%m-%d %H:%M:%S",
        tz: Optional[str] = "UTC",
    ) -> "Timestamp":
        """
        Parses a date string into a `Timestamp` object based on the given
        format and optional timezone.

        Parameters:
        -----------
        date_string : str
            The date string to parse.
        fmt : str, optional
            The format of the date string (default: "%Y-%m-%d %H:%M:%S").
        tz : Optional[str]
            The timezone for the new `Timestamp` object (default: "UTC").

        Returns
        -------
        --------
        Timestamp
            A new `Timestamp` object.
        """
        dt = datetime.strptime(date_string, fmt)
        tzinfo = Timezone(tz).timezone
        return Timestamp(dt.replace(tzinfo=tzinfo), tz)

    def add_duration(
        self,
        duration: Duration,
    ) -> "Timestamp":
        """
        Adds a `Duration` object to the timestamp.

        Parameters:
        -----------
        duration : Duration
            The duration to add.

        Returns
        -------
        --------
        Timestamp
            The updated `Timestamp` object.
        """
        self.datetime += duration.td
        return self

    def subtract_duration(
        self,
        duration: Duration,
    ) -> "Timestamp":
        """
        Subtracts a `Duration` object from the timestamp.

        Parameters:
        -----------
        duration : Duration
            The duration to subtract.

        Returns
        -------
        --------
        Timestamp
            The updated `Timestamp` object.
        """
        self.datetime -= duration.td
        return self

    def add_duration_immutable(
        self,
        duration: Duration,
    ) -> "Timestamp":
        """
        Returns a new `Timestamp` object with the specified duration added.

        Parameters:
        -----------
        duration : Duration
            The duration to add.

        Returns
        -------
        --------
        Timestamp
            A new `Timestamp` object with the updated datetime.
        """
        new_datetime = self.datetime + duration.td
        return Timestamp(new_datetime)

    def subtract_duration_immutable(
        self,
        duration: Duration,
    ) -> "Timestamp":
        """
        Returns a new `Timestamp` object with the specified duration subtracted.

        Parameters:
        -----------
        duration : Duration
            The duration to subtract.

        Returns
        -------
        --------
        Timestamp
            A new `Timestamp` object with the updated datetime.
        """
        new_datetime = self.datetime - duration.td
        return Timestamp(new_datetime)

    def difference(
        self,
        other: "Timestamp",
    ) -> Duration:
        """
        Calculates the difference between this timestamp and another as
        a `Duration`.

        Parameters:
        -----------
        other : Timestamp
            The other `Timestamp` object to compare.

        Returns
        -------
        --------
        Duration
            The difference between the two timestamps as a `Duration` object.
        """
        return Duration((self.datetime - other.datetime).total_seconds())

    def convert_to_timezone(
        self,
        target_timezone: str,
    ) -> "Timestamp":
        """
        Converts the timestamp to a target timezone.

        Parameters:
        -----------
        target_timezone : str
            The name of the target timezone.

        Returns
        -------
        --------
        Timestamp
            A new `Timestamp` object in the target timezone.
        """
        target_tzinfo = Timezone(target_timezone).timezone
        converted_dt = self.datetime.astimezone(target_tzinfo)
        return Timestamp(converted_dt, target_timezone)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "Timestamp",
]


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":

    # Create a timestamp for the current time
    ts = Timestamp()
    print("Current Timestamp:", ts)
    print("UNIX Time:", ts.to_unix())
    print("Current Timestamp in ISO 8601:", ts.to_iso8601())

    # Convert UNIX timestamp to ISO 8601
    unix_ts = Timestamp.from_unix(1735689599)
    print("UNIX Timestamp in ISO 8601:", unix_ts.to_iso8601())

    # Parse a date string and convert to ISO 8601
    parsed_ts = Timestamp.parse("2024-12-31 23:59:59", tz="Europe/Amsterdam")
    print("Parsed Timestamp in ISO 8601:", parsed_ts.to_iso8601())
