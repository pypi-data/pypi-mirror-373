from typing import Optional, Union, override

import numpy as np
import pandas as pd
from statsforecast.models import AutoCES

from forecaster_toolkit.models.statistical.StatisticalModel import StatisticalModel


class AutoCESModel(StatisticalModel):
    """
    AutoCES model.

    Attributes
    ----------
    model : statsforecast.models.AutoCES
        The AutoCES model instance
    Methods
    -------
    fit(self, X: Union[pd.DataFrame, pd.Series, np.ndarray]) -> None:
        Fit the model to the training data.
    predict(self, h: int, level: Optional[list[float]] = None, **kwargs) -> np.ndarray:
        Make predictions using the model.
    """

    def __init__(self, season_length: int, **kwargs):
        """
        Initialize the AutoCES model.

        Parameters
        ----------
        season_length : int
            The season length of the time series
        **kwargs : dict
            Additional keyword arguments for the model
        """
        super().__init__()
        self.season_length = season_length
        self.model = AutoCES(season_length=self.season_length, **kwargs)

    @override
    def fit(self, X: Union[pd.DataFrame, pd.Series, np.ndarray]) -> None:
        """
        Fit the model to the training data.

        Parameters
        ----------
        X : Union[pd.DataFrame, pd.Series, np.ndarray]
            Training input samples
        """
        # Conversion to numpy array
        if isinstance(X, (pd.DataFrame, pd.Series)):
            X = X.values
        X = np.asarray(X)

        # Fit the model
        self.model.fit(X)
        self.is_fitted = True

    def predict(
        self, h: int, level: Optional[list[float]] = None, **kwargs
    ) -> np.ndarray:
        """
        Make predictions using the fitted model.

        Parameters
        ----------
        h : int
            Number of steps to forecast
        level : list[float]
            The confidence levels for the prediction intervals
        **kwargs
            Additional keyword arguments for the model
        Returns
        -------
        dict[str, np.ndarray]
            Predicted values stored in a dictionary
        """
        return super().predict(h, level, **kwargs)
