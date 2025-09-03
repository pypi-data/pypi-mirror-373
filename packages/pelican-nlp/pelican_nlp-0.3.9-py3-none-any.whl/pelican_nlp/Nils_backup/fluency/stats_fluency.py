import numpy as np
from scipy.stats import pearsonr,  shapiro
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from statsmodels.stats.outliers_influence import variance_inflation_factor
import statsmodels.api as sm
import pandas as pd
import pickle
from plot_fluency import plot_regression_with_levels, plot_regression_coefficients, compare_groups, compare_groups_single_plot_regression,  plot_stepwise_regression_results

from plotting_utils import (
    GROUP_DICT as group_dict,
    NAMES as names,
    COG_VAR as cog_var,
    format_p_value,
    set_size
)

from config import CONFIG
import os

# Use configuration from config.py
diag_dict = CONFIG["stats"]["groups"]

# Create results directories if they don't exist
os.makedirs(CONFIG["stats"]["paths"]["results_dir"], exist_ok=True)
os.makedirs(CONFIG["stats"]["paths"]["figures_dir"], exist_ok=True)

def apply_normality_test(df):
    """
    Applies the Shapiro-Wilk normality test to each column of the DataFrame after dropping NaN values.
    Returns a DataFrame with the test statistics and p-values.
    """
    results = {'Column': [], 'Statistic': [], 'P-Value': []}
    
    for column in df.columns:
        # Ensure the column is numeric
        if pd.api.types.is_numeric_dtype(df[column]):
            # Drop NaN values
            cleaned_data = df[column].dropna()
            if len(cleaned_data) > 0:  # Ensure there is data to test
                stat, p_value = shapiro(cleaned_data)
                results['Column'].append(column)
                results['Statistic'].append(stat)
                results['P-Value'].append(p_value)
            else:
                results['Column'].append(column)
                results['Statistic'].append(None)
                results['P-Value'].append(None)
        else:
            results['Column'].append(column)
            results['Statistic'].append(None)
            results['P-Value'].append(None)
    
    return pd.DataFrame(results)


def calculate_vif(X):
    """
    Calculate the VIF for each feature in the DataFrame X.
    """
    vif_data = pd.DataFrame()
    vif_data["Variable"] = X.columns
    vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
    vif_data["Variable"] = vif_data["Variable"].apply(lambda x: names[x])
    return vif_data


def hierarchical_regression_with_vif(data, metrics, scores, control):
    results = []
    scaler = StandardScaler()

    for score in scores:
        for metric in metrics:
            # Scale the data
            X1_scaled = scaler.fit_transform(data[control])
            y_scaled = scaler.fit_transform(data[[score]])

            X1 = sm.add_constant(X1_scaled)
            model1 = sm.OLS(y_scaled, X1).fit()
            
            X2_list = ([control] if isinstance(control, str) else control) + ([metric] if isinstance(metric, str) else metric)
            X2_scaled = scaler.fit_transform(data[X2_list])

            X2 = sm.add_constant(X2_scaled)
            model2 = sm.OLS(y_scaled, X2).fit()

            # Calculate VIF for the full model
            vif = calculate_vif(pd.DataFrame(X2, columns=['const'] + X2_list))
            
            r2_adj_change = model2.rsquared_adj - model1.rsquared_adj
            r2_change = model2.rsquared - model1.rsquared
            anova_results = sm.stats.anova_lm(model1, model2)
            f_value = anova_results['F'][1]
            p_value = anova_results['Pr(>F)'][1]
            
            df1_control = len(control)  # Number of predictors for this outcome
            df2_control = len(data) - df1_control - 1  # Residual degrees of freedom
            
            df1_full = len(control) + 1  # Number of predictors for this outcome
            df2_full = len(data) - df1_full - 1  # Residual degrees of freedom

            results.append({
                'psychiatric_score': score,
                'control': control,
                'metric': metric,
                'r2_adj_control': model1.rsquared_adj,
                'r2_adj_full': model2.rsquared_adj,
                'r2_adj_change': r2_adj_change,
                'r2_control': model1.rsquared,
                'df_control': f"({df1_control}, {df2_control})",
                'df_full': f"({df1_full}, {df2_full})",
                'r2_full': model2.rsquared,
                'r2_change': r2_change,
                'f_value': f_value,
                'p_value': p_value,
                'vif': vif.set_index('Variable')['VIF'].to_dict(),  # Save VIF as a dictionary
                'model1': dict(zip(control, model1.params.flatten())),  # Convert to a dictionary
                'model2': dict(zip(X2_list, model2.params.flatten())),  # Convert to a dictionary
            })

    results_df = pd.DataFrame(results)
    return results_df

def report_stepwise_regression(df):
    """
    Generate compact APA-style formatted strings from the result of stepwise regression.

    Parameters:
    - df: DataFrame containing the stepwise regression results.

    Returns:
    - A list of formatted strings for each row of the DataFrame.
    """
    formatted_strings = {}

    for index, row in df.iterrows():
        # Extract the relevant data from the row
        metric = row['metric']
        r2_adj_control = row['r2_adj_control']  # Adjusted R² for control model
        r2_adj_full = row['r2_adj_full']  # Adjusted R² for full model
        f_value = row['f_value']  # F statistic
        p_value = row['p_value']  # p-value
        df_control = row['df_control']
        df_full = row['df_full']
        # Format the string in compact APA style
        formatted_strings[names[metric]] = (
            f"R² control {df_control} = {r2_adj_control:.3f}, R² full {df_full} = {r2_adj_full:.3f}, F = {f_value:.2f}, {format_p_value(p_value)}."
        )

    return formatted_strings


def regress_out_demographics(df, outcomes=None, demographics=None, names=None, group_filter=None):
    """
    Regress out demographic variables from each outcome separately. 
    The original outcome columns are scaled and then replaced with residuals, 
    while keeping the rest of the DataFrame intact.

    Parameters:
    - df: Original DataFrame containing the full dataset.
    - outcomes: List of outcome columns to scale and regress out demographics from. Defaults to all outcomes from config.
    - demographics: List of demographic variables. Defaults to demographics from config.
    - names: Dictionary mapping column names to display names
    - group_filter: If specified, regress out demographics within each group separately.

    Returns:
    - Tuple containing the modified DataFrame with residuals and a dictionary of regression results.
    """
    # Use defaults from config if not provided
    if outcomes is None:
        outcomes = CONFIG["stats"]["outcomes"]["clinical"] + CONFIG["stats"]["outcomes"]["cognitive"]
    if demographics is None:
        demographics = CONFIG["stats"]["demographics"]

    df_residuals = df.copy()
    
    # Initialize placeholders for results
    results = {
        'coefficients': pd.DataFrame(index=[], columns=outcomes),
        'ci_lower': pd.DataFrame(index=[], columns=outcomes),
        'ci_upper': pd.DataFrame(index=[], columns=outcomes),
        'p_values': pd.DataFrame(index=[], columns=outcomes),
        'f_statistic': pd.Series(index=outcomes, dtype=float),
        'r_squared': pd.Series(index=outcomes, dtype=float),
        'adj_r_squared': pd.Series(index=outcomes, dtype=float),
        'aic': pd.Series(index=outcomes, dtype=float),
        'bic': pd.Series(index=outcomes, dtype=float),
        'model_p_value': pd.Series(index=outcomes, dtype=float)
    }

    # Identify categorical and numeric demographics
    numeric_features = df[demographics].select_dtypes(include=[np.number]).columns.tolist()
    categorical_features = df[demographics].select_dtypes(exclude=[np.number]).columns.tolist()

    # Preprocessing pipeline: scale numeric, one-hot encode categorical
    transformers = [('num', StandardScaler(), numeric_features)]
    if categorical_features:
        transformers.append(('cat', OneHotEncoder(drop='first', sparse=False), categorical_features))

    preprocessor = ColumnTransformer(transformers, remainder='passthrough')

    # Scale the outcomes explicitly
    outcome_scaler = StandardScaler()

    if group_filter:
        # Apply group-wise regression for each subgroup
        for group in df[group_filter].unique():
            group_data = df[df[group_filter] == group]
            for outcome in outcomes:
                # Scale the outcome data before regression
                y_scaled = outcome_scaler.fit_transform(group_data[[outcome]]).flatten()
                
                X = preprocessor.fit_transform(group_data[demographics])
                X = sm.add_constant(X)  # Add constant (intercept)

                # Extract feature names from the ColumnTransformer
                feature_names = ['const'] + numeric_features + list(preprocessor.named_transformers_['cat'].get_feature_names_out(categorical_features))

                # Fit demographic model and calculate residuals for this outcome
                model = sm.OLS(y_scaled, X).fit()
                df_residuals.loc[group_data.index, outcome] = model.resid

                # Store coefficients, confidence intervals, p-values
                for i, name in enumerate(feature_names):
                    if name != 'const':  # Ignore the constant for demographics results
                        results['coefficients'].loc[name, outcome] = model.params[i]
                        results['ci_lower'].loc[name, outcome] = model.conf_int()[i, 0]
                        results['ci_upper'].loc[name, outcome] = model.conf_int()[i, 1]
                        results['p_values'].loc[name, outcome] = model.pvalues[i]

                # Store model metrics
                results['f_statistic'].loc[outcome] = model.fvalue
                results['r_squared'].loc[outcome] = model.rsquared
                results['adj_r_squared'].loc[outcome] = model.rsquared_adj
                results['aic'].loc[outcome] = model.aic
                results['bic'].loc[outcome] = model.bic
                results['model_p_value'].loc[outcome] = model.f_pvalue

    else:
        # Global regression (apply regression for each outcome separately)
        for outcome in outcomes:
            # Scale the outcome data before regression
            y_scaled = outcome_scaler.fit_transform(df[[outcome]]).flatten()
            X = preprocessor.fit_transform(df[demographics])
            X = sm.add_constant(X)  # Add constant (intercept)

            # Extract feature names from the ColumnTransformer
            feature_names = ['const'] + numeric_features + list(preprocessor.named_transformers_['cat'].get_feature_names_out(categorical_features))

            # Fit demographic model and calculate residuals for this outcome
            model = sm.OLS(y_scaled, X).fit()
            df_residuals[outcome] = model.resid

            # Store coefficients, confidence intervals, p-values
            for i, name in enumerate(feature_names):
                if name != 'const':  # Ignore the constant for demographics results
                    results['coefficients'].loc[name, outcome] = model.params[i]
                    results['ci_lower'].loc[name, outcome] = model.conf_int()[i, 0]
                    results['ci_upper'].loc[name, outcome] = model.conf_int()[i, 1]
                    results['p_values'].loc[name, outcome] = model.pvalues[i]

            # Store model metrics
            results['f_statistic'].loc[outcome] = model.fvalue
            results['r_squared'].loc[outcome] = model.rsquared
            results['adj_r_squared'].loc[outcome] = model.rsquared_adj
            results['aic'].loc[outcome] = model.aic
            results['bic'].loc[outcome] = model.bic
            results['model_p_value'].loc[outcome] = model.f_pvalue
    
    if names:
        for result_df in [results['coefficients'], results['ci_lower'], results['ci_upper'], results['p_values']]:
            result_df.rename(columns=names, index=names, inplace=True)
        for results_series in [results['f_statistic'], results['r_squared'], results['adj_r_squared'], results['aic'], results['bic'], results['model_p_value']]:
            results_series.rename(index=names, inplace=True)
        
    # Return the modified DataFrame with residuals and regression results
    return df_residuals, results

def process_regression_on_residuals(df, outcome_cols, predictors, names, group_filter=None):
    """
    Perform regression on residuals (which are now in the original outcome columns), rename columns and index, 
    and format p-values, optionally filtering by group.

    Parameters:
    - df: DataFrame containing residuals in the original outcome columns.
    - outcome_cols: List of original outcome columns (now containing residuals).
    - predictors: List of predictor variables.
    - names: Dictionary of names for renaming columns and index.
    - prefix: Optional string prefix to add to formatted column names and dictionary keys.
    - group_filter: If specified, filter the DataFrame by this group before running the regression.

    Returns:
    - Dictionary containing coefficients, confidence intervals (lower and upper), p-values, formatted results, and other metrics.
    """
    
    # Apply the group filter if provided
    if group_filter:
        if 'group' in df.columns:
            df = df[df['group'] == group_filter]
        else:
            raise ValueError(f"The 'group' column does not exist in the DataFrame. Check your group filter.")

    # Perform the multivariable regression on the residuals
    coeff, coeff_lower, coeff_upper, p_values, f_stat, r_squared, adj_r_squared, aic, bic, model_p_value = multivariable_regression_with_residuals(
        df[outcome_cols], df, predictors
    )

    # Apply renaming for coefficients, confidence intervals, and p-values
    for result_df in [coeff, coeff_lower, coeff_upper, p_values]:
        result_df.rename(columns=names, index=names, inplace=True)
    for results_series in [f_stat, r_squared, adj_r_squared, aic, bic, model_p_value]:
        results_series.rename(index=names, inplace=True)

    # Create the result dictionary with dynamic keys
    result_dict = {
        "coefficients": coeff,
        "ci_lower": coeff_lower,
        "ci_upper": coeff_upper,
        "p_values": p_values,
        "f_statistic": f_stat,
        "r_squared": r_squared,
        "adj_r_squared": adj_r_squared,
        "aic": aic,
        "bic": bic,
        "model_p_value": model_p_value
    }

    return result_dict

def multivariable_regression_with_residuals(residuals, df, predictors):
    """
    Perform multivariable regression using residuals as outcomes.
    Handles scaling of numeric predictors.

    Parameters:
    - residuals: DataFrame of residuals from regressing out demographics.
    - df: The original DataFrame containing all data, including predictors.
    - predictors: List of numeric predictors for the multivariable regression.

    Returns:
    - DataFrames of coefficients, confidence intervals, p-values, F-statistics, R-squared, Adjusted R-squared, and overall p-values.
    - Dictionary containing the preprocessed predictor matrix (X_preprocessed) for each outcome.
    """
    results = {
        'coefficients': pd.DataFrame(index=predictors, columns=residuals.columns),
        'ci_lower': pd.DataFrame(index=predictors, columns=residuals.columns),
        'ci_upper': pd.DataFrame(index=predictors, columns=residuals.columns),
        'p_values': pd.DataFrame(index=predictors, columns=residuals.columns),
        'f_statistic': pd.Series(index=residuals.columns),
        'r_squared': pd.Series(index=residuals.columns),
        'adj_r_squared': pd.Series(index=residuals.columns),
        'aic': pd.Series(index=residuals.columns),
        'bic': pd.Series(index=residuals.columns),
        'model_p_value': pd.Series(index=residuals.columns)  # New addition for overall p-values
    }
    
    for outcome in residuals.columns:
        # Combine residuals and predictors to ensure they are aligned
        combined = pd.concat([residuals[outcome], df[predictors]], axis=1).dropna()

        # Check if combined data has sufficient rows
        if combined.shape[0] < len(predictors) + 1:
            print(f"Warning: Not enough data points to perform regression for outcome {outcome}. Skipping...")
            continue

        # Separate the aligned residuals and predictors
        y = combined[outcome]
        X = combined[predictors]

        # Scale the numeric predictors
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Add a constant (intercept) term
        X_scaled = sm.add_constant(X_scaled)

        # Fit the regression model
        model = sm.OLS(y, X_scaled).fit()

        # Map the model's parameter names (e.g., x1, x2) back to the original predictor names
        params = model.params
        conf_int = model.conf_int()
        pvalues = model.pvalues
        # Store coefficients, confidence intervals, and p-values (excluding the constant term)
        for i, predictor in enumerate(predictors):
            results['coefficients'].loc[predictor, outcome] = params[i+1]  # Skip constant
            results['ci_lower'].loc[predictor, outcome] = conf_int.iloc[i+1, 0]
            results['ci_upper'].loc[predictor, outcome] = conf_int.iloc[i+1, 1]
            results['p_values'].loc[predictor, outcome] = pvalues[i+1]  # Skip constant

        # Store model metrics
        results['f_statistic'].loc[outcome] = model.fvalue
        results['r_squared'].loc[outcome] = model.rsquared
        results['adj_r_squared'].loc[outcome] = model.rsquared_adj
        results['aic'].loc[outcome] = model.aic
        results['bic'].loc[outcome] = model.bic

        # Calculate the degrees of freedom
        df_model = len(predictors)  # Number of predictors
        df_resid = model.df_resid  # Residual degrees of freedom

        # Calculate the overall p-value using the F-distribution
        overall_p_value = model.f_pvalue
        results['model_p_value'].loc[outcome] = overall_p_value
    
    return (results['coefficients'].T, 
            results['ci_lower'].T, 
            results['ci_upper'].T, 
            results['p_values'].T, 
            results['f_statistic'], 
            results['r_squared'], 
            results['adj_r_squared'],
            results['aic'], 
            results['bic'],
            results['model_p_value'])  
    
def format_regression_results_apa(results_dict, n):
    """
    Format regression results into an APA-style dictionary for multiple outcome measures.

    Parameters:
    - results_dict: Dictionary containing regression results, including coefficients, confidence intervals, F-statistic, R-squared, overall p-value, etc.
    - n: The number of observations (sample size) used in the regression.

    Returns:
    - A dictionary with outcome names as keys, where each key contains another dictionary with the model summary 
      and APA-formatted strings for each variable for that outcome.
    """
    
    # Create a dictionary to store the output for multiple outcomes
    final_result_dict = {}

    # Iterate over each outcome in the result dictionary
    for outcome in results_dict["f_statistic"].index:
        
        # Extract necessary metrics for the current outcome
        coefficients = results_dict["coefficients"].loc[outcome]
        ci_lower = results_dict["ci_lower"].loc[outcome]
        ci_upper = results_dict["ci_upper"].loc[outcome]
        f_stat = results_dict["f_statistic"].loc[outcome]  # F-statistic for the current outcome
        r_squared = results_dict["r_squared"].loc[outcome]  # R-squared for the current outcome
        adj_r_squared = results_dict["adj_r_squared"].loc[outcome]  # Adjusted R-squared for the current outcome
        p_values = results_dict["p_values"].loc[outcome]
        overall_p_value = results_dict["model_p_value"].loc[outcome]  # Overall p-value for the current outcome
        # Assuming df1 is the number of predictors and df2 is the number of observations minus predictors minus 1
        df1 = len(coefficients)  # Number of predictors for this outcome
        df2 = n - df1 - 1  # Residual degrees of freedom

        # Overall regression stats (APA formatted)
        summary = (
            f"R² = {r_squared:.2f}, F({df1}, {df2}) = {f_stat:.2f}, {format_p_value(overall_p_value)}"
        )

        # Create a dictionary for the current outcome to store the summary and coefficient details
        outcome_result_dict = {"summary": summary}

        for predictor in results_dict["coefficients"].columns:
            coeff = results_dict["coefficients"].loc[outcome,predictor]  # Extract scalar values
            ci_l = results_dict["ci_lower"].loc[outcome, predictor]  # Extract scalar values
            ci_u = results_dict["ci_upper"].loc[outcome, predictor]  # Extract scalar values
            p_val = results_dict["p_values"].loc[outcome, predictor]  # Extract scalar values

            # APA style for variable coefficients with confidence intervals
            outcome_result_dict[predictor] = (
                f"β = {coeff:.2f}, 95% CI [{ci_l:.2f}, {ci_u:.2f}], {format_p_value(p_val)}"
            )

        # Store the result for this outcome in the final dictionary
        final_result_dict[outcome] = outcome_result_dict

    return final_result_dict


def correlation_apa(df, columns, names):
    """
    Compute correlations between the specified columns in a DataFrame and return results in APA style,
    while renaming the index and columns using the `names` dictionary.

    Parameters:
    - df: pandas DataFrame containing the data.
    - columns: List of column names to compute correlations for.
    - names: Dictionary for renaming the index and columns.

    Returns:
    - A pandas DataFrame with APA-formatted correlation results.
    """
    
    # Prepare an empty DataFrame to store results
    apa_corr = pd.DataFrame(index=columns, columns=columns)

    # Compute correlations for each pair of columns
    for i, col1 in enumerate(columns):
        for j, col2 in enumerate(columns): 
            # Compute Pearson correlation
            r, p_value = pearsonr(df[col1], df[col2])
            
            # Degrees of freedom
            n = df[[col1, col2]].dropna().shape[0]  # Exclude missing data
            df_corr = n - 2
            
            # Format in APA style: r(df) = r_value, p = p_value
            apa_corr.loc[col1, col2] = f"r ({df_corr}) = {r:.2f}, {format_p_value(p_value)}"

    # Apply the renaming using the `names` dictionary
    apa_corr.rename(index=names, columns=names, inplace=True)

    return apa_corr

def report_categorical_regression(df):
    """
    Generate compact APA-style formatted strings from a categorical univariable regression table.

    Parameters:
    - df: DataFrame containing the regression results.

    Returns:
    - A list of compact formatted strings for each metric.
    """
    formatted_strings = {}

    for metric in df['metric'].unique():
        # Filter rows for the current metric
        metric_df = df[df['metric'] == metric]

        # Extract intercept information
        intercept_row = metric_df[metric_df['group'] == 'Intercept'].iloc[0]
        intercept = intercept_row['coef']
        r_squared = intercept_row['r_squared']
        model_p = format_p_value(intercept_row['p_model'])
        dof = intercept_row['df']
        f_stat = intercept_row['f_stat']
        # Start constructing the compact APA-style string
        formatted_string = f"R² = {r_squared:.2f}, F {dof} = {f_stat:.2f} {model_p}; Intercept = {intercept:.2f}, "

        # Loop through each group comparison (excluding the intercept)
        group_strings = []
        for _, row in metric_df[metric_df['group'] != 'Intercept'].iterrows():
            group = row['group'].split('[')[-1].strip(']')[2:]
            coef = row['coef']
            p_value = row['p']
            group_strings.append(f"{group} = {coef:.2f}, {format_p_value(p_value)}")

        # Combine group results and add the R² value
        formatted_string += "; ".join(group_strings)

        # Append the formatted string to the list
        formatted_strings[metric] = formatted_string

    return formatted_strings

def categorize_first_language(lang):
    """Categorize first language into 'German', 'Both', or 'Other'."""
    if lang.lower() == 'german':
        return 'German'
    elif lang.lower() == 'both':
        return 'German'
    else:
        return 'Other'

def format_combined_table(summary_patients, summary_controls):
    # Prepare shared variables in combined table
    combined_df = summary_patients[['group', 'n']].copy()
    combined_df['Age, mean (SD)'] = summary_patients.apply(lambda x: f"{x['age_mean']:.2f} ({x['age_sd']:.2f})", axis=1)
    combined_df['Gender, Male'] = summary_patients.apply(lambda x: f"{x['gender_male']} ({x['gender_male_pct']:.2f}%)", axis=1)
    combined_df['Gender, Female'] = summary_patients.apply(lambda x: f"{x['gender_female']} ({x['gender_female_pct']:.2f}%)", axis=1)
    combined_df['Education Years, mean (SD)'] = summary_patients.apply(lambda x: f"{x['education_mean']:.2f} ({x['education_sd']:.2f})", axis=1)


    # Add first language counts and percentages
    combined_df['1st Language: German'] = summary_patients.apply(lambda x: f"{x['first_lang_german']} ({x['first_lang_german_pct']:.2f}%)", axis=1)
    combined_df['1st Language: Bilingual'] = summary_patients.apply(lambda x: f"{x['first_lang_both']} ({x['first_lang_both_pct']:.2f}%)", axis=1)
    combined_df['1st Language: Other'] = summary_patients.apply(lambda x: f"{x['first_lang_other']} ({x['first_lang_other_pct']:.2f}%)", axis=1)
    
    # Add PANSS for patients and MSS for controls
    combined_df['PANSS, mean (SD)'] = summary_patients.apply(lambda x: f"{x['panss_total_mean']:.2f} ({x['panss_total_sd']:.2f})", axis=1)
    combined_df['MSS, mean (SD)'] = summary_patients.apply(lambda x: f"{x['mss_total_mean']:.2f} ({x['mss_total_sd']:.2f})", axis=1)

    # Add controls to the combined table
    combined_df_controls = summary_controls[['group', 'n']].copy()
    
    combined_df_controls['Age, mean (SD)'] = summary_controls.apply(lambda x: f"{x['age_mean']:.2f} ({x['age_sd']:.2f})", axis=1)
    combined_df_controls['Gender, Male'] = summary_controls.apply(lambda x: f"{x['gender_male']} ({x['gender_male_pct']:.2f}%)", axis=1)
    combined_df_controls['Gender, Female'] = summary_controls.apply(lambda x: f"{x['gender_female']} ({x['gender_female_pct']:.2f}%)", axis=1)
    
    combined_df_controls['Education Years, mean (SD)'] = summary_controls.apply(lambda x: f"{x['education_mean']:.2f} ({x['education_sd']:.2f})", axis=1)
    
    combined_df_controls['1st Language: German'] = summary_controls.apply(lambda x: f"{x['first_lang_german']} ({x['first_lang_german_pct']:.2f}%)", axis=1)
    combined_df_controls['1st Language: Bilingual'] = summary_controls.apply(lambda x: f"{x['first_lang_both']} ({x['first_lang_both_pct']:.2f}%)", axis=1)
    combined_df_controls['1st Language: Other'] = summary_controls.apply(lambda x: f"{x['first_lang_other']} ({x['first_lang_other_pct']:.2f}%)", axis=1)
    
    # Add PANSS for patients and MSS for controls
    combined_df_controls['PANSS, mean (SD)'] = summary_controls.apply(lambda x: f"{x['panss_total_mean']:.2f} ({x['panss_total_sd']:.2f})", axis=1)
    combined_df_controls['MSS, mean (SD)'] = summary_controls.apply(lambda x: f"{x['mss_total_mean']:.2f} ({x['mss_total_sd']:.2f})", axis=1)

    
    combined_table = pd.concat([combined_df, combined_df_controls], ignore_index=True)
    
    return combined_table


def format_breakout_table(df_patients):
    breakout_df = df_patients[['group']].copy()
    
    
    breakout_df['Duration Untreated, mean (SD)'] = df_patients.apply(lambda x: f"{x['duration_untreated_mean']:.2f} ({x['duration_untreated_sd']:.2f})", axis=1)
    breakout_df['Age of Onset, mean (SD)'] = df_patients.apply(lambda x: f"{x['age_onset_mean']:.2f} ({x['age_onset_sd']:.2f})", axis=1)
    breakout_df['Antipsychotic Treatment (weeks), mean (SD)'] = df_patients.apply(lambda x: f"{x['antipsy_duration_mean']:.2f} ({x['antipsy_duration_sd']:.2f})", axis=1)
    breakout_df["**Diagnosis:**"] = ""  
    # Add diagnosis percentages
    diagnosis_cols = ['Schizophrenia', 'Brief psychotic disorder', 'Schizoaffective disorders', 'MDD with psychotic symptoms',  'other']
    for col in diagnosis_cols:
        if col in df_patients.columns:
            breakout_df[col] = df_patients[col].apply(lambda x: '-' if x == 0 else f"{x:.1f}%" if isinstance(x, (int, float)) else x)
    
    return breakout_df

def summary_table(df):
    # Categorize the first language column
    df['first_language_category'] = df['first_language'].apply(categorize_first_language)
    
    # Convert numeric columns to float
    numeric_cols = ['age', 'education', 'duration_untreated', 'age_onset', 'antipsy_duration', 'panss_total', 'mss_total']
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    
    # Data preparation
    df_patients = df[df["group"] == "patient"].groupby("study_id")[[
            "group",
            "age",
            "gender",
            "education",
            "first_language_category",
            "diagnosis",
            'duration_untreated',
            'age_onset',
            'antipsy_duration', 
            "panss_total",
            "mss_total"
            ]].first().reset_index().drop("study_id", axis=1)
    
    df_controls = df[df["group"] != "patient"].groupby("study_id")[[
            "group",
            "age",
            "gender",
            "education",
            "first_language_category",
            "panss_total",
            "mss_total"
            ]].first().reset_index().drop("study_id", axis=1)

    df_patients["diagnosis"] = df_patients["diagnosis"].replace(diag_dict)
    
    # Calculate summary statistics for groups including n
    summary_patients = df_patients.groupby('group').agg(
        n=('age', 'size'),
        age_mean=('age', 'mean'),
        age_sd=('age', 'std'),
        
        gender_male=('gender', lambda x: (x == 'male').sum()),
        gender_female=('gender', lambda x: (x == 'female').sum()),
        
        education_mean=('education', 'mean'),
        education_sd=('education', 'std'),
        
        duration_untreated_mean=('duration_untreated', 'mean'),
        duration_untreated_sd=('duration_untreated', 'std'),
        
        age_onset_mean=('age_onset', 'mean'),
        age_onset_sd=('age_onset', 'std'),
        
        antipsy_duration_mean=('antipsy_duration', 'mean'),
        antipsy_duration_sd=('antipsy_duration', 'std'),
        
        panss_total_mean=('panss_total', 'mean'),
        panss_total_sd=('panss_total', 'std'),
        
        mss_total_mean=('mss_total', 'mean'),
        mss_total_sd=('mss_total', 'std'),

        first_lang_german=('first_language_category', lambda x: (x == 'German').sum()),
        first_lang_both=('first_language_category', lambda x: (x == 'Both').sum()),
        first_lang_other=('first_language_category', lambda x: (x == 'Other').sum()),
    ).reset_index()
    
    summary_controls = df_controls.groupby('group').agg(
        n=('age', 'size'),
        age_mean=('age', 'mean'),
        age_sd=('age', 'std'),
        
        gender_male=('gender', lambda x: (x == 'male').sum()),
        gender_female=('gender', lambda x: (x == 'female').sum()),
        
        education_mean=('education', 'mean'),
        education_sd=('education', 'std'),
        
        panss_total_mean=('panss_total', 'mean'),
        panss_total_sd=('panss_total', 'std'),
        
        mss_total_mean=('mss_total', 'mean'),
        mss_total_sd=('mss_total', 'std'),

        first_lang_german=('first_language_category', lambda x: (x == 'German').sum()),
        first_lang_both=('first_language_category', lambda x: (x == 'Both').sum()),
        first_lang_other=('first_language_category', lambda x: (x == 'Other').sum()),
    ).reset_index()
    
    # Calculate percentages for gender
    summary_patients['gender_male_pct'] = summary_patients['gender_male'] / summary_patients['n'] * 100
    summary_patients['gender_female_pct'] = summary_patients['gender_female'] / summary_patients['n'] * 100

    summary_controls['gender_male_pct'] = summary_controls['gender_male'] / summary_controls['n'] * 100
    summary_controls['gender_female_pct'] = summary_controls['gender_female'] / summary_controls['n'] * 100

    # Calculate percentages for first language
    summary_patients['first_lang_german_pct'] = summary_patients['first_lang_german'] / summary_patients['n'] * 100
    summary_patients['first_lang_both_pct'] = summary_patients['first_lang_both'] / summary_patients['n'] * 100
    summary_patients['first_lang_other_pct'] = summary_patients['first_lang_other'] / summary_patients['n'] * 100

    summary_controls['first_lang_german_pct'] = summary_controls['first_lang_german'] / summary_controls['n'] * 100
    summary_controls['first_lang_both_pct'] = summary_controls['first_lang_both'] / summary_controls['n'] * 100
    summary_controls['first_lang_other_pct'] = summary_controls['first_lang_other'] / summary_controls['n'] * 100
    
    # Aggregate diagnosis counts
    diagnosis_counts = df_patients.groupby(['group', 'diagnosis']).size().unstack(fill_value=0)
    diagnosis_percent = diagnosis_counts.apply(lambda x: np.round(x * 100 / x.sum(), 2), axis=1)  # Normalize counts
    diagnosis_counts.columns = [f'{col}' for col in diagnosis_counts.columns]
    diagnosis_counts.reset_index(inplace=True)
    diagnosis_percent.columns = [f'{col}_p' for col in diagnosis_percent.columns]
    diagnosis_percent.reset_index(inplace=True)

    # Merge diagnosis counts with summary
    summary_patients = summary_patients.merge(diagnosis_counts, on='group', how='left').rename(columns=diag_dict).merge(diagnosis_percent, on='group', how='left').rename(columns=diag_dict)

    # Create combined and breakout tables
    combined_table = format_combined_table(summary_patients, summary_controls)
    breakout_table = format_breakout_table(summary_patients)
    
    combined_table['group'] = combined_table['group'].replace(group_dict)
    breakout_table['group'] = breakout_table['group'].replace(group_dict)

    combined_table.rename({"group": "Group"}, axis=1, inplace=True)
    breakout_table.rename({"group": "Group"}, axis=1, inplace=True)

    return combined_table, breakout_table

def main():
    """Main execution function."""
    multivariate = True
    lower = CONFIG["shared"]["preprocessing"]["lower"]
    case = "lower" if lower else "upper"
    
    df_raw = pd.read_csv(
            CONFIG["aggregation"]["paths"]["output"],
            index_col=0,
            dtype=str,
        )
    
    df_raw["z_Real_semantic_include0_includeN_8"] = - df_raw["z_Real_semantic_include0_includeN_8"].astype(float)

    df_filtered = df_raw[df_raw["number_tokens"].astype(float) >= CONFIG["min_tokens"]]
    df_filtered = df_filtered[df_filtered["task"] == CONFIG["task_type"]]
    exclusions_bev = CONFIG["exclusions_bev"]
    demographics = CONFIG["stats"]["demographics"]
    
    metrics = CONFIG["metrics"]
    new_metrics = CONFIG["new_metrics"]
    
    bev_cols_quant = CONFIG["stats"]["outcomes"]["clinical"] + CONFIG["stats"]["outcomes"]["cognitive"]
    
    # Convert numeric columns to float
    df_filtered[metrics] = df_filtered[metrics].astype(float)
    df_filtered[bev_cols_quant] = df_filtered[bev_cols_quant].astype(float)
    numeric_demographics = ['age', 'education']
    df_filtered[numeric_demographics] = df_filtered[numeric_demographics].astype(float)

    # Get unique columns for aggregation, ensuring we include demographics and group
    all_cols = list(set(metrics + bev_cols_quant + exclusions_bev + demographics + ['group']))
    
    # Create aggregation dictionary ensuring no duplicates
    agg_dict = {}
    for col in all_cols:
        if col in metrics:
            agg_dict[col] = 'mean'
        else:
            agg_dict[col] = 'first'
    
    # Perform groupby aggregation
    task_means = df_filtered.drop("sub_task", axis=1).groupby("study_id").agg(agg_dict).reset_index()

    normality_results_means = apply_normality_test(task_means)
    normality_results = apply_normality_test(df_filtered)

    task_means["first_language"] = task_means['first_language'].apply(categorize_first_language)
    
    metric_residuals, metrics_demographics_results = regress_out_demographics(
        task_means, 
        outcomes=metrics, 
        demographics=['age', 'gender', 'education', 'first_language'],
        names=names)
    
    # Process metrics for cognition using residuals (no group filter)
    ls_multivar = process_regression_on_residuals(
        metric_residuals[metric_residuals["group"]!="patient"], 
        metrics,  # No need for _resid suffix, these columns are overwritten
        predictors=['working_memory',  'stroop_inhibition'], 
        names = names,
        group_filter=None
    )

    # Process metrics for patients using residuals (filter for patients)
    pat_multivar = process_regression_on_residuals(
        metric_residuals, 
        metrics, 
        predictors=['working_memory', 'stroop_inhibition','panss_pos_sum', 'panss_neg_sum'
                ], 
        names = names,
        group_filter="patient"
    )

    # Process metrics for healthy participants using residuals (filter for healthy participants)
    hs_multivar = process_regression_on_residuals(
        metric_residuals, 
        metrics, 
        predictors=['working_memory',  'stroop_inhibition', 'mss_pos_sum', 'mss_neg_sum', 'mss_dis_sum',], 
        names = names,
        group_filter="hs"
    )

    corr_control_cog_demo_length_patients = hierarchical_regression_with_vif(task_means[task_means["group"] == "patient"], new_metrics, [
        'panss_pos_sum', 'panss_neg_sum'
        ], ["stroop_inhibition", "working_memory", "number_tokens"])
    
    corr_control_cog_demo_patients = hierarchical_regression_with_vif(task_means[task_means["group"] == "patient"], metrics, [
        'panss_neg_sum',
        ], ["stroop_inhibition", "working_memory"])

    path = CONFIG["stats"]["paths"]["figures_dir"]

    anova_list = []
    pairwise_list = []

    alpha = 0.05  # Add these missing config values
    num_tests = 4
    corrected_alpha = alpha / num_tests
    n_groups = len(df_filtered["group"].unique())
    n_subjects = len(df_filtered["study_id"].unique())

    anova, pairwise = compare_groups_single_plot_regression(task_means, metrics, "group", path, scale_data=False, n_comp=len(metrics))
    anova_list += anova
    pairwise_list += pairwise

    pairwise_df = pd.DataFrame(pairwise_list)
    anova_df = pd.DataFrame(anova_list)
    
    anova_table = anova_df.copy().reset_index(drop=True)[['metric', 'r_squared', 'f_stat', 'p_model', 'Low Sczt mean', 'Low Sczt sd',
       'High Sczt mean', 'High Sczt sd', 'Psychosis mean', 'Psychosis sd']]

    anova_table['Low Sczt'] = anova_table.apply(lambda row: f"{row['Low Sczt mean']:.2f} ({row['Low Sczt sd']:.2f})", axis=1)
    anova_table['High Sczt'] = anova_table.apply(lambda row: f"{row['High Sczt mean']:.2f} ({row['High Sczt sd']:.2f})", axis=1)
    anova_table['Psychosis'] = anova_table.apply(lambda row: f"{row['Psychosis mean']:.2f} ({row['Psychosis sd']:.2f})", axis=1)
    
    anova_table['r_squared'] = anova_table.apply(lambda row: f"{row['r_squared']:.2f}", axis=1)
    anova_table['f_stat'] = anova_table.apply(lambda row: f"{row['f_stat']:.2f} ({format_p_value(row['p_model'])})", axis=1)

    # Drop the separate mean and SD columns
    anova_table = anova_table[['metric', 'r_squared', 'f_stat',  'Low Sczt', 'High Sczt', 'Psychosis']]

    # Rename columns to the final desired names
    anova_table.columns = ["Metric", "${R}^2$", "F", "Low Sczt (Mean, SD)", "High Sczt (Mean, SD)", "Psychosis (Mean, SD)"]
    
    pairwise_table = pairwise_df.copy().reset_index(drop=True)
    pairwise_table.columns = ["Metric", "Comparison", "Mean Diff.", "p adj."]
    
    df_summary = df_filtered[[
            "study_id",
            "group",
            "age",
            "gender",
            "education",
            "first_language",
            "diagnosis",
            'duration_untreated',
            'age_onset',
            'antipsy_duration', 
            "panss_total",
            "mss_total"]].groupby("study_id").first().reset_index()
    
    formatted_summary, patient_breakout = summary_table(df_summary)

    results = {
        "corr_df": correlation_apa(task_means, cog_var+metrics, names),
        "formatted_summary": formatted_summary,
        "breakout_patients": patient_breakout,
        "normality_results": normality_results,
        "normality_results_means": normality_results_means,
        "demographic_factors_metrics": metrics_demographics_results,
        "metrics_ls_reg": format_regression_results_apa(ls_multivar, 40),
        "metrics_ls_reg_dict": ls_multivar,
        "metrics_pat_reg": format_regression_results_apa(pat_multivar, 40),
        "metrics_pat_reg_dict": pat_multivar,
        "metrics_hs_reg": format_regression_results_apa(hs_multivar, 40),
        "metrics_hs_reg_dict": hs_multivar,
        
        "stepwise_length": corr_control_cog_demo_length_patients,
        "stepwise": corr_control_cog_demo_patients,
        
        "stepwise_length_str": report_stepwise_regression(corr_control_cog_demo_length_patients),
        "stepwise_str": report_stepwise_regression(corr_control_cog_demo_patients),
        
        
        "pairwise": pairwise_table,
        "anova": anova_table,
        "anova_str": report_categorical_regression(anova_df),
        "alpha": alpha,
        "num_tests": num_tests,
        "corrected_alpha": corrected_alpha,
        "n_groups": n_groups,
        "n_subjects": n_subjects}
    
    with open(os.path.join(CONFIG["stats"]["paths"]["results_dir"], f"stats_results{'_lower' if lower else '_upper'}.pkl"), 'wb') as handle:
        pickle.dump(results, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    df_filtered.to_csv(os.path.join(CONFIG["stats"]["paths"]["results_dir"], f"filtered_df{'_lower' if lower else '_upper'}.csv"), index=False)
    df_raw[df_raw["task"] == CONFIG["task_type"]].to_csv(os.path.join(CONFIG["stats"]["paths"]["results_dir"], f"raw_df{'_lower' if lower else '_upper'}.csv"), index=False)
    task_means.to_csv(os.path.join(CONFIG["stats"]["paths"]["results_dir"], f"task_means{'_lower' if lower else '_upper'}.csv"), index=False)
    
    return True

if __name__ == "__main__":
    main()