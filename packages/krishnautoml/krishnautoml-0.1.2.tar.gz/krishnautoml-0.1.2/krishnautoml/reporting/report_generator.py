# krishnautoml/reporting/report_generator.py

import os
import datetime
from jinja2 import Environment, FileSystemLoader


class ReportGenerator:
    def __init__(self, template_dir=None, output_dir="reports/final"):
        if template_dir is None:
            template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _make_relative(self, path: str) -> str:
        """
        Convert a file path to be relative to the report output directory.
        """
        if not path:
            return path
        return os.path.relpath(path, start=self.output_dir)

    def generate_report(
        self, project_name, metrics, plots=None, eda_report=None, model_info=None
    ):
        """
        Generate an HTML report combining EDA, evaluation metrics, and plots.

        Args:
            project_name (str): name of the ML project
            metrics (dict): evaluation results
            plots (list): list of file paths to plots
            eda_report (str): path to EDA HTML report
            model_info (dict): model name, hyperparameters, etc.
        """
        template = self.env.get_template("report_template.html")

        # Ensure relative paths so assets are accessible from HTML location
        rel_plots = [self._make_relative(p) for p in (plots or [])]
        rel_eda_report = self._make_relative(eda_report) if eda_report else None

        report_data = {
            "project_name": project_name,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "metrics": metrics,
            "plots": rel_plots,
            "eda_report": rel_eda_report,
            "model_info": model_info or {},
        }

        output_html = template.render(report_data)

        output_path = os.path.join(self.output_dir, f"{project_name}_report.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_html)

        return output_path
