def to_reverse_words_individually_case(text: str) -> str:
    """
    Reverses each word in the text individually.
    Example: 'Hello world' -> 'olleH dlrow'

    Parameters:
    text (str): The text to reverse.

    Returns
    -------
    str: The text with each word reversed individually.
    """
    return " ".join(word[::-1] for word in text.split())
