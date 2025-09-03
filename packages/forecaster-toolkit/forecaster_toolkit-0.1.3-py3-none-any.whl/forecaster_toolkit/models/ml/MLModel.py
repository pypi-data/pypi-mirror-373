from typing import Union

import numpy as np
import pandas as pd

from forecaster_toolkit.models.BaseModel import BaseModel


class MLModel(BaseModel):
    """
    MLModel is a base class for all machine learning models.

    Attributes
    ----------
    model : Any
        The model instance

    Methods
    -------
    fit(self, X: Union[pd.DataFrame, pd.Series, np.ndarray], y: Union[pd.Series, np.ndarray]) -> None:
        Fit the model to the training data.
    predict(self, X: Union[pd.DataFrame, pd.Series, np.ndarray], **kwargs) -> np.ndarray:
        Make predictions using the fitted model.
    """

    def __init__(self):
        """
        Initialize the MLModel.
        """
        super().__init__()

    def fit(
        self,
        X: Union[pd.DataFrame, pd.Series, np.ndarray],
        y: Union[pd.Series, np.ndarray],
    ) -> None:
        """
        Fit the model to the training data.

        Parameters
        ----------
        X : Union[pd.DataFrame, pd.Series, np.ndarray]
            The training data
        y : Union[pd.Series, np.ndarray]
            The target values
        """
        self.model.fit(X, y)
        self.is_fitted = True

    def predict(
        self, X: Union[pd.DataFrame, pd.Series, np.ndarray], **kwargs
    ) -> np.ndarray:
        """
        Make predictions using the fitted model.

        Parameters
        ----------
        X : Union[pd.DataFrame, pd.Series, np.ndarray]
            The data to make predictions on
        **kwargs : dict
            Additional keyword arguments for the model

        Returns
        -------
        np.ndarray
            The predicted values
        """
        if not self.is_fitted:
            raise ValueError("Model is not fitted yet. Please call fit() method first.")
        return self.model.predict(X, **kwargs)
