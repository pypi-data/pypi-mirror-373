# -*- coding: utf-8 -*-

# =============================================================================
# Imports
# =============================================================================

import logging
import os
import platform

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
# Class
# =============================================================================


class System:
    """
    System Class
    ============
    Provides utility methods for system operations, including:
    - Executing system commands.
    - Determining the operating system type.
    """

    @staticmethod
    def execute_command(command: str) -> None:
        """
        Executes a system command and raises an OSError if it fails.

        Parameters:
        -----------
        command : str
            The system command to execute.

        Raises:
        -------
        OSError:
            If the command exits with a non-zero status.
        """
        logger.info("Executing command: %s", command)
        return_code = os.system(command)
        if return_code != 0:
            raise OSError(
                f"Command failed with return code {return_code}: {command}"
            )

    @staticmethod
    def get_os_type() -> str:
        """
        Determines the operating system type.

        Returns
        -------
        --------
        str:
            A string representing the operating system type.
            Possible values are:
            - "MacOS" for macOS systems.
            - "Linux" for Linux systems.
            - "Windows" for Windows systems.
            - "Unknown" for unsupported or unrecognized systems.
        """
        os_name = platform.system()
        if os_name == "Darwin":
            return "MacOS"
        elif os_name == "Linux":
            return "Linux"
        elif os_name == "Windows":
            return "Windows"
        else:
            return "Unknown"


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Example: Execute a system command
    try:
        System.execute_command("echo 'Hello, World!'")
    except OSError as e:
        logger.error(e)

    # Example: Get the operating system type
    OS_TYPE = System.get_os_type()
    logger.info("Operating System: %s", OS_TYPE)

    # # Example: Check if a file exists
    # file_path = "example.txt"
    # exists = System.file_exists(file_path)
    # logger.info(f"Does the file exist? {exists}")

    # # Example: Write to a file
    # try:
    #     System.write_file(file_path, "Sample content.")
    # except OSError as e:
    #     logger.error(e)

    # # Example: Read from a file
    # try:
    #     content = System.read_file(file_path)
    #     if content:
    #         logger.info(f"File content: {content}")
    # except OSError as e:
    #     logger.error(e)

    # # Example: Create a directory
    # try:
    #     System.create_directory("example_dir")
    # except OSError as e:
    #     logger.error(e)
