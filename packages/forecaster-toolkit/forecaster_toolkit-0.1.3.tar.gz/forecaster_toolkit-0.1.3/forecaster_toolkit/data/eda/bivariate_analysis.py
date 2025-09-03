from typing import Optional, Union

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler
from statsmodels.formula.api import ols
from statsmodels.tsa.stattools import ccovf
from tqdm import tqdm


class BivariateAnalysis:
    """
    A class for performing bivariate analysis on a time series. This class proposes
    multiple statistical tests to perform a deep and strong EDA (Exploratory Data Analysis).

    Attributes
    ---------
    data : pd.DataFrame
        The data to perform the bivariate analysis on
    numeric_features : pd.DataFrame
        Non categorical features

    Methods
    -------
    plot_correlation_matrix() -> go.Figure
        Plot the correlation matrix of the numeric features.

    plot_cross_correlation_matrix() -> go.Figure
        Plot the cross-correlation matrix of the numeric features.

    plot_covariance_matrix() -> go.Figure
        Plot the covariance matrix of the numeric features.

    plot_cross_covariance_matrix() -> go.Figure
        Plot the cross-covariance matrix of the numeric features.

    perform_anova_numeric_categorical(cat_cols: Union[str, list[str]]) -> tuple[go.Figure, pd.DataFrame]
        Perform ANOVA (Analysis of Variance) between numerical and categorical variables using Fisher's F-statistic.
    """

    def __init__(
        self, data: pd.DataFrame, numeric_features: Optional[list[str]] = None
    ):
        self.data = data.copy()
        if numeric_features is None:
            numeric_features = self.data.select_dtypes(include=[np.number]).columns
        self.numeric_features = numeric_features

    def plot_correlation_matrix(self) -> go.Figure:
        """
        Plot the correlation matrix of the numeric features.

        Returns
        -------
        go.Figure
            Plotly figure containing the correlation matrix heatmap
        """
        corr_matrix = self.data.loc[:, self.numeric_features].corr()

        fig = go.Figure(
            data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.index,
                colorscale="RdBu",
                zmin=-1,
                zmax=1,
                text=corr_matrix.round(2).values,
                texttemplate="%{text}",
                textfont={"size": 10},
                colorbar={"title": "Correlation"},
            )
        )

        fig.update_layout(
            title="Correlation Matrix",
            xaxis_title="Features",
            yaxis_title="Features",
            width=800,
            height=800,
            xaxis={"tickangle": 45},
            yaxis={"tickangle": 0},
            margin={"l": 100, "r": 100, "t": 100, "b": 100},
        )

        return fig

    def plot_cross_correlation_matrix(self) -> go.Figure:
        """
        Plot the cross-correlation matrix of the numeric features.

        Returns
        -------
        go.Figure
            Plotly figure containing the cross-correlation matrix heatmap
        """
        cross_corr = self.data.loc[:, self.numeric_features].corr()

        fig = go.Figure(
            data=go.Heatmap(
                z=cross_corr.values,
                x=cross_corr.columns,
                y=cross_corr.index,
                colorscale="RdBu",
                zmin=-1,
                zmax=1,
                text=cross_corr.round(2).values,
                texttemplate="%{text}",
                textfont={"size": 10},
                colorbar={"title": "Cross-Correlation"},
            )
        )

        fig.update_layout(
            title="Cross-Correlation Matrix",
            xaxis_title="Features",
            yaxis_title="Features",
            width=800,
            height=800,
            xaxis={"tickangle": 45},
            yaxis={"tickangle": 0},
            margin={"l": 100, "r": 100, "t": 100, "b": 100},
        )

        return fig

    def plot_covariance_matrix(self) -> go.Figure:
        """
        Plot the covariance matrix of the numeric features.

        Returns
        -------
        go.Figure
            Plotly figure containing the covariance matrix heatmap
        """
        cov_matrix = self.data.loc[:, self.numeric_features].cov()

        fig = go.Figure(
            data=go.Heatmap(
                z=cov_matrix.values,
                x=cov_matrix.columns,
                y=cov_matrix.index,
                colorscale="RdBu",
                text=cov_matrix.round(2).values,
                texttemplate="%{text}",
                textfont={"size": 10},
                colorbar={"title": "Covariance"},
            )
        )

        fig.update_layout(
            title="Covariance Matrix",
            xaxis_title="Features",
            yaxis_title="Features",
            width=800,
            height=800,
            xaxis={"tickangle": 45},
            yaxis={"tickangle": 0},
            margin={"l": 100, "r": 100, "t": 100, "b": 100},
        )

        return fig

    def plot_cross_covariance_matrix(self) -> go.Figure:
        """
        Plot the cross-covariance matrix of the numeric features.

        Returns
        -------
        go.Figure
            Plotly figure containing the cross-covariance matrix heatmap
        """
        cross_cov = ccovf(self.data.loc[:, self.numeric_features].to_numpy())

        fig = go.Figure(
            data=go.Heatmap(
                z=cross_cov,
                x=self.numeric_features,
                y=self.numeric_features,
                colorscale="RdBu",
                text=np.round(cross_cov, 2),
                texttemplate="%{text}",
                textfont={"size": 10},
                colorbar={"title": "Cross-Covariance"},
            )
        )

        fig.update_layout(
            title="Cross-Covariance Matrix",
            xaxis_title="Features",
            yaxis_title="Features",
            width=800,
            height=800,
            xaxis={"tickangle": 45},
            yaxis={"tickangle": 0},
            margin={"l": 100, "r": 100, "t": 100, "b": 100},
        )

        return fig

    def perform_anova_numeric_categorical(
        self, cat_cols: Union[str, list[str]]
    ) -> tuple[go.Figure, pd.DataFrame]:
        """
        Perform ANOVA (Analysis of Variance) between numerical and categorical variables
        using Fisher's F-statistic.

        Arguments
        ---------
        cat_cols : Union[str, list[str]]
            List of categorical column names to include in the ANOVA analysis.

        Returns
        -------
        Tuple[go.Figure, pd.DataFrame]
            The Plotly figure object of the ANOVA heatmap and the DataFrame containing ANOVA results.
        """
        if isinstance(cat_cols, str):
            cat_cols = [cat_cols]

        # Check if the columns exist in the DataFrame
        missing_columns = [col for col in cat_cols if col not in self.data.columns]
        if missing_columns:
            raise ValueError(
                f"The following columns are not in the DataFrame: {missing_columns}"
            )

        # Create a copy of the data to avoid modifying the original
        data_copy = self.data.copy()

        # Standardize numerical data
        std_scaler = StandardScaler()
        numerical_feature_list_std = []
        for num in self.numeric_features:
            data_copy[num + "_std"] = std_scaler.fit_transform(
                data_copy[num].to_numpy().reshape(-1, 1)
            )
            numerical_feature_list_std.append(num + "_std")

        # Perform ANOVA for each combination of numerical and categorical variables
        rows = []
        total_combinations = len(cat_cols) * len(numerical_feature_list_std)

        with tqdm(total=total_combinations, desc="Performing ANOVA") as pbar:
            for cat in cat_cols:
                col = []
                for num in numerical_feature_list_std:
                    try:
                        equation = f"{num} ~ C({cat})"
                        model = ols(equation, data=data_copy).fit()
                        anova_table = sm.stats.anova_lm(model, typ=1)
                        col.append(anova_table.loc[f"C({cat})"]["F"])
                    except Exception as e:
                        print(f"Error in ANOVA for {num} ~ {cat}: {e!s}")
                        col.append(np.nan)
                    pbar.update(1)
                rows.append(col)

        # Store the results in a DataFrame
        anova_result = np.array(rows)
        anova_result_df = pd.DataFrame(
            anova_result, columns=self.numeric_features, index=cat_cols
        )

        # Create a Plotly heatmap
        fig = go.Figure(
            data=go.Heatmap(
                z=anova_result_df.values,
                x=anova_result_df.columns,
                y=anova_result_df.index,
                colorscale="plasma",
                text=np.round(anova_result_df.values, 2),
                texttemplate="%{text}",
                textfont={"size": 10},
                colorbar={"title": "Fisher's F-statistic"},
            )
        )

        # Update layout
        fig.update_layout(
            title="Fisher's Statistic Heatmap",
            xaxis_title="Numerical Features",
            yaxis_title="Categorical Features",
            width=800,
            height=800,
            xaxis={"tickangle": 45},
            yaxis={"tickangle": 0},
            margin={"l": 100, "r": 100, "t": 100, "b": 100},
        )

        return fig, anova_result_df
