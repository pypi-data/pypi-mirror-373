def to_reverse_words_case(text: str) -> str:
    """
    Reverse each individual word in the text.
    Example: 'Hello World' -> 'olleH dlroW'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text with each word reversed.
    """
    return " ".join(word[::-1] for word in text.split())
