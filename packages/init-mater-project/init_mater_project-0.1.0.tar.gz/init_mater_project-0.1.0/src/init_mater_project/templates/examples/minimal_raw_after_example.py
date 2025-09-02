"""
Data processing script for dataset: minimal_raw_example
Generated automatically - customize the transformation logic as needed
Source file: examples/minimal_raw_example.csv
"""

from pathlib import Path
import json

import pandas as pd

from settings import MaterConfig

def main():
    """Main execution function"""
    # Load data 
    df = load_data() 
    
    # Apply transformation
    input_data = transform_to_mater_format(df)

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
    # CSV data
    df = pd.read_csv('examples/minimal_raw_example.csv', encoding='utf-8')
    print(f"Loaded {len(df)} records from CSV file")

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
            "time": int(row.get('time', 2000)),
            "value": int(row.get('value', 0)),
            "scenario": row.get('scenario', 'historical'),
            "unit": row.get('unit', 'number of objects'),
            "variable": row.get('variable', 'exogenous_stock'),
            "dimensions_values": {
                "location": row.get('location', 'unknown'),
                "object": row.get('object', 'unknown')
            }
        }
        mater_data.append(record)
    
    return mater_data


if __name__ == "__main__":
    main()
