def to_hexadecimal_case(text: str) -> str:
    """
    Convert the text to hexadecimal form.
    Example: 'AB' -> '41 42'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text in hexadecimal form.
    """
    return " ".join(format(ord(char), "x") for char in text)
