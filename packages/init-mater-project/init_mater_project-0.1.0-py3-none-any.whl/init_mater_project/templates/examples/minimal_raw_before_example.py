"""
Data processing script for dataset: minimal_raw_example
Generated automatically - customize the transformation logic as needed
Source file: examples/minimal_raw_example.csv
"""

from pathlib import Path
import json

import pandas as pd

from settings import MaterConfig

# Transform to MATER format
# TIP: Use 'uv run mater-cli list-variables' to see available variables and dimensions

def main():
    """Main execution function"""
    # Load data 
    df = load_data()  # TODO: Adjust loading logic as needed
    
    # Apply transformation
    input_data = transform_to_mater_format(df) # TODO: Customize this function to match your data structure

    # Provider and metadata information (generated from config)
    provider_info = {
        "first_name": "Lauranne",
        "last_name": "Sarribouette",
        "email_address": "lauranne.sarribouette@univ-grenoble-alpes.fr"
    }
    
    metadata_info = {
        "source": "Example Dataset Source",
        "link": "https://example.org/dataset",
        "project": "Example MATER Project"
    }

    # Assemble final structure
    final_data = {
        "input_data": input_data,
        "provider": provider_info,
        "metadata": metadata_info
    }

    # Save to input_path (from config)
    config = MaterConfig()
    output_dir = Path(config.paths.input_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Use original file stem as output name
    script_name = Path(__file__).stem
    output_path = output_dir / f"{script_name}.json"

    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(final_data, file, indent=2, ensure_ascii=False)

    print(f"Transformed data saved to {output_path}")
    print(f"Generated {len(input_data)} MATER records")


def load_data():
    """Load and return data for transformation"""
    # TODO: Adjust loading logic as needed
    
    # CSV data
    df = pd.read_csv('examples/minimal_raw_example.csv', encoding='utf-8')
    print(f"Loaded {len(df)} records from CSV file")

    # Optional: specify columns if needed
    # df = pd.read_csv('examples/minimal_raw_example.csv', usecols=['col1', 'col2', 'col3'], encoding='utf-8')

    print(f"Loaded {len(df)} records from Excel file")
    return df 


def transform_to_mater_format(df):
    """
    Transform DataFrame to MATER standardized format
    
    Expected MATER format:
    {
        "time": int,
        "value": any,
        "scenario": str,
        "unit": str,
        "variable": str,
        "dimensions_values": dict
    }
    """
    # TODO: Customize this function to match your data structure
    mater_data = []
    
    for _, row in df.iterrows():
        record = {
            "time": int(row.get('year', 2000)),  # Adjust field name
            "value": row.get('value', 0),  # Adjust field name
            "scenario": "historical",  # Set appropriate scenario
            "unit": "adjust_unit_here",  # Set appropriate unit
            "variable": "exogenous_stock",  # TODO: Choose from 'uv run mater-cli list-variables'
            "dimensions_values": {
                # TODO: Choose dimensions based on your variable and data
                # Use 'uv run mater-cli list-variables' to see available dimensions
                "location": row.get('location', 'unknown'),
                "object": row.get('object_type', 'unknown')
            }
        }
        mater_data.append(record)
    
    return mater_data


if __name__ == "__main__":
    main()
