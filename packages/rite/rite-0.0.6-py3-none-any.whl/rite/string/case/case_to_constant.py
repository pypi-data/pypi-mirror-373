def to_constant_case(text: str) -> str:
    """
    Convert the text to constant case.
    Capitalizes each word and joins them with underscores, creating
    a format commonly used for constants.
    Example: 'Hello World' -> 'HELLO_WORLD'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text converted to constant case.
    """
    words = text.split()
    return "_".join(word.upper() for word in words)
