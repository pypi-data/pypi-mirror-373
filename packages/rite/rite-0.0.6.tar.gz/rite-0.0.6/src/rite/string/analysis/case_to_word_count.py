def to_word_count_case(text: str) -> int:
    """
    Counts the number of words in the text.
    Example: 'Hello world' -> 2

    Parameters:
    text (str): The text to count words in.

    Returns
    -------
    int: The number of words in the text.
    """
    return len(text.split())
