import pandas as pd
import ruptures as rpt


def outlier_detection(series, z_threshold=3, window=11) -> pd.Series:
    """
    Enhanced detection with volatility-adjusted thresholds and trend validation
    """
    # Compute rolling volatility metrics
    series = series.sort_index().dropna()

    returns = series.pct_change()
    series = series[returns != 0]
    series = series[series > 0.1]  # we exclude penny stock
    rolling_mean = series.rolling(window, center=True).mean()
    rolling_std = series.rolling(window, center=True).std()
    # Calculate Z-scores
    z_scores = (series - rolling_mean) / rolling_std
    candidates = z_scores.abs() > z_threshold

    return series[candidates]


def statistical_change_point_detection(
    df: pd.Series,
    pen: int = 10,
    model: str = "l2",
    threshold: float = 0.7,
    min_size: int = 30,
    min_threshold: float = 1.0,
) -> pd.Series:
    """Detects abnormal changes in a time series using Pelt change point detection.

    Analyzes a pandas Series using ruptures' Pelt algorithm to identify statistical
    change points, then validates them using percentage change and minimum value thresholds.

    Args:
        df: Input time series as pandas Series. Should be numeric and ordered by time.
        pen: Penalty value for change point detection (higher values reduce sensitivity).
            Default: 5.
        model: Cost function model for change point detection. Supported values:
            'l1' (least absolute deviation), 'l2' (least squared deviation).
            Default: 'l1'.
        threshold: Minimum percentage change (0-1) between consecutive segments to
            consider as abnormal. Default: 0.7 (70%).
        min_size: Minimum number of samples between change points. Default: 30.
        min_threshold: Minimum mean value required in both segments to validate
            a change point (avoids flagging low-value fluctuations). Default: 1.0.

    Returns:
        tuple[bool, list[int]]: Contains:
            - bool: True if any validated abnormal changes detected
            - list[int]: Indices of validated change points (empty if none)

    Example:
        >>> ts = pd.Series([1.0, 1.1, 1.2, 3.0, 3.1, 3.2])
        >>> detected, points = detect_abnormal_changes(ts, threshold=0.5)
        >>> print(detected, points)
        True [3]

    Note:
        Base on https://medium.com/@enginsorhun/decoding-market-shifts-detecting-structural-breaks-ii-2b77bdafd064.
    """
    changes = []

    if len(df) < min_size:
        return df.iloc[changes]

    df = df.sort_index()

    # Initialize and fit Pelt model
    algo = rpt.Pelt(model=model, min_size=min_size).fit(df.values)
    change_points = algo.predict(pen=pen)

    # If no changes detected
    if len(change_points) == 0:
        return (False, [])

    # Calculate percentage changes between segments
    segments = [1] + change_points

    for i in range(1, len(segments) - 1):
        previous_segment = df.iloc[segments[i - 1] : segments[i] - 1].mean()
        next_segment = df.iloc[segments[i] : segments[i + 1] - 1].mean()
        pct_change = abs(next_segment - previous_segment) / previous_segment
        if next_segment > min_threshold and previous_segment > min_threshold and pct_change > threshold:
            changes.append(segments[i])
    return df.iloc[changes]
