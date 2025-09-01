def to_slug_case(text: str) -> str:
    """
    Convert the text to slug case (URL-friendly format).
    Example: 'Hello World' -> 'hello-world'

    Parameters:
    text (str): The text to convert to slug case.

    Returns
    -------
    str: The text in slug case.
    """
    words = text.split()
    return "-".join(word.lower() for word in words)
