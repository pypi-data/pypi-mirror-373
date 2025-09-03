"""
Configuration for VELAS fluency analysis pipeline.

This file contains all configuration settings for the analysis pipeline, organized by component.
Each section corresponds to a specific analysis step and contains paths, parameters, and settings
used by that component.

Manual Mounting Instructions:
----------------------------
Windows:
1. Open File Explorer
2. Right-click on 'This PC'
3. Select 'Map Network Drive'
4. Enter: \\nas01.bli.uzh.ch\studies\homan.puk.uzh\VELAS\VELAS_Master_Folder

macOS:
1. Finder > Go > Connect to Server
2. Enter: smb://nas01.bli.uzh.ch/studies/homan.puk.uzh/VELAS/VELAS_Master_Folder

Linux:
1. Create mount point: mkdir -p ~/VELAS_mount
2. Mount: sudo mount -t cifs //nas01.bli.uzh.ch/studies/homan.puk.uzh/VELAS/VELAS_Master_Folder ~/VELAS_mount
"""
from pathlib import Path
import os
import sys
import platform


def get_default_mount_point():
    """Get the default mount point based on the operating system."""
    system = platform.system().lower()
    if system == "windows":
        # Use the UNC path directly for Windows
        return Path(r"\\nas01.bli.uzh.ch\Studies\homan.puk.uzh\VELAS\VELAS_Master_Folder")
    elif system == "darwin":  # macOS
        return Path("/Volumes/VELAS_Master_Folder")
    else:  # Linux and others
        return Path.home() / "VELAS_mount"

def check_mount_point(mount_point):
    """Check if the mount point exists and is accessible."""
    if not mount_point.exists():
        print(f"ERROR: Mount point {mount_point} does not exist!")
        print("\nPlease mount the VELAS network share first.")
        print("See the instructions in the config.py file header.")
        sys.exit(1)
    return mount_point

# Server configuration
SERVER_CONFIG = {
    "server": "nas01.bli.uzh.ch",  # NAS server address
    "share": "studies",  # Share name
    "project_path": "homan.puk.uzh/VELAS/VELAS_Master_Folder",  # Project directory on server
    "mount_point": os.environ.get("VELAS_MOUNT", str(get_default_mount_point()))  # Allow override via env var
}

# Base paths for the project
BASE_DIR = check_mount_point(Path(SERVER_CONFIG["mount_point"]))  # Root directory with mount check
DATA_DIR = BASE_DIR / "Master_Files"  # Directory containing master data files

MODELS_DIR = BASE_DIR / "Sub_Projects" / "VELAS_Fluency" / "00_Nils" / "fluency-main" / "code"  # Directory containing trained models
RESULTS_DIR = BASE_DIR / "Sub_Projects" / "VELAS_Fluency" / "Results"  # Local directory for all output files

# Shared configuration settings
SHARED_CONFIG = {
    "preprocessing": {
        "lower": True,  # Whether to convert text to lowercase
        "free_text": False,  # Whether input is free text
    },
    "parallelization": {
        "parallelize": True,
        "max_workers": 16
    },
    "model": {
        "fasttext_path": str(MODELS_DIR / "cc.de.300.bin"),
        "language_code": "deu-Latn"
    }
}

# Configuration for questionnaire data processing
QUESTIONNAIRES_CONFIG = {
    "paths": {
        "input": str(DATA_DIR / "Online_Questionnaire_Data/VELAS_Questionnaire_Master.csv"),  # Control group responses
        "output": str(RESULTS_DIR / "aggregates/questionnaires.csv")  # Processed questionnaire results
    },
    "columns_to_save": ["study_id", "mss_total", "mss_pos_sum", "mss_neg_sum", "mss_dis_sum"]  # Columns to retain in output
}

# Configuration for behavioral data processing
BEHAVIORAL_CONFIG = {
    "paths": {
        "input": str(DATA_DIR / "Behavioral_Data/VELAS_Behav_Master.csv"),  # Raw behavioral data
        "output": str(RESULTS_DIR / "aggregates/behav_agg.csv")  # Processed behavioral metrics
    },
    "columns_to_save": [  # Columns to retain in output
        "study_id",
        "panss_pos_sum", "panss_neg_sum", "panss_gen_sum", "panss_total",  # PANSS scores
        "working_memory", "stroop_psychomotor", "stroop_attention", "stroop_inhibition"  # Cognitive measures
    ],
    "cognitive_variable_mapping": {  # Mapping of raw variable names to standardized names
        "stroop_time_1": "stroop_psychomotor",
        "stroop_time_2": "stroop_attention",
        "stroop_time_3": "stroop_inhibition",
        "ds_bw_total": "working_memory"
    }
}

# Configuration for duplicate checking in transcripts
DUPLICATES_CONFIG = {
    "paths": {
        "input": str(DATA_DIR / "Language_Data/NLP_Data/fluency_transcripts"),  # Raw transcript files
        "output": str(RESULTS_DIR / "fluency_transcripts_cleaned")  # Cleaned transcript files
    },
    "file_filter": "sem_flu"  # Only process files containing this string in filename
}

# Configuration for coherence analysis
COHERENCE_CONFIG = {
    "modes": ["semantic"],  # Types of coherence to analyze
    "windows": [0, 2, 8],  # Window sizes (0=whole text, 2/8=sliding windows)
    **SHARED_CONFIG["parallelization"],  # Include shared parallelization settings
    "error_messages": True,  # Whether to print error messages
    "model": SHARED_CONFIG["model"],  # Use shared model settings
    "paths": {
        "data_dir": str(RESULTS_DIR / "fluency_transcripts_cleaned"),
        "results_dir": str(RESULTS_DIR / "coherence")
    },
    "preprocessing": SHARED_CONFIG["preprocessing"]  # Use shared preprocessing settings
}

# Configuration for optimality analysis
OPTIMALITY_CONFIG = {
    "modes": [ "semantic"],
    "window_sizes": [8],  # Specific window size for optimality
    **SHARED_CONFIG["parallelization"],  # Include shared parallelization settings
    "bootstrap": 10000,
    "shuffle_modes": ["include0_includeN", "exclude0_excludeN"], #whether to include or exclude the first and last word of the window
    "model": SHARED_CONFIG["model"],  # Use shared model settings
    "paths": {
        "data_dir": str(RESULTS_DIR / "fluency_transcripts_cleaned"),
        "results_dir": str(RESULTS_DIR / "optimality")
    },
    "preprocessing": SHARED_CONFIG["preprocessing"]  # Use shared preprocessing settings
}

# Configuration for statistical analysis
STATS_CONFIG = {
    "paths": {
        "data_dir": str(RESULTS_DIR / "fluency_transcripts_cleaned"),  # Raw transcript data
        "results_dir": str(RESULTS_DIR / "stats"),  # Statistical analysis results
        "figures_dir": str(RESULTS_DIR / "figures")  # Generated figures
    },
    "demographics": ["age", "gender", "education", "first_language"],  # Demographic variables
    "outcomes": {
        "clinical": ["panss_pos_sum", "panss_neg_sum", "panss_gen_sum", "panss_total"],  # Clinical outcome measures
        "cognitive": ["working_memory", "stroop_psychomotor", "stroop_attention", "stroop_inhibition"]  # Cognitive outcome measures
    },
    "groups": {  # Mapping of group codes to labels
        "none": "0",
        "schizophrenia": "1",
        "delusional": "2", 
        "brief_psychotic": "3",
        "schizoaffective": "4",
        "other_psychotic": "5",
        "manic_psychotic": "6",
        "mdd_psychotic": "7",
        "other": "8"
    },
    "min_tokens": 8,  # Minimum number of tokens required for analysis
    "task_type": "semantic",  # Type of task to analyze
    "metrics": [  # Main metrics for analysis
        "semantic_coherence_2_mean_of_window_means",
        "semantic_coherence_8_mean_of_window_means",
        "z_Real_semantic_include0_includeN_8",
        "number_tokens"
    ],
    "new_metrics": [  # Additional metrics for analysis
        "semantic_coherence_2_mean_of_window_means",
        "semantic_coherence_8_mean_of_window_means",
        "z_Real_semantic_include0_includeN_8"
    ],
    "exclusions_bev": [  # Behavioral data columns to exclude
        "panss_pos_sum",
        "panss_neg_sum",
        "panss_gen_sum",
        "panss_total",
        "mss_total",
        "mss_pos_sum",
        "mss_neg_sum",
        "mss_dis_sum",
        "working_memory",
        "stroop_psychomotor",
        "stroop_attention",
        "stroop_inhibition"
    ],
    "alpha": 0.05,  # Significance level
    "num_tests": 4  # Number of tests for multiple comparison correction
}

# Configuration for aggregation
AGGREGATION_CONFIG = {
    "paths": {
        "behav_agg": str(RESULTS_DIR / "aggregates/behav_agg.csv"),
        "questionnaires": str(RESULTS_DIR / "aggregates/questionnaires.csv"),

        "demo_clinical": str(DATA_DIR / "Demographic_Clinical_Data/VELAS_Demo_Clin_Master.csv"),
        "output": str(RESULTS_DIR / f"master_fluency{'_lower' if SHARED_CONFIG['preprocessing']['lower'] else '_upper'}.csv")
    },
    "demo_columns": [
        'study_id', 'group', 'age', 'gender', 'first_language', 'education',
        'diagnosis', 'duration_untreated', 'age_onset', 'antipsy_duration',  
    ]
}

# Combine all configs into a single dictionary for easy access
CONFIG = {
    "questionnaires": QUESTIONNAIRES_CONFIG,
    "behavioral": BEHAVIORAL_CONFIG,
    "duplicates": DUPLICATES_CONFIG,
    "coherence": COHERENCE_CONFIG,
    "optimality": OPTIMALITY_CONFIG,
    "stats": STATS_CONFIG,
    "aggregation": AGGREGATION_CONFIG,
    "shared": SHARED_CONFIG,
    "min_tokens": STATS_CONFIG["min_tokens"],
    "task_type": STATS_CONFIG["task_type"],
    "metrics": STATS_CONFIG["metrics"],
    "new_metrics": STATS_CONFIG["new_metrics"],
    "exclusions_bev": STATS_CONFIG["exclusions_bev"]
} 