# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Duration Module
===============

This module provides the `Duration` class for representing and manipulating
time intervals. It supports functionalities such as:
- Creating durations in seconds or days.
- Adding or subtracting durations.
- Converting durations to human-readable formats or other units (e.g., days).

Dependencies:
- Standard Library: `datetime` for handling date and time.

"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations


from datetime import timedelta

# Import | Standard Library
from typing import Union

# Import | Libraries

# Import | Local Modules


# =============================================================================
# Classes
# =============================================================================


class Duration:
    """
    Duration Class
    ==============

    Represents a time interval with utilities for formatting, manipulation,
    and conversion.

    Attributes
    ----------
    -----------
    td : timedelta
        The `timedelta` object representing the duration.

    Methods
    -------
    --------
    __str__() -> str:
        Returns a human-readable string representation of the duration.
    from_days(days: Union[int, float]) -> "Duration":
        Creates a `Duration` object from a number of days.
    to_days() -> float:
        Converts the duration to days.
    add(other: "Duration") -> "Duration":
        Adds another `Duration` object to this one.
    subtract(other: "Duration") -> "Duration":
        Subtracts another `Duration` object from this one.
    to_seconds() -> float:
        Returns the total duration in seconds.
    """

    def __init__(self, seconds: Union[int, float] = 0) -> None:
        """
        Initializes the `Duration` object.

        Parameters:
        -----------
        seconds : Union[int, float], optional
            The number of seconds for the duration (default: 0).
        """
        self.timedelta: timedelta = timedelta(seconds=seconds)

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the duration.

        Returns
        -------
        --------
        str
            A string in the format "{hours}h {minutes}m {seconds}s".
        """
        total_seconds = self.timedelta.total_seconds()
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if hours:
            parts.append(f"{int(hours)}h")
        if minutes:
            parts.append(f"{int(minutes)}m")
        if seconds:
            parts.append(f"{int(seconds)}s")

        return " ".join(parts) if parts else "0s"

    @staticmethod
    def from_days(days: Union[int, float]) -> "Duration":
        """
        Creates a `Duration` object from a number of days.

        Parameters:
        -----------
        days : Union[int, float]
            The number of days.

        Returns
        -------
        --------
        Duration
            A new `Duration` object.
        """
        if days < 0:
            raise ValueError("Days cannot be negative.")
        return Duration(seconds=days * 86400)

    def to_days(self) -> float:
        """
        Converts the duration to days.

        Returns
        -------
        --------
        float
            The total duration in days.
        """
        return self.timedelta.total_seconds() / 86400

    def add(self, other: "Duration") -> "Duration":
        """
        Adds another `Duration` object to this one.

        Parameters:
        -----------
        other : Duration
            The `Duration` object to add.

        Returns
        -------
        --------
        Duration
            The updated `Duration` object.
        """
        self.timedelta += other.td
        return self

    def subtract(self, other: "Duration") -> "Duration":
        """
        Subtracts another `Duration` object from this one.

        Parameters:
        -----------
        other : Duration
            The `Duration` object to subtract.

        Returns
        -------
        --------
        Duration
            The updated `Duration` object.
        """
        self.timedelta -= other.td
        return self

    def to_seconds(self) -> float:
        """
        Returns the total duration in seconds.

        Returns
        -------
        --------
        float
            The total duration in seconds.
        """
        return self.timedelta.total_seconds()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "Duration",
]


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":

    # Create a Duration of 3600 seconds (1 hour)
    duration = Duration(3600)
    print("Duration:", duration)

    # Create a Duration from 2 days
    duration_from_days = Duration.from_days(2)
    print("Duration from days:", duration_from_days)

    # Add two durations
    total_duration = duration.add(duration_from_days)
    print("Total Duration:", total_duration)

    # Convert to days
    print("Total Duration in days:", total_duration.to_days())

    # Subtract a duration (2 hours)
    remaining_duration = total_duration.subtract(Duration(7200))
    print("Remaining Duration:", remaining_duration)

    # Get total seconds
    print("Remaining Duration in seconds:", remaining_duration.to_seconds())
