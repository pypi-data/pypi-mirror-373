import sys
import os
from urllib.parse import urlencode
current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.abspath(os.path.join(current_path, ".."))
sys.path.append(parent_path)

def execute_SQL_file_list(con, list_of_file_paths):
    """
    Execute a list of SQL files against the provided DuckDB connection.

    Parameters
    - con: duckdb connection object to execute SQL on.
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

def add_query_params_to_url(base_url, params):
    """
    Append query parameters to a base URL without parsing the URL first.

    - Skips parameters with value None.
    - Values are converted to strings and URL-encoded.
    - Preserves existing query separators on the base_url.

    Parameters
    - base_url: the URL string to append params to
    - params: mapping of keys to values (values of None are skipped)

    Returns
    - A new URL string with encoded query parameters appended.
    """
    if not params:
        return base_url

    cleaned_params = {}
    for name, value in params.items():
        if value is None:
            continue
        cleaned_params[str(name)] = str(value)

    if not cleaned_params:
        return base_url

    encoded_query = urlencode(cleaned_params, doseq=True)

    if base_url.endswith('?') or base_url.endswith('&'):
        separator = ''
    elif '?' in base_url:
        separator = '&'
    else:
        separator = '?'

    result = f"{base_url}{separator}{encoded_query}"
    return result


