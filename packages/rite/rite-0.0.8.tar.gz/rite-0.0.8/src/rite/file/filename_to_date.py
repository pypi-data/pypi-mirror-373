from datetime import datetime

from .filename_to_datestring import filename_to_datestring


def filename_to_datefilename_to_date(filename, date_format="%Y-%m-%d-%H%M%S"):
    """
    Return a datetime from a file name.

    :param date_format: strftime format string, ``settings.DATE_FORMAT`` is used
                    if is ``None``
    :type date_format: ``str`` or ``NoneType``

    :returns: Date guessed or nothing if no date found
    :rtype: ``datetime.datetime`` or ``NoneType``
    """
    datestring = filename_to_datestring(filename, date_format)
    if datestring is not None:
        return datetime.strptime(datestring, date_format)
