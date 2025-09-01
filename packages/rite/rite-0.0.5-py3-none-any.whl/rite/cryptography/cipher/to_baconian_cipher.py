def to_baconian_cipher(text: str) -> str:
    """
    Encodes text using the Baconian cipher. Non-alphabetic characters are
    ignored.

    Parameters:
    text (str): The text to encode.

    Returns
    -------
    str: The encoded text using the Baconian cipher.
    """
    bacon_dict = {
        "a": "aaaaa",
        "b": "aaaab",
        "c": "aaaba",
        "d": "aaabb",
        "e": "aabaa",
        "f": "aabab",
        "g": "aabba",
        "h": "aabbb",
        "i": "abaaa",
        "j": "abaab",
        "k": "ababa",
        "l": "ababb",
        "m": "abbaa",
        "n": "abbab",
        "o": "abbba",
        "p": "abbbb",
        "q": "baaaa",
        "r": "baaab",
        "s": "baaba",
        "t": "baabb",
        "u": "babaa",
        "v": "babab",
        "w": "babba",
        "x": "babbb",
        "y": "bbaaa",
        "z": "bbaab",
    }
    return "".join(
        bacon_dict.get(char.lower(), "") for char in text if char.isalpha()
    )  # noqa E501
