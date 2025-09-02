from __future__ import annotations
import pandas as pd
from typing import Tuple


class DataLoader:
    """Load CSV or DataFrame and split features/target."""

    def __init__(self):
        self.X_orig = None
        self.y_orig = None

    def load(
        self, data: pd.DataFrame | str, target: str
    ) -> Tuple[pd.DataFrame, pd.Series]:
        if isinstance(data, str):
            df = pd.read_csv(data)
        elif isinstance(data, pd.DataFrame):
            df = data.copy()
        else:
            raise TypeError("data must be a file path or a pandas DataFrame")

        if target not in df.columns:
            raise ValueError(
                f"Target column '{target}' not found in data. Available: {list(df.columns)}"
            )

        y = df[target]
        X = df.drop(columns=[target])

        # Add these lines to store a copy of the original data
        self.X_orig = X.copy()
        self.y_orig = y.copy()

        return X, y
