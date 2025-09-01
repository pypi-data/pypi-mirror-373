def to_upper_first_letter_case(text: str) -> str:
    """
    Convert only the first letter of each word in the text to uppercase,
    the rest to lowercase.
    Example: 'hello world' -> 'Hello World'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text with the first letter of each word in uppercase.
    """
    return " ".join(
        word[0].upper() + word[1:].lower() if word else ""
        for word in text.split()
    )  # noqa E501
