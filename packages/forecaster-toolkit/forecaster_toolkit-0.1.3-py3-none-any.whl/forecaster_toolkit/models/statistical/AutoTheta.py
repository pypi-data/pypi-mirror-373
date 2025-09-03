from typing import Optional, Union

import numpy as np
import pandas as pd
from statsforecast.models import AutoTheta

from forecaster_toolkit.models.statistical.StatisticalModel import StatisticalModel


class AutoThetaModel(StatisticalModel):
    """
    AutoThetaModel is a statistical model that uses the AutoTheta algorithm to forecast time series data.

    Attributes:
    -----------
    model : AutoTheta
        The model used to forecast the time series data.

    Methods:
    --------
    fit(self, X: Union[pd.DataFrame, pd.Series, np.ndarray]) -> None:
        Fit the model to the training data.
    predict(self, h: int, level: Optional[list[float]] = None, **kwargs) -> np.ndarray:
        Make predictions using the model.
    """

    def __init__(self, season_length: int, **kwargs):
        """
        Initialize the AutoTheta model.

        Parameters
        ----------
        season_length : int
            The season length of the time series
        **kwargs : dict
            Additional keyword arguments for the AutoTheta model
        """
        super().__init__()
        self.season_length = season_length
        self.model = AutoTheta(season_length=self.season_length, **kwargs)

    def fit(self, X: Union[pd.DataFrame, pd.Series, np.ndarray]) -> None:
        """
        Fit the model to the training data.

        Parameters
        ----------
        X : array-like
            Training input samples
        """
        if isinstance(X, (pd.DataFrame, pd.Series)):
            X = X.values
        X = np.asarray(X)

        # Fit the model
        super().fit(X)

    def predict(
        self, h: int, level: Optional[list[float]] = None, **kwargs
    ) -> np.ndarray:
        """
        Make predictions using the model.

        Parameters
        ----------
        h : int
            Number of steps to forecast
        level : list[float]
            The confidence levels for the prediction intervals
        **kwargs : dict
            Additional keyword arguments for the model

        Returns
        -------
        dict[str, np.ndarray]
            Predicted values stored in a dictionary
        """
        return super().predict(h, level, **kwargs)
