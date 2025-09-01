# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Provides File Utils



"""


# Import | Standard Library
import re
import unicodedata

# Import | Libraries

# Import | Local Modules


class URL(object):
    """"""

    # Static Methods

    @staticmethod
    def is_string_an_url(url_string: str) -> bool:
        result = validators.url(url_string)

        if isinstance(result, ValidationFailure):
            return False

        return result
