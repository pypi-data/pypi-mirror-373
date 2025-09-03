"""
Shared utilities and constants for plotting functions.
"""

# Colors for different groups
COLORS = {
    "Patients": '#242424',
    "Psychosis": '#242424',
    "HS": '#6d6d6d',
    "LS": '#b6b6b6',
    "Low Sczt": '#b6b6b6',
    "High Sczt": '#6d6d6d',
}

# Colors for different outcomes
OUTCOME_COLORS = {
    "Age": '#2b2b2b',
    "Education": '#cc78bc',
    "Male Gender": '#949494',
    "German Native":  'sienna',
    "Other Native": 'slategrey', 
    'Working Memory': '#2b2b2b',
    'Psychomotor Speed': '#cc78bc',
    'Negative Inhibition': '#949494',
    'MSS Pos':  'sienna',
    'MSS Neg': 'slategrey', 
    'PANSS Gen': '#ca9161',
    'MSS Dis': '#ca9161',
    'PANSS Pos':  'sienna',
    'PANSS Neg': 'slategrey'
}

# Ordered list of outcomes for consistent plotting
SORTED_OUTCOMES = [
    'Age',
    'Education',
    'Male Gender',
    "German Native",  
    "Other Native",
    'Working Memory',
    'Psychomotor Speed',
    'Negative Inhibition',
    'MSS Pos',
    'MSS Neg',
    'MSS Dis',
    'PANSS Pos',
    'PANSS Neg',
    'PANSS Gen',
    'Age of Disease Onset',
    'Duration of Untreated Illness',
    'Duration of Antipsychotic Treatment',
    "Risperidone Equivalent",
]

# Group dictionary for consistent naming
GROUP_DICT = {
    "ls": "Low Sczt",
    "hs": "High Sczt", 
    "control": "Healthy Controls",
    "patient": "Psychosis"
}

# Variable name mapping for plots
NAMES = {
    "const": "Constant",
    "gender_male": "Male Gender",
    "age": "Age",
    "education": "Education",
    "age_onset": "Age of Disease Onset",
    "antipsy_duration": "Duration of Antipsychotic Treatment",
    "duration_untreated": "Duration of Untreated Illness",
    "first_language_German": "German Native",  
    "first_language_Other": "Other Native",
    "total_risp_eq": "Risperidone Equivalent",
    "semantic_coherence_0_mean_of_window_means": "Average Sim",
    "semantic_coherence_2_mean_of_window_means": "Coherence 2",
    "semantic_coherence_5_mean_of_window_means": "Coherence 5",
    "semantic_coherence_8_mean_of_window_means": "Coherence 8",
    "semantic_coherence_16_mean_of_window_means": "Coherence 16",
    "semantic_coherence_32_mean_of_window_means": "Coherence 32",
    "number_tokens": "\# Items",
    "z_Real_semantic_include0_includeN_5": "Optimality 5",
    "z_Real_semantic_include0_includeN_8": "Optimality 8",
    "z_Real_semantic_include0_includeN_16": "Optimality 16",
    "z_Real_semantic_include0_includeN_32": "Optimality 32",
    "panss_p_total": "PANSS Pos",
    "panss_g_total": "PANSS Gen",
    "panss_n_total": "PANSS Neg",
    "panss_total": "PANSS Total",
    "mss_sum": "MSS",
    "mss_pos_sum": "MSS Pos",
    "mss_neg_sum": "MSS Neg",
    "mss_dis_sum": "MSS Dis",
    "tlc_mean": "TLC Mean",
    "stroop_psychomotor": "Psychomotor Speed",
    "stroop_attention": "Selective Attention",
    "stroop_inhibition": "Negative Inhibition",
    "working_memory": "Working Memory",
    'panss_sim_total': "PANSS Similarities",
    'tangentiality_mean': "Tangentiality Mean", 
    'derailment_mean': "Derailment Mean",
    "top_p": "Probability Mass Cutoff",
    "temperature": "Temperature",
    "semantic_coherence_": "Semantic Similarity Metric"
}

# Key metrics for analysis
METRICS = [
    "semantic_coherence_2_mean_of_window_means",
    "semantic_coherence_8_mean_of_window_means",
    "z_Real_semantic_include0_includeN_8",
    "number_tokens"
]

# Cognitive variables
COG_VAR = [
    'working_memory',
    'stroop_inhibition'
]

def format_p_value(p_value: float) -> str:
    """
    Format a p-value according to APA style.

    Args:
        p_value: The p-value to format.

    Returns:
        A string representing the formatted p-value.
    """
    if p_value < 0.001:
        return "p < .001"
    elif p_value < 0.01:
        return f"p = .{str(round(p_value, 3))[2:]}"
    else:
        return f"p = .{str(round(p_value, 2))[2:]}"

def set_size(width: float = 750, fraction: float = 1, subplots: tuple = (1, 1)) -> tuple:
    """
    Set figure dimensions to avoid scaling in LaTeX.

    Args:
        width: Document width in points, or string of predefined document type
        fraction: Fraction of the width which you wish the figure to occupy
        subplots: The number of rows and columns of subplots.

    Returns:
        Dimensions of figure in inches
    """
    if width == "thesis":
        width_pt = 426.79135
    elif width == "beamer":
        width_pt = 307.28987
    else:
        width_pt = width

    # Width of figure (in pts)
    fig_width_pt = width_pt * fraction
    # Convert from pt to inches
    inches_per_pt = 1 / 72.27

    # Golden ratio to set aesthetic figure height
    golden_ratio = (5**0.5 - 1) / 2

    # Figure width in inches
    fig_width_in = fig_width_pt * inches_per_pt
    # Figure height in inches
    fig_height_in = fig_width_in * golden_ratio * (subplots[0] / subplots[1])

    return (fig_width_in, fig_height_in) 