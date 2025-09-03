from typing import Literal, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pymannkendall as mk
from coreforecast.seasonal import find_season_length
from plotly.subplots import make_subplots
from prophet import Prophet
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA, AutoETS, AutoTheta
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import acf, adfuller, kpss, pacf

from forecaster_toolkit.visualization._config import (
    conf_linelayout,
    my_figlayout,
    my_linelayout,
    split_linelayout,
)


class UnivariateAnalysis:
    """
    A class for performing univariate analysis on a time series. This class proposes
    multiple statistical tests to perform a deep and strong EDA (Exploratory Data Analysis).

    Attributs
    ---------

    data : pd.DataFrame
        The data to perfrom the univariate analysis on
    numeric_features : list[str]
        The numeric features of the data

    Methods
    -------
    perform_stationarity_test(feature: str) -> None:
        Perform the Augmented Dickey-Fuller test on a feature.

    perform_kpss_test(feature: str) -> None:
        Perform the KPSS test on a feature.

    perform_man_kendall_test(feature: str) -> None:
        Perform the non-parametric Mann-Kendall test on a feature.

    perform_auto_correlation_test(feature: str) -> None:
        Perform the auto-correlation test on a feature.

    plot_trend_over_raw(
        feature: str,
        slope: float,
        intercept: float,
        start_date: str,
        periods: int,
        freq: str,
    ) -> tuple[go.Figure, pd.Series]:
        Plot the trend over the raw data.

    plot_acf(features: Optional[list[str]] = None) -> list[go.Figure]:
        Plot the ACF of all numeric features in the data attribute.

    plot_histogram(features: Optional[list[str]] = None) -> list[go.Figure]:
        Plot the histogram of the given features.

    plot_boxplot(features: Optional[list[str]] = None) -> go.Figure:
        Plot the boxplot of the given features.

    detect_anomalies_STL_decomposition(feature: str) -> tuple[go.Figure, pd.Series]:
        Detect anomalies in the given feature using the Z-score method.

    detect_anomalies_isolation_forest(
        features: list[str],
        contamination: float = 0.05,
        random_state: int = 42,
    ) -> tuple[go.Figure, pd.Series]:
        Detect anomalies in the given features using the Isolation Forest method.
    """

    def __init__(self, data: pd.DataFrame):
        """
        Initialize the UnivariateAnalysis class.

        Arguments
        ---------
        data: pd.DataFrame
            The data to perform the univariate analysis on
        """
        self.data = data
        self.numeric_features = data.select_dtypes(include=[np.number]).columns

    def perform_stationarity_test(self, feature: str):
        """
        Perform the Augmented Dickey-Fuller test on a feature.
        This test is used to determine if a time series is stationary.
        If the p-value is less than 0.05, we can reject the null hypothesis
        and conclude that the time series is stationary.

        The two hypotheses are:
        - Null hypothesis (H0): The time series is non-stationary.
        - Alternative hypothesis (H1): The time series is stationary or trend-stationary.

        If the p-value is greater than 0.05, we fail to reject the null hypothesis
        and conclude that the time series is non-stationary.

        The method displays the ADF statistic for different significance levels. The more
        negative the statistic, the stronger the evidence against the null hypothesis.

        Arguments
        ---------
        feature: str
            The feature to perform the Augmented Dickey-Fuller test on
        """
        adf_result = adfuller(self.data[feature])
        print("Augmented Dickey-Fuller Test:")
        print(f"ADF Statistic: {adf_result[0]}")
        print(f"p-value: {adf_result[1]}")
        print("Critical values:")
        for key, value in adf_result[4].items():
            print(f"\t{key}: {value}")
        return adf_result

    def perform_kpss_test(self, feature: str):
        """
        Perform the KPSS test on a feature.
        This test is used to determine if a time series is stationary.
        If the p-value is less than 0.05, we can reject the null hypothesis
        and conclude that the time series is non-stationary.

        The two hypotheses are:
        - Null hypothesis (H0): The time series is trend-stationary or has a no unit root.
        - Alternative hypothesis (H1): The time series is non-stationary or series has unit root.

        A process has unit root if the autoregressive coefficient is 1 and therefore the process
        is ruled by the following equation:

        y_t = y_t-1 + epsilon_t

        where:
            - y_t is the value of the time series at time t
            - y_t-1 is the value of the time series at time t-1
            - epsilon_t is white noise

        Which is more or less the definition of a random walk.

        The method displays the KPSS statistic for different significance levels. The more
        positive the statistic, the stronger the evidence against the null hypothesis.
        """
        kpss_result = kpss(self.data[feature], regression="c", nlags="auto")
        print("KPSS Test:")
        print(f"KPSS Statistic: {kpss_result[0]}")
        print(f"p-value: {kpss_result[1]}")
        print("Critical values:")
        for key, value in kpss_result[3].items():
            print(f"\t{key}: {value}")

    def perform_man_kendall_test(self, feature: str):
        """
        Perform the non-parametric Mann-Kendall test on a feature.
        This test is used to determine wether a time series has a trend or not.

        The two hypotheses are:
        - Null hypothesis (H0): The time series has no trend.
        - Alternative hypothesis (H1): The time series has a trend.

        If the p-value is less than 0.05, we can reject the null hypothesis
        and conclude that the time series has a trend.
        """
        mk_result = mk.original_test(self.data[feature])
        print("Mann-Kendall Test:")
        has_trend = mk_result[1]

        if has_trend:
            print(f"Mann-Kendall Statistic: {mk_result[0]}")
            print(f"p-value: {mk_result[2]}")
        else:
            print("The time series has no trend.")

        return mk_result

    def perform_auto_correlation_test(self, feature: str):
        """
        Perform the auto-correlation test on a feature.
        This test is used to determine if a time series is auto-correlated.
        If the p-value is less than 0.05, we can reject the null hypothesis
        and conclude that the time series is auto-correlated.

        The two hypotheses are:
        - Null hypothesis (H0): The time series is not auto-correlated.
        - Alternative hypothesis (H1): The time series is auto-correlated.

        If the p-value is less than 0.05, we can reject the null hypothesis
        and conclude that the time series is auto-correlated.
        """
        acf_result = acf(self.data[feature])
        print("Auto-Correlation Test:")
        print(f"ACF Statistic: {acf_result[0]}")
        print(f"p-value: {acf_result[1]}")
        print("Critical values:")
        for key, value in acf_result[3].items():
            print(f"\t{key}: {value}")
        return acf_result

    def plot_trend_over_raw(
        self,
        feature: str,
        slope: float,
        intercept: float,
        start_date: str,
        periods: int,
        freq: str,
    ) -> tuple[go.Figure, pd.Series]:
        """
        Create a time series with given slope and intercept and plot it with Plotly

        Returns
        -------
        tuple[go.Figure, pd.Series]
            Plotly figure and the trend series
        """
        dates = pd.date_range(start=start_date, periods=periods, freq=freq)
        x = np.arange(periods)
        y = slope * x + intercept
        trend = pd.Series(y, index=dates)

        fig = go.Figure()

        # Add original data
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data[feature],
                mode="lines",
                name="Original",
                line={"color": "blue"},
            )
        )

        # Add trend line
        fig.add_trace(
            go.Scatter(
                x=trend.index,
                y=trend,
                mode="lines",
                name="Trend",
                line={"color": "red", "dash": "dash"},
            )
        )

        fig.update_layout(
            title=f"Time Series (slope={slope}, intercept={intercept})",
            xaxis_title="Date",
            yaxis_title="Value",
            legend={"yanchor": "top", "y": 0.99, "xanchor": "left", "x": 0.01},
            height=600,
            width=1000,
        )

        return fig, trend

    def plot_acf(
        self,
        features: Optional[list[str]] = None,
        nlags: int = 40,
        return_figs: bool = False,
    ) -> list[go.Figure]:
        """
        Plot the ACF of features using Plotly

        Parameters
        ----------
        features : Optional[list[str]]
            The list of the features names to perform the acf
        nlags : int
            The number of lags to use
        return_figs : bool
            Whether to return the go.Figure objects or not, default fals

        Returns
        -------
        list[go.Figure]
            List of Plotly figures for each feature
        """
        if features is None:
            features = self.numeric_features
        if isinstance(features, str):
            features = [features]

        confidence_interval = 1.96 / np.sqrt(len(self.data))

        figures = []
        for feature in features:
            acf_values = acf(self.data[feature], nlags=nlags)
            fig = go.Figure(layout=my_figlayout)
            fig.add_trace(go.Bar(x=list(range(nlags + 1)), y=acf_values, name="ACF"))
            fig.add_hline(
                y=confidence_interval,
                line=split_linelayout,
                name="95% Confidence Interval",
            )
            fig.add_hline(
                y=-confidence_interval, line=split_linelayout, showlegend=False
            )
            fig.update_layout(
                title="Autocorrelation Function (ACF)",
                xaxis_title="Lag",
                yaxis_title="Correlation",
                height=400,
                showlegend=True,
                yaxis_range=[-1, 1],
            )
            figures.append(fig)

        if return_figs:
            return figures

    def plot_pacf(
        self,
        features: Optional[list[str]] = None,
        nlags: int = 40,
        return_figs: bool = False,
    ):
        """
        Plot the ACF of features using Plotly

        Parameters
        ----------
        features : Optional[list[str]]
            The list of the features names to perform the acf
        nlags : int
            The number of lags to use
        return_figs : bool
            Whether to return the go.Figure objects or not, default fals

        Returns
        -------
        list[go.Figure]
            List of Plotly figures for each feature
        """
        if features is None:
            features = self.numeric_features
        if isinstance(features, str):
            features = [features]

        confidence_interval = 1.96 / np.sqrt(len(self.data))

        figures = []
        for feature in features:
            acf_values = pacf(self.data[feature], nlags=nlags)
            fig = go.Figure(layout=my_figlayout)
            fig.add_trace(go.Bar(x=list(range(nlags + 1)), y=acf_values, name="ACF"))
            fig.add_hline(
                y=confidence_interval,
                line=split_linelayout,
                name="95% Confidence Interval",
            )
            fig.add_hline(
                y=-confidence_interval, line=split_linelayout, showlegend=False
            )
            fig.update_layout(
                title="Autocorrelation Function (ACF)",
                xaxis_title="Lag",
                yaxis_title="Correlation",
                height=400,
                showlegend=True,
                yaxis_range=[-1, 1],
            )
            figures.append(fig)

        if return_figs:
            return figures

    def plot_histogram(self, features: Optional[list[str]] = None) -> list[go.Figure]:
        """
        Plot histograms using Plotly

        Returns
        -------
        list[go.Figure]
            List of Plotly figures for each feature
        """
        if features is None:
            features = self.numeric_features
        if isinstance(features, str):
            features = [features]

        figures = []
        for feature in features:
            fig = px.histogram(
                self.data,
                x=feature,
                nbins=len(self.data[feature].unique()),
                title=f"Histogram of {feature}",
            )

            fig.update_layout(height=500, width=800, showlegend=False)

            figures.append(fig)

        return figures

    def plot_boxplot(self, features: Optional[list[str]] = None) -> go.Figure:
        """
        Plot boxplots using Plotly

        Returns
        -------
        go.Figure
            Plotly figure containing boxplots
        """
        if features is None:
            features = self.numeric_features
        if isinstance(features, str):
            features = [features]

        fig = go.Figure()

        for feature in features:
            fig.add_trace(
                go.Box(y=self.data[feature], name=feature, boxpoints="outliers")
            )

        fig.update_layout(
            title="Boxplots of Features",
            yaxis_title="Value",
            height=600,
            width=1000,
            showlegend=False,
        )

        return fig

    def detect_anomalies_STL_decomposition(
        self, feature: str, return_figs: bool = False
    ) -> tuple[go.Figure, pd.Series]:
        """
        Detect anomalies using STL decomposition and plot with Plotly

        Returns
        -------
        tuple[go.Figure, pd.Series]
            Plotly figure and anomalies series
        """
        season_length = find_season_length(
            self.data[feature].values, max_season_length=52
        )
        decomposition = seasonal_decompose(
            self.data[feature].values, model="additive", period=season_length
        )

        # Calculate anomaly thresholds
        resid_mean = decomposition.resid[~np.isnan(decomposition.resid)].mean()
        resid_std = decomposition.resid[~np.isnan(decomposition.resid)].std()
        lower_bound = resid_mean - 3 * resid_std
        upper_bound = resid_mean + 3 * resid_std

        # Identify anomalies
        anomalies = (decomposition.resid < lower_bound) | (
            decomposition.resid > upper_bound
        )

        # Create a comprehensive plot with subplots
        fig = make_subplots(
            rows=4,
            cols=1,
            subplot_titles=("Original Data", "Trend", "Seasonal", "Residuals"),
            vertical_spacing=0.1,
        )

        # Original data
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=self.data[feature],
                name="Original Data",
                line=my_linelayout,
            ),
            row=1,
            col=1,
        )

        # Trend
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=decomposition.trend,
                name="Trend",
                line={"color": "green"},
            ),
            row=2,
            col=1,
        )

        # Seasonal
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=decomposition.seasonal,
                name="Seasonal",
                line={"color": "blue"},
            ),
            row=3,
            col=1,
        )

        # Residuals with anomaly bounds
        fig.add_trace(
            go.Scatter(
                x=self.data.index,
                y=decomposition.resid,
                name="Residuals",
                line={"color": "purple"},
            ),
            row=4,
            col=1,
        )

        # Add anomaly bounds
        fig.add_hline(y=lower_bound, line_dash="dash", line_color="red", row=4, col=1)

        fig.add_hline(y=upper_bound, line_dash="dash", line_color="red", row=4, col=1)

        # Highlight anomalies in residuals
        anomaly_points = self.data[anomalies]
        fig.add_trace(
            go.Scatter(
                x=anomaly_points.index,
                y=decomposition.resid[anomalies],
                mode="markers",
                name="Anomalies",
                marker={
                    "color": "red",
                    "size": 10,
                    "symbol": "x",
                },
            ),
            row=4,
            col=1,
        )

        # Update layout
        fig.update_layout(
            height=1000, showlegend=True, title_text="STL Decomposition Analysis"
        )

        if return_figs:
            return fig, anomalies
        else:
            return anomalies

    def plot_seasonal_decompose(
        self,
        target_column: str,
        return_fig: bool = False,
    ) -> go.Figure:
        decomposition = seasonal_decompose(self.data[target_column], model="additive")

        fig = go.Figure(layout=my_figlayout)

        # Plot 1: Time Series
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(x=self.data.index, y=self.data[target_column], mode="lines")
        )

        fig.update_layout(
            title="Time Series Plot",
            xaxis_title="Date",
            yaxis_title="Value",
            height=400,
        )

        fig.add_trace(
            go.Scatter(
                x=decomposition.trend.index,
                y=decomposition.trend.values,
                mode="lines",
                name="Trend",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=decomposition.seasonal.index,
                y=decomposition.seasonal.values,
                mode="lines",
                name="Seasonal",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=decomposition.resid.index,
                y=decomposition.resid.values,
                mode="lines",
                name="Residual",
            )
        )

        if return_fig:
            return fig

    def detect_anomalies_isolation_forest(
        self,
        features: list[str],
        contamination: float = 0.05,
        random_state: int = 42,
    ) -> tuple[go.Figure, pd.Series]:
        """
        Detect anomalies using Isolation Forest and plot with Plotly

        Returns
        -------
        tuple[go.Figure, pd.Series]
            Plotly figure and anomaly scores
        """
        isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=random_state,
        )

        isolation_forest.fit(self.data[features])
        self.data["anomaly"] = isolation_forest.predict(self.data[features])
        self.data["anomaly"] = self.data["anomaly"].map({1: 0, -1: 1})

        fig = go.Figure()

        # Add original data
        for feature in features:
            fig.add_trace(
                go.Scatter(
                    x=self.data.index,
                    y=self.data[feature],
                    mode="lines",
                    name=feature,
                    line={"color": "blue"},
                )
            )

        # Add anomaly points
        anomaly_points = self.data[self.data["anomaly"] == 1]
        for feature in features:
            fig.add_trace(
                go.Scatter(
                    x=anomaly_points.index,
                    y=anomaly_points[feature],
                    mode="markers",
                    name=f"{feature} Anomalies",
                    marker={"color": "red", "size": 10},
                )
            )

        fig.update_layout(
            title="Isolation Forest Anomaly Detection",
            xaxis_title="Date",
            yaxis_title="Value",
            height=800,
            width=1200,
            legend={"yanchor": "top", "y": 0.99, "xanchor": "left", "x": 0.01},
        )

        return fig, self.data["anomaly"]

    def detect_anomalies_kmeans(
        self,
        features: list[str],
        n_clusters: int = 3,
        random_state: int = 42,
    ) -> tuple[go.Figure, pd.Series]:
        """
        Detect anomalies using KMeans and plot with Plotly

        Returns
        -------
        tuple[go.Figure, pd.Series]
            Plotly figure and cluster assignments
        """
        kmeans = KMeans(
            n_clusters=n_clusters,
            random_state=random_state,
        )
        kmeans.fit(self.data[features])
        self.data["cluster"] = kmeans.predict(self.data[features])

        fig = go.Figure()

        # Add data points colored by cluster
        for cluster in range(n_clusters):
            cluster_data = self.data[self.data["cluster"] == cluster]
            for feature in features:
                fig.add_trace(
                    go.Scatter(
                        x=cluster_data.index,
                        y=cluster_data[feature],
                        mode="markers",
                        name=f"Cluster {cluster} - {feature}",
                        marker={"size": 10, "color": cluster, "colorscale": "Viridis"},
                    )
                )

        fig.update_layout(
            title="KMeans Clustering",
            xaxis_title="Date",
            yaxis_title="Value",
            height=800,
            width=1200,
            legend={"yanchor": "top", "y": 0.99, "xanchor": "left", "x": 0.01},
        )

        return fig, self.data["cluster"]

    def detect_anomalies_prophet(
        self,
        feature: Optional[list[str]],
        interval_width: float,
        changepoint_prior_scale: float,
        return_figs: bool = False,
    ):
        # Initialize and fit Prophet
        df_prophet = pd.DataFrame(
            {"ds": self.data.index, "y": self.data[feature]},
        ).reset_index()

        print(df_prophet)

        model = Prophet(
            interval_width=interval_width,
            changepoint_prior_scale=changepoint_prior_scale,
        )

        # Fit the model
        model.fit(df_prophet)

        # Make predictions
        forecast = model.predict(df_prophet)

        # Calculate residuals
        df_prophet["residual"] = df_prophet["y"] - forecast["yhat"]

        # Identify anomalies (points outside the prediction interval)
        anomalies = (df_prophet["y"] < forecast["yhat_lower"]) | (
            df_prophet["y"] > forecast["yhat_upper"]
        )

        # Create plot
        fig = go.Figure(layout=my_figlayout)

        # Add original data
        fig.add_trace(
            go.Scatter(
                x=df_prophet["ds"],
                y=df_prophet["y"],
                name="Original Data",
                line=my_linelayout,
            )
        )

        # Add prediction interval
        fig.add_trace(
            go.Scatter(
                x=df_prophet["ds"],
                y=forecast["yhat_upper"],
                name="Upper Bound",
                line=conf_linelayout,
                mode="lines",
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_prophet["ds"],
                y=forecast["yhat_lower"],
                name="Lower Bound",
                line=conf_linelayout,
                mode="lines",
                fill="tonexty",
                fillcolor="rgba(0,100,80,0.2)",
                showlegend=False,
            )
        )

        # Add predicted values
        fig.add_trace(
            go.Scatter(
                x=df_prophet["ds"],
                y=forecast["yhat"],
                name="Predicted",
                line={"color": "green"},
            )
        )

        # Add anomalies
        anomaly_points = df_prophet[anomalies]
        fig.add_trace(
            go.Scatter(
                x=anomaly_points["ds"],
                y=anomaly_points["y"],
                mode="markers",
                name="Anomalies",
                marker={
                    "color": "red",
                    "size": 10,
                    "symbol": "x",
                },
            )
        )

        if return_figs:
            return fig, anomalies
        else:
            return anomalies

    def detect_anomalies_stats(
        self,
        model_name: Literal["autoarima", "autoets", "autotetha"],
        feature: Optional[list[str]],
        confidence_interval: int = 99,
        return_figs: bool = False,
    ):
        # StatsForecast models
        model_map = {
            "autoarima": AutoARIMA,
            "autoets": AutoETS,
            "autotheta": AutoTheta,
        }

        df_stats = self.data.copy()
        df_stats.reset_index(inplace=True)
        df_stats.columns = ["ds", "y"]

        model = model_map[model_name](
            season_length=find_season_length(
                self.data[feature].values, max_season_length=52
            )
        )

        sf = StatsForecast(models=[model], freq="MS", n_jobs=-1)

        levels = [confidence_interval]

        df_stats["unique_id"] = "y"

        # Get both forecast and fitted values
        _ = sf.forecast(df=df_stats, h=12, level=levels, fitted=True)
        insample_forecasts = sf.forecast_fitted_values()

        # Identify anomalies (points outside the prediction interval)
        anomalies = ~insample_forecasts["y"].between(
            insample_forecasts[f"{model.__class__.__name__}-lo-{levels[0]}"],
            insample_forecasts[f"{model.__class__.__name__}-hi-{levels[0]}"],
        )

        anomalies_df = insample_forecasts[anomalies]

        # Create plot
        fig = go.Figure(layout=my_figlayout)

        # Add original data
        fig.add_trace(
            go.Scatter(
                x=insample_forecasts["ds"],
                y=insample_forecasts["y"],
                name="Original Data",
                line=my_linelayout,
            )
        )

        # Add prediction interval (using the fitted values)
        fig.add_trace(
            go.Scatter(
                x=insample_forecasts["ds"],
                y=insample_forecasts[
                    f"{model.__class__.__name__}-hi-{levels[0]}"
                ].values,
                name="Upper Bound",
                line=conf_linelayout,
                mode="lines",
                showlegend=False,
            )
        )

        fig.add_trace(
            go.Scatter(
                x=insample_forecasts["ds"],
                y=insample_forecasts[
                    f"{model.__class__.__name__}-lo-{levels[0]}"
                ].values,
                name="Lower Bound",
                line=conf_linelayout,
                mode="lines",
                fill="tonexty",
                fillcolor="rgba(0,100,80,0.2)",
                showlegend=False,
            )
        )

        # Add predicted values
        fig.add_trace(
            go.Scatter(
                x=insample_forecasts["ds"],
                y=insample_forecasts[f"{model.__class__.__name__}"],
                name="Predicted",
                line={"color": "green"},
            )
        )

        # Add anomalies
        fig.add_trace(
            go.Scatter(
                x=anomalies_df["ds"],
                y=anomalies_df["y"],
                mode="markers",
                name="Anomalies",
                marker={"color": "red", "size": 10, "symbol": "x"},
            )
        )

        # Update layout to ensure proper rendering of the prediction interval
        fig.update_layout(
            showlegend=True,
            hovermode="x unified",
            plot_bgcolor="white",
            paper_bgcolor="white",
            yaxis={
                "title": "Value",
                "showgrid": True,
                "gridcolor": "lightgray",
            },
            xaxis={
                "title": "Date",
                "showgrid": True,
                "gridcolor": "lightgray",
            },
        )

        if return_figs:
            return fig, anomalies
        else:
            return anomalies
