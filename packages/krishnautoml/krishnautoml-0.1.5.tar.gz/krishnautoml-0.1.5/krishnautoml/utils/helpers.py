from __future__ import annotations
import numpy as np
from sklearn.model_selection import KFold, StratifiedKFold


def detect_problem_type(y) -> str:
    """Infer problem type from target vector."""
    if y.dtype.kind in {"O"}:  # strings/objects
        return "classification"

    # If numeric but few unique integer-like values → classification
    unique_vals = np.unique(y.dropna()) if hasattr(y, "dropna") else np.unique(y)
    if unique_vals.size <= 20 and np.all(np.equal(np.mod(unique_vals, 1), 0)):
        return "classification"

    return "regression"


def get_cv(problem_type: str, n_splits: int, random_state: int):
    if problem_type == "classification":
        return StratifiedKFold(
            n_splits=n_splits, shuffle=True, random_state=random_state
        )
    return KFold(n_splits=n_splits, shuffle=True, random_state=random_state)


def get_default_scoring(problem_type: str) -> str:
    return (
        "accuracy"
        if problem_type == "classification"
        else "neg_root_mean_squared_error"
    )


# In krishnautoml/utils/helpers.py


def safe_import_xgboost(task: str, random_state: int):
    """Return configured xgboost model class or None if not installed."""
    try:
        from xgboost import XGBClassifier, XGBRegressor
    except Exception:
        return None

    if task == "cls":
        return XGBClassifier
    return XGBRegressor


def safe_import_lightgbm(task: str, random_state: int):
    """Return configured lightgbm model class or None if not installed."""
    try:
        from lightgbm import LGBMClassifier, LGBMRegressor
    except Exception:
        return None

    if task == "cls":
        return LGBMClassifier
    return LGBMRegressor
