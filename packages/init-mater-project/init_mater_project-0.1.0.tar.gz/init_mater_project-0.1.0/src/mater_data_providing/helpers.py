"""
This module defines helper functions.

SPDX-License-Identifier: LGPL-3.0-or-later
"""

from typing import Tuple

import pandas as pd


def explode_dict_to_column(df: pd.DataFrame, column: str | int | float) -> pd.DataFrame:
    """explode a column containing dictionaries into multiple column for each dict keys

    :param df: The dataframe to explode
    :type df: pd.DataFrame
    :param column: The column containing the dictionaries
    :type column: str | int | float
    :return: A DataFrale containing only the columns corresponding to the dict keys
    :rtype: pd.DataFrame

    Examples
    --------

    .. code-block:: python

        >>> df = pd.DataFrame(
                [
                    {"value": "car", "equivalence": {"eq1": "PLDV", "eq2": "auto"}},
                    {"value": "truck", "equivalence": {"eq1": "HV"}},
                ]
            )
        >>> explode_dict_to_column(df, "equivalence")
            eq1   eq2
        0  PLDV  auto
        1    HV   NaN
    """
    # Expand 'equivalence' dictionary into separate columns
    df_exploded = df[column].apply(pd.Series)
    return df_exploded


# Internal functions


def _process_dimension_equivalence(
    dimension: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.Series]:
    """Process dimension DataFrame to extract equivalence mappings.

    Private helper function for internal use in equivalence processing.

    :param dimension: Dimension DataFrame with equivalence column
    :type dimension: pd.DataFrame
    :return: Tuple of (filtered_df, exploded_df)
    :rtype: Tuple[pd.DataFrame, pd.Series]

    Examples
    --------
    Complete example with equivalence processing:

    **Input dimension DataFrame:**

    .. code-block:: python

        >>> import pandas as pd
        >>> dimension = pd.DataFrame([
        ...     {
        ...         "name": "location",
        ...         "value": "france",
        ...         "equivalence": {"equ1": "FR", "equ2": "FRA"}
        ...     },
        ...     {
        ...         "name": "location",
        ...         "value": "germany",
        ...         "equivalence": {"equ1": "GE", "equ2": "DEU"}
        ...     },
        ...     {
        ...         "name": "object",
        ...         "value": "car",
        ...         "equivalence": None  # Will be filtered out
        ...     }
        ... ])

    **Processing results:**

    .. code-block:: python

        >>> filtered_df, exploded_series = _process_dimension_equivalence(dimension)
        >>>
        >>> # Filtered DataFrame (rows with non-null equivalence)
        >>> print(filtered_df)
           name     value                    equivalence
        0  location  france  {'equ1': 'FR', 'equ2': 'FRA'}
        1  location  germany {'equ1': 'GE', 'equ2': 'DEU'}
        >>>
        >>> # Exploded Series (equivalence values mapped to standard values)
        >>> print(exploded_series)
        0    FR
        0   FRA
        1    GE
        1   DEU
        Name: equivalence, dtype: object

    **Empty equivalence handling:**

    .. code-block:: python

        >>> # DataFrame with no valid equivalences
        >>> dimension_empty = pd.DataFrame([
        ...     {"name": "location", "value": "france", "equivalence": None},
        ...     {"name": "object", "value": "car", "equivalence": None}
        ... ])
        >>>
        >>> filtered_df, exploded_series = _process_dimension_equivalence(dimension_empty)
        >>> print(filtered_df.empty)
        True
        >>> print(exploded_series.empty)
        True

    **Usage:**

    .. code-block:: python

        >>> # Internal processing in equivalence replacement
        >>> filtered_df, exploded_series = _process_dimension_equivalence(dimension_df)
        >>>
        >>> # Use results for mapping creation
        >>> if not exploded_series.empty:
        ...     equivalence_mapping = create_mapping_from_series(exploded_series)
        ... else:
        ...     equivalence_mapping = {}
    """
    df_filtered = dimension.dropna(subset=["equivalence"])
    df_exploded = explode_dict_to_column(df_filtered, "equivalence")
    # check if df_exploded is empty before stack
    if not df_exploded.empty:
        df_exploded = df_exploded.stack().reset_index(level=1, drop=True)

    return df_filtered, df_exploded
