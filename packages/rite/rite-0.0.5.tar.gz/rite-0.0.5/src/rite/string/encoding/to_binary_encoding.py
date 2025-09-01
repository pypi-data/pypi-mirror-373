def to_binary_encoding(text: str) -> str:
    """
    Encodes text to binary.

    Parameters:
    text (str): The text to encode.

    Returns
    -------
    str: The binary encoded text.
    """
    return " ".join(format(ord(char), "08b") for char in text)
