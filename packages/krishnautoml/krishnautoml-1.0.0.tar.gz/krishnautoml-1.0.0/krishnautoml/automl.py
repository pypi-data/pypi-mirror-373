import pandas as pd
from typing import Optional, Dict, Any, List


from .data.loader import DataLoader
from .data.preprocessing import Preprocessor
from .models.model_factory import ModelFactory
from .tuning.tuner import Tuner
from .evaluation.evaluator import Evaluator
from .eda.eda_report import EDAReport
from .reporting.report_generator import ReportGenerator
from .utils.helpers import detect_problem_type
from joblib import dump
from sklearn.base import BaseEstimator


class KrishnAutoML:
    """
    Main entry point for the KrishnAutoML pipeline.
    Automates: loading, preprocessing, model selection, evaluation, saving.
    """

    def __init__(
        self,
        target: str,
        problem_type: str = "auto",
        generate_eda: bool = False,  # reserved for Phase 2
        random_state: int = 42,
        n_splits: int = 5,
    ) -> None:
        self.target = target
        self.problem_type = problem_type
        self.generate_eda = generate_eda
        self.random_state = random_state
        self.n_splits = n_splits

        self._loader = DataLoader()
        self._preproc = Preprocessor()

        self.X = None
        self.y = None
        self.X_test = None  # also make sure these are defined
        self.y_test = None
        self.best_model = None
        self.results: Dict[str, Any] = {}

        self.evaluator = Evaluator()

    # Fluent API
    def load_data(self, data: pd.DataFrame | str) -> "KrishnAutoML":
        """Accepts a CSV file path or pandas DataFrame; splits X, y."""
        self.X, self.y = self._loader.load(data, self.target)
        if self.X is None or self.y is None:
            raise ValueError("Loaded features or target are None. Check input data.")
        if self.problem_type == "auto":
            self.problem_type = detect_problem_type(self.y)
        return self

    def preprocess(self) -> "KrishnAutoML":
        """Fit the preprocessing pipeline and transform X."""
        self.X = self._preproc.fit_transform(self.X, self.y)
        return self

    def train_models(self, models: Optional[List[str]] = None) -> "KrishnAutoML":
        factory = ModelFactory(
            problem_type=self.problem_type, random_state=self.random_state
        )
        candidates = factory.get_models(models)

        from sklearn.model_selection import train_test_split

        X_train, X_test, y_train, y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=self.random_state
        )

        tuner = Tuner(cv=self.n_splits, random_state=self.random_state)
        self.results, self.best_model = tuner.run(
            candidates, X_train, y_train, problem_type=self.problem_type
        )

        self.model_info = {
            "name": type(self.best_model).__name__,
            "params": (
                self.best_model.get_params()
                if isinstance(self.best_model, BaseEstimator)
                else {}
            ),
        }

        # Store test data for evaluation
        self.X_test = X_test
        self.y_test = y_test

        return self

    def evaluate(self):
        if self.best_model is None:
            raise Exception("No trained model found. Run train_models() first.")
        if self.X_test is None or self.y_test is None:
            raise Exception(
                "Test data not available. Ensure load_data() and train_models() were called."
            )

        print(" Evaluating model...")
        results = self.evaluator.evaluate(
            model=self.best_model,
            X=self.X_test,
            y=self.y_test,
            problem_type=self.problem_type,
        )
        self.metrics = results

        print("Evaluation complete. Metrics:")
        for k, v in results.items():
            print(f"  {k}: {v:.4f}")

        return results

    def save(self, path: str = "best_model.pkl") -> None:
        dump(self.best_model, path)
        print(f"Model saved at {path}")

    def run_eda(self) -> "KrishnAutoML":
        """Generates an EDA report."""
        if self._loader.X_orig is None or self._loader.y_orig is None:
            raise RuntimeError("Data not loaded. Call load_data() first.")

        eda_report = EDAReport()
        eda_report.generate(self._loader.X_orig, self._loader.y_orig)

        return self

    def generate_report(self, project_name="AutoML_Project") -> str:
        if not hasattr(self, "metrics") or not hasattr(self, "model_info"):
            raise RuntimeError(
                "Please run train_models() and evaluate() before generating the report."
            )

        # Plots (conditionally included based on task)
        plots = []
        if self.problem_type == "classification":
            plots = [
                "reports/evaluation/confusion_matrix.png",
                "reports/evaluation/roc_curve.png",
            ]
        elif self.problem_type == "regression":
            plots = ["reports/evaluation/residual_plot.png"]

        eda_report = "reports/eda/eda_report.html"

        reporter = ReportGenerator()
        path = reporter.generate_report(
            project_name=project_name,
            metrics=self.metrics,
            plots=plots,
            eda_report=eda_report,
            model_info=self.model_info,
        )

        print(f"📄 Final report saved to: {path}")
        return path
