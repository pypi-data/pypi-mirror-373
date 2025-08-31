# # autoclean/imputation.py
# import pandas as pd
# from sklearn.impute import SimpleImputer, KNNImputer
# from sklearn.preprocessing import LabelEncoder

# def impute_missing(df, strategy='mean'):
#     """
#     Handles missing values in the DataFrame based on the chosen strategy.

#     Args:
#         df (pd.DataFrame): The DataFrame with missing values.
#         strategy (str): The imputation strategy ('mean', 'median', 'mode', 'knn').

#     Returns:
#         tuple: A tuple containing the imputed DataFrame and a report dictionary.
#     """
#     report = {'strategy': strategy, 'imputed_columns': {}}
#     cols_with_missing = df.columns[df.isnull().any()].tolist()

#     if not cols_with_missing:
#         return df, {}

#     if strategy in ['mean', 'median', 'mode']:
#         # Separate numeric and categorical columns
#         numeric_cols = df.select_dtypes(include=['number']).columns.intersection(cols_with_missing)
#         categorical_cols = df.select_dtypes(include=['object', 'category']).columns.intersection(cols_with_missing)

#         if not numeric_cols.empty:
#             num_strategy = 'mean' if strategy != 'mode' else 'most_frequent'
#             imputer = SimpleImputer(strategy=num_strategy)
#             df[numeric_cols] = imputer.fit_transform(df[numeric_cols])
#             report['imputed_columns'].update({col: num_strategy for col in numeric_cols})

#         if not categorical_cols.empty:
#             imputer = SimpleImputer(strategy='most_frequent')
#             df[categorical_cols] = imputer.fit_transform(df[categorical_cols])
#             report['imputed_columns'].update({col: 'mode' for col in categorical_cols})

#     elif strategy == 'knn':
#         # KNNImputer works only on numeric data. We need to encode categorical data first.
#         encoders = {}
#         df_encoded = df.copy()

#         for col in df.select_dtypes(include=['object', 'category']).columns:
#             if df_encoded[col].isnull().sum() > 0:
#                 # FIX: Replaced inplace=True with direct assignment to avoid FutureWarning
#                 df_encoded[col] = df_encoded[col].fillna('missing')
#             le = LabelEncoder()
#             df_encoded[col] = le.fit_transform(df_encoded[col])
#             encoders[col] = le

#         imputer = KNNImputer()
#         df_imputed_encoded = pd.DataFrame(imputer.fit_transform(df_encoded), columns=df.columns)

#         # Decode the categorical columns back
#         for col, le in encoders.items():
#             # Convert imputed floats back to integers for decoding
#             df_imputed_encoded[col] = df_imputed_encoded[col].round().astype(int)
#             df_imputed_encoded[col] = le.inverse_transform(df_imputed_encoded[col])
#             # Change placeholder back to NaN
#             df_imputed_encoded[col] = df_imputed_encoded[col].replace('missing', pd.NA)

#         df = df_imputed_encoded
#         report['imputed_columns'].update({col: 'knn' for col in cols_with_missing})

#     else:
#         raise ValueError("Invalid imputation strategy. Choose from 'mean', 'median', 'mode', 'knn'.")

#     return df, report

# autoclean/imputation.py
import pandas as pd
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import LabelEncoder

def _impute_datetimes(df, report):
    """Handles missing datetime columns separately using the mode."""
    # Identify datetime columns with missing values
    datetime_cols = df.select_dtypes(include=['datetime64[ns]']).columns
    for col in datetime_cols:
        if df[col].isnull().any():
            mode_val = df[col].mode()
            # Check if mode returns a value
            if not mode_val.empty:
                df[col] = df[col].fillna(mode_val[0])
                report['imputed_columns'][col] = 'mode (datetime)'
    return df

def impute_missing(df, strategy='mean'):
    """
    Handles missing values in the DataFrame based on the chosen strategy.
    Datetime columns are handled first with 'mode', then others are processed.
    """
    report = {'strategy': strategy, 'imputed_columns': {}}
    
    # FIX: Handle datetime columns first and separately
    df = _impute_datetimes(df, report)

    # Continue with other types, excluding datetimes
    df_subset = df.select_dtypes(exclude=['datetime64[ns]'])
    cols_with_missing = df_subset.columns[df_subset.isnull().any()].tolist()

    if not cols_with_missing:
        return df, report # Return early if no other missing values

    if strategy in ['mean', 'median', 'mode']:
        numeric_cols = df_subset.select_dtypes(include=['number']).columns.intersection(cols_with_missing)
        categorical_cols = df_subset.select_dtypes(include=['object', 'category']).columns.intersection(cols_with_missing)

        if not numeric_cols.empty:
            num_strategy = 'mean' if strategy != 'mode' else 'most_frequent'
            imputer = SimpleImputer(strategy=num_strategy)
            df[numeric_cols] = imputer.fit_transform(df[numeric_cols])
            report['imputed_columns'].update({col: num_strategy for col in numeric_cols})

        if not categorical_cols.empty:
            imputer = SimpleImputer(strategy='most_frequent')
            df[categorical_cols] = imputer.fit_transform(df[categorical_cols])
            report['imputed_columns'].update({col: 'mode' for col in categorical_cols})

    elif strategy == 'knn':
        encoders = {}
        df_encoded = df_subset.copy()

        for col in df_subset.select_dtypes(include=['object', 'category']).columns:
            if df_encoded[col].isnull().sum() > 0:
                df_encoded[col] = df_encoded[col].fillna('__MISSING__') # Use a unique placeholder
            le = LabelEncoder()
            df_encoded[col] = le.fit_transform(df_encoded[col])
            encoders[col] = le

        if df_encoded.isnull().values.any():
            imputer = KNNImputer()
            df_imputed_encoded = pd.DataFrame(imputer.fit_transform(df_encoded), columns=df_subset.columns, index=df_subset.index)

            for col, le in encoders.items():
                df_imputed_encoded[col] = df_imputed_encoded[col].round().astype(int)
                df_imputed_encoded[col] = le.inverse_transform(df_imputed_encoded[col])
                df_imputed_encoded[col] = df_imputed_encoded[col].replace('__MISSING__', pd.NA)

            df[df_subset.columns] = df_imputed_encoded
            report['imputed_columns'].update({col: 'knn' for col in cols_with_missing})

    else:
        raise ValueError("Invalid imputation strategy. Choose from 'mean', 'median', 'mode', 'knn'.")

    return df, report

