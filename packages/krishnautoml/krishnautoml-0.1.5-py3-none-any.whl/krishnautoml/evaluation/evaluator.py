# krishnautoml/evaluation/evaluator.py

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    roc_curve,
    r2_score,
    mean_squared_error,
    mean_absolute_error,
)


class Evaluator:
    def __init__(self, output_dir="reports/evaluation"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def evaluate(self, model, X, y, problem_type="auto", metrics=None):
        """
        Evaluate model on classification or regression.
        Returns dict of metrics.
        """
        y_pred = model.predict(X)

        # Auto detect if not specified
        if problem_type == "auto":
            problem_type = (
                "classification"
                if len(np.unique(y)) < 20 and y.dtype in ["int32", "int64"]
                else "regression"
            )

        results = {}

        if problem_type == "classification":
            results.update(self._classification_metrics(model, X, y, y_pred, metrics))
        else:
            results.update(self._regression_metrics(y, y_pred, metrics))

        return results

    def _classification_metrics(self, model, X, y, y_pred, metrics=None):
        if metrics is None:
            metrics = ["accuracy", "precision", "recall", "f1", "roc_auc"]

        results = {}
        if "accuracy" in metrics:
            results["accuracy"] = accuracy_score(y, y_pred)
        if "precision" in metrics:
            results["precision"] = precision_score(
                y, y_pred, average="weighted", zero_division=0
            )
        if "recall" in metrics:
            results["recall"] = recall_score(
                y, y_pred, average="weighted", zero_division=0
            )
        if "f1" in metrics:
            results["f1"] = f1_score(y, y_pred, average="weighted", zero_division=0)

        if "roc_auc" in metrics and len(np.unique(y)) == 2:  # binary classification
            y_prob = model.predict_proba(X)[:, 1]
            results["roc_auc"] = roc_auc_score(y, y_prob)

            # ROC Curve
            fpr, tpr, _ = roc_curve(y, y_prob)
            plt.figure()
            plt.plot(fpr, tpr, label=f"ROC (AUC={results['roc_auc']:.2f})")
            plt.plot([0, 1], [0, 1], linestyle="--")
            plt.xlabel("False Positive Rate")
            plt.ylabel("True Positive Rate")
            plt.title("ROC Curve")
            plt.legend()
            plt.savefig(os.path.join(self.output_dir, "roc_curve.png"))
            plt.close()

        # Confusion Matrix
        cm = confusion_matrix(y, y_pred)
        plt.figure(figsize=(6, 5))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
        plt.xlabel("Predicted")
        plt.ylabel("True")
        plt.title("Confusion Matrix")
        plt.savefig(os.path.join(self.output_dir, "confusion_matrix.png"))
        plt.close()

        return results

    def _regression_metrics(self, y, y_pred, metrics=None):
        if metrics is None:
            metrics = ["r2", "rmse", "mae", "mape"]

        results = {}
        if "r2" in metrics:
            results["r2"] = r2_score(y, y_pred)
        if "rmse" in metrics:
            results["rmse"] = mean_squared_error(y, y_pred, squared=False)
        if "mae" in metrics:
            results["mae"] = mean_absolute_error(y, y_pred)
        if "mape" in metrics:
            results["mape"] = np.mean(np.abs((y - y_pred) / y)) * 100

        # Residual plot
        residuals = y - y_pred
        plt.figure(figsize=(6, 5))
        sns.scatterplot(x=y_pred, y=residuals)
        plt.axhline(0, linestyle="--", color="red")
        plt.xlabel("Predicted")
        plt.ylabel("Residuals")
        plt.title("Residual Plot")
        plt.savefig(os.path.join(self.output_dir, "residual_plot.png"))
        plt.close()

        return results
