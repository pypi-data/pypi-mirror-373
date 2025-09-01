# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Module
===================


"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
import time

# Import | Libraries

# Import | Local Modules


# =============================================================================
# Classes
# =============================================================================


def debounce(wait_time):
    """
    Decorator to debounce a function call.
    """

    def decorator(func):
        def wrapped(*args, **kwargs):
            time.sleep(wait_time)
            return func(*args, **kwargs)

        return wrapped

    return decorator
