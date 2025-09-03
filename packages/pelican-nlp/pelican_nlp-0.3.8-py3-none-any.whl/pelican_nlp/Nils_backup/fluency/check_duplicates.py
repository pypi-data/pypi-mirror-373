#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process VELAS fluency transcripts by cleaning duplicates and hyphenated words.

This script:
1. Analyzes text files for duplicates and hyphenated words
2. Cleans transcripts by removing duplicates and hyphens
3. Saves processed transcripts to output directory
"""
import os
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple
from utils import ensure_output_dir, validate_input_data
from config import DUPLICATES_CONFIG


#implemented in fluency_cleaner==================================
def analyze_transcript(content: str) -> Tuple[int, int]:
    """
    Count duplicates and hyphenated words in a transcript.
    
    Args:
        content: Semicolon-separated transcript content
    
    Returns:
        Tuple of (duplicate_count, hyphenated_word_count)
    """
    words = content.split(';')
    word_counter = Counter(words)
    
    duplicates = sum(count - 1 for count in word_counter.values() if count > 1)
    hyphenated = sum(1 for word in words if '-' in word)
    
    return duplicates, hyphenated
#=============================================================================

def analyze_directory(directory: str) -> Dict[str, int]:
    """
    Analyze all transcripts in directory for duplicates and hyphenated words.
    
    Args:
        directory: Path to transcript directory
    
    Returns:
        Dictionary with total counts of duplicates and hyphenated words
    """
    total_duplicates = 0
    total_hyphenated = 0

    for filename in os.listdir(directory):
        if filename.endswith('.txt') and DUPLICATES_CONFIG["file_filter"] in filename:
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as file:
                content = file.read()
                duplicates, hyphenated = analyze_transcript(content)
                total_duplicates += duplicates
                total_hyphenated += hyphenated

    return {
        'duplicates': total_duplicates,
        'hyphenated': total_hyphenated
    }

#=======================================================
#implemented in fluency_cleaner
def clean_transcript(content: str) -> str:

    # Remove whitespace and decorators
    content = re.sub(r'\s+', '', content).strip()
    
    # Split and clean words
    words = [word for word in content.split(';') if word]
    words = [word.replace('-', '') for word in words]
    
    # Remove duplicate words while preserving order
    word_counter = Counter(words)
    seen = set()
    cleaned_words = []
    
    for word in words:
        if word in seen and word_counter[word] > 1:
            word_counter[word] -= 1
        else:
            cleaned_words.append(word)
            seen.add(word)
    
    return ';'.join(cleaned_words)
#===========================================================

def process_directory(input_dir: str, output_dir: str) -> None:
    """
    Process all transcripts in directory, cleaning and saving to output directory.
    
    Args:
        input_dir: Directory containing raw transcripts
        output_dir: Directory for cleaned transcripts
    """
    # Create the output directory and any necessary parent directories
    print(f"Creating output directory: {output_dir}")
    print(f"Output directory exists before ensure_output_dir? {os.path.exists(output_dir)}")
    ensure_output_dir(output_dir)
    print(f"Output directory exists after ensure_output_dir? {os.path.exists(output_dir)}")

    for filename in os.listdir(input_dir):
        if filename.endswith('.txt') and DUPLICATES_CONFIG["file_filter"] in filename:
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            
            print(f"\nProcessing file: {filename}")
            print(f"Input path: {input_path}")
            print(f"Output path: {output_path}")
            print(f"Output dir exists? {os.path.exists(os.path.dirname(output_path))}")
            
            # Ensure the directory for this specific file exists
            ensure_output_dir(os.path.dirname(output_path))
            print(f"Output dir exists after ensure? {os.path.exists(os.path.dirname(output_path))}")
            
            with open(input_path, 'r') as infile:
                content = infile.read()
                cleaned_content = clean_transcript(content)
                
            with open(output_path, 'w') as outfile:
                outfile.write(cleaned_content)

def print_analysis_results(results: Dict[str, int], stage: str) -> None:
    """Print analysis results in a formatted way."""
    print(f"\nAnalysis results ({stage}):")
    print(f"- Total duplicates: {results['duplicates']}")
    print(f"- Total hyphenated words: {results['hyphenated']}")

def main():
    # Get paths from config
    paths = DUPLICATES_CONFIG["paths"]
    
    # Validate input paths and create output directories
    input_errors = validate_input_data({"transcripts": paths["input"]})
    if input_errors:
        for desc, error in input_errors.items():
            print(f"Error with {desc}: {error}")
        return
    
    print(f"\nInput directory: {paths['input']}")
    print(f"Output directory: {paths['output']}")
    print(f"Input directory exists? {os.path.exists(paths['input'])}")
    
    ensure_output_dir(paths["output"])
    print(f"Output directory exists after ensure? {os.path.exists(paths['output'])}")
    
    # Analyze original transcripts
    print("\nAnalyzing original transcripts...")
    original_results = analyze_directory(paths["input"])
    print_analysis_results(original_results, "before cleaning")
    
    # Process transcripts
    print("\nCleaning transcripts...")
    process_directory(paths["input"], paths["output"])
    
    # Analyze cleaned transcripts
    print("\nAnalyzing cleaned transcripts...")
    cleaned_results = analyze_directory(paths["output"])
    print_analysis_results(cleaned_results, "after cleaning")
    
    print(f"\nCleaned transcripts saved to: {paths['output']}")

if __name__ == "__main__":
    main()