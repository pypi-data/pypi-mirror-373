"""
This module defines the constants of the project.

SPDX-License-Identifier: LGPL-3.0-or-later
"""

import os

REQUIRED_COLUMNS = frozenset({"value", "unit", "time", "scenario", "variable"})

ASPECT_COLUMNS = frozenset(
    {
        "object",
        "object_composition",
        "object_downgrading",
        "object_Su",
        "object_efficiency",
        "location",
        "location_production",
        "process",
    }
)

DIMENSION_NAMES = frozenset({"object", "location", "process"})

DIMENSION_REQUIRED_KEYS = frozenset({"name", "value"})

DIMENSION_OPTIONAL_KEYS = frozenset({"equivalence", "parents_values"})

DIMENSION_FILE_PATH = os.path.join("data", "dimension", "dimension.json")

VARIABLE_DIMENSION_FILE_PATH = os.path.join(
    "data", "variable_dimension", "variable_dimension.json"
)

INPUT_DATA_DIR_PATH = os.path.join("data", "input_data")

VARIABLE_DIMENSION_REQUIRED_KEYS = frozenset({"variable", "dimension", "property"})

PROPERTY_VALUES = frozenset({"intensive", "extensive"})
