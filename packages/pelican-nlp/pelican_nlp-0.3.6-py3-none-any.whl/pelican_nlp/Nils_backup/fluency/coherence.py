#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compute semantic and phonetic coherence metrics for VELAS fluency tasks.

Algorithm Overview:
------------------
The script implements two main coherence metrics:

1. Semantic Coherence:
   - Uses FastText word embeddings to convert words to 300d vectors
   - Calculates cosine similarity between word pairs
   - Analyzes in sliding windows (e.g., 2-word, 8-word)
   - For each window:
     a) Creates similarity matrix of all word pairs
     b) Computes mean and std of similarities
     c) Aggregates across windows

2. Phonetic Coherence:
   - Converts words to IPA (International Phonetic Alphabet)
   - Computes feature-based edit distance between phonetic transcriptions
   - Uses same window approach as semantic coherence
   - Normalizes distances by word length

Window Analysis:
---------------
- Window size n (e.g., n=2 or n=8)
- For each position i in text:
  1. Take words[i:i+n]
  2. Compute all pairwise similarities
  3. Calculate window statistics
  4. Move to next position
- Final metrics:
  * Mean of window means (average coherence)
  * Std of window means (coherence variability)
  * Mean of window stds (within-window variability)
  * Std of window stds (variability of within-window variability)
"""
import os
import re
import time
import logging
from typing import List, Tuple, Dict, Union, Optional, Any
from pathlib import Path
from collections import Counter
from itertools import combinations
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
import scipy
import fasttext
import fasttext.util
import epitran
import panphon
from utils import ensure_output_dir
from config import COHERENCE_CONFIG, RESULTS_DIR

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(str(RESULTS_DIR / 'coherence.log'))
    ]
)
logger = logging.getLogger(__name__)

# Type aliases
Vector = np.ndarray
Matrix = np.ndarray
TokenList = List[str]
VectorList = List[Vector]

def preprocess(
    in_text: str,
    lower: bool = COHERENCE_CONFIG["preprocessing"]["lower"],
    free_text: bool = COHERENCE_CONFIG["preprocessing"]["free_text"]
) -> TokenList:
    """
    Preprocess text by tokenizing and optionally lowercasing.
    
    Args:
        in_text: Input text to process
        lower: Whether to convert to lowercase
        free_text: If True, split on whitespace; if False, split on semicolons/commas
    
    Returns:
        List of preprocessed tokens
    """
    # Strip leading/trailing whitespace
    in_text = in_text.strip()

    if free_text:
        # Remove punctuation and split on whitespace
        in_text = re.sub(r"[^\w\s]", "", in_text)
        words = in_text.split()
    else:
        # Split structured text on delimiters
        words = re.split(";|,", in_text)

    # Process tokens
    if lower:
        processed_words = [word.lower().strip() for word in words if word.strip()]
    else:
        processed_words = [word.strip() for word in words if word.strip()]

    return processed_words

def get_vector(
    model: Any,
    mode: str,
    tokens: TokenList,
    error_messages: bool = COHERENCE_CONFIG["error_messages"]
) -> List[Union[Vector, str]]:
    """
    Get vector representations for tokens.
    
    Args:
        model: Either FastText model (semantic) or Epitran model (phonetic)
        mode: Either "semantic" or "phonetic"
        tokens: List of words to vectorize
        error_messages: Whether to print error messages
    
    Returns:
        List of vectors (semantic) or IPA transcriptions (phonetic)
    """
    if mode == "semantic":
        try:
            return [model.get_word_vector(token) for token in tokens]
        except KeyError as e:
            if error_messages:
                print(f"Vector lookup error: {e}")
            return [np.nan]
    elif mode == "phonetic":
        try:
            return [model.transliterate(token) for token in tokens]
        except KeyError as e:
            if error_messages:
                print(f"Phonetic transcription error: {e}")
            return [np.nan]
    else:
        raise ValueError(f"Unknown mode: {mode}")

def get_semantic_similarity(vec1: Vector, vec2: Vector) -> float:
    """
    Compute cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
    
    Returns:
        Cosine similarity (1 - cosine distance)
    """
    try:
        return 1 - scipy.spatial.distance.cosine(vec1, vec2)
    except ValueError:
        return np.nan

def get_phonetic_similarity(vec1: str, vec2: str, dist: Any) -> float:
    """
    Compute normalized phonetic similarity using feature edit distance.
    
    Args:
        vec1: First IPA transcription
        vec2: Second IPA transcription
        dist: Panphon distance calculator
    
    Returns:
        Normalized similarity score (1 - normalized edit distance)
    """
    try:
        return 1 - dist.feature_edit_distance(vec1, vec2) / max(len(vec1), len(vec2))
    except ValueError:
        return np.nan

def wordseq(
    tokens: TokenList,
    vectors: Union[VectorList, List[str]],
    mode: str,
    dist: Optional[Any] = None,
    word_sim: bool = False
) -> Union[float, Tuple[float, List[Union[str, float]]]]:
    """
    Calculate mean similarity between consecutive words.
    
    Args:
        tokens: List of original words
        vectors: List of vector representations
        mode: Either "semantic" or "phonetic"
        dist: Panphon distance calculator (required for phonetic mode)
        word_sim: If True, return word-by-word similarities
    
    Returns:
        If word_sim=False: Mean similarity
        If word_sim=True: Tuple of (mean_similarity, list of alternating words and similarities)
    """
    similarities = np.array([])
    
    for position, vec in enumerate(vectors):
        if position == 0:
            vec1 = vec
            continue
            
        vec2 = vec
        # Calculate similarity based on mode
        if mode == "semantic":
            similarity = get_semantic_similarity(vec1, vec2)
        elif mode == "phonetic":
            similarity = get_phonetic_similarity(vec1, vec2, dist)
        vec1 = vec2

        similarities = np.append(similarities, similarity)

    mean_sim = similarities[~np.isnan(similarities)].mean()

    if word_sim:
        word_sims = [i for sublist in list(zip(tokens, np.append(similarities, np.nan))) for i in sublist][:-1]
        return mean_sim, word_sims

    return mean_sim

def wordmatrix(
    tokens: TokenList,
    vectors: Union[VectorList, List[str]],
    mode: str,
    dist: Optional[Any] = None,
    dataframe: bool = False
) -> Union[Matrix, pd.DataFrame]:
    """
    Compute similarity matrix for all word pairs.
    
    Args:
        tokens: List of words
        vectors: List of vector representations
        mode: Either "semantic" or "phonetic"
        dist: Panphon distance calculator (required for phonetic mode)
        dataframe: If True, return pandas DataFrame; if False, return numpy array
    
    Returns:
        Similarity matrix as either numpy array or pandas DataFrame
    """
    vectors = np.array(vectors)
    if mode == "semantic":
        # Compute cosine similarity matrix
        similarity_matrix = 1 - scipy.spatial.distance.cdist(vectors, vectors, 'cosine')
        # Zero out upper triangle
        upper_triangle_indices = np.triu_indices_from(similarity_matrix)
        similarity_matrix[upper_triangle_indices] = np.nan
    elif mode == "phonetic":
        # Compute pairwise phonetic similarities
        distances = [get_phonetic_similarity(i, j, dist) for (i, j) in combinations(vectors, 2)]
        similarity_matrix = scipy.spatial.distance.squareform(distances)
        upper_triangle_indices = np.triu_indices_from(similarity_matrix)
        similarity_matrix[upper_triangle_indices] = np.nan

    if dataframe:
        return pd.DataFrame(similarity_matrix, index=tokens, columns=tokens)

    # Return lower triangle as list of lists
    return [list(row[:i+1]) for i, row in enumerate(similarity_matrix)]

def calculate_segment_avg(
    tokens: TokenList,
    vectors: Union[VectorList, List[str]],
    mode: str,
    start_idx: int,
    window_size: int,
    dist: Optional[Any] = None
) -> Tuple[float, float]:
    """
    Calculate average similarity for a segment of tokens.
    
    Args:
        tokens: List of words
        vectors: List of vector representations
        mode: Either "semantic" or "phonetic"
        start_idx: Starting index of segment
        window_size: Size of window
        dist: Panphon distance calculator (required for phonetic mode)
    
    Returns:
        Tuple of (mean_similarity, std_similarity)
    """
    segment_tokens = tokens[start_idx:start_idx + window_size]
    segment_vectors = vectors[start_idx:start_idx + window_size]
    
    # Get similarity matrix for segment
    segment_df = wordmatrix(segment_tokens, segment_vectors, mode, dist=dist, dataframe=True)
    segment_values = segment_df.stack()
    
    return segment_values.mean(), segment_values.std()

def coherence(
    tokens: TokenList,
    vectors: Union[VectorList, List[str]],
    mode: str,
    window_size: int,
    dist: Optional[Any] = None
) -> Tuple[float, float, float, float]:
    """
    Compute coherence metrics for a sequence of words.
    
    Args:
        tokens: List of words
        vectors: List of vector representations
        mode: Either "semantic" or "phonetic"
        window_size: Size of sliding window (0 for whole text)
        dist: Panphon distance calculator (required for phonetic mode)
    
    Returns:
        Tuple of (mean_of_means, std_of_means, mean_of_stds, std_of_stds)
    """
    # Handle empty or single-word sequences
    if len(tokens) < 2:
        return np.nan, np.nan, np.nan, np.nan
    
    # Handle whole-text analysis
    elif window_size == 0:
        tokens_df = wordmatrix(tokens, vectors, mode, dist=dist, dataframe=True)
        matrix_values = tokens_df.stack()
        return matrix_values.mean(), np.nan, matrix_values.std(), np.nan
    
    # Handle sliding window analysis
    else:
        window_means = []
        window_stds = []
        
        for i in range(len(tokens) - window_size + 1):
            window_tokens = tokens[i:i + window_size]
            window_vectors = vectors[i:i + window_size]
            
            # Get similarity matrix for window
            window_df = wordmatrix(window_tokens, window_vectors, mode, dist=dist, dataframe=True)
            window_values = window_df.stack()
            
            # Calculate window statistics
            window_means.append(window_values.mean())
            window_stds.append(window_values.std())
        
        # Calculate aggregate statistics
        mean_mean = np.mean(window_means)
        mean_std = np.std(window_means)
        std_mean = np.mean(window_stds)
        std_std = np.std(window_stds)
        
        return mean_mean, mean_std, std_mean, std_std

def split_coherence(
    row: pd.Series,
    window: int,
    mode: str,
    dist: Optional[Any] = None
) -> pd.Series:
    """
    Compute coherence metrics for a single row with given window size.
    
    Args:
        row: DataFrame row containing tokens and vectors
        window: Window size for coherence calculation
        mode: Either "semantic" or "phonetic"
        dist: Panphon distance calculator (required for phonetic mode)
    
    Returns:
        Series with coherence metrics for this window size
    """
    # Both modes use 'tokens' column
    tokens = row['tokens']
    vectors = row["phonetic_vectors" if mode == "phonetic" else "embeddings"]
    
    mean_mean, mean_std, std_mean, std_std = coherence(
        tokens, vectors, mode, window_size=window, dist=dist
    )
    
    return pd.Series({
        f"{mode}_coherence_{window}_mean_of_window_means": mean_mean,
        f"{mode}_coherence_{window}_std_of_window_means": mean_std,
        f"{mode}_coherence_{window}_mean_of_window_stds": std_mean,
        f"{mode}_coherence_{window}_std_of_window_stds": std_std
    })

def process_window(
    data_df: pd.DataFrame,
    window: int,
    mode: str,
    dist: Optional[Any] = None
) -> pd.DataFrame:
    """
    Process entire DataFrame for a given window size.
    
    Args:
        data_df: DataFrame containing tokens and vectors
        window: Window size for coherence calculation
        mode: Either "semantic" or "phonetic"
        dist: Panphon distance calculator (required for phonetic mode)
    
    Returns:
        DataFrame with coherence metrics for this window size
    """
    logger.info(f"Processing {mode} coherence with window size: {window}")
    return data_df.apply(lambda row: split_coherence(row, window, mode, dist), axis=1)

def apply_coherence(
    data_df: pd.DataFrame,
    windows: List[int],
    mode: str,
    dist: Optional[Any] = None,
    parallelize: bool = False
) -> pd.DataFrame:
    """
    Apply coherence calculation across multiple window sizes.
    
    Args:
        data_df: DataFrame containing tokens and embedding vectors
        windows: List of window sizes to process
        mode: Either "semantic" or "phonetic"
        dist: Panphon distance calculator (required for phonetic mode)
        parallelize: Whether to use parallel processing
    
    Returns:
        DataFrame with coherence metrics for all window sizes
    """
    if parallelize:
        with ProcessPoolExecutor() as executor:
            futures = [
                executor.submit(
                    process_window,
                    data_df.copy(),
                    window,
                    mode,
                    dist
                )
                for window in windows
            ]
            results = [future.result() for future in futures]
    else:
        results = [
            process_window(data_df.copy(), window, mode, dist)
            for window in windows #window_sizes not windows
        ]

    # Combine results into main DataFrame
    for result in results:
        for col in result.columns:
            data_df[col] = result[col]

    return data_df

def ipa_to_features(ipa_tokens: List[str]) -> List[List[float]]:
    """
    Convert IPA tokens into phonetic feature vectors.
    
    Args:
        ipa_tokens: List of IPA transcriptions
    
    Returns:
        List of feature vectors for each token
    """
    return [fasttext.word_to_vector_list(ipa) for ipa in ipa_tokens]

def load_models() -> Tuple[Any, Any, Any]:
    """Load FastText, Epitran, and Panphon models."""
    logger.info("Loading models...")
    
    # Load FastText model
    logger.info("Loading FastText model...")
    ft_model = fasttext.load_model(COHERENCE_CONFIG["model"]["fasttext_path"])
    
    # Load Epitran model
    logger.info("Loading Epitran model...")
    epi = epitran.Epitran(COHERENCE_CONFIG["model"]["language_code"])
    
    # Load Panphon distance calculator
    logger.info("Loading Panphon model...")
    dist = panphon.distance.Distance()
    
    return ft_model, epi, dist

def load_transcripts() -> pd.DataFrame:
    """Load and preprocess transcripts."""
    logger.info("Loading transcripts...")
    
    # Get list of transcript files
    transcript_files = [f for f in os.listdir(COHERENCE_CONFIG["paths"]["data_dir"]) if f.endswith('.txt')]
    logger.info(f"Found {len(transcript_files)} transcript files")
    
    # Load each transcript
    data = []


    # Load each transcript
    data = []
    for filename in transcript_files:
        filepath = os.path.join(COHERENCE_CONFIG["paths"]["data_dir"], filename)
        
        try:
            # Read file with UTF-8, ignoring errors or replacing unknown chars
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                tokens = preprocess(content)
                data.append({
                    'file_name': filename,
                    'transcript': content,
                    'tokens': tokens
                })
        except UnicodeDecodeError:
            print(f"Warning: UnicodeDecodeError in file {filename}. Trying alternative encoding...")
            
            # Try alternative encoding (ISO-8859-1 or cp1252)
            try:
                with open(filepath, 'r', encoding='ISO-8859-1') as f:
                    content = f.read()
                    tokens = preprocess(content)
                    data.append({
                        'file_name': filename,
                        'transcript': content,
                        'tokens': tokens
                    })
            except Exception as e:
                print(f"Failed to read {filename} with alternative encoding: {e}")
                continue  # Skip the file

    return pd.DataFrame(data)

def process_transcripts(
    data_df: pd.DataFrame,
    ft_model: Any,
    epi: Any,
    dist: Any,
    config: Dict
) -> pd.DataFrame:
    """
    Process transcripts to compute coherence metrics.
    
    Args:
        data_df: DataFrame with raw transcripts
        ft_model: FastText model
        epi: Epitran model
        dist: Panphon distance calculator
        config: Configuration dictionary
    
    Returns:
        DataFrame with computed metrics
    """
    logger.info("Processing transcripts...")
    
    # Tokenization
    logger.info("Tokenizing transcripts...")
    data_df["tokens"] = data_df["transcript"].apply(
        lambda x: preprocess(x, config["preprocessing"]["lower"], config["preprocessing"]["free_text"])
    )
    
    # Process each mode
    for mode in config["modes"]:
        if mode == "semantic":
            # Generate embeddings
            logger.info("Generating FastText embeddings...")
            data_df["embeddings"] = data_df["tokens"].apply(
                lambda x: get_vector(ft_model, "semantic", x)
            )
            
            # Calculate word sequence similarities
            logger.info("Computing word sequence similarities...")
            data_df["wordseq_ft"] = data_df.apply(
                lambda row: wordseq(row["tokens"], row["embeddings"], "semantic"),
                axis=1
            )
            
            # Apply coherence calculations
            logger.info("Computing coherence metrics...")
            data_df = apply_coherence(data_df, config["windows"], "semantic")
            
        elif mode == "phonetic":
            # Generate phonetic vectors
            logger.info("Generating phonetic vectors...")
            data_df["phonetic_vectors"] = data_df["tokens"].apply(
                lambda x: get_vector(epi, "phonetic", x)
            )
            
            # Calculate word sequence similarities
            data_df["wordseq_phon"] = data_df.apply(
                lambda row: wordseq(row["tokens"], row["phonetic_vectors"], "phonetic", dist),
                axis=1
            )
            
            # Apply coherence calculations
            data_df = apply_coherence(data_df, config["windows"], "phonetic", dist=dist)
    
    # Calculate additional metrics
    logger.info("Computing additional metrics...")
    data_df["number_tokens"] = data_df["tokens"].apply(len)
    data_df["multiword_count"] = data_df["tokens"].apply(
        lambda x: len([i for i in x if len(i.split()) > 1])
    )
    
    return data_df

def save_results(data_df: pd.DataFrame) -> None:
    """Save processed results to CSV."""
    # Extract study_id and sub_task from filename
    data_df["study_id"] = data_df["file_name"].apply(lambda x: x.split("_")[0])  # Get first part (0029)
    data_df["sub_task"] = data_df["file_name"].apply(lambda x: x.split("_")[-1].replace(".txt", ""))
    
    # Determine output path
    out_file = os.path.join(
        COHERENCE_CONFIG["paths"]["results_dir"],
        f'coherence_results{"_lower" if COHERENCE_CONFIG["preprocessing"]["lower"] else "_upper"}.csv'
    )
    
    # Ensure output directory exists
    ensure_output_dir(out_file)
    
    # Save results, dropping intermediate columns if they exist
    columns_to_drop = [
        col for col in [
            "transcript", "tokens",
            "embeddings", "phonetic_vectors", "file_name"
        ] if col in data_df.columns
    ]
    
    # Reorder columns to put study_id and sub_task first
    final_df = data_df.drop(columns=columns_to_drop)
    cols = ["study_id", "sub_task"] + [col for col in final_df.columns if col not in ["study_id", "sub_task"]]
    final_df = final_df[cols]
    
    final_df.to_csv(out_file, index=None)
    logger.info(f"Results saved to: {out_file}")

def main():
    """Main execution function."""
    try:
        logger.info("Starting coherence analysis...")
        
        # Load models
        ft_model, epi, dist = load_models()
        
        # Load and process transcripts
        data_df = load_transcripts()
        data_df = process_transcripts(data_df, ft_model, epi, dist, COHERENCE_CONFIG)
        
        # Save results
        save_results(data_df)
        
        logger.info("Coherence analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during execution: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()