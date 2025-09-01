def to_atbash_cipher(text: str) -> str:
    """
    Encodes and decodes text using the Atbash cipher (reversible).

    Parameters:
    text (str): The text to encode or decode.

    Returns
    -------
    str: The encoded or decoded text.
    """
    return text.translate(
        str.maketrans(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
            "ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba",
        )
    )
