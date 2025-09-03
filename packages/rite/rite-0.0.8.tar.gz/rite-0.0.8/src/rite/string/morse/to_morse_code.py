def to_morse_code(text: str) -> str:
    """
    Convert the text to Morse code.
    Example: 'HELP' -> '.... . .-.. .--.'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text in Morse code.
    """
    morse_dict = {
        "A": ".-",
        "B": "-...",
        "C": "-.-.",
        "D": "-..",
        "E": ".",
        "F": "..-.",
        "G": "--.",
        "H": "....",
        "I": "..",
        "J": ".---",
        "K": "-.-",
        "L": ".-..",
        "M": "--",
        "N": "-.",
        "O": "---",
        "P": ".--.",
        "Q": "--.-",
        "R": ".-.",
        "S": "...",
        "T": "-",
        "U": "..-",
        "V": "...-",
        "W": ".--",
        "X": "-..-",
        "Y": "-.--",
        "Z": "--..",
        " ": "/",
    }
    return " ".join(morse_dict.get(char.upper(), "") for char in text)
