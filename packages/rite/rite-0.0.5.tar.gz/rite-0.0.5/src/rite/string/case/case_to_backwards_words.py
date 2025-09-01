def to_backwards_words_case(text: str) -> str:
    """
    Reverse the order of characters in each word of the text.
    Example: 'Hello World' -> 'olleH dlroW'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text with each word reversed.
    """
    return " ".join(word[::-1] for word in text.split())
