# AutoClean: Advanced Automated Data Cleaning Toolkit

AutoClean is a Python package that automates the heavy-lifting of data cleaning and preparation. It provides a simple, high-level API to handle common data quality issues and generates a beautiful, insightful HTML report of the entire process.

## Key Features

- **Comprehensive Cleaning**: Handles missing values, outliers, duplicate records, and data type inconsistencies.
- **Smart Imputation**: Includes standard (mean/median/mode) and ML-based (KNN) imputation methods.
- **Outlier Detection**: Uses the IQR method to detect and handle outliers in numerical data.
- **Data Type Inference**: Automatically detects and converts data types (e.g., object to datetime).
- **Automated HTML Report**: Generates a detailed, visual report with before-and-after statistics and visualizations.

## Installation

You can install AutoClean using pip:

```bash
pip install autoclean
```

## Quick Start

Clean your data and generate a report in just a few lines of code.

```python
import pandas as pd
from autoclean import AutoClean

# 1. Load your messy data
df = pd.read_csv('your_messy_data.csv')

# 2. Initialize the cleaner
# You can specify the imputation strategy, e.g., 'knn'
cleaner = AutoClean(df, imputation_strategy='knn')

# 3. Run the cleaning process
cleaned_df = cleaner.clean()

# 4. Generate the HTML report
cleaner.generate_report(output_path='cleaning_report.html')

# 5. View the cleaned data
print("Cleaned DataFrame:")
print(cleaned_df.head())
```
This will create a file named `cleaning_report.html` in your current directory. Open it in your browser to see a full analysis of the cleaning process.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
