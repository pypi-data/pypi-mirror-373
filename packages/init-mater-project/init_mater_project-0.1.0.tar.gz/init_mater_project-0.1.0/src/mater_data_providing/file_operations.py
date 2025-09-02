"""
This module defines file operation functions.

SPDX-License-Identifier: LGPL-3.0-or-later
"""

import inspect
import json
import os
from pathlib import Path

from .constants import INPUT_DATA_DIR_PATH


def write_json(
    data: str | dict | list,
    name: str | None = None,
    input_data_directory_path: str | os.PathLike | None = None,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> str:
    """Write data to a JSON file in the specified directory.

    Processes input data and writes it to a JSON file with proper formatting and encoding.
    Automatically detects the calling file's name if no name is provided. Handles string
    data by parsing it as JSON first, while preserving dict and list data as-is.
    Creates the target directory if it doesn't exist and provides comprehensive error
    handling for file operations.

    :param data: The data to write to the JSON file. Can be a JSON string (will be parsed),
        a dictionary, or a list - any JSON-serializable object
    :type data: str | dict | list
    :param name: The name of the file (without .json extension). If None, automatically
        uses the calling file's name
    :type name: str | None
    :param input_data_directory_path: The directory path where the file will be created.
        If None, uses INPUT_DATA_DIR_PATH
    :type input_data_directory_path: str | os.PathLike | None
    :param indent: Number of spaces for JSON indentation
    :type indent: int
    :param ensure_ascii: If False, non-ASCII characters are preserved
    :type ensure_ascii: bool
    :return: The full path to the created JSON file
    :rtype: str
    :raises OSError: If directory creation or file writing fails
    :raises TypeError: If data is not JSON serializable
    :raises ValueError: If name is empty or contains invalid characters

    Examples
    --------
    Complete example with JSON file writing:

    **Writing dictionary data:**

    .. code-block:: python

        >>> # Write a dictionary to JSON
        >>> data = {"name": "John", "age": 30, "city": "Paris"}
        >>> file_path = write_json(data, "user_data")
        >>> print(file_path)
        '/path/to/input_data/user_data.json'

    **Expected file content:**

    .. code-block:: json

        {
          "name": "John",
          "age": 30,
          "city": "Paris"
        }

    **Writing JSON string data:**

    .. code-block:: python

        >>> # Write a JSON string (gets parsed first)
        >>> data = '{"name": "Jane", "age": 25, "country": "France"}'
        >>> file_path = write_json(data, "user_from_string")
        >>> print(file_path)
        '/path/to/input_data/user_from_string.json'

    **Writing list data:**

    .. code-block:: python

        >>> # Write a list to JSON
        >>> data = [
        ...     {"name": "Alice", "score": 95},
        ...     {"name": "Bob", "score": 87},
        ...     {"name": "Charlie", "score": 92}
        ... ]
        >>> file_path = write_json(data, "student_scores")

    **Automatic file naming:**

    .. code-block:: python

        >>> # Auto-detect file name from calling script
        >>> data = {"project": "MATER", "version": "1.0"}
        >>> file_path = write_json(data)  # Uses calling file name
        >>> # If called from 'main.py', creates 'main.json'

    **Custom formatting options:**

    .. code-block:: python

        >>> # Custom indentation and ASCII encoding
        >>> data = {"name": "François", "city": "Münich"}
        >>> file_path = write_json(
        ...     data,
        ...     "unicode_data",
        ...     indent=4,
        ...     ensure_ascii=False  # Preserves non-ASCII characters
        ... )

    **Expected file content with custom formatting:**

    .. code-block:: json

        {
            "name": "François",
            "city": "Münich"
        }

    **Custom directory path:**

    .. code-block:: python

        >>> # Write to custom directory
        >>> data = {"experiment": "test_01", "results": [1, 2, 3]}
        >>> file_path = write_json(
        ...     data,
        ...     "experiment_results",
        ...     input_data_directory_path="./custom_output"
        ... )

    **Usage:**

    .. code-block:: python

        >>> # Basic usage
        >>> file_path = write_json(data_dict, "output_file")
    """
    # Auto-detect name from calling file if not provided
    if name is None:
        # Get the calling frame (frame 1, since frame 0 is this function)
        caller_frame = inspect.currentframe().f_back
        caller_filename = caller_frame.f_globals.get("__file__")

        if caller_filename:
            # Extract filename without path and extension
            name = os.path.basename(caller_filename)
            if name.endswith(".py"):
                name = name[:-3]  # Remove .py extension
        else:
            # Fallback if we can't detect the filename
            name = "output"
    # Validate inputs
    if not name or not name.strip():
        raise ValueError("Name cannot be empty")

    # Remove any existing .json extension and sanitize name
    name = name.strip().replace(".json", "")
    if not name:
        raise ValueError("Name cannot be empty after sanitization")

    # Set directory path
    directory = (
        Path(input_data_directory_path)
        if input_data_directory_path
        else Path(INPUT_DATA_DIR_PATH)
    )

    # Create directory if it doesn't exist
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise OSError(f"Failed to create directory {directory}: {e}")

    # Construct file path
    file_path = directory / f"{name}.json"

    # Write JSON file
    try:
        if isinstance(data, str):
            data = json.loads(data)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
    except (TypeError, ValueError) as e:
        raise TypeError(f"Data is not JSON serializable: {e}")
    except OSError as e:
        raise OSError(f"Failed to write file {file_path}: {e}")

    return str(file_path)
