def to_reverse_word_order_case(text: str) -> str:
    """
    Reverses the order of words in the text.
    Example: 'Hello world' -> 'world Hello'

    Parameters:
    text (str): The text to reverse word order.

    Returns
    -------
    str: The text with reversed word order.
    """
    return " ".join(reversed(text.split()))
