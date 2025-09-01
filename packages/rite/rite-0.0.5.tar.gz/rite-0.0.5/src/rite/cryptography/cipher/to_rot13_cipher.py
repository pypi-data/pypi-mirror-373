def to_rot13_cipher(text: str) -> str:
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
