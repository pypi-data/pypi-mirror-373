# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - Cryptography - SHA256 Hash Module
========================================

Provides functionality to compute SHA256 hashes.

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


def sha256_hash(
    key,
    msg,
) -> str:
    """
    SHA256 hexdigest of `msg` salted with `key`. UTF-8 Encoded.
    """
    return hmac.new(
        key=key.encode("utf-8") if isinstance(key, str) else key,
        msg=msg.encode("utf-8") if isinstance(msg, str) else msg,
        digestmod=hashlib.sha256,
    ).hexdigest()


# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "sha256_hash",
]
