def to_repeated_letters_case(text: str) -> str:
    """
    Repeats each letter in the word based on its position.
    Example: 'Hello' -> 'Heelllllooooo'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text with each letter repeated based on its position.
    """
    return " ".join(
        "".join(char * (i + 1) for i, char in enumerate(word))
        for word in text.split()
    )  # noqa E501
