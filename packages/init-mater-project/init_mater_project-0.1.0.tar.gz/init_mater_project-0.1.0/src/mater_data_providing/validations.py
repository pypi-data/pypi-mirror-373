"""
This module defines variable type and structure validation functions.

SPDX-License-Identifier: LGPL-3.0-or-later
"""

import json
import os
from typing import Dict

import pandas as pd
from email_validator import validate_email

from .constants import (
    ASPECT_COLUMNS,
    DIMENSION_FILE_PATH,
    DIMENSION_NAMES,
    DIMENSION_OPTIONAL_KEYS,
    DIMENSION_REQUIRED_KEYS,
    PROPERTY_VALUES,
    REQUIRED_COLUMNS,
    VARIABLE_DIMENSION_FILE_PATH,
    VARIABLE_DIMENSION_REQUIRED_KEYS,
)
from .helpers import _process_dimension_equivalence, explode_dict_to_column


def validate_provider(provider: Dict[str, str]) -> Dict[str, str]:
    """Check the right keys and validate email and strings in provider dictionary.

    :param provider: Provider dictionary to validate
    :type provider: Dict[str, str]
    :return: Validated and normalized provider dictionary
    :rtype: Dict[str, str]
    :raises ValueError: If provider structure is invalid

    Examples
    --------
    Complete example with provider validation:

    **Valid provider structure:**

    .. code-block:: python

        >>> # Valid provider example
        >>> provider = {
        ...     "first_name": "John",
        ...     "last_name": "Doe",
        ...     "email_address": "john.doe@example.com"
        ... }
        >>> validated_provider = validate_provider(provider)
        >>> print(validated_provider)
        {
            'first_name': 'John',
            'last_name': 'Doe',
            'email_address': 'john.doe@example.com'
        }

    **Provider with whitespace (gets normalized):**

    .. code-block:: python

        >>> provider_with_whitespace = {
        ...     "first_name": "    John    ",
        ...     "last_name": "  Doe  ",
        ...     "email_address": "john.doe@example.com"
        ... }
        >>> validated_provider = validate_provider(provider_with_whitespace)
        >>> print(validated_provider)
        {
            'first_name': 'John',
            'last_name': 'Doe',
            'email_address': 'john.doe@example.com'
        }

    **Examples that would fail validation:**

    .. code-block:: python

        >>> # Missing required keys
        >>> invalid_provider_1 = {
        ...     "first_name": "John",
        ...     "last_name": "Doe"
        ...     # Missing 'email_address'
        ... }
        >>> validate_provider(invalid_provider_1)
        ValueError: Missing required provider keys: {'email_address'}

        >>> # Invalid email format
        >>> invalid_provider_2 = {
        ...     "first_name": "John",
        ...     "last_name": "Doe",
        ...     "email_address": "invalid-email-format"
        ... }
        >>> validate_provider(invalid_provider_2)
        ValueError: Invalid email address format: 'invalid-email-format'

        >>> # Empty strings
        >>> invalid_provider_3 = {
        ...     "first_name": "",
        ...     "last_name": "Doe",
        ...     "email_address": "john.doe@example.com"
        ... }
        >>> validate_provider(invalid_provider_3)
        ValueError: Provider values cannot be empty strings

        >>> # Invalid value types
        >>> invalid_provider_4 = {
        ...     "first_name": "John",
        ...     "last_name": "Doe",
        ...     "email_address": 123  # Should be string
        ... }
        >>> validate_provider(invalid_provider_4)
        ValueError: All provider values must be strings

    **Usage:**

    .. code-block:: python

        >>> # Basic validation
        >>> validated = validate_provider(provider_dict)

        >>> # Use in data pipeline
        >>> try:
        ...     clean_provider = validate_provider(user_provider)
        ...     # Continue with pipeline
        ... except ValueError as e:
        ...     print(f"Provider validation failed: {e}")

        >>> # Validate multiple providers
        >>> providers = [provider1, provider2, provider3]
        >>> validated_providers = []
        >>> for provider in providers:
        ...     try:
        ...         validated_providers.append(validate_provider(provider))
        ...     except ValueError as e:
        ...         print(f"Skipping invalid provider: {e}")
    """
    # check type
    if not isinstance(provider, dict):
        raise TypeError(f"must be a dictionary, got {type(provider).__name__}")

    required_fields = {"first_name", "last_name", "email_address"}
    actual_fields = set(provider.keys())

    missing_fields = required_fields - actual_fields
    if missing_fields:
        raise ValueError(f"Missing required provider fields: {sorted(missing_fields)}")

    extra_fields = actual_fields - required_fields
    if extra_fields:
        raise ValueError(f"Unexpected provider fields: {sorted(extra_fields)}")

    # validate each field
    _validate_string(provider["first_name"])
    _validate_string(provider["last_name"])
    validate_email(provider["email_address"], check_deliverability=False)


def validate_metadata(metadata: Dict[str, str]) -> Dict[str, str]:
    """Check the right keys and validate strings in metadata dictionary.

    :param metadata: Metadata dictionary to validate
    :type metadata: Dict[str, str]
    :return: Validated and normalized metadata dictionary
    :rtype: Dict[str, str]
    :raises ValueError: If metadata structure is invalid

    Examples
    --------
    Complete example with metadata validation:

    **Valid metadata structure:**

    .. code-block:: python

        >>> # Valid metadata example
        >>> metadata = {
        ...     "link": "https://data.example.com/dataset.csv",
        ...     "source": "European Environment Agency",
        ...     "project": "Carbon Footprint Analysis 2024"
        ... }
        >>> validated_metadata = validate_metadata(metadata)
        >>> print(validated_metadata)
        {
            'link': 'https://data.example.com/dataset.csv',
            'source': 'European Environment Agency',
            'project': 'Carbon Footprint Analysis 2024'
        }

    **Metadata with whitespace (gets normalized):**

    .. code-block:: python

        >>> metadata_with_whitespace = {
        ...     "link": "    https://data.example.com/dataset.csv    ",
        ...     "source": "  European Environment Agency  ",
        ...     "project": "Carbon Footprint Analysis 2024"
        ... }
        >>> validated_metadata = validate_metadata(metadata_with_whitespace)
        >>> print(validated_metadata)
        {
            'link': 'https://data.example.com/dataset.csv',
            'source': 'European Environment Agency',
            'project': 'Carbon Footprint Analysis 2024'
        }

    **Examples that would fail validation:**

    .. code-block:: python

        >>> # Missing required keys
        >>> invalid_metadata_1 = {
        ...     "link": "https://data.example.com/dataset.csv"
        ...     # Missing 'source' and 'project'
        ... }
        >>> validate_metadata(invalid_metadata_1)
        ValueError: Missing required metadata keys: {'source', 'project'}

        >>> # Invalid key types
        >>> invalid_metadata_2 = {
        ...     "link": "https://data.example.com/dataset.csv",
        ...     "source": "European Environment Agency",
        ...     "project": 123  # Should be string
        ... }
        >>> validate_metadata(invalid_metadata_2)
        ValueError: All metadata values must be strings

        >>> # Empty strings
        >>> invalid_metadata_3 = {
        ...     "link": "",
        ...     "source": "European Environment Agency",
        ...     "project": "Carbon Footprint Analysis 2024"
        ... }
        >>> validate_metadata(invalid_metadata_3)
        ValueError: Metadata values cannot be empty strings

    **Usage:**

    .. code-block:: python

        >>> # Basic validation
        >>> validated = validate_metadata(metadata_dict)

        >>> # Use in data pipeline
        >>> try:
        ...     clean_metadata = validate_metadata(user_metadata)
        ...     # Continue with pipeline
        ... except ValueError as e:
        ...     print(f"Metadata validation failed: {e}")
    """
    # check type
    if not isinstance(metadata, dict):
        raise TypeError(f"must be a dictionary, got {type(metadata).__name__}")

    required_fields = {"link", "source", "project"}
    actual_fields = set(metadata.keys())

    missing_fields = required_fields - actual_fields
    if missing_fields:
        raise ValueError(f"Missing required metadata fields: {sorted(missing_fields)}")

    extra_fields = actual_fields - required_fields
    if extra_fields:
        raise ValueError(f"Unexpected metadata fields: {sorted(extra_fields)}")

    # Validate each field
    for field in required_fields:
        _validate_string(metadata[field])


def validate_input_data_structure(
    input_data: pd.DataFrame,
    required_columns: set | None = None,
    aspect_columns: set | None = None,
) -> set:
    """Check format and columns of DataFrame for MATER data pipeline.

    Validates that the DataFrame has the correct structure with required columns
    and at least one aspect column. Returns the set of present aspect columns.

    :param input_data: DataFrame to validate
    :type input_data: pd.DataFrame
    :param required_columns: Set of required column names (uses REQUIRED_COLUMNS if None)
    :type required_columns: set | None
    :param aspect_columns: Set of aspect column names (uses ASPECT_COLUMNS if None)
    :type aspect_columns: set | None
    :return: Set of aspect columns present in the DataFrame
    :rtype: set
    :raises TypeError: If input_data is not a pandas DataFrame or if column sets are invalid
    :raises ValueError: If DataFrame structure is invalid

    Examples
    --------
    Complete example with DataFrame structure validation:

    **Basic usage with default column requirements:**

    .. code-block:: python

        >>> import pandas as pd
        >>> from mater_data_providing.validations import validate_input_data_structure
        >>>
        >>> # Create valid DataFrame
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
        >>> # Validate with default requirements
        >>> present_aspects = validate_input_data_structure(df)
        >>> print(present_aspects)
        {'location', 'object'}

    **Usage with custom column requirements:**

    .. code-block:: python

        >>> # Custom requirements for specific validation
        >>> custom_required = {"value", "unit", "time"}
        >>> custom_aspects = {"location", "process"}
        >>>
        >>> df_custom = pd.DataFrame([
        ...     {
        ...         "location": "germany",
        ...         "value": 20,
        ...         "unit": "kg",
        ...         "time": 2024
        ...     }
        ... ])
        >>>
        >>> present_aspects = validate_input_data_structure(
        ...     df_custom,
        ...     required_columns=custom_required,
        ...     aspect_columns=custom_aspects
        ... )
        >>> print(present_aspects)
        {'location'}

    **DataFrame with multiple aspect columns:**

    .. code-block:: python

        >>> df_multi = pd.DataFrame([
        ...     {
        ...         "location": "spain",
        ...         "object": "truck",
        ...         "process": "manufacturing",
        ...         "value": 25,
        ...         "unit": "year",
        ...         "time": 2020,
        ...         "scenario": "projection",
        ...         "variable": "lifetime_estimate"
        ...     }
        ... ])
        >>>
        >>> present_aspects = validate_input_data_structure(df_multi)
        >>> print(present_aspects)
        {'location', 'object', 'process'}

    **Return value:**

    The function returns a set containing the names of aspect columns found in the DataFrame.
    This can be used for further validation or processing steps in the MATER pipeline.

    **Usage:**

    .. code-block:: python

        >>> # Basic validation
        >>> aspect_cols = validate_input_data_structure(df)

        >>> # With custom parameters
        >>> aspect_cols = validate_input_data_structure(
        ...     df,
        ...     required_columns={"value", "unit"},
        ...     aspect_columns={"location", "object", "process"}
        ... )

        >>> # Use returned aspect columns for further processing
        >>> print(f"Found {len(aspect_cols)} aspect columns: {aspect_cols}")
    """
    if not isinstance(input_data, pd.DataFrame):
        raise TypeError("input_data must be a pandas DataFrame")

    if not isinstance(required_columns, (set, type(None))):
        raise TypeError("required_columns must be a set or None")

    if not isinstance(aspect_columns, (set, type(None))):
        raise TypeError("aspect_columns must be a set or None")

    # Check if DataFrame is empty
    if input_data.empty:
        raise ValueError("DataFrame cannot be empty")

    # Validate index structure - should have default RangeIndex
    if not isinstance(input_data.index, pd.RangeIndex):
        raise ValueError(
            "DataFrame must have a default RangeIndex (use .reset_index() if needed)"
        )

    # Required columns that must always be present
    requ_cols = required_columns or REQUIRED_COLUMNS

    # At least one of these aspect columns must be present
    asp_cols = aspect_columns or ASPECT_COLUMNS

    # Get actual columns from DataFrame
    actual_columns = set(input_data.columns)

    # Check for missing required columns
    missing_required = requ_cols - actual_columns
    if missing_required:
        raise ValueError(f"Missing required columns: {sorted(missing_required)}")

    # Check for at least one aspect column
    present_aspect = asp_cols & actual_columns
    if not present_aspect:
        raise ValueError(
            f"At least one aspect column is required from: {sorted(asp_cols)}"
        )

    # Check invalid column names
    valid_columns = requ_cols | asp_cols
    invalid_columns = actual_columns - valid_columns
    if invalid_columns:
        raise ValueError(
            f"Invalid column names: {sorted(invalid_columns)}. "
            f"Valid column names: {sorted(valid_columns)}"
        )

    return present_aspect


def validate_aspect_elements(
    df: pd.DataFrame, dimension_file_path: str | os.PathLike | None = None
):
    """Check if aspect elements of a validated input_data DataFrame exist in dimension.json 'value' or 'equivalence' columns.

    This function validates that all aspect column values in the DataFrame are either:
    1. Present in the 'value' column of dimension.json for the corresponding aspect
    2. Present as keys in the 'equivalence' dictionaries for the corresponding aspect

    :param df: Validated input_data DataFrame with aspect columns
    :type df: pd.DataFrame
    :param dimension_file_path: Path to dimension.json file (optional, uses default if None)
    :type dimension_file_path: str | os.PathLike | None
    :raises ValueError: If any aspect elements are not found in dimension.json
    :raises FileNotFoundError: If dimension.json file is not found
    :raises ValidationError: If DataFrame structure is invalid

    Examples
    --------
    Complete example with aspect element validation:

    **Example input DataFrame:**

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
        ...         "variable": "lifetime_mean"
        ...     },
        ...     {
        ...         "location": "FR",
        ...         "object": "PLDV",
        ...         "value": 17,
        ...         "unit": "year",
        ...         "time": 2020,
        ...         "scenario": "projection",
        ...         "variable": "lifetime_max"
        ...     }
        ... ])

    **Required dimension.json file structure:**

    .. code-block:: json

        [
            {
                "name": "location",
                "value": "france",
                "equivalence": {"equ1": "FR", "equ2": "FRA"}
            },
            {
                "name": "location",
                "value": "germany",
                "equivalence": {"equ1": "GE", "equ2": "DEU"}
            },
            {
                "name": "object",
                "value": "car",
                "equivalence": {"equ1": "PLDV", "equ2": "auto"}
            },
            {
                "name": "object",
                "value": "truck",
                "equivalence": {"equ1": "HV", "equ2": "heavy_vehicle"}
            }
        ]

    **Validation logic:**

    The function will pass validation because:

    - "france" exists in location values
    - "FR" exists in location equivalence (equ1: "FR")
    - "car" exists in object values
    - "PLDV" exists in object equivalence (equ1: "PLDV")

    **Usage:**

    .. code-block:: python

        >>> # Uses default dimension file path
        >>> validate_aspect_elements(df)

        >>> # Custom path
        >>> validate_aspect_elements(df, "custom/path/dimension.json")

    **Example that would fail validation:**

    .. code-block:: python

        >>> df_invalid = pd.DataFrame([
        ...     {
        ...         "location": "unknown_country",
        ...         "object": "car",
        ...         "value": 15,
        ...         "unit": "year",
        ...         "time": 2015,
        ...         "scenario": "historical",
        ...         "variable": "lifetime_mean"
        ...     }
        ... ])
        >>> validate_aspect_elements(df_invalid)
        ValueError: Invalid elements in location column: ['unknown_country'].
        Add them as equivalences or new value entries in the dimension.json file.
    """
    # validate df structure and get the aspect columns
    asp_cols = validate_input_data_structure(df)
    # validate dimension json
    validate_dimension_file(dimension_file_path=dimension_file_path)
    # read dimension json
    dim_path = dimension_file_path or DIMENSION_FILE_PATH
    dimension = pd.read_json(dim_path, orient="records")
    # check for each aspect of df
    for aspect in asp_cols:
        df_elements = set(df[aspect].dropna())
        dimension_subset = dimension[dimension["name"] == aspect.split("_")[0]]

        dimension_elements = set(dimension_subset["value"])
        if "equivalence" in dimension_subset.columns:
            # Ensure multiple keys in 'equivalence' dictionaries are handled correctly
            #### ToDo change _process_dimension_equivalence to return the entire dataframe so that we can call it only once
            #### and then filter by aspect
            _, series_exploded = _process_dimension_equivalence(dimension_subset)
            equivalence_elements = set(series_exploded)
            dimension_elements = dimension_elements | equivalence_elements
        invalid_elements = df_elements - dimension_elements
        if invalid_elements:
            raise ValueError(
                f"Invalid elements in {aspect} column: {sorted(invalid_elements)}. "
                f"Add them as equivalences or new value entries in the {dim_path} file."
            )


def validate_dimension_file(
    dimension_json: str | None = None,
    dimension_file_path: str | os.PathLike | None = None,
    dimension_names: set | None = None,
    required_keys: set | None = None,
    optional_keys: set | None = None,
):
    """Validate the structure and content of a dimension.json file.

    Validates that the dimension file has the correct structure, required columns,
    valid data types, and proper relationships between elements.

    :param dimension_json: JSON string to validate (alternative to file path)
    :type dimension_json: str | None
    :param dimension_file_path: Path to dimension.json file to validate
    :type dimension_file_path: str | os.PathLike | None
    :param dimension_names: Valid dimension names (uses default if None)
    :type dimension_names: set | None
    :param required_keys: Required column names (uses default if None)
    :type required_keys: set | None
    :param optional_keys: Optional column names (uses default if None)
    :type optional_keys: set | None
    :raises TypeError: If parameter types are incorrect
    :raises ValueError: If file structure or content is invalid
    :raises KeyError: If required values are missing

    Examples
    --------
    Complete example with dimension file validation:

    **Validation checks performed:**

    - Required columns are present
    - No invalid columns
    - 'value' and 'name' columns have no missing values
    - All dimension names are valid
    - 'equivalence' and 'parents_values' are dictionaries
    - Parent values reference existing values

    **Required file structure for data/dimension/dimension.json:**

    .. code-block:: json

        [
            {
                "name": "location",
                "value": "france",
                "equivalence": {"equ1": "FR", "equ2": "FRA"}
            },
            {
                "name": "location",
                "value": "germany",
                "equivalence": {"equ1": "GE", "equ2": "DEU"}
            },
            {
                "name": "object",
                "value": "car",
                "equivalence": {"equ1": "PLDV", "equ2": "auto"},
                "parents_values": {"location": ["france", "germany"]}
            },
            {
                "name": "object",
                "value": "truck",
                "equivalence": {"equ1": "HV", "equ2": "heavy_vehicle"}
            },
            {
                "name": "process",
                "value": "manufacturing",
                "equivalence": {"equ1": "manuf", "equ2": "production"}
            }
        ]

    **Usage:**

    .. code-block:: python

        >>> # Validate default dimension file
        >>> validate_dimension_file()

        >>> # Validate specific file
        >>> validate_dimension_file(dimension_file_path="custom/dimension.json")

        >>> # Validate JSON string directly
        >>> json_str = '''[
        ...     {
        ...         "name": "location",
        ...         "value": "france",
        ...         "equivalence": {"equ1": "FR"}
        ...     }
        ... ]'''
        >>> validate_dimension_file(dimension_json=json_str)

        >>> # Validate with custom parameters
        >>> custom_dimensions = {"location", "object"}
        >>> custom_required = {"name", "value"}
        >>> custom_optional = {"equivalence", "parents_values", "description"}
        >>> validate_dimension_file(
        ...     dimension_file_path="custom/dimension.json",
        ...     dimension_names=custom_dimensions,
        ...     required_keys=custom_required,
        ...     optional_keys=custom_optional
        ... )
    """
    if not isinstance(dimension_names, (set, type(None))):
        raise TypeError(
            f"dimension_names must be a set or None to get the default set: {DIMENSION_NAMES}"
        )

    if not isinstance(required_keys, (set, type(None))):
        raise TypeError(
            f"required_keys must be a set or None to get the default set: {DIMENSION_REQUIRED_KEYS}"
        )

    if not isinstance(optional_keys, (set, type(None))):
        raise TypeError(
            f"optional_keys must be a set or None to get the default set: {DIMENSION_OPTIONAL_KEYS}"
        )
    # read dimension json
    if dimension_json:
        dimension = json.loads(dimension_json)
    else:
        dim_path = dimension_file_path or DIMENSION_FILE_PATH
        dimension = pd.read_json(dim_path, orient="records")
    # structure validation
    dim_df = pd.DataFrame(dimension)
    requ_keys = required_keys or DIMENSION_REQUIRED_KEYS
    opt_keys = optional_keys or DIMENSION_OPTIONAL_KEYS
    actual_keys = set(dim_df.columns)
    # Check for missing required keys
    missing_required = requ_keys - actual_keys
    if missing_required:
        raise KeyError(
            f"Missing required keys in dimension.json: {sorted(missing_required)}"
        )
    # Check invalid column names
    valid_keys = requ_keys | opt_keys
    invalid_keys = actual_keys - valid_keys
    if invalid_keys:
        raise KeyError(
            f"Invalid keys in dimension.json: {sorted(invalid_keys)}. Valid keys: {sorted(valid_keys)}"
        )
    # check for missing value
    missing_value_df = dim_df[dim_df["value"].isna()]
    if not missing_value_df.empty:
        raise KeyError(
            f"Missing one or more 'value' keys in dimension.json \n{str(missing_value_df)}"
        )
    # check for missing name
    missing_name_df = dim_df[dim_df["name"].isna()]
    if not missing_name_df.empty:
        raise KeyError(
            f"Missing one or more 'name' keys in dimension.json \n{str(missing_name_df)}"
        )
    # dimension names
    dim_names = dimension_names or DIMENSION_NAMES
    names = set(dim_df["name"])
    invalid_names = names - dim_names
    if invalid_names:
        raise ValueError(
            f"Invalid names in dimension.json: {sorted(invalid_names)}. Valid names: {sorted(dim_names)}"
        )
    # validate that parents_values and equivalence are dict
    # Find rows where values are NOT dictionaries
    if "equivalence" in dim_df.columns:
        equivalence_not_dict = ~dim_df["equivalence"].dropna().apply(
            lambda x: isinstance(x, dict)
        )
        if equivalence_not_dict.any():
            raise TypeError(
                f"equivalence must be a dict in dimension.json. Problematic elements: \n{str(dim_df[equivalence_not_dict])}"
            )
    if "parents_values" in dim_df.columns:
        parents_values_not_dict = ~dim_df["parents_values"].dropna().apply(
            lambda x: isinstance(x, dict)
        )
        if parents_values_not_dict.any():
            raise TypeError(
                f"parents_values must be a dict in dimension.json. Problematic elements: \n{str(dim_df[parents_values_not_dict])}"
            )
    # parents in value
    if "parents_values" in actual_keys:
        ex_df = explode_dict_to_column(dim_df, "parents_values")
        parents_values = set(ex_df.values[ex_df.notna().values])
        values = set(dim_df["value"])
        invalid_parents_values = parents_values - values
        if invalid_parents_values:
            raise ValueError(
                f"Invalid parents_values in dimension.json: {sorted(invalid_parents_values)}."
                f"A valid parents_values must have its own value registered."
            )


def validate_variable_dimension_file(
    vardim_json: str | None = None,
    vardim_file_path: str | os.PathLike | None = None,
    dimension_names: set | None = None,
    property_values: set | None = None,
    required_keys: set | None = None,
):
    """Validate the structure and content of variable dimension file.

    Validates that the variable dimension file (JSON) contains the required keys,
    valid dimension names from ASPECT_COLUMNS, and valid property values.

    :param vardim_json: JSON string to validate (alternative to file path)
    :type vardim_json: str | None
    :param vardim_file_path: Path to variable dimension JSON file
    :type vardim_file_path: str | os.PathLike | None
    :param dimension_names: Valid dimension names (defaults to ASPECT_COLUMNS)
    :type dimension_names: set | None
    :param property_values: Valid property values (defaults to PROPERTY_VALUES)
    :type property_values: set | None
    :param required_keys: Required keys in the file (defaults to VARIABLE_DIMENSION_REQUIRED_KEYS)
    :type required_keys: set | None
    :raises TypeError: If parameters are not of correct type
    :raises KeyError: If required keys are missing or invalid keys are present
    :raises ValueError: If dimension names or property values are invalid

    Examples
    --------
    Complete example with file validation:

    **Required file structure for data/variable_dimension/variable_dimension.json:**

    .. code-block:: json

        [
            {
                "dimension": "location",
                "property": "mean",
                "variable": "lifetime_location_mean"
            },
            {
                "dimension": "location",
                "property": "max",
                "variable": "lifetime_location_max"
            },
            {
                "dimension": "object",
                "property": "mean",
                "variable": "lifetime_object_mean"
            },
            {
                "dimension": "object",
                "property": "max",
                "variable": "lifetime_object_max"
            },
            {
                "dimension": "process",
                "property": "sum",
                "variable": "efficiency_process_sum"
            }
        ]

    **Default validation sets:**

    .. code-block:: python

        VARIABLE_DIMENSION_REQUIRED_KEYS = {"dimension", "property", "variable"}

        ASPECT_COLUMNS = {
            "object", "object_composition", "object_downgrading", "object_Su",
            "object_efficiency", "location", "location_production", "process"
        }

        PROPERTY_VALUES = {"mean", "max", "min", "sum", "count"}

    **Usage:**

    .. code-block:: python

        >>> # Basic file validation
        >>> validate_variable_dimension_file("data/variable_dimension/variable_dimension.json")

        >>> # Validate JSON string directly
        >>> json_content = '''[
        ...     {
        ...         "dimension": "location",
        ...         "property": "mean",
        ...         "variable": "lifetime_location_mean"
        ...     },
        ...     {
        ...         "dimension": "object",
        ...         "property": "max",
        ...         "variable": "lifetime_object_max"
        ...     }
        ... ]'''
        >>> validate_variable_dimension_file(vardim_json=json_content)

        >>> # Validate with custom sets
        >>> custom_dimensions = {"location", "object"}
        >>> custom_properties = {"average", "maximum"}
        >>> custom_required = {"dimension", "property", "variable", "unit"}
        >>> validate_variable_dimension_file(
        ...     "custom_vardim.json",
        ...     dimension_names=custom_dimensions,
        ...     property_values=custom_properties,
        ...     required_keys=custom_required
        ... )
    """
    if not isinstance(required_keys, (set, type(None))):
        raise TypeError(
            f"required_keys must be a set or None to get the default set: {VARIABLE_DIMENSION_REQUIRED_KEYS}"
        )
    if not isinstance(dimension_names, (set, type(None))):
        raise TypeError(
            f"dimension_names must be a set or None to get the default set: {ASPECT_COLUMNS}"
        )
    if not isinstance(property_values, (set, type(None))):
        raise TypeError(
            f"property_values must be a set or None to get the default set: {PROPERTY_VALUES}"
        )
    # read dimension json
    if vardim_json:
        vardim = json.loads(vardim_json)
    else:
        dim_path = vardim_file_path or VARIABLE_DIMENSION_FILE_PATH
        vardim = pd.read_json(dim_path, orient="records")
    # structure validation
    vardim_df = pd.DataFrame(vardim)
    requ_keys = required_keys or VARIABLE_DIMENSION_REQUIRED_KEYS
    actual_keys = set(vardim_df.columns)
    # Check invalid column names
    invalid_keys = actual_keys - requ_keys
    if invalid_keys:
        raise KeyError(
            f"Invalid keys: {sorted(invalid_keys)}. Valid keys: {sorted(requ_keys)}"
        )
    # Check for missing required keys
    missing_required = requ_keys - actual_keys
    if missing_required:
        raise KeyError(
            f"Missing required keys for all elements: {sorted(missing_required)}"
        )
    # check for missing element
    for key in requ_keys:
        missing_value_df = vardim_df[vardim_df[key].isna()]
        if not missing_value_df.empty:
            raise KeyError(f"Missing one or more {key} keys \n{str(missing_value_df)}")
    # dimension names
    dim_names = dimension_names or ASPECT_COLUMNS
    names = set(vardim_df["dimension"])
    invalid_names = names - dim_names
    if invalid_names:
        raise ValueError(
            f"Invalid aspect names: {sorted(invalid_names)}. Valid aspect names: {sorted(dim_names)}"
        )
    # property values
    prop_values = property_values or PROPERTY_VALUES
    values = set(vardim_df["property"])
    invalid_values = values - prop_values
    if invalid_values:
        raise ValueError(
            f"Invalid properties: {sorted(invalid_values)}. Valid properties: {sorted(prop_values)}"
        )


def validate_variable_elements(
    df: pd.DataFrame, vardim_file_path: str | os.PathLike | None = None
):
    """Validate that DataFrame variables and dimensions match variable dimension requirements.

    Validates that all variables in the DataFrame exist in the variable dimension file
    and that each row has the correct dimension columns for its variable as specified
    in the variable dimension file.

    :param df: DataFrame to validate with required columns and variables
    :type df: pd.DataFrame
    :param vardim_file_path: Path to variable dimension JSON file
    :type vardim_file_path: str | os.PathLike | None
    :raises ValueError: If variables are invalid or dimension requirements not met

    Examples
    --------
    Complete example with DataFrame validation:

    **Input DataFrame structure:**

    .. code-block:: python

        >>> import pandas as pd
        >>> df = pd.DataFrame([
        ...     {
        ...         "location": "france",
        ...         "value": 15.2,
        ...         "unit": "year",
        ...         "time": 2020,
        ...         "scenario": "historical",
        ...         "variable": "lifetime_location_mean"
        ...     },
        ...     {
        ...         "object": "car",
        ...         "value": 18.5,
        ...         "unit": "year",
        ...         "time": 2021,
        ...         "scenario": "projection",
        ...         "variable": "lifetime_object_max"
        ...     }
        ... ])

    **Required data/variable_dimension/variable_dimension.json file structure:**

    .. code-block:: json

        [
            {
                "dimension": "location",
                "property": "mean",
                "variable": "lifetime_location_mean"
            },
            {
                "dimension": "location",
                "property": "max",
                "variable": "lifetime_location_max"
            },
            {
                "dimension": "object",
                "property": "mean",
                "variable": "lifetime_object_mean"
            },
            {
                "dimension": "object",
                "property": "max",
                "variable": "lifetime_object_max"
            },
            {
                "dimension": "process",
                "property": "sum",
                "variable": "efficiency_process_sum"
            }
        ]

    **Usage:**

    .. code-block:: python

        >>> # Basic validation with default path
        >>> validate_variable_elements(df)
        >>> # Validation with custom path
        >>> validate_variable_elements(
        ...     df,
        ...     vardim_file_path="data/variable_dimension/variable_dimension.json"
        ... )
    """
    validate_variable_dimension_file(vardim_file_path=vardim_file_path)
    validate_input_data_structure(df)
    # read variable_dimension json
    dim_path = vardim_file_path or VARIABLE_DIMENSION_FILE_PATH
    vardim = pd.read_json(dim_path, orient="records")
    # ckeck variable exists
    actual_variables = set(df["variable"])
    valid_variables = set(vardim["variable"])
    # check invalid variable
    invalid_variables = actual_variables - valid_variables
    if invalid_variables:
        raise ValueError(
            f"Invalid variables: {sorted(invalid_variables)}."
            f"Add to variable_dimension.json file or chose a valid variable in: {sorted(valid_variables)}"
        )
    # check invalid aspect
    requirements = vardim.pivot_table(
        index="variable", columns="dimension", aggfunc="size", fill_value=0
    ).astype(bool)
    # get dimension columns from df that match vardim dimensions
    dimension_cols = requirements.columns.intersection(df.columns).tolist()
    # merge df with requirements
    df_with_req = df.merge(
        requirements[dimension_cols],
        left_on="variable",
        right_index=True,
        how="left",
        suffixes=("", "_req"),
    )
    # actual_pattern
    actual_pattern = df_with_req[dimension_cols].notna()
    # required data pattern (rename _required columns to match)
    required_cols = [f"{col}_req" for col in dimension_cols]
    required_pattern = df_with_req[required_cols].copy()
    required_pattern.columns = dimension_cols
    comparison = actual_pattern == required_pattern
    # if any False in a row, that row violates requirements
    invalid_mask = ~comparison.all(axis=1)
    if invalid_mask.any():
        invalid_df = df[invalid_mask]
        failure_summary = invalid_df.groupby("variable").size().to_dict()
        raise ValueError(
            f"Validation failed for {invalid_mask.sum()} rows across variables: {failure_summary}\n"
            f"Problematic rows:\n{invalid_df.to_string()}\n"
            f"Check variable_dimension.json for requirements."
        )


def validate_input_data_full(
    df: pd.DataFrame,
    vardim_file_path: str | os.PathLike | None = None,
    dimension_file_path: str | os.PathLike | None = None,
):
    """Complete validation of input DataFrame against variable dimension and dimension files.

    Performs comprehensive validation by checking that:
    1. Variable names exist in variable dimension file (validate_variable_elements)
    2. Aspect elements exist in dimension file (validate_aspect_elements)

    :param df: DataFrame to validate with all required columns and aspect columns
    :type df: pd.DataFrame
    :param vardim_file_path: Path to variable dimension JSON file
    :type vardim_file_path: str | os.PathLike | None
    :param dimension_file_path: Path to dimension JSON file
    :type dimension_file_path: str | os.PathLike | None
    :raises ValueError: If variable names or aspect elements are not found in respective files
    :raises TypeError: If df is not a pandas DataFrame

    Examples
    --------
    Complete example with all files:

    **Input DataFrame structure:**

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
        ...         "variable": "lifetime_location_mean"
        ...     },
        ...     {
        ...         "location": "germany",
        ...         "object": "truck",
        ...         "value": 20,
        ...         "unit": "year",
        ...         "time": 2020,
        ...         "scenario": "projection",
        ...         "variable": "lifetime_object_max"
        ...     }
        ... ])

    **Required data/variable_dimension/variable_dimension.json structure:**

    .. code-block:: json

        [
            {
                "dimension": "location",
                "property": "mean",
                "variable": "lifetime_location_mean"
            },
            {
                "dimension": "object",
                "property": "max",
                "variable": "lifetime_object_max"
            },
            {
                "dimension": "process",
                "property": "sum",
                "variable": "efficiency_process_sum"
            }
        ]

    **Required data/dimension/dimension.json structure:**

    .. code-block:: json

        [
            {
                "name": "location",
                "value": "france",
                "equivalence": {"equ1": "FR", "equ2": "FRA"}
            },
            {
                "name": "location",
                "value": "germany",
                "equivalence": {"equ1": "GE", "equ2": "DEU"}
            },
            {
                "name": "object",
                "value": "car",
                "equivalence": {"equ1": "PLDV", "equ2": "auto"}
            },
            {
                "name": "object",
                "value": "truck",
                "equivalence": {"equ1": "HV", "equ2": "heavy_vehicle"}
            },
            {
                "name": "process",
                "value": "manufacturing",
                "equivalence": {"equ1": "manuf", "equ2": "production"}
            }
        ]

    **Usage:**

    .. code-block:: python

        >>> # Basic validation with default file paths
        >>> validate_input_data_full(df)
        >>> # Validation with custom file paths
        >>> validate_input_data_full(
        ...     df,
        ...     vardim_file_path="custom/path/variable_dimension.json",
        ...     dimension_file_path="custom/path/dimension.json"
        ... )
    """
    validate_variable_elements(df, vardim_file_path)
    validate_aspect_elements(df, dimension_file_path)


def validate_dumped_json(
    json_data: str,
    vardim_file_path: str | os.PathLike | None = None,
    dimension_file_path: str | os.PathLike | None = None,
):
    """Validate the three keys and structure of dumped JSON from dump_json.

    This function validates that JSON has the correct structure with input_data,
    provider, and metadata keys, and that all data conforms to MATER standards.
    It also validates that aspect elements exist in dimension files.

    :param json_data: JSON string from dump_json
    :type json_data: str
    :param vardim_file_path: Path to variable_dimension.json file for variable-dimension validation
    :type vardim_file_path: str | os.PathLike | None
    :param dimension_file_path: Path to dimension.json file for aspect element validation
    :type dimension_file_path: str | os.PathLike | None
    :raises ValueError: If JSON structure is invalid
    :raises FileNotFoundError: If dimension files are not found

    Examples
    --------
    Complete example with all files:

    **Directory structure:**

    .. code-block:: text

        data/
        ├── dimension/
        │   ├── dimension.json
        │   └── variable_dimension.json

    **Content of data/dimension/dimension.json:**

    .. code-block:: json

        [
            {
                "name": "location",
                "value": "france",
                "equivalence": {"equ1": "FR", "equ2": "FRA"}
            },
            {
                "name": "location",
                "value": "germany",
                "equivalence": {"equ1": "GE"}
            },
            {
                "name": "object",
                "value": "car",
                "equivalence": {"equ1": "PLDV", "equ2": "auto"}
            },
            {
                "name": "object",
                "value": "truck",
                "equivalence": {"equ1": "HV"}
            },
            {
                "name": "process",
                "value": "manufacturing",
                "equivalence": {"equ": "manuf"}
            }
        ]

    **Content of data/dimension/variable_dimension.json:**

    .. code-block:: json

        [
            {
                "variable": "lifetime_mean_value",
                "dimension": ["location", "object"],
                "unit": "year"
            },
            {
                "variable": "production_rate",
                "dimension": ["process"],
                "unit": "pieces"
            },
            {
                "variable": "weight",
                "dimension": ["process"],
                "unit": "kg"
            }
        ]

    **JSON data to validate:**

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
                },
                {
                    "process": "manufacturing",
                    "value": 100,
                    "unit": "pieces",
                    "time": 2024,
                    "scenario": "current",
                    "variable": "production_rate"
                }
            ],
            "provider": {
                "first_name": "John",
                "last_name": "Doe",
                "email_address": "john.doe@example.com"
            },
            "metadata": {
                "link": "https://data.example.com/dataset.csv",
                "source": "European Environment Agency",
                "project": "Carbon Footprint Analysis 2024"
            }
        }

    **Usage:**

    .. code-block:: python

        >>> import json
        >>> # Assuming json_data is a JSON string
        >>> validate_dumped_json(json_data)
        >>> # Validation with dimension files
        >>> validate_dumped_json(
        ...     json_data,
        ...     vardim_file_path="data/dimension/variable_dimension.json",
        ...     dimension_file_path="data/dimension/dimension.json"
        ... )
    """
    # Parse JSON string
    data = json.loads(json_data)

    # Check top-level structure
    required_keys = {"input_data", "provider", "metadata"}
    actual_keys = set(data.keys())

    missing_keys = required_keys - actual_keys
    if missing_keys:
        raise ValueError(f"Missing required keys in JSON: {sorted(missing_keys)}")

    extra_keys = actual_keys - required_keys
    if extra_keys:
        raise ValueError(f"Unexpected keys in JSON: {sorted(extra_keys)}")

    # Validate input_data is a list
    if not isinstance(data["input_data"], list):
        raise ValueError("input_data must be a list of records")

    if len(data["input_data"]) == 0:
        raise ValueError("input_data cannot be empty")

    # Validate provider structure
    validate_provider(data["provider"])

    # Validate metadata structure
    validate_metadata(data["metadata"])

    # Validate DataFrame structure
    df = pd.DataFrame(data["input_data"])
    validate_input_data_full(
        df, vardim_file_path=vardim_file_path, dimension_file_path=dimension_file_path
    )


# internal functions


def _validate_string(value: str):
    """Validate that a value is a non-empty string.

    :param value: Value to validate
    :type value: Any
    :return: Stripped string value
    :rtype: str
    :raises TypeError: If value is not a string
    :raises ValueError: If value is unstripped, empty or only whitespace

    Examples
    --------
    Complete example with string validation:

    **Valid string examples:**

    .. code-block:: python

        >>> # Valid non-empty string
        >>> result = _validate_string("hello")
        >>> print(result)
        'hello'

        >>> # String with whitespace gets stripped
        >>> result = _validate_string("  hello world  ")
        >>> print(result)
        'hello world'

        >>> # Single character
        >>> result = _validate_string("x")
        >>> print(result)
        'x'

    **Examples that would fail validation:**

    .. code-block:: python

        >>> # Empty string
        >>> _validate_string("")
        ValueError: Value cannot be empty or only whitespace

        >>> # Only whitespace
        >>> _validate_string("   ")
        ValueError: Value cannot be empty or only whitespace

        >>> # Non-string types
        >>> _validate_string(123)
        TypeError: Value must be a string, got <class 'int'>

        >>> _validate_string(None)
        TypeError: Value must be a string, got <class 'NoneType'>

        >>> _validate_string(["hello"])
        TypeError: Value must be a string, got <class 'list'>

    **Usage:**

    .. code-block:: python

        >>> # Basic validation
        >>> clean_value = _validate_string(user_input)

        >>> # In a validation loop
        >>> values = ["hello", "  world  ", "", "test"]
        >>> validated_values = []
        >>> for value in values:
        ...     try:
        ...         validated_values.append(_validate_string(value))
        ...     except (TypeError, ValueError) as e:
        ...         print(f"Invalid value '{value}': {e}")

        >>> # Use in form validation
        >>> def validate_form_field(field_value, field_name):
        ...     try:
        ...         return _validate_string(field_value)
        ...     except (TypeError, ValueError):
        ...         raise ValueError(f"Invalid {field_name}: must be non-empty string")
    """
    # check type
    if not isinstance(value, str):
        raise TypeError(f"must be a string, got {type(value).__name__}")

    # strip the string
    stripped_value = value.strip()
    if not stripped_value:
        raise ValueError("cannot be empty or only whitespace")

    if stripped_value != value:
        raise ValueError("string not stripped of blanks. Use the .strip() method")
