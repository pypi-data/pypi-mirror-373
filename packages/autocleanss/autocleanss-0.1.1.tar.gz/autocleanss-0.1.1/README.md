# AutoCleanSS: Your Automated Data Cleaning Companion

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/sudipta9749/autocleanss/blob/main/LICENSE)

An advanced and automated data cleaning toolkit for Python, designed to streamline your data preprocessing workflow with intelligent imputation, outlier handling, and comprehensive reporting.


## ✨ Key Features

*   **Automated Cleaning Pipeline**: Orchestrates a complete data cleaning process from duplicates to outliers.
*   **Duplicate Handling**: Automatically identifies and removes duplicate rows to ensure data uniqueness.
*   **Intelligent Missing Value Imputation**: Supports various strategies including `mean`, `median`, `mode`, and `knn` imputation, tailored for numerical and categorical data. Special handling for datetime missing values.
*   **Robust Outlier Treatment**: Employs the Interquartile Range (IQR) method to detect and cap outliers in numerical columns, preventing skewness and improving model performance.
*   **Automatic Data Type Inference**: Dynamically infers and converts appropriate data types (e.g., object to numeric, object to datetime) for better data integrity.
*   **Comprehensive HTML Reports**: Generates detailed, interactive HTML reports summarizing cleaning actions, before/after statistics, and visual distribution plots for key numerical features.
*   **Seamless Pandas Integration**: Built to work effortlessly with Pandas DataFrames, making it intuitive for data scientists and analysts.

## 📦 Installation

To get started with AutoCleanSS, clone the repository and install it using pip:

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/sudipta9749/autocleanss.git
    cd autocleanss
    ```

2.  **Install dependencies and the package**:
    It's recommended to install in a virtual environment.
    ```bash
    pip install autocleanss
    ```

## 🚀 Usage

Using `autocleanss` is straightforward. Here's a quick example:

```python
import pandas as pd
from autoclean import AutoClean

# 1. Load your messy data into a Pandas DataFrame
#    (Replace with your actual data loading, e.g., pd.read_csv('your_data.csv'))
data = {
    'ID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'Feature_A': [10.1, 11.2, None, 13.4, 14.5, 100.0, 16.7, 17.8, 10.1, 19.9],
    'Feature_B': ['A', 'B', 'A', 'C', 'B', 'D', 'A', 'A', 'A', None],
    'Feature_C': ['01-01-2023', '02-01-2023', '03-01-2023', '04-01-2023', '05-01-2023', None, '07-01-2023', '08-01-2023', '01-01-2023', '09-01-2023'],
    'Feature_D': [5, 6, 5, 7, 8, 9, 10, 11, 5, 12]
}
df = pd.DataFrame(data)

print("--- Original DataFrame ---")
print(df)
print("\n" + "="*40 + "\n")

# 2. Initialize the AutoClean object with your DataFrame
#    You can specify an imputation strategy: 'mean', 'median', 'mode', or 'knn'
cleaner = AutoClean(df, imputation_strategy='knn')

# 3. Run the cleaning process
cleaned_df = cleaner.clean()

print("--- Cleaned DataFrame ---")
print(cleaned_df)
print("\n" + "="*40 + "\n")

# 4. Generate a comprehensive HTML report
#    The report will be saved as 'cleaning_report.html' in your current directory.
cleaner.generate_report(output_path='my_cleaning_report.html')
print("✅ Cleaning report saved to 'my_cleaning_report.html'")
```

This will produce a `my_cleaning_report.html` file in your project directory, detailing all the cleaning steps and showing the impact on your data.

You can use 
``` python
from IPython.display import HTML
HTML(filename='cleaning_report.html')
```
In your notebook to visualize the report.