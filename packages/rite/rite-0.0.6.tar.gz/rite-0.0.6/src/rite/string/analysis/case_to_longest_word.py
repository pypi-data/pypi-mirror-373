def to_longest_word_case(text: str) -> str:
    """
    Finds the longest word in the text.
    Example: 'This is a test' -> 'test'

    Parameters:
    text (str): The text to search.

    Returns
    -------
    str: The longest word in the text.
    """
    return max(text.split(), key=len)
