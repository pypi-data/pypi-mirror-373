# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Provides JSONHandler Module
==========================



"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

import csv
import json

# Import | Standard Library
from typing import Any, Callable, Dict, List

# Import | Libraries
import xmltodict  # Requires installation: pip install xmltodict
import yaml

# Import | Local Modules


# =============================================================================
# Classes
# =============================================================================


class JSONHandler(object):
    """
    A class for handling JSON data operations.

    Methods
    -------
    --------
    read_json(file_path: str) -> Any:
        Reads JSON data from a file and returns it.
    write_json(file_path: str, data: Any, indent: int = 4):
        Writes JSON data to a file.
    validate_json(data: str) -> bool:
        Validates a JSON string.
    """

    @staticmethod
    def read_json(file_path: str) -> Any:
        """
        Reads JSON data from a file.

        Parameters:
            file_path (str): The path to the JSON file.

        Returns
        -------
            Any: The data read from the JSON file.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            print(f"Error reading JSON file: {e}")
            raise

    # def load_json(file):
    #     """
    #     """
    #     with open(file) as f:
    #         dict = json.load(f)
    #         return(dict)

    # @staticmethod
    # def load_json(path):
    #     """Load JSON."""
    #     f = open(path)
    #     data = json.loads(f.read())
    #     f.close()
    #     return data

    @staticmethod
    def write_json(file_path: str, data: Any, indent: int = 4):
        """
        Writes JSON data to a file.

        Parameters:
            file_path (str): The path to the JSON file.
            data (Any): The data to write to the file.
            indent (int): The indentation level for pretty-printing the JSON
            data.
        """
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=indent)
        except Exception as e:
            print(f"Error writing JSON file: {e}")
            raise

    @staticmethod
    def validate_json(data: str) -> bool:
        """
        Validates a JSON string.

        Parameters:
            data (str): The JSON string to validate.

        Returns
        -------
            bool: True if the string is valid JSON, False otherwise.
        """
        try:
            json.loads(data)
            return True
        except json.JSONDecodeError:
            return False

    @staticmethod
    def pretty_print_json(data: Any):
        """
        Pretty print JSON data.

        Parameters:
            data (Any): The JSON data to print.
        """
        print(json.dumps(data, indent=4, sort_keys=True))

    @staticmethod
    def merge_json(json1: Dict, json2: Dict) -> Dict:
        """
        Merge two JSON objects.

        Parameters:
            json1 (Dict): The first JSON object.
            json2 (Dict): The second JSON object.

        Returns
        -------
            Dict: Merged JSON object.
        """
        merged = {**json1, **json2}
        return merged

    @staticmethod
    def find_in_json(data: Dict, key: str) -> Any:
        """
        Search for a key in JSON data and return its value.

        Parameters:
            data (Dict): The JSON data to search in.
            key (str): The key to search for.

        Returns
        -------
            Any: The value of the found key or None.
        """
        if key in data:
            return data[key]
        for _, value in data.items():
            if isinstance(value, dict):
                result = JSONHandler.find_in_json(value, key)
                if result is not None:
                    return result
        return None

    @staticmethod
    def json_to_xml(json_data: Dict) -> str:
        """
        Convert JSON data to XML format.

        Parameters:
            json_data (Dict): The JSON data to convert.

        Returns
        -------
            str: The converted data in XML format.
        """
        return xmltodict.unparse(json_data)

    @staticmethod
    def xml_to_json(xml_data: str) -> Dict:
        """
        Convert XML data to JSON format.

        Parameters:
            xml_data (str): The XML data to convert.

        Returns
        -------
            Dict: The converted data in JSON format.
        """
        return xmltodict.parse(xml_data)

    @staticmethod
    def filter_json(data: Dict, filter_func: Callable[[Dict], bool]) -> Dict:
        """
        Filter JSON data based on a filter function.

        Parameters:
            data (Dict): The JSON data to filter.
            filter_func (Callable): A function that takes a dictionary and
            returns a boolean.

        Returns
        -------
            Dict: Filtered JSON data.
        """
        return {k: v for k, v in data.items() if filter_func({k: v})}

    @staticmethod
    def update_json(data: Dict, updates: Dict) -> Dict:
        """
        Update specific keys in a JSON object.

        Parameters:
            data (Dict): The original JSON data.
            updates (Dict): A dictionary with updates.

        Returns
        -------
            Dict: Updated JSON data.
        """
        data.update(updates)
        return data

    @staticmethod
    def flatten_json(data: Dict, parent_key: str = "", sep: str = ".") -> Dict:
        """
        Flatten a nested JSON object into a single level.

        Parameters:
            data (Dict): The JSON data to flatten.
            parent_key (str): The base key string.
            sep (str): Separator for nested keys.

        Returns
        -------
            Dict: The flattened JSON object.
        """
        items = []
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, Dict):
                items.extend(
                    JSONHandler.flatten_json(v, new_key, sep=sep).items()
                )
            else:
                items.append((new_key, v))
        return dict(items)

    @staticmethod
    def deep_merge_json(json1: Dict, json2: Dict) -> Dict:
        """
        Merge two JSON objects deeply.

        Parameters:
            json1 (Dict): The first JSON object.
            json2 (Dict): The second JSON object.

        Returns
        -------
            Dict: The deeply merged JSON object.
        """
        for key, value in json2.items():
            if key in json1:
                if isinstance(json1[key], Dict) and isinstance(value, Dict):
                    JSONHandler.deep_merge_json(json1[key], value)
                else:
                    json1[key] = value
            else:
                json1[key] = value
        return json1

    @staticmethod
    def json_to_yaml(json_data: Dict) -> str:
        """
        Convert JSON data to YAML format.

        Parameters:
            json_data (Dict): The JSON data to convert.

        Returns
        -------
            str: The converted data in YAML format.
        """
        return yaml.dump(json_data)

    @staticmethod
    def yaml_to_json(yaml_data: str) -> Dict:
        """
        Convert YAML data to JSON format.

        Parameters:
            yaml_data (str): The YAML data to convert.

        Returns
        -------
            Dict: The converted data in JSON format.
        """
        return yaml.safe_load(yaml_data)

    @staticmethod
    def sort_json(data: Dict, by_key=True, reverse=False) -> Dict:
        """
        Sort a JSON object based on keys or values.

        Parameters:
            data (Dict): The JSON data to sort.
            by_key (bool): Sort by keys if True, else by values.
            reverse (bool): Sort in reverse order if True.

        Returns
        -------
            Dict: The sorted JSON object.
        """
        return dict(
            sorted(
                data.items(),
                key=lambda item: item[0 if by_key else 1],
                reverse=reverse,
            )
        )

    @staticmethod
    def diff_json(json1: Dict, json2: Dict) -> Dict:
        """
        Find differences between two JSON objects.

        Parameters:
            json1 (Dict): The first JSON object.
            json2 (Dict): The second JSON object.

        Returns
        -------
            Dict: A dictionary showing differences.
        """
        diff = {}
        for key in json1:
            if key not in json2:
                diff[key] = f"Only in first: {json1[key]}"
            elif json1[key] != json2[key]:
                diff[key] = f"First: {json1[key]}, Second: {json2[key]}"
        for key in json2:
            if key not in json1:
                diff[key] = f"Only in second: {json2[key]}"
        return diff

    @staticmethod
    def extract_keys(data: Dict) -> List[str]:
        """
        Extract all keys from a JSON object.

        Parameters:
            data (Dict): The JSON data.

        Returns
        -------
            List[str]: A list of all keys in the JSON object.
        """
        keys = []
        for key, value in data.items():
            keys.append(key)
            if isinstance(value, dict):
                keys.extend(JSONHandler.extract_keys(value))
        return keys

    @staticmethod
    def json_to_csv(json_data: List[Dict], csv_file: str):
        """
        Convert JSON data to CSV format.

        Parameters:
            json_data (List[Dict]): The JSON data to convert.
            csv_file (str): The path to the CSV file to create.

        Note: Only works with flat JSON structures.
        """
        with open(csv_file, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=json_data[0].keys())
            writer.writeheader()
            for row in json_data:
                writer.writerow(row)

    @staticmethod
    def csv_to_json(csv_file: str) -> List[Dict]:
        """
        Convert CSV data to JSON format.

        Parameters:
            csv_file (str): The path to the CSV file to read.

        Returns
        -------
            List[Dict]: The converted data in JSON format.
        """
        with open(csv_file, "r", encoding="utf-8") as file:
            return list(csv.DictReader(file))

    @staticmethod
    def extract_from_path(json_data: Dict, path: str) -> Any:
        """
        Extract data from a JSON object using a specified path.

        Parameters:
            json_data (Dict): The JSON data.
            path (str): The path to extract data from (e.g., 'key1/key2').

        Returns
        -------
            Any: The extracted data.
        """
        elements = path.split("/")
        for elem in elements:
            json_data = json_data.get(elem)
            if json_data is None:
                return None
        return json_data

    @staticmethod
    def indent_json(json_data: Any, indent: int = 4) -> str:
        """
        Adjust the indentation of a JSON string.

        Parameters:
            json_data (Any): The JSON data to indent.
            indent (int): The number of spaces to use for indentation.

        Returns
        -------
            str: Indented JSON string.
        """
        return json.dumps(json_data, indent=indent)

    @staticmethod
    def compress_json(json_data: Any) -> str:
        """
        Compress JSON data by removing unnecessary spaces.

        Parameters:
            json_data (Any): The JSON data to compress.

        Returns
        -------
            str: Compressed JSON string.
        """
        return json.dumps(json_data, separators=(",", ":"))

    @staticmethod
    def transform_keys(
        json_data: Any, transform_func: Callable[[Any], Any]
    ) -> Any:
        """
        Apply a transformation to all keys in a JSON object.

        Parameters:
            json_data (Any): The JSON data.
            transform_func (Callable): The function to apply to each key.

        Returns
        -------
            Any: The JSON data with transformed keys.
        """
        if isinstance(json_data, dict):
            return {
                transform_func(k): JSONHandler.transform_keys(
                    v, transform_func
                )
                for k, v in json_data.items()
            }
        elif isinstance(json_data, list):
            return [
                JSONHandler.transform_keys(elem, transform_func)
                for elem in json_data
            ]
        else:
            return json_data

    @staticmethod
    def path_exists(json_data: Any, path: str) -> bool:
        """
        Check if a given path exists in the JSON data.

        Parameters:
            json_data (Any): The JSON data.
            path (str): The path to check (e.g., 'key1/key2').

        Returns
        -------
            bool: True if the path exists, False otherwise.
        """
        elements = path.split("/")
        for elem in elements:
            if isinstance(json_data, dict) and elem in json_data:
                json_data = json_data[elem]
            else:
                return False
        return True

    @staticmethod
    def nested_update(json_data: Any, path: str, value: Any) -> Any:
        """
        Update a value in a nested JSON structure based on a given path.

        Parameters:
            json_data (Any): The JSON data.
            path (str): The path to the value to update (e.g., 'key1/key2').
            value (Any): The new value to set.

        Returns
        -------
            Any: The updated JSON data.
        """
        elements = path.split("/")
        for i, elem in enumerate(elements):
            if i == len(elements) - 1:
                json_data[elem] = value
            else:
                json_data = json_data.setdefault(elem, {})
        return json_data

    @staticmethod
    def save_dict_to_json(data: dict, file_path: str, indent: int = 4):
        """
        Saves a dictionary to a JSON file.

        Parameters:
            data (dict): The dictionary to save.
            file_path (str): The path of the file where the JSON data will be
            saved.
            indent (int): The indentation level for pretty-printing the JSON
            data.
        """
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=indent)
        except Exception as e:
            print(f"Error saving dictionary to JSON file: {e}")
            raise


# =============================================================================
# Functions
# =============================================================================


def test():
    """
    Test Function
    """

    # Example usage
    json_data = {"name": "John Doe", "age": 30, "is_employee": True}

    # Write JSON to file
    JSONHandler.write_json("user.json", json_data)

    # Read JSON from file
    read_data = JSONHandler.read_json("user.json")
    print(read_data)

    # Validate JSON
    is_valid = JSONHandler.validate_json('{"name": "John Doe", "age": 30}')
    print(f"Is valid JSON: {is_valid}")

    # Pretty print JSON
    JSONHandler.pretty_print_json({"name": "John", "age": 30})

    # Merge JSON
    merged_json = JSONHandler.merge_json({"name": "John"}, {"age": 30})
    print(merged_json)

    # Find in JSON
    value = JSONHandler.find_in_json(
        {"person": {"name": "John", "age": 30}}, "age"
    )
    print(value)

    # Convert JSON to XML and back
    json_data = {"person": {"name": "John", "age": 30}}
    xml_data = JSONHandler.json_to_xml(json_data)
    print(xml_data)
    back_to_json = JSONHandler.xml_to_json(xml_data)
    print(back_to_json)

    # Filter JSON
    filtered_json = JSONHandler.filter_json(
        {"name": "John", "age": 30}, lambda x: x["age"] > 25
    )
    print(filtered_json)

    # Update JSON
    updated_json = JSONHandler.update_json(
        {"name": "John", "age": 30}, {"age": 31}
    )
    print(updated_json)

    # Flatten JSON
    flattened_json = JSONHandler.flatten_json(
        {"person": {"name": "John", "age": 30}}
    )
    print(flattened_json)

    # Deep Merge JSON
    merged_json = JSONHandler.deep_merge_json(
        {"person": {"name": "John", "age": 30}},
        {"person": {"age": 31, "city": "New York"}},
    )
    print(merged_json)

    # Convert JSON to YAML and back
    json_data = {"person": {"name": "John", "age": 30}}
    yaml_data = JSONHandler.json_to_yaml(json_data)
    print(yaml_data)
    back_to_json = JSONHandler.yaml_to_json(yaml_data)
    print(back_to_json)

    # Sort JSON
    sorted_json = JSONHandler.sort_json({"b": 2, "a": 1}, by_key=True)
    print(sorted_json)

    # Find differences between JSON objects
    diff = JSONHandler.diff_json({"a": 1, "b": 2}, {"b": 3, "c": 4})
    print(diff)

    # Extract keys from JSON
    keys = JSONHandler.extract_keys({"a": {"b": 2}, "c": 3})
    print(keys)

    # Convert JSON to CSV and back
    json_data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
    JSONHandler.json_to_csv(json_data, "data.csv")
    csv_to_json_data = JSONHandler.csv_to_json("data.csv")
    print(csv_to_json_data)

    # Extract data using path
    data = JSONHandler.extract_from_path({"a": {"b": {"c": 1}}}, "a/b/c")
    print(data)

    # Indent JSON
    json_data = {"name": "John", "age": 30}
    indented_json = JSONHandler.indent_json(json_data)
    print(indented_json)

    # Compress JSON
    compressed_json = JSONHandler.compress_json(json_data)
    print(compressed_json)

    # Transform Keys
    uppercased_json = JSONHandler.transform_keys(json_data, str.upper)
    print(uppercased_json)

    # Path Exists
    exists = JSONHandler.path_exists({"a": {"b": {"c": 1}}}, "a/b/c")
    print(exists)

    # Nested Update
    updated_json = JSONHandler.nested_update({"a": {"b": 1}}, "a/b", 2)
    print(updated_json)

    data_dict = {"name": "John Doe", "age": 30, "is_employee": True}

    # Save the dictionary to a JSON file
    JSONHandler.save_dict_to_json(data_dict, "data.json")


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    """Main"""
    import doctest

    doctest.testmod()
    test()
