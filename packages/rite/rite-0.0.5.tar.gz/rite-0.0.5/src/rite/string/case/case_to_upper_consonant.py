def to_consonant_uppercase_case(text: str) -> str:
    """
    Convert all consonants in the text to uppercase.
    Example: 'Hello World' -> 'hEllO wOrld'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text with uppercase consonants.
    """
    vowels = "aeiou"
    return "".join(
        char.upper() if char.lower() not in vowels else char for char in text
    )  # noqa E501
