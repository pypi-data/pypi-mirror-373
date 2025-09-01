def to_playfair_cipher(text: str, key: str) -> str:
    """
    Encodes text using the Playfair cipher.

    Parameters:
    text (str): The text to encode.
    key (str): The key for the Playfair cipher.

    Returns
    -------
    str: The encoded text.
    """

    def prepare_text(text):
        text = text.upper().replace("J", "I")
        prepared_text = ""
        i = 0
        while i < len(text):
            if i + 1 < len(text) and text[i] != text[i + 1]:
                prepared_text += text[i : i + 2]
                i += 2
            else:
                prepared_text += text[i] + "X"
                i += 1
        if len(prepared_text) % 2 != 0:
            prepared_text += "X"
        return prepared_text

    square = Cipher.create_playfair_square(key)
    prepared_text = prepare_text(text)
    encoded_text = ""

    for i in range(0, len(prepared_text), 2):
        encoded_text += Cipher.playfair_cipher_pair(
            prepared_text[i : i + 2], square, "encode"
        )

    return encoded_text
