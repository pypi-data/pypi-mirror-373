"""
This module tests the transformation functions.

Copyright (C) 2025 @verzierf <francois.verzier@univ-grenoble-alpes.fr>

SPDX-License-Identifier: LGPL-3.0-or-later
"""

import numpy as np
import pandas as pd
import pytest

from src.mater_data_providing.transformations import (
    dimension_as_dict,
    replace_equivalence,
)


class TestReplaceEquivalence:
    """Simple test suite for replace_equivalence function."""

    def test_replace_equivalence_basic(self, sample_dimension_file, valid_dataframe):
        """Test basic equivalence replacement."""
        # DataFrame with equivalence values that should be replaced
        df_with_equivalences = pd.DataFrame(
            [
                {
                    "location": "FR",  # Should be replaced with "france"
                    "object": "PLDV",  # Should be replaced with "car"
                    "value": 15,
                    "unit": "year",
                    "time": 2015,
                    "scenario": "historical",
                    "variable": "lifetime_mean_value",
                }
            ]
        )

        result = replace_equivalence(df_with_equivalences, sample_dimension_file)

        # Check that equivalences were replaced
        pd.testing.assert_frame_equal(result, valid_dataframe)

    def test_replace_equivalence_no_changes_needed(
        self, valid_dataframe, sample_dimension_file
    ):
        """Test that DataFrame with standard values remains unchanged."""
        original_values = valid_dataframe.copy()

        result = replace_equivalence(valid_dataframe, sample_dimension_file)

        # Should remain the same since "france" and "car" are standard values
        pd.testing.assert_frame_equal(result, original_values)

    def test_replace_equivalence_mixed_values(self, sample_dimension_file):
        """Test replacement with mix of standard and equivalence values."""
        df_mixed = pd.DataFrame(
            [
                {
                    "location": "france",  # Standard value - no change
                    "object": "PLDV",  # Equivalence - should become "car"
                    "value": 20,
                    "unit": "year",
                    "time": 2020,
                    "scenario": "projection",
                    "variable": "lifetime_max_value",
                },
                {
                    "location": "GE",  # Equivalence - should become "germany"
                    "object": "car",  # Standard value - no change
                    "value": 25,
                    "unit": "year",
                    "time": 2025,
                    "scenario": "optimistic",
                    "variable": "lifetime_estimate",
                },
            ]
        )

        df_good = pd.DataFrame(
            [
                {
                    "location": "france",
                    "object": "car",
                    "value": 20,
                    "unit": "year",
                    "time": 2020,
                    "scenario": "projection",
                    "variable": "lifetime_max_value",
                },
                {
                    "location": "germany",
                    "object": "car",
                    "value": 25,
                    "unit": "year",
                    "time": 2025,
                    "scenario": "optimistic",
                    "variable": "lifetime_estimate",
                },
            ]
        )

        result = replace_equivalence(df_mixed, sample_dimension_file)

        pd.testing.assert_frame_equal(result, df_good)

    def test_replace_equivalence_with_process_column(self, sample_dimension_file):
        """Test replacement with process column."""
        df_with_process = pd.DataFrame(
            [
                {
                    "process": "manuf",  # Should be replaced with "manufacturing"
                    "value": 100,
                    "unit": "pieces",
                    "time": 2024,
                    "scenario": "current",
                    "variable": "production_rate",
                }
            ]
        )

        df_good = pd.DataFrame(
            [
                {
                    "process": "manufacturing",
                    "value": 100,
                    "unit": "pieces",
                    "time": 2024,
                    "scenario": "current",
                    "variable": "production_rate",
                }
            ]
        )

        result = replace_equivalence(df_with_process, sample_dimension_file)

        pd.testing.assert_frame_equal(result, df_good)

    def test_validate_dataframe_elements(self, valid_dataframe, sample_dimension_file):
        """Test that function first validates the DataFrame elements."""
        invalid_element_df = pd.DataFrame(
            [
                {
                    "location": "unknown_location",  # Not in dimension file
                    "object": "car",
                    "value": 15,
                    "unit": "year",
                    "time": 2015,
                    "scenario": "historical",
                    "variable": "lifetime_mean_value",
                }
            ]
        )

        with pytest.raises(ValueError):
            replace_equivalence(invalid_element_df, sample_dimension_file)


class TestDimensionAsDict:
    """Simple test suite for dimension_as_dict function."""

    def test_dimension_as_dict_basic_functionality(self, valid_dataframe):
        """Test basic transformation of aspect columns to dictionary."""
        result = dimension_as_dict(valid_dataframe)

        # Should have dimensions_values column
        assert "dimensions_values" in result.columns

        # Original aspect columns should be removed
        assert "location" not in result.columns
        assert "object" not in result.columns

        # Required columns should remain
        assert "value" in result.columns
        assert "unit" in result.columns
        assert "time" in result.columns
        assert "scenario" in result.columns
        assert "variable" in result.columns

        # Check dimensions_values content
        dimensions = result.loc[0, "dimensions_values"]
        assert isinstance(dimensions, dict)
        assert dimensions["location"] == "france"
        assert dimensions["object"] == "car"

    def test_dimension_as_dict_with_custom_aspect_columns(self, valid_dataframe):
        """Test transformation with custom aspect columns."""
        # Only transform location, not object
        custom_aspects = {"location"}

        result = dimension_as_dict(valid_dataframe, custom_aspects)

        # location should be in dimensions_values, object should remain as column
        assert "location" not in result.columns
        assert "object" in result.columns  # Should remain

        dimensions = result.loc[0, "dimensions_values"]
        assert "location" in dimensions
        assert "object" not in dimensions
        assert dimensions["location"] == "france"

    def test_dimension_as_dict_preserves_non_aspect_columns(self, valid_dataframe):
        """Test that non-aspect columns are preserved unchanged."""
        original_value = valid_dataframe.loc[0, "value"]
        original_unit = valid_dataframe.loc[0, "unit"]

        result = dimension_as_dict(valid_dataframe)

        # Values should be preserved
        assert result.loc[0, "value"] == original_value
        assert result.loc[0, "unit"] == original_unit
        assert result.loc[0, "time"] == 2015
        assert result.loc[0, "scenario"] == "historical"
        assert result.loc[0, "variable"] == "lifetime_mean_value"

    def test_dimension_as_dict_multiple_rows(self):
        """Test transformation with multiple rows."""
        multi_row_df = pd.DataFrame(
            [
                {
                    "location": "france",
                    "object": "car",
                    "value": 15,
                    "unit": "year",
                    "time": 2015,
                    "scenario": "historical",
                    "variable": "lifetime",
                },
                {
                    "location": "germany",
                    "object": "truck",
                    "value": 20,
                    "unit": "year",
                    "time": 2020,
                    "scenario": "projection",
                    "variable": "lifetime",
                },
            ]
        )

        result = dimension_as_dict(multi_row_df)

        # Check both rows have dimensions_values
        assert len(result) == 2

        # First row
        dims1 = result.loc[0, "dimensions_values"]
        assert dims1["location"] == "france"
        assert dims1["object"] == "car"

        # Second row
        dims2 = result.loc[1, "dimensions_values"]
        assert dims2["location"] == "germany"
        assert dims2["object"] == "truck"

    def test_dimension_as_dict_returns_dataframe(self, valid_dataframe):
        """Test that function returns a DataFrame."""
        result = dimension_as_dict(valid_dataframe)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(valid_dataframe)

    def test_dimension_as_dict_no_aspect_columns(self):
        """Test with DataFrame that has no aspect columns."""
        df_no_aspects = pd.DataFrame(
            [
                {
                    "value": 10,
                    "unit": "kg",
                    "time": 2020,
                    "scenario": "baseline",
                    "variable": "weight",
                }
            ]
        )

        result = dimension_as_dict(df_no_aspects)

        # Should have empty dimensions_values
        assert "dimensions_values" in result.columns
        dimensions = result.loc[0, "dimensions_values"]
        assert isinstance(dimensions, dict)
        assert len(dimensions) == 0  # Empty dict

    def test_dimension_as_dict_nan_column(self):
        """Test transformation with multiple rows."""
        multi_row_df = pd.DataFrame(
            [
                {
                    "location": "france",
                    "object": "car",
                    "process": np.nan,
                    "value": 15,
                    "unit": "year",
                    "time": 2015,
                    "scenario": "historical",
                    "variable": "lifetime",
                },
            ]
        )

        result = dimension_as_dict(multi_row_df)
        # First row
        dims = result.loc[0, "dimensions_values"]
        assert len(dims) == 2
        assert dims["location"] == "france"
        assert dims["object"] == "car"
