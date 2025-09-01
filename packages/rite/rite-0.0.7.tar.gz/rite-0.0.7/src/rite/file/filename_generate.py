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


def filename_generate(
    extension,
    database_name="",
    servername=None,
    content_type="db",
    wildcard=None,
):
    """
    Create a new backup filename.

    :param extension: Extension of backup file
    :type extension: ``str``

    :param database_name: If it is database backup specify its name
    :type database_name: ``str``

    :param servername: Specify server name or by default ``settings.STURNUS_DATABASE_HOSTNAME``
    :type servername: ``str``

    :param content_type: Content type to backup, ``'media'`` or ``'db'``
    :type content_type: ``str``

    :param wildcard: Replace datetime with this wilecard regex
    :type content_type: ``str``

    :returns: Computed file name
    :rtype: ``str`
    """
    if content_type == "db":
        if "/" in database_name:
            database_name = os.path.basename(database_name)
        if "." in database_name:
            database_name = database_name.split(".")[0]
        template = settings.FILENAME_TEMPLATE
    elif content_type == "media":
        template = settings.MEDIA_FILENAME_TEMPLATE
    else:
        template = settings.FILENAME_TEMPLATE

    params = {
        "servername": servername or settings.HOSTNAME,
        "datetime": wildcard or datetime.now().strftime(settings.DATE_FORMAT),
        "databasename": database_name,
        "extension": extension,
        "content_type": content_type,
    }
    if callable(template):
        filename = template(**params)
    else:
        filename = template.format(**params)
        filename = REG_FILENAME_CLEAN.sub("-", filename)
        filename = filename[1:] if filename.startswith("-") else filename
    return filename
