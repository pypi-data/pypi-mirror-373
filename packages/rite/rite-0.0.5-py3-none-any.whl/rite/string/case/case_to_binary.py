def to_binary_case(text: str) -> str:
    """
    Convert the text to binary form.
    Example: 'AB' -> '01000001 01000010'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text in binary form.
    """
    return " ".join(format(ord(char), "08b") for char in text)
