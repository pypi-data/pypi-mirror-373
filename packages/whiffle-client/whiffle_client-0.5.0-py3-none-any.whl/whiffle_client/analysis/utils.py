import numpy as np
import pandas as pd
from scipy.stats import exponweib


def wind_speed_histogram(
    wind_speed_series: pd.Series,
    bin_width: float = 1.0,
) -> pd.Series:
    """Calculate wind speed histogram from wind speed series.

    Parameters
    ----------
    wind_speed_series : pd.Series
        Wind speed series.
    bin_width : float, optional
        Bin width

    Returns
    -------
    pd.Series
        Wind speed histogram with IntervalIndex.
    """
    ws_min = 0
    ws_max = np.ceil(wind_speed_series.max())
    bins = np.arange(ws_min, ws_max + 1, bin_width) - bin_width / 2
    ws_cut = pd.cut(wind_speed_series, bins=bins)
    ws_hist = ws_cut.value_counts().sort_index()
    return ws_hist


def wind_rose_frequency(
    wind_direction_series: pd.Series,
    n_sectors: int = 12,
) -> pd.Series:
    """Calculate wind rose frequency from wind direction series.

    Parameters
    ----------
    wind_direction_series : pd.Series
        Wind direction series.
    n_sectors : int, optional
        Number of sectors for the wind rose.

    Returns
    -------
    pd.Series
        Wind rose frequency with IntervalIndex.
    """
    dir_bin_width = 360 / n_sectors
    dir_bins = np.linspace(0, 360 + dir_bin_width, n_sectors + 2)
    dir_bins = dir_bins - dir_bin_width / 2
    dir_intervals = pd.IntervalIndex.from_breaks(dir_bins)
    wd_cut = pd.cut(wind_direction_series, bins=dir_intervals)
    wd_hist = wd_cut.value_counts().sort_index()
    wd_hist[dir_intervals[0]] = wd_hist[dir_intervals[0]] + wd_hist[dir_intervals[-1]]
    wd_hist.drop(dir_intervals[-1], inplace=True)
    return wd_hist


def mean_wind_speed_by_hour_of_the_day(
    wind_speed_series: pd.Series,
) -> pd.Series:
    """Mean wind speed by hour of the day.

    Parameters
    ----------
    wind_speed_series : pd.Series
        Wind speed series.

    Returns
    -------
    pd.Series
        Mean wind speed by hour of the day.
    """
    return wind_speed_series.groupby(wind_speed_series.index.hour).mean()


def weibull_params_from_samples(data: pd.Series) -> tuple[float, float]:
    """Estimate Weibull parameters from samples.

    Parameters
    ----------
    data : pd.Series
        Data samples.

    Returns
    -------
    tuple[float, float]
        Shape and scale parameters of the Weibull distribution.
    """
    _, k, _, A = exponweib.fit(data.dropna(), fa=1, floc=0)
    return k, A


def weibull_pdf_from_params(
    x_pdf: pd.Series,
    k: float,
    A: float,
) -> pd.Series:
    """Estimate PDF of a Weibull distribution.

    Parameters
    ----------
    x_pdf : pd.Series
        Random variable values.
    k : float
        Scale parameter.
    A : float
        Shape parameter.

    Returns
    -------
    pd.Series
        PDF of the Weibull distribution at `x_pdf`.
    """
    return exponweib.pdf(x_pdf, 1, k, 0, A)


def mean_angle(a, weight=None, axis=None):
    """
    When averaging wind directions, `weight` is the wind speed
    """
    c = np.pi / 180

    if weight is None:
        weight = np.ones(a.shape)

    xs = np.cos(a * c) * weight
    ys = np.sin(a * c) * weight

    return np.arctan2(np.nanmean(ys, axis=axis), np.nanmean(xs, axis=axis)) / c % 360
