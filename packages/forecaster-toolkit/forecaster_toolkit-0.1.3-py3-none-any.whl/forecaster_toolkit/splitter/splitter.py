import inspect
from typing import Any, Optional, override

import numpy as np
import pandas as pd
from sktime.split import (
    CutoffSplitter,
    ExpandingCutoffSplitter,
    ExpandingWindowSplitter,
    SingleWindowSplitter,
    SlidingWindowSplitter,
    TemporalTrainTestSplitter,
)
from sktime.split.base._base_splitter import BaseSplitter


class Splitter:
    """
    A class for creating time series cross-validation splits.

    This class provides a flexible interface for creating different types of time series
    cross-validation splits. It supports various splitting strategies from the sktime library,
    each suitable for different time series forecasting scenarios.

    Supported Splitting Methods:
    - CutoffSplitter: Splits data at specific cutoff points
    - SingleWindowSplitter: Uses a single window for training
    - SlidingWindowSplitter: Creates overlapping windows
    - ExpandingWindowSplitter: Creates expanding windows (default)
    - ExpandingCutoffSplitter: Creates expanding windows with cutoff points
    - TemporalTrainTestSplitter: Simple train-test split respecting time order

    Attributes
    ----------
    method : str
        The splitting method to use
    params : dict
        Parameters for the splitter
    splitter : Any
        The initialized splitter instance
    ts_length : int
        Length of the time series being split

    Examples
    --------
    >>> from forecaster_toolkit.splitter import Splitter
    >>>
    >>> # Create an expanding window splitter
    >>> splitter = Splitter(method="expandingwindowsplitter")
    >>> splitter.fit()
    >>>
    >>> # Get splits for your data
    >>> splits = splitter.get_splits(df=your_data)
    >>> for train, test in splits:
    ...     print(f"Train size: {len(train)}, Test size: {len(test)}")
    """

    def __init__(self, method: str, splitter_params: Optional[dict] = None):
        """
        Initialize the Splitter with a splitting method.

        Parameters
        ----------
        method : str
            The splitting method to use. Must be one of:
            - "cutoffsplitter"
            - "singlewindowsplitter"
            - "slidingwindowsplitter"
            - "expandingwindowsplitter"
            - "expandingcutoffsplitter"
            - "temporaltraintestsplitter"
        splitter_params : dict, optional
            Custom parameters for the splitter. If empty, uses default parameters
            from BASE_CONFIGS

        Raises
        ------
        ValueError
            If method is not recognized or parameters are invalid
        """
        self._validate_method(method.lower())
        self.method = method.lower()
        self.splitter = None
        self.ts_length = None
        self.params = splitter_params
        self.is_fitted = False

    def _validate_method(self, method: str) -> None:
        """
        Validate that the specified method exists in the mapping.

        Parameters
        ----------
        method : str
            The method to validate

        Raises
        ------
        ValueError
            If method is not in the list of valid methods
        """
        valid_methods = list(self._get_mapping().keys())
        if method not in valid_methods:
            raise ValueError(
                f"Invalid method '{self.method}'. Must be one of: {valid_methods}"
            )

    def _get_mapping(self) -> dict[str, type]:
        """
        Get the mapping of method names to splitter classes.

        Returns
        -------
        dict[str, type]
            Dictionary mapping method names to their corresponding splitter classes
        """
        return {
            "cutoffsplitter": CutoffSplitter,
            "singlewindowsplitter": SingleWindowSplitter,
            "slidingwindowsplitter": SlidingWindowSplitter,
            "expandingwindowsplitter": ExpandingWindowSplitter,
            "expandingcutoffsplitter": ExpandingCutoffSplitter,
            "temporaltraintestsplitter": TemporalTrainTestSplitter,
        }

    def _validate_params(self, params: dict[str, Any]) -> None:
        """
        Validate the parameters for the current splitter.

        This method checks:
        1. All required parameters are present
        2. Parameter types match their annotations
        3. No unknown parameters are provided

        Parameters
        ----------
        params : dict[str, Any]
            Dictionary of parameters to validate

        Raises
        ------
        ValueError
            If parameters are invalid or missing
        """
        required_params = self.get_splitter_params()
        errors = []

        # Check for missing required parameters
        for name, param in required_params.items():
            if param.default == inspect.Parameter.empty and name not in params:
                errors.append(f"Missing required parameter: {name}")

        # Check parameter types
        for name, value in params.items():
            if name not in required_params:
                errors.append(f"Unknown parameter: {name}")
                continue

            param = required_params[name]
            if param.annotation != inspect.Parameter.empty:
                expected_type = param.annotation
                if not isinstance(value, expected_type):
                    errors.append(
                        f"Parameter '{name}' should be of type {expected_type}, "
                        f"got {type(value)}"
                    )

        if errors:
            raise ValueError(
                f"Invalid parameters for {self.method}:\n" + "\n".join(errors)
            )

    def fit(self, df: pd.DataFrame = None) -> "Splitter":
        """
        Initialize the splitter with the given parameters.

        This method creates the actual splitter instance using the specified
        method and parameters. If a DataFrame is provided, it will calculate
        dynamic parameters based on the time series length.

        Parameters
        ----------
        df : pd.DataFrame, optional
            The DataFrame to use for calculating dynamic parameters.
            If provided, parameters will be adjusted based on the time series length.

        Returns
        -------
        Splitter
            The fitted Splitter instance

        Raises
        ------
        ValueError
            If initialization fails due to invalid parameters
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Data must be a dataframe or numpy array, got {type(df)}")

        self.df = df

        if self.params is None and df is not None:
            print(
                "No specific parameters given for the splitter, using dynamic ones based on time series length"
            )
            ts_length = len(self.df)
            dynamic_params = self.calculate_splitter_params(ts_length=ts_length - 1)
            self.params = dynamic_params

        self._validate_params(self.params)
        mapping = self._get_mapping()
        splitter_class = mapping[self.method]

        try:
            self.splitter = splitter_class(**self.params)
        except Exception as e:
            raise ValueError(
                f"Failed to initialize {self.method} with parameters: {self.params}\n"
                f"Error: {e!s}"
            ) from e

        self.is_fitted = True

        return self

    def get_splits(self) -> list[tuple[pd.DataFrame, pd.DataFrame]]:
        """
        Get the train-test splits from the fitted splitter.

        This method generates a list of (train, test) splits from the input data,
        respecting the time series order. If the splitter hasn't been fitted with
        dynamic parameters, it will refit using the provided DataFrame.

        Returns
        -------
        List[Tuple[pd.DataFrame, pd.DataFrame]]
            List of (train, test) splits, where each split is a tuple of DataFrames
            with preserved datetime indexes

        Raises
        ------
        ValueError
            If splitter is not fitted
        TypeError
            If input is not a DataFrame
        """
        if self.splitter is None or self.ts_length != len(self.df):
            self.fit(self.df)

        splits = []

        df = self.df.copy()

        if isinstance(self.df.index, pd.DatetimeIndex):
            df.reset_index(inplace=True)

        for train_idx, test_idx in self.splitter.split(df):
            # Get the data using the original indices
            train_data = df.iloc[train_idx].copy()
            test_data = df.iloc[test_idx].copy()

            splits.append((train_data, test_data))
        return splits

    def get_splitter_params(self) -> dict[str, inspect.Parameter]:
        """
        Get the parameters that can be passed to the current splitter.

        This method uses Python's inspect module to get detailed information
        about the parameters of the current splitter class.

        Returns
        -------
        Dict[str, inspect.Parameter]
            Dictionary of parameter names and their Parameter objects containing:
            - name: parameter name
            - default: default value (if any)
            - annotation: type annotation
            - kind: parameter kind (POSITIONAL_ONLY, POSITIONAL_OR_KEYWORD, etc.)
        """
        splitter_class = self._get_mapping()[self.method]
        signature = inspect.signature(splitter_class.__init__)

        # Remove 'self' from parameters
        params = dict(signature.parameters)
        params.pop("self", None)

        return params

    def get_splitter_params_info(self) -> str:
        """
        Get a human-readable description of the parameters for the current splitter.

        This method generates a formatted string containing detailed information
        about each parameter of the current splitter.

        Returns
        -------
        str
            Formatted string containing parameter information including:
            - Parameter names
            - Types
            - Default values
            - Parameter kinds
        """
        params = self.get_splitter_params()

        info = [f"Parameters for {self.method}:"]
        for name, param in params.items():
            param_info = [f"  - {name}:"]

            if param.annotation != inspect.Parameter.empty:
                param_info.append(f"    Type: {param.annotation}")

            if param.default != inspect.Parameter.empty:
                param_info.append(f"    Default: {param.default}")

            if param.kind != inspect.Parameter.POSITIONAL_OR_KEYWORD:
                param_info.append(f"    Kind: {param.kind}")

            info.append("\n".join(param_info))

        return "\n".join(info)

    def calculate_splitter_params(self, ts_length: int) -> dict[str, Any]:
        """
        Calculate appropriate splitter parameters based on time series length.

        Parameters
        ----------
        ts_length : int
            Length of the time series
        method : str
            The splitting method to use

        Returns
        -------
        Dict[str, Any]
            Dictionary of parameters for the specified splitter method

        Notes
        -----
        The parameters are calculated to maximize data usage while maintaining
        reasonable validation windows:
        - For single window: Uses 80% for training, remaining for testing
        - For sliding/expanding windows: Uses 70% initial window, 10% step
        - For cutoff splitters: Creates evenly spaced cutoffs
        - For temporal split: Uses 80% for training
        """
        if self.method == "singlewindowsplitter":
            # Use 80% of data for training, remaining for testing
            split_idx = int(ts_length * 0.8)
            return {
                "fh": np.arange(start=1, stop=ts_length - split_idx + 1, step=1),
                "window_length": split_idx,
            }
        elif self.method == "cutoffsplitter":
            # Create 3 evenly spaced cutoffs using 80% of data
            n_cutoffs = 3
            max_cutoff = int(ts_length * 0.8)
            cutoffs = np.linspace(
                start=int(
                    ts_length * 0.4
                ),  # Start at 40% to ensure enough training data
                stop=max_cutoff,
                num=n_cutoffs,
                dtype=int,
            )
            return {
                "fh": np.arange(start=1, stop=ts_length - max_cutoff + 1, step=1),
                "cutoffs": cutoffs,
                "window_length": int(ts_length * 0.2),  # Minimum window size
            }
        elif self.method == "slidingwindowsplitter":
            # Use 70% initial window, 10% step
            window_length = max(3, int(ts_length * 0.7))
            step_length = max(1, int(ts_length * 0.1))
            return {
                "fh": np.arange(start=1, stop=ts_length - window_length + 1, step=1),
                "window_length": window_length,
                "step_length": step_length,
            }
        elif self.method == "expandingwindowsplitter":
            # Start with 40% initial window, expand by 10% steps
            initial_window = max(5, int(ts_length * 0.4))
            step_length = max(1, int(ts_length * 0.1))
            return {
                "fh": np.arange(start=1, stop=ts_length - initial_window + 1, step=1),
                "initial_window": initial_window,
                "step_length": step_length,
            }
        elif self.method == "expandingcutoffsplitter":
            # Calculate parameters for the expanding cutoff splitter
            initial_cutoff = int(ts_length * 0.4)  # Start at 40% of data
            step_length = int(ts_length * 0.1)  # Expand by 10% each time
            forecast_horizon = int(ts_length * 0.1)  # Use 20% of data for forecasting

            return {
                "cutoff": initial_cutoff,
                "fh": np.arange(start=1, stop=forecast_horizon + 1, step=1),
                "step_length": step_length,
            }
        elif self.method == "temporaltraintestsplitter":
            # Use 80% for training
            return {"test_size": 0.2}
        else:
            raise ValueError(f"Unknown splitter method: {self.method}")


class SplitterCV(BaseSplitter):
    def __init__(self, splitter: Splitter):
        if not splitter.is_fitted:
            raise ValueError("Splitter must be fitted")
        else:
            self.splitter = splitter
            # Get fh from the underlying splitter's parameters
            self.fh = splitter.params.get("fh", None)
            if self.fh is None:
                raise ValueError(
                    "Splitter must have a forecasting horizon (fh) parameter"
                )

    def get_n_splits(self):
        """
        Get the number of splits in the cross-validator.

        Parameters
        ----------
        X : object, default=None
            Always ignored, exists for compatibility.
        y : object, default=None
            Always ignored, exists for compatibility.
        groups : object, default=None
            Always ignored, exists for compatibility.

        Returns
        -------
        n_splits : int
            The number of splits.
        """
        return len(self.splitter.get_splits())

    @override
    def split(self):
        splits = self.splitter.get_splits()
        for train_data, test_data in splits:
            train_idx = train_data.index
            test_idx = test_data.index
            yield train_idx, test_idx
