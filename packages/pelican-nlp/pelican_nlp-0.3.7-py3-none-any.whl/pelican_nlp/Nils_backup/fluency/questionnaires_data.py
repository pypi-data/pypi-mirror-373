#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process VELAS questionnaire data.

This script:
1. Loads questionnaire data from master file
2. Selects relevant columns
3. Outputs selected questionnaire scores
"""
import pandas as pd
from utils import ensure_output_dir
from config import QUESTIONNAIRES_CONFIG

def load_questionnaire_data(questionnaire_path: str) -> pd.DataFrame:
    """
    Load questionnaire data from master file.
    
    Args:
        questionnaire_path: Path to master questionnaire data
    
    Returns:
        DataFrame with questionnaire data
    """
    return pd.read_csv(questionnaire_path)

def save_questionnaire_data(df: pd.DataFrame, output_path: str) -> None:
    """Save processed questionnaire data to CSV."""
    ensure_output_dir(output_path)
    df[QUESTIONNAIRES_CONFIG["columns_to_save"]].to_csv(output_path, index=False)

def main():
    # Get paths from config
    paths = QUESTIONNAIRES_CONFIG["paths"]
    
    # Process data
    df = load_questionnaire_data(paths["input"])
    save_questionnaire_data(df, paths["output"])
    
    print("Questionnaire data processed successfully!")

if __name__ == "__main__":
    main()