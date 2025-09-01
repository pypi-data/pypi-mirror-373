def to_spongebob_meme_case(text: str) -> str:
    """
    Alternates the case of each letter in a mocking manner, starting with
    uppercase.
    Example: 'spongebob case' -> 'SpOnGeBoB cAsE'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text in Spongebob Meme case.
    """
    return "".join(
        char.upper() if i % 2 else char.lower() for i, char in enumerate(text)
    )  # noqa E501
