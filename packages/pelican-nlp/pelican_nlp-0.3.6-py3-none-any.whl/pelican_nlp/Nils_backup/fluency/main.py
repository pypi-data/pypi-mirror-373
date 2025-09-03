#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main script for VELAS fluency analysis pipeline.

This script orchestrates the entire analysis pipeline:
1. Validates input data
2. Processes behavioral data
3. Computes NLP metrics
4. Performs statistical analysis
5. Generates visualizations
"""
import os
import sys
from pathlib import Path
import logging
from typing import Dict, List, Any
from config import CONFIG, RESULTS_DIR
from utils import ensure_output_dir  # Add import

# Debug print CONFIG structure
print("Initial CONFIG structure:")
print("CONFIG type:", type(CONFIG))
print("CONFIG keys:", list(CONFIG.keys()))
if "questionnaires" in CONFIG:
    print("questionnaires keys:", list(CONFIG["questionnaires"].keys()))

# Get absolute path and ensure results directory exists
results_path = Path(os.getcwd()) / 'results'
results_path.mkdir(parents=True, exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(results_path / 'pipeline.log'))
    ]
)
logger = logging.getLogger(__name__)

def validate_paths(config: Dict[str, Any], required_paths: List[str]) -> bool:
    """Validate that all required paths exist."""
    logger.info(f"CONFIG keys: {list(config.keys())}")  # Debug print
    logger.info(f"Required paths: {required_paths}")  # Debug print
    
    for path_key in required_paths:
        # Split into section and path
        section, *path_parts = path_key.split('.')
        if section not in config:
            logger.error(f"Missing config section: {section}")
            return False
            
        current = config[section]
        try:
            for key in path_parts:
                current = current[key]
            
            # Handle paths with format strings
            if isinstance(current, str) and '{' in current:
                # If path contains format string, check parent directory
                path = Path(current.format(case='lower')).parent
            else:
                path = Path(current)
                
            # For input paths, check existence
            if 'input' in path_parts:
                if not path.exists():
                    logger.error(f"Input path does not exist: {path}")
                    return False
            # For output paths, create if doesn't exist
            else:
                ensure_output_dir(str(path))
                logger.info(f"Created output directory: {path}")
                
        except KeyError:
            logger.error(f"Missing required path key: {path_key}")
            return False
        except Exception as e:
            logger.error(f"Error validating path {path_key}: {str(e)}")
            return False
    return True

def log_config_section(section_name: str, config: Dict[str, Any]):
    """Log the configuration section being used."""
    logger.info(f"\nConfiguration for {section_name}:")
    for key, value in config.items():
        if isinstance(value, dict):
            logger.info(f"{key}:")
            for subkey, subvalue in value.items():
                logger.info(f"  {subkey}: {subvalue}")
        else:
            logger.info(f"{key}: {value}")

def run_questionnaires():
    """Process questionnaire data."""
    logger.info("\nProcessing questionnaire data...")
    import questionnaires_data
    questionnaires_data.main()
    return True

def run_behavioral_data():
    """Run behavioral data processing."""
    logger.info("\nRunning behavioral data processing...")
    import behavioral_data
    behavioral_data.main()
    return True

def run_check_duplicates():
    """Check for duplicates in processed data."""
    logger.info("\nChecking for duplicates...")
    import check_duplicates
    check_duplicates.main()
    return True

def run_coherence():
    """Run coherence analysis."""
    logger.info("\nRunning coherence analysis...")
    import coherence
    coherence.main()
    return True

def run_optimality():
    """Run optimality analysis."""
    logger.info("\nRunning optimality analysis...")
    import optimality_without_tsa
    optimality_without_tsa.main()
    return True

def run_aggregate_results():
    """Aggregate fluency results."""
    logger.info("\nAggregating results...")
    import aggregate_fluency_results
    aggregate_fluency_results.main()
    return True

def run_stats():
    """Run statistical analysis."""
    logger.info("\nRunning statistical analysis...")
    import stats_fluency
    stats_fluency.main()
    return True

def main():
    """Main execution pipeline."""
    logger.info("Starting VELAS fluency analysis pipeline...")
    
    # Create necessary directories
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Pipeline execution order
    pipeline_steps = [
        ("Questionnaire Data Processing", run_questionnaires),
        ("Behavioral Data Processing", run_behavioral_data),
        ("Duplicate Check", run_check_duplicates),
        ("Coherence Analysis", run_coherence),
        ("Optimality Analysis", run_optimality),
        ("Result Aggregation", run_aggregate_results),
        ("Statistical Analysis", run_stats)
    ]
    
    # Execute pipeline
    for step_name, step_func in pipeline_steps:
        logger.info(f"\n{'='*50}")
        logger.info(f"Starting {step_name}")
        logger.info(f"{'='*50}")
        
        try:
            success = step_func()
            if not success:
                logger.error(f"{step_name} failed. Stopping pipeline.")
                return
            logger.info(f"{step_name} completed successfully.")
        except Exception as e:
            logger.exception(f"Error in {step_name}: {str(e)}")
            return
    
    logger.info("\nPipeline completed successfully!")

if __name__ == "__main__":
    main() 