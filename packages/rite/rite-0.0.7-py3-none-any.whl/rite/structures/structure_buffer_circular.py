# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Circular Buffer
===============

A circular buffer (ring buffer) implementation that overwrites the oldest
entries when the buffer reaches its maximum capacity.

Classes:
--------
- CircularBuffer: A fixed-size buffer with circular indexing.

Features:
---------
- Append new elements, overwriting the oldest if the buffer is full.
- Retrieve all elements in the correct order.
- Check if the buffer is empty or full.

Usage:
------
    buffer = CircularBuffer(size=5)
    buffer.append(1)
    buffer.append(2)
    print(buffer.get_all())  # Outputs: [1, 2]
    buffer.append(3)
    buffer.append(4)
    buffer.append(5)
    print(buffer.get_all())  # Outputs: [1, 2, 3, 4, 5]
    buffer.append(6)
    print(buffer.get_all())  # Outputs: [6, 2, 3, 4, 5]

"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
from typing import Any, List, Optional

# Import | Libraries

# Import | Local Modules


# =============================================================================
# Classes
# =============================================================================


class CircularBuffer:
    """
    CircularBuffer Class
    ====================

    A fixed-size buffer that overwrites the oldest data when full.

    Attributes
    ----------
    -----------
    size : int
        The maximum number of elements the buffer can hold.
    buffer : List[Optional[Any]]
        The internal list storing buffer elements.
    index : int
        The current index for the next write operation.
    full : bool
        Indicates if the buffer has reached its maximum capacity.

    Methods
    -------
    --------
    append(value: Any) -> None:
        Adds a value to the buffer, overwriting the oldest element if full.
    get_all() -> List[Optional[Any]]:
        Retrieves all elements in the buffer in the correct order.
    is_empty() -> bool:
        Checks if the buffer is empty.
    is_full() -> bool:
        Checks if the buffer is full.
    """

    def __init__(self, size: int) -> None:
        """
        Initializes a CircularBuffer instance.

        Parameters:
        -----------
        size : int
            The maximum number of elements the buffer can hold.
        """
        if size <= 0:
            raise ValueError("Buffer size must be a positive integer.")
        self.size = size
        self.buffer: List[Optional[Any]] = [None] * size
        self.index = 0
        self.full = False

    def __repr__(self) -> str:
        """
        Returns a string representation of the CircularBuffer.

        Returns
        -------
        --------
        str:
            A string describing the buffer contents and state.
        """
        return (
            f"CircularBuffer(\n"
            f"    size={self.size},\n"
            f"    buffer={self.get_all()},\n"
            f"    full={self.full}\n"
            f")"
        )

    def append(self, value: Any) -> None:
        """
        Adds a value to the buffer. Overwrites the oldest element if the
        buffer is full.

        Parameters:
        -----------
        value : Any
            The value to add to the buffer.
        """
        self.buffer[self.index] = value
        self.index = (self.index + 1) % self.size
        # Mark the buffer as full if we've looped back to the start
        self.full = self.full or self.index == 0

    def get_all(self) -> List[Optional[Any]]:
        """
        Retrieves all elements in the buffer in the correct order.

        Returns
        -------
        --------
        List[Optional[Any]]:
            A list of elements in the buffer, ordered from the oldest to the
            newest.
        """
        if self.full:
            return self.buffer[self.index :] + self.buffer[: self.index]
        return self.buffer[: self.index]

    def is_empty(self) -> bool:
        """
        Checks if the buffer is empty.

        Returns
        -------
        --------
        bool:
            True if the buffer is empty, False otherwise.
        """
        return not self.full and self.index == 0

    def is_full(self) -> bool:
        """
        Checks if the buffer is full.

        Returns
        -------
        --------
        bool:
            True if the buffer is full, False otherwise.
        """
        return self.full


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "CircularBuffer",
]


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Create a circular buffer with a size of 5
    buffer = CircularBuffer(size=5)

    # Append values and display the buffer contents
    buffer.append(1)
    buffer.append(2)
    print(buffer.get_all())  # Outputs: [1, 2]

    buffer.append(3)
    buffer.append(4)
    buffer.append(5)
    print(buffer.get_all())  # Outputs: [1, 2, 3, 4, 5]

    # Overwrite the oldest values
    buffer.append(6)
    buffer.append(7)
    print(buffer.get_all())  # Outputs: [6, 7, 3, 4, 5]

    # Check buffer state
    print("Is buffer full?", buffer.is_full())  # Outputs: True
    print("Is buffer empty?", buffer.is_empty())  # Outputs: False
