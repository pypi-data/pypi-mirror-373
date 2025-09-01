def to_ascii_value_case(text: str) -> str:
    """
    Converts each character to its ASCII value.
    Example: 'AB' -> '65 66'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: A string of ASCII values for each character.
    """
    return " ".join(str(ord(char)) for char in text)
