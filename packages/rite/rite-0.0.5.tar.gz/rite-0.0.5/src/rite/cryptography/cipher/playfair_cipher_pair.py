def playfair_cipher_pair(pair, square, mode="encode"):
    """
    Cipher a pair of letters using the Playfair square.
    """

    def find_position(c):
        for row in square:
            if c in row:
                return square.index(row), row.index(c)

    pos1 = find_position(pair[0])
    pos2 = find_position(pair[1])

    if pos1[0] == pos2[0]:  # Same row
        col_shift = 1 if mode == "encode" else -1
        return (
            square[pos1[0]][(pos1[1] + col_shift) % 5]
            + square[pos2[0]][(pos2[1] + col_shift) % 5]
        )
    elif pos1[1] == pos2[1]:  # Same column
        row_shift = 1 if mode == "encode" else -1
        return (
            square[(pos1[0] + row_shift) % 5][pos1[1]]
            + square[(pos2[0] + row_shift) % 5][pos2[1]]
        )
    else:  # Rectangle
        return square[pos1[0]][pos2[1]] + square[pos2[0]][pos1[1]]
