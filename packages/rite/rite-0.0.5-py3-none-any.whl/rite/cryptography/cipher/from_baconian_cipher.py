def from_baconian_cipher(encoded_text: str) -> str:
    """
    Decodes text from the Baconian cipher. Assumes the text contains
    only 'a' and 'b'.

    Parameters:
    encoded_text (str): The text to decode.

    Returns
    -------
    str: The decoded text from the Baconian cipher.
    """
    bacon_dict = {
        v: k
        for k, v in Cipher.to_baconian_cipher(
            "abcdefghijklmnopqrstuvwxyz"
        ).split()
    }  # noqa E501
    return "".join(
        bacon_dict.get(encoded_text[i : i + 5], "")
        for i in range(0, len(encoded_text), 5)
    )  # noqa E501
