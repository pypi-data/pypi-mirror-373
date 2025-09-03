from typing import Union

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

from forecaster_toolkit.models.ml.MLModel import MLModel


class XGBoostModel(MLModel):
    def __init__(self, **kwargs):
        """
        Initialize the XGBoost model.

        Attributes
        ----------
        model : XGBRegressor
            The XGBoost model instance

        Methods
        -------
        fit(self, X: np.ndarray, y: np.ndarray) -> None:
            Fit the XGBoost model to the training data.
        predict(self, X: np.ndarray) -> np.ndarray:
            Make predictions using the fitted model.
        """
        super().__init__()
        self.model = XGBRegressor(**kwargs)

    def fit(
        self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]
    ) -> None:
        """
        Fit the model to the training data.

        Parameters
        ----------
        X : Union[pd.DataFrame, np.ndarray]
            Training input samples
        y : Union[pd.Series, np.ndarray]
            Target values
        """
        super().fit(X, y)

    def predict(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.Series, np.ndarray]:
        """
        Make predictions using the fitted model.

        Parameters
        ----------
        X : Union[pd.DataFrame, np.ndarray]
            Input samples

        Returns
        -------
        Union[pd.Series, np.ndarray]
            Predicted values

        Raises
        ------
        ValueError
            If the model is not fitted.
        """
        return super().predict(X=X)
