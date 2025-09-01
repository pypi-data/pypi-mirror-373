# -*- coding: UTF-8 -*-

import math


def float_to_degree_minute_second(value, absolute=False):
    """
    Split a float value into DMS (degree, minute, second) parts

    :param value - Float value to split
    :param absolute - Obtain the absolute value
    :return tuple containing DMS values
    """
    invert = not absolute and value < 0
    value = abs(value)
    degree = int(math.floor(value))
    value = (value - degree) * 60
    minute = int(math.floor(value))
    second = (value - minute) * 60
    return (degree * -1 if invert else degree, minute, second)
