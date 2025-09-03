from typing import Any, Union

import pandas as pd
from sklearn.base import is_regressor
from sktime.forecasting.compose import make_reduction
from sktime.forecasting.model_selection import ForecastingGridSearchCV
from sktime.performance_metrics.forecasting import MeanAbsoluteError
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.exponential_smoothing.ets import ETSModel

from forecaster_toolkit.models.ml.MLModel import MLModel
from forecaster_toolkit.models.model_selection._model_factory import (
    MLModelFactory,
    StatisticalModelFactory,
)
from forecaster_toolkit.models.statistical.StatisticalModel import StatisticalModel
from forecaster_toolkit.splitter import SplitterCV


def hyperparameter_opt(
    model: Union[MLModel, StatisticalModel, str],
    time_series: pd.DataFrame,
    param_grid: dict,
    target_name: str,
    splitter: SplitterCV,
    **kwargs,
) -> tuple[Any, dict[str, Any]]:
    """
    Perform hyperparameter tuning for a given Machine Learning model.

    Parameters
    ----------
    model : Union[MLModel, str]
        The model instance or name of the model to tune.
    time_series : pd.DataFrame
        The time series to tune the model on.
    param_grid : dict
        The parameter grid to search over.
    target_name : str
        Name of the target variable column.
    scoring : Union[str, list[str]]
        Scoring metric(s) to use for evaluation.
    cv : int
        The number of cross-validation folds.
    **kwargs
        Additional keyword arguments to pass to the model initialization.

    Returns
    -------
    tuple[Any, dict[str, Any]]
        The best estimator found and its parameters.
    """
    if isinstance(model, str):
        if model in MLModelFactory.get_models():
            model = MLModelFactory.create(model, **kwargs)
        elif model in StatisticalModelFactory.get_models():
            model = StatisticalModelFactory.create(model, **kwargs)
        else:
            raise ValueError(f"Unknown model: {model}")

    if not is_regressor(model.model):
        raise ValueError("Model must be a scikit-learn regressor")

    # Create the reduced model for time series forecasting
    reduced_model = make_reduction(
        estimator=model.model, window_length=10, strategy="recursive"
    )

    # Adjust parameter grid for the reduced model
    reduced_param_grid = {f"estimator__{k}": v for k, v in param_grid.items()}

    grid_search = ForecastingGridSearchCV(
        forecaster=reduced_model,
        param_grid=reduced_param_grid,
        cv=splitter,
        refit=True,  # Suggested to be set to False if working with a large dataset
        scoring=MeanAbsoluteError(),
        verbose=1,
    )

    # Fit with the forecasting horizon
    grid_search.fit(
        X=time_series.drop(columns=[target_name]),
        y=time_series[target_name],
    )

    print(f"Best estimator: {grid_search.best_forecaster_}")
    print(f"Best parameters found within the grid: {grid_search.best_params_}")

    return grid_search.best_forecaster_, grid_search.best_params_


def hyperparameter_opt_statistical(
    model_name: str,
    time_series: pd.DataFrame,
    season_lengths: list[int],
) -> dict[str, Any]:
    """
    Perform hyperparameter tuning for a given Statistical model.
    This method performs a grid search over the season lengths to choose the
    the bestand returns the metrics for each season length.

    AIC = Akaike Information Criterion = -2 * log(L) + 2k
    BIC = Bayesian Information Criterion = -2 * log(L) + k * log(n)
    HQIC = Hannan-Quinn Information Criterion = -2 * log(L) + 2k * log(log(n))

    L = likelihood of the model
    k = number of parameters
    n = number of observations

    The lower the AIC, BIC, and HQIC, the better the model because they penalize the number of parameters
    and the number of observations used to fit the model.

    Parameters
    ----------
    model_name : str
        The name of the model to tune.
    time_series : pd.DataFrame
        The time series to tune the model on.
    season_lengths : list[int]
        The season lengths to tune the model on.
    """
    model_correspondance = {
        "ETS": ETSModel,
        "ARIMA": ARIMA,
    }

    if model_name not in model_correspondance:
        raise ValueError(
            f"Unknown model: {model_name}, please choose from {model_correspondance.keys()}"
        )

    metrics = {}

    for season_length in season_lengths:
        model = model_correspondance[model_name](
            time_series, season_length=season_length
        )
        results = model.fit()

        metrics[season_length] = {
            "aic": results.aic,
            "bic": results.bic,
            "hqic": results.hqic,
        }

    return metrics
