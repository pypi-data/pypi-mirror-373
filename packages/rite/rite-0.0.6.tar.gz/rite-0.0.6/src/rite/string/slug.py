# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Provides Slug Module
===================



"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
import re
import unicodedata

# Import | Libraries

# Import | Local Modules


# =============================================================================
# Classes
# =============================================================================


class Slug:
    """
    Slug Class
    ==========

    A class to generate URL-friendly slugs from strings with additional
    customization.

    Methods
    -------
    --------
    generate_slug(text: str, delimiter: str = '-', max_length: int = None,
        lowercase: bool = True, custom_replacements: dict = None) -> str:
        Generates a slug for the given text with various customization options.
    """

    @staticmethod
    def generate_slug(
        text: str,
        delimiter: str = "-",
        max_length: int = None,
        lowercase: bool = True,
        custom_replacements: dict = None,
    ) -> str:
        """
        Generates a slug for the given text.

        Parameters:
            text (str): The text to convert into a slug.
            delimiter (str): The delimiter to use for separating words.
            max_length (int): Maximum length of the slug.
            lowercase (bool): Convert slug to lowercase if True.
            custom_replacements (dict): Custom replacements for specific
            characters.

        Returns
        -------
            str: A URL-friendly slug.
        """
        # Apply custom replacements if provided
        if custom_replacements:
            for key, value in custom_replacements.items():
                text = text.replace(key, value)

        # Normalize and optionally convert to lowercase
        slug = unicodedata.normalize("NFKD", text)
        if lowercase:
            slug = slug.encode("ascii", "ignore").decode("ascii").lower()
        else:
            slug = slug.encode("ascii", "ignore").decode("ascii")

        # Replace non-word characters with the delimiter
        slug = re.sub(r"[^\w\s]", delimiter, slug)
        slug = re.sub(r"[\s" + re.escape(delimiter) + r"]+", delimiter, slug)
        slug = slug.strip(delimiter)

        # Truncate slug to max_length
        if max_length and len(slug) > max_length:
            slug = slug[:max_length].rstrip(delimiter)

        return slug

    @staticmethod
    def add_prefix(slug: str, prefix: str, delimiter: str = "-") -> str:
        """
        Adds a prefix to the slug.

        Parameters:
            slug (str): The original slug.
            prefix (str): The prefix to add.
            delimiter (str): The delimiter used in the slug.

        Returns
        -------
            str: The slug with the prefix added.
        """
        return f"{prefix}{delimiter}{slug}" if prefix else slug

    @staticmethod
    def add_suffix(slug: str, suffix: str, delimiter: str = "-") -> str:
        """
        Adds a suffix to the slug.

        Parameters:
            slug (str): The original slug.
            suffix (str): The suffix to add.
            delimiter (str): The delimiter used in the slug.

        Returns
        -------
            str: The slug with the suffix added.
        """
        return f"{slug}{delimiter}{suffix}" if suffix else slug

    @staticmethod
    def generate_incremental_slug(
        slug: str,
        existing_slugs: set,
        delimiter: str = "-",
    ) -> str:
        """
        Generates an incremental slug for uniqueness.

        Parameters:
            slug (str): The original slug.
            existing_slugs (set): A set of existing slugs to check against.
            delimiter (str): The delimiter used in the slug.

        Returns
        -------
            str: A unique slug with an incremental number added if needed.
        """
        new_slug = slug
        counter = 1
        while new_slug in existing_slugs:
            new_slug = f"{slug}{delimiter}{counter}"
            counter += 1
        return new_slug

    @staticmethod
    def is_valid_slug(
        slug: str,
        delimiter: str = "-",
    ) -> bool:
        """
        Validates if a string is a valid slug.

        Parameters:
            slug (str): The string to validate as a slug.
            delimiter (str): The delimiter used in the slug.

        Returns
        -------
            bool: True if the string is a valid slug, False otherwise.
        """
        pattern = re.compile(
            f"^[a-z0-9]+(?:{re.escape(delimiter)}[a-z0-9]+)*$"
        )
        return bool(pattern.match(slug))

    @staticmethod
    def normalize_unicode(text: str) -> str:
        """
        Normalize Unicode characters in a string.

        Parameters:
            text (str): The text to normalize.

        Returns
        -------
            str: The normalized text.
        """
        return unicodedata.normalize("NFKD", text)

    @staticmethod
    def remove_stop_words(
        text: str, stop_words: set, delimiter: str = " "
    ) -> str:
        """
        Remove stop words from a string.

        Parameters:
            text (str): The text to process.
            stop_words (set): A set of stop words to remove.
            delimiter (str): The delimiter used to separate words.

        Returns
        -------
            str: The text with stop words removed.
        """
        words = text.split(delimiter)
        filtered_words = [
            word for word in words if word.lower() not in stop_words
        ]
        return " ".join(filtered_words)

    @staticmethod
    def limit_word_count(text: str, limit: int, delimiter: str = " ") -> str:
        """
        Limit the number of words in a string.

        Parameters:
            text (str): The text to limit.
            limit (int): The maximum number of words.
            delimiter (str): The delimiter used to separate words.

        Returns
        -------
            str: The limited text.
        """
        words = text.split(delimiter)[:limit]
        return " ".join(words)

    @staticmethod
    def replace_with_delimiter(
        text: str, chars: str, delimiter: str = "-"
    ) -> str:
        """
        Replace specific characters in a string with a delimiter.

        Parameters:
            text (str): The text to process.
            chars (str): A string of characters to replace.
            delimiter (str): The delimiter to use as replacement.

        Returns
        -------
            str: The processed text.
        """
        return re.sub(f"[{re.escape(chars)}]", delimiter, text)


# Example usage
title = "This is a Test -- Slug with extra features! ÄÖÜ"
custom_mappings = {"Ä": "Ae", "Ö": "Oe", "Ü": "Ue"}
slug = Slug.generate_slug(
    title, custom_replacements=custom_mappings, max_length=30
)
print(slug)  # Output: 'this-is-a-test-slug-with-e'

basic_slug = Slug.generate_slug("Example Title")
prefixed_slug = Slug.add_prefix(basic_slug, "blog")
suffixed_slug = Slug.add_suffix(basic_slug, "2021")
incremental_slug = Slug.generate_incremental_slug(
    basic_slug, {"example-title", "example-title-1"}
)
is_valid = Slug.is_valid_slug(basic_slug)

print("Basic Slug:", basic_slug)
print("Prefixed Slug:", prefixed_slug)
print("Suffixed Slug:", suffixed_slug)
print("Incremental Slug:", incremental_slug)
print("Is Valid Slug:", is_valid)

# Example usage
text = "This is an example slug with Unicode characters: ÄÖÜ and stop words."
normalized_text = Slug.normalize_unicode(text)
clean_text = Slug.remove_stop_words(
    normalized_text, {"is", "an", "and", "with"}
)
limited_text = Slug.limit_word_count(clean_text, 5)
custom_delimiter_text = Slug.replace_with_delimiter(limited_text, "ÄÖÜ", "-")
slug = Slug.generate_slug(custom_delimiter_text)

print("Normalized Text:", normalized_text)
print("Clean Text:", clean_text)
print("Limited Text:", limited_text)
print("Custom Delimiter Text:", custom_delimiter_text)
print("Slug:", slug)


# Static Methods

# @staticmethod
# def create_slug(value, allow_unicode=False):
#     """"""
#     value = str(value)
#     if allow_unicode:
#         value = unicodedata.normalize('NFKC', value)
#     else:
#         value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
#     value = re.sub(r'[^\w\s-]', '', value.lower())
#     return re.sub(r'[-\s]+', '-', value).strip('-_')

# @staticmethod
# def create_slug_snake(value, allow_unicode=False):
#     """"""
#     value = str(value)
#     if allow_unicode:
#         value = unicodedata.normalize('NFKC', value)
#     else:
#         value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
#     value = re.sub(r'[^\w\s-]', '', value.lower())
#     return re.sub(r'[-\s]+', '_', value).strip('-_')


# def slugify(value, allow_unicode=False):
#     """
#     Taken from https://github.com/django/django/blob/master/django/utils/text.py
#     Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
#     dashes to single dashes. Remove characters that aren't alphanumerics,
#     underscores, or hyphens. Convert to lowercase. Also strip leading and
#     trailing whitespace, dashes, and underscores.
#     """
#     value = str(value)
#     if allow_unicode:
#         value = unicodedata.normalize('NFKC', value)
#     else:
#         value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
#     value = re.sub(r'[^\w\s-]', '', value.lower())
#     return re.sub(r'[-\s]+', '-', value).strip('-_')
