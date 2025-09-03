from typing import Union

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor

from forecaster_toolkit.models.ml.MLModel import MLModel


class CatBoostModel(MLModel):
    def __init__(self, **kwargs):
        """
        Initialize the CatBoost model.

        The CatBoost model is a gradient boosting model that uses the CatBoost algorithm to forecast time series data.

        Attributes
        ----------
        model : CatBoostRegressor
            The CatBoost model instance

        Methods
        -------
        fit(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]) -> None:
            Fit the model to the training data.
        predict(self, X: Union[pd.DataFrame, np.ndarray]) -> Union[pd.Series, np.ndarray]:
            Make predictions using the fitted model.
        """
        super().__init__()
        self.model = CatBoostRegressor(**kwargs)

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
