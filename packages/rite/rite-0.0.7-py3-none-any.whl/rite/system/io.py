# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
IO Module
=========

This module provides a utility class `IOOperations` for performing common
file input/output operations such as reading, writing, and checking file
existence. It also includes error handling and ensures compatibility with
various file encodings.

Classes:
--------
- IOOperations: A static utility class for file I/O operations.

Features:
---------
- Read content from files.
- Write content to files.
- Check if a file exists.
- Enhanced error handling and support for custom encodings.

Usage:
------
    from io_module import IOOperations

    # Check if a file exists
    if IOOperations.file_exists("example.txt"):
        content = IOOperations.read_file("example.txt")
        print(content)

    # Write content to a file
    IOOperations.write_file("example.txt", "Hello, World!")
"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
import logging
import os

# =============================================================================
# Configure Logging
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


# =============================================================================
# Classes
# =============================================================================


class IOOperations:
    """
    IOOperations Class
    ==================

    A utility class for performing common file input/output operations.

    Methods
    -------
    --------
    read_file(file_path: str, encoding: str = "utf-8") -> str:
        Reads the content of a file with the specified encoding.

    write_file(file_path: str, content: str, encoding: str = "utf-8") -> None:
        Writes content to a file with the specified encoding.

    file_exists(file_path: str) -> bool:
        Checks if a file exists at the given path.
    """

    @staticmethod
    def read_file(path: str, encoding: str = "utf-8") -> str:
        """
        Reads the content of a file.

        Parameters:
        -----------
        path : str
            The path of the file to read.
        encoding : str, optional
            The encoding to use for reading the file (default: "utf-8").

        Returns
        -------
        --------
        str:
            The content of the file.

        Raises:
        -------
        FileNotFoundError:
            If the specified file does not exist.
        IOError:
            If an error occurs during file reading.
        """
        try:
            with open(path, "r", encoding=encoding) as file:
                return file.read()
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"The file '{path}' does not exist."
            ) from exc
        except IOError as e:
            raise IOError(
                f"An error occurred while reading the file '{path}': {e}"
            ) from e

    @staticmethod
    def write_file(
        path: str, file_content: str, encoding: str = "utf-8"
    ) -> None:
        """
        Writes content to a file.

        Parameters:
        -----------
        path : str
            The path of the file to write to.
        file_content : str
            The content to write to the file.
        encoding : str, optional
            The encoding to use for writing to the file (default: "utf-8").

        Raises:
        -------
        IOError:
            If an error occurs during file writing.
        """
        try:
            with open(path, "w", encoding=encoding) as file:
                file.write(file_content)
        except IOError as e:
            raise IOError(
                f"An error occurred while writing to the file '{path}': {e}"
            ) from e

    @staticmethod
    def file_exists(file_path: str) -> bool:
        """
        Checks if a file exists at the specified path.

        Parameters:
        -----------
        file_path : str
            The path to the file.

        Returns
        -------
        --------
        bool:
            True if the file exists, False otherwise.
        """
        exists = os.path.exists(file_path)
        logger.info("File exists check for '%s': %s", file_path, exists)
        return exists

    @staticmethod
    def create_directory(directory_path: str) -> None:
        """
        Creates a directory if it does not already exist.

        Parameters:
        -----------
        directory_path : str
            The path to the directory to create.

        Raises:
        -------
        OSError:
            If the directory cannot be created.
        """
        if not os.path.exists(directory_path):
            try:
                os.makedirs(directory_path)
                logger.info("Directory created: %s", directory_path)
            except Exception as e:
                raise OSError(
                    f"Failed to create directory: {directory_path}"
                ) from e
        else:
            logger.info("Directory already exists: %s", directory_path)


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":

    # Example file path
    FILE_PATH = "example.txt"

    # Check if the file exists
    if IOOperations.file_exists(FILE_PATH):
        # Read file content
        content = IOOperations.read_file(FILE_PATH)
        print(f"File Content:\n{content}")
    else:
        # Write new content to the file
        IOOperations.write_file(FILE_PATH, "Hello, World!")
        print(f"File '{FILE_PATH}' created with content: 'Hello, World!'")
