from typing import override

import numpy as np
import pandas as pd
import pmdarima

from forecaster_toolkit.models.statistical.StatisticalModel import StatisticalModel


class ArimaModel(StatisticalModel):
    """
    ArimaModel is a statistical model that uses the Arima algorithm to forecast time series data.

    Attributes
    ----------
    model : pmdarima.arima.ARIMA
        The ARIMA model instance

    Methods
    -------
    fit(self, **kwargs) -> None:
        Fit the model to the training data.
    predict(self, h: int, **kwargs) -> np.ndarray:
        Make predictions using the model.
    """

    def __init__(self, X: pd.DataFrame, **kwargs):
        """
        Initialize the ARIMA model.

        Parameters
        ----------
        X : pd.DataFrame
            The training data
        """
        super().__init__()
        self.model = pmdarima.auto_arima(X, **kwargs)

    @override
    def fit(self, **kwargs) -> None:
        """
        Fit the model to the training data.

        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments for the model
        """
        return self.model.fit(**kwargs)

    @override
    def predict(self, h: int, **kwargs) -> np.ndarray:
        """
        Make predictions using the model.

        Parameters
        ----------
        h : int
            Number of steps to forecast
        **kwargs : dict
            Additional keyword arguments for the model

        Returns
        -------
        dict[str, np.ndarray]
            Predicted values stored in a dictionary
        """
        return self.model.predict(n_periods=h, **kwargs)
