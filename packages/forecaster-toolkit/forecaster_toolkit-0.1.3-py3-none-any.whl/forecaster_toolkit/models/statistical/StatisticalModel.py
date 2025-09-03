from typing import Optional, Union

import numpy as np
import pandas as pd

from forecaster_toolkit.models.BaseModel import BaseModel


class StatisticalModel(BaseModel):
    """
    StatisticalModel is a base class for all statistical models.

    Attributes
    ----------
    model : Any
        The model

    Methods
    -------
    fit(self, X: Union[pd.DataFrame, pd.Series, np.ndarray]) -> None:
        Fit the model to the training data.
    predict(self, h: int, level: Optional[list[float]] = None, **kwargs) -> np.ndarray:
        Make predictions using the model.
    """

    def __init__(self) -> None:
        super().__init__()

    def fit(self, X: Union[pd.DataFrame, pd.Series, np.ndarray]) -> None:
        """
        Fit the model to the training data.

        Parameters
        ----------
        X : Union[pd.DataFrame, pd.Series, np.ndarray]
            The training data
        """
        if isinstance(X, pd.DataFrame):
            self.model.fit(X.values)
        elif isinstance(X, (pd.Series, np.ndarray)):
            self.model.fit(X)
        self.is_fitted = True

    def predict(
        self, h: int, level: Optional[list[float]] = None, **kwargs
    ) -> np.ndarray:
        """
        Make predictions using the model.

        Parameters
        ----------
        h : int
            The number of steps to forecast
        level : Optional[list[float]]
            The confidence level for the prediction intervals

        Returns
        -------
        np.ndarray
            Predicted values
        """
        return self.model.predict(h, level=level, **kwargs)
