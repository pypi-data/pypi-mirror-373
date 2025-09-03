def to_alternate_uppercase_lowercase_case(text: str) -> str:
    """
    Alternates between uppercase and lowercase starting from the second
    character.
    Example: 'hello world' -> 'hElLo WoRlD'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text with alternating uppercase and lowercase letters.
    """
    return "".join(
        char.upper() if i % 2 else char.lower() for i, char in enumerate(text)
    )  # noqa E501
