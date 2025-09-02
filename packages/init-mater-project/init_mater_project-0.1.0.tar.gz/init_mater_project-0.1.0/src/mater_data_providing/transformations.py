"""
This module defines the transformation functions.

SPDX-License-Identifier: LGPL-3.0-or-later
"""

import os

import pandas as pd

from .constants import ASPECT_COLUMNS, DIMENSION_FILE_PATH
from .helpers import _process_dimension_equivalence
from .validations import validate_aspect_elements


def dimension_as_dict(
    df: pd.DataFrame, aspect_columns: set | None = None
) -> pd.DataFrame:
    r"""Transform aspect columns into a single dictionary column for MATER format.

    Groups all aspect columns (location, object, process, etc.) into a single
    'dimensions_values' column containing a dictionary as long as the aspect value is not nan,
    then removes the original aspect columns.
    This prepares the DataFrame for the final MATER JSON format.

    :param df: Input DataFrame with aspect columns to transform
    :type df: pd.DataFrame
    :param aspect_columns: Set of aspect column names to group (uses ASPECT_COLUMNS if None)
    :type aspect_columns: set | None
    :return: DataFrame with aspect columns grouped into dimensions_values dict column
    :rtype: pd.DataFrame

    Examples
    --------
    Complete example with dimension transformation:

    **Input DataFrame with aspect columns:**

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
        ...         "variable": "lifetime"
        ...     }
        ... ])

    **Expected output with grouped dimensions:**

    .. code-block:: python

        >>> result = dimension_as_dict(df)
        >>> print(result.columns.tolist())
        ['value', 'unit', 'time', 'scenario', 'variable', 'dimensions_values']
        >>>
        >>> print(result.loc[0, 'dimensions_values'])
        {'location': 'france', 'object': 'car'}
        >>>
        >>> print(result)
           value unit  time     scenario variable                    dimensions_values
        0     15 year  2015   historical lifetime  {'location': 'france', 'object': 'car'}
    """
    df2 = df.copy()
    # list of aspects
    asp_cols = aspect_columns or ASPECT_COLUMNS
    # Get actual columns from DataFrame
    actual_columns = set(df.columns)
    # Get present aspect columns
    present_aspect = asp_cols & actual_columns
    # Add dimensions_values column with the dict inside
    ## but don't add an entry for nan aspect elements
    df2["dimensions_values"] = df.apply(
        lambda row: {asp: row[asp] for asp in present_aspect if not pd.isna(row[asp])},
        axis=1,
    )
    return df2.drop(present_aspect, axis=1)


def replace_equivalence(
    df: pd.DataFrame, dimension_file_path: str | os.PathLike | None = None
) -> pd.DataFrame:
    """Replaces the dimension elements of a dataframe according to the dimension.json file.

    This function validates that all aspect elements in the DataFrame exist in the
    dimension.json file, then replaces equivalence keys with their corresponding
    standard values to ensure data uniformity.

    :param df: Initial dataframe with aspect columns to be standardized
    :type df: pd.DataFrame
    :param dimension_file_path: Path to dimension.json file (uses default if None)
    :type dimension_file_path: str | os.PathLike | None
    :return: DataFrame with equivalence values replaced by standard values
    :rtype: pd.DataFrame
    :raises ValueError: If aspect elements are not found in dimension.json
    :raises FileNotFoundError: If dimension.json file is not found

    Examples
    --------
    Complete example with equivalence replacement:

    **Input DataFrame with equivalence values:**

    .. code-block:: python

        >>> import pandas as pd
        >>> df = pd.DataFrame([
        ...     {
        ...         "location": "FR",
        ...         "object": "PLDV",
        ...         "value": 15,
        ...         "unit": "year",
        ...         "time": 2015,
        ...         "scenario": "historical",
        ...         "variable": "lifetime_mean"
        ...     },
        ...     {
        ...         "location": "GE",
        ...         "object": "HV",
        ...         "value": 20,
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
                "equivalence": {"equ1": "GE", "equ2": "DE"}
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

    **Expected output with standardized values:**

    .. code-block:: python

        >>> result = replace_equivalence(df, "dimension.json")
        >>> print(result)
           location object  value unit  time     scenario      variable
        0    france    car     15 year  2015   historical  lifetime_mean
        1   germany  truck     20 year  2020   projection   lifetime_max

    **Transformation details:**

    In this example, the following replacements occur:

    - "FR" → "france" (standard value for location)
    - "GE" → "germany" (standard value for location)
    - "PLDV" → "car" (standard value for object)
    - "HV" → "truck" (standard value for object)

    **Usage:**

    .. code-block:: python

        >>> # Basic replacement with default dimension file
        >>> standardized_df = replace_equivalence(df)
    """
    validate_aspect_elements(df, dimension_file_path)
    dim_path = dimension_file_path or DIMENSION_FILE_PATH
    dimension = pd.read_json(dim_path, orient="records")

    if "equivalence" in dimension.columns:
        # Ensure multiple keys in 'equivalence' dictionaries are handled correctly
        df_filtered, series_exploded = _process_dimension_equivalence(dimension)
        # Map each source equivalence key to its corresponding value name
        equivalence_dict = (
            series_exploded.to_frame()
            .join(df_filtered["value"])
            .set_index(0)["value"]
            .to_dict()
        )
        df.replace(equivalence_dict, inplace=True)
    return df
