from __future__ import annotations
from typing import Dict, Optional, List

from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from ..utils.helpers import safe_import_lightgbm, safe_import_xgboost


class ModelFactory:
    """Create candidate model classes based on the problem type."""

    def __init__(self, problem_type: str, random_state: int = 42) -> None:
        if problem_type not in {"classification", "regression"}:
            raise ValueError("problem_type must be 'classification' or 'regression'")
        self.problem_type = problem_type
        self.random_state = random_state

    def get_models(self, include: Optional[List[str]] = None) -> Dict[str, object]:
        include = set(m.lower() for m in include) if include else None

        models: Dict[str, object] = {}

        if self.problem_type == "classification":
            if include is None or "logreg" in include:
                models["logreg"] = LogisticRegression
            if include is None or "rf" in include or "randomforest" in include:
                models["random_forest"] = RandomForestClassifier

            xgb_cls = safe_import_xgboost(task="cls", random_state=self.random_state)
            if xgb_cls and (
                include is None or "xgb" in include or "xgboost" in include
            ):
                models["xgboost"] = xgb_cls

            lgbm_cls = safe_import_lightgbm(task="cls", random_state=self.random_state)
            if lgbm_cls and (
                include is None or "lgbm" in include or "lightgbm" in include
            ):
                models["lightgbm"] = lgbm_cls

        else:  # regression
            if include is None or "linreg" in include or "linear" in include:
                models["linear"] = LinearRegression
            if include is None or "rf" in include or "randomforest" in include:
                models["random_forest"] = RandomForestRegressor

            xgb_reg = safe_import_xgboost(task="reg", random_state=self.random_state)
            if xgb_reg and (
                include is None or "xgb" in include or "xgboost" in include
            ):
                models["xgboost"] = xgb_reg

            lgbm_reg = safe_import_lightgbm(task="reg", random_state=self.random_state)
            if lgbm_reg and (
                include is None or "lgbm" in include or "lightgbm" in include
            ):
                models["lightgbm"] = lgbm_reg

        if not models:
            raise RuntimeError(
                "No models available. Check your 'include' filter or install optional libs."
            )
        return models
