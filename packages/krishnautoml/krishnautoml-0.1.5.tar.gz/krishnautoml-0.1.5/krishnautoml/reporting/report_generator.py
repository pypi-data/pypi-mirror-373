import datetime
from jinja2 import Environment, PackageLoader, select_autoescape
import os


class ReportGenerator:
    def __init__(self, output_dir="reports/final"):
        # Load templates from package resources
        self.env = Environment(
            loader=PackageLoader("krishnautoml.reporting", "templates"),
            autoescape=select_autoescape(["html", "xml"]),
        )
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _make_relative(self, path: str) -> str:
        if not path:
            return path
        return os.path.relpath(path, start=self.output_dir)

    def generate_report(
        self, project_name, metrics, plots=None, eda_report=None, model_info=None
    ):
        template = self.env.get_template("report_template.html")

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
