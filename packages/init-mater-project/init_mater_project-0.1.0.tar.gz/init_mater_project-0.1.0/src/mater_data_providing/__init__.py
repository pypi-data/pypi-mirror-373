"""
This module defines the functions of the package, the logging configuration and the __version__ of the package.


SPDX-License-Identifier: LGPL-3.0-or-later
"""

import logging
from importlib.metadata import version

from .definitions import metadata_definition, provider_definition
from .file_operations import write_json
from .helpers import explode_dict_to_column
from .serialization import dump_json, standardize_json, to_mater_json
from .transformations import dimension_as_dict, replace_equivalence
from .validations import (
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

# Version
__version__ = version("mater-data-providing")

# Wildcard imports
__all__ = [
    "metadata_definition",
    "provider_definition",
    "replace_equivalence",
    "dump_json",
    "dimension_as_dict",
    "validate_input_data_structure",
    "standardize_json",
    "to_mater_json",
    "validate_aspect_elements",
    "validate_dimension_file",
    "validate_dumped_json",
    "validate_input_data_full",
    "validate_metadata",
    "validate_provider",
    "validate_variable_dimension_file",
    "validate_variable_elements",
    "explode_dict_to_column",
    "write_json",
]

# Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
