# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - Cryptography - Caesar Cipher Module
==========================================

Provides functionality to encode and decode text using the Caesar cipher.

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


def encode_caesar_cipher(
    text: str,
    shift: int,
) -> str:
    """
    Encodes the text using a Caesar cipher with a given shift.
    Only alphabetic characters are shifted, others remain unchanged.

    Parameters:
    text (str): The text to encode.
    shift (int): The shift for the Caesar cipher.

    Returns
    -------
    str: The encoded text.
    """
    encoded_text = []
    for char in text:
        if char.isalpha():
            start = 65 if char.isupper() else 97
            encoded_text.append(
                chr((ord(char) - start + shift) % 26 + start),
            )
        else:
            encoded_text.append(char)
    return "".join(encoded_text)


# =============================================================================


def decode_caesar_cipher(
    encoded_text: str,
    shift: int,
) -> str:
    """
    Decodes the text from a Caesar cipher with a given shift.

    Parameters:
    encoded_text (str): The text to decode.
    shift (int): The shift used in the Caesar cipher.

    Returns
    -------
    str: The decoded text.

    """

    return encode_caesar_cipher(encoded_text, -shift)


# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "decode_caesar_cipher",
    "encode_caesar_cipher",
]
