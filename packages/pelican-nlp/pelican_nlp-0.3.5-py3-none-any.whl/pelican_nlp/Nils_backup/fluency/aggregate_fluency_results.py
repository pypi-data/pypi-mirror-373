#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 12:28:18 2024

@author: nilsl
"""
import os
import pandas as pd
import numpy as np
from config import CONFIG


def add_prefix_if_short(text, length, prefix):
    if len(text) < length:
        return prefix + text
    return text


def parse_array_from_string(s):
    """Parses a numpy array from a string representation."""
    cleaned = s.strip("[]")
    return np.array([float(x) for x in cleaned.split()])

def load_csvs_to_dataframe(directory, match_str, indeces):
    df_list = []
    # Loop through all files in the specified directory
    for filename in os.listdir(directory):
        # Check if the file is a CSV and contains the match_str in the filename
        if filename.endswith(".csv") and match_str in filename:
            # Construct the full path to the file
            file_path = os.path.join(directory, filename)
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file_path, index_col=0, dtype=str)
            # Remove the file extension and use the filename as the key in the dictionary
            for i, index in enumerate(indeces):
                df[f"attr_{i}"] = filename.split(".")[0].split("_")[index]
            df_list.append(df)

    return pd.concat(df_list, axis=0)


def pivot_df(df, index_cols, pivot_cols):
    # Perform the pivot operation
    df_pivot = df.pivot_table(
        index=index_cols, columns=pivot_cols, aggfunc="first"
    )

    # Flatten the MultiIndex columns by joining level names with corresponding values
    df_pivot.columns = [
        "{}_{}".format("_".join(map(str, col[:-1])), col[-1])
        for col in df_pivot.columns
    ]

    # Reset index to make index columns regular columns again
    df_pivot.reset_index(inplace=True)

    # Handling the columns after resetting index
    all_cols = df_pivot.columns.tolist()
    non_index_cols = [col for col in all_cols if col not in index_cols]

    # Sorting non-index columns by base name and context number, modified to handle multiple pivots
    sorted_cols = sorted(
        non_index_cols, key=lambda x: (x.split("_")[0], int(x.split("_")[-1]))
    )

    # Reordering DataFrame columns including index and sorted other columns
    df_pivot = df_pivot[index_cols + sorted_cols]

    return df_pivot

def main():
    """Main execution function."""
    lower = CONFIG["shared"]["preprocessing"]["lower"]
    
    behav = pd.read_csv(CONFIG["aggregation"]["paths"]["behav_agg"], dtype=str)
    behav["study_id"] = (
        behav["study_id"]
        .apply(add_prefix_if_short, length=4, prefix="0")
        .apply(add_prefix_if_short, length=4, prefix="0")
    )
    behav_scores = [col for col in behav.columns if not col in ["study_id", "group", "gender", "first_language", "diagnosis"]]
    behav[behav_scores] = behav[behav_scores].astype(float)

    demo = pd.read_csv(
        CONFIG["aggregation"]["paths"]["demo_clinical"], 
        dtype=str
    )[CONFIG["aggregation"]["demo_columns"]]

    demo_scores = [col for col in demo.columns if not col in ['study_id', 'group', 'gender', 'first_language', 'diagnosis']]
    demo[demo_scores] = demo[demo_scores].astype(float)

    behav_mss = pd.read_csv(CONFIG["aggregation"]["paths"]["questionnaires"], dtype=str)
    behav_mss[behav_mss.columns.drop("study_id")] = behav_mss[behav_mss.columns.drop("study_id")].astype(float)

    behav_mss["study_id"] = (
        behav_mss["study_id"]
        .apply(add_prefix_if_short, length=4, prefix="0")
        .apply(add_prefix_if_short, length=4, prefix="0")
    )

    fluency_optimality = (
        load_csvs_to_dataframe(
            CONFIG["optimality"]["paths"]["results_dir"],
            "lower" if lower else "upper",
            [3, 4, 5],
        )
        .rename(
            columns={
                "attr_0": "min_length",
                "attr_1": "index_0_shuffle",
                "attr_2": "index_-1_shuffle",
            }
        )
        .drop("task", axis=1)
    )

    fluency_optimality["z_Real"] = (
        fluency_optimality["actual_dist"].astype(float)
        - fluency_optimality["average_dist"].astype(float)
    ) / fluency_optimality["std_dist"].astype(float)
    fluency_optimality["z_Real"] = fluency_optimality["z_Real"].astype(float)
    fluency_optimality["all_pairs_average"] = fluency_optimality[
        "all_pairs_average"
    ].astype(float)
    fluency_optimality["actual_dist"] = fluency_optimality["actual_dist"].astype(
        float
    )
    fluency_optimality["min_length"] = fluency_optimality["min_length"].astype(
        int
    )

    fluency_optimality = (
        fluency_optimality.drop("window_index", axis = 1).groupby(
            [
                "min_length",
                "index_0_shuffle",
                "index_-1_shuffle",
                "analysis_mode",
                "study_id",
                "sub_task",
            ]
        )["z_Real"]
        .mean()
        .reset_index()
    )

    fluency_optimality_pivot = pivot_df(
        fluency_optimality,
        ["study_id", "sub_task"],
        ["analysis_mode", "index_0_shuffle", "index_-1_shuffle", "min_length"],
    )

    fluency_coherence = pd.read_csv(
        os.path.join(CONFIG["coherence"]["paths"]["results_dir"], 
                    f"coherence_results{'_lower' if lower else '_upper'}.csv"), 
        dtype=str
    )
    
    print(fluency_coherence.columns)
    print(fluency_coherence.head())
    
    fluency_coherence[fluency_coherence.columns.drop(["study_id", "sub_task"])] = fluency_coherence[fluency_coherence.columns.drop(["study_id", "sub_task"])].astype(float)


    index = demo.merge(behav).merge(behav_mss)
    metrics = fluency_coherence.merge(fluency_optimality_pivot, how = "outer")

    paper_df = index.merge(metrics)

    paper_df["task"] = ""
        
    paper_df.loc[paper_df["sub_task"] == "b", "task"] = "phonetic"
    paper_df.loc[paper_df["sub_task"] == "k", "task"] = "phonetic"
    paper_df.loc[paper_df["sub_task"] == "m", "task"] = "phonetic"
        
    paper_df.loc[paper_df["sub_task"] == "animals", "task"] = "semantic"
    paper_df.loc[paper_df["sub_task"] == "clothes", "task"] = "semantic"
    paper_df.loc[paper_df["sub_task"] == "food", "task"] = "semantic"

    paper_df.to_csv(CONFIG["aggregation"]["paths"]["output"])
    
    return True

if __name__ == "__main__":
    main()
