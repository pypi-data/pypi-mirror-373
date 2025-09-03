import logging
import re

PATTERN_MATCHNG = (
    ("%a", r"[A-Z][a-z]+"),
    ("%A", r"[A-Z][a-z]+"),
    ("%w", r"\d"),
    ("%d", r"\d{2}"),
    ("%b", r"[A-Z][a-z]+"),
    ("%B", r"[A-Z][a-z]+"),
    ("%m", r"\d{2}"),
    ("%y", r"\d{2}"),
    ("%Y", r"\d{4}"),
    ("%H", r"\d{2}"),
    ("%I", r"\d{2}"),
    # ('%p', r'(?AM|PM|am|pm)'),
    ("%M", r"\d{2}"),
    ("%S", r"\d{2}"),
    ("%f", r"\d{6}"),
    # ('%z', r'\+\d{4}'),
    # ('%Z', r'(?|UTC|EST|CST)'),
    ("%j", r"\d{3}"),
    ("%U", r"\d{2}"),
    ("%W", r"\d{2}"),
    # ('%c', r'[A-Z][a-z]+ [A-Z][a-z]{2} \d{2} \d{2}:\d{2}:\d{2} \d{4}'),
    # ('%x', r'd{2}/d{2}/d{4}'),
    # ('%X', r'd{2}:d{2}:d{2}'),
    # ('%%', r'%'),
)


def date_format_to_regex(
    datefmt,
) -> logging.Pattern[str]:
    """
    Convert a strftime format string to a regex.

    :param datefmt: strftime format string
    :type datefmt: ``str``

    :returns: Equivalent regex
    :rtype: ``re.compite``
    """
    new_string = datefmt
    for pat, reg in PATTERN_MATCHNG:
        new_string = new_string.replace(pat, reg)
    return re.compile(pattern=f"({new_string})")
