# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Provides File Module
===================



"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
import os
import shutil

# Import | Libraries

# Import | Local Modules


# =============================================================================
# Classes
# =============================================================================


class File(object):
    """
    File Class
    ==========

    """

    def __init__(self, file_path):
        self.file_path = file_path

    def read_file(self):
        # Read contents of the file
        pass

    def write_file(self, content, mode="w"):
        # Write content to the file
        pass

    def convert_file_format(self, new_format):
        # Convert file to a new format
        pass

    def copy_file(src, dst):
        """ """
        shutil.copyfile(src, dst)


def copy_files(source_dir, target_dir):
    """ """
    file_names = os.listdir(source_dir)

    for file_name in file_names:
        # shutil.move(os.path.join(source_dir, file_name), target_dir)
        source = os.path.join(source_dir, file_name)
        target = os.path.join(target_dir, file_name)
        # print(source)
        # print(target)
        shutil.copyfile(source, target)
