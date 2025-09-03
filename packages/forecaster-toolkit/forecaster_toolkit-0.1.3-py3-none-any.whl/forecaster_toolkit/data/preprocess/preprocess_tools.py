from functools import wraps
from typing import Literal, Optional, Union

import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.preprocessing import MinMaxScaler, StandardScaler


def check_index(func):
    """Decorator to ensure DataFrame has a datetime index"""

    @wraps(func)
    def wrapper(self, df, *args, **kwargs):
        # Convert Series to DataFrame if needed
        if isinstance(df, pd.Series):
            df = df.to_frame()

        if not isinstance(df.index, pd.DatetimeIndex):
            print("Index is not a datetime index, trying to find a datetime column")
            datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

            if not datetime_cols:
                raise ValueError(
                    f"Did not find a datetime column in the data, data must have a datetime index or column. Got index type: {type(df.index)}"
                )

            df = df.set_index(datetime_cols[0]).sort_index(ascending=True)
            print(f"Set {datetime_cols[0]} as index")

        return func(self, df, *args, **kwargs)

    return wrapper


class TimeSeriesPreprocessor:
    """
    Preprocessor for time series data

    Attributes
    ----------
    freq : str
        Frequency for resampling ('MS' for month start, 'D' for daily...)
    interpolation_method : str
        Method for interpolating missing values
    handle_negatives : str
        Strategy for negative values ('truncate', 'remove', 'keep', 'abs')
    spline_degree : int, optional
        Degree of the spline for the 'spline' method
    polynomial_degree : int, optional
        Degree of the polynomial for the 'polynomial' method
    min_value : float, optional
        Minimum value allowed in the series (None to disable)
    knn_imputer_params : dict, optional
        Parameters for the KNN imputer if interpolation_method is 'knn'
    normalize : str, optional
        Normalization method ('standard', 'minmax')

    Methods
    -------
    fill_missing_values(df : pd.DataFrame, cols_name : Union[str, list[str]]) -> pd.DataFrame
        Fill missing values in the series.

    replace_nan_with_zero(df : pd.DataFrame) -> pd.DataFrame
        Replace NaN values with zero.

    treat_negatives(df : pd.DataFrame, method : str) -> pd.DataFrame
        Handle negative values in the data according to specified method.

    remove_negatives(df : pd.DataFrame) -> pd.DataFrame
        Remove negative values from the series.

    transform(df : pd.DataFrame, **kwargs) -> pd.DataFrame
        Apply preprocessing to the data.
    """

    def __init__(
        self,
        freq: str,
        interpolation_method: Literal[
            "linear",
            "polynomial",
            "spline",
            "quadratic",
            "zero",
            "ffill",
            "bfill",
            "knn",
        ] = "linear",
        handle_negatives: Literal["truncate", "remove", "keep", "abs"] = "truncate",
        spline_degree: Optional[int] = 3,
        polynomial_degree: Optional[int] = 2,
        min_value: Optional[float] = 0,
        knn_imputer_params: Optional[dict] = None,
        normalize: Literal["standard", "minmax"] = "standard",
    ):
        """
        Arguments
        ---------
        freq: str
            Frequency for resampling ('MS' for month start, 'D' for daily...)
        interpolation_method : str
            Method for interpolating missing values ('linear', 'polynomial', 'spline', 'quadratic', 'zero', 'ffill', 'bfill', 'knn')
        handle_negatives : str
            Strategy for negative values ('truncate', 'remove', 'keep', 'abs')
        spline_degree : int, optional
            Degree of the spline for the 'spline' method
        polynomial_degree : int, optional
            Degree of the polynomial for the 'polynomial' method
        min_value : float, optional
            Minimum value allowed in the series (None to disable)
        knn_imputer_params : dict, optional
            Parameters for the KNN imputer if interpolation_method is 'knn'
        normalize : str, optional
            Normalization method ('standard', 'minmax')

        Raises
        ------
        TypeError
            If arguments are not of the correct type
        ValueError
            If arguments have invalid values
        """
        # Type checking
        if not isinstance(freq, str):
            raise TypeError(f"freq must be a string, got {type(freq)}")
        if not isinstance(interpolation_method, str):
            raise TypeError(
                f"interpolation_method must be a string, got {type(interpolation_method)}"
            )
        if not isinstance(handle_negatives, str):
            raise TypeError(
                f"handle_negatives must be a string, got {type(handle_negatives)}"
            )
        if min_value is not None and not isinstance(min_value, (int, float)):
            raise TypeError(
                f"min_value must be a number or None, got {type(min_value)}"
            )
        # Value validation for the interpolation method
        valid_methods = [
            "linear",
            "polynomial",
            "spline",
            "quadratic",
            "zero",
            "ffill",
            "bfill",
            "knn",
        ]
        if interpolation_method not in valid_methods:
            raise ValueError(
                f"interpolation_method must be one of {valid_methods}, got {interpolation_method}"
            )

        # Value validation for the handle_negatives strategy
        valid_strategies = ["truncate", "remove", "keep", "abs"]
        if handle_negatives not in valid_strategies:
            raise ValueError(
                f"handle_negatives must be one of {valid_strategies}, got {handle_negatives}"
            )

        valid_normalize = ["standard", "minmax"]
        if normalize not in valid_normalize:
            raise ValueError(
                f"normalize must be one of {valid_normalize}, got {normalize}"
            )

        # All checks passed, assign values
        self.freq = freq
        self.interpolation_method = interpolation_method
        self.handle_negatives = handle_negatives
        self.min_value = min_value
        self.spline_degree = spline_degree
        self.polynomial_degree = polynomial_degree
        self.knn_imputer_params = knn_imputer_params
        self.normalize = normalize

    def standard_normalization(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize the data using standard normalization.

        x = (x - x.mean()) / x.std()

        Parameters
        ----------
        df : pd.DataFrame
            The dataframe to normalize

        Returns
        -------
        pd.DataFrame
            The dataframe normalized

        Examples
        --------
        >>> df = pd.DataFrame({'A': [1, 2, 3, 4, 5]})
        >>> print(df)
           A
        0  1
        1  2
        2  3
        3  4
        4  5
        >>> preprocessor = TimeSeriesPreprocessor()
        >>> df_normalized = preprocessor.standard_normalization(df)
        >>> print(df_normalized)
           A
        0 -1.264911
        1 -0.632456
        2  0.000000
        3  0.632456
        4  1.264911
        """
        if isinstance(df, pd.Series):
            df = df.values.reshape(-1, 1)
        return StandardScaler().fit_transform(df)

    def min_max_normalization(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize the data using min-max normalization.

        x = (x - x.min()) / (x.max() - x.min())

        Parameters
        ----------
        df : pd.DataFrame
            The dataframe to normalize

        Returns
        -------
        pd.DataFrame
            The dataframe normalized

        Examples
        --------
        >>> df = pd.DataFrame({'A': [1, 2, 3, 4, 5]})
        >>> print(df)
           A
        0  1
        1  2
        2  3
        3  4
        4  5
        >>> preprocessor = TimeSeriesPreprocessor()
        >>> df_normalized = preprocessor.min_max_normalization(df)
        >>> print(df_normalized)
           A
        0  0.0
        1  0.5
        2  1.0
        3  0.0
        4  1.0
        """
        if isinstance(df, pd.Series):
            df = df.values.reshape(-1, 1)

        return MinMaxScaler().fit_transform(df)

    def fill_missing_values(
        self, df: Union[pd.DataFrame, np.ndarray], cols_name: Union[str, list[str]]
    ) -> Union[pd.DataFrame, np.ndarray]:
        """Core function to fill missing values and interpolate a time series.

        Parameters
        ----------
        df : Union[pd.DataFrame, np.ndarray]
            The series to fill missing values in
        cols_name : Union[str, list[str]]
            Column(s) to fill missing values in

        Returns
        -------
        Union[pd.DataFrame, np.ndarray]
            The series with a consistent time step and interpolated values

        Examples
        --------
        >>> df = pd.DataFrame({'sales': [100, 120, 80, 95, 150]})
        >>> df.index = pd.date_range(start='2020-01-01', periods=5, freq='D')
        >>> df.loc['2020-02-01'] = np.nan
        >>> df.loc['2020-04-01'] = np.nan
        >>> print(df)
           sales
        2020-01-01  100.0
        2020-02-01    NaN
        2020-03-01   80.0
        2020-04-01    NaN
        2020-05-01  150.0
        >>> preprocessor = TimeSeriesPreprocessor(freq='D')
        >>> df_processed = preprocessor.fill_missing_values(df, 'sales')
        >>> print(df_processed)
           sales
        2020-01-01  100.0
        2020-02-01  110.0
        2020-03-01   80.0
        2020-04-01   97.5
        2020-05-01  150.0
        """
        # Ensure cols_name is a list
        cols_name = [cols_name] if isinstance(cols_name, str) else cols_name

        # Generate a regular time series between the first and last index
        full_date_range = pd.date_range(
            start=df.index.min(), end=df.index.max(), freq=self.freq
        )
        # If there are missing dates
        if len(full_date_range.difference(df.index)) != 0:
            # Create a DataFrame with the full date range
            print(
                "There are missing dates in the data at dates : ",
                full_date_range.difference(df.index),
            )
            filled_df = pd.DataFrame(index=full_date_range)

            # Copy data from original DataFrame
            filled_df = filled_df.join(df)

            # Interpolate specified columns
            for col in cols_name:
                # Convert to numeric first
                filled_df[col] = pd.to_numeric(filled_df[col], errors="coerce")
                print(f"Interpolating {col} with {self.interpolation_method} method")
                if self.interpolation_method == "knn":
                    # Apply KNN imputation
                    filled_df[col] = KNNImputer(
                        **self.knn_imputer_params
                    ).fit_transform(filled_df[[col]])
                else:
                    # Initialize interpolation parameters
                    interpolation_params = {}
                    if self.interpolation_method in ["spline", "polynomial"]:
                        interpolation_params["order"] = (
                            self.spline_degree
                            if self.interpolation_method == "spline"
                            else self.polynomial_degree
                        )

                    # Apply interpolation with the appropriate parameters
                    filled_df[col] = filled_df[col].interpolate(
                        method=self.interpolation_method, **interpolation_params
                    )

            return filled_df

        if self.freq is None:
            self.freq = pd.infer_freq(df.index)
        return df

    def replace_nan_with_zero(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Replace NaN values with zero

        Parameters
        ----------
        df : pd.DataFrame
            The dataframe to replace NaN values with zero

        Returns
        -------
        pd.DataFrame
            The dataframe with NaN values replaced with zero

        Examples
        --------
        >>> df = pd.DataFrame({'A': [1, 2, np.nan, 4, 5]})
        >>> print(df)
              A
        0     1
        1     2
        2   NaN
        3     4
        4     5
        >>> preprocessor = TimeSeriesPreprocessor()
        >>> df_processed = preprocessor.replace_nan_with_zero(df)
        >>> print(df_processed)
           A
        0  1
        1  2
        2  0
        3  4
        4  5
        """
        return df.fillna(0)

    def treat_negatives(
        self, method: str, df: Union[pd.DataFrame, pd.Series]
    ) -> Union[pd.DataFrame, pd.Series]:
        """
        Handle negative values in the data according to specified method.

        Parameters
        ----------
        df : Union[pd.DataFrame, pd.Series]
            The data containing negative values to be treated
        method: str
            Method to handle negative values. Options:
            - 'truncate': Truncate data before first negative value
            - 'remove': Remove all rows containing negative values
            - 'keep': Keep negative values unchanged

        Returns
        -------
        Union[pd.DataFrame, pd.Series]
            The data with negative values handled according to specified method

        Examples
        --------
        >>> df = pd.DataFrame({'A': [1, 2, -3, 4, 5]})
        >>> preprocessor = TimeSeriesPreprocessor()
        >>> # Remove negatives
        >>> df_removed = preprocessor.treat_negatives(df, method='remove')
        >>> print(df_removed)
           A
        0  1
        1  2
        3  4
        4  5
        >>> # Truncate at first negative
        >>> df_truncated = preprocessor.treat_negatives(df, method='truncate')
        >>> print(df_truncated)
           A
        0  1
        1  2
        """
        if method == "truncate":
            df = self.truncate_before_first_negative(df)
        elif method == "remove":
            df = self.remove_negatives(df)
        elif method == "abs":
            df = df.abs()
        elif method == "keep":
            pass
        else:
            raise ValueError(f"Invalid method: {method}")
        return df

    def remove_negatives(
        self,
        df: Union[pd.DataFrame, pd.Series],
    ) -> Union[pd.DataFrame, pd.Series]:
        """
        Remove negative values from the series

        Parameters
        ----------
        df : Union[pd.DataFrame, pd.Series]
            The series to remove negative values from

        Returns
        -------
        Union[pd.DataFrame, pd.Series]
            The series with negative values removed

        Examples
        --------
        >>> df = pd.DataFrame({'A': [1, 2, -3, 4, 5],
                            'B': [1, -2, 3, -4, 5]})
        >>> print(df)
           A  B
        0  1  1
        1  2 -2
        2 -3  3
        3  4 -4
        4  5  5
        >>> preprocessor = TimeSeriesPreprocessor(handle_negatives='remove')
        >>> df = preprocessor.remove_negatives(df)
        >>> print(df)
           A  B
        0  1  1
        4  5  5
        """
        df = df[df >= 0].dropna()
        return df

    def truncate_before_first_negative(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Truncate data before first negative value

        Parameters
        ----------
        df : pd.DataFrame
            The dataframe to truncate

        Returns
        -------
        pd.DataFrame
            The dataframe truncated before first negative value

        Examples
        --------
        >>> df = pd.DataFrame({'A': [1, 2, -3, 4, 5]})
        >>> print(df)
           A
        0  1
        1  2
        2 -3
        3  4
        4  5
        >>> preprocessor = TimeSeriesPreprocessor(handle_negatives='truncate')
        >>> df_truncated = preprocessor.truncate_before_first_negative(df)
        >>> print(df_truncated)
           A
        0  1
        1  2
        """
        df = df.copy()

        # Convert to numeric first
        df = df.apply(pd.to_numeric, errors="coerce")

        if self.handle_negatives == "truncate":
            # Trouver la première valeur négative pour chaque colonne numérique
            neg_dates = []
            for col in df.select_dtypes(include=np.number).columns:
                neg_idx = df[df[col] < 0].index
                if len(neg_idx) > 0:
                    neg_dates.append(neg_idx.min())

            # Tronquer à la première valeur négative trouvée
            if neg_dates:
                min_date_neg = min(neg_dates)
                df = df.loc[:min_date_neg].iloc[
                    :-1
                ]  # Exclure la ligne avec la valeur négative

        return df

    @check_index
    def transform(
        self,
        df: Union[pd.DataFrame, np.ndarray],
        **kwargs,
    ) -> Union[pd.DataFrame, np.ndarray]:
        """
        Apply preprocessing to the data

        Parameters
        ----------
        df : Union[pd.DataFrame, np.ndarray]
            The series to preprocess
        **kwargs:
            cols_name : str or list[str]
                Column(s) to process
        Returns
        -------
        Union[pd.DataFrame, np.ndarray]
            The preprocessed series
        """
        # Create a copy of the input data
        df = df.copy()
        # Fill missing time steps and interpolate values
        df = self.fill_missing_values(
            df=df, cols_name=kwargs.get("cols_name")
        ).sort_index()
        return df
