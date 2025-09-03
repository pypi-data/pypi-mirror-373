def to_vowel_uppercase_case(text: str) -> str:
    """
    Convert all vowels in the text to uppercase.
    Example: 'Hello World' -> 'HEllO WOrld'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text with uppercase vowels.
    """
    vowels = "aeiou"
    return "".join(
        char.upper() if char.lower() in vowels else char for char in text
    )  # noqa E501
