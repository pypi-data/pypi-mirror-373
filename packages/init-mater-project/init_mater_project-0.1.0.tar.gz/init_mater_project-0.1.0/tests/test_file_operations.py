"""
This module defines file operation test classes.

Copyright (C) 2025 @verzierf <francois.verzier@univ-grenoble-alpes.fr>

SPDX-License-Identifier: LGPL-3.0-or-later
"""

import inspect
import json
import os

import pytest

from src.mater_data_providing.file_operations import write_json


class TestWriteJson:
    """Test class for the write_json function."""

    def test_write_json_dict_data(self, tmp_path, sample_dict_data):
        """Test writing dictionary data to JSON file."""
        file_path = write_json(sample_dict_data, "test_dict", tmp_path)

        assert os.path.exists(file_path)
        assert file_path.endswith("test_dict.json")

        # Verify content
        with open(file_path, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)

        assert loaded_data == sample_dict_data

    def test_write_json_list_data(self, tmp_path, sample_list_data):
        """Test writing list data to JSON file."""
        file_path = write_json(sample_list_data, "test_list", tmp_path)

        assert os.path.exists(file_path)
        assert file_path.endswith("test_list.json")

        # Verify content
        with open(file_path, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)

        assert loaded_data == sample_list_data
        assert isinstance(loaded_data, list)
        assert len(loaded_data) == 3

    def test_write_json_string_data(self, tmp_path, sample_json_string):
        """Test writing JSON string data (gets parsed first)."""
        file_path = write_json(sample_json_string, "test_string", tmp_path)

        assert os.path.exists(file_path)
        assert file_path.endswith("test_string.json")

        # Verify content - should be parsed from string
        with open(file_path, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)

        expected_data = json.loads(sample_json_string)
        assert loaded_data == expected_data
        assert loaded_data["message"] == "Hello World"
        assert loaded_data["count"] == 42
        assert loaded_data["active"] is True

    def test_write_json_creates_directory(self, tmp_path, sample_dict_data):
        """Test that the function creates directories if they don't exist."""
        nested_dir = os.path.join(tmp_path, "nested", "deep", "path")
        file_path = write_json(sample_dict_data, "test_file", nested_dir)

        assert os.path.exists(file_path)
        assert os.path.exists(nested_dir)

    def test_write_json_auto_name_detection(
        self, tmp_path, sample_dict_data, monkeypatch
    ):
        """Test automatic name detection from calling file."""
        # Mock the calling frame to simulate being called from 'test_script.py'
        mock_frame = type("MockFrame", (), {})()
        mock_frame.f_globals = {"__file__": "/path/to/test_script.py"}

        # Mock inspect.currentframe to return our mock frame
        def mock_currentframe():
            mock_current = type("MockFrame", (), {})()
            mock_current.f_back = mock_frame
            return mock_current

        monkeypatch.setattr(inspect, "currentframe", mock_currentframe)

        # Call without name parameter
        file_path = write_json(sample_dict_data, input_data_directory_path=tmp_path)

        # Should use 'test_script' as the filename
        assert file_path.endswith("test_script.json")
        assert os.path.exists(file_path)

    def test_write_json_auto_name_fallback(
        self, tmp_path, sample_dict_data, monkeypatch
    ):
        """Test fallback name when auto-detection fails."""

        # Mock inspect.currentframe to return frame without __file__
        def mock_currentframe():
            mock_current = type("MockFrame", (), {})()
            mock_frame = type("MockFrame", (), {})()
            mock_frame.f_globals = {}  # No __file__ key
            mock_current.f_back = mock_frame
            return mock_current

        monkeypatch.setattr(inspect, "currentframe", mock_currentframe)

        # Call without name parameter
        file_path = write_json(sample_dict_data, input_data_directory_path=tmp_path)

        # Should use 'output' as fallback filename
        assert file_path.endswith("output.json")
        assert os.path.exists(file_path)

    def test_write_json_custom_formatting(self, tmp_path, sample_dict_data):
        """Test custom JSON formatting options."""
        file_path = write_json(
            sample_dict_data, "formatted", tmp_path, indent=4, ensure_ascii=True
        )

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check that indentation is 4 spaces
        lines = content.split("\n")
        indented_lines = [line for line in lines if line.startswith("    ")]
        assert len(indented_lines) > 0  # Should have 4-space indented lines

    def test_write_json_removes_extension(self, tmp_path, sample_dict_data):
        """Test that .json extension is removed from name if present."""
        file_path = write_json(sample_dict_data, "test_file.json", tmp_path)

        assert file_path.endswith("test_file.json")
        assert "test_file.json.json" not in file_path

    def test_write_json_empty_name_raises_error(self, tmp_path, sample_dict_data):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            write_json(sample_dict_data, "", tmp_path)

        with pytest.raises(ValueError, match="Name cannot be empty"):
            write_json(sample_dict_data, "   ", tmp_path)

    def test_write_json_invalid_json_string_raises_error(self, tmp_path):
        """Test that invalid JSON string raises TypeError."""
        invalid_json_string = '{"invalid": json, "missing": quotes}'

        with pytest.raises(TypeError, match="Data is not JSON serializable"):
            write_json(invalid_json_string, "test_file", tmp_path)

    def test_write_json_non_serializable_data_raises_error(self, tmp_path):
        """Test that non-JSON-serializable data raises TypeError."""
        # Function objects are not JSON serializable
        non_serializable_data = {"func": lambda x: x}

        with pytest.raises(TypeError, match="Data is not JSON serializable"):
            write_json(non_serializable_data, "test_file", tmp_path)

    def test_write_json_returns_correct_path(self, tmp_path, sample_dict_data):
        """Test that the function returns the correct file path."""
        expected_path = os.path.join(tmp_path, "test_file.json")
        actual_path = write_json(sample_dict_data, "test_file", tmp_path)

        assert actual_path == expected_path

    def test_write_json_overwrites_existing_file(self, tmp_path):
        """Test that existing files are overwritten."""
        # Write initial data
        initial_data = {"version": 1}
        file_path = write_json(initial_data, "test_file", tmp_path)

        # Write new data to same file
        new_data = {"version": 2, "updated": True}
        write_json(new_data, "test_file", tmp_path)

        # Verify new data overwrote old data
        with open(file_path, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)

        assert loaded_data == new_data
        assert loaded_data != initial_data

    def test_write_json_unicode_handling(self, tmp_path):
        """Test handling of Unicode characters."""
        unicode_data = {
            "name": "José María",
            "city": "São Paulo",
            "emoji": "🎉",
            "chinese": "你好",
        }

        # Test with ensure_ascii=False (default)
        file_path = write_json(
            unicode_data, "unicode_test", tmp_path, ensure_ascii=False
        )

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            loaded_data = json.load(open(file_path, "r", encoding="utf-8"))

        assert "José" in content  # Unicode preserved
        assert loaded_data == unicode_data

    def test_write_json_complex_nested_data(self, tmp_path):
        """Test writing complex nested data structures."""
        complex_data = {
            "users": [
                {
                    "id": 1,
                    "profile": {
                        "name": "Alice",
                        "preferences": {
                            "theme": "dark",
                            "notifications": True,
                            "languages": ["en", "es", "fr"],
                        },
                    },
                    "scores": [95, 87, 92],
                }
            ],
            "metadata": {
                "version": "1.0",
                "created": "2024-01-01T00:00:00Z",
                "settings": {"debug": False, "max_users": 1000},
            },
        }

        file_path = write_json(complex_data, "complex_test", tmp_path)

        with open(file_path, "r", encoding="utf-8") as f:
            loaded_data = json.load(f)

        assert loaded_data == complex_data
        assert loaded_data["users"][0]["profile"]["name"] == "Alice"
        assert loaded_data["metadata"]["settings"]["max_users"] == 1000
