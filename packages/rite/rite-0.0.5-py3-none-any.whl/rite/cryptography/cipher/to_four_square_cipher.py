from rite.cryptography.cipher.four_square_cipher_pair import (
    four_square_cipher_pair,
)
from rite.cryptography.cipher.generate_square import generate_square


def to_four_square_cipher(text: str, key1: str, key2: str) -> str:
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
