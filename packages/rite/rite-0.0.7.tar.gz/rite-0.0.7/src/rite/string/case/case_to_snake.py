def to_snake_case(text: str) -> str:
    """
    Convert the text to snake case.
    Example: 'Hello World' -> 'hello_world'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text converted to snake case.
    """
    words = text.split()
    return "_".join(word.lower() for word in words)
