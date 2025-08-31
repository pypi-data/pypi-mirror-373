# autoclean/outliers.py
import pandas as pd

def handle_outliers_iqr(df):
    """
    Detects and caps outliers in numerical columns using the IQR method.

    Args:
        df (pd.DataFrame): The DataFrame to process.

    Returns:
        tuple: A tuple containing the processed DataFrame and a report dictionary.
    """
    report = {'capped_columns': {}}
    numeric_cols = df.select_dtypes(include=['number']).columns

    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        original_series = df[col].copy()
        df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)

        outliers_count = (original_series < lower_bound).sum() + (original_series > upper_bound).sum()
        if outliers_count > 0:
            report['capped_columns'][col] = {
                'outliers_found': outliers_count,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound
            }

    return df, report
