"""
Data processing script for dataset: example_raw_fhwa_reports_fleet_california
Generated automatically - customize the transformation logic as needed
Source file: examples/example_raw_fhwa_reports_fleet_california.xlsx
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
    df = pd.read_excel('examples/example_raw_fhwa_reports_fleet_california.xlsx',
                    usecols=["Year",
                        "Motorcycles",
                        "Automobiles",
                        "Buses",
                        "Trucks",
                    ])

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
    # Melt data from wide to long format
    df_melted = df.melt(
        id_vars=['Year'],
        value_vars=['Motorcycles', 'Automobiles', 'Buses', 'Trucks'],
        var_name='vehicle_type',
        value_name='count'
    )
    
    # Remove rows with NaN values
    df_melted = df_melted.dropna()
    
    mater_data = []
    
    for _, row in df_melted.iterrows():
        record = {
            "time": int(row['Year']),
            "value": float(row['count']),
            "scenario": "historical",
            "unit": "number of vehicles",
            "variable": "exogenous_stock",
            "dimensions_values": {
                "location": "California",
                "object": row['vehicle_type'].lower()
            }
        }
        mater_data.append(record)
    
    return mater_data


if __name__ == "__main__":
    main()
