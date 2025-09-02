# krishnautoml/eda/eda_report.py

import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


class EDAReport:
    def __init__(self):
        pass

    def generate(self, X: pd.DataFrame, y: pd.Series, output_dir="reports/eda"):
        os.makedirs(output_dir, exist_ok=True)

        df = X.copy()
        df["__target__"] = y

        # 1. Basic summary
        summary = df.describe(include="all").transpose()
        summary.to_csv(os.path.join(output_dir, "summary.csv"))

        # 2. Missing values
        missing = df.isnull().mean().sort_values(ascending=False)
        missing.to_csv(os.path.join(output_dir, "missing_values.csv"))

        # 3. Target distribution
        plt.figure(figsize=(6, 4))
        sns.histplot(y, kde=True)
        plt.title("Target Distribution")
        target_plot_path = os.path.join(output_dir, "target_distribution.png")
        plt.savefig(target_plot_path)
        plt.close()

        # 4. Correlation heatmap (numeric only)
        plt.figure(figsize=(10, 8))
        corr = df.corr(numeric_only=True)
        sns.heatmap(corr, annot=False, cmap="coolwarm")
        plt.title("Feature Correlation Heatmap")
        corr_plot_path = os.path.join(output_dir, "correlation_heatmap.png")
        plt.savefig(corr_plot_path)
        plt.close()

        # 5. Generate simple HTML
        html_path = os.path.join(output_dir, "eda_report.html")
        with open(html_path, "w") as f:
            f.write(
                """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>EDA Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; }}
        img {{ max-width: 600px; margin: 20px 0; }}
        table {{ border-collapse: collapse; width: 80%; margin-bottom: 30px; }}
        th, td {{ border: 1px solid #ccc; padding: 8px; }}
        th {{ background-color: #f9f9f9; }}
    </style>
</head>
<body>
    <h1>Exploratory Data Analysis Report</h1>

    <h2>1. Summary Statistics</h2>
    <p>Saved as: <code>summary.csv</code></p>

    <h2>2. Missing Values</h2>
    <p>Saved as: <code>missing_values.csv</code></p>

    <h2>3. Target Distribution</h2>
    <img src="target_distribution.png" alt="Target Distribution">

    <h2>4. Correlation Heatmap</h2>
    <img src="correlation_heatmap.png" alt="Correlation Heatmap">

</body>
</html>
            """
            )

        print(f"EDA report generated at {html_path}")
