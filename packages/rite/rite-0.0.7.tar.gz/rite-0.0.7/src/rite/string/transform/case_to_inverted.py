def to_inverted_case(text: str) -> str:
    """
    Invert the case of each letter in the text.

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text with inverted case.
    """
    return "".join(
        char.upper() if char.islower() else char.lower() for char in text
    )  # noqa E501
