# -*- coding: utf-8 -*-

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind, f_oneway
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from matplotlib import cm
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import pearsonr
from scipy import stats
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from plotting_utils import (
    COLORS as colors,
    GROUP_DICT as group_dict,
    NAMES as names,
    METRICS as metrics,
    COG_VAR as cog_var,
    OUTCOME_COLORS as outcome_colors,
    SORTED_OUTCOMES as sorted_outcomes,
    format_p_value,
    set_size
)

# Get the current PATH
original_path = os.environ.get("PATH", "")

# Specify the directory where MacTeX is installed
latex_path = "/Library/TeX/texbin"

# Prepend this path to the existing PATH
os.environ["PATH"] = latex_path + ":" + original_path

def compare_groups(df, metric, group_col, task, task_col, path):
    """
    Perform regression analysis to assess group differences and obtain effect sizes.

    Parameters:
    - df: DataFrame containing the data.
    - metric: Metric to analyze.
    - group_col: Column indicating the group labels.
    - task: The specific task to filter data by.
    - task_col: Column name indicating the task in the DataFrame.
    - path: Path to save the results.
    - plot: Boolean indicating whether to plot the results.

    Returns:
    - List of significance annotations including regression coefficients and effect sizes.
    """

    sig_list = []
    sig_text = []
    sig_list_pairwise = []
    if task:
        df_task = df[df[task_col] == task]
    else:
        df_task = df

    # Prepare data
    data = df_task[["study_id", "sub_task", group_col, metric]]
    aggregations = {metric: "mean", group_col: "first"}
    mean = df_task.groupby("study_id").agg(aggregations).reset_index()
    mean["sub_task"] = "mean"
    data = pd.concat([data, mean]).reset_index(drop=True).dropna()
    data["sub_task"] = data["sub_task"].apply(lambda x: x.capitalize())
    data[group_col] = data[group_col].replace(group_dict)
    name = f"group_{metric}_{task}_{group_col}"

    plt.figure(figsize=set_size(fraction=1), dpi=300)
    sns.stripplot(
        data=data[data["sub_task"] != "mean"],
        x="sub_task",
        y=metric,
        hue=group_col,
        jitter=True,
        alpha=0.4,
        dodge=True,
        legend=None,
        size=4,
        palette=colors,
    )
    sns.pointplot(
        data=data[data["sub_task"] != "mean"],
        x="sub_task",
        y=metric,
        hue=group_col,
        capsize=0.2,
        markers="s",
        errorbar='ci',
        dodge=0.4 if group_col == "class" else 0.55,
        palette=colors,
    )

    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), title = "Group means with 95\% CI",
    ncol=4, frameon = True)

    plt.ylabel(names[metric])
    plt.xlabel("")
    plt.savefig(path + name + ".tiff")
    plt.show()

    return sig_list, sig_list_pairwise  

    
def compare_groups_single_plot_regression(df, metrics, group_col, path=None, scale_data=True, n_comp=1):
    """
    Compare groups across multiple metrics, perform regression analysis, and create a single plot with significance stars.

    Parameters:
    - df: DataFrame containing the data.
    - metrics: List of metrics to analyze.
    - group_col: Column indicating the group labels.
    - path: Optional path to save the plot.
    - scale_data: Boolean indicating whether to scale the metrics.
    - pairwise: Boolean indicating whether to perform post-hoc pairwise comparisons.

    Returns:
    - List of significance annotations and pairwise comparisons if requested.
    """
    
    # Initialize lists for storing results
    sig_list = []
    sig_list_pairwise = []

    # Scale the data if specified
    df_scaled = df.copy()
    if scale_data:
        scaler = StandardScaler()
        df_scaled[metrics] = scaler.fit_transform(df[metrics])

    # Replace group column values using group_dict (ensure group_dict is defined)
    df_scaled[group_col] = df_scaled[group_col].replace(group_dict)
    
    # Melt the DataFrame for easier plotting
    df_melted = df_scaled.melt(id_vars=[group_col], value_vars=metrics, var_name='Metric', value_name='Value')
    df_melted['Metric'] = df_melted['Metric'].replace(names)

    # Set up the plot
    plt.figure(figsize=set_size(fraction=1), dpi=300)
    
    # Create a point plot with error bars
    sns.pointplot(
        data=df_melted,
        x='Metric',
        y='Value',
        hue=group_col,
        palette=colors,
        capsize=0.2,
        markers="s",
        errorbar='ci',
        dodge=0.4 if group_col == "class" else 0.55,
    )
    
    # Add jittered dots to show the individual data points
    sns.stripplot(
        data=df_melted,
        x='Metric',
        y='Value',
        hue=group_col,
        dodge=True,
        legend=None,
        palette=colors,
        marker='o',
        edgecolor='gray',
        alpha=0.5
    )

    for metric in metrics:
        # Perform regression analysis
        formula = f"{metric} ~ C({group_col})"
        model = smf.ols(formula, data=df_scaled).fit()
        p_value = model.f_pvalue  # Get the overall p-value for the group effect
        r_squared = model.rsquared

        # Extract p-values and coefficients
        p_values = model.pvalues
        coefs = model.params

        # Group statistics: means and standard deviations
        grouped_data_stats = {}
        for g in df_scaled[group_col].unique():
            grouped_data_stats[f'{g} mean'] = df_scaled[df_scaled[group_col] == g][metric].mean()
            grouped_data_stats[f'{g} sd'] = df_scaled[df_scaled[group_col] == g][metric].std()
        
        # Store regression results
        for group in p_values.index:
            sig_list.append(
                {
                    "metric": names[metric],
                    "group": group,
                    "coef": coefs[group],
                    "p": p_values[group],
                    "r_squared": r_squared,
                    "f_stat": model.fvalue,
                    "p_model": p_value,
                    "df": f"(1, {int(model.df_resid)})"
                }| grouped_data_stats
            )
        


        if p_value < 0.05/n_comp:
            pairwise_results = pairwise_tukeyhsd(df_scaled[metric], df_scaled[group_col], alpha=0.05)
            for comparison in pairwise_results.summary().data[1:]:
                group1, group2, mean_diff, p_adj, _, _, _ = comparison
                sig_list_pairwise.append(
                    {
                        "metric": names[metric],
                        "group": f"{group1} vs {group2}",
                        "mean_diff": mean_diff,
                        "p": format_p_value(p_adj),
                    }
                )

        # Add annotation to the plot for p-value and R²
        x_pos = metrics.index(metric)
        plt.annotate(f"{format_p_value(p_value)}", xy=(x_pos, 0.82), xycoords=('data', 'axes fraction'),
                     ha='center', va='bottom', color='black')
        plt.annotate(f"R²={r_squared:.2f}", xy=(x_pos, 0.88), xycoords=('data', 'axes fraction'),
                     ha='center', va='bottom',color='black')

    # Customize the plot
    plt.ylabel('Values' if not scale_data else 'z-scores')
    plt.xlabel("")
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=3, frameon=True, title="Group means with 95\% CI")
    plt.tight_layout()

    # Save the plot if a path is provided
    if path:
        plt.savefig(f"{path}/group_comparisons.png", dpi=300)
    
    # Show the plot
    plt.show()

    return sig_list, sig_list_pairwise
    

def plot_regression_coefficients(coefficients, ci_lower, ci_upper, r2_values_df, title, path):
    # Create a DataFrame for plotting
    metrics = coefficients.index.to_list()
    outcomes = coefficients.columns.to_list()
    outcomes = sorted(outcomes, key=lambda x: sorted_outcomes.index(x))

    df_results = pd.DataFrame({
        'Metric': np.repeat(metrics, len(outcomes)),
        'Outcome': np.tile(outcomes, len(metrics)),
        'Coefficient': coefficients.values.flatten(),
        'CI Lower': ci_lower.values.flatten(),
        'CI Upper': ci_upper.values.flatten()
    })
    
    # Calculate the error (half the confidence interval width)
    df_results['Error Lower'] = (df_results['Coefficient'] - df_results['CI Lower'])
    df_results['Error Upper'] = (df_results['CI Upper'] - df_results['Coefficient'])
    
    # Set up the plot with increased figure size
    plt.figure(figsize=set_size())
    
    # Parameters for spacing
    n_metrics = len(metrics)
    n_outcomes = len(outcomes)
    
    group_spacing = len(outcomes) * 0.28  # Space between different metrics
    bar_width = 0.18  # Space between bars within the same metric

    # Calculate positions for each metric and outcome
    x_positions = []
    for i in range(n_metrics):
        base_pos = i * group_spacing
        for j in range(n_outcomes):
            x_positions.append(base_pos + j * bar_width)

    # Plot each outcome separately
    for i, outcome in enumerate(outcomes):
        subset = df_results[df_results['Outcome'] == outcome]

        # Extract positions for this outcome
        x_pos_subset = x_positions[i::n_outcomes]
        
        # Plot points with error bars
        plt.errorbar(
            x_pos_subset,
            subset['Coefficient'], 
            yerr=[subset['Error Lower'], subset['Error Upper']],
            fmt='s', 
            label=outcome, 
            color=outcome_colors[outcome],
            capsize=6,
            elinewidth=4,
            markeredgewidth=4,
            markersize=5
        )
        # Add a horizontal line at zero
    plt.axhline(y=0, color='black', linestyle='--', linewidth=1)
    # Customize plot labels and title
    plt.xlabel(f"Dependent Variable {title}", fontweight='bold')
    plt.ylabel("Standardized Coefficient", fontweight='bold')
    
    metric_ticks = [i * group_spacing + (n_outcomes - 1) * bar_width / 2 for i in range(n_metrics)]
    metric_labels = []
    for metric in metrics:
        model_r2_value = r2_values_df.loc[metric]
        metric_labels.append(f"{metric}\n" + "(${R}^2$" + f' = {model_r2_value:.3f})')
            
    plt.xticks(ticks=metric_ticks, labels=metric_labels)
    
    # Adjust legend
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.30),
               ncol=3, frameon=True, title=f"Independent Variables {title}")
    
    # Increase spacing around plot elements
    plt.tight_layout(pad=2.0)
    
    # Save the plot
    plt.savefig(f"{path}/multivar_reg_{title}.png", dpi=300)

    # Show the plot
    plt.show()
    
def scatterplot_matrix_with_corr(df, columns, hspace=0.1, wspace=0.1):
    """
    Create a 2D matrix of scatterplots for each pair of columns in the DataFrame.
    Annotate each plot with the Pearson correlation coefficient.
    """
    num_cols = len(columns)
    
    fig, axes = plt.subplots(nrows=num_cols, ncols=num_cols, figsize=(15, 15))
    fig.subplots_adjust(hspace=hspace, wspace=wspace)
    
    for i, col1 in enumerate(columns):
        for j, col2 in enumerate(columns):
            ax = axes[i, j]
            
            if i == j:
                # Diagonal: Show the histogram
                ax.hist(df[col1], bins=20, color='lightblue')
                ax.set_title("")
                ax.grid(False)
            else:
                # Scatter plot and correlation coefficient
                ax.scatter(df[col2], df[col1], alpha=0.6)
                ax.grid(False)
                # Calculate the correlation coefficient
                corr_coeff = pearsonr(df[col2], df[col1])[0]
                
                # Annotate the correlation coefficient
                ax.annotate(f'r = {corr_coeff:.2f}', xy=(0.5, 0.85), xycoords='axes fraction',
                            ha='center',  color='red', fontsize = 17)
            
            # Only show x labels on the bottom row and y labels on the left column
            if i < num_cols - 1:
                ax.set_xticklabels([])
            else:
                ax.set_xlabel(names[col2])
            
            if j > 0:
                ax.set_yticklabels([])
            else:
                ax.set_ylabel(names[col1])
    
    plt.show()
    


def calculate_residuals(df, col, control_vars):
    """
    Regress a single column on control variables and return the residuals.
    
    Parameters:
    df (pd.DataFrame): The input DataFrame.
    col (str): The column for which to calculate residuals.
    control_vars (list): The list of control variables (both numeric and categorical).
    
    Returns:
    pd.Series: The residuals for the column after regressing out the control variables.
    """
    # Identify numeric and categorical control variables
    numeric_features = df[control_vars].select_dtypes(include=[np.number]).columns.tolist()
    categorical_features = df[control_vars].select_dtypes(exclude=[np.number]).columns.tolist()

    # Preprocessing pipeline: scale numeric, one-hot encode categorical
    transformers = [('num', StandardScaler(), numeric_features)]
    if categorical_features:
        transformers.append(('cat', OneHotEncoder(drop='first', sparse=False), categorical_features))
    
    preprocessor = ColumnTransformer(transformers, remainder='passthrough')

    # Ensure the column is numeric and convert it
    df[col] = pd.to_numeric(df[col], errors='coerce')

    # Preprocess control variables
    X = preprocessor.fit_transform(df[control_vars])
    X = sm.add_constant(X)  # Add constant (intercept)

    # Regress col on control variables and get residuals
    model = sm.OLS(df[col], X).fit()

    return model.resid  # Return the residuals

def scatterplot_matrix_with_partial_corr(df, columns1, columns2, control_vars, hspace=0.1, wspace=0.1):
    """
    Create a 2D matrix of scatterplots using residuals for each pair of columns in the DataFrame, 
    while controlling for background variables (including categorical variables). 
    Annotate each plot with the partial correlation coefficient.
    
    Parameters:
    df (pd.DataFrame): The input DataFrame.
    columns (list): List of column names to plot.
    control_vars (list): List of control variables to control for (can include categorical variables).
    hspace (float): The amount of height reserved for space between subplots, expressed as a fraction of the average axis height.
    wspace (float): The amount of width reserved for space between subplots, expressed as a fraction of the average axis width.
    """
    num_cols = len(columns2)
    num_rows = len(columns1)
    
    fig, axes = plt.subplots(nrows=num_rows, ncols=num_cols, figsize=(15, 15))
    fig.subplots_adjust(hspace=hspace, wspace=wspace)
    
    residuals = {}  # Dictionary to store residuals for each column
    
    # Calculate residuals for each column
    for col in list(set(columns1 + columns2)):
        residuals[col] = calculate_residuals(df, col, control_vars)
    
    for i, col1 in enumerate(columns1):
        for j, col2 in enumerate(columns2):
            ax = axes[i, j]

            # Scatter plot of residuals and partial correlation coefficient
            ax.scatter(residuals[col2], residuals[col1], alpha=0.8, s = 10)
            
            # Calculate the partial correlation
            try:
                partial_corr, _ = pearsonr(residuals[col2], residuals[col1])
            except Exception as e:
                print(f"Error calculating partial correlation for {col1} and {col2}: {e}")
                partial_corr = np.nan
            
            # Annotate the partial correlation coefficient
            ax.annotate(f'pcorr = {partial_corr:.2f}', xy=(0.5, 0.85), xycoords='axes fraction',
                        ha='center', fontsize=17, color='red')
            ax.grid(False)
        
            # Only show x labels on the bottom row
            if i < num_rows - 1:
                ax.set_xticklabels([])
            else:
                ax.set_xlabel(f'{names[col2]}')
            
            # Only show y labels on the leftmost column
            if j > 0:
                ax.set_yticklabels([])
            else:
                ax.set_ylabel(f'{names[col1]}')
    
    plt.show()


def plot_stepwise_regression_results(df, group, path, title):
    """
    Plots the R-squared values for the base model and the full models,
    labeled by the metric added and annotated with p-values.
    """
    # Extract the relevant data
    base_r2 = df['r2_adj_control'].iloc[0]  # Assuming the base model R-squared is the same across all rows
    metrics = df['metric']
    r2_full = df['r2_adj_full']
    p_values = df['p_value']
    controls = df["control"].iloc[0]
    score = names[df["psychiatric_score"].iloc[0]]
    control_string = " + ".join([names[control] for control in controls])
    
    # Plotting
    plt.figure(figsize = set_size(), dpi = 300)  # Adjust figure size for a more compact plot

    # Plot the full models R-squared
    plt.bar(metrics, r2_full, color='deepskyblue', width=0.4, label=f'Control Model + NLP Metric $\sim$ {score}' )

    # Plot the base model R-squared
    plt.bar(metrics, [base_r2] * len(metrics), color='gray', width=0.4, label=f'{control_string} $\sim$ {score}')

    # Annotate the p-values on the full models
    for i, p_val in enumerate(p_values):
        plt.text(i, r2_full[i] + 0.02, f'p={p_val:.3f}', ha='center', color='black')

    # Add labels and title
    plt.ylabel('${R}^2$ adj.' + f' {score} {group}')

    plt.ylim(0, max(r2_full) + 0.05)  # Adjust y-axis limits

    # Get the current x-tick labels and positions
    x_ticks = plt.xticks()
    x_tick_labels = x_ticks[1]  # Extract the labels

    # Create a list of translated labels
    xticklabels = [names.get(tick.get_text(), tick.get_text()) for tick in x_tick_labels]  # Translate using the 'names' dictionary

    # Apply the translated labels back to the x-ticks
    plt.xticks(ticks=x_ticks[0], labels=xticklabels)
    # Add legend
    plt.legend(loc='upper right', frameon = True)

    # Make layout more compact
    plt.tight_layout()
    plt.savefig(f"{path}/stepwise_reg_{title}.png", dpi=300)
    # Show plot
    plt.show()

def plot_regression_with_levels(df, x_col, y_col_prefix, feature_suffix, title, path):
    """
    Plots a scatter plot with regression lines for each level of a third variable 
    that is embedded in the column names. Also plots a secondary y-axis showing 
    the relationship between the x_col and response length.
    """
    # Initialize the plot
    fig, ax1 = plt.subplots(figsize=set_size(), dpi = 300)
    
    # Extract columns that match the y_col_prefix and feature_suffix
    matching_columns = [col for col in df.columns if col.startswith(y_col_prefix) and col.endswith(feature_suffix)]
    
    # Extract the unique level values from the matching columns
    levels = [col.split('_')[2] for col in matching_columns]
    
    # Define a color palette with enough colors for each level
    palette = sns.color_palette("colorblind", len(levels))
    
    # Iterate over each level, fit a regression, and plot
    for i, col in enumerate(matching_columns):
        level = col.split('_')[2]
        
        # Filter out rows where y is NaN
        valid_data = df[[x_col, col]].dropna()
        if valid_data.empty:
            continue
        
        X = valid_data[[x_col]]
        y = valid_data[col]
        
        # Fit a linear regression model
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)
        
        # Calculate the R² value
        r2 = r2_score(y, y_pred)
        
        # Plot the data points
        ax1.scatter(X, y, color=palette[i], label=None, alpha=0.6, s = 10)
        
        # Plot the regression line
        ax1.plot(X, y_pred, color=palette[i], 
                 label=f'{names[y_col_prefix+level+"_"+feature_suffix]} (R² = {r2:.2f})', linewidth = 3)
    
    # Adding labels and title for the first y-axis
    ax1.set_xlabel(names[x_col])
    ax1.set_ylabel(f'{names[y_col_prefix]}')

    # Add legend
    ax1.legend(loc = "upper right")
    plt.savefig(f"{path}/synthetic_p_{feature_suffix}_with_length.png", dpi=300)
    
    # Show plot
    plt.show()