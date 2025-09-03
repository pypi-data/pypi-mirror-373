from typing import Union

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from forecaster_toolkit.models.ml.MLModel import MLModel


class RandomForestModel(MLModel):
    """
    Random Forest model

    Attributes
    ----------
    model : RandomForestRegressor
        The Random Forest model instance

    Methods
    -------
    fit(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]) -> None:
        Fit the Random Forest model
    predict(self, X: Union[pd.DataFrame, np.ndarray]) -> Union[pd.Series, np.ndarray]:
        Predict the target variable
    """

    def __init__(self, **kwargs):
        """
        Initialize the Random Forest model

        Parameters
        ----------
        **kwargs : dict
            Additional keyword arguments for the Random Forest model
        """
        super().__init__()
        self.model = RandomForestRegressor(**kwargs)

    def fit(
        self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]
    ) -> None:
        """
        Fit the Random Forest model

        Parameters
        ----------
        X : Union[pd.DataFrame, np.ndarray]
            The features
        y : Union[pd.Series, np.ndarray]
            The target variable
        """
        super().fit(X, y)

    def predict(
        self, X: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.Series, np.ndarray]:
        """
        Predict the target variable

        Parameters
        ----------
        X : Union[pd.DataFrame, np.ndarray]
            The features

        Returns
        -------
        Union[pd.Series, np.ndarray]
            The predicted target variable
        """
        return super().predict(X)
