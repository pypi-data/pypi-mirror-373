"""
Utility functions for the VELAS fluency analysis pipeline.
"""
import os
from pathlib import Path
from typing import List, Dict

def ensure_output_dir(path: str) -> None:
    """
    Create output directory if it doesn't exist.
    
    Args:
        path: Path to create. Can be a directory path or a file path.
              If it's a file path, the directory containing the file will be created.
              If it's a directory path, the directory itself will be created.
    """
    # If path ends with a file extension, get its directory
    if '.' in os.path.basename(path):
        dir_path = os.path.dirname(os.path.abspath(path))
    else:
        dir_path = os.path.abspath(path)
    
    Path(dir_path).mkdir(parents=True, exist_ok=True)

def validate_input_data(filepaths: Dict[str, str]) -> Dict[str, str]:
    """
    Check if input files exist and return any errors.
    
    Args:
        filepaths: Dictionary mapping file descriptions to their paths
                  e.g., {"behavioral_data": "/path/to/behav.csv"}
    
    Returns:
        Dictionary of error messages for missing files.
        Empty dict if all files exist.
    """
    errors = {}
    for description, path in filepaths.items():
        if not os.path.exists(path):
            errors[description] = f"File not found: {path}"
    return errors 