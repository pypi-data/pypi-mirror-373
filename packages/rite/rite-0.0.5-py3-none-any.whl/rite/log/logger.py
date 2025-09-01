# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Logger Module
=============

This module provides the `Logger` class, which serves as a simple and
configurable logging utility for applications within the Sense ecosystem.
It supports logging to both the console and a file, includes timestamped
messages, and provides different logging levels such as debug, info, warning,
error, and critical.

Classes:
--------
- Logger: A configurable logger for managing log messages in applications.

Features:
---------
- Log to console and/or file.
- Timestamped messages for traceability.
- Logging levels: debug, info, warning, error, critical.
- Clear log file utility.

"""


# =============================================================================
# Imports
# =============================================================================

import logging

# Standard Library Imports
import os
from typing import Optional

# =============================================================================
# Classes
# =============================================================================


class Logger:
    """
    Logger Class
    ============

    A configurable logger that supports logging to both console and file
    outputs with various log levels. This class wraps Python's built-in
    logging module, providing an easy interface to integrate logging into
    applications.

    Attributes
    ----------
    -----------
    logger : logging.Logger
        The underlying logger instance from Python's logging module.
    log_file : Optional[str]
        Path to the log file if file logging is enabled.

    """

    def __init__(self, name: str, log_file: Optional[str] = None) -> None:
        """
        Initializes a new Logger instance with the specified name and optional
        log file.

        Parameters:
        -----------
        name : str
            The name of the logger, typically the module or application name.
        log_file : Optional[str]
            Path to a log file for file logging. If None, logging to file is
            disabled.

        Example:
        --------
        >>> logger = Logger(name="MyApp", log_file="app.log")
        >>> logger.info("Application started")
        """
        self.log_file = log_file
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Set up file logging if a log file path is provided
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        # Set up console logging
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def log(self, level: str, message: str) -> None:
        """
        Logs a message with the specified level.

        Parameters:
        -----------
        level : str
            The log level (e.g., "debug", "info", "warning", "error", "critical").
        message : str
            The message to log.
        """
        log_method = getattr(self.logger, level.lower(), None)
        if callable(log_method):
            log_method(message)
        else:
            raise ValueError(f"Invalid log level: {level}")

    def debug(self, message: str) -> None:
        """
        Logs a debug message.

        Parameters:
        -----------
        message : str
            The debug message to log.

        Example:
        --------
        >>> logger.debug("This is a debug message")
        """
        self.logger.debug(message)

    def info(self, message: str) -> None:
        """
        Logs an informational message.

        Parameters:
        -----------
        message : str
            The informational message to log.

        Example:
        --------
        >>> logger.info("This is an info message")
        """
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """
        Logs a warning message.

        Parameters:
        -----------
        message : str
            The warning message to log.

        Example:
        --------
        >>> logger.warning("This is a warning message")
        """
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """
        Logs an error message.

        Parameters:
        -----------
        message : str
            The error message to log.

        Example:
        --------
        >>> logger.error("This is an error message")
        """
        self.logger.error(message)

    def critical(self, message: str) -> None:
        """
        Logs a critical message.

        Parameters:
        -----------
        message : str
            The critical message to log.

        Example:
        --------
        >>> logger.critical("This is a critical message")
        """
        self.logger.critical(message)

    def clear_log(self) -> None:
        """
        Clears the log file content, if file logging is enabled.
        """
        if self.log_file and os.path.exists(self.log_file):
            open(self.log_file, "w", encoding="utf-8").close()
            self.info("Log file cleared.")


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "Logger",
]


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Initialize the Logger
    logger = Logger(name="ExampleApp", log_file="example.log")

    # Log messages at various levels
    logger.debug("This is a debug message.")
    logger.info("This is an informational message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")

    # Clear the log file
    logger.clear_log()
