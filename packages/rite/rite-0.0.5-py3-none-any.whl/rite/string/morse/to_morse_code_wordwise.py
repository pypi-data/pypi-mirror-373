def to_morse_code_wordwise(text: str) -> str:
    """
    Converts each word to Morse code, maintaining word boundaries.
    Example: 'Hi' -> '.... ..'

    Parameters:
    text (str): The text to convert.

    Returns
    -------
    str: The text with each word converted to Morse code.
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
    return " / ".join(
        " ".join(morse_dict.get(char.upper(), "") for char in word)
        for word in text.split()
    )
