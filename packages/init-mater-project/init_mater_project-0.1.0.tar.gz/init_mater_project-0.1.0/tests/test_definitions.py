"""
This module tests the definitions functions.

Copyright (C) 2025 @verzierf <francois.verzier@univ-grenoble-alpes.fr>

SPDX-License-Identifier: LGPL-3.0-or-later
"""

from src.mater_data_providing.definitions import (
    metadata_definition,
    provider_definition,
)


class TestMetadataDefinition:
    """Test suite for metadata_definition function."""

    def test_metadata_definition_basic(self, sample_metadata_inputs):
        """Test basic functionality with standard inputs."""
        result = metadata_definition(**sample_metadata_inputs)

        expected = {
            "link": sample_metadata_inputs["link"],
            "source": sample_metadata_inputs["source"],
            "project": sample_metadata_inputs["project"],
        }
        assert result == expected


class TestProviderDefinition:
    """Test suite for provider_definition function."""

    def test_provider_definition_basic(self, sample_provider_inputs):
        """Test basic functionality with standard inputs."""
        result = provider_definition(**sample_provider_inputs)

        assert result["first_name"] == sample_provider_inputs["first_name"]
        assert result["last_name"] == sample_provider_inputs["last_name"]
        assert "@" in result["email_address"]
