def space_text(input_str: str, space_side: str, line_len: int, space_character: str = ' '):
    """
    Inserts a given amount of space cleanly on either side of a string, or on both.
    :param input_str: actual text to space
    :param space_side: one of "left", "right" or "both" -- side to add space to.
        Both will split space amount evenly, favoring right on odd #.
    :param line_len: Total line length after spaces are added
    :param space_character" character used in spacing
    """
    assert len(space_character) == 1
    diff = line_len-len(input_str)
    if space_side == 'left':
        return space_character*diff + input_str
    if space_side == 'right':
        return input_str + space_character*diff
    if space_side == 'both':
        if diff % 2 == 0:
            return space_character*(diff//2) + input_str + space_character*(diff//2)
        else:
            return space_character*(diff//2) + input_str + space_character*(diff//2 + 1)


def squish_between(middle_str: str, side_str: str):
    return side_str+middle_str+side_str
