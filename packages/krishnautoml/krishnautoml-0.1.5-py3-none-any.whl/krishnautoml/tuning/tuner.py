import optuna
import numpy as np
from sklearn.model_selection import (
    cross_val_score,
    KFold,
    StratifiedKFold,
)
from sklearn.model_selection import train_test_split
import warnings

warnings.filterwarnings("ignore", category=UserWarning)


class Tuner:
    def __init__(self, n_trials=20, cv=5, use_optuna=True, random_state=42):
        self.n_trials = n_trials
        self.cv = cv
        self.use_optuna = use_optuna
        self.random_state = random_state

    def run(self, candidates, X, y, problem_type="auto"):
        """
        Train and tune models, return results + best model.
        candidates: dict {name: model_class}
        """
        results = {}
        best_score = -np.inf
        best_model = None

        cv_strategy = (
            StratifiedKFold(
                n_splits=self.cv, shuffle=True, random_state=self.random_state
            )
            if problem_type == "classification"
            else KFold(n_splits=self.cv, shuffle=True, random_state=self.random_state)
        )

        for name, model_cls in candidates.items():
            print(f"🔍 Tuning {name}...")

            if self.use_optuna:
                study = optuna.create_study(direction="maximize")
                study.optimize(
                    lambda trial: self._objective(
                        trial, model_cls, X, y, cv_strategy, problem_type
                    ),
                    n_trials=self.n_trials,
                )

                best_params = study.best_params
                # Pass random_state to the model constructor after Optuna finds the best params
                model = model_cls(**best_params, random_state=self.random_state)
            else:
                # fallback: grid search with default hyperparameters
                model = model_cls(random_state=self.random_state)

            # Final CV score with chosen params
            scoring = "accuracy" if problem_type == "classification" else "r2"
            scores = cross_val_score(model, X, y, cv=cv_strategy, scoring=scoring)
            mean_score = np.mean(scores)
            results[name] = {"score": mean_score}

            if mean_score > best_score:
                best_score = mean_score
                best_model = model.fit(X, y)

        print(f"🏆 Best model: {type(best_model).__name__} (CV={best_score:.4f})")
        return results, best_model

    def _objective(self, trial, model_cls, X, y, cv, problem_type):
        """
        Optuna objective function: sample hyperparams, return CV score.
        Currently supports LightGBM/XGBoost/RandomForest.
        """
        model_name = model_cls.__name__.lower()
        params = {}

        if "randomforest" in model_name:
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 50, 300),
                "max_depth": trial.suggest_int("max_depth", 3, 20),
            }

        # --- REVISED XGBOOST LOGIC ---
        elif "xgb" in model_name or "xgboost" in model_name:
            # Note: This is for older versions of XGBoost.
            # It uses deprecated parameters and is not recommended.
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 50, 300),
                "max_depth": trial.suggest_int("max_depth", 3, 15),
                "learning_rate": trial.suggest_float(
                    "learning_rate", 0.01, 0.3, log=True
                ),
                "subsample": trial.suggest_float("subsample", 0.5, 1.0),
                # Deprecated: use device='cuda' in new versions
                "tree_method": (
                    "gpu_hist"
                    if trial.suggest_categorical("use_gpu", [True, False])
                    else "auto"
                ),
                "verbosity": 0,  # Add this to suppress XGBoost warnings
            }

            if "eval_metric" in params:
                del params["eval_metric"]
            if "callbacks" in params:
                del params["callbacks"]

            model = model_cls(**params)

            # Split data for a single-fold validation within the trial
            X_train, X_val, y_train, y_val = train_test_split(
                X,
                y,
                test_size=0.2,
                random_state=self.random_state,
                stratify=y if problem_type == "classification" else None,
            )

            # Use deprecated early stopping parameters
            model.fit(
                X_train, y_train, eval_set=[(X_val, y_val)], verbose=False
            )  # Removed early_stopping_rounds and verbose

            # The way to get the best score for older versions might be different or not available,
            # so we fall back to a simple evaluation.
            if hasattr(model, "best_score_") and model.best_score_ is not None:
                return model.best_score_
            else:
                from sklearn.metrics import (
                    roc_auc_score,
                    r2_score,
                )

                y_pred = model.predict(X_val)
                if problem_type == "classification":
                    # For classification, return AUC for maximization
                    return roc_auc_score(y_val, y_pred)
                else:
                    # For regression, return R2 for maximization
                    return r2_score(y_val, y_pred)

        # --- REVISED LIGHTGBM LOGIC ---
        elif "lgbm" in model_name or "lightgbm" in model_name:
            # Build a dictionary for parameters, excluding 'use_gpu'.
            # We directly set the 'device' parameter based on the trial.
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 50, 300),
                "max_depth": trial.suggest_int("max_depth", -1, 20),
                "learning_rate": trial.suggest_float(
                    "learning_rate", 0.01, 0.3, log=True
                ),
                "subsample": trial.suggest_float("subsample", 0.5, 1.0),
                "min_gain_to_split": trial.suggest_float("min_gain_to_split", 0, 1.0),
                "verbose": -1,  # Suppress all warnings and informational output
            }

            # Conditionally add the device parameter to the dictionary
            params["device"] = "cpu"

            # Split data for a single-fold validation within the trial
            X_train, X_val, y_train, y_val = train_test_split(
                X,
                y,
                test_size=0.2,
                random_state=self.random_state,
                stratify=y if problem_type == "classification" else None,
            )

            model = model_cls(**params)

            # Use 'auc' for pruning metric since we are maximizing
            pruning_metric = "auc" if problem_type == "classification" else "l1"

            # The 'eval_metric' parameter tells LightGBM which metrics to compute
            if problem_type == "classification":
                eval_metric = [pruning_metric, "binary_logloss"]
            else:
                eval_metric = [pruning_metric, "l2"]

            # Fit the model with early stopping callbacks
            model.fit(
                X_train,
                y_train,
                eval_set=[(X_val, y_val)],
                eval_metric=eval_metric,
                callbacks=[
                    optuna.integration.LightGBMPruningCallback(trial, pruning_metric)
                ],
            )

            # The get the best score, we access the booster and then its evaluation history
            booster = model.booster_
            eval_results = booster.best_score

            # Return the best score from the evaluation set for the specified metric
            return eval_results["valid_0"][pruning_metric]

        else:
            # default for simple models
            pass

        # Add random_state to parameters if the model supports it
        if "random_state" in model_cls.__init__.__code__.co_varnames:
            params["random_state"] = self.random_state

        # Existing cross_val_score logic for other models
        model = model_cls(**params)
        scoring = "accuracy" if problem_type == "classification" else "r2"
        scores = cross_val_score(model, X, y, cv=cv, scoring=scoring)
        return np.mean(scores)
