def to_transposition_cipher(text: str, key: int) -> str:
    """
    Encodes text using a simple columnar transposition cipher.

    Parameters:
    text (str): The text to encode.
    key (int): The number of columns.

    Returns
    -------
    str: The encoded text.
    """
    return "".join(text[i::key] for i in range(key))
