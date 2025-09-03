from typing import Union

import numpy as np
import pandas as pd
from prophet import Prophet

from forecaster_toolkit.models.statistical.StatisticalModel import StatisticalModel


class ProphetModel(StatisticalModel):
    """
    Prophet model.
    """

    def __init__(self, **kwargs):
        """
        Initialize the Prophet model.
        """
        # Set default changepoint_prior_scale if not provided
        if "changepoint_prior_scale" not in kwargs:
            kwargs["changepoint_prior_scale"] = 0.05

        # Set default n_changepoints if not provided
        if "n_changepoints" not in kwargs:
            kwargs["n_changepoints"] = 25

        self.model = Prophet(**kwargs)

    def fit(self, df: Union[pd.DataFrame, pd.Series, np.ndarray]) -> None:
        """
        Fit the model to the training data.

        Parameters
        ----------
        df : Union[pd.DataFrame, pd.Series, np.ndarray]
            The training data. If a Series or ndarray is provided, it will be converted
            to a DataFrame with a datetime index.
        """
        # Convert input to DataFrame if it's a Series or ndarray
        if isinstance(df, (pd.Series, np.ndarray)):
            df = pd.DataFrame(df)

        # Create a copy to avoid modifying the original data
        df_prophet = df.copy()

        # Reset index and rename columns for Prophet
        df_prophet = df_prophet.reset_index()
        df_prophet.columns = ["ds", "y"]

        # Adjust n_changepoints based on data length
        n_points = len(df_prophet)
        if n_points < self.model.n_changepoints:
            self.model.n_changepoints = max(1, n_points // 2)

        # Fit the model
        self.model.fit(df_prophet)

    def predict(
        self,
        h: int,
    ) -> Union[np.ndarray, pd.DataFrame]:
        """
        Make predictions using the model.

        Parameters
        ----------
        h : int
            The forecast horizon.
        level : Optional[list[float]]
            The confidence level(s) for the prediction intervals.
        **kwargs
            Additional keyword arguments to pass to the model's predict method.

        Returns
        -------
        Union[np.ndarray, pd.DataFrame]
            The predicted values. If level is provided, returns a DataFrame with mean and confidence intervals.
            Otherwise, returns a numpy array of predictions.
        """
        # Create future dates for prediction
        future = self.model.make_future_dataframe(periods=h)

        # Make predictions
        forecast = self.model.predict(future)

        # Get only the forecasted values
        predictions = forecast.iloc[-h:]

        result = pd.DataFrame(
            {
                "mean": predictions["yhat"],
                "lower": predictions["yhat_lower"],
                "upper": predictions["yhat_upper"],
            }
        )
        return result
