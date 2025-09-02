"""
Pytest configuration and shared fixtures.

Copyright (C) 2025 @verzierf <francois.verzier@univ-grenoble-alpes.fr>

SPDX-License-Identifier: LGPL-3.0-or-later
"""

import json

import pandas as pd
import pytest


@pytest.fixture
def sample_metadata_inputs():
    """Sample inputs for metadata_definition."""
    return {
        "link": "https://data.example.com/dataset.csv",
        "source": "European Environment Agency",
        "project": "Carbon Footprint Analysis 2024",
    }


@pytest.fixture
def sample_provider_inputs():
    """Sample inputs for provider_definition."""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email_address": "john.doe@example.com",
    }


@pytest.fixture
def valid_dataframe():
    """Valid DataFrame for testing."""
    return pd.DataFrame(
        [
            {
                "location": "france",
                "object": "car",
                "value": 15,
                "unit": "year",
                "time": 2015,
                "scenario": "historical",
                "variable": "lifetime_mean_value",
            }
        ]
    )


@pytest.fixture
def invalid_dataframe_missing_required():
    """DataFrame missing required columns."""
    return pd.DataFrame(
        [
            {
                "location": "france",
                "value": 15,
                # Missing: unit, time, scenario, variable
            }
        ]
    )


@pytest.fixture
def invalid_dataframe_missing_aspect():
    """DataFrame missing aspect columns."""
    return pd.DataFrame(
        [
            {
                "value": 15,
                "unit": "year",
                "time": 2015,
                "scenario": "historical",
                "variable": "lifetime",
                # Missing any aspect column
            }
        ]
    )


@pytest.fixture
def expected_json_structure():
    """Define expected structure for dump_json(valid_dataframe, sample_provider_inputs, sample_metadata_inputs)."""
    return {
        "input_data": [
            {
                "location": "france",
                "object": "car",
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
            "email_address": "john.doe@example.com",
        },
        "metadata": {
            "link": "https://data.example.com/dataset.csv",
            "source": "European Environment Agency",
            "project": "Carbon Footprint Analysis 2024",
        },
    }


@pytest.fixture
def expected_json_string(expected_json_structure):
    """Create expected JSON string using json.dumps directly from dump_json(valid_dataframe, sample_provider_inputs, sample_metadata_inputs)."""
    return json.dumps(expected_json_structure, indent=2, ensure_ascii=False)


@pytest.fixture
def sample_dimension_file(tmp_path):
    """Create a temporary dimension.json file for testing."""
    dimension_data = [
        {
            "name": "location",
            "value": "france",
            "equivalence": {"equ1": "FR", "equ2": "FRA"},
        },
        {"name": "location", "value": "germany", "equivalence": {"equ1": "GE"}},
        {
            "name": "object",
            "value": "car",
            "equivalence": {"equ1": "PLDV", "equ2": "auto"},
        },
        {"name": "object", "value": "truck", "equivalence": {"equ1": "HV"}},
        {
            "name": "process",
            "value": "manufacturing",
            "equivalence": {"equ": "manuf"},
        },
        {
            "name": "object",
            "value": "SUV",
            "equivalence": {"equ": "big car"},
            "parents_values": {"default": "car"},
        },
    ]

    # Create temporary file
    dimension_file = tmp_path / "dimension.json"
    with open(dimension_file, "w") as f:
        json.dump(dimension_data, f)

    return str(dimension_file)


@pytest.fixture
def sample_dimension_json(sample_dimension_file):
    with open(sample_dimension_file, "r") as f:
        data = json.load(f)
    return json.dumps(data)


@pytest.fixture
def sample_variable_dimension_file(tmp_path):
    """Create a temporary variable_dimension.json file for testing."""
    variable_dimension_data = [
        {
            "variable": "lifetime_mean_value",
            "dimension": "location",
            "property": "intensive",
        },
        {
            "variable": "lifetime_mean_value",
            "dimension": "object",
            "property": "intensive",
        },
        {
            "variable": "lifetime_standard_deviation",
            "dimension": "location",
            "property": "intensive",
        },
        {
            "variable": "lifetime_standard_deviation",
            "dimension": "object",
            "property": "intensive",
        },
        {
            "variable": "control_flow_shares",
            "dimension": "location",
            "property": "intensive",
        },
        {
            "variable": "control_flow_shares",
            "dimension": "object",
            "property": "intensive",
        },
        {
            "variable": "control_flow_shares",
            "dimension": "process",
            "property": "extensive",
        },
    ]

    # Create temporary file
    variable_dimension_file = tmp_path / "variable_dimension.json"
    with open(variable_dimension_file, "w") as f:
        json.dump(variable_dimension_data, f)

    return str(variable_dimension_file)


@pytest.fixture
def sample_dict_data():
    """Sample dictionary data for testing."""
    return {
        "name": "John Doe",
        "age": 30,
        "skills": ["Python", "JavaScript", "SQL"],
        "active": True,
        "metadata": {"created": "2024-01-01", "version": 1.0},
    }


@pytest.fixture
def sample_list_data():
    """Sample list data for testing."""
    return [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
        {"id": 3, "name": "Charlie"},
    ]


@pytest.fixture
def sample_json_string():
    """Sample JSON string data for testing."""
    return '{"message": "Hello World", "count": 42, "active": true}'
