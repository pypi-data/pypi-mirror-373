# autoclean/reports.py

import matplotlib # <-- ADD THIS LINE
matplotlib.use('Agg') # <-- AND THIS LINE. Must be before pyplot import.

import base64
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Environment, FileSystemLoader, Template

# (The rest of the file is exactly the same as before)
# ...
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AutoClean Report</title>
    <style>
        body { font-family: sans-serif; margin: 2em; background-color: #f9f9f9; color: #333; }
        h1, h2, h3 { color: #1a237e; }
        .container { background-color: #fff; padding: 2em; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        .summary, .section { margin-bottom: 2em; border-bottom: 1px solid #eee; padding-bottom: 1em; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #e8eaf6; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 1em; }
        .plot img { max-width: 100%; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>AutoClean Cleaning Report</h1>
        
        <div class="summary">
            <h2>Summary</h2>
            <p><strong>Initial DataFrame Shape:</strong> {{ initial_shape[0] }} rows, {{ initial_shape[1] }} columns</p>
            <p><strong>Final DataFrame Shape:</strong> {{ final_shape[0] }} rows, {{ final_shape[1] }} columns</p>
            <h3>Actions Performed:</h3>
            <ul>
                {% for action in actions %}
                <li>{{ action }}</li>
                {% endfor %}
            </ul>
        </div>

        {% if duplicates_removed %}
        <div class="section">
            <h3>Duplicates</h3>
            <p>Removed {{ duplicates_removed }} duplicate rows.</p>
        </div>
        {% endif %}

        {% if missing_values %}
        <div class="section">
            <h3>Missing Values</h3>
            <p>Imputation Strategy: <strong>{{ missing_values.strategy }}</strong></p>
            <ul>
            {% for col, method in missing_values.imputed_columns.items() %}
                <li><strong>{{ col }}:</strong> Imputed using '{{ method }}'.</li>
            {% endfor %}
            </ul>
        </div>
        {% endif %}

        {% if outliers %}
        <div class="section">
            <h3>Outliers (IQR Method)</h3>
            <ul>
            {% for col, details in outliers.capped_columns.items() %}
                <li><strong>{{ col }}:</strong> Found and capped {{ details.outliers_found }} outliers.</li>
            {% endfor %}
            </ul>
        </div>
        {% endif %}
        
        <div class="section">
            <h2>Data Distribution: Before vs. After</h2>
            <div class="grid">
            {% for plot in plots %}
                <div class="plot">
                    <h3>{{ plot.col_name }}</h3>
                    <img src="data:image/png;base64,{{ plot.data }}" alt="Distribution plot for {{ plot.col_name }}">
                </div>
            {% endfor %}
            </div>
        </div>

        <div class="section">
            <h2>Summary Statistics: Before Cleaning</h2>
            {{ original_stats | safe }}
        </div>
        <div class="section">
            <h2>Summary Statistics: After Cleaning</h2>
            {{ cleaned_stats | safe }}
        </div>
    </div>
</body>
</html>
"""

def _generate_plots(df_before, df_after):
    """Generates distribution plots for numeric columns."""
    plots = []
    numeric_cols = df_before.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        sns.histplot(df_before[col], kde=True, ax=axes[0], color='blue').set_title('Before')
        sns.histplot(df_after[col], kde=True, ax=axes[1], color='green').set_title('After')
        fig.suptitle(f'Distribution of {col}', fontsize=16)
        
        buf = BytesIO()
        fig.savefig(buf, format='png')
        plt.close(fig)
        data = base64.b64encode(buf.getbuffer()).decode('ascii')
        plots.append({'col_name': col, 'data': data})
    return plots

def generate_html_report(report_data, original_df, cleaned_df, output_path):
    """
    Generates and saves an HTML report.
    """
    plots = _generate_plots(original_df, cleaned_df)
    report_data['plots'] = plots

    template = Template(HTML_TEMPLATE)
    html_content = template.render(report_data)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
