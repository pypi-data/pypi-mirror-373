from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Optional
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer


class Preprocessor:
    """
    Builds a ColumnTransformer:
    - Numeric: median impute → standard scale
    - Categorical: most_frequent impute → one-hot encode
    Returns numpy array to keep models framework-agnostic.
    """

    def __init__(self) -> None:
        self.pipeline: Optional[Pipeline] = None
        self.feature_names_: Optional[list[str]] = None

    @staticmethod
    def _get_ohe() -> OneHotEncoder:
        # Handle different sklearn versions
        try:
            return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        except TypeError:
            return OneHotEncoder(handle_unknown="ignore", sparse=False)

    def fit_transform(
        self, X: pd.DataFrame, y: Optional[pd.Series] = None
    ) -> np.ndarray:
        cat_cols = X.select_dtypes(
            include=["object", "category", "bool"]
        ).columns.tolist()
        num_cols = X.select_dtypes(include=[np.number]).columns.tolist()

        num_pipe = Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]
        )

        cat_pipe = Pipeline(
            [
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("ohe", self._get_ohe()),
            ]
        )

        ct = ColumnTransformer(
            [
                ("num", num_pipe, num_cols),
                ("cat", cat_pipe, cat_cols),
            ]
        )

        self.pipeline = Pipeline([("ct", ct)])
        Xt = self.pipeline.fit_transform(X, y)
        return Xt

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        if self.pipeline is None:
            raise RuntimeError("Preprocessor is not fitted; call fit_transform first.")
        return self.pipeline.transform(X)
