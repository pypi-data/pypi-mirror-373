# KrishnAutoML

[![PyPI version](https://img.shields.io/pypi/v/krishnautoml.svg)](https://pypi.org/project/krishnautoml/)
[![Build Status](https://github.com/knight22-21/KrishnAutoML/actions/workflows/ci.yaml/badge.svg)](https://github.com/knight22-21/KrishnAutoML/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**KrishnAutoML** is a lightweight, beginner-friendly, and production-ready **AutoML library** for **tabular data**.  
It automates the end-to-end machine learning workflow with **minimal user input**, while keeping things modular and extensible.

---

## Features

- Load data from CSV or Pandas DataFrame  
- Automatic problem type detection (classification or regression)  
- Smart preprocessing (missing values, categorical encoding, scaling)  
- Optional EDA reports for insights  
- Train multiple models (LightGBM, XGBoost, CatBoost, Scikit-Learn)  
- Automated model selection and hyperparameter tuning (Optuna / GridSearchCV)  
- Flexible cross-validation (KFold, StratifiedKFold, GroupKFold)  
- Multiple evaluation metrics dynamically  
- Early stopping and GPU support  
- Save models + reproducible pipeline code  
- Auto-generated reports in HTML/Markdown  

---

## Installation

From PyPI (after publishing):
```bash
pip install krishnautoml
````

From source:

```bash
git clone https://github.com/knight22-21/KrishnAutoML.git
cd KrishnAutoML
pip install -e .[dev]
```

---

## Quick Start

### Python API

```python
from krishnautoml import KrishnAutoML

# Initialize AutoML
automl = KrishnAutoML(target="Survived", problem_type="auto")

# Full pipeline
(
    automl
    .load_data("data/titanic.csv")
    .preprocess()
    .train_models()
    .evaluate()
    .save_model("best_model.pkl")
)

print("Best model metrics:", automl.best_score)
```

### Command Line Interface (CLI)

```bash
krishnautoml fit --data data/titanic.csv --target Survived --report
```

This will:

* Train models
* Save `best_model.pkl`
* Generate an HTML performance report

---

## Example Output

**Metrics (Classification example):**

```python
{'accuracy': 0.8567, 'precision': 0.8421, 'recall': 0.8312, 'f1': 0.8350}
```

**Generated Report:**

* Confusion matrix
* Feature importance
* ROC-AUC curve
* Summary of preprocessing steps

---

## Advanced Usage

* Custom cross-validation:

```python
automl = KrishnAutoML(target="SalePrice", cv_strategy="KFold", n_splits=10)
```

* Specify metrics:

```python
automl = KrishnAutoML(target="Survived", metrics=["accuracy", "f1"])
```

* Load trained model:

```python
from joblib import load
model = load("best_model.pkl")
```

---

## Development

Clone and install dev dependencies:

```bash
git clone https://github.com/knight22-21/KrishnAutoML.git
cd KrishnAutoML
pip install -e .[dev]
```

Run tests:

```bash
pytest
```

Lint & format:

```bash
flake8 krishnautoml
black krishnautoml
```

---

## License

MIT License © 2025 \Krishna Tyagi

---

## Contributing

Contributions are welcome!

* Fork the repo
* Create a feature branch
* Submit a PR

---

## Acknowledgements

* [scikit-learn](https://scikit-learn.org)
* [XGBoost](https://xgboost.ai)
* [LightGBM](https://lightgbm.readthedocs.io)
* [CatBoost](https://catboost.ai)
* [Optuna](https://optuna.org)