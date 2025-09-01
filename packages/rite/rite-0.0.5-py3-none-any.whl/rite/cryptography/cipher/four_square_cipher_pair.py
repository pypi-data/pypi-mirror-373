def four_square_cipher_pair(pair, square1, square2, mode="encode"):
    """
    Cipher a pair of letters using the Four-Square squares.
    """

    def find_position(letter, square):
        for row in square:
            if letter in row:
                return square.index(row), row.index(letter)

    # Find positions in the standard square
    pos1 = find_position(pair[0], square1)
    pos2 = find_position(pair[1], square2)

    if mode == "encode":
        return square2[pos1[0]][pos2[1]] + square1[pos2[0]][pos1[1]]
    else:  # mode == 'decode'
        return square1[pos1[0]][pos2[1]] + square2[pos2[0]][pos1[1]]
