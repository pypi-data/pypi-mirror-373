"""
This module tests the validation functions.

Copyright (C) 2025 @verzierf <francois.verzier@univ-grenoble-alpes.fr>

SPDX-License-Identifier: LGPL-3.0-or-later
"""

import json

import numpy as np
import pandas as pd
import pytest

from src.mater_data_providing.validations import (
    _validate_string,
    validate_aspect_elements,
    validate_dimension_file,
    validate_dumped_json,
    validate_input_data_full,
    validate_input_data_structure,
    validate_metadata,
    validate_provider,
    validate_variable_dimension_file,
    validate_variable_elements,
)


class TestValidateString:
    """Test suite for _validate_string function."""

    def test_valid_string(self):
        """Test with valid string."""
        result = _validate_string("hello")
        assert result is None

    def test_unstripped_string_fails(self):
        """test fails with unstripped string"""
        with pytest.raises(ValueError, match="[Ss]trip"):
            _validate_string("   hello   ")

    def test_empty_string_fails(self):
        """Test fails with empty string."""
        with pytest.raises(ValueError):
            _validate_string("")

    def test_wrong_type_fails(self):
        """Test fails with non-string input."""
        with pytest.raises(TypeError):
            _validate_string(123)


class TestValidateProvider:
    """Test suite for validate_provider function."""

    def test_validate_provider_with_valid_data(self, sample_provider_inputs):
        """Test that valid provider data passes validation."""

        result = validate_provider(sample_provider_inputs)

        # Test the interface/contract, not internal implementation
        assert result is None

    def test_validate_provider_wrong_type(self):
        """Test that not dict raises en error."""
        wrong_type_provider = "not-a-dict"
        with pytest.raises(TypeError, match="dict"):
            validate_provider(wrong_type_provider)

    def test_validate_provider_missing_fields(self):
        """Test that missing fields are caught."""
        incomplete_provider = {
            "first_name": "John"
            # Missing last_name and email_address
        }

        with pytest.raises(ValueError, match="[Mm]issing"):
            validate_provider(incomplete_provider)

    def test_validate_provider_extra_fields(self):
        """Test that extra fields are rejected."""
        provider_with_extra = {
            "first_name": "John",
            "last_name": "Doe",
            "email_address": "john@example.com",
            "extra_field": "should_not_be_here",
        }

        with pytest.raises(ValueError, match="[Uu]nexpected"):
            validate_provider(provider_with_extra)


class TestValidateMetadata:
    """Test suite for validate_metadata function."""

    def test_validate_provider_with_valid_data(self, sample_metadata_inputs):
        """Test that valid provider data passes validation."""

        result = validate_metadata(sample_metadata_inputs)

        # Test the interface/contract, not internal implementation
        assert result is None

    def test_validate_metadata_wrong_type(self):
        """Test that not dict raises en error."""
        wrong_type_metadata = "not-a-dict"
        with pytest.raises(TypeError, match="dict"):
            validate_metadata(wrong_type_metadata)

    def test_validate_metadata_missing_fields(self):
        """Test that missing fields are caught."""
        incomplete_metadata = {"link": "https://data.example.com/dataset.csv"}

        with pytest.raises(ValueError, match="[Mm]issing"):
            validate_metadata(incomplete_metadata)

    def test_validate_metadata_extra_fields(self):
        """Test that extra fields are rejected."""
        metadata_with_extra = {
            "link": "https://data.example.com/dataset.csv",
            "source": "European Environment Agency",
            "project": "Carbon Footprint Analysis 2024",
            "extra_field": "should_not_be_here",
        }

        with pytest.raises(ValueError, match="[Uu]nexpected"):
            validate_metadata(metadata_with_extra)


class TestValidateInputData:
    """Test suite for validate_input_data_structure function."""

    def test_valid_dataframe(self, valid_dataframe):
        """Test with valid DataFrame structure."""
        # Should not raise
        result = validate_input_data_structure(valid_dataframe)
        assert result == {"location", "object"}

    def test_validate_input_data_structure_empty_dataframe(self):
        """Test validation fails with empty DataFrame."""
        empty_df = pd.DataFrame()

        with pytest.raises(ValueError, match="[Ee]mpty"):
            validate_input_data_structure(empty_df)

    def test_missing_required_columns(self, invalid_dataframe_missing_required):
        """Test fails when required columns missing."""
        with pytest.raises(ValueError, match="[Mm]issing"):
            validate_input_data_structure(invalid_dataframe_missing_required)

    def test_missing_aspect_columns(self, invalid_dataframe_missing_aspect):
        """Test fails when no aspect columns present."""
        with pytest.raises(ValueError, match="[Cc]olumn.*[Rr]equired"):
            validate_input_data_structure(invalid_dataframe_missing_aspect)

    def test_invalid_columns(self, valid_dataframe):
        """Test fails with invalid column names."""
        # Add invalid column to valid dataframe
        valid_dataframe["bad_column"] = "invalid"

        with pytest.raises(ValueError, match="[Ii]nvalid.*[Cc]olumn"):
            validate_input_data_structure(valid_dataframe)

    def test_wrong_input_data_type(self):
        """Test fails with non-DataFrame input."""
        with pytest.raises(TypeError, match="[Pp]andas.*DataFrame"):
            validate_input_data_structure("not a dataframe")

    def test_wrong_aspect_type(self, valid_dataframe):
        """Test fails with non-set aspect."""
        with pytest.raises(TypeError, match="set.*[Nn]one"):
            validate_input_data_structure(valid_dataframe, aspect_columns="not a set")

    def test_wrong_required_type(self, valid_dataframe):
        """Test fails with non-set aspect."""
        with pytest.raises(TypeError, match="set.*[Nn]one"):
            validate_input_data_structure(valid_dataframe, required_columns="not a set")

    def test_custom_index_fails(self, valid_dataframe):
        """Test fails with custom index."""
        valid_dataframe.index = ["custom"]

        with pytest.raises(ValueError, match="[Dd]efault.*RangeIndex"):
            validate_input_data_structure(valid_dataframe)


class TestValidateAspectElements:
    """Test suite for validate_aspect_elements function."""

    def test_valid_elements_pass_validation(
        self, valid_dataframe, sample_dimension_file
    ):
        """Test that valid elements pass validation."""
        # Should not raise any exception
        result = validate_aspect_elements(valid_dataframe, sample_dimension_file)
        assert result is None

    def test_invalid_elements_raise_error(self, sample_dimension_file):
        """Test that invalid elements raise ValueError."""
        # DataFrame with elements not in dimension file
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

        with pytest.raises(ValueError, match="[Ii]nvalid.*element"):
            validate_aspect_elements(invalid_element_df, sample_dimension_file)

    def test_elements_in_equivalence_pass_validation(self, sample_dimension_file):
        """Test that elements found in equivalence mappings."""
        # DataFrame with elements that exist in equivalence mappings
        df_with_equivalence = pd.DataFrame(
            [
                {
                    "location": "FR",  # Should be in equivalence for "france"
                    "object": "PLDV",  # Should be in equivalence for "car"
                    "value": 20,
                    "unit": "year",
                    "time": 2020,
                    "scenario": "projection",
                    "variable": "lifetime_max_value",
                }
            ]
        )

        # Should not raise exception if "FR" is equivalent to "france" and "PLDV" to "car"
        result = validate_aspect_elements(df_with_equivalence, sample_dimension_file)
        assert result is None

    def test_composed_aspect_name_pass_validation(self, sample_dimension_file):
        """Test that the composed aspect name has been split."""
        # DataFrame with elements that exist in equivalence mappings
        df_with_composed_aspect_name = pd.DataFrame(
            [
                {
                    "location": "france",
                    "object_composition": "car",  # object_composition becomes the object
                    "value": 20,
                    "unit": "year",
                    "time": 2020,
                    "scenario": "projection",
                    "variable": "lifetime_max_value",
                }
            ]
        )

        result = validate_aspect_elements(
            df_with_composed_aspect_name, sample_dimension_file
        )
        assert result is None

    def test_nan_in_aspect_pass_validation(self, sample_dimension_file):
        """Test that nan elements pass validation."""
        # DataFrame with nan is ok
        df_with_nan = pd.DataFrame(
            [
                {
                    "location": "france",
                    "object": np.nan,  # Should be ignored
                    "value": 20,
                    "unit": "year",
                    "time": 2020,
                    "scenario": "projection",
                    "variable": "lifetime_max_value",
                }
            ]
        )

        # Should not raise exception if "FR" is equivalent to "france" and "PLDV" to "car"
        result = validate_aspect_elements(df_with_nan, sample_dimension_file)
        assert result is None

    def test_validate_input_data_structure_is_called(self, sample_dimension_file):
        """Test dataframe structure validation."""
        invalid_df = pd.DataFrame(
            [
                {
                    "loc": "FR",  # Should be "location" not "loc"
                    "object": "PLDV",
                    "value": 20,
                    "unit": "year",
                    "time": 2020,
                    "scenario": "projection",
                    "variable": "lifetime_max_value",
                }
            ]
        )
        # Should raise ValueError
        with pytest.raises(ValueError):
            validate_aspect_elements(invalid_df, sample_dimension_file)

    def test_missing_name_in_dimension_fails(self, valid_dataframe, tmp_path):
        """Test that missing 'name' entries raise KeyError."""
        invalid_data = [
            {
                "name": None,  # Missing name
                "value": "france",
                "equivalence": {},
                "parents_values": {},
            }
        ]

        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, "w") as f:
            json.dump(invalid_data, f)

        with pytest.raises(KeyError, match="[Mm]issing.*name"):
            validate_aspect_elements(
                valid_dataframe, dimension_file_path=str(invalid_file)
            )


class TestValidateDumpedJson:
    """Test suite for validate_dumped_json function."""

    def test_valid_json_structure_succeeds(
        self,
        valid_dataframe,
        sample_provider_inputs,
        sample_metadata_inputs,
        sample_variable_dimension_file,
        sample_dimension_file,
    ):
        """Test that valid dumped JSON structure passes validation."""
        # Create valid JSON structure
        valid_json_data = {
            "input_data": valid_dataframe.to_dict(orient="records"),
            "provider": sample_provider_inputs,
            "metadata": sample_metadata_inputs,
        }
        json_string = json.dumps(valid_json_data)

        # Should not raise any exception
        result = validate_dumped_json(
            json_string,
            vardim_file_path=sample_variable_dimension_file,
            dimension_file_path=sample_dimension_file,
        )
        assert result is None

    def test_invalid_json_string_fails(
        self, sample_variable_dimension_file, sample_dimension_file
    ):
        """Test that invalid JSON string raises ValueError."""
        invalid_json = '{"input_data": [}, "provider": {'  # Malformed JSON

        with pytest.raises(json.JSONDecodeError):
            validate_dumped_json(
                invalid_json,
                vardim_file_path=sample_variable_dimension_file,
                dimension_file_path=sample_dimension_file,
            )

    def test_missing_required_keys_fails(
        self,
        valid_dataframe,
        sample_provider_inputs,
        sample_variable_dimension_file,
        sample_dimension_file,
    ):
        """Test that missing required keys raise ValueError."""
        # Missing 'metadata' key
        incomplete_json_data = {
            "input_data": valid_dataframe.to_dict(orient="records"),
            "provider": sample_provider_inputs,
            # Missing: metadata
        }
        json_string = json.dumps(incomplete_json_data)

        with pytest.raises(ValueError, match="[Mm]issing.*key"):
            validate_dumped_json(
                json_string,
                vardim_file_path=sample_variable_dimension_file,
                dimension_file_path=sample_dimension_file,
            )

    def test_multiple_missing_keys_fails(
        self, valid_dataframe, sample_variable_dimension_file, sample_dimension_file
    ):
        """Test that multiple missing keys are properly reported."""
        # Missing 'provider' and 'metadata' keys
        incomplete_json_data = {
            "input_data": valid_dataframe.to_dict(orient="records")
            # Missing: provider, metadata
        }
        json_string = json.dumps(incomplete_json_data)

        with pytest.raises(ValueError, match="[Mm]issing.*key"):
            validate_dumped_json(
                json_string,
                vardim_file_path=sample_variable_dimension_file,
                dimension_file_path=sample_dimension_file,
            )

    def test_unexpected_keys_fails(
        self,
        valid_dataframe,
        sample_provider_inputs,
        sample_metadata_inputs,
        sample_variable_dimension_file,
        sample_dimension_file,
    ):
        """Test that unexpected keys raise ValueError."""
        # Add unexpected keys
        json_with_extra_keys = {
            "input_data": valid_dataframe.to_dict(orient="records"),
            "provider": sample_provider_inputs,
            "metadata": sample_metadata_inputs,
            "extra_key": "should_not_be_here",
            "another_extra": "also_invalid",
        }
        json_string = json.dumps(json_with_extra_keys)

        with pytest.raises(ValueError, match="[Uu]nexpected.*key"):
            validate_dumped_json(
                json_string,
                vardim_file_path=sample_variable_dimension_file,
                dimension_file_path=sample_dimension_file,
            )

    def test_input_data_not_list_fails(
        self,
        sample_provider_inputs,
        sample_metadata_inputs,
        sample_variable_dimension_file,
        sample_dimension_file,
    ):
        """Test that input_data must be a list."""
        # input_data as dict instead of list
        invalid_json_data = {
            "input_data": {"location": "france", "value": 15},  # Should be list
            "provider": sample_provider_inputs,
            "metadata": sample_metadata_inputs,
        }
        json_string = json.dumps(invalid_json_data)

        with pytest.raises(ValueError, match="list"):
            validate_dumped_json(
                json_string,
                vardim_file_path=sample_variable_dimension_file,
                dimension_file_path=sample_dimension_file,
            )

    def test_input_data_string_fails(
        self,
        sample_provider_inputs,
        sample_metadata_inputs,
        sample_variable_dimension_file,
        sample_dimension_file,
    ):
        """Test that input_data as string fails."""
        invalid_json_data = {
            "input_data": "not_a_list",
            "provider": sample_provider_inputs,
            "metadata": sample_metadata_inputs,
        }
        json_string = json.dumps(invalid_json_data)

        with pytest.raises(ValueError, match="list"):
            validate_dumped_json(
                json_string,
                vardim_file_path=sample_variable_dimension_file,
                dimension_file_path=sample_dimension_file,
            )

    def test_empty_input_data_fails(
        self,
        sample_provider_inputs,
        sample_metadata_inputs,
        sample_variable_dimension_file,
        sample_dimension_file,
    ):
        """Test that empty input_data list raises ValueError."""
        invalid_json_data = {
            "input_data": [],  # Empty list
            "provider": sample_provider_inputs,
            "metadata": sample_metadata_inputs,
        }
        json_string = json.dumps(invalid_json_data)

        with pytest.raises(ValueError, match="empty"):
            validate_dumped_json(
                json_string,
                vardim_file_path=sample_variable_dimension_file,
                dimension_file_path=sample_dimension_file,
            )

    def test_invalid_provider_structure_fails(
        self,
        valid_dataframe,
        sample_metadata_inputs,
        sample_variable_dimension_file,
        sample_dimension_file,
    ):
        """Test that invalid provider structure is caught."""
        # Provider missing required fields
        invalid_provider = {
            "first_name": "John"
            # Missing: last_name, email_address
        }

        invalid_json_data = {
            "input_data": valid_dataframe.to_dict(orient="records"),
            "provider": invalid_provider,
            "metadata": sample_metadata_inputs,
        }
        json_string = json.dumps(invalid_json_data)

        with pytest.raises(ValueError):
            validate_dumped_json(
                json_string,
                vardim_file_path=sample_variable_dimension_file,
                dimension_file_path=sample_dimension_file,
            )

    def test_invalid_provider_email_fails(
        self,
        valid_dataframe,
        sample_metadata_inputs,
        sample_variable_dimension_file,
        sample_dimension_file,
    ):
        """Test that invalid provider email is caught."""
        invalid_provider = {
            "first_name": "John",
            "last_name": "Doe",
            "email_address": "not-an-email",  # Invalid email format
        }

        invalid_json_data = {
            "input_data": valid_dataframe.to_dict(orient="records"),
            "provider": invalid_provider,
            "metadata": sample_metadata_inputs,
        }
        json_string = json.dumps(invalid_json_data)

        with pytest.raises(ValueError):
            validate_dumped_json(
                json_string,
                vardim_file_path=sample_variable_dimension_file,
                dimension_file_path=sample_dimension_file,
            )

    def test_invalid_metadata_structure_fails(
        self,
        valid_dataframe,
        sample_provider_inputs,
        sample_variable_dimension_file,
        sample_dimension_file,
    ):
        """Test that invalid metadata structure is caught."""
        # Metadata missing required fields
        invalid_metadata = {
            "link": "https://example.com"
            # Missing: source, project
        }

        invalid_json_data = {
            "input_data": valid_dataframe.to_dict(orient="records"),
            "provider": sample_provider_inputs,
            "metadata": invalid_metadata,
        }
        json_string = json.dumps(invalid_json_data)

        with pytest.raises(ValueError):
            validate_dumped_json(
                json_string,
                vardim_file_path=sample_variable_dimension_file,
                dimension_file_path=sample_dimension_file,
            )

    def test_invalid_dataframe_structure_fails(
        self,
        sample_provider_inputs,
        sample_metadata_inputs,
        sample_variable_dimension_file,
        sample_dimension_file,
    ):
        """Test that invalid DataFrame structure is caught."""
        # DataFrame data missing required columns
        invalid_input_data = [
            {
                "location": "spain",
                "value": 25,
                # Missing: unit, time, scenario, variable
            }
        ]

        invalid_json_data = {
            "input_data": invalid_input_data,
            "provider": sample_provider_inputs,
            "metadata": sample_metadata_inputs,
        }
        json_string = json.dumps(invalid_json_data)

        with pytest.raises(ValueError):
            validate_dumped_json(
                json_string,
                vardim_file_path=sample_variable_dimension_file,
                dimension_file_path=sample_dimension_file,
            )

    def test_multiple_input_data_records(
        self,
        sample_provider_inputs,
        sample_metadata_inputs,
        sample_variable_dimension_file,
        sample_dimension_file,
    ):
        """Test validation with multiple input_data records."""
        multiple_records_df = pd.DataFrame(
            [
                {
                    "location": "france",
                    "object": "car",
                    "value": 15,
                    "unit": "year",
                    "time": 2015,
                    "scenario": "historical",
                    "variable": "lifetime_mean_value",
                },
                {
                    "location": "germany",
                    "object": "truck",
                    "value": 20,
                    "unit": "year",
                    "time": 2040,
                    "scenario": "projection",
                    "variable": "lifetime_mean_value",
                },
            ]
        )

        valid_json_data = {
            "input_data": multiple_records_df.to_dict(orient="records"),
            "provider": sample_provider_inputs,
            "metadata": sample_metadata_inputs,
        }
        json_string = json.dumps(valid_json_data)

        # Should not raise exception
        result = validate_dumped_json(
            json_string,
            vardim_file_path=sample_variable_dimension_file,
            dimension_file_path=sample_dimension_file,
        )
        assert result is None

    def test_with_different_aspect_columns(
        self,
        sample_provider_inputs,
        sample_metadata_inputs,
        sample_variable_dimension_file,
        sample_dimension_file,
    ):
        """Test validation with different valid aspect columns."""
        df_with_process = pd.DataFrame(
            [
                {
                    "location": "france",
                    "object": "car",
                    "process": "manufacturing",
                    "value": 1,
                    "unit": "pieces",
                    "time": 2024,
                    "scenario": "current",
                    "variable": "control_flow_shares",
                }
            ]
        )

        valid_json_data = {
            "input_data": df_with_process.to_dict(orient="records"),
            "provider": sample_provider_inputs,
            "metadata": sample_metadata_inputs,
        }
        json_string = json.dumps(valid_json_data)

        # Should not raise exception
        result = validate_dumped_json(
            json_string,
            vardim_file_path=sample_variable_dimension_file,
            dimension_file_path=sample_dimension_file,
        )
        assert result is None

    def test_unicode_data_handling(
        self,
        sample_provider_inputs,
        sample_metadata_inputs,
        sample_variable_dimension_file,
        sample_dimension_file,
    ):
        """Test validation with Unicode characters in data."""
        unicode_df = pd.DataFrame(
            [
                {
                    "location": "france",
                    "object": "SUV",
                    "value": 0.5,
                    "unit": "années",
                    "time": 2023,
                    "scenario": "réaliste",
                    "variable": "lifetime_standard_deviation",
                }
            ]
        )

        valid_json_data = {
            "input_data": unicode_df.to_dict(orient="records"),
            "provider": sample_provider_inputs,
            "metadata": sample_metadata_inputs,
        }
        json_string = json.dumps(valid_json_data, ensure_ascii=False)

        # Should not raise exception
        result = validate_dumped_json(
            json_string,
            vardim_file_path=sample_variable_dimension_file,
            dimension_file_path=sample_dimension_file,
        )
        assert result is None

    def test_numeric_data_types(
        self,
        sample_provider_inputs,
        sample_metadata_inputs,
        sample_variable_dimension_file,
        sample_dimension_file,
    ):
        """Test validation with various numeric data types."""
        numeric_df = pd.DataFrame(
            [
                {
                    "location": "germany",
                    "object": "truck",
                    "value": 20.75,  # float
                    "unit": "year",
                    "time": 2034,  # int
                    "scenario": "baseline",
                    "variable": "lifetime_mean_value",
                }
            ]
        )

        valid_json_data = {
            "input_data": numeric_df.to_dict(orient="records"),
            "provider": sample_provider_inputs,
            "metadata": sample_metadata_inputs,
        }
        json_string = json.dumps(valid_json_data)

        # Should not raise exception
        result = validate_dumped_json(
            json_string,
            vardim_file_path=sample_variable_dimension_file,
            dimension_file_path=sample_dimension_file,
        )
        assert result is None


class TestValidateDumpedJsonIntegration:
    """Integration tests for validate_dumped_json with dump_json output."""

    def test_validates_dump_json_output(
        self,
        valid_dataframe,
        sample_provider_inputs,
        sample_metadata_inputs,
        sample_variable_dimension_file,
        sample_dimension_file,
    ):
        """Test that validate_dumped_json can validate dump_json output."""
        from src.mater_data_providing.serialization import dump_json

        # Create JSON using dump_json
        json_output = dump_json(
            valid_dataframe,
            sample_provider_inputs,
            sample_metadata_inputs,
            vardim_file_path=sample_variable_dimension_file,
            dimension_file_path=sample_dimension_file,
        )

        # Should validate successfully
        result = validate_dumped_json(
            json_output,
            vardim_file_path=sample_variable_dimension_file,
            dimension_file_path=sample_dimension_file,
        )
        assert result is None

    def test_integration_with_invalid_dump_json_input(
        self,
        sample_provider_inputs,
        sample_metadata_inputs,
        sample_variable_dimension_file,
        sample_dimension_file,
    ):
        """Test integration when dump_json receives invalid input."""
        from src.mater_data_providing.serialization import dump_json

        # This should fail in dump_json before reaching validate_dumped_json
        invalid_df = pd.DataFrame([{"location": "spain"}])

        with pytest.raises(ValueError):
            dump_json(
                invalid_df,
                sample_provider_inputs,
                sample_metadata_inputs,
                vardim_file_path=sample_variable_dimension_file,
                dimension_file_path=sample_dimension_file,
            )


class TestValidateDimensionFile:
    """Simple test suite for validate_dimension_file function."""

    def test_valid_dimension_file_passes(self, sample_dimension_file):
        """Test that valid dimension file passes validation."""
        # Should not raise any exception
        validate_dimension_file(dimension_file_path=sample_dimension_file)

    def test_valid_dimension_json_string_passes(self, sample_dimension_json):
        """Test that valid dimension JSON string passes validation."""
        # Should not raise any exception
        validate_dimension_file(dimension_json=sample_dimension_json)

    def test_missing_required_keys_fails(self, tmp_path):
        """Test that missing required columns raise KeyError."""
        # Missing 'name' column
        invalid_data = [
            {
                "value": "france",
                "equivalence": {},
                "parents_values": {},
                # Missing: name
            }
        ]

        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, "w") as f:
            json.dump(invalid_data, f)

        with pytest.raises(KeyError, match="[Mm]issing.*require"):
            validate_dimension_file(dimension_file_path=str(invalid_file))

    def test_invalid_name_fails(self, tmp_path):
        """Test that invalid names raise ValueError."""
        # Missing 'name' column
        invalid_data = [
            {
                "name": "invalid_name",
                "value": "france",
                "equivalence": {},
                "parents_values": {},
            }
        ]

        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, "w") as f:
            json.dump(invalid_data, f)

        with pytest.raises(ValueError, match="[Vv]alid.*name"):
            validate_dimension_file(dimension_file_path=str(invalid_file))

    def test_invalid_keys_fails(self, tmp_path):
        """Test that invalid column names raise KeyError."""
        invalid_data = [
            {
                "name": "location",
                "value": "france",
                "equivalence": {},
                "parents_values": {},
                "invalid_column": "should_not_be_here",
            }
        ]

        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, "w") as f:
            json.dump(invalid_data, f)

        with pytest.raises(KeyError, match="[Ii]nvalid.*key"):
            validate_dimension_file(dimension_file_path=str(invalid_file))

    def test_missing_value_fails(self, tmp_path):
        """Test that missing 'value' entries raise ValueError."""
        invalid_data = [
            {
                "name": "location",
                "value": None,  # Missing value
                "equivalence": {},
                "parents_values": {},
            },
            {
                "name": "location",
                "value": "france",
                "equivalence": {},
                "parents_values": {},
            },
        ]

        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, "w") as f:
            json.dump(invalid_data, f)

        with pytest.raises(KeyError, match="[Mm]issing.*value"):
            validate_dimension_file(dimension_file_path=str(invalid_file))

    def test_missing_name_fails(self, tmp_path):
        """Test that missing 'name' entries raise ValueError."""
        invalid_data = [
            {
                "name": None,  # Missing name
                "value": "france",
                "equivalence": {},
                "parents_values": {},
            },
            {
                "name": "location",
                "value": "germany",
                "equivalence": {},
                "parents_values": {},
            },
        ]

        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, "w") as f:
            json.dump(invalid_data, f)

        with pytest.raises(KeyError, match="[Mm]issing.*name"):
            validate_dimension_file(dimension_file_path=str(invalid_file))

    def test_equivalence_not_dict_fails(self, tmp_path):
        """Test that non-dict equivalence raises TypeError."""
        invalid_data = [
            {
                "name": "location",
                "value": "france",
                "equivalence": "not_a_dict",  # Should be dict
                "parents_values": {},
            }
        ]

        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, "w") as f:
            json.dump(invalid_data, f)

        with pytest.raises(TypeError, match="[Ee]quivalence.*dict"):
            validate_dimension_file(dimension_file_path=str(invalid_file))

    def test_parents_values_not_dict_fails(self, tmp_path):
        """Test that non-dict parents_values raises TypeError."""
        invalid_data = [
            {
                "name": "location",
                "value": "france",
                "equivalence": {},
                "parents_values": "not_a_dict",  # Should be dict
            }
        ]

        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, "w") as f:
            json.dump(invalid_data, f)

        with pytest.raises(TypeError, match="[Pp]arent.*value.*dict"):
            validate_dimension_file(dimension_file_path=str(invalid_file))

    def test_invalid_parent_value_fails(self, tmp_path):
        """Test that missing 'value' entries raise ValueError."""
        invalid_data = [
            {
                "name": "location",
                "value": "france",
                "equivalence": {},
                "parents_values": {"default": "europe"},
            },
            {
                "name": "location",
                "value": "world",
                "equivalence": {},
                "parents_values": {},
            },
        ]

        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, "w") as f:
            json.dump(invalid_data, f)

        with pytest.raises(ValueError, match="[Vv]alid.*parent"):
            validate_dimension_file(dimension_file_path=str(invalid_file))

    def test_wrong_parameter_types_fail(self, sample_dimension_file):
        """Test that wrong parameter types raise TypeError."""
        with pytest.raises(TypeError, match="[Dd]imension.*name.*set"):
            validate_dimension_file(
                dimension_names="not_a_set", dimension_file_path=sample_dimension_file
            )

        with pytest.raises(TypeError, match="[Rr]equire.*set"):
            validate_dimension_file(
                required_keys=["not", "a", "set"],
                dimension_file_path=sample_dimension_file,
            )

        with pytest.raises(TypeError, match="[Oo]ptional.*set"):
            validate_dimension_file(
                optional_keys=("not", "a", "set"),
                dimension_file_path=sample_dimension_file,
            )


class TestValidateVariableDimensionFile:
    def test_valid_dimension_file_passes(self, sample_variable_dimension_file):
        result = validate_variable_dimension_file(
            vardim_file_path=sample_variable_dimension_file
        )
        assert result is None

    def test_missing_key_raises_error(self):
        not_valid = [
            {
                "dimension": "location",
                "property": "intensive",
            },
            {
                "variable": "lifetime_mean_value",
                "dimension": "object",
                "property": "intensive",
            },
        ]

        with pytest.raises(KeyError, match="[Mm]issing.*key"):
            validate_variable_dimension_file(json.dumps(not_valid))

    def test_invalid_key_raises_error(self):
        not_valid = [
            {
                "invalid_key": "lifetime_mean_value",
                "dimension": "location",
                "property": "intensive",
            },
            {
                "variable": "lifetime_mean_value",
                "dimension": "object",
                "property": "intensive",
            },
        ]

        with pytest.raises(KeyError, match="[Ii]nvalid.*key"):
            validate_variable_dimension_file(json.dumps(not_valid))

    def test_globally_missing_key_raises_error(self):
        not_valid = [
            {
                "dimension": "location",
                "property": "intensive",
            },
            {
                "dimension": "object",
                "property": "intensive",
            },
        ]

        with pytest.raises(KeyError, match="[Mm]iss.*key"):
            validate_variable_dimension_file(json.dumps(not_valid))

    def test_invalid_arg_type_raises_error(self, sample_variable_dimension_file):
        with pytest.raises(TypeError, match="[Rr]equire.*set"):
            validate_variable_dimension_file(
                vardim_file_path=sample_variable_dimension_file,
                required_keys="not a set",
            )
        with pytest.raises(TypeError, match="[Dd]imension.*set"):
            validate_variable_dimension_file(
                vardim_file_path=sample_variable_dimension_file,
                dimension_names=pd.DataFrame(),
            )
        with pytest.raises(TypeError, match="[Pp]ropert.*set"):
            validate_variable_dimension_file(
                vardim_file_path=sample_variable_dimension_file,
                property_values=["not", "a", "set"],
            )

    def test_invalid_aspect_names_raises_error(self):
        not_valid = [
            {
                "variable": "lifetime_mean_value",
                "dimension": "invalid_name",
                "property": "intensive",
            },
            {
                "variable": "lifetime_mean_value",
                "dimension": "object",
                "property": "intensive",
            },
        ]

        with pytest.raises(ValueError, match="[Ii]nvalid.*aspect"):
            validate_variable_dimension_file(json.dumps(not_valid))

    def test_invalid_property_raises_error(self):
        not_valid = [
            {
                "variable": "lifetime_mean_value",
                "dimension": "object",
                "property": "intensive",
            },
            {
                "variable": "lifetime_mean_value",
                "dimension": "object",
                "property": "invalid_property",
            },
        ]

        with pytest.raises(ValueError, match="[Ii]nvalid.*propert"):
            validate_variable_dimension_file(json.dumps(not_valid))


class TestValidateVariableElements:
    def test_valid_element_passes(
        self, valid_dataframe, sample_variable_dimension_file
    ):
        result = validate_variable_elements(
            valid_dataframe, sample_variable_dimension_file
        )
        assert result is None

    def test_missing_key_in_variable_dimension_raises_error(
        self, tmp_path, valid_dataframe
    ):
        not_valid = [
            {
                "dimension": "location",
                "property": "intensive",
            },
            {
                "variable": "lifetime_mean_value",
                "dimension": "object",
                "property": "intensive",
            },
        ]
        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, "w") as f:
            json.dump(not_valid, f)

        with pytest.raises(KeyError, match="[Mm]issing.*key"):
            validate_variable_elements(valid_dataframe, invalid_file)

    def test_invalid_element_in_dataframe_raises_error(
        self, sample_variable_dimension_file
    ):
        not_valid = pd.DataFrame(
            [
                {
                    "location": "france",
                    "object": "car",
                    "value": 15,
                    "unit": "year",
                    "time": 2015,
                    "scenario": "historical",
                    "variable": "not_in_variable_dimension",
                }
            ]
        )
        with pytest.raises(ValueError, match="[In]nvalid.*variable"):
            validate_variable_elements(not_valid, sample_variable_dimension_file)

    def test_invalid_aspect_list_for_variable_in_dataframe_raises_error(
        self, sample_variable_dimension_file
    ):
        not_valid = pd.DataFrame(
            [
                {
                    "location": "france",
                    "object": "car",
                    "process": "car manufacturing",  # invalid aspect for lifetime_mean_value
                    "value": 15,
                    "unit": "year",
                    "time": 2015,
                    "scenario": "historical",
                    "variable": "lifetime_mean_value",
                },
                {
                    "location": "france",
                    "object": "car",
                    "value": 16,
                    "unit": "year",
                    "time": 2020,
                    "scenario": "historical",
                    "variable": "lifetime_mean_value",
                },
                {
                    "location": "france",
                    "object": "car",
                    "process": "car manufacturing",
                    "value": 1,
                    "unit": "year",
                    "time": 2015,
                    "scenario": "historical",
                    "variable": "control_flow_shares",
                },
            ]
        )
        with pytest.raises(ValueError, match="[Vv]alid.*variable"):
            validate_variable_elements(not_valid, sample_variable_dimension_file)


class TestValidateInputDataFull:
    def test_valid_input_data_passes(
        self, valid_dataframe, sample_variable_dimension_file, sample_dimension_file
    ):
        result = validate_input_data_full(
            valid_dataframe,
            vardim_file_path=sample_variable_dimension_file,
            dimension_file_path=sample_dimension_file,
        )
        assert result is None

    def test_invalid_aspect_list_for_variable_in_dataframe_raises_error(
        self, sample_variable_dimension_file, sample_dimension_file
    ):
        not_valid = pd.DataFrame(
            [
                {
                    "location": "france",
                    "object": "car",
                    "process": "car manufacturing",  # invalid aspect for lifetime_mean_value
                    "value": 15,
                    "unit": "year",
                    "time": 2015,
                    "scenario": "historical",
                    "variable": "lifetime_mean_value",
                },
                {
                    "location": "france",
                    "object": "car",
                    "value": 16,
                    "unit": "year",
                    "time": 2020,
                    "scenario": "historical",
                    "variable": "lifetime_mean_value",
                },
                {
                    "location": "france",
                    "object": "car",
                    "process": "car manufacturing",
                    "value": 1,
                    "unit": "year",
                    "time": 2015,
                    "scenario": "historical",
                    "variable": "control_flow_shares",
                },
            ]
        )
        with pytest.raises(ValueError, match="[Vv]alid.*variable"):
            validate_input_data_full(
                not_valid,
                vardim_file_path=sample_variable_dimension_file,
                dimension_file_path=sample_dimension_file,
            )

    def test_missing_name_in_dimension_fails(
        self, valid_dataframe, tmp_path, sample_variable_dimension_file
    ):
        """Test that missing 'name' entries raise KeyError."""
        invalid_data = [
            {
                "name": None,  # Missing name
                "value": "france",
                "equivalence": {},
                "parents_values": {},
            }
        ]

        invalid_file = tmp_path / "invalid.json"
        with open(invalid_file, "w") as f:
            json.dump(invalid_data, f)

        with pytest.raises(KeyError, match="[Mm]issing.*name"):
            validate_input_data_full(
                valid_dataframe,
                vardim_file_path=sample_variable_dimension_file,
                dimension_file_path=str(invalid_file),
            )
