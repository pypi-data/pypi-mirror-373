# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite Time Module
======================

This module provides core utilities and classes for handling time-related
operations. It includes functionalities such as:
- Managing timestamps.
- Handling time durations.
- Managing and converting between timezones.
- Real-Time Clock (RTC) management for hardware integrations.

Dependencies:
- Standard Library: Built-in modules like `datetime` and `time`.
- Third-Party Libraries: Libraries like `pytz` for timezone support.

Components:
-----------
1. Timestamp
2. Duration
3. Timezone

"""


# =============================================================================
# Imports
# =============================================================================


# Import | Local Modules
from .duration import Duration
from .timestamp import Timestamp
from .timezone import Timezone

# =============================================================================
# Module Components
# =============================================================================


# Example of a placeholder module-level function or class
def example_module_function() -> None:
    """
    Example function for the Sense Core Time Module.

    This function demonstrates how module-level functionality can be implemented.
    """
    print("This is an example function in the Sense Core Time Module.")


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "Timestamp",
    "Duration",
    "Timezone",
]
