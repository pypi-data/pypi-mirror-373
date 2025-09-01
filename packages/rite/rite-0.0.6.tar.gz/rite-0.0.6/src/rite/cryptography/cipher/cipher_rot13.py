# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - Cryptography - Rot13 Cipher Module
=========================================

Provides functionality to encode and decode text using the Rot13 cipher.

"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
from typing import List

# Import | Libraries

# Import | Local Modules


# =============================================================================
# Functions
# =============================================================================


def encode_rot13_cipher(text: str) -> str:
    """
    Encodes and decodes text using the Rot13 cipher (reversible).

    Parameters:
    text (str): The text to encode or decode.

    Returns
    -------
    str: The encoded or decoded text.
    """
    return text.translate(
        str.maketrans(
            "ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz",
            "NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm",
        )
    )


# =============================================================================


def decode_rot13_cipher(text: str) -> str:
    """
    Decodes text using the Rot13 cipher.

    Parameters:
    text (str): The text to decode.

    Returns
    -------
    str: The decoded text.
    """
    return encode_rot13_cipher(text)


# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "decode_rot13_cipher",
    "encode_rot13_cipher",
]
