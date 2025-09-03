from typing import Any


class BaseModel:
    """
    Base class for all models for time series forecasting.

    Attributes
    ----------
    is_fitted: bool
        Whether the model is fitted
    model_name: str
        The name of the model
    model: Any
        The model

    Methods
    -------
    fit(self, X: Union[pd.DataFrame, pd.Series, np.ndarray], **kwargs) -> None:
        Fit the model to the training data.
    predict(self, X: Union[pd.DataFrame, pd.Series, np.ndarray], h: int, **kwargs) -> np.ndarray:
        Make predictions using the model.
    """

    def __init__(self) -> None:
        self.is_fitted: bool = False
        self.model_name: str = self.__class__.__name__
        self.model: Any = None
