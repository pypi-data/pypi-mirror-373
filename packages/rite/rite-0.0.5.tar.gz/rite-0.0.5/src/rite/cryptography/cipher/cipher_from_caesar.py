from .cipher_to_caesar import to_caesar_cipher


def from_caesar_cipher(encoded_text: str, shift: int) -> str:
    """
    Decodes the text from a Caesar cipher with a given shift.

    Parameters:
    encoded_text (str): The text to decode.
    shift (int): The shift used in the Caesar cipher.

    Returns
    -------
    str: The decoded text.
    """
    return to_caesar_cipher(encoded_text, -shift)
