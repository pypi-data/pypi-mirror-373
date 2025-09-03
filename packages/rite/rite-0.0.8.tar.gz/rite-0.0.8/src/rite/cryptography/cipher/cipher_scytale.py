# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - Cryptography - Scytale Cipher Module
===========================================

Provides functionality to encode and decode text using the Scytale cipher.

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


def encode_scytale_cipher(text: str, diameter: int) -> str:
    """
    Encodes text using the Scytale cipher.

    Parameters:
    text (str): The text to encode.
    diameter (int): The diameter (number of characters per turn) of the Scytale.

    Returns
    -------
    str: The encoded text.
    """
    if diameter <= 0:
        return text

    padded_text = text + " " * ((diameter - len(text) % diameter) % diameter)
    encoded_text = [""] * diameter

    for i, char in enumerate(padded_text):
        encoded_text[i % diameter] += char

    return "".join(encoded_text)


# =============================================================================


def decode_scytale_cipher(encoded_text: str, diameter: int) -> str:
    """
    Decodes text from the Scytale cipher.

    Parameters:
    encoded_text (str): The text to decode.
    diameter (int): The diameter used in the Scytale cipher.

    Returns
    -------
    str: The decoded text.
    """
    if diameter <= 0:
        return encoded_text

    num_columns = len(encoded_text) // diameter
    decoded_text = [""] * num_columns

    for i, char in enumerate(encoded_text):
        decoded_text[i // diameter] += char

    return "".join(decoded_text).rstrip()


# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "decode_scytale_cipher",
    "encode_scytale_cipher",
]
