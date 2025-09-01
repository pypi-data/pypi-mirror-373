# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - Cryptography - Rail Fence Cipher Module
==========================================

Provides functionality to encode and decode text using the Rail Fence cipher.

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


def encode_rail_fence_cipher(
    text: str,
    num_rails: int,
) -> str:
    """
    Encodes text using the Rail Fence cipher.

    Parameters:
    text (str): The text to encode.
    num_rails (int): The number of rails.

    Returns
    -------
    str: The encoded text.
    """
    fence = [[] for _ in range(num_rails)]
    rail = 0
    change = 1

    for char in text:
        fence[rail].append(char)
        rail += change

        if rail == num_rails - 1 or rail == 0:
            change = -change

    return "".join("".join(row) for row in fence)


# =============================================================================


def decode_rail_fence_cipher(
    encoded_text: str,
    num_rails: int,
) -> str:
    """
    Decodes text from the Rail Fence cipher.

    Parameters:
    encoded_text (str): The text to decode.
    num_rails (int): The number of rails.

    Returns
    -------
    str: The decoded text.
    """
    fence = [[] for _ in range(num_rails)]
    rail_lengths = [0] * num_rails
    rail = 0
    change = 1

    for _ in encoded_text:
        rail_lengths[rail] += 1
        rail += change
        if rail == num_rails - 1 or rail == 0:
            change = -change

    index = 0
    for i, length in enumerate(rail_lengths):
        fence[i] = list(encoded_text[index : index + length])
        index += length

    result = []
    rail = 0
    change = 1
    for _ in range(len(encoded_text)):
        result.append(fence[rail].pop(0))
        rail += change

        if rail == num_rails - 1 or rail == 0:
            change = -change

    return "".join(result)


# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "decode_rail_fence_cipher",
    "encode_rail_fence_cipher",
]
