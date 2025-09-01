def to_sentence_case(text: str) -> str:
    """
    Convert the text to sentence case.
    Example: 'hello world. it's a test' -> 'Hello world. It's a test'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text converted to sentence case.
    """
    sentences = text.split(". ")
    return ". ".join(sentence.capitalize() for sentence in sentences)
