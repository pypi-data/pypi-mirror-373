from typing import ClassVar

from forecaster_toolkit.models.ml import (
    CatBoostModel,
    RandomForestModel,
    XGBoostModel,
)
from forecaster_toolkit.models.ml.MLModel import MLModel
from forecaster_toolkit.models.statistical import (
    AutoArimaModel,
    AutoCESModel,
    AutoETSModel,
    AutoThetaModel,
    ETSModel,
    ProphetModel,
)
from forecaster_toolkit.models.statistical.StatisticalModel import StatisticalModel


class MLModelFactory:
    """Factory class for creating ML models"""

    _models: ClassVar[dict[str, type[MLModel]]] = {
        "CatBoostModel": CatBoostModel,
        "RandomForestModel": RandomForestModel,
        "XGBoostModel": XGBoostModel,
    }

    @classmethod
    def get_models(cls) -> dict[str, type[MLModel]]:
        """Get the models"""
        return cls._models

    @classmethod
    def create(cls, model_name: str, **kwargs) -> MLModel:
        """Create a model instance by name"""
        if model_name not in cls._models:
            raise ValueError(
                f"Unknown model: {model_name}. Available models: {list(cls._models.keys())}"
            )
        return cls._models[model_name](**kwargs)


class StatisticalModelFactory:
    """Factory class for creating statistical models"""

    _models: ClassVar[dict[str, type[StatisticalModel]]] = {
        "AutoArimaModel": AutoArimaModel,
        "AutoETSModel": AutoETSModel,
        "AutoThetaModel": AutoThetaModel,
        "AutoCESModel": AutoCESModel,
        "ETSModel": ETSModel,
        "ProphetModel": ProphetModel,
    }

    @classmethod
    def get_models(cls) -> dict[str, type[StatisticalModel]]:
        """Get the models"""
        return cls._models

    @classmethod
    def create(cls, model_name: str, **kwargs) -> StatisticalModel:
        """Create a model instance by name"""
        if model_name not in cls._models:
            raise ValueError(
                f"Unknown model: {model_name}. Available models: {list(cls._models.keys())}"
            )
        return cls._models[model_name](**kwargs)
