# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Singleton
=========

This module provides a metaclass `SingletonMeta` for implementing the Singleton
design pattern. Classes using this metaclass ensure that only one instance of
the class is created, regardless of how many times it is instantiated.

Classes:
--------
- SingletonMeta: A metaclass for implementing the Singleton pattern.

Features:
---------
- Ensures a single instance of a class.
- Thread-safe by default.
- Provides an easy-to-use interface for creating Singleton classes.

Usage:
------
To use the Singleton pattern, define your class with `SingletonMeta` as its
metaclass:

    class MySingleton(metaclass=SingletonMeta):
        pass

Example:
--------
    # Define a Singleton class
    class Configuration(metaclass=SingletonMeta):
        def __init__(self, value):
            self.value = value

    # Test the Singleton behavior
    config1 = Configuration("value1")
    config2 = Configuration("value2")
    assert config1 is config2  # True
    print(config1.value)       # Outputs: value2

"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
from typing import Any, Dict

# =============================================================================
# Classes
# =============================================================================


class SingletonMeta(type):
    """
    SingletonMeta Class
    ===================

    A metaclass for implementing the Singleton pattern. This ensures that only
    one instance of a class exists throughout the application lifecycle.

    Attributes
    ----------
    -----------
    _instances : Dict[type, Any]
        A dictionary that maps classes to their single instances.

    Methods
    -------
    --------
    __call__(*args, **kwargs):
        Overrides the `__call__` method to control instance creation.
    """

    _instances: Dict[type, Any] = {}

    def __call__(cls, *args, **kwargs) -> Any:
        """
        Ensures that only one instance of the class is created. Updates
        attributes on subsequent calls.

        Parameters:
        -----------
        *args, **kwargs:
            Arguments passed to the class constructor.

        Returns
        -------
        --------
        Any:
            The single instance of the class.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        else:
            instance = cls._instances[cls]
            # Update attributes of the existing instance
            instance.__init__(*args, **kwargs)
        return instance


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "SingletonMeta",
]


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":

    # Example Singleton class
    class Configuration(metaclass=SingletonMeta):
        """
        A Singleton class for storing configuration values.
        """

        def __init__(self, value: str) -> None:
            self.value = value

    # Test Singleton behavior
    config1 = Configuration("value1")
    config2 = Configuration("value2")

    # Validate that both instances are the same
    assert config1 is config2  # True
    print(f"Config1 Value: {config1.value}")  # Outputs: value2
    print(f"Config2 Value: {config2.value}")  # Outputs: value2
