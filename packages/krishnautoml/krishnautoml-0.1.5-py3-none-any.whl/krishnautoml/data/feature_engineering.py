# krishnautoml/data/feature_engineering.py

import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from category_encoders import TargetEncoder
from scipy.sparse import hstack


class FeatureEngineer:
    def __init__(
        self, use_target_encoding=True, use_tfidf=True, max_tfidf_features=500
    ):
        self.use_target_encoding = use_target_encoding
        self.use_tfidf = use_tfidf
        self.max_tfidf_features = max_tfidf_features

        # Internal encoders
        self.target_encoders = {}
        self.tfidf_encoders = {}
        self.onehot_encoder = None

        # Column tracking
        self.numeric_cols = []
        self.categorical_cols = []
        self.text_cols = []

    def fit_transform(self, X: pd.DataFrame, y: pd.Series):
        """
        Detect feature types and transform them accordingly.
        """
        self._detect_feature_types(X)

        # ----- Numeric -----
        X_numeric = X[self.numeric_cols] if self.numeric_cols else pd.DataFrame()

        # ----- Categorical -----
        if self.use_target_encoding and self.categorical_cols:
            te = TargetEncoder()
            X_categ = te.fit_transform(X[self.categorical_cols], y)
            self.target_encoders = te
        else:
            ohe = OneHotEncoder(handle_unknown="ignore", sparse=False)
            X_categ = (
                pd.DataFrame(ohe.fit_transform(X[self.categorical_cols]))
                if self.categorical_cols
                else pd.DataFrame()
            )
            self.onehot_encoder = ohe

        # ----- Text -----
        text_matrices = []
        if self.use_tfidf and self.text_cols:
            for col in self.text_cols:
                tfidf = TfidfVectorizer(max_features=self.max_tfidf_features)
                X_tfidf = tfidf.fit_transform(X[col].fillna("").astype(str))
                text_matrices.append(X_tfidf)
                self.tfidf_encoders[col] = tfidf

        # Combine everything
        if text_matrices:
            X_text = hstack(text_matrices)
        else:
            X_text = None

        from scipy.sparse import csr_matrix

        if isinstance(X_numeric, pd.DataFrame):
            X_numeric = csr_matrix(X_numeric.values)
        if isinstance(X_categ, pd.DataFrame):
            X_categ = csr_matrix(X_categ.values)

        if X_text is not None:
            return hstack([X_numeric, X_categ, X_text])
        else:
            return hstack([X_numeric, X_categ])

    def transform(self, X: pd.DataFrame):
        """
        Apply saved encoders to new data.
        """
        # ----- Numeric -----
        X_numeric = X[self.numeric_cols] if self.numeric_cols else pd.DataFrame()

        # ----- Categorical -----
        if self.use_target_encoding and self.categorical_cols:
            X_categ = self.target_encoders.transform(X[self.categorical_cols])
        else:
            X_categ = (
                pd.DataFrame(self.onehot_encoder.transform(X[self.categorical_cols]))
                if self.categorical_cols
                else pd.DataFrame()
            )

        # ----- Text -----
        text_matrices = []
        if self.use_tfidf and self.text_cols:
            for col in self.text_cols:
                tfidf = self.tfidf_encoders[col]
                X_tfidf = tfidf.transform(X[col].fillna("").astype(str))
                text_matrices.append(X_tfidf)

        # Combine everything
        from scipy.sparse import csr_matrix, hstack

        if isinstance(X_numeric, pd.DataFrame):
            X_numeric = csr_matrix(X_numeric.values)
        if isinstance(X_categ, pd.DataFrame):
            X_categ = csr_matrix(X_categ.values)

        if text_matrices:
            return hstack([X_numeric, X_categ] + text_matrices)
        else:
            return hstack([X_numeric, X_categ])

    def _detect_feature_types(self, X: pd.DataFrame):
        """
        Auto-detect numeric, categorical, and text features.
        """
        self.numeric_cols = X.select_dtypes(
            include=["int64", "float64"]
        ).columns.tolist()
        self.categorical_cols = X.select_dtypes(
            include=["object", "category"]
        ).columns.tolist()

        # Heuristic: long string columns → text
        self.text_cols = [
            col
            for col in self.categorical_cols
            if X[col].astype(str).str.len().mean() > 20
        ]

        # Remove text cols from categorical list
        self.categorical_cols = [
            col for col in self.categorical_cols if col not in self.text_cols
        ]
