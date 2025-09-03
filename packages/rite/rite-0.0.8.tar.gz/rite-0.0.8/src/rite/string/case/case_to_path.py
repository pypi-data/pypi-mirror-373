def to_path_case(text: str) -> str:
    """
    Convert the text to path case.
    Words are separated by forward slashes, similar to a file path.
    Example: 'Hello World' -> 'hello/world'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text converted to path case.
    """
    words = text.split()
    return "/".join(word.lower() for word in words)
