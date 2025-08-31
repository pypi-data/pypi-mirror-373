# PurnamaTools

**PurnamaTools** is a Python package designed to simplify data analysis and machine learning workflows, especially for beginners. It provides utilities for:

- Initial data inspection and validation
- Feature selection and correlation analysis
- Model evaluation for regression and classification

The package is intended to be continuously updated with new features and improvements.

## Features

### 1. Initial Data Check
- `initial_data_overview(df, target=None, is_classification=True)`: Comprehensive overview of your dataset, including missing values, duplicates, outliers, low variance columns, and more.
- `check_class_balance(df, target)`: Quickly check class imbalance and get recommendations for classification tasks.

### 2. Feature Selection
- `correlation_analysis(df, target, method='pearson')`: Identify strong correlations and potential redundant features.
- `mi_analysis(X, y)`: Select top features based on Mutual Information.
- `batch_rfe_feature_selection(X, y)`: Scalable Recursive Feature Elimination for datasets with many features.
- `sfs_feature_selection(X, y)`: Sequential Feature Selection (forward or backward) using any estimator.
- `lasso_feature_selection(X, y)`: Feature selection using Lasso regression.

### 3. Model Evaluation
- `evaluate_model_regression(model, X_train, y_train, X_test, y_test, scoring)`: Evaluate regression models and get guidance for overfitting or underfitting.
- `evaluate_model_classification(model, X_train, y_train, X_test, y_test, scoring)`: Evaluate classification models and get suggestions for handling class imbalance.

## Installation

```bash
pip install purnamatools
