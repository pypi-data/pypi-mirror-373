# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Provides Case Module
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


class Folder:
    """
    Folder Class
    ============

    """

    def __init__(self, directory_path):
        """
        Initialize the Folder class with a specific directory path.

        Parameters:
        directory_path (str): The path to the directory this class will
        operate on.
        """
        self.directory_path = directory_path

    def list_dirs(rootdir):
        """ """
        dirs = []
        for file in os.listdir(rootdir):
            d = os.path.join(rootdir, file)
            if os.path.isdir(d):
                dirs.append(file)
        return dirs

    def list_files(self):
        """
        List all files in the directory.

        Returns
        -------
        list: A list of filenames in the directory.

        Raises:
        FileNotFoundError: If the specified directory does not exist.
        """
        try:
            return [
                f
                for f in os.listdir(self.directory_path)
                if os.path.isfile(os.path.join(self.directory_path, f))
            ]  # noqa E501
        except FileNotFoundError:
            print(f"Directory not found: {self.directory_path}")
            return []

    # def list_files(rootdir):
    #     """
    #     """
    #     dirs = []
    #     for file in os.listdir(rootdir):
    #         d = os.path.join(rootdir, file)
    #         dirs.append(file)
    #     return(dirs)

    def create_subfolder(self, subfolder_name):
        """
        Creates a subfolder within the current directory.

        Parameters:
        subfolder_name (str): The name of the subfolder to create.

        Raises:
        Exception: If the subfolder could not be created.
        """
        path = os.path.join(self.directory_path, subfolder_name)
        try:
            os.makedirs(path, exist_ok=True)
            print(f"Subfolder created: {path}")
        except Exception as e:
            print(f"Error creating subfolder: {e}")

    def delete_file(self, file_name):
        """
        Deletes a file within the directory.

        Parameters:
        file_name (str): The name of the file to delete.

        Raises:
        Exception: If the file could not be deleted.
        """
        file_path = os.path.join(self.directory_path, file_name)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"File deleted: {file_path}")
            else:
                print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error deleting file: {e}")

    def get_folder_size(self):
        """
        Calculates and returns the total size of the folder in bytes.

        Returns
        -------
        int: The total size of the folder in bytes.
        """
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.directory_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.isfile(fp):
                    total_size += os.path.getsize(fp)
        return total_size

    def rename_file(self, old_file_name, new_file_name):
        """
        Renames a file within the directory.

        Parameters:
        old_file_name (str): The current name of the file.
        new_file_name (str): The new name for the file.

        Raises:
        Exception: If the file could not be renamed.
        """
        old_file = os.path.join(self.directory_path, old_file_name)
        new_file = os.path.join(self.directory_path, new_file_name)
        try:
            if os.path.isfile(old_file):
                os.rename(old_file, new_file)
                print(f"File renamed from {old_file} to {new_file}")
            else:
                print(f"File not found: {old_file}")
        except Exception as e:
            print(f"Error renaming file: {e}")

    def move_file(self, file_name, new_directory):
        """
        Moves a file from the current directory to a specified new directory.

        Parameters:
        file_name (str): The name of the file to be moved.
        new_directory (str): The path to the directory where the file should
        be moved.

        Notes:
        If the new directory does not exist, it is created.
        If the file does not exist in the current directory, an error message
        is displayed.

        Raises:
        Exception: If an error occurs during the file moving process.
        """
        source = os.path.join(self.directory_path, file_name)
        destination = os.path.join(new_directory, file_name)

        try:
            if os.path.isfile(source):
                os.makedirs(new_directory, exist_ok=True)
                shutil.move(source, destination)
                print(f"File moved: {source} -> {destination}")
            else:
                print(f"File not found: {source}")
        except Exception as e:
            print(f"Error moving file: {e}")

    def copy_file(self, file_name, new_directory):
        """
        Copies a file from the current directory to a specified new directory.

        Parameters:
        file_name (str): The name of the file to be copied.
        new_directory (str): The path to the directory where the file should
        be copied.

        Notes:
        If the new directory does not exist, it is created.
        If the file does not exist in the current directory, an error message
        is displayed.

        Raises:
        Exception: If an error occurs during the file copying process.
        """
        source = os.path.join(self.directory_path, file_name)
        destination = os.path.join(new_directory, file_name)

        try:
            if os.path.isfile(source):
                os.makedirs(new_directory, exist_ok=True)
                shutil.copy2(source, destination)
                print(f"File copied: {source} -> {destination}")
            else:
                print(f"File not found: {source}")
        except Exception as e:
            print(f"Error copying file: {e}")

    def delete_contents(self, folder):
        """
        Deletes all contents (files and subdirectories) within a specified
        folder.

        Parameters:
        folder (str): The path to the folder whose contents are to be deleted.

        Notes:
        This method removes both files and subdirectories within the specified
        folder. It handles symbolic links and regular files differently to
        ensure safe deletion.

        Raises:
        Exception: If an error occurs during the deletion process.
        """
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")


# Function | Create Directory
def create_dir(dir_path, mode=777):
    """ """
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path, mode)
        except OSError as err:
            return err
    else:
        pass


def path_leaf(path):
    """ """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def copy_all_files(source_dir, target_dir):
    """ """
    for root, dirs, files in os.walk(
        source_dir
    ):  # replace the . with your starting directory

        for file in files:
            path_file = os.path.join(root, file)
            shutil.copy2(path_file, target_dir)  # change you destination dir
            # shutil.copy2(path_file,os.path.join(rootdir, file)) # change you destination dir
