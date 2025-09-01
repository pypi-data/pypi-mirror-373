import pandas as pd
import os # <-- Import the os module
from autoclean import AutoClean

# --- This is the new, more robust way to find the data file ---
# Get the absolute path to the directory where this script is located
script_dir = os.path.dirname(__file__) 
# Join that path with the filename
csv_path = os.path.join(script_dir, 'sample_data.csv')
# ----------------------------------------------------------------

# 1. Load the messy data using the correct path
print(f"Loading data from: {csv_path}")
df = pd.read_csv(csv_path)
print("Original Data:")
print(df)
print("\n" + "="*30 + "\n")

# 2. Initialize AutoClean
cleaner = AutoClean(df, imputation_strategy='knn')

# 3. Run the cleaning process
print("Starting the cleaning process...")
cleaned_df = cleaner.clean()
print("Cleaning complete!")
print("\n" + "="*30 + "\n")

# 4. Generate the HTML report
# We'll save the report in the main project folder, not inside 'tests'
report_filename = 'cleaning_report.html' 
cleaner.generate_report(output_path=report_filename)
print(f"Report generated: {report_filename}")
print("\n" + "="*30 + "\n")

# 5. Display the cleaned data
print("Cleaned Data:")
print(cleaned_df)
