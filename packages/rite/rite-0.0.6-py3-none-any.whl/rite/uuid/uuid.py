# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - UUID Module
==================


"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
import uuid

# Import | Libraries

# Import | Local Modules


# =============================================================================
# Classes
# =============================================================================


class UUID(object):
    """
    UUID Class
    ==========

    A class for generating and handling UUIDs.

    This class provides static methods to generate UUIDs in various formats
    and validate UUID strings.

    Methods
    -------
    create_random_uuid():
        Generates a random UUID.
    create_uuid_string():
        Generates a random UUID and returns it as a standard string.
    create_hex_uuid():
        Generates a random UUID and returns it as a hexadecimal string.
    validate_uuid(uuid_string):
        Validates whether a given string is a valid UUID.
    from_name(namespace, name):
        Generates a UUID based on a namespace and a name.
    get_version(uuid_obj):
        Extracts the version of a UUID.
    is_random_uuid(uuid_obj):
        Checks if the UUID is randomly generated (UUID4).
    formatted_string(uuid_obj):
        Returns a formatted string representation of the UUID.
    """

    @staticmethod
    def create_random_uuid():
        """
        Generates a random UUID (UUID4).

        Returns
        -------
            uuid.UUID: A randomly generated UUID.
        """
        return uuid.uuid4()

    @staticmethod
    def create_uuid_string():
        """
        Generates a random UUID and returns it as a string in standard form.

        Returns
        -------
            str: UUID as a string in standard form.
        """
        return str(uuid.uuid4())

    @staticmethod
    def create_hex_uuid():
        """
        Generates a random UUID and returns it as a 32-character hexadecimal
        string.

        Returns
        -------
            str: UUID as a 32-character hexadecimal string.
        """
        return uuid.uuid4().hex

    @staticmethod
    def validate_uuid(uuid_string):
        """
        Validates whether a given string is a valid UUID.

        Parameters:
            uuid_string (str): The UUID string to validate.

        Returns
        -------
            bool: True if valid, False otherwise.
        """
        try:
            uuid_obj = uuid.UUID(uuid_string)
            return str(uuid_obj) == uuid_string
        except ValueError:
            return False

    @staticmethod
    def from_name(namespace, name):
        """
        Generates a UUID based on a namespace and a name.

        Parameters:
            namespace (uuid.UUID): The namespace UUID.
            name (str): The name from which to generate the UUID.

        Returns
        -------
            uuid.UUID: A UUID generated from the namespace and name.
        """
        return uuid.uuid5(namespace, name)

    @staticmethod
    def get_version(uuid_obj):
        """
        Extracts the version of a UUID.

        Parameters:
            uuid_obj (uuid.UUID): The UUID object.

        Returns
        -------
            int: The version number of the UUID.
        """
        return uuid_obj.version

    @staticmethod
    def is_random_uuid(uuid_obj):
        """
        Checks if the UUID is randomly generated (UUID4).

        Parameters:
            uuid_obj (uuid.UUID): The UUID object.

        Returns
        -------
            bool: True if the UUID is a random UUID, False otherwise.
        """
        return uuid_obj.version == 4

    @staticmethod
    def formatted_string(uuid_obj):
        """
        Returns a formatted string representation of the UUID.

        Parameters:
            uuid_obj (uuid.UUID): The UUID object.

        Returns
        -------
            str: A formatted string representation of the UUID.
        """
        return f"UUID: {str(uuid_obj)}, Version: {uuid_obj.version}, Variant: {uuid_obj.variant}"


# =============================================================================
# Functions
# =============================================================================


def test():
    """
    Test Function
    """

    # Example usage
    random_uuid = UUID.create_random_uuid()
    uuid_string = UUID.create_uuid_string()
    hex_uuid = UUID.create_hex_uuid()
    is_valid = UUID.validate_uuid(uuid_string)
    namespace_uuid = uuid.NAMESPACE_DNS
    name_based_uuid = UUID.from_name(namespace_uuid, "example.com")
    version = UUID.get_version(name_based_uuid)
    is_random = UUID.is_random_uuid(name_based_uuid)
    formatted_str = UUID.formatted_string(name_based_uuid)

    print(f"Random UUID: {random_uuid}")
    print(f"UUID String: {uuid_string}")
    print(f"Hex UUID: {hex_uuid}")
    print(f"Is Valid: {is_valid}")
    print(f"Name-based UUID: {name_based_uuid}")
    print(f"UUID Version: {version}")
    print(f"Is Random UUID: {is_random}")
    print(f"Formatted UUID String: {formatted_str}")


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    """Main"""
    import doctest

    doctest.testmod()
    test()
