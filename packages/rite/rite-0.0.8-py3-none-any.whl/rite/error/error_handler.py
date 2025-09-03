# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Error Handling Module
=====================

This module provides the `ErrorHandler` class for managing and logging errors
in the system. It supports error logging, raising alerts, and retrying failed
operations with customizable retry logic.

Classes:
--------
- ErrorHandler: Handles error logging, alerting, and retrying operations.

Features:
---------
- Logs errors to a specified log file.
- Raises alerts for critical errors.
- Retries failed operations with configurable retry limits and exponential
backoff.

"""


# =============================================================================
# Imports
# =============================================================================

import logging
import time
from typing import Callable, Optional

# =============================================================================
# Classes
# =============================================================================


class ErrorHandler:
    """
    Error Handler Class
    ===================

    A class to handle and log errors in the system. It provides methods for
    logging errors, raising alerts, and retrying operations.

    Attributes
    ----------
    -----------
    log_file : Optional[str]
        The path to the log file for error logging.
    """

    def __init__(
        self,
        log_file: Optional[str] = "error_log.txt",
    ) -> None:
        """
        Initializes the ErrorHandler with a specified log file.

        Parameters:
        -----------
        log_file : Optional[str]
            The path to the log file (default: 'error_log.txt').
        """
        self.log_file = log_file
        logging.basicConfig(
            filename=self.log_file,
            level=logging.ERROR,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

    def log_error(self, error: str) -> None:
        """
        Logs an error message to the log file.

        Parameters:
        -----------
        error : str
            The error message to log.
        """
        logging.error(error)
        print(f"Error logged: {error}")

    def raise_alert(
        self,
        error: str,
    ) -> None:
        """
        Raises an alert for critical errors and logs the alert message.

        Parameters:
        -----------
        error : str
            The error message to alert on.
        """
        # Extendable to include email, SMS, or notification services
        print(f"ALERT: {error}")
        self.log_error(error)

    def retry_operation(
        self,
        operation: Callable,
        retries: int = 3,
        backoff: float = 1.0,
    ) -> bool:
        """
        Retries a specified operation a given number of times with optional
        exponential backoff.

        Parameters:
        -----------
        operation : Callable
            The operation (function) to retry.
        retries : int, optional
            The number of retry attempts (default: 3).
        backoff : float, optional
            The initial backoff time in seconds between retries (default: 1.0).

        Returns
        -------
        --------
        bool:
            True if the operation succeeded, False if all retries failed.
        """
        for attempt in range(1, retries + 1):
            try:
                operation()
                print(f"Operation succeeded on attempt {attempt}.")
                return True
            except (
                RuntimeError,
                ValueError,
            ) as e:  # Catch specific exceptions
                self.log_error(f"Attempt {attempt} failed with error: {e}")
                if attempt < retries:
                    sleep_time = backoff * (
                        2 ** (attempt - 1)
                    )  # Exponential backoff
                    print(f"Retrying in {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
        print(f"Operation failed after {retries} attempts.")
        return False


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Initialize the error handler
    error_handler = ErrorHandler()

    # Example of a failing operation
    def failing_operation():
        """
        A simulated operation that raises a RuntimeError.
        """
        raise RuntimeError("Simulated operation failure.")

    # Log an error
    error_handler.log_error("This is a test error.")

    # Raise an alert
    error_handler.raise_alert("Critical system failure detected.")

    # Retry a failing operation
    SUCCESS = error_handler.retry_operation(
        failing_operation, retries=3, backoff=2.0
    )
    if not SUCCESS:
        print("All retry attempts failed.")
