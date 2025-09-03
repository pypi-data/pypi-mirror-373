# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - Cryptography - Playfair Cipher Module
===========================================

Provides functionality to encode and decode text using the Playfair cipher.

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


def create_playfair_square(key: str):
    """
    Create a Playfair square with a given key.
    """
    alphabet = (
        "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # J is omitted in traditional Playfair
    )
    key = "".join(dict.fromkeys(key.upper()))
    # key = "".join(sorted(set(key.upper()), key=lambda x: key.index(x)))
    key += "".join([c for c in alphabet if c not in key])
    return [key[i : i + 5] for i in range(0, 25, 5)]


# =============================================================================


def playfair_cipher_pair(pair, square, mode="encode"):
    """
    Cipher a pair of letters using the Playfair square.
    """

    def find_position(c):
        for row in square:
            if c in row:
                return square.index(row), row.index(c)

    pos1 = find_position(pair[0])
    pos2 = find_position(pair[1])

    if pos1[0] == pos2[0]:  # Same row
        col_shift = 1 if mode == "encode" else -1
        return (
            square[pos1[0]][(pos1[1] + col_shift) % 5]
            + square[pos2[0]][(pos2[1] + col_shift) % 5]
        )
    elif pos1[1] == pos2[1]:  # Same column
        row_shift = 1 if mode == "encode" else -1
        return (
            square[(pos1[0] + row_shift) % 5][pos1[1]]
            + square[(pos2[0] + row_shift) % 5][pos2[1]]
        )
    else:  # Rectangle
        return square[pos1[0]][pos2[1]] + square[pos2[0]][pos1[1]]


# =============================================================================


def encode_playfair_cipher(text: str, key: str) -> str:
    """
    Encodes text using the Playfair cipher.

    Parameters:
    text (str): The text to encode.
    key (str): The key for the Playfair cipher.

    Returns
    -------
    str: The encoded text.
    """

    def prepare_text(text):
        text = text.upper().replace("J", "I")
        prepared_text = ""
        i = 0
        while i < len(text):
            if i + 1 < len(text) and text[i] != text[i + 1]:
                prepared_text += text[i : i + 2]
                i += 2
            else:
                prepared_text += text[i] + "X"
                i += 1
        if len(prepared_text) % 2 != 0:
            prepared_text += "X"
        return prepared_text

    square = create_playfair_square(key)
    prepared_text = prepare_text(text)
    encoded_text = ""

    for i in range(0, len(prepared_text), 2):
        encoded_text += playfair_cipher_pair(
            prepared_text[i : i + 2], square, "encode"
        )

    return encoded_text


# =============================================================================


def decode_playfair_cipher(encoded_text: str, key: str) -> str:
    """
    Decodes text from the Playfair cipher.

    Parameters:
    encoded_text (str): The text to decode.
    key (str): The key for the Playfair cipher.

    Returns
    -------
    str: The decoded text.
    """
    square = create_playfair_square(key)
    decoded_text = ""

    for i in range(0, len(encoded_text), 2):
        decoded_text += playfair_cipher_pair(
            encoded_text[i : i + 2], square, "decode"
        )

    return decoded_text


# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "decode_playfair_cipher",
    "encode_playfair_cipher",
]
