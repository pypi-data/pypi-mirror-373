"""
This module defines the serialization functions.

SPDX-License-Identifier: LGPL-3.0-or-later
"""

import json
import os
from typing import Dict

import pandas as pd

from .transformations import dimension_as_dict, replace_equivalence
from .validations import (
    validate_dumped_json,
    validate_input_data_full,
    validate_metadata,
    validate_provider,
)


def dump_json(
    input_data: pd.DataFrame,
    provider: Dict[str, str],
    metadata: Dict[str, str],
    vardim_file_path: str | os.PathLike | None = None,
    dimension_file_path: str | os.PathLike | None = None,
) -> str:
    """Serialize input dataframe, provider info, and metadata into standardized JSON format.

    This is the final step in the data providing pipeline that creates a complete
    data package with provenance information.

    :param input_data: A dataframe with the right columns
    :type input_data: pd.DataFrame
    :param provider: The provider dictionnary from provider_definition()
    :type provider: Dict[str, str]
    :param metadata: The metadata dictionnary from metadata_definition()
    :type metadata: Dict[str, str]
    :param vardim_file_path: Path to variable_dimension.json file for validation
    :type vardim_file_path: str | os.PathLike | None
    :return: Formatted JSON string containing the complete data package
    :rtype: str

    Examples
    --------
    Complete example with JSON serialization:

    **Input data preparation:**

    .. code-block:: python

        >>> import pandas as pd
        >>> input_data = pd.DataFrame([
        ...     {
        ...         "location": "france",
        ...         "object": "car",
        ...         "value": 15,
        ...         "unit": "year",
        ...         "time": 2015,
        ...         "scenario": "historical",
        ...         "variable": "lifetime_mean_value"
        ...     }
        ... ])
        >>>
        >>> provider = {
        ...     "first_name": "Jon",
        ...     "last_name": "Do",
        ...     "email_address": "jon.do@mail.com"
        ... }
        >>>
        >>> metadata = {
        ...     "link": "source_link",
        ...     "source": "my_source",
        ...     "project": "my_project"
        ... }

    **Expected JSON output:**

    .. code-block:: json

        {
            "input_data": [
                {
                    "location": "france",
                    "object": "car",
                    "value": 15,
                    "unit": "year",
                    "time": 2015,
                    "scenario": "historical",
                    "variable": "lifetime_mean_value"
                }
            ],
            "provider": {
                "first_name": "Jon",
                "last_name": "Do",
                "email_address": "jon.do@mail.com"
            },
            "metadata": {
                "link": "source_link",
                "source": "my_source",
                "project": "my_project"
            }
        }

    **Multiple rows example:**

    .. code-block:: python

        >>> # DataFrame with multiple entries
        >>> input_data_multi = pd.DataFrame([
        ...     {
        ...         "location": "france",
        ...         "object": "car",
        ...         "value": 15,
        ...         "unit": "year",
        ...         "time": 2015,
        ...         "scenario": "historical",
        ...         "variable": "lifetime_mean_value"
        ...     },
        ...     {
        ...         "location": "germany",
        ...         "object": "truck",
        ...         "value": 20,
        ...         "unit": "year",
        ...         "time": 2020,
        ...         "scenario": "projection",
        ...         "variable": "lifetime_max_value"
        ...     }
        ... ])
        >>>
        >>> json_output = dump_json(input_data_multi, provider, metadata)
        >>> print(json_output)

    **Usage:**

    .. code-block:: python

        >>> # Basic serialization
        >>> json_string = dump_json(input_data, provider, metadata)

        >>> # With custom variable dimension file
        >>> json_string = dump_json(
        ...     input_data,
        ...     provider,
        ...     metadata,
        ...     vardim_file_path="custom/variable_dimension.json"
        ... )

        >>> # Save to file
        >>> json_string = dump_json(input_data, provider, metadata)
        >>> with open("output_data.json", "w") as f:
        ...     f.write(json_string)

        >>> # Parse back to dictionary
        >>> import json
        >>> json_string = dump_json(input_data, provider, metadata)
        >>> data_dict = json.loads(json_string)
        >>> print(data_dict.keys())
        dict_keys(['input_data', 'provider', 'metadata'])
    """
    # Validate arguments structure
    validate_input_data_full(
        input_data,
        vardim_file_path=vardim_file_path,
        dimension_file_path=dimension_file_path,
    )
    validate_provider(provider)
    validate_metadata(metadata)

    data = {
        "input_data": input_data.to_dict(orient="records"),
        "provider": provider,
        "metadata": metadata,
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def standardize_json(
    data: str,
    vardim_file_path: str | os.PathLike | None = None,
    dimension_file_path: str | os.PathLike | None = None,
    validation: bool = True,
) -> str:
    """Standardize and transform JSON data for MATER processing pipeline.

    Takes JSON data from any source (dump_json, external APIs, other languages)
    and transforms it into the final MATER format with dimension standardization
    and equivalence replacement.

    :param data: JSON string to parse, validate and transform
    :type data: str
    :param validation: Whether to validate JSON structure before processing
    :type validation: bool, default to True
    :return: Standardized JSON string ready for MATER processing
    :rtype: str
    :raises ValueError: If validation enabled and JSON structure is invalid
    :raises json.JSONDecodeError: If data is not valid JSON

    Examples
    --------
    Complete example with JSON standardization:

    **Processing steps performed:**

    1. Validates JSON structure (optional)
    2. Replaces equivalences using dimension.json
    3. Transforms dimensions into JSON format
    4. Returns standardized JSON ready for processing

    **Input JSON with equivalences:**

    .. code-block:: json

        {
            "input_data": [
                {
                    "location": "FR",
                    "object": "PLDV",
                    "value": 15,
                    "unit": "year",
                    "time": 2015,
                    "scenario": "historical",
                    "variable": "lifetime_mean_value"
                }
            ],
            "provider": {
                "first_name": "Jon",
                "last_name": "Do",
                "email_address": "jon.do@mail.com"
            },
            "metadata": {
                "link": "source_link",
                "source": "my_source",
                "project": "my_project"
            }
        }

    **Expected standardized output:**

    .. code-block:: json

        {
            "input_data": [
                {
                    "location": "france",
                    "object": "car",
                    "value": 15,
                    "unit": "year",
                    "time": 2015,
                    "scenario": "historical",
                    "variable": "lifetime_mean_value"
                }
            ],
            "provider": {
                "first_name": "Jon",
                "last_name": "Do",
                "email_address": "jon.do@mail.com"
            },
            "metadata": {
                "link": "source_link",
                "source": "my_source",
                "project": "my_project"
            }
        }

    **Usage:**

    .. code-block:: python

        >>> # Basic standardization with validation
        >>> raw_json = '{"input_data": [...], "provider": {...}, "metadata": {...}}'
        >>> standardized = standardize_json(raw_json)
        >>> # Now ready for database or processing pipeline

        >>> # Skip validation for trusted sources (faster processing)
        >>> trusted_json = dump_json(df, provider, metadata)
        >>> standardized = standardize_json(trusted_json, validation=False)
    """
    if validation:
        validate_dumped_json(
            data,
            vardim_file_path=vardim_file_path,
            dimension_file_path=dimension_file_path,
        )

    parsed_data = json.loads(data)
    transformed_df = dimension_as_dict(
        replace_equivalence(
            pd.DataFrame(parsed_data["input_data"]), dimension_file_path
        )
    )
    parsed_data["input_data"] = transformed_df.to_dict(orient="records")

    return json.dumps(parsed_data, indent=2, ensure_ascii=False)


def to_mater_json(
    input_data: pd.DataFrame,
    provider: Dict[str, str],
    metadata: Dict[str, str],
    vardim_file_path: str | os.PathLike | None = None,
    dimension_file_path: str | os.PathLike | None = None,
) -> str:
    """Complete end-to-end pipeline from DataFrame and dict to MATER-ready JSON.

    This is the main high-level function that combines all processing steps:
    data validation, serialization, equivalence replacement, and dimension
    transformation into a single call.

    :param input_data: DataFrame with valid MATER structure
    :type input_data: pd.DataFrame
    :param provider: Provider information dictionary
    :type provider: Dict[str, str]
    :param metadata: Metadata information dictionary
    :type metadata: Dict[str, str]
    :return: Fully processed JSON ready for MATER database
    :rtype: str
    :raises TypeError: If input_data is not a pandas DataFrame
    :raises ValueError: If DataFrame, provider, or metadata structure is invalid

    Examples
    --------
    Complete example with end-to-end processing:

    **Processing pipeline equivalent:**

    This function is equivalent to:

    1. ``dump_json(input_data, provider, metadata)``
    2. ``standardize_json(result, validation=False)``

    **Input data preparation:**

    .. code-block:: python

        >>> import pandas as pd
        >>> df = pd.DataFrame([
        ...     {
        ...         "location": "france",
        ...         "object": "car",
        ...         "value": 15,
        ...         "unit": "year",
        ...         "time": 2015,
        ...         "scenario": "historical",
        ...         "variable": "lifetime_mean_value"
        ...     }
        ... ])
        >>>
        >>> provider = {
        ...     "first_name": "John",
        ...     "last_name": "Doe",
        ...     "email_address": "john@example.com"
        ... }
        >>>
        >>> metadata = {
        ...     "link": "source.com",
        ...     "source": "Research",
        ...     "project": "Study"
        ... }

    **Expected MATER-ready JSON output:**

    .. code-block:: json

        {
            "input_data": [
                {
                    "location": "france",
                    "object": "car",
                    "value": 15,
                    "unit": "year",
                    "time": 2015,
                    "scenario": "historical",
                    "variable": "lifetime_mean_value"
                }
            ],
            "provider": {
                "first_name": "John",
                "last_name": "Doe",
                "email_address": "john@example.com"
            },
            "metadata": {
                "link": "source.com",
                "source": "Research",
                "project": "Study"
            }
        }

    **Multiple entries example:**

    .. code-block:: python

        >>> # DataFrame with multiple rows and equivalences
        >>> df_multi = pd.DataFrame([
        ...     {
        ...         "location": "FR",  # Will be standardized to "france"
        ...         "object": "PLDV",  # Will be standardized to "car"
        ...         "value": 15,
        ...         "unit": "year",
        ...         "time": 2015,
        ...         "scenario": "historical",
        ...         "variable": "lifetime_mean_value"
        ...     },
        ...     {
        ...         "location": "germany",
        ...         "object": "truck",
        ...         "value": 20,
        ...         "unit": "year",
        ...         "time": 2020,
        ...         "scenario": "projection",
        ...         "variable": "lifetime_max_value"
        ...     }
        ... ])
        >>>
        >>> mater_json = to_mater_json(df_multi, provider, metadata)

    **Usage:**

    .. code-block:: python

        >>> # Basic end-to-end processing
        >>> mater_json = to_mater_json(df, provider, metadata)
        >>> # Ready for processing pipeline or database insertion
    """
    return standardize_json(
        dump_json(
            input_data,
            provider,
            metadata,
            vardim_file_path=vardim_file_path,
            dimension_file_path=dimension_file_path,
        ),
        vardim_file_path=vardim_file_path,
        dimension_file_path=dimension_file_path,
        validation=False,
    )
