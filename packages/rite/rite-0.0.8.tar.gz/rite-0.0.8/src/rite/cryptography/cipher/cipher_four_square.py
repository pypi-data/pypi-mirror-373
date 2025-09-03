# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - Cryptography - Four-Square Cipher Module
===============================================

Provides functionality to encode and decode text using the Four-Square cipher.

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


def generate_square(key: str):
    """
    Generate a 5x5 matrix for the Four-Square cipher using a key.
    """
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # Typically J is omitted
    key = "".join(sorted(set(key.upper()), key=lambda x: key.index(x)))
    key += "".join([c for c in alphabet if c not in key])
    return [key[i : i + 5] for i in range(0, 25, 5)]


def four_square_cipher_pair(pair, square1, square2, mode="encode"):
    """
    Cipher a pair of letters using the Four-Square squares.
    """

    def find_position(letter, square):
        for row in square:
            if letter in row:
                return square.index(row), row.index(letter)

    # Find positions in the standard square
    pos1 = find_position(pair[0], square1)
    pos2 = find_position(pair[1], square2)

    if mode == "encode":
        return square2[pos1[0]][pos2[1]] + square1[pos2[0]][pos1[1]]
    else:  # mode == 'decode'
        return square1[pos1[0]][pos2[1]] + square2[pos2[0]][pos1[1]]


def encode_four_square_cipher(
    text: str,
    key1: str,
    key2: str,
) -> str:
    """
    Encodes text using the Four-Square cipher.

    Parameters:
    text (str): The text to encode.
    key1 (str): The first key for the Four-Square cipher.
    key2 (str): The second key for the Four-Square cipher.

    Returns
    -------
    str: The encoded text.
    """
    square1 = generate_square(key1)
    square2 = generate_square(key2)
    standard_square = generate_square("")

    text = text.upper().replace("J", "I")
    if len(text) % 2 != 0:
        text += "X"

    encoded_text = ""

    for i in range(0, len(text), 2):
        encoded_text += four_square_cipher_pair(
            text[i : i + 2],
            standard_square,
            standard_square,
            mode="encode",
        )

    return encoded_text


def decode_four_square_cipher(encoded_text: str, key1: str, key2: str) -> str:
    """
    Decodes text from the Four-Square cipher.

    Parameters:
    encoded_text (str): The text to decode.
    key1 (str): The first key used in the Four-Square cipher.
    key2 (str): The second key used in the Four-Square cipher.

    Returns
    -------
    str: The decoded text.
    """
    square1 = generate_square(key1)
    square2 = generate_square(key2)
    standard_square = generate_square("")

    decoded_text = ""

    for i in range(0, len(encoded_text), 2):
        decoded_text += four_square_cipher_pair(
            encoded_text[i : i + 2], square1, square2, mode="decode"
        )

    return decoded_text


# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "four_square_cipher_pair",
    "encode_four_square_cipher",
    "decode_four_square_cipher",
]
