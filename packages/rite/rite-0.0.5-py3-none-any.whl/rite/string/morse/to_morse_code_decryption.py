def to_morse_code_decryption(text: str) -> str:
    """
    Decode Morse code back into text.
    Example: '.... . .-.. .-.. ---' -> 'HELLO'

    Parameters:
    text (str): The Morse code to decode.

    Returns
    -------
    str: The decoded text.
    """
    morse_dict = {
        ".-": "A",
        "-...": "B",
        "-.-.": "C",
        "-..": "D",
        ".": "E",
        "..-.": "F",
        "--.": "G",
        "....": "H",
        "..": "I",
        ".---": "J",
        "-.-": "K",
        ".-..": "L",
        "--": "M",
        "-.": "N",
        "---": "O",
        ".--.": "P",
        "--.-": "Q",
        ".-.": "R",
        "...": "S",
        "-": "T",
        "..-": "U",
        "...-": "V",
        ".--": "W",
        "-..-": "X",
        "-.--": "Y",
        "--..": "Z",
        "/": " ",
    }
    return "".join(morse_dict.get(code, "") for code in text.split(" "))
