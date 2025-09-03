# Forecaster Toolkit

[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style - Black](https://img.shields.io/badge/Code%20Style-Black-000000.svg)](https://github.com/psf/black)

A comprehensive Python library for time series forecasting that combines statistical and machine learning approaches with advanced feature engineering and data preprocessing capabilities. The library embarks also the possibility to perform model selection betweem statistical and machine learning models using cross-validation and hyperparameter tuning for machine learning models. Utils methods to make forecast plots are provided.

## Table of Contents

1. [Installation](#installation)
2. [Modules Overview](#modules-overview)
3. [Usage Examples](#examples)
3.1. [Data](#data-examples---preprocess-and-feature-engineering)
3.2. [Model selection](#model-selection-examples)
3.3. [Explainability](#explainability-examples)
4. [Solve Common Problems](#solve-common-problems)

## Installation

Since this library is not yet published on PyPI, you need to install it from source.

### Requirements
- Python 3.12+
- All the requirements are specified in the pyproject.toml file

I suggest you create a virtual environnememt on the first hand : 

```bash
source .venv/bin/activate
```

Then run development install :

```bash
poetry install
```

or :

```bash
pip install -e .
```

If you want to use this library in another folder than this one, simply keep this virtual environnement activated and move in another folder, it will keep the library installed. 

#### Verify installation
```bash
python -c "import forecaster_toolkit; print(forecaster_toolkit.__version__)
```

## Usage

This library automates time series forecasting tasks with a focus on combining statistical and machine learning approaches. It includes several packages designed to address the main steps in any time series forecasting task:

1. **Feature Engineering**: Accessible through `feature_engineering` module. This package provides comprehensive time-based feature generation and engineering functionality.
2. **Model Selection**: The `model_selection` module enables automated model selection and evaluation for statistical and machine learning models.
3. **Model Explainability**: The `explainability` module offers various tools for understanding model predictions.
4. **Data Preprocessing**: The `preprocess` module handles data preparation and clustering capabilities.


### Modules Overview

- **Data Feature Engineering Module**: 
  - Automatic generation of time-based features:
    - Lag features with customizable periods
    - Rolling statistics (mean, standard deviation)
    - Exponential moving averages
    - Calendar features (month, quarter, year, week, weekday)
    - Percentage changes and growth rates
  - Automatic feature extension for forecasting (ML models specific)
  - Automatic detection of extensible features
  - Time series specific transformations

- **Model Selection Module**:
  - Automated model selection using cross-validation
  - Support for both statistical and machine learning models:
    - Statistical Models: ARIMA, ETS, CES, Theta
    - Machine Learning Models: CatBoost, Random Forest, XGBoost
  - Exponentially weighted evaluation metrics 
  - Built-in performance metrics (RMSE, MAE, MAPE, MSE, R²)
  - Hyperparameter optimization capabilities

- **Model Explainability Module**:
  - SHAP (SHapley Additive exPlanations) values
  - LIME (Local Interpretable Model-agnostic Explanations)
  - Permutation importance analysis
  - Partial dependence plots
  - Feature importance visualization

- **Data Preprocessing Module**:
  - Clustering capabilities for time series
  - Automated feature mapping
  - Time series specific preprocessing
  - Data transformation utilities

### Examples

#### Data examples - preprocess and feature engineering

```python
import pandas as pd

from forecaster_toolkit.data.preprocess.preprocess_tools import TimeSeriesPreprocessor

from forecaster_toolkit.data.feature_engineering import (
    add_pct_change,
    add_lags,
    add_lag_ratios,
    add_rolling_mean,
    add_rolling_std,
    add_exponential_moving_average,
)

# Can be parquet, or csv, or xcl files, adapt the 2 following lines accordingly
parquet_path = "path/to/your/data"

df = pd.read_parquet(parquet_path)

TSPreprocessor = TimeSeriesPreprocessor(freq="freq_of_your_data")

df_processed = TSPreprocessor.fill_missing_values(df=df, cols_name="column_you_want_to_process")

print(f"Cleaned {len(df) - len(df_processed)} duplicate rows")

df_features = add_lags(
  df=df_processed, 
  lags=[3,6,12]
)

df_features = add_rolling_mean(
  df=df_features,
  column="target_column_lag_X"
  window=6
)

# Add the features you want

# Save your dataframe
df_features.to_csv("path")
```

#### Model selection examples

```python
import pandas as pd

from forecaster_toolkit.models.model_selection import (
  ModelSelectionCV,
  hyperparameter_opt
)

from forecaster_toolkit.models.ml import (
  CatBoostModel,
  RandomForestModel,
)

df_features = pd.read_csv("path/to/your/data")

catBoost = CatBoostModel(
    iterations=50,
    learning_rate=0.01,
    random_seed=63,
    silent=True,
)

# Check for your ML models that the features you want to use can be extended to predict the future values
_, _, features_to_remove = find_extensible_features(df=df_features, nb_periods=3)

features_to_remove.remove("your_true_value")

# Get the extension of your dataset, on which you will infer the future values
df_extended = extend_time_series_for_prediction(
    df=df_features.drop(columns=features_to_remove), nb_periods=3
)

param_grid = {
    "iterations": [50, 100, 200],
    "learning_rate": [0.01, 0.05, 0.1],
    "depth": [4, 6, 8],
    "l2_leaf_reg": [1, 3, 5, 7],
    "random_strength": [1, 3, 5],
}

best_catboost, best_params = hyperparameter_opt(
    model="CatBoostModel",
    time_series=df_features.drop(columns=features_to_remove),
    param_grid=param_grid,
    target_name="nb_cs",
    cv=5,
    silent=True,
)

randomForest = RandomForestModel()

param_grid = {
    "max_depth": [3, 5, 7],
    "n_estimators": [100, 200, 300],
    "bootstrap": [True, False],
}

best_rdf, best_params = hyperparameter_opt(
    model="RandomForestModel",
    time_series=df_features.drop(columns=features_to_remove),
    param_grid=param_grid,
    target_name="nb_cs",
    cv=5,
)

# Perform model selection between statistical and machine learning models
model_selection = ModelSelectionCV(
    model_list=[
        AutoArimaModel(season_length=52),
        AutoETSModel(season_length=52),
        AutoThetaModel(season_length=52),
        AutoCESModel(season_length=52),
        AutoArimaModel(season_length=26),
        AutoETSModel(season_length=26),
        AutoThetaModel(season_length=26),
        AutoCESModel(season_length=26),
        best_catboost,
        best_rdf,
    ],
    data=df_features.drop(columns=features_to_remove),
    metrics=["rmse", "mae", "mape"],
    cv=5,
    season_length=12,
)

best_model = model_selection.perform_model_selection(
    target_column="nb_cs", lambda_exp=0.9, cv=5
)

# Get the summary of the model selection process
summary = model_selection.get_summary()

# Get the best model at the sense of the least important global_error
summary.sort_values(by="global_error")
```

#### Explainability examples

```python
import pandas as pd
import numpy as np
from forecaster_toolkit.explainability.explainability_tools import ModelExplainer
from forecaster_toolkit.models.ml import CatBoostModel

# Load your data and train a model
df_features = pd.read_csv("path/to/your/data")
target_column = "your_target"

# Train a model (example with CatBoost)
model = CatBoostModel(iterations=100, learning_rate=0.1)
X = df_features.drop(columns=[target_column])
y = df_features[target_column]
model.fit(X, y)

# Initialize the explainer
explainer = ModelExplainer(model)

# 1. SHAP Values Analysis
shap_values = explainer.feature_importance_shap(
    X=X,
    y=y,
    feature_names=X.columns.tolist()
)
# This will display a SHAP summary plot showing feature importance and impact

# 2. LIME Explanation for a specific prediction
lime_exp = explainer.lime_explanation(
    X=X,
    feature_names=X.columns.tolist(),
    instance_index=0  # Explain the first instance
)
# This will show how different features contributed to a specific prediction

# 3. Permutation Importance
perm_importance = explainer.permutation_importance(
    X=X,
    y=y,
    n_repeats=10,
    feature_names=X.columns.tolist(),
    plot_mean=True
)
# This will display a bar plot of feature importance based on permutation

# 4. Partial Dependence Plots
# Choose the most important features based on previous analyses
important_features = ["feature1", "feature2"]
explainer.partial_dependence_plot(
    X=X,
    features=important_features,
    kind="both",  # Shows both average and individual effects
    centered=True
)
# This will show how the model's predictions change as feature values vary
```

## Solve common problems

### Index is not a pd.DatetimeIndex

```python
# If you have a datetime column in your dataframe
pd.set_index("columm_of_type_pd.DatetimeIndex")

# If not
full_date_range = pd.date_range(
  start="start_date",
  end="end_date"
  periods=len("your_dataframe"),
  freq="freq_of_your_observations",
)
```

### ValueError - number of columns are not equal (extend_time_series method)

```python
# You should remove the observed feature from the columns to remove 
#
# _, _, features_to_remove = find_extensible_features(df_features, nb_periods=X)
#
# Please do the following :

features_to_remove_copy = features_to_remove.copy()

features_to_remove_copy.remove("target_column")

df_extended = extend_time_series_for_prediction(
  df=df_features.drop(columns=features_to_remove_copy)
  ....
)

# You can use it after like this :
model_selection = ModelSelectionCV(
  model_list=[...]
  data=df_features.drop(columns=features_to_remove_copy)
)

best_model = model_selection.perform_model_selection(
  target_column="target_column",
  ....
)
```