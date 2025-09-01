# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Provides INIHandler Module
==========================



"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
import configparser
from typing import Any, Dict, List, Optional

# Import | Libraries

# Import | Local Modules


# =============================================================================
# Classes
# =============================================================================


class INIHandler(object):
    """
    A class for handling INI configuration files.


    Methods
    -------
    --------
    load_ini(file_path: str) -> configparser.ConfigParser:
        Loads an INI configuration file.
    save_ini(config: configparser.ConfigParser, file_path: str):
        Saves a ConfigParser object to an INI file.
    update_ini(config: configparser.ConfigParser, section: str, updates: Dict[str, Any]):
        Updates a section in the ConfigParser object.
    get_value(config: configparser.ConfigParser, section: str, key: str, fallback: Optional[Any] = None) -> Any:
        Gets a value from a section in the ConfigParser object.
    add_section(config: configparser.ConfigParser, section: str):
        Adds a new section to the ConfigParser object.
    remove_section(config: configparser.ConfigParser, section: str):
        Removes a section from the ConfigParser object.
    list_sections(config: configparser.ConfigParser) -> List[str]:
        Lists all sections in the configuration.
    list_keys(config: configparser.ConfigParser, section: str) -> List[str]:
        Lists all keys in a specific section.
    has_key(config: configparser.ConfigParser, section: str, key: str) -> bool:
        Checks if a specific key exists in a section.
    remove_key(config: configparser.ConfigParser, section: str, key: str) -> bool:
        Removes a specific key from a section.

    """

    @staticmethod
    def load_ini(file_path: str) -> configparser.ConfigParser:
        """
        Loads an INI configuration file.

        Parameters:
            file_path (str): Path to the INI file.

        Returns
        -------
            configparser.ConfigParser: The parsed INI file.
        """
        config = configparser.ConfigParser()
        config.read(file_path)
        return config

    @staticmethod
    def save_ini(config: configparser.ConfigParser, file_path: str):
        """
        Saves a ConfigParser object to an INI file.

        Parameters:
            config (configparser.ConfigParser): The ConfigParser object to save.
            file_path (str): Path to the INI file where the data will be saved.
        """
        with open(file_path, "w", encoding="utf-8") as file:
            config.write(file)

    @staticmethod
    def update_ini(
        config: configparser.ConfigParser,
        section: str,
        updates: Dict[str, Any],
    ):
        """
        Updates a section in the ConfigParser object.

        Parameters:
            config (configparser.ConfigParser): The ConfigParser object.
            section (str): The section in the INI file to update.
            updates (Dict[str, Any]): A dictionary containing the updates.
        """
        if not config.has_section(section):
            config.add_section(section)
        for key, value in updates.items():
            config.set(section, key, str(value))

    @staticmethod
    def get_value(
        config: configparser.ConfigParser,
        section: str,
        key: str,
        fallback: Optional[Any] = None,
    ) -> Any:
        """
        Gets a value from a section in the ConfigParser object.

        Parameters:
            config (configparser.ConfigParser): The ConfigParser object.
            section (str): The section from which to get the value.
            key (str): The key for the value to get.
            fallback (Optional[Any]): The default value to return if the key
            is not found.

        Returns
        -------
            Any: The value from the specified section and key, or the fallback
            value.
        """
        return config.get(section, key, fallback=fallback)

    @staticmethod
    def add_section(config: configparser.ConfigParser, section: str):
        """
        Adds a new section to the ConfigParser object.

        Parameters:
            config (configparser.ConfigParser): The ConfigParser object.
            section (str): The section to add.

        Returns
        -------
            bool: True if the section was added, False if the section already
            exists.
        """
        if not config.has_section(section):
            config.add_section(section)
            return True
        return False

    @staticmethod
    def remove_section(config: configparser.ConfigParser, section: str):
        """
        Removes a section from the ConfigParser object.

        Parameters:
            config (configparser.ConfigParser): The ConfigParser object.
            section (str): The section to remove.

        Returns
        -------
            bool: True if the section was removed, False if the section does
            not exist.
        """
        return config.remove_section(section)

    @staticmethod
    def list_sections(config: configparser.ConfigParser) -> List[str]:
        """
        Lists all sections in the configuration.

        Parameters:
            config (configparser.ConfigParser): The ConfigParser object.

        Returns
        -------
            List[str]: A list of section names.
        """
        return config.sections()

    @staticmethod
    def list_keys(
        config: configparser.ConfigParser, section: str
    ) -> List[str]:
        """
        Lists all keys in a specific section.

        Parameters:
            config (configparser.ConfigParser): The ConfigParser object.
            section (str): The section to list keys from.

        Returns
        -------
            List[str]: A list of key names in the section.
        """
        if config.has_section(section):
            return list(config[section])
        return []

    @staticmethod
    def has_key(
        config: configparser.ConfigParser, section: str, key: str
    ) -> bool:
        """
        Checks if a specific key exists in a section.

        Parameters:
            config (configparser.ConfigParser): The ConfigParser object.
            section (str): The section to check.
            key (str): The key to check for.

        Returns
        -------
            bool: True if the key exists in the section, False otherwise.
        """
        return config.has_option(section, key)

    @staticmethod
    def remove_key(
        config: configparser.ConfigParser, section: str, key: str
    ) -> bool:
        """
        Removes a specific key from a section.

        Parameters:
            config (configparser.ConfigParser): The ConfigParser object.
            section (str): The section to remove the key from.
            key (str): The key to remove.

        Returns
        -------
            bool: True if the key was removed, False if the key or section
            does not exist.
        """
        if config.has_section(section) and config.has_option(section, key):
            config.remove_option(section, key)
            return True
        return False


# =============================================================================
# Functions
# =============================================================================


def test():
    """
    Test Function
    """

    # Example usage
    config = INIHandler.load_ini("config.ini")

    # Update configuration
    INIHandler.update_ini(
        config, "section1", {"key1": "value1", "key2": "value2"}
    )

    # Save configuration
    INIHandler.save_ini(config, "config_updated.ini")

    # Example usage
    config = INIHandler.load_ini("config.ini")

    # Get value with a fallback
    value = INIHandler.get_value(
        config, "section1", "key1", fallback="default"
    )

    # Add a new section
    added = INIHandler.add_section(config, "new_section")

    # Remove a section
    removed = INIHandler.remove_section(config, "section_to_remove")

    # Save configuration
    INIHandler.save_ini(config, "config_updated.ini")

    # Example usage
    config = INIHandler.load_ini("config.ini")

    # List all sections
    sections = INIHandler.list_sections(config)
    print(sections)

    # List all keys in a section
    keys = INIHandler.list_keys(config, "section1")
    print(keys)

    # Check if a specific key exists
    exists = INIHandler.has_key(config, "section1", "key1")
    print(exists)

    # Remove a specific key
    removed = INIHandler.remove_key(config, "section1", "key1")
    print(removed)

    # Save configuration
    INIHandler.save_ini(config, "config_updated.ini")


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    """Main"""
    import doctest

    doctest.testmod()
    test()
