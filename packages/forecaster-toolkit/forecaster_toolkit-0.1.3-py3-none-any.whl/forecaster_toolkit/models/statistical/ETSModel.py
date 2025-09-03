from typing import Any, override

import numpy as np
import pandas as pd
from statsmodels.tsa.exponential_smoothing.ets import ETSModel

from forecaster_toolkit.models.statistical.StatisticalModel import StatisticalModel


class ErrorTrendSeasonalModel(StatisticalModel):
    """
    ErrorTrendSeasonalModel is a statistical model that uses the ETS algorithm to make predictions.

    Attributes
    ----------
    model : statsforecast.models.ETS
        The ETS model

    Methods
    -------
    fit(self, **kwargs) -> Any:
        Fit the model to the training data.
    predict(self, h: int, **kwargs) -> np.ndarray:
        Make predictions using the model.
    """

    def __init__(self, data_train: pd.DataFrame, **kwargs):
        super().__init__()
        self.model = ETSModel(data_train, **kwargs)

    @override
    def fit(self, **kwargs) -> Any:
        """
        Fit the model to the training data.

        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments for the model

        Returns
        -------
        ETSModel
            The fitted model
        """
        return self.model.fit(**kwargs)

    @override
    def predict(self, h: int, **kwargs) -> np.ndarray:
        """
        Make predictions using the fitted model.

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
        return self.model.forecast(steps=h, **kwargs)
