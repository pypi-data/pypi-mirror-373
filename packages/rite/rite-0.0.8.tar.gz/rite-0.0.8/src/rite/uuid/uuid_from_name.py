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


def from_name(namespace, name):
    """
    Generates a UUID based on a namespace and a name.

    Parameters:
        namespace (uuid.UUID): The namespace UUID.
        name (str): The name from which to generate the UUID.

    Returns
    -------
        uuid.UUID: A UUID generated from the namespace and name.
    """
    return uuid.uuid5(namespace, name)
