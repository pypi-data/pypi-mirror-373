# # autoclean/cleaner.py
# import pandas as pd
# from .imputation import impute_missing
# from .outliers import handle_outliers_iqr
# from .reports import generate_html_report

# class AutoClean:
#     """
#     The main class for automating the data cleaning process.
#     """
#     def __init__(self, dataframe, imputation_strategy='mean'):
#         """
#         Initializes the AutoClean object.

#         Args:
#             dataframe (pd.DataFrame): The DataFrame to be cleaned.
#             imputation_strategy (str): The method for imputing missing values.
#                                        Options: 'mean', 'median', 'mode', 'knn'.
#         """
#         self.original_df = dataframe.copy()
#         self.cleaned_df = dataframe.copy()
#         self.imputation_strategy = imputation_strategy
#         self.report_data = {
#             'initial_shape': self.original_df.shape,
#             'actions': []
#         }

#     def clean(self):
#         """
#         Executes the full data cleaning pipeline.

#         Returns:
#             pd.DataFrame: The cleaned DataFrame.
#         """
#         # 1. Handle Duplicates
#         initial_rows = len(self.cleaned_df)
#         self.cleaned_df.drop_duplicates(inplace=True)
#         final_rows = len(self.cleaned_df)
#         duplicates_removed = initial_rows - final_rows
#         if duplicates_removed > 0:
#             self.report_data['actions'].append(f"Removed {duplicates_removed} duplicate rows.")
#             self.report_data['duplicates_removed'] = duplicates_removed

#         # 2. Handle Missing Values
#         self.cleaned_df, missing_report = impute_missing(self.cleaned_df, strategy=self.imputation_strategy)
#         if missing_report:
#             self.report_data['actions'].append(f"Handled missing values using '{self.imputation_strategy}' strategy.")
#             self.report_data['missing_values'] = missing_report

#         # 3. Handle Outliers
#         self.cleaned_df, outlier_report = handle_outliers_iqr(self.cleaned_df)
#         if outlier_report:
#             self.report_data['actions'].append("Handled outliers using the IQR method.")
#             self.report_data['outliers'] = outlier_report

#         # 4. Data Type Inference (simple version)
#         type_conversions = {}
#         for col in self.cleaned_df.select_dtypes(include=['object']).columns:
#             try:
#                 # FIX: Added dayfirst=True to correctly parse dates like '15-01-2022'
#                 converted_col = pd.to_datetime(self.cleaned_df[col], dayfirst=True)
#                 if self.cleaned_df[col].dtype != converted_col.dtype:
#                     self.cleaned_df[col] = converted_col
#                     type_conversions[col] = {'from': 'object', 'to': 'datetime64'}
#             except (ValueError, TypeError):
#                 continue
#         if type_conversions:
#             self.report_data['actions'].append("Performed automatic data type conversions.")
#             self.report_data['type_conversions'] = type_conversions

#         self.report_data['final_shape'] = self.cleaned_df.shape
#         self.report_data['original_df_head'] = self.original_df.head().to_html()
#         self.report_data['cleaned_df_head'] = self.cleaned_df.head().to_html()
#         self.report_data['original_stats'] = self.original_df.describe(include='all').to_html()
#         self.report_data['cleaned_stats'] = self.cleaned_df.describe(include='all').to_html()

#         return self.cleaned_df

#     def generate_report(self, output_path='cleaning_report.html', format='html'):
#         """
#         Generates a cleaning report.

#         Args:
#             output_path (str): The path to save the report file.
#             format (str): The format of the report ('html', 'pdf', etc.). Currently only 'html' is supported.
#         """
#         if format.lower() == 'html':
#             generate_html_report(self.report_data, self.original_df, self.cleaned_df, output_path)
#             print(f"HTML report generated at: {output_path}")
#         else:
#             raise NotImplementedError("Only HTML reports are currently supported.")

# # autoclean/cleaner.py
# import pandas as pd
# from .imputation import impute_missing
# from .outliers import handle_outliers_iqr
# from .reports import generate_html_report

# class AutoClean:
#     """
#     The main class for automating the data cleaning process.
#     """
#     def __init__(self, dataframe, imputation_strategy='mean'):
#         """
#         Initializes the AutoClean object.
#         """
#         self.original_df = dataframe.copy()
#         self.cleaned_df = dataframe.copy()
#         self.imputation_strategy = imputation_strategy
#         self.report_data = {
#             'initial_shape': self.original_df.shape,
#             'actions': []
#         }

#     def clean(self):
#         """
#         Executes the full data cleaning pipeline in the correct order.
#         """
#         # STEP 1: Handle Duplicates
#         initial_rows = len(self.cleaned_df)
#         self.cleaned_df.drop_duplicates(inplace=True, ignore_index=True)
#         final_rows = len(self.cleaned_df)
#         duplicates_removed = initial_rows - final_rows
#         if duplicates_removed > 0:
#             self.report_data['actions'].append(f"Removed {duplicates_removed} duplicate rows.")
#             self.report_data['duplicates_removed'] = duplicates_removed

#         # STEP 2: Data Type Inference (Run this early to identify date columns)
#         type_conversions = {}
#         for col in self.cleaned_df.select_dtypes(include=['object']).columns:
#             try:
#                 # Use errors='coerce' to turn unparseable strings into NaT
#                 converted_col = pd.to_datetime(self.cleaned_df[col], dayfirst=True, errors='coerce')
#                 # Only convert if a high percentage of values are valid dates
#                 if converted_col.notna().sum() / self.cleaned_df[col].notna().sum() > 0.8:
#                      self.cleaned_df[col] = converted_col
#                      type_conversions[col] = {'from': 'object', 'to': 'datetime64[ns]'}
#             except (ValueError, TypeError):
#                 continue
#         if type_conversions:
#             self.report_data['actions'].append("Performed automatic data type conversions.")
#             self.report_data['type_conversions'] = type_conversions
            
#         # STEP 3: Handle Outliers (BEFORE IMPUTATION)
#         self.cleaned_df, outlier_report = handle_outliers_iqr(self.cleaned_df)
#         if outlier_report:
#             self.report_data['actions'].append("Handled outliers using the IQR method.")
#             self.report_data['outliers'] = outlier_report

#         # STEP 4: Handle Missing Values (AFTER OUTLIERS)
#         self.cleaned_df, missing_report = impute_missing(self.cleaned_df, strategy=self.imputation_strategy)
#         if missing_report:
#             self.report_data['actions'].append(f"Handled missing values using '{self.imputation_strategy}' strategy.")
#             self.report_data['missing_values'] = missing_report

#         # Final reporting data
#         self.report_data['final_shape'] = self.cleaned_df.shape
#         self.report_data['original_stats'] = self.original_df.describe(include='all').to_html()
#         self.report_data['cleaned_stats'] = self.cleaned_df.describe(include='all').to_html()

#         return self.cleaned_df

#     def generate_report(self, output_path='cleaning_report.html', format='html'):
#         """
#         Generates a cleaning report.
#         """
#         if format.lower() == 'html':
#             generate_html_report(self.report_data, self.original_df, self.cleaned_df, output_path)
#             # print(f"HTML report generated at: {output_path}") # This is now handled in test_run.py
#         else:
#             raise NotImplementedError("Only HTML reports are currently supported.")

# autoclean/cleaner.py
import pandas as pd
from .imputation import impute_missing
from .outliers import handle_outliers_iqr
from .reports import generate_html_report

class AutoClean:
    """
    The main class for automating the data cleaning process.
    """
    def __init__(self, dataframe, imputation_strategy='mean'):
        """
        Initializes the AutoClean object.
        """
        self.original_df = dataframe.copy()
        self.cleaned_df = dataframe.copy()
        self.imputation_strategy = imputation_strategy
        self.report_data = {
            'initial_shape': self.original_df.shape,
            'actions': []
        }

    def clean(self):
        """
        Executes the full data cleaning pipeline in the correct order.
        """
        # STEP 1: Handle Duplicates
        initial_rows = len(self.cleaned_df)
        self.cleaned_df.drop_duplicates(inplace=True, ignore_index=True)
        final_rows = len(self.cleaned_df)
        duplicates_removed = initial_rows - final_rows
        if duplicates_removed > 0:
            self.report_data['actions'].append(f"Removed {duplicates_removed} duplicate rows.")
            self.report_data['duplicates_removed'] = duplicates_removed

        # STEP 2: Data Type Inference
        type_conversions = {}
        for col in self.cleaned_df.select_dtypes(include=['object']).columns:
            # Try to convert to numeric first
            converted_numeric = pd.to_numeric(self.cleaned_df[col], errors='coerce')
            if converted_numeric.notna().sum() / self.cleaned_df[col].notna().sum() > 0.8:
                self.cleaned_df[col] = converted_numeric
                type_conversions[col] = {'from': 'object', 'to': 'numeric'}
                continue # Move to next column

            # If not numeric, try to convert to datetime
            try:
                # FINAL FIX: Specify the exact date format to silence warnings.
                converted_col = pd.to_datetime(self.cleaned_df[col], format='%d-%m-%Y', errors='coerce')
                if converted_col.notna().sum() / self.cleaned_df[col].notna().sum() > 0.8:
                     self.cleaned_df[col] = converted_col
                     type_conversions[col] = {'from': 'object', 'to': 'datetime64[ns]'}
            except (ValueError, TypeError):
                continue
        if type_conversions:
            self.report_data['actions'].append("Performed automatic data type conversions.")
            self.report_data['type_conversions'] = type_conversions
            
        # STEP 3: Handle Outliers (BEFORE IMPUTATION)
        self.cleaned_df, outlier_report = handle_outliers_iqr(self.cleaned_df)
        if outlier_report:
            self.report_data['actions'].append("Handled outliers using the IQR method.")
            self.report_data['outliers'] = outlier_report

        # STEP 4: Handle Missing Values (AFTER OUTLIERS)
        self.cleaned_df, missing_report = impute_missing(self.cleaned_df, strategy=self.imputation_strategy)
        if missing_report:
            self.report_data['actions'].append(f"Handled missing values using '{self.imputation_strategy}' strategy.")
            self.report_data['missing_values'] = missing_report

        # Final reporting data
        self.report_data['final_shape'] = self.cleaned_df.shape
        self.report_data['original_stats'] = self.original_df.describe(include='all').to_html()
        self.report_data['cleaned_stats'] = self.cleaned_df.describe(include='all').to_html()

        return self.cleaned_df

    def generate_report(self, output_path='cleaning_report.html', format='html'):
        """
        Generates a cleaning report.
        """
        if format.lower() == 'html':
            generate_html_report(self.report_data, self.original_df, self.cleaned_df, output_path)
        else:
            raise NotImplementedError("Only HTML reports are currently supported.")

