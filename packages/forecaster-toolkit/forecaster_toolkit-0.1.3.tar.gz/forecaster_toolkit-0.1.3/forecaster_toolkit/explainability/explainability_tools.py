from typing import Any, Literal, Optional

import lime
import lime.lime_tabular
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from catboost import CatBoostRegressor, Pool
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import PartialDependenceDisplay, permutation_importance
from xgboost import XGBRegressor


class ModelExplainer:
    """
    Class containing various methods for explaining model predictions

    Attributes
    ----------
    model : Any
        The model to explain

    Methods
    -------
    feature_importance_shap(self, X: np.ndarray, y: np.ndarray, feature_names: Optional[list[str]] = None) -> dict[str, np.ndarray]:
        Calculate SHAP (SHapley Additive exPlanations) values for feature importance
    lime_explanation(self, X: np.ndarray, feature_names: list[str], instance_index: int = 0) -> dict[str, Any]:
        Generate LIME (Local Interpretable Model-agnostic Explanations) for a specific instance
    permutation_importance(self, X: np.ndarray, y: np.ndarray, plot_mean: bool = True, n_repeats: int = 10, feature_names: Optional[list[str]] = None) -> dict[str, np.ndarray]:
        Calculate permutation importance scores for features
    partial_dependence_plot(self, X: np.ndarray, features: list[str], kind: Literal["average", "individual", "both"] = "average", centered: bool = True, **kwargs) -> None:
        Create partial dependence plot for a specific feature
    """

    def __init__(self, model: Any):
        """
        Initialize the ModelExplainer

        Parameters
        ----------
        model : Any
            The model to explain
        """
        self.model = model

    def feature_importance_shap(
        self, X: np.ndarray, y: np.ndarray, feature_names: Optional[list[str]] = None
    ) -> dict[str, np.ndarray]:
        """
        Calculate SHAP (SHapley Additive exPlanations) values for feature importance

        Parameters
        ----------
        X: np.ndarray
            Input data array
        y: np.ndarray
            Target values
        feature_names: Optional[list[str]]
            list of feature names

        Returns
        -------
        dict[str, np.ndarray]
            Dictionary containing SHAP values and summary plot
        """
        if isinstance(self.model, CatBoostRegressor):
            shap_values = self.model.get_feature_importance(
                Pool(X, y), type="ShapValues"
            )
        elif isinstance(self.model, (RandomForestRegressor, XGBRegressor)):
            explainer = shap.TreeExplainer(self.model)
            shap_values = explainer.shap_values(X)

        shap.summary_plot(shap_values[:, :-1], X, feature_names=feature_names)
        return {"shap_values": shap_values}

    def lime_explanation(
        self, X: np.ndarray, feature_names: list[str], instance_index: int = 0
    ) -> dict[str, Any]:
        """
        Generate LIME (Local Interpretable Model-agnostic Explanations) for a specific instance

        Parameters
        ----------
        X: np.ndarray
            Input data array
        feature_names: list[str]
            list of feature names
        instance_index: int
            Index of instance to explain

        Returns
        -------
        dict[str, Any]
            Dictionary containing LIME explanation
        """
        # Prepare the explainer
        explainer = lime.lime_tabular.LimeTabularExplainer(
            X.values,  # Ensure a NumPy array
            feature_names=feature_names,
            mode="regression",
            discretize_continuous=False,
        )

        # Explain a single instance
        exp = explainer.explain_instance(
            X.iloc[instance_index].values, self.model.predict
        )

        # Plot the explanation
        _ = exp.as_pyplot_figure()
        plt.show()

        return {"lime_explanation": exp}

    def permutation_importance(
        self,
        X: np.ndarray,
        y: np.ndarray,
        plot_mean: bool = True,
        n_repeats: int = 10,
        feature_names: Optional[list[str]] = None,
    ) -> dict[str, np.ndarray]:
        """
        Calculate permutation importance scores for features

        Parameters
        ----------
        X: np.ndarray
            Input data array
        y: np.ndarray
            Target values
        feature_names: list[str]
            list of feature names
        n_repeats: int
            Number of times to repeat the permutation

        Returns
        -------
        dict[str, np.ndarray]
            Dictionary containing importance scores
        """
        perm_importance = permutation_importance(
            self.model, X, y, n_repeats=n_repeats, random_state=42
        )

        plt.figure(figsize=(10, 6))
        plt.bar(
            X.columns if isinstance(X, pd.DataFrame) else feature_names,
            (
                perm_importance.importances_mean
                if plot_mean
                else perm_importance.importances_std
            ),
        )
        plt.xticks(rotation=45, ha="right")
        plt.title("Feature Importance (Permutation)")
        plt.xlabel("Features")
        plt.ylabel("Importance Score")
        plt.tight_layout()
        plt.show()

        return {"perm_importance": perm_importance}

    def partial_dependence_plot(
        self,
        X: np.ndarray,
        features: list[str],
        kind: Literal["average", "individual", "both"] = "average",
        centered: bool = True,
        **kwargs,
    ) -> None:
        """
        Create partial dependence plot for a specific feature

        Arguments
        ---------
        X: np.ndarray
            Input data array
        features: list[str]
            list of features to analyze
        kind: Literal["average", "individual", "both"]
            Kind of plot to create
        center: bool
            Whether to center the plot
        """
        PartialDependenceDisplay.from_estimator(
            self.model, X, features, kind=kind, centered=centered, **kwargs
        )
        plt.show()
