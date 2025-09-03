# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - SQLite Server Module
============================

This module provides a simple SQLite server implementation using Python's
built-in sqlite3 library.

"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

import logging
import sqlite3

# Import | Standard Library
from typing import Any, List, Tuple

# Import | Libraries

# Import | Local Modules


# =============================================================================
# Classes
# =============================================================================


class SQLiteServer:
    """
    A SQLite3 server class for handling database operations with enhanced
    functionality.

    This class provides a simplified interface for interacting with SQLite
    databases, including methods for executing queries, handling transactions,
    and performing basic CRUD operations.

    Attributes
    ----------
        db_path (str): Path to the SQLite3 database file.

    Methods
    -------
        execute_query(query, params): Executes a SQL query with parameters.
        fetch_all(query, params): Fetches all rows from a SQL query.
        fetch_one(query, params): Fetches the first row from a SQL query.
        insert(table, data_dict): Inserts data into a table.
        update(table, data_dict, condition): Updates data in a table based on
        a condition.
        delete(table, condition): Deletes data from a table based on a condition.
        transaction(queries): Executes a series of queries in a transaction.
    """

    def __init__(self, db_path: str):
        """
        Initializes the SQLite3 server with the specified database path.

        Parameters:
            db_path (str): Path to the SQLite3 database file.
        """
        self.db_path = db_path
        logging.basicConfig(level=logging.INFO)

    def _execute(
        self, query: str, params: Tuple = (), commit: bool = False
    ) -> Any:
        """
        Private method to execute a SQL query.

        Parameters:
            query (str): SQL query to execute.
            params (Tuple): Parameters for the SQL query.
            commit (bool): Specifies whether to commit the transaction.

        Returns
        -------
            Any: Query result for 'SELECT' or None for other queries.

        Raises:
            sqlite3.Error: If an error occurs during query execution.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.execute(query, params)
                if commit:
                    conn.commit()
                else:
                    return (
                        cur.fetchall()
                        if query.strip().upper().startswith("SELECT")
                        else None
                    )
        except sqlite3.Error as e:
            logging.error("SQLite error: %s", e)
            raise

    def execute_query(self, query: str, params: Tuple = ()):
        """
        Executes a SQL query with parameters.

        Parameters:
            query (str): SQL query to execute.
            params (Tuple): Parameters for the SQL query.

        Returns
        -------
            None
        """
        self._execute(query, params, commit=True)

    def fetch_all(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """
        Fetches all rows from a SQL query.

        Parameters:
            query (str): SQL query to execute.
            params (Tuple): Parameters for the SQL query.

        Returns
        -------
            List[Tuple]: List of rows returned by the query.
        """
        return self._execute(query, params)

    def fetch_one(self, query: str, params: Tuple = ()) -> Tuple:
        """
        Fetches the first row from a SQL query.

        Parameters:
            query (str): SQL query to execute.
            params (Tuple): Parameters for the SQL query.

        Returns
        -------
            Tuple: The first row returned by the query.
        """
        return self._execute(query, params)[0]

    def insert(self, table: str, data_dict: dict):
        """
        Inserts a new row into a table.

        Parameters:
            table (str): Name of the table to insert data into.
            data_dict (dict): Dictionary containing column names and values.

        Returns
        -------
            None
        """
        columns = ", ".join(data_dict.keys())
        placeholders = ":" + ", :".join(data_dict.keys())
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self._execute(query, data_dict, commit=True)

    def update(self, table: str, data_dict: dict, condition: str):
        """
        Updates rows in a table.

        Parameters:
            table (str): Name of the table to update.
            data_dict (dict): Dictionary containing column names and values.
            condition (str): SQL condition for the update.

        Returns
        -------
            None
        """
        assignments = ", ".join([f"{k} = :{k}" for k in data_dict.keys()])
        query = f"UPDATE {table} SET {assignments} WHERE {condition}"
        self._execute(query, data_dict, commit=True)

    def delete(self, table: str, condition: str):
        """
        Deletes rows from a table.

        Parameters:
            table (str): Name of the table to delete from.
            condition (str): SQL condition for the deletion.

        Returns
        -------
            None
        """
        query = f"DELETE FROM {table} WHERE {condition}"
        self._execute(query, commit=True)

    def transaction(self, queries: List[Tuple[str, Tuple]]):
        """
        Executes a series of queries in a single transaction.

        Parameters:
            queries (List[Tuple[str, Tuple]]): A list of queries and their parameters.

        Raises:
            sqlite3.Error: If an error occurs during the transaction.
        """
        with sqlite3.connect(self.db_path) as conn:
            try:
                cur = conn.cursor()
                for query, params in queries:
                    cur.execute(query, params)
                conn.commit()
            except sqlite3.Error as e:
                conn.rollback()
                logging.error("Transaction failed: %s", e)
                raise


# =============================================================================
# Exports
# =============================================================================

__all__: List[str] = [
    "SQLiteServer",
]


# =============================================================================
# Functions
# =============================================================================


def test():
    """
    Test Function
    """

    # Example usage
    db_server = SQLiteServer("example.db")

    # Insert data
    db_server.insert("users", {"name": "Bob", "age": 25})

    # Update data
    db_server.update("users", {"age": 26}, "name = 'Bob'")

    # Fetch data
    print(db_server.fetch_all("SELECT * FROM users"))

    # Delete data
    db_server.delete("users", "name = 'Bob'")


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":

    import doctest

    doctest.testmod()
    test()
