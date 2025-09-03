from functools import wraps
from typing import Literal, Optional, Union

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_validate
from xgboost import XGBRegressor

from forecaster_toolkit.data.feature_engineering.time_features import (
    extend_time_series_for_prediction,
)
from forecaster_toolkit.models.ml.MLModel import MLModel
from forecaster_toolkit.models.model_selection import hyperparameter_opt
from forecaster_toolkit.models.model_selection._base_configs import BASE_PARAM_GRID
from forecaster_toolkit.models.model_selection._model_factory import (
    MLModelFactory,
    StatisticalModelFactory,
)
from forecaster_toolkit.models.statistical.StatisticalModel import StatisticalModel
from forecaster_toolkit.splitter import Splitter, SplitterCV
from forecaster_toolkit.visualization import plot_forecast


def compute_rmse(
    y_true: Union[pd.DataFrame, pd.Series, np.ndarray],
    y_pred: Union[pd.DataFrame, pd.Series, np.ndarray],
) -> float:
    """
    Compute the RMSE

    Parameters
    ----------
    y_true : np.ndarray
        The true values
    y_pred : np.ndarray
        The predicted values

    Returns
    -------
    float
        The RMSE
    """
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


def compute_mae(
    y_true: Union[pd.DataFrame, pd.Series, np.ndarray],
    y_pred: Union[pd.DataFrame, pd.Series, np.ndarray],
) -> float:
    """
    Compute the MAE

    Parameters
    ----------
    y_true : np.ndarray
        The true values
    y_pred : np.ndarray
        The predicted values

    Returns
    -------
    float
        The MAE
    """
    return np.mean(np.abs(y_true - y_pred))


def compute_mape(
    y_true: Union[pd.DataFrame, pd.Series, np.ndarray],
    y_pred: Union[pd.DataFrame, pd.Series, np.ndarray],
) -> float:
    """
    Compute the MAPE

    Parameters
    ----------
    y_true : np.ndarray
        The true values
    y_pred : np.ndarray
        The predicted values

    Returns
    -------
    float
        The MAPE
    """
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


def compute_mse(
    y_true: Union[pd.DataFrame, pd.Series, np.ndarray],
    y_pred: Union[pd.DataFrame, pd.Series, np.ndarray],
) -> float:
    """
    Compute the MSE

    Parameters
    ----------
    y_true : np.ndarray
        The true values
    y_pred : np.ndarray
        The predicted values

    Returns
    -------
    float
        The MSE
    """
    return compute_rmse(y_true, y_pred) ** 2


def compute_r2(
    y_true: Union[pd.DataFrame, pd.Series, np.ndarray],
    y_pred: Union[pd.DataFrame, pd.Series, np.ndarray],
) -> float:
    """
    Compute the R2

    Parameters
    ----------
    y_true : np.ndarray
        The true values
    y_pred : np.ndarray
        The predicted values

    Returns
    -------
    float
        The R2
    """
    return 1 - (
        np.sum((y_true - y_pred) ** 2) / np.sum((y_true - np.mean(y_true)) ** 2)
    )


def compute_metrics(
    y_true: Union[pd.DataFrame, pd.Series, np.ndarray],
    y_pred: Union[pd.DataFrame, pd.Series, np.ndarray],
    metrics: list[str],
) -> list[float]:
    """
    Compute all metrics

    Parameters
    ----------
    y_true : np.ndarray
        The true values
    y_pred : np.ndarray
        The predicted values

    Returns
    -------
    dict[str, float]
        The metrics [rmse, mae, mape, mse, r2]
    """
    callable_metrics = {
        "rmse": compute_rmse,
        "mae": compute_mae,
        "mape": compute_mape,
        "mse": compute_mse,
        "r2": compute_r2,
    }
    metrics_dict = {}
    for metric in metrics:
        if metric in callable_metrics:
            metrics_dict[metric] = callable_metrics[metric](y_true, y_pred)
        else:
            raise ValueError(f"Metric {metric} not found")
    return metrics_dict


def _compute_exponential_avg_weights(
    data: Union[pd.Series, pd.DataFrame, np.ndarray], lambda_exp: float
) -> float:
    """
    Compute exponential weighted average of a list of values.
    More recent values have higher weights.

    Parameters
    ----------
    data : Union[pd.Series, pd.DataFrame, np.ndarray]
        The values to compute the exponential average on
    lambda_exp : float
        The lambda value for the exponential weights (between 0 and 1)
        Higher values give more weight to recent observations

    Returns
    -------
    float
        The exponential weighted average

    Examples
    --------
    >>> data = [1, 2, 3, 4]
    >>> _compute_exponential_avg_weights(data, lambda_exp=0.3)
    3.0843...  # Plus récentes valeurs (3,4) ont plus de poids
    """
    # Convert input to numpy array
    # Use simple position indices
    positions = np.arange(len(data))

    # Compute exponential weights
    weights = np.exp(lambda_exp * positions)
    weights = weights / np.sum(weights)  # Normalize weights

    # Compute weighted average
    return np.sum(data * weights)


def check_index(func):
    """Decorator to ensure DataFrame has a datetime index"""

    @wraps(func)
    def wrapper(self, df, *args, **kwargs):
        # Convert Series to DataFrame if needed
        if isinstance(df, pd.Series):
            df = df.to_frame()

        if not isinstance(df.index, pd.DatetimeIndex):
            print("Index is not a datetime index, trying to find a datetime column")
            datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

            if not datetime_cols:
                raise ValueError(
                    f"Did not find a datetime column in the data, data must have a datetime index or column. Got index type: {type(df.index)}"
                )

            df = df.set_index(datetime_cols[0])
            print(f"Set {datetime_cols[0]} as index")

        return func(self, df, *args, **kwargs)

    return wrapper


class ModelSelectionCV:
    """
    Class to perform model selection using cross validation.
    The main objective is to find the best model and the best hyperparameters for a given model.

    Note that hyperparameter optimization is performed implicitly for statistical models.
    For ML models, the default hyperparameters are used. If you want to perform a stronger hyperparameter optimization,
    you can use the `hyperparameter_opt` function on the first hand and pass the best model to the `model_list` argument
    to compare the models with the best hyperparameters.

    Attributes:
    -----------
    data : pd.DataFrame
        The data to fit the models on
    metrics : list[str]
        The metrics to evaluate the models on
    scoring_map : dict[str, str]
        The mapping between our metrics and sklearn scoring names
    models : pd.DataFrame
        The models to compare
    normalize : Optional[Literal["standard", "minmax"]]
        The normalization method to use
    kwargs : dict
        Additional keyword arguments to pass to the models

    Methods
    -------
    __init__(model_list: Union[list[str], list[object], list[tuple[str, object]]], normalize: Optional[Literal["standard", "minmax"]] = None, metrics: Optional[list[str]] = None)
        Initialize the ModelSelectionCV object.

    instantiate_models(model_list: list[str, object, tuple[str, object]], **kwargs) -> pd.DataFrame
        Instantiate the models.

    add_model(model: Union[str, object], model_name: Optional[str] = None) -> None
        Add a model to the list of models.

    fit_models() -> None
        Fit the models on the data.

    cross_validation_exp_avg(lambda_exp: float, target_column: str, cv: int = 5, plot: Optional[bool] = False, forecast_horizon: Optional[int] = 3) -> object
        Performs cross validation to evaluate the fitted models.

    get_summary() -> pd.DataFrame
        Get a summary of the models.

    fit(data: Union[pd.DataFrame, pd.Series], lambda_exp: float, target_column: str, plot: Optional[bool] = False, forecast_horizon: Optional[int] = 3) -> tuple[object, pd.DataFrame, pd.DataFrame]
        Perform model selection on the provided data
    """

    def __init__(
        self,
        model_list: Union[list[str], list[object], list[tuple[str, object]]],
        normalize: Optional[Literal["standard", "minmax"]] = None,
        metrics: Optional[list[str]] = None,
        splitter: Optional[str] = "expandingwindowsplitter",
        **kwargs,
    ):
        """
        Initialize the ModelSelectionCV object.

        Parameters
        ----------
        model_list : list[str]
            The list of models to compare
        normalize : Optional[Literal["standard", "minmax"]]
            The normalization method to use
        metrics : list[str]
            The metrics to evaluate the models on
        kwargs : dict
            Additional keyword arguments to pass to the models
        """
        self.metrics = (
            ["rmse", "mae", "mape", "mse", "r2"] if metrics is None else metrics
        )
        self.scoring_map = {
            "rmse": "neg_root_mean_squared_error",
            "mae": "neg_mean_absolute_error",
            "mse": "neg_mean_squared_error",
            "mape": "neg_mean_absolute_percentage_error",
            "r2": "r2",
        }
        self.normalize = normalize
        self.kwargs = kwargs
        self.models = model_list
        self.summary = None
        self.splitter = Splitter(method=splitter)

    def instantiate_models(
        self,
        model_list: list[str, object, tuple[str, object]],
        n_folds: int,
        **kwargs: dict,
    ) -> pd.DataFrame:
        """
        Instantiate the models

        Parameters
        ----------
        model_list : list[str, object, tuple[str, object]]
            The list containing the names of the models to instantiate or pre-instantiated models
            or already fitted models
        kwargs : dict
            Additional keyword arguments to pass to the models

        Returns
        -------
        pd.DataFrame
            DataFrame containing the instantiated models and their metadata to be stored in the ModelSelectionCV object

        Raises
        ------
        ValueError
            If the model is not found within the statistical or ml modules
        """
        # Create a list to store the model data
        model_data = []

        # Process each model in the model_list
        for model in model_list:
            fold_metrics = {f"fold_{j}": {} for j in range(n_folds)}

            try:
                # Handle different input types
                if isinstance(model, str):
                    model_name = model
                    if model in MLModelFactory.get_models():
                        estimator = MLModelFactory.create(model, **kwargs)
                    elif model in StatisticalModelFactory.get_models():
                        estimator = StatisticalModelFactory.create(model, **kwargs)
                    else:
                        raise ValueError(f"Unknown model: {model}")
                elif isinstance(model, tuple):
                    model_name, estimator = model
                else:
                    # For pre-instantiated model objects
                    model_name = model.__class__.__name__
                    estimator = model

                # Create a dictionary for this model's data
                model_info = {
                    "model_name": model_name,
                    "estimator": estimator,
                    "global_error": None,
                    "metric_per_fold": fold_metrics,
                    "avg_metric_per_fold": {
                        f"exp_avg_{metric}": None for metric in self.metrics
                    },
                }
                model_data.append(model_info)
            except KeyError as e:
                raise KeyError(f"Model {model} not found") from e

        # Create and return the DataFrame
        return pd.DataFrame(model_data)

    def add_model(
        self, model: Union[str, object], model_name: Optional[str] = None
    ) -> None:
        """
        Add a model to the list of models

        Parameters
        ----------
        model : Union[str, object]
            The model to add to the list of models
        model_name : Optional[str]
            The name of the model

        Raises
        ------
        ValueError
            If the model is not found within the statistical or ml modules
        """

        if isinstance(model, str):
            if model in MLModelFactory.get_models():
                self.summary.append(
                    [model, MLModelFactory.create(model, **self.kwargs)]
                )
            elif model in StatisticalModelFactory.get_models():
                self.summary.append(
                    [model, StatisticalModelFactory.create(model, **self.kwargs)]
                )
            else:
                raise ValueError(f"Unknown model: {model}")
        else:
            self.summary.append([model_name, model])

    def fit_models(self) -> None:
        """
        Fit the models on the data
        """
        # Fit the models
        for i in self.summary.index:
            self.summary.iloc[i, 1] = self.summary.iloc[i, 1].fit(self._data)

    def cross_validation_exp_avg(
        self,
        lambda_exp: float,
        target_column: str,
        plot: Optional[bool] = False,
        forecast_horizon: Optional[int] = 3,
    ):
        """
        Performs cross validation to evaluate the fitted models.

        Parameters
        ----------
        lambda_exp : float
            The lambda value for the exponential weights
        target_column : str
            The column to fit the models on for the statistical models and the target column for the ML models
        plot : bool
            Whether to plot the forecast for each model
        forecast_horizon : int
            The forecast horizon

        Returns
        -------
        object
            The best model in the sense of the lowest global error
        """
        self.splitter = self.splitter.fit(df=self._data)
        splits = self.splitter.get_splits()

        self.summary = self.instantiate_models(
            model_list=self.models, n_folds=len(splits)
        )

        cv = SplitterCV(self.splitter)

        for index, row in self.summary.iterrows():
            model = row["estimator"]
            fold_metrics = {f"fold_{i}": {} for i in range(len(splits))}

            try:
                if isinstance(model, StatisticalModel):
                    # Statistical model handling
                    print(f"Processing model {row['model_name']}")
                    for i, (X_train, X_test) in enumerate(splits):
                        print(f"Processing fold {i}")
                        # For statistical models, we need to pass the target column values
                        if not hasattr(model, "is_fitted"):
                            model.model.history = None
                        model.fit(X_train[target_column].values)
                        predictions = model.predict(h=len(X_test))

                        metrics = compute_metrics(
                            X_test[target_column].values,
                            predictions["mean"],
                            self.metrics,
                        )
                        fold_metrics[f"fold_{i}"] = metrics

                    if plot:
                        # Fit the model on the whole dataset
                        model.fit(self._data[target_column].values)

                        # Predict the future values
                        predictions = model.predict(h=len(self._data))

                        # Plot the forecast
                        plot_forecast(
                            series=self._data[target_column],
                            predictions=predictions["mean"],
                            title=f"Forecast for {row['model_name']}",
                        )

                elif isinstance(
                    model,
                    (
                        MLModel,
                        CatBoostRegressor,
                        RandomForestRegressor,
                        XGBRegressor,
                    ),
                ):
                    # ML model handling
                    X = self._data
                    y = self._data[target_column]

                    if not model.is_fitted:
                        best_model, _ = hyperparameter_opt(
                            model=model,
                            time_series=X,
                            param_grid=BASE_PARAM_GRID[model.__class__.__name__],
                            target_name=target_column,
                            splitter=cv,
                        )
                        # Extract the base estimator from the sktime forecaster
                        if hasattr(best_model, "estimator_"):
                            best_model = best_model.estimator_
                        elif hasattr(best_model, "estimator"):
                            best_model = best_model.estimator

                    # Fit the model
                    best_model.fit(X.drop(columns=[target_column]), y)
                    self.summary.at[index, "estimator"] = best_model

                    scores = cross_validate(
                        estimator=best_model,
                        X=X,
                        y=y,
                        scoring=[self.scoring_map[metric] for metric in self.metrics],
                        cv=cv,
                        return_estimator=True,
                    )

                    # Process scores
                    for metric in self.metrics:
                        metric_key = self.scoring_map[metric]
                        metric_values = -scores[f"test_{metric_key}"]
                        for fold_idx, value in enumerate(metric_values):
                            fold_metrics[f"fold_{fold_idx}"][metric] = value

                    if plot:
                        # Extend the time series for prediction
                        try:
                            extended_data = extend_time_series_for_prediction(
                                self._data.drop(columns=[target_column]),
                                nb_periods=forecast_horizon,
                            )

                            # Predict the future values
                            predictions = model.predict(extended_data)

                            # Plot the forecast
                            plot_forecast(
                                series=self._data[target_column],
                                predictions=predictions,
                                title=f"Forecast for {row['model_name']}",
                            )
                        except ValueError as e:
                            print(
                                f"Error extending the time series for prediction: {e!s}"
                                f"The model {row['model_name']} cannot be plotted"
                            )
                            continue

                # Update metrics in the DataFrame
                self.summary.at[index, "metric_per_fold"] = fold_metrics

                # Compute exponential averages
                avg_metrics = {}
                for metric in self.metrics:
                    metric_values = [
                        fold_metrics[f"fold_{i}"][metric] for i in range(len(splits))
                    ]
                    avg_metrics[f"exp_avg_{metric}"] = _compute_exponential_avg_weights(
                        data=metric_values, lambda_exp=lambda_exp
                    )

                self.summary.at[index, "avg_metric_per_fold"] = avg_metrics
                self.summary.at[index, "global_error"] = np.mean(
                    list(avg_metrics.values())
                )

            except Exception as e:
                print(f"Error processing model {row['model_name']}: {e}")
                import traceback

                traceback.print_exc()
                # Set high error value for failed models
                self.summary.at[index, "global_error"] = float("inf")
                continue

        # Return the model with the lowest error
        best_idx = self.summary["global_error"].idxmin()
        return self.summary.loc[best_idx]["estimator"]

    def get_summary(self) -> pd.DataFrame:
        """
        Get a summary of the models

        Returns
        -------
        pd.DataFrame
            A summary of the models with their global error and their metrics per fold
        """
        return self.summary

    @check_index
    def fit(
        self,
        df: Union[pd.DataFrame, pd.Series],
        lambda_exp: float,
        target_column: str,
        plot: Optional[bool] = False,
        forecast_horizon: Optional[int] = 3,
    ) -> tuple[object, pd.DataFrame, pd.DataFrame]:
        """
        Perform model selection on the provided data

        Parameters
        ----------
        data : Union[pd.DataFrame, pd.Series]
            The data to perform model selection on
        lambda_exp : float
            Lambda parameter for exponential weighting
        target_column : str
            Target column name
        plot : bool
            Whether to plot the forecast for each model
        forecast_horizon : int
            The forecast horizon

        Returns
        -------
        tuple[object, pd.DataFrame, pd.DataFrame]
            - The best model
            - The predictions from the best model
            - Summary of all models' performance
        """
        # Store data temporarily for the cross-validation process
        self._data = df
        self._data["values"] = self._data[target_column]

        # Perform the cross validation
        best_model = self.cross_validation_exp_avg(
            lambda_exp=lambda_exp,
            target_column=target_column,
            plot=plot,
            forecast_horizon=forecast_horizon,
        )

        # Fit the best model on the whole dataset
        if isinstance(best_model, StatisticalModel):
            best_model.fit(self._data[target_column])
        else:
            best_model.fit(
                X=self._data.drop(columns=[target_column]), y=self._data[target_column]
            )

        # Clean up temporary data
        del self._data

        return best_model, self.get_summary()
