import re
from typing import Optional

import pandas as pd


def add_rolling_mean(df: pd.DataFrame, column: str, window: int) -> pd.DataFrame:
    """
    Add rolling mean of a column

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the data
    column : str
        Name of the column to compute rolling mean from
    window : int
        Window size for the rolling mean

    Returns
    -------
    pd.DataFrame
        DataFrame with additional rolling mean feature

    Examples
    --------
    >>> df = pd.DataFrame({'sales': [100, 120, 80, 95, 150, 140]})
    >>> df = add_rolling_mean(df, 'sales', 3)
    >>> print(df)
       sales      rolling_mean
    0    100               Nan
    1    120               Nan
    2     80             100.0
    3     95            98.333
    4    150           108.333
    5    140           108.333
    """
    df = df.copy()
    df[f"{column}_rolling_mean_{window}"] = df[column].rolling(window=window).mean()
    return df


def add_rolling_std(df: pd.DataFrame, column: str, window: int) -> pd.DataFrame:
    """
    Add rolling standard deviation of a column

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the data
    column : str
        Name of the column to compute rolling standard deviation from
    window : int
        Window size for the rolling standard deviation

    Returns
    -------
    pd.DataFrame
        DataFrame with additional rolling standard deviation feature

    Examples
    --------
    >>> df = pd.DataFrame({'sales': [100, 120, 80, 95, 150, 140]})
    >>> df = add_rolling_std(df, 'sales', 3)
    >>> print(df)
       sales  sales_rolling_std
    0    100                NaN
    1    120                NaN
    2     80            20.000
    3     95            20.207
    4    150            37.859
    5    140            29.439
    """
    df = df.copy()
    df[f"{column}_rolling_std_{window}"] = df[column].rolling(window=window).std()
    return df


def add_exponential_moving_average(
    df: pd.DataFrame, column: str, window: int
) -> pd.DataFrame:
    """
    Add exponential moving average of a column

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the data
    column : str
        Name of the column to compute exponential moving average from
    window : int
        Window size for the exponential moving average

    Returns
    -------
    pd.DataFrame
        DataFrame with additional exponential moving average feature

    Examples
    --------
    >>> df = pd.DataFrame({'sales': [100, 120, 80, 95, 150, 140]})
    >>> df = add_exponential_moving_average(df, 'sales', 3)
    >>> print(df)
       sales     sales_ema
    0    100        100.00
    1    120        110.00
    2     80         95.00
    3     95         95.00
    4    150        122.50
    5    140        131.25
    """
    df = df.copy()
    df[f"{column}_ema_{window}"] = df[column].ewm(span=window, adjust=False).mean()
    return df


def add_lag_ratios(df: pd.DataFrame, column: str, lags: list[int]) -> pd.DataFrame:
    """
    Add lag ratios of a column

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the data
    column : str
        Name of the column to compute lag ratios from
    lags : list[int]
        List of lag values to compute ratios for

    Returns
    -------
    pd.DataFrame
        DataFrame with additional lag ratios feature

    Examples
    --------
    >>> df = pd.DataFrame({'sales': [100, 120, 80, 95, 150, 140]})
    >>> df = add_lag_ratios(df, 'sales', [1, 2])
    >>> print(df)
       sales  lag_1  lag_2  lag_1_lag_2_ratio
    0    100    NaN    NaN                NaN
    1    120  100.0    NaN                NaN
    2     80  120.0  100.0              0.833
    3     95   80.0  120.0              1.500
    4    150   95.0   80.0              0.833
    5    140  150.0   95.0              0.833
    """
    # Check that the number of lags is at least 2
    assert len(lags) > 1, "At least two lags are required to compute ratios"
    # Check that the number of lags is 2
    assert len(lags) == 2, "Ratios are only supported for two lags"

    df = df.copy()
    # First create the lag columns
    for lag in lags:
        if f"lag_{lag}" not in df.columns:
            df[f"lag_{lag}"] = df[column].shift(lag)

    # Then create ratios between consecutive lag pairs
    for i in range(len(lags) - 1):
        lag1, lag2 = lags[i], lags[i + 1]
        df[f"{column}_lag_{lag1}_lag_{lag2}_ratio"] = (
            df[f"lag_{lag1}"] / df[f"lag_{lag2}"]
        )

    # Remove the intermediate lag columns
    for lag in lags:
        df = df.drop(columns=[f"lag_{lag}"])

    return df


def add_month_feature(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add month as a feature from the datetime index

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the data

    Returns
    -------
    pd.DataFrame
        The DataFrame with the month feature

    Examples
    --------
    >>> dates = pd.date_range(start='2023-01-01', end='2023-06-01', freq='MS')
    >>> df = pd.DataFrame({'sales': [100, 120, 80, 95, 150, 140]}, index=dates)
    >>> df = add_month_feature(df)
    >>> print(df)
                 sales  month
    2023-01-01    100        1
    2023-02-01    120        2
    2023-03-01     80        3
    2023-04-01     95        4
    2023-05-01    150        5
    2023-06-01    140        6
    """
    assert isinstance(df.index, pd.DatetimeIndex), (
        "DataFrame must have a datetime index"
    )
    df = df.copy()
    df["month"] = df.index.month
    return df


def add_quarter_feature(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add quarter as a feature from the datetime index

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the data

    Returns
    -------
    pd.DataFrame
        The DataFrame with the quarter feature

    Examples
    --------
    >>> dates = pd.date_range(start='2023-01-01', end='2023-06-01', freq='MS')
    >>> df = pd.DataFrame({'sales': [100, 120, 80, 95, 150, 140]}, index=dates)
    >>> df = add_quarter_feature(df)
    >>> print(df)
                 sales  quarter
    2023-01-01    100        1
    2023-02-01    120        1
    2023-03-01     80        1
    2023-04-01     95        2
    2023-05-01    150        2
    2023-06-01    140        2
    """
    assert isinstance(df.index, pd.DatetimeIndex), (
        "DataFrame must have a datetime index"
    )
    df = df.copy()
    df["quarter"] = df.index.quarter
    return df


def add_year_feature(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add year as a feature from the datetime index

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the data

    Returns
    -------
    pd.DataFrame
        The DataFrame with the year feature

    Examples
    --------
    >>> dates = pd.date_range(start='2023-01-01', end='2023-06-01', freq='MS')
    >>> df = pd.DataFrame({'sales': [100, 120, 80, 95, 150, 140]}, index=dates)
    >>> df = add_year_feature(df)
    >>> print(df)
                 sales  year
    2023-01-01    100  2023
    2023-02-01    120  2023
    2023-03-01     80  2023
    2023-04-01     95  2023
    2023-05-01    150  2023
    2023-06-01    140  2023
    """
    assert isinstance(df.index, pd.DatetimeIndex), (
        "DataFrame must have a datetime index"
    )
    df = df.copy()
    df["year"] = df.index.year
    return df


def add_weekday_feature(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add weekday feature from the datetime index

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the data

    Returns
    -------
    pd.DataFrame
        The DataFrame with the weekday feature

    Examples
    --------
    >>> dates = pd.date_range(start='2023-01-01', end='2023-06-01', freq='MS')
    >>> df = pd.DataFrame({'sales': [100, 120, 80, 95, 150, 140]}, index=dates)
    >>> df = add_weekday_feature(df)
    >>> print(df)
                 sales  weekday
    2023-01-01    100        0
    2023-01-02    120        1
    2023-01-03     80        2
    2023-01-04     95        3
    2023-01-05    150        4
    2023-01-06    140        5
    """
    assert isinstance(df.index, pd.DatetimeIndex), (
        "DataFrame must have a datetime index"
    )
    df = df.copy()
    df["weekday"] = df.index.weekday
    return df


def add_week_feature(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add week feature from the datetime index

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the data

    Returns
    -------
    pd.DataFrame
        The DataFrame with the week feature

    Examples
    --------
    >>> dates = pd.date_range(start='2023-01-01', end='2023-06-01', freq='MS')
    >>> df = pd.DataFrame({'sales': [100, 120, 80, 95, 150, 140]}, index=dates)
    >>> df = add_week_feature(df)
    >>> print(df)
                 sales  week
    2023-01-01    100     1
    2023-02-01    120     1
    2023-03-01     80     1
    2023-04-01     95     2
    2023-05-01    150     2
    2023-06-01    140     2
    """
    assert isinstance(df.index, pd.DatetimeIndex), (
        "DataFrame must have a datetime index"
    )
    df = df.copy()
    df["week"] = df.index.isocalendar().week
    return df


def add_pct_change(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Add percentage change of a column

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the data
    column : str
        The column to compute percentage change from

    Returns
    -------
    pd.DataFrame
        The DataFrame with the percentage change feature

    Examples
    --------
    >>> dates = pd.date_range(start='2023-01-01', end='2023-06-01', freq='MS')
    >>> df = pd.DataFrame({'sales': [100, 120, 80, 95, 150, 140]}, index=dates)
    >>> df = add_pct_change(df, 'sales')
    >>> print(df)
                 sales  pct_change
    2023-01-01    100         NaN
    2023-02-01    120       0.200
    2023-03-01     80      -0.333
    2023-04-01     95       0.188
    2023-05-01    150       0.579
    2023-06-01    140      -0.067
    """
    df = df.copy()
    df[f"{column}_pct_change"] = df[column].pct_change()
    return df


def add_growth_rate(df: pd.DataFrame, column: str, period: int = 1) -> pd.DataFrame:
    """
    Add growth rate of a column

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the data
    column : str
        Name of the column to compute growth rate from
    period : int, optional
        Period to compute growth rate from, by default 1
    Returns
    -------
    pd.DataFrame
        DataFrame with additional growth rate feature

    Examples
    --------
    >>> df = pd.DataFrame({'sales': [100, 120, 80]})
    >>> df = add_growth_rate(df, 'sales', 1)
    >>> print(df)
       sales  growth_rate
    0    100         NaN
    1    120       0.200
    """
    df = df.copy()
    df[f"{column}_growth_rate"] = df[column].diff() / df[column].shift(period)
    return df


def add_lags(df: pd.DataFrame, column: str, lags: list[int]) -> pd.DataFrame:
    """
    Add lagged values of a column

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the data
    column : str
        Name of the column to compute lags from
    lags : list[int]
        List of lag values to create

    Returns
    -------
    pd.DataFrame
        DataFrame with additional lag features

    Examples
    --------
    >>> df = pd.DataFrame({'sales': [100, 120, 80, 95]})
    >>> df = add_lags(df, 'sales', [1, 2])
    >>> print(df)
       sales  lag_1  lag_2
    0    100    100    100
    1    120  100.0    120
    2     80  120.0  100.0
    3     95   80.0  120.0
    """
    if not all(isinstance(lag, int) and lag > 0 for lag in lags):
        raise ValueError("All lags must be positive integers")

    df = df.copy()

    for lag in lags:
        lag_col = f"{column}_lag_{lag}"
        df[lag_col] = df[column].shift(lag)
        # Fill NaN values with the original values at those positions
        df[lag_col] = df[lag_col].fillna(df[column])

    return df


def _extract_ratio_lags(column_name: str) -> tuple[Optional[int], Optional[int]]:
    """
    Extract two lag numbers from a ratio column name using regular expression.

    Parameters
    ----------
    column_name : str
        Name of the column containing lag ratio information

    Returns
    -------
    tuple[Optional[int], Optional[int]]
        Tuple containing the two lag numbers, or (None, None) if not found

    Examples
    --------
    >>> _extract_ratio_lags("sales_lag_3_lag_6_ratio")
    (3, 6)
    >>> _extract_ratio_lags("invalid_column")
    (None, None)
    """
    pattern = r"lag_(\d+).*lag_(\d+).*ratio"
    match = re.search(pattern, column_name.lower())
    if match:
        return [int(match.group(1)), int(match.group(2))]
    return None


def _extract_lag_number(feature_name: str) -> int:
    """
    Extract lag number from feature name using regular expression.

    Parameters
    ----------
    feature_name : str
        Name of the feature containing lag information

    Returns
    -------
    int
        The lag number

    Raises
    ------
    ValueError
        If no lag number could be extracted from the feature name

    Examples
    --------
    >>> _extract_lag_number("sales_lag_3_rolling_mean_12")
    3
    >>> _extract_lag_number("sales_lag_6")
    6
    """
    lag_match = re.search(r"lag_(\d+)", feature_name)
    if lag_match:
        return int(lag_match.group(1))
    else:
        return None


def _extract_window_size(column_name: str) -> tuple[Optional[int], Optional[str]]:
    """
    Extract window size from column name using regex.

    Parameters
    ----------
    column_name : str
        Name of the column containing window size information

    Returns
    -------
    int
        The window size

    Examples
    --------
    >>> _extract_window_size("sales_rolling_mean_12")
    12
    """
    window_match = re.search(r"rolling_mean_(\d+)", column_name)
    if window_match:
        return int(window_match.group(1))
    return None


def _extract_feature_info(column_name: str) -> tuple[Optional[int], Optional[str]]:
    """
    Extract lag number and feature type from column name using regex.

    Parameters
    ----------
    column_name : str
        Name of the column containing lag information

    Returns
    -------
    tuple[Optional[int], Optional[str]]
        Tuple containing the lag number and feature type, or (None, None) if not found

    Examples
    --------
    >>> _extract_feature_info("sales_lag_3_rolling_mean_12")
    (3, "rolling_mean")
    >>> _extract_feature_info("sales_lag_6_lag_12_ratio")
    ([6, 12], "lag_ratio")
    >>> _extract_feature_info("sales_lag_6")
    ([6], "lag")
    """
    # Check for lag ratios first
    if "_ratio" in column_name:
        lag_values = _extract_ratio_lags(column_name)
        if lag_values:
            return lag_values, "lag_ratio"
        return None, None

    # Then check for rolling patterns
    if "_rolling_mean_" in column_name:
        return [_extract_lag_number(column_name)], "rolling_mean"
    elif "_rolling_std_" in column_name:
        return [_extract_lag_number(column_name)], "rolling_std"
    elif "_ema_" in column_name:
        return [_extract_lag_number(column_name)], "ema"
    elif "_pct_change" in column_name:
        return [_extract_lag_number(column_name)], "pct_change"

    # Finally check for simple lags
    lag_value = _extract_lag_number(column_name)
    if lag_value is not None:
        return [lag_value], "lag"

    return None, None


def _find_numeric_feature_columns(df: pd.DataFrame) -> list[str]:
    """
    Find all feature columns in the DataFrame using regex.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the data

    Returns
    -------
    list[str]
        List of feature columns

    Examples
    --------
    >>> df = pd.DataFrame({
    ...     'sales': [100, 120, 80, 95],
    ...     'sales_lag_3_rolling_mean_12': [100, 120, 80, 95],
    ...     'sales_lag_6_lag_12_ratio': [1.2, 0.8, 1.1, 0.9]
    ... })
    >>> _find_numeric_feature_columns(df)
    ['sales_lag_3_rolling_mean_12', 'sales_lag_6_lag_12_ratio']
    """
    patterns = [
        "lag_",
        "rolling_mean_",
        "rolling_std_",
        "lag_ratio",
        "ema_",
        "pct_change",
    ]

    return [
        col for col in df.columns if any(pattern in col.lower() for pattern in patterns)
    ]


def _find_categorical_feature_columns(df: pd.DataFrame) -> list[str]:
    """
    Find all categorical feature columns in the DataFrame using regex.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the data

    Returns
    -------
    list[str]
        List of feature columns

    Examples
    --------
    >>> df = pd.DataFrame({'sales': [100, 120, 80, 95], 'sales_lag_3_rolling_mean_12': [100, 120, 80, 95]}, index=pd.date_range(start='2023-01-01', end='2023-06-01', freq='MS'))
    >>> df = add_month_feature(df)
    >>> df = add_quarter_feature(df)
    >>> df = add_year_feature(df)
    >>> _find_categorical_feature_columns(df)
    ['month', 'quarter', 'year']
    """
    return [
        col
        for col in df.columns
        if any(
            pattern in col.lower()
            for pattern in ["month", "quarter", "year", "weekday", "week"]
        )
    ]


def _get_base_column(feature_name: str) -> str:
    """
    Extract the base column name from a feature name.

    Parameters
    ----------
    feature_name : str
        Name of the feature

    Returns
    -------
    str
        Base column name

    Examples
    --------
    >>> _get_base_column("sales_lag_3_rolling_mean_12")
    "sales_lag_3"
    >>> _get_base_column("sales_lag_6")
    "sales"
    >>> _get_base_column("sales_lag_6_lag_12_ratio")
    "sales"
    >>> _get_base_column("sales_lag_3_ema_12")
    "sales_lag_3"
    """
    # Special handling for lag ratios
    if "_lag_" in feature_name and "_ratio" in feature_name:
        return feature_name.split("_lag_")[0]

    # Handle rolling features
    if any(
        pattern in feature_name
        for pattern in ["_rolling_mean_", "_rolling_std_", "_ema_", "_pct_change"]
    ):
        if "_lag_" in feature_name:
            parts = feature_name.split("_")
            lag_index = parts.index("lag") + 2  # +2 to include "lag" and the number
            return "_".join(parts[:lag_index])
        return feature_name

    # Handle simple lag features
    if "_lag_" in feature_name:
        return feature_name.split("_lag_")[0]

    return feature_name


def _check_frequency(df: pd.DataFrame) -> str:
    """
    Check the frequency of the DataFrame index.
    """
    freq = df.index.freq or pd.infer_freq(df.index)
    if freq is None:
        raise ValueError("Could not determine frequency of time series index")
    return freq


def _find_extensible_numeric_features(
    df: pd.DataFrame,
    nb_periods: int,
) -> dict:
    """Find all extensible numeric features in the DataFrame"""
    # Change to a list of tuples (function, kwargs) instead of a dict
    numeric_feature_columns = _find_numeric_feature_columns(df)

    if not numeric_feature_columns:
        print("No extensible numeric features found")
        return [], []

    extensible_numeric_features = []
    numeric_features_to_remove = []

    map_feature_methods = {
        "rolling_mean": add_rolling_mean,
        "rolling_std": add_rolling_std,
        "lag": add_lags,
        "lag_ratio": add_lag_ratios,
        "pct_change": add_pct_change,
        "ema": add_exponential_moving_average,
    }

    # Group columns by base column to combine lags
    features_by_base = {}

    for col in numeric_feature_columns:
        lag_values, feature_type = _extract_feature_info(col)
        base_column = _get_base_column(col)

        print(f"Base column: {base_column}")
        print(f"Lag values: {lag_values}, Feature type: {feature_type}")

        if lag_values is not None and feature_type is not None:
            print(
                f"Lag values >= nb_periods: {all(lag >= nb_periods for lag in lag_values)}"
            )

            if all(lag >= nb_periods for lag in lag_values):
                if feature_type == "lag":
                    # Group lags by base column
                    if base_column not in features_by_base:
                        features_by_base[base_column] = {"lags": set()}
                    features_by_base[base_column]["lags"].update(lag_values)

                elif feature_type == "lag_ratio":
                    extensible_numeric_features.append(
                        (
                            map_feature_methods["lag_ratio"],
                            {"lags": lag_values, "column": base_column},
                        )
                    )

                elif feature_type in ["rolling_mean", "rolling_std", "ema"]:
                    window_size = _extract_window_size(col)
                    if window_size is not None:
                        extensible_numeric_features.append(
                            (
                                map_feature_methods[feature_type],
                                {"column": base_column, "window": window_size},
                            )
                        )

                elif feature_type == "pct_change":
                    extensible_numeric_features.append(
                        (map_feature_methods[feature_type], {"column": base_column})
                    )

        else:
            numeric_features_to_remove.append(col)

    # Add combined lags for each base column
    for base_column, info in features_by_base.items():
        if info["lags"]:
            extensible_numeric_features.append(
                (add_lags, {"column": base_column, "lags": list(info["lags"])})
            )

    return extensible_numeric_features, numeric_features_to_remove


def _find_extensible_categorical_features(
    df: pd.DataFrame,
) -> tuple[dict, dict, list[str]]:
    """
    Find all extensible categorical features in the DataFrame and columns to delete

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the features

    Returns
    -------
    tuple[dict, dict, list[str]]
        - Dictionary of extensible categorical features and their creation methods
        - List of column names that should be deleted (non-extensible features)
    """
    # Find all categorical calendar features columns
    categorical_feature_columns = _find_categorical_feature_columns(df)

    if not categorical_feature_columns:
        return []

    # Fixed list of extensible features
    extensible_categorical_features = []

    # Map of feature types to methods
    categorical_calendar_feature_methods = {
        "month": add_month_feature,
        "quarter": add_quarter_feature,
        "year": add_year_feature,
        "weekday": add_weekday_feature,
        "week": add_week_feature,
    }

    for col in categorical_feature_columns:
        extensible_categorical_features.append(
            categorical_calendar_feature_methods[col]
        )

    return extensible_categorical_features


def find_extensible_features(
    df: pd.DataFrame,
    nb_periods: int,
) -> tuple[dict, dict, list[str]]:
    """
    Find all extensible features in the DataFrame and columns to delete for
    a given forecast horizon. This method is usefull if you want to know which
    features you are able to train your model on and which features you need to
    delete if your objective is to predict for a certain amount of periods in the
    future.

    This method is built specifically to be used after creating your features from
    this package since the checks are made on the column names and are specific to
    the tipology of the forecaster_toolkit library.

    Other features can be built by the user but this method will not be able to
    detect them, it is up to the user to know which features are extensible in
    order to predict for a given amount of periods in the future.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the features
    nb_periods : int
        Number of periods to predict

    Returns
    -------
    tuple[dict, dict, list[str]]
        - Dictionary of extensible numeric features and their creation methods
        - Dictionary of extensible categorical features and their creation methods
        - List of column names that should be deleted (non-extensible features)
    """
    # Check if the DataFrame has a datetime index
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame must have a datetime index")

    # Find extensible numeric features
    extensible_numeric_features, numeric_features_to_remove = (
        _find_extensible_numeric_features(df, nb_periods)
    )

    # Find extensible categorical features
    extensible_categorical_features = _find_extensible_categorical_features(df)

    # Add invalid columns to remove list
    # Categorical features are by definition extensible, so we don't need to remove them
    features_to_remove = list(set(numeric_features_to_remove))

    return (
        extensible_numeric_features,
        extensible_categorical_features,
        features_to_remove,
    )


def extend_time_series_for_prediction(
    df: pd.DataFrame,
    nb_periods: int,
) -> pd.DataFrame:
    """
    Extends the features for prediction. This method completes the job done by
    the find_extensible_features method. For the extensible features found, this
    method will extend the time series for the prediction of nb_periods timesteps.

    The extension is done by creating a new DataFrame, the index being the union
    of the original index and the future dates (to be predicted). The new DataFrame
    is then filled with the original data at the correct indexes. The added rows are
    filled by calling the appropriate methods with the correct arguments stored in
    the dictionaries returned by the find_extensible_features method.

    Only the last nb_periods rows of the dataframe is returned, ready to feed into
    the predict method of the model.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the features
    nb_periods : int
        Number of periods to predict

    Returns
    -------
    pd.DataFrame
        DataFrame containing the extended features of length nb_periods
    """
    extensible_numeric_features, extensible_categorical_features, _ = (
        find_extensible_features(df, nb_periods)
    )

    # Create the prediction date range
    freq = _check_frequency(df)
    future_dates = pd.date_range(start=df.index[-1], periods=nb_periods + 1, freq=freq)[
        1:
    ]

    # Create extended DataFrame
    extended_df = pd.DataFrame(index=df.index.union(future_dates))

    # Copy original data
    for col in df.columns:
        extended_df[col] = df[col]

    # Process numeric features
    for function, kwargs in extensible_numeric_features:
        extended_df = function(extended_df, **kwargs)

    # Process categorical features
    for function in extensible_categorical_features:
        extended_df = function(extended_df)

    if len(extended_df.columns) != len(df.columns):
        raise ValueError(
            "The number of columns in the extended DataFrame does not match the number of columns in the original DataFrame"
        )

    return extended_df.loc[future_dates]
