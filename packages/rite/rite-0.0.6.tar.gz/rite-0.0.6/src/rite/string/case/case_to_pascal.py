def to_pascal_case(text: str) -> str:
    """
    Convert the text to pascal case.
    Similar to camel case, but the first letter of each word is
    capitalized.
    Example: 'hello world' -> 'HelloWorld'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text converted to pascal case.
    """
    words = text.split()
    return "".join(word.capitalize() for word in words)
