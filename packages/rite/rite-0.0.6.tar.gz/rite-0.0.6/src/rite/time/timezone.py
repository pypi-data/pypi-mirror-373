# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Timezone Module
===============

This module provides the `Timezone` class for managing timezones and
performing timezone-related operations such as:
- Converting datetime objects between timezones.
- Retrieving the current time in a specific timezone.
- Listing all available timezones.

Dependencies:
- Libraries: `pytz` for timezone handling, `datetime` for date and time.

"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
from datetime import datetime
from typing import List

# Import | Libraries
import pytz

# Import | Local Modules


# =============================================================================
# Classes
# =============================================================================


class Timezone:
    """
    Timezone Class
    ==============

    Provides utilities for timezone management and conversion.

    Attributes
    ----------
    -----------
    timezone : pytz.timezone
        The timezone object representing the current timezone.

    Methods
    -------
    --------
    convert(dt: datetime, target_timezone: str) -> datetime:
        Converts a datetime object to a target timezone.
    now() -> datetime:
        Returns the current time in the handler's timezone.
    list_timezones() -> List[str]:
        Returns a list of all available timezones.
    """

    def __init__(
        self,
        timezone: str = "UTC",
    ) -> None:
        """
        Initializes the `Timezone` with the specified timezone.

        Parameters:
        -----------
        timezone : str, optional
            The name of the timezone (default: "UTC").

        Raises:
        -------
        pytz.UnknownTimeZoneError:
            If the timezone is not recognized.
        """
        try:
            self.timezone = pytz.timezone(timezone)
        except pytz.UnknownTimeZoneError as exc:
            raise pytz.UnknownTimeZoneError(
                f"Invalid timezone: {timezone}"
            ) from exc

    def convert(
        self,
        dt: datetime,
        target_timezone: str,
    ) -> datetime:
        """
        Converts a datetime object to a target timezone.

        Parameters:
        -----------
        dt : datetime
            The datetime object to convert.
        target_timezone : str
            The name of the target timezone.

        Returns
        -------
        --------
        datetime
            A new datetime object in the target timezone.

        Raises:
        -------
        pytz.UnknownTimeZoneError:
            If the target timezone is not recognized.
        """
        target_tz = pytz.timezone(target_timezone)
        return dt.astimezone(target_tz)

    def now(self) -> datetime:
        """
        Returns the current time in the handler's timezone.

        Returns
        -------
        --------
        datetime
            The current datetime in the handler's timezone.
        """
        return datetime.now(self.timezone)

    @staticmethod
    def list_timezones() -> List[str]:
        """
        Returns a list of all available timezones.

        Returns
        -------
        --------
        List[str]
            A list of timezone names supported by `pytz`.
        """
        return pytz.all_timezones

    def __str__(self) -> str:
        """
        Returns a string representation of the handler's timezone.

        Returns
        -------
        --------
        str
            The name of the current timezone.
        """
        return f"Current timezone: {self.timezone}"

    @staticmethod
    def get_timezone_from_abbreviation(abbreviation: str) -> str:
        """
        Returns the full timezone name for a given abbreviation.

        Parameters:
        -----------
        abbreviation : str
            The timezone abbreviation (e.g., "PST", "EST").

        Returns
        -------
        --------
        str
            The full timezone name.

        Raises:
        -------
        ValueError:
            If the abbreviation is not recognized.
        """
        timezone_map = {
            "PST": "America/Los_Angeles",
            "EST": "America/New_York",
            "CET": "Europe/Paris",
            # Add more as needed
        }
        if abbreviation not in timezone_map:
            raise ValueError(
                f"Unrecognized timezone abbreviation: {abbreviation}"
            )
        return timezone_map[abbreviation]


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "Timezone",
]


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Initialize the Timezone for UTC
    tz_handler = Timezone("UTC")
    print("Handler Timezone:", tz_handler)

    # Get the current time in UTC
    utc_now = tz_handler.now()
    print("Current UTC Time:", utc_now)

    # Convert UTC to another timezone
    local_time = tz_handler.convert(utc_now, "Europe/Amsterdam")
    print("Converted Time (Amsterdam):", local_time)

    # List all available timezones
    print(
        "Available Timezones:",
        # Display first 5 for brevity
        Timezone.list_timezones()[:5],
    )
