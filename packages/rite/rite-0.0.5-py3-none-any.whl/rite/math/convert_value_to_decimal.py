# -*- coding: UTF-8 -*-

import decimal


def convert_value_to_decimal(value):
    """
    Convert a value into a decimal and handle any conversion required.

    @raises ValueError if trying to convert a value that does not translate to decimal.
    """
    if value is None:
        raise ValueError("None is not a valid money value.")
    if not isinstance(value, decimal.Decimal):
        try:
            return decimal.Decimal(str(value))
        except decimal.InvalidOperation as exc:
            raise ValueError(
                "Value could not be converted into a decimal."
            ) from exc
    return value
