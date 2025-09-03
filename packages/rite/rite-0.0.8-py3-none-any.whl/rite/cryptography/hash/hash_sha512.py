# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - Cryptography - SHA512 Hash Module
========================================

Provides functionality to compute SHA512 hashes.

"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
import hashlib
import hmac
from typing import List

# Import | Libraries

# Import | Local Modules


# =============================================================================
# Constants
# =============================================================================

ASCII_NOT_CONFUSABLE = "ABCEFGHJKLMNPQRSTUWXYZ123456789"


# =============================================================================
# Functions
# =============================================================================


def sha512_hash(
    key,
    msg,
) -> str:
    """
    SHA512 hexdigest of `msg` salted with `key`. UTF-8 Encoded.
    """
    return hmac.new(
        key=key.encode("utf-8") if isinstance(key, str) else key,
        msg=msg.encode("utf-8") if isinstance(msg, str) else msg,
        digestmod=hashlib.sha512,
    ).hexdigest()


# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "sha512_hash",
]
