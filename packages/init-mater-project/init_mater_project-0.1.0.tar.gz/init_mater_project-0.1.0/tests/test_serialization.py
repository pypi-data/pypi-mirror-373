"""
This module tests the serialization functions.

Copyright (C) 2025 @verzierf <francois.verzier@univ-grenoble-alpes.fr>

SPDX-License-Identifier: LGPL-3.0-or-later
"""

import json

import pandas as pd
import pytest

from src.mater_data_providing.serialization import (
    dump_json,
    standardize_json,
    to_mater_json,
)


class TestDumpJson:
    """Test suite for dump_json function."""

    def test_valid_inputs(
        self,
        sample_metadata_inputs,
        sample_provider_inputs,
        valid_dataframe,
        expected_json_string,
        sample_dimension_file,
        sample_variable_dimension_file,
    ):
        """tests valid call of the function"""
        df = pd.DataFrame(valid_dataframe)
        result = dump_json(
            df,
            sample_provider_inputs,
            sample_metadata_inputs,
            vardim_file_path=sample_variable_dimension_file,
            dimension_file_path=sample_dimension_file,
        )
        assert result == expected_json_string

    def test_calls_validate_input_data_structure(
        self,
        sample_provider_inputs,
        sample_metadata_inputs,
        sample_dimension_file,
        sample_variable_dimension_file,
    ):
        """Test that input_data validation function is actually called."""
        invalid_df = pd.DataFrame([{"location": "spain"}])  # Any invalid DataFrame

        with pytest.raises(ValueError):  # No specific match needed
            dump_json(
                invalid_df,
                sample_provider_inputs,
                sample_metadata_inputs,
                vardim_file_path=sample_variable_dimension_file,
                dimension_file_path=sample_dimension_file,
            )

    def test_calls_validate_provider(
        self,
        valid_dataframe,
        sample_metadata_inputs,
        sample_dimension_file,
        sample_variable_dimension_file,
    ):
        """Test that provider validation function is actually called."""
        invalid_provider = {"invalid_key": "anything"}  # Any invalid dict

        with pytest.raises(ValueError):  # No specific match needed
            dump_json(
                valid_dataframe,
                invalid_provider,
                sample_metadata_inputs,
                vardim_file_path=sample_variable_dimension_file,
                dimension_file_path=sample_dimension_file,
            )

    def test_calls_validate_metadata(
        self,
        valid_dataframe,
        sample_provider_inputs,
        sample_dimension_file,
        sample_variable_dimension_file,
    ):
        """Test that metadata validation function is actually called."""
        invalid_metadata = {"invalid_key": "anything"}  # Any invalid dict

        with pytest.raises(ValueError):  # No specific match needed
            dump_json(
                valid_dataframe,
                sample_provider_inputs,
                invalid_metadata,
                vardim_file_path=sample_variable_dimension_file,
                dimension_file_path=sample_dimension_file,
            )


class TestStandardizeJson:
    """Test suite for standardize_json function."""

    def test_standardize_valid_json_with_validation(
        self,
        expected_json_string,
        sample_variable_dimension_file,
        sample_dimension_file,
    ):
        """Test standardizing valid JSON with validation enabled."""
        result = standardize_json(
            expected_json_string,
            vardim_file_path=sample_variable_dimension_file,
            dimension_file_path=sample_dimension_file,
            validation=True,
        )

        # Should return valid JSON
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        assert set(parsed.keys()) == {"input_data", "provider", "metadata"}
        assert "dimensions_values" in parsed["input_data"][0]
        assert set(parsed["input_data"][0]["dimensions_values"].keys()) == {
            "location",
            "object",
        }
        assert parsed["input_data"][0]["dimensions_values"]["location"] == "france"
        assert parsed["input_data"][0]["dimensions_values"]["object"] == "car"

    def test_standardize_valid_json_without_validation(
        self,
        expected_json_string,
        sample_variable_dimension_file,
        sample_dimension_file,
    ):
        """Test standardizing valid JSON with validation disabled."""
        result = standardize_json(
            expected_json_string,
            vardim_file_path=sample_variable_dimension_file,
            dimension_file_path=sample_dimension_file,
            validation=False,
        )

        # Should return valid JSON
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        assert set(parsed.keys()) == {"input_data", "provider", "metadata"}
        assert "dimensions_values" in parsed["input_data"][0]
        assert set(parsed["input_data"][0]["dimensions_values"].keys()) == {
            "location",
            "object",
        }
        assert parsed["input_data"][0]["dimensions_values"]["location"] == "france"
        assert parsed["input_data"][0]["dimensions_values"]["object"] == "car"

    def test_standardize_json_with_equivalences(
        self, sample_variable_dimension_file, sample_dimension_file
    ):
        """Test standardizing JSON that contains equivalence values."""
        # JSON with equivalence values that should be replaced
        json_with_equivalences = json.dumps(
            {
                "input_data": [
                    {
                        "location": "FR",  # Should become "france"
                        "object": "PLDV",  # Should become "car"
                        "value": 15,
                        "unit": "year",
                        "time": 2015,
                        "scenario": "historical",
                        "variable": "lifetime_mean_value",
                    }
                ],
                "provider": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "email_address": "john@example.com",
                },
                "metadata": {"link": "test.com", "source": "Test", "project": "Study"},
            }
        )

        result = standardize_json(
            json_with_equivalences,
            vardim_file_path=sample_variable_dimension_file,
            dimension_file_path=sample_dimension_file,
            validation=False,
        )
        parsed = json.loads(result)

        # Should return valid JSON
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        assert set(parsed.keys()) == {"input_data", "provider", "metadata"}
        assert "dimensions_values" in parsed["input_data"][0]
        assert set(parsed["input_data"][0]["dimensions_values"].keys()) == {
            "location",
            "object",
        }
        assert parsed["input_data"][0]["dimensions_values"]["location"] == "france"
        assert parsed["input_data"][0]["dimensions_values"]["object"] == "car"

    def test_standardize_invalid_json_with_validation_fails(
        self, sample_variable_dimension_file, sample_dimension_file
    ):
        """Test that invalid JSON fails when validation is enabled."""
        invalid_json = json.dumps(
            {
                "input_data": [],  # Empty - should fail validation
                "provider": {"first_name": "John"},  # Missing fields
                "metadata": {},  # Missing fields
            }
        )

        with pytest.raises(ValueError):
            standardize_json(
                invalid_json,
                vardim_file_path=sample_variable_dimension_file,
                dimension_file_path=sample_dimension_file,
                validation=True,
            )

    def test_standardize_malformed_json_fails(
        self, sample_variable_dimension_file, sample_dimension_file
    ):
        """Test that malformed JSON always fails."""
        malformed_json = '{"input_data": [invalid json'

        with pytest.raises(json.JSONDecodeError):
            standardize_json(
                malformed_json,
                vardim_file_path=sample_variable_dimension_file,
                dimension_file_path=sample_dimension_file,
                validation=True,
            )

        with pytest.raises(json.JSONDecodeError):
            standardize_json(
                malformed_json,
                vardim_file_path=sample_variable_dimension_file,
                dimension_file_path=sample_dimension_file,
                validation=False,
            )


class TestToMaterJson:
    """Test suite for to_mater_json function."""

    def test_to_mater_json_complete_pipeline(
        self,
        valid_dataframe,
        sample_provider_inputs,
        sample_metadata_inputs,
        sample_variable_dimension_file,
        sample_dimension_file,
    ):
        """Test complete end-to-end pipeline."""
        result = to_mater_json(
            valid_dataframe,
            sample_provider_inputs,
            sample_metadata_inputs,
            vardim_file_path=sample_variable_dimension_file,
            dimension_file_path=sample_dimension_file,
        )

        # Should return valid JSON
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        assert set(parsed.keys()) == {"input_data", "provider", "metadata"}
        assert "dimensions_values" in parsed["input_data"][0]
        assert set(parsed["input_data"][0]["dimensions_values"].keys()) == {
            "location",
            "object",
        }
        assert parsed["input_data"][0]["dimensions_values"]["location"] == "france"
        assert parsed["input_data"][0]["dimensions_values"]["object"] == "car"

        # Provider and metadata should match inputs
        assert parsed["provider"] == sample_provider_inputs
        assert parsed["metadata"] == sample_metadata_inputs

    def test_to_mater_json_validates_inputs(
        self,
        sample_provider_inputs,
        sample_metadata_inputs,
        sample_variable_dimension_file,
        sample_dimension_file,
    ):
        """Test that invalid inputs are caught."""
        # Invalid DataFrame
        invalid_df = pd.DataFrame([{"location": "test"}])  # Missing required columns

        with pytest.raises(ValueError):
            to_mater_json(
                invalid_df,
                sample_provider_inputs,
                sample_metadata_inputs,
                vardim_file_path=sample_variable_dimension_file,
                dimension_file_path=sample_dimension_file,
            )

    def test_to_mater_json_with_equivalence(
        self,
        sample_provider_inputs,
        sample_metadata_inputs,
        sample_variable_dimension_file,
        sample_dimension_file,
    ):
        """Test with equivalence values in dataframe."""
        # JSON with equivalence values that should be replaced
        df_with_equivalences = pd.DataFrame(
            [
                {
                    "location": "FR",  # Should become "france"
                    "object": "PLDV",  # Should become "car"
                    "value": 15,
                    "unit": "year",
                    "time": 2015,
                    "scenario": "historical",
                    "variable": "lifetime_mean_value",
                }
            ]
        )

        result = to_mater_json(
            df_with_equivalences,
            sample_provider_inputs,
            sample_metadata_inputs,
            vardim_file_path=sample_variable_dimension_file,
            dimension_file_path=sample_dimension_file,
        )
        parsed = json.loads(result)

        # Should return valid JSON
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        assert set(parsed.keys()) == {"input_data", "provider", "metadata"}
        assert "dimensions_values" in parsed["input_data"][0]
        assert set(parsed["input_data"][0]["dimensions_values"].keys()) == {
            "location",
            "object",
        }
        assert parsed["input_data"][0]["dimensions_values"]["location"] == "france"
        assert parsed["input_data"][0]["dimensions_values"]["object"] == "car"

    def test_missing_name_in_dimension_fails(
        self,
        valid_dataframe,
        sample_provider_inputs,
        sample_metadata_inputs,
        sample_variable_dimension_file,
        tmp_path,
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
            to_mater_json(
                valid_dataframe,
                sample_provider_inputs,
                sample_metadata_inputs,
                vardim_file_path=sample_variable_dimension_file,
                dimension_file_path=str(invalid_file),
            )

    def test_invalid_aspect_list_for_variable_in_dataframe_raises_error(
        self,
        sample_provider_inputs,
        sample_metadata_inputs,
        sample_variable_dimension_file,
        sample_dimension_file,
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
            to_mater_json(
                not_valid,
                sample_provider_inputs,
                sample_metadata_inputs,
                vardim_file_path=sample_variable_dimension_file,
                dimension_file_path=sample_dimension_file,
            )
