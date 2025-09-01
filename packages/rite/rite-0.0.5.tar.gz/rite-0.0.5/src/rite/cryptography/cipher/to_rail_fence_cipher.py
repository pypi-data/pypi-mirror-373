def to_rail_fence_cipher(text: str, num_rails: int) -> str:
    """
    Encodes text using the Rail Fence cipher.

    Parameters:
    text (str): The text to encode.
    num_rails (int): The number of rails.

    Returns
    -------
    str: The encoded text.
    """
    fence = [[] for _ in range(num_rails)]
    rail = 0
    change = 1

    for char in text:
        fence[rail].append(char)
        rail += change

        if rail == num_rails - 1 or rail == 0:
            change = -change

    return "".join("".join(row) for row in fence)
