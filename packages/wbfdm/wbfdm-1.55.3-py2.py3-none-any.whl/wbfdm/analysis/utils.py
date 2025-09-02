from contextlib import suppress

import pandas as pd


def normalize_series(series: pd.Series, base_series: pd.Series | None = None) -> pd.Series:
    """
    Normalize the given time series by aligning and adjusting its values based on a base series.

    Args:
        series (pd.Series): The time series to be normalized.
        base_series (pd.Series | None): The base time series for alignment and normalization.
            If None, no alignment or normalization is performed.

    Returns:
        pd.Series: The normalized time series.

    Note:
        - If base_series is provided, the function aligns the series with the base_series and normalizes
          the values based on the first value of both series.
        - If the series index is older than the base series index, the function trims the series accordingly.
        - If the first value of the series is zero or if the base series first value is zero, no normalization
          is performed.
    """
    if base_series is not None and not base_series.empty:
        with suppress(KeyError, IndexError):
            # Ensure the series is not older than the the base serie
            series = series.loc[series.index >= base_series.index.min()]
            # if a base serie is provided and normalization is possible, we align the timeseries
            if series.iloc[0] != 0 and (normalize_factor := base_series.iloc[0]):
                series = series / series.iloc[0] * normalize_factor
    return series
