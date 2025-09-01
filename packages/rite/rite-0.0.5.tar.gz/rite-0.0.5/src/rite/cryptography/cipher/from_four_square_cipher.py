from rite.cryptography.cipher import four_square_cipher_pair, generate_square


def from_four_square_cipher(encoded_text: str, key1: str, key2: str) -> str:
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
