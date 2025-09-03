#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process VELAS behavioral data.

This script:
1. Loads the VELAS behavioral master data
2. Renames cognitive test variables for clarity
3. Selects relevant columns
4. Outputs cleaned CSV
"""
import pandas as pd
from utils import ensure_output_dir
from config import BEHAVIORAL_CONFIG

def load_behavioral_data(filepath):
    """Load behavioral data from CSV."""
    return pd.read_csv(filepath)

def rename_cognitive_variables(df):
    """Rename cognitive test variables for clarity."""
    return df.rename(columns=BEHAVIORAL_CONFIG["cognitive_variable_mapping"])

def save_aggregated_data(df, output_path):
    """Save relevant columns to CSV."""
    ensure_output_dir(output_path)
    df[BEHAVIORAL_CONFIG["columns_to_save"]].to_csv(output_path, index=False)

def main():
    # Get paths from config
    paths = BEHAVIORAL_CONFIG["paths"]
    
    # Process data
    df = load_behavioral_data(paths["input"])
    print(df.columns)
    df = rename_cognitive_variables(df)
    save_aggregated_data(df, paths["output"])
    
    print(f"Processed behavioral data saved to: {paths['output']}")

if __name__ == "__main__":
    main()