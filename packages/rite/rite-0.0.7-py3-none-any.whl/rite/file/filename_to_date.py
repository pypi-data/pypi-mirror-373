import gzip
import logging
import os
import re
import sys
import tempfile
import traceback
from datetime import datetime
from functools import wraps
from getpass import getpass
from shlex import quote
from shutil import copyfileobj

from django.core.mail import EmailMultiAlternatives
from django.db import connection
from django.http import HttpRequest
from django.utils import timezone

from . import settings


def filename_to_datefilename_to_date(filename, datefmt=None):
    """
    Return a datetime from a file name.

    :param datefmt: strftime format string, ``settings.DATE_FORMAT`` is used
                    if is ``None``
    :type datefmt: ``str`` or ``NoneType``

    :returns: Date guessed or nothing if no date found
    :rtype: ``datetime.datetime`` or ``NoneType``
    """
    datefmt = datefmt or settings.DATE_FORMAT
    datestring = filename_to_datestring(filename, datefmt)
    if datestring is not None:
        return datetime.strptime(datestring, datefmt)
