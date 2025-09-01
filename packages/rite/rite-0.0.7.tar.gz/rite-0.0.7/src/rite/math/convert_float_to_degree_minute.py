# -*- coding: UTF-8 -*-

import math


def float_to_degree_minute(value, absolute=False):
    """
    Split a float value into DM (degree, minute) parts

    :param value - Float value to split
    :param absolute - Obtain the absolute value
    :return tuple containing DM values
    """
    invert = not absolute and value < 0
    value = abs(value)
    degree = int(math.floor(value))
    minute = (value - degree) * 60
    return (degree * -1 if invert else degree, minute)
