def to_dot_case(text: str) -> str:
    """
    Convert the text to dot case.
    Words are separated by dots.
    Example: 'Hello World' -> 'hello.world'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text converted to dot case.
    """
    words = text.split()
    return ".".join(word.lower() for word in words)
