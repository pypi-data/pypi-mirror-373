def to_camel_case(text: str) -> str:
    """
    Convert the text to camel case.
    Example: 'hello world' -> 'helloWorld'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text converted to camel case.
    """
    words = text.split()
    return words[0].lower() + "".join(
        word.capitalize() for word in words[1:]
    )  # noqa E501
