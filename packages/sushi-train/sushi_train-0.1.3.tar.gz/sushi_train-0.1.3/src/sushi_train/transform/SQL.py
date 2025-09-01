import sys
import os
current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.abspath(os.path.join(current_path, ".."))
sys.path.append(parent_path)

def execute_SQL_file_list(con, list_of_file_paths):
    """
    Execute a list of SQL files against the provided DuckDB connection.

    Parameters
    - con: connection object to execute SQL on.
    - list_of_file_paths: iterable of file paths (relative to project parent) containing SQL statements.

    Raises
    - FileNotFoundError: if any SQL file is missing.
    - Exception: re-raises underlying execution errors.
    """
    for file_path in list_of_file_paths:
        full_path = os.path.join(parent_path, file_path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(full_path)

        with open(full_path, 'r') as file:
            sql = file.read()
        try:
            con.execute(sql)
        except Exception as e:
            raise

def execute_SQL_file(con, file_path):
    """
    Execute a list of SQL files against the provided DuckDB connection.

    Parameters
    - con: connection object to execute SQL on.
    - file_path: path to the SQL file to execute.

    Raises
    - FileNotFoundError: if the SQL file is missing.
    - Exception: re-raises underlying execution errors.
    """
    full_path = os.path.join(parent_path, file_path)
    if not os.path.exists(full_path):
        raise FileNotFoundError(full_path)

    with open(full_path, 'r') as file:
        sql = file.read()
    try:
        con.execute(sql)
    except Exception as e:
        raise