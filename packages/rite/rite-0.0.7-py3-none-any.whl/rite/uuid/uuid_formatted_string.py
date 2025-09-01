# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - UUID Module
==================


"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
import uuid

# Import | Libraries

# Import | Local Modules


# =============================================================================
# Functions
# =============================================================================


def formatted_string(uuid_obj):
    """
    Returns a formatted string representation of the UUID.

    Parameters:
        uuid_obj (uuid.UUID): The UUID object.

    Returns
    -------
        str: A formatted string representation of the UUID.
    """
    return f"UUID: {str(uuid_obj)}, Version: {uuid_obj.version}, Variant: {uuid_obj.variant}"
