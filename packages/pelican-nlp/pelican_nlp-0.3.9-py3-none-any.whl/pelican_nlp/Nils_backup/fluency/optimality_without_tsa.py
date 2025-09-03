#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimality Analysis for Verbal Fluency Tasks

This module computes optimality metrics for verbal fluency responses by analyzing:
1. Semantic distances (using FastText embeddings)
2. Phonetic distances (using Epitran/PanPhon)
3. Orthographic distances (using edit distance)

For each response sequence, it:
1. Computes distance matrices between consecutive items
2. Calculates actual path costs vs random permutations
3. Generates z-scores to measure path optimality
4. Supports different shuffling modes for baseline comparison

Key Parameters:
- bootstrap: Number of random permutations (default: 10000)
- min_len: Minimum sequence length to analyze (default: 8)
- shuffle_mode: How to handle first/last items in permutations
"""

import os
import re
from typing import Dict, List, Tuple, Any
import numpy as np
import pandas as pd
import fasttext.util
import editdistance
import panphon.distance
import scipy
import epitran
from concurrent.futures import ProcessPoolExecutor, as_completed
from config import OPTIMALITY_CONFIG
from utils import ensure_output_dir, validate_input_data

# Type aliases for clarity
DistanceMatrix = np.ndarray
EmbeddingDict = Dict[str, Dict[str, List[Any]]]

def load_data_dict(directory_path: str, lower: bool = False) -> Dict[str, List[str]]:
    """
    Load and preprocess verbal fluency responses from text files.
    
    Args:
        directory_path: Path to directory containing response files
        lower: Whether to convert text to lowercase
    
    Returns:
        Dictionary mapping task IDs to lists of responses
    """
    data_dict = {}
    
    for filename in os.listdir(directory_path):
        if not filename.endswith(".txt"):
            continue
            
        key = filename.split(".")[0]
        file_path = os.path.join(directory_path, filename)
        
        with open(file_path, "r") as file:
            content = file.read().strip()
            words = [word.strip() for word in re.split(";|,", content) if word.strip()]
            
            if lower:
                words = [word.lower() for word in words]
                
            data_dict[key] = words
            print(f"Loaded {filename}: {words}")
            
    return data_dict


def embedded_data_dict(
    data_dict: Dict[str, List[str]], 
    min_len: int,
    epi: epitran.Epitran,
    ft_model: Any
) -> EmbeddingDict:
    """
    Convert word sequences into embeddings and phonetic transcriptions.
    
    Args:
        data_dict: Dictionary of word sequences
        min_len: Minimum sequence length to process
        epi: Epitran model for phonetic transcription
        ft_model: FastText model for word embeddings
    
    Returns:
        Dictionary containing words, phonemes and embeddings for each sequence
    """
    embeddings_dict = {}

    for key, words in data_dict.items():
        if len(words) < min_len:
            continue

        embeddings_dict[key] = {
            "words": words,
            "phonemes": [epi.transliterate(word) for word in words],
            "embeddings": [ft_model.get_word_vector(word) for word in words]
        }

    return embeddings_dict


def create_semantic_distance_matrix(embedding_list: List[np.ndarray]) -> DistanceMatrix:
    """
    Create a distance matrix using cosine distances between word embeddings.
    
    Args:
        embedding_list: List of word embeddings
        
    Returns:
        Matrix of pairwise cosine distances between embeddings
    """
    distances = scipy.spatial.distance.cdist(
        np.array(embedding_list), 
        np.array(embedding_list), 
        'cosine'
    )
    np.fill_diagonal(distances, 0)
    return distances


def create_phonetic_distance_matrix(
    words: List[str], 
    distance_fun: callable, 
    norm_range: Tuple[float, float] = (0, 1)
) -> DistanceMatrix:
    """
    Create a distance matrix using phonetic or orthographic distances.
    
    Args:
        words: List of words or phonetic transcriptions
        distance_fun: Function to compute distance between two strings
        norm_range: Range to normalize distances to
        
    Returns:
        Matrix of pairwise distances between words
    """
    num_words = len(words)
    dist_matrix = np.zeros((num_words, num_words))

    for i in range(num_words):
        for j in range(i + 1, num_words):
            # Normalize by max length to get relative distance
            distance = distance_fun(words[i], words[j]) / max(len(words[i]), len(words[j]))
            dist_matrix[i, j] = distance
            dist_matrix[j, i] = distance

    return dist_matrix


def calculate_total_distance_covered(dist_matrix: DistanceMatrix, order: np.ndarray) -> float:
    """
    Calculate total distance covered by a path through items.
    
    Args:
        dist_matrix: Matrix of pairwise distances
        order: Sequence of indices defining the path
        
    Returns:
        Total distance covered by the path
    """
    distances = dist_matrix[order[:-1], order[1:]]
    return float(np.sum(distances))


def average_similarity(matrix: DistanceMatrix) -> float:
    """
    Calculate average similarity between all pairs of items.
    
    Args:
        matrix: Matrix of pairwise distances/similarities
        
    Returns:
        Average similarity across all pairs
    """
    n = matrix.shape[0]
    
    # Only count upper triangle to avoid double counting
    upper_tri = np.triu(matrix, k=1)
    total = np.sum(upper_tri)
    count = (n * (n - 1)) // 2  # Number of pairs
    
    return float(total / count) if count > 0 else 0.0


def get_shuffled_order(n: int, shuffle_mode: str, seed: int) -> np.ndarray:
    """
    Generate shuffled sequence based on specified mode.
    
    Args:
        n: Length of sequence
        shuffle_mode: How to handle first/last items:
            - include0_includeN: Shuffle all items
            - exclude0_includeN: Keep first item fixed
            - exclude0_excludeN: Keep first and last items fixed
        seed: Random seed for reproducibility
        
    Returns:
        Shuffled sequence of indices
    """
    np.random.seed(seed)
    
    if shuffle_mode == "include0_includeN":
        order = np.arange(n)
        np.random.shuffle(order)
    elif shuffle_mode == "exclude0_includeN":
        rest = np.arange(1, n)
        np.random.shuffle(rest)
        order = np.concatenate(([0], rest))
    elif shuffle_mode == "exclude0_excludeN":
        middle = np.arange(1, n-1)
        np.random.shuffle(middle)
        order = np.concatenate(([0], middle, [n-1]))
    else:
        raise ValueError(f"Invalid shuffle mode: {shuffle_mode}")
        
    return order


def analyze_optimality_transcript(
    key: str,
    embeddings: Dict[str, List[Any]],
    mode: str,
    min_len: int,
    bootstrap: int,
    phon_dist: Any,
    shuffle_mode: str
) -> List[Dict[str, Any]]:
    """
    Analyze optimality of a single transcript using bootstrap permutations.
    
    Args:
        key: Identifier for the transcript
        embeddings: Dictionary containing words, phonemes, and embeddings
        mode: Analysis mode ('semantic', 'phonetic', or 'orthographic')
        min_len: Window size for analysis
        bootstrap: Number of random permutations
        phon_dist: PanPhon distance calculator
        shuffle_mode: How to handle permutations
        
    Returns:
        List of results for each window position
    """
    answer_res = []
    answer_len = len(embeddings["words"])
    
    # Analyze each possible window position
    for i in range((answer_len - min_len) + 1):
        # Get window of items to analyze
        if mode == "semantic":
            window = embeddings["embeddings"][i:i + min_len]
            dist_matrix = create_semantic_distance_matrix(window)
        elif mode == "orthographic":
            window = embeddings["words"][i:i + min_len]
            dist_matrix = create_phonetic_distance_matrix(window, editdistance.eval)
        elif mode == "phonetic":
            window = embeddings["phonemes"][i:i + min_len]
            dist_matrix = create_phonetic_distance_matrix(window, phon_dist.feature_edit_distance)
        else:
            raise ValueError(f"Invalid mode: {mode}")

        # Calculate costs for actual sequence and permutations
        perm_costs = []
        for j in range(bootstrap):
            order = (np.arange(len(window)) if j == 0 
                    else get_shuffled_order(len(window), shuffle_mode, j))
            cost = calculate_total_distance_covered(dist_matrix, order)
            perm_costs.append(cost)
            
            if j == 0:
                all_pairs_avg = average_similarity(dist_matrix)

        # Normalize costs by number of edges
        costs_per_edge = np.array(perm_costs) / (min_len - 1)
        true_cost = costs_per_edge[0]
        
        # Store results for this window
        window_results = {
            "analysis_mode": mode,
            "study_id": key.split("_")[1],
            "task": key.split("_")[-3],
            "sub_task": key.split("_")[-1],
            "window_index": i,
            "all_pairs_average": all_pairs_avg,
            "actual_dist": true_cost,
            "average_dist": np.mean(costs_per_edge[1:]),
            "std_dist": np.std(costs_per_edge[1:])
        }
        answer_res.append(window_results)

    return answer_res


def process_key(
    key: str,
    embeddings: Dict[str, List[Any]],
    mode: str,
    min_len: int,
    bootstrap: int,
    phon_dist: Any,
    shuffle_mode: str
) -> List[Dict[str, Any]]:
    """Wrapper to process a single key with progress printing."""
    print(f"Processing {key}")
    return analyze_optimality_transcript(
        key, embeddings, mode, min_len, bootstrap, phon_dist, shuffle_mode
    )


def process_data_parallel(
    embeddings_dict: EmbeddingDict,
    modes: List[str],
    min_len: int,
    bootstrap: int,
    phon_dist: Any,
    shuffle_mode: str,
    max_workers: int = 16
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Process data in parallel using ProcessPoolExecutor.
    
    Args:
        embeddings_dict: Dictionary of embeddings to process
        modes: List of analysis modes to run
        min_len: Window size for analysis
        bootstrap: Number of permutations
        phon_dist: PanPhon distance calculator
        shuffle_mode: Permutation mode
        max_workers: Maximum number of parallel workers
        
    Returns:
        Dictionary mapping keys to analysis results
    """
    results_dict = {}
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for mode in modes:
            for key, embeddings in embeddings_dict.items():
                future = executor.submit(
                    process_key,
                    f"{mode}_{key}",
                    embeddings,
                    mode,
                    min_len,
                    bootstrap,
                    phon_dist,
                    shuffle_mode
                )
                futures[future] = (key, mode)

        for future in as_completed(futures):
            key, mode = futures[future]
            try:
                result = future.result()
                results_dict[f"{mode}_{key}"] = result
                print(f"Completed processing {mode}_{key}")
            except Exception as exc:
                print(f"{key} generated an exception: {exc}")
                
    return results_dict


def process_data_sequential(
    embeddings_dict: EmbeddingDict,
    modes: List[str],
    min_len: int,
    bootstrap: int,
    phon_dist: Any,
    shuffle_mode: str
) -> Dict[str, List[Dict[str, Any]]]:
    """Process data sequentially (for debugging/testing)."""
    results_dict = {}
    for key, embeddings in embeddings_dict.items():
        for mode in modes:
            result = analyze_optimality_transcript(
                key, embeddings, mode, min_len, bootstrap, phon_dist, shuffle_mode
            )
            results_dict[f"{key}_{mode}"] = result
    return results_dict


def save_results(results_dict: Dict[str, List[Dict[str, Any]]], output_path: str) -> None:
    """Save results to CSV file."""
    results_list = []
    for lines in results_dict.values():
        results_list.extend(lines)
    
    pd.DataFrame(results_list).to_csv(output_path)
    print(f"Results saved to {output_path}")


def main():
    """Main execution function."""
    # Validate input and output paths
    paths_to_validate = {
        "fasttext_model": OPTIMALITY_CONFIG["model"]["fasttext_path"],
        "data_directory": OPTIMALITY_CONFIG["paths"]["data_dir"]
    }
    
    # Check input paths
    path_errors = validate_input_data(paths_to_validate)
    if path_errors:
        for desc, error in path_errors.items():
            print(f"Error with {desc}: {error}")
        raise FileNotFoundError("Required files/directories not found")
        
    # Ensure results directory exists
    ensure_output_dir(OPTIMALITY_CONFIG["paths"]["results_dir"])
    
    # Initialize models
    ft_model = fasttext.load_model(OPTIMALITY_CONFIG["model"]["fasttext_path"])
    epi = epitran.Epitran(OPTIMALITY_CONFIG["model"]["language_code"])
    phon_dist = panphon.distance.Distance()
    
    # Load and preprocess data
    data_dict = load_data_dict(
        OPTIMALITY_CONFIG["paths"]["data_dir"],
        OPTIMALITY_CONFIG["preprocessing"]["lower"]
    )
    
    # Process each window size and shuffle mode
    for shuffle_mode in OPTIMALITY_CONFIG["shuffle_modes"]:
        for min_len in OPTIMALITY_CONFIG["window_sizes"]:
            print(f"\nProcessing window size {min_len} with mode {shuffle_mode}")
            
            # Prepare embeddings
            embeddings_dict = embedded_data_dict(data_dict, min_len, epi, ft_model)
            
            # Process data
            results_dict = (
                process_data_parallel(
                    embeddings_dict,
                    OPTIMALITY_CONFIG["modes"],
                    min_len,
                    OPTIMALITY_CONFIG["bootstrap"],
                    phon_dist,
                    shuffle_mode,
                    OPTIMALITY_CONFIG["max_workers"]
                ) if OPTIMALITY_CONFIG["parallelize"] else
                process_data_sequential(
                    embeddings_dict,
                    OPTIMALITY_CONFIG["modes"],
                    min_len,
                    OPTIMALITY_CONFIG["bootstrap"],
                    phon_dist,
                    shuffle_mode
                )
            )
            
            # Save results
            results_path = os.path.join(
                OPTIMALITY_CONFIG["paths"]["results_dir"],
                f"optimality_{OPTIMALITY_CONFIG['bootstrap']}_window_{min_len}_{shuffle_mode}_"
                f"{'lower' if OPTIMALITY_CONFIG['preprocessing']['lower'] else 'upper'}.csv"
            )
            save_results(results_dict, results_path)
    
    return True

if __name__ == "__main__":
    main() 