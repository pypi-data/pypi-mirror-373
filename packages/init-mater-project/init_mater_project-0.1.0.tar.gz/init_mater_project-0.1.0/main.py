"""
This is the main module to test features.

Copyright (C) 2025 @verzierf <francois.verzier@univ-grenoble-alpes.fr>

SPDX-License-Identifier: LGPL-3.0-or-later
"""

import pandas as pd

import mater_data_providing as mdp


def main():
    # 1. Build a DataFrame from your source (here from scratch for the example)
    input_data = pd.DataFrame(
        [
            {
                "location": "france",
                "object": "PLDV",
                "value": 15,
                "unit": "year",
                "time": 2015,
                "scenario": "historical",
                "variable": "lifetime_mean_value",
            }
        ]
    )

    # 2. Create a provider and metadata dictionnary
    provider = mdp.provider_definition("John", "Doe", "john.doe@example.com")
    metadata = mdp.metadata_definition("source_link", "source_name", "project_name")

    # 3. Dump the data into a serialized json
    return mdp.to_mater_json(input_data, provider, metadata)


if __name__ == "__main__":
    data = main()

    # 4. Write the json in the data/input_data/ directory
    mdp.write_json(data)
