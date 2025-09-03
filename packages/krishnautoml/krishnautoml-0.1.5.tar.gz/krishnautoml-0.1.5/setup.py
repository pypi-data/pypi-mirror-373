from setuptools import setup, find_packages

setup(
    name="krishnautoml",
    version="0.1.5",
    description="AutoML pipeline for classification and regression",
    author="Krish",
    license="MIT",
    packages=find_packages(include=["krishnautoml", "krishnautoml.*"]),
    include_package_data=True,
    install_requires=[
        "pandas",
        "numpy",
        "scikit-learn",
        "matplotlib",
        "seaborn",
        "jinja2",
        "joblib",
        "optuna",
    ],
    entry_points={
        "console_scripts": [
            "krishnautoml=krishnautoml.cli:main",
        ]
    },
    python_requires=">=3.7",
)
