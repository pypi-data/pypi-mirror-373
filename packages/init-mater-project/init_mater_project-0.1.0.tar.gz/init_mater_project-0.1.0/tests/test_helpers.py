"""
This module tests the helper functions.

Copyright (C) 2025 @verzierf <francois.verzier@univ-grenoble-alpes.fr>

SPDX-License-Identifier: LGPL-3.0-or-later
"""

import pandas as pd

from src.mater_data_providing.helpers import (
    _process_dimension_equivalence,
    explode_dict_to_column,
)


class TestExplodeDictToColumn:
    """Simple test suite for explode_dict_to_column function."""

    def test_explode_basic_functionality(self):
        """Test that the function works with your equivalence use case."""
        df = pd.DataFrame(
            [
                {"value": "car", "equivalence": {"eq1": "PLDV", "eq2": "auto"}},
                {"value": "truck", "equivalence": {"eq1": "HV"}},
            ]
        )

        result = explode_dict_to_column(df, "equivalence")

        # Should create columns for dictionary keys
        assert "eq1" in result.columns
        assert "eq2" in result.columns

        # Should preserve values
        assert result.loc[0, "eq1"] == "PLDV"
        assert result.loc[0, "eq2"] == "auto"
        assert result.loc[1, "eq1"] == "HV"

    def test_explode_handles_none_values(self):
        """Test that None values don't break the function."""
        df = pd.DataFrame(
            [
                {"value": "car", "equivalence": {"eq1": "PLDV"}},
                {"value": "bike", "equivalence": None},
            ]
        )

        result = explode_dict_to_column(df, "equivalence")

        # Should still work and create the column
        assert "eq1" in result.columns
        assert result.loc[0, "eq1"] == "PLDV"


class TestProcessDimensionEquivalence:
    """Test the private helper function directly."""

    def test_process_dimension_equivalence_basic(self):
        """Test basic processing of dimension data."""
        dimension = pd.DataFrame(
            [
                {"value": "car", "equivalence": {"eq1": "PLDV", "eq2": "auto"}},
                {"value": "truck", "equivalence": {"eq1": "HV"}},
                {"value": "bike", "equivalence": None},  # This should be filtered out
            ]
        )

        df_filtered, df_exploded = _process_dimension_equivalence(dimension)

        # Test df_filtered
        assert len(df_filtered) == 2  # bike row filtered out
        assert "car" in df_filtered["value"].values
        assert "truck" in df_filtered["value"].values

        # Test df_exploded
        assert len(df_exploded) == 3  # vehicle, auto, vehicle

    def test_process_dimension_equivalence_empty(self):
        """Test with empty equivalence data."""
        dimension = pd.DataFrame(
            [
                {"value": "car", "equivalence": None},
                {"value": "truck", "equivalence": None},
            ]
        )

        df_filtered, df_exploded = _process_dimension_equivalence(dimension)

        assert len(df_filtered) == 0
        assert len(df_exploded) == 0
