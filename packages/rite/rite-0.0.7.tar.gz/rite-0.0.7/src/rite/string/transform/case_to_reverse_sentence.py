def to_reversed_sentence_case(text: str) -> str:
    """
    Reverses the order of words in a sentence.
    Example: 'Hello world' -> 'world Hello'

    Parameters:
    text (str): The sentence to reverse.

    Returns
    -------
    str: The sentence with reversed word order.
    """
    return " ".join(reversed(text.split()))
