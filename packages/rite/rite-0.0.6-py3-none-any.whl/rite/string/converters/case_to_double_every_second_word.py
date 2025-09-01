def to_double_every_second_word_case(text: str) -> str:
    """
    Doubles every second word in the text.
    Example: 'Hello world program' -> 'Hello Hello world world program
    program'

    Parameters:
    text (str): The text to process.

    Returns
    -------
    str: The text with every second word doubled.
    """
    words = text.split()
    return " ".join(
        word if i % 2 == 0 else word + " " + word
        for i, word in enumerate(words)
    )
