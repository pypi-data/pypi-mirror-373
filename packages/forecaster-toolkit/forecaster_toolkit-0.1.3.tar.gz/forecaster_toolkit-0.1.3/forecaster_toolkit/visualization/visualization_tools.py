import matplotlib.pyplot as plt
import pandas as pd


def create_future_dates(series: pd.Series, horizon: int) -> pd.DatetimeIndex:
    """
    Create future dates for forecasting based on the series' frequency.

    Parameters
    ----------
    series : pd.Series
        Time series with datetime index
    horizon : int
        Number of future periods to create

    Returns
    -------
    pd.DatetimeIndex
        Future dates for forecasting

    Examples
    --------
    >>> dates = pd.date_range('2023-01-01', '2023-03-01', freq='MS')
    >>> series = pd.Series([1, 2, 3], index=dates)
    >>> future = create_future_dates(series, horizon=2)
    >>> print(future)
    DatetimeIndex(['2023-04-01', '2023-05-01'], freq='MS', dtype='datetime64[ns]')
    """
    last_timestamp = series.index[-1]  # Get the last timestamp
    freq = pd.infer_freq(series.index)  # Infer the frequency

    if freq is None:
        raise ValueError("Could not infer frequency from series index")

    # Create future dates starting after the last timestamp
    future_dates = pd.date_range(start=last_timestamp, periods=horizon + 1, freq=freq)[
        1:
    ]  # Exclude the start date

    return future_dates


def plot_forecast(
    series: pd.Series,
    predictions: pd.DataFrame,
    title: str = "Time Series Forecast",
) -> None:
    """
    Plot the forecasted values against the actual values with a vertical line
    separating historical data from predictions.

    Parameters
    ----------
    series : pd.Series
        Historical values with datetime index
    predictions : pd.DataFrame
        Predicted values
    """
    future_dates = create_future_dates(series, predictions.shape[0])

    plt.figure(figsize=(15, 5))

    # Plot historical data
    plt.plot(series.index, series.values, color="blue", label="Historical")

    # Plot predictions starting from the last historical point
    forecast_dates = pd.concat([pd.Series(series.index[-1]), pd.Series(future_dates)])
    forecast_values = pd.concat(
        [pd.Series(series.values[-1]), pd.Series(predictions.squeeze())]
    )
    plt.plot(forecast_dates, forecast_values, color="green", label="Forecast")

    # Add vertical line at the last historical date
    plt.axvline(x=series.index[-1], color="red", linestyle="--", label="Forecast Start")

    # Add legend
    plt.legend()

    # Add title and labels
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Value")

    plt.show()
