# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Provides Date Utils

...

Examples:
    ...

Attributes:
    ...

Todo:

"""


# Import | Standard Library
from datetime import date

# Import | Libraries

# Import | Local Modules


class Date:
    """
    A class used to represent a Date

    ...

    Attributes
    ----------


    Methods
    -------
    test()
        test method
    """

    # Static Methods

    @staticmethod
    def date_dict():
        date_dict = {}
        date_today = date.today()
        date_default = str(date_today)
        date_dict["date_year"] = date_today.year
        date_dict["date_default"] = date_default
        date_dict["date_us_simple"] = date_default.replace("-", "/")
        # print(date_dict)
        return date_dict
