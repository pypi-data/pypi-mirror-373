import warnings

import numpy as np
import pandas as pd
import seaborn as sns
import xarray as xr
from matplotlib import pyplot as plt

from whiffle_client.analysis.skill import skill, skill_str
from whiffle_client.analysis.utils import (
    mean_wind_speed_by_hour_of_the_day,
    weibull_params_from_samples,
    weibull_pdf_from_params,
    wind_rose_frequency,
    wind_speed_histogram,
)


def _concat_wind_data(
    measured_wind_speed_series,
    aspire_wind_speed_series,
    concurrent,
):
    wind_speed_data = [
        measured_wind_speed_series.rename("measured"),
        aspire_wind_speed_series.rename("whiffle-wind"),
    ]
    wind_speed_df = pd.concat(wind_speed_data, axis=1)
    if concurrent:
        wind_speed_df = wind_speed_df.dropna()
    return wind_speed_df


def _wind_rose_set_yticks(ax, yticks=None):
    if yticks is not None:
        ax.set_yticks(yticks)

    labels = ["{:2.0f}%".format(item) for item in ax.get_yticks()]

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ax.set_yticklabels(labels, fontsize=8)
    return ax


def _rose_dir_bins(nsector):
    angle = 360.0 / nsector
    dir_bin_centers = np.arange(-angle / 2, 360.0 + angle, angle, dtype=float)
    dir_bin_edges = list(dir_bin_centers)
    dir_bin_edges.pop(-1)
    dir_bin_edges[0] = dir_bin_edges.pop(-1)
    dir_bin_centers[0] = 0.0

    return dir_bin_centers, dir_bin_edges


def _rose_histogram(
    direction, var, nsector, wind_speed_bin_edges, normed=False, blowto=False
):
    """
    Returns an array where, for each sector of wind
    (centred on the north), we have the number of time the wind comes with a
    particular var (speed, polluant concentration, ...).
    * direction : 1D array - directions the wind blows from, North centred
    * var : 1D array - values of the variable to compute. Typically the wind
        speeds
    * wind_speed_bin_edges : list - list of var category against we're going to compute the table
    * nsector : integer - number of sectors
    * normed : boolean - The resulting table is normed in percent or not.
    * blowto : boolean - Normaly a windrose is computed with directions
    as wind blows from. If true, the table will be reversed (usefull for
    pollutantrose)

    """
    if len(var) != len(direction):
        raise (ValueError("var and direction must have same length"))

    dir_bin_centers, dir_bin_edges = _rose_dir_bins(nsector)

    var_bins = list(wind_speed_bin_edges)
    var_bins = [-np.inf] + var_bins + [np.inf]

    if blowto:
        direction = direction + 180.0
        direction[direction >= 360.0] = direction[direction >= 360.0] - 360

    table = np.histogram2d(
        x=var, y=direction, bins=[var_bins, dir_bin_centers], density=False
    )[0]
    # add the last value to the first to have the table of North winds
    table[:, 0] = table[:, 0] + table[:, -1]
    # and remove the last col
    table = table[:, :-1]
    if normed:
        table = table * 100 / table.sum()

    return dir_bin_edges, var_bins, table


def _plot_scatter_density_hist(
    x,
    y,
    ax=None,
    add_skill_str=True,
    fancy_skill_str=False,
    cmap=plt.cm.inferno,
    one_to_one=True,
    normalize=1.0,
):
    def _hist_colouring(
        xarray, yarray, nbins=1000, cmap=plt.cm.inferno, smoother=15, fnc=None
    ):
        """Helper function to generate a colored histogram."""

        def bin_indices(data, bins):
            ixs = np.zeros(len(data), int) - 1
            for i, bini in enumerate(bins[:-1]):
                inbin = (bini <= data) * (data < bins[i + 1])
                if i == len(bins) - 1:
                    inbin *= data == bins[i + 1]
                ixs += inbin * (i + 1)
            return ixs

        xarray = xarray[np.invert(np.isnan(xarray) | np.isnan(yarray))]
        yarray = yarray[np.invert(np.isnan(xarray) | np.isnan(yarray))]

        xbins = np.linspace(
            np.floor(np.min(xarray)) - 0.1, np.ceil(np.max(xarray)) + 0.1, nbins + 1
        )
        ybins = np.linspace(
            np.floor(np.min(yarray)) - 0.1, np.ceil(np.max(yarray)) + 0.1, nbins + 1
        )
        hist2d, _, _ = np.histogram2d(xarray, yarray, bins=[xbins, ybins])
        if fnc is not None:
            hist2d = fnc(hist2d)
        x_ix = bin_indices(xarray, xbins)
        y_ix = bin_indices(yarray, ybins)

        if smoother:
            smoothhist = np.zeros(len(x_ix))
            for i, (ix, iy) in enumerate(zip(x_ix, y_ix)):
                # smoothhist[i] = np.sum(hist2d[ix-smoother:ix+smoother+1,iy-smoother:iy+smoother+1])
                smoothhist[i] = np.mean(
                    hist2d[
                        max(0, ix - smoother) : ix + smoother + 1,
                        max(0, iy - smoother) : iy + smoother + 1,
                    ]
                )
            return cmap(smoothhist / np.max(smoothhist))
        else:
            return cmap(hist2d[x_ix, y_ix] / np.max(hist2d))

    inds = np.isfinite(x) & np.isfinite(y)

    x = x[inds]
    y = y[inds]

    cvals = _hist_colouring(x, y, nbins=1000, cmap=cmap, smoother=15, fnc=None)

    ax.scatter(x, y, c=cvals, edgecolor=None, s=1)

    my_skill_names = {"bias": "bias", "corr2": r"$R^2$", "MAE": "MAE", "RMSE": "RMSE"}

    def my_skill_str(a, b, skill_names, norm=None):
        msg = ""

        msg += "# of data points = {:d}\n".format(a.size)

        msg += "mean(a) = {:.4f}\n".format(float(np.nanmean(a)))
        msg += "mean(b) = {:.4f}\n".format(float(np.nanmean(b)))

        for score, value in skill(a, b, norm).items():
            if score in skill_names:
                msg += "{} = {:.4f}\n".format(skill_names[score], float(value))

        return msg.strip()

    if add_skill_str:
        if fancy_skill_str:
            skill_str_value = my_skill_str(
                x, y, my_skill_names, normalize
            )  # y is model
            props = dict(boxstyle="round", facecolor="white")

            ax.text(
                0.05,
                0.95,
                skill_str_value,
                transform=ax.transAxes,
                fontsize=10,
                verticalalignment="top",
                bbox=props,
            )

        else:
            skill_str_value = skill_str(y, x, norm=normalize)  # y is model

            props = dict(boxstyle="round", facecolor="white")

            ax.text(
                0.05,
                0.95,
                skill_str_value,
                transform=ax.transAxes,
                fontsize=6,
                verticalalignment="top",
                bbox=props,
            )

    if one_to_one:
        start = min(np.nanmin(x), np.nanmin(y))
        end = max(np.nanmax(x), np.nanmax(y))

        ax.plot([start, end], [start, end], "-k", zorder=4)

        ax.set_xlim(start, end)
        ax.set_ylim(start, end)

        ax.set_aspect(1)

    ax.set_xlabel("Measured wind speed [m/s]")
    ax.set_ylabel("Whiffle-wind wind speed [m/s]")
    ax.set_title("Wind speed scatter density plot with metrics")
    ax.grid()

    return ax


def plot_weibull_pdf_comparison(
    measured_wind_speed_series: pd.Series,
    aspire_wind_speed_series: pd.Series,
    concurrent: bool = True,
    ax: plt.axes = None,
) -> plt.axes:
    """Fit a Weibull distribution to the data and plot the PDF.

    Parameters
    ----------
    measured_wind_speed_series : pd.Series
        Measured wind speed series.
    aspire_wind_speed_series : pd.Series
        Simulated wind speed series.
    concurrent : bool, optional
        If True, compare concurrent wind speeds i.e. an intersection of
        measured and simulated data on the time index will be performed
        before plotting.
    ax : plt.axes, optional
        Matplotlib axes.

    Returns
    -------
    plt.axes
        Matplotlib axes with the plot.
    """
    if ax is None:
        _, ax = plt.subplots()
    wind_speed_df = _concat_wind_data(
        measured_wind_speed_series,
        aspire_wind_speed_series,
        concurrent,
    )
    weibull_params_df = wind_speed_df.apply(
        lambda x: pd.Series(
            weibull_params_from_samples(x),
            index=["k", "A"],
        )
    )
    x_pdf = np.linspace(0, np.ceil(wind_speed_df.max().max()), 200)
    weibull_pdf_df = weibull_params_df.apply(
        lambda x: pd.Series(
            weibull_pdf_from_params(x_pdf, *x[["k", "A"]].tolist()),
            index=x_pdf,
        )
    )
    weibull_pdf_df.columns = [
        f'{c}:\nk={weibull_params_df[c]["k"]:.2f}\nA={weibull_params_df[c]["A"]:.2f} m/s'
        for c in weibull_pdf_df.columns
    ]
    weibull_pdf_df.plot(ax=ax)
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    ax.set_xlabel("Wind speed [m/s]")
    ax.set_ylabel("Weibull pdf [-]")
    ax.set_title("Fitted Weibull PDF comparison on wind speed")
    ax.grid()
    return ax


def plot_wind_speed_distribution_comparison(
    measured_wind_speed_series: pd.Series,
    aspire_wind_speed_series: pd.Series,
    concurrent: bool = True,
    bin_width: float = 1.0,
    kind: str = "bar",
    ax: plt.Axes = None,
) -> plt.Axes:
    """Compare wind speed distributions between measured and simulated data.

    Notes
    -----
    When 'kind' parameter is set to 'line', each point correspond to the
    histogram bin frequency (not the density). The 'line' plot represents
    the same underlying data as the 'bar' plot but is helpful for comparison.

    Parameters
    ----------
    measured_wind_speed_series : pd.Series
        Measured wind speed series.
    aspire_wind_speed_series : pd.Series
        Simulated wind speed series.
    concurrent : bool, optional
        If True, compare concurrent wind speeds i.e. an intersection of
        measured and simulated data on the time index will be performed
        before plotting.
    bin_width : float, optional
        Binning width.
    kind : str, optional
        Whether to plot distributions as 'bar' or 'line'.
    ax : plt.Axes, optional
        Matplotlib axes.

    Returns
    -------
    plt.Axes
        Matplotlib axes with the plot.
    """
    allowed_kind = ["bar", "line"]
    if kind not in allowed_kind:
        raise ValueError(f"'kind' parameter should be in {allowed_kind}")
    if ax is None:
        _, ax = plt.subplots()
    wind_speed_df = _concat_wind_data(
        measured_wind_speed_series,
        aspire_wind_speed_series,
        concurrent,
    )
    ws_hist_df = wind_speed_df.apply(wind_speed_histogram, bin_width=bin_width)
    ws_hist_df = ws_hist_df.fillna(0)
    ws_hist_df.index = ws_hist_df.index.map(lambda x: x.mid)
    ws_hist_df = ws_hist_df / ws_hist_df.sum()
    if kind == "line":
        ws_hist_df.plot(marker=".", ax=ax, legend=True)
    elif kind == "bar":
        ws_hist_df.plot.bar(ax=ax, legend=True)
    ax.set_xlabel("Wind speed bin center [m/s]")
    ax.set_ylabel("Frequency [-]")
    ax.set_title("Wind speed histogram comparison")
    ax.grid()
    return ax


def plot_wind_rose_frequency_comparison(
    measured_wind_direction_series: pd.Series,
    aspire_wind_direction_series: pd.Series,
    concurrent: bool = True,
    n_sectors: int = 12,
    ax: plt.Axes = None,
) -> plt.Axes:
    """Compare sector frequencies between measured and simulated data.

    Notes
    -----
    This plot is in polar projection.

    Parameters
    ----------
    measured_wind_direction_series : pd.Series
        Measured wind direction series.
    aspire_wind_direction_series : pd.Series
        Simulated wind direction series.
    concurrent : bool, optional
        If True, compare concurrent wind directions i.e. an intersection of
        measured and simulated data on the time index will be performed
        before plotting.
    n_sectors : int, optional
        Number of sectors to use for the wind rose.
    ax : plt.Axes, optional
        Matplotlib axes.

    Returns
    -------
    plt.Axes
        Matplotlib axes with the plot.
    """
    if ax is None:
        _, ax = plt.subplots(subplot_kw={"projection": "polar"})
    wind_dir_df = _concat_wind_data(
        measured_wind_direction_series,
        aspire_wind_direction_series,
        concurrent,
    )
    wind_rose_df = wind_dir_df.apply(
        wind_rose_frequency,
        n_sectors=n_sectors,
    )
    wind_rose_df = wind_rose_df / wind_rose_df.sum()
    wind_rose_df_rad = wind_rose_df.copy()
    wind_rose_df_rad.index = wind_rose_df_rad.index.map(lambda x: np.deg2rad(x.mid))
    for c in wind_rose_df_rad.columns:
        x = wind_rose_df_rad.index.to_series()
        x = pd.concat([x, x.iloc[[0]]]).to_numpy()
        y = wind_rose_df_rad[c]
        y = pd.concat([y, y.iloc[[0]]]).to_numpy()
        ax.plot(
            x,
            y,
            marker=".",
            label=c,
        )
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.grid(True)
    ax.legend(loc="center left", bbox_to_anchor=(1.1, 0.5))
    ax.set_xlabel("Wind direction bin center [m/s]")
    ax.set_ylabel("Frequency [-]", labelpad=30)
    ax.set_title("Wind rose frequency comparison")
    return ax


def plot_wind_speed_scatter(
    measured_wind_speed_series: pd.Series,
    aspire_wind_speed_series: pd.Series,
    ax: plt.Axes = None,
) -> plt.Axes:
    """Scatter plot of measured and simulated wind speeds.

    Parameters
    ----------
    measured_wind_speed_series : pd.Series
        Measured wind speed series.
    aspire_wind_speed_series : pd.Series
        Simulated wind speed series.
    ax : plt.Axes, optional
        Matplotlib axes.

    Returns
    -------
    plt.Axes
        Matplotlib axes with the plot.
    """
    if ax is None:
        _, ax = plt.subplots()
    wind_speed_df = _concat_wind_data(
        measured_wind_speed_series,
        aspire_wind_speed_series,
        concurrent=True,
    )
    ws_min = np.floor(wind_speed_df.min().min())
    ws_max = np.ceil(wind_speed_df.max().max())

    ax.set_aspect("equal")
    wind_speed_df.plot.scatter(
        x="measured",
        y="whiffle-wind",
        s=10,
        alpha=0.2,
        ax=ax,
    )
    ax.plot([ws_min, ws_max], [ws_min, ws_max], "-", color="k", lw=0.5)
    ax.set_xlim(ws_min, ws_max)
    ax.set_ylim(ws_min, ws_max)
    ax.set_xlabel("Measured wind speed [m/s]")
    ax.set_ylabel("Whiffle-wind wind speed [m/s]")
    ax.set_title("Wind speed scatter plot")
    ax.grid()
    return ax


def plot_wind_speed_scatter_density(
    measured_wind_speed_series: pd.Series,
    aspire_wind_speed_series: pd.Series,
    ax: plt.Axes = None,
) -> plt.Axes:
    """Density plot of measured and simulated wind speeds.

    Notes
    -----
    This plot is particularly useful when the data contains many samples.

    Parameters
    ----------
    measured_wind_speed_series : pd.Series
        Measured wind speed series.
    aspire_wind_speed_series : pd.Series
        Simulated wind speed series.
    ax : plt.Axes, optional
        Matplotlib axes.

    Returns
    -------
    plt.Axes
        Matplotlib axes with the plot.
    """
    if ax is None:
        _, ax = plt.subplots()
    return _plot_scatter_density_hist(
        measured_wind_speed_series,
        aspire_wind_speed_series,
        ax=ax,
    )


def plot_wind_speed_diurnal_cycle_comparison(
    measured_wind_speed_series: pd.Series,
    aspire_wind_speed_series: pd.Series,
    concurrent: bool = True,
    ax: plt.Axes = None,
) -> plt.Axes:
    """Compare mean diurnal cycle of measured and simulated wind speeds.

    Notes
    -----
    Each point in the plot represents the mean wind speed grouped
    by hour of the day.

    Parameters
    ----------
    measured_wind_speed_series : pd.Series
        Measured wind speed series.
    aspire_wind_speed_series : pd.Series
        Simulated wind speed series.
    concurrent : bool, optional
        If True, compare concurrent wind speeds i.e. an intersection of
        measured and simulated data on the time index will be performed
        before plotting.
    ax : plt.Axes, optional
        Matplotlib axes.

    Returns
    -------
    plt.Axes
        Matplotlib axes with the plot.
    """
    if ax is None:
        _, ax = plt.subplots()
    wind_speed_df = _concat_wind_data(
        measured_wind_speed_series,
        aspire_wind_speed_series,
        concurrent,
    )
    wind_speed_diurnal_cycle = wind_speed_df.apply(
        mean_wind_speed_by_hour_of_the_day,
    )
    wind_speed_diurnal_cycle.plot(marker=".", ax=ax)
    ax.set_xlabel("Hour of the day [-]")
    ax.set_ylabel("Mean wind speed by hour of the day [m/s]")
    ax.set_title("Wind speed diurnal cycle comparison")
    ax.grid()
    return ax


def plot_wind_speed_vertical_profile_comparison(
    measured_wind_speed_da: xr.DataArray,
    aspire_wind_speed_da: xr.DataArray,
    concurrent: bool = True,
    ax: plt.Axes = None,
) -> plt.Axes:
    """Compare vertical profiles of measured and simulated wind speeds.

    Notes
    -----
        - Data arrays should contain time and height dimensions.
        - Data arrays can have different heights.
        - If 'concurrent' is True, time intersection between all heights
          and data arrays will be performed.

    Parameters
    ----------
    measured_wind_speed_da : xr.DataArray
        Measured wind speed data array.
    aspire_wind_speed_da : xr.DataArray
        Simulated wind speed data array.
    concurrent : bool, optional
        If True, compare concurrent wind speeds i.e. an intersection of
        measured and simulated data on the time index will be performed
        before plotting.
    ax : bool, optional
        Matplotlib axes.

    Returns
    -------
    plt.Axes
        Matplotlib axes with the plot.
    """
    if ax is None:
        _, ax = plt.subplots()
    measured_wind_speed_da = measured_wind_speed_da.dropna("height", how="all")
    if concurrent:
        measured_time_idx = measured_wind_speed_da.dropna("time")["time"].to_index()
        aspire_time_idx = aspire_wind_speed_da.dropna("time")["time"].to_index()
        concurrent_time_idx = measured_time_idx.intersection(aspire_time_idx)
        measured_wind_speed_da = measured_wind_speed_da.sel(time=concurrent_time_idx)
        aspire_wind_speed_da = aspire_wind_speed_da.sel(time=concurrent_time_idx)
    measured_wind_speed_da.mean("time", keep_attrs=True).plot(
        y="height",
        label="measured",
        marker=".",
        ax=ax,
    )
    aspire_wind_speed_da.mean("time", keep_attrs=True).plot(
        y="height",
        label="whiffle-wind",
        marker=".",
        ax=ax,
    )
    ax.legend()
    ax.set_xlabel("Mean wind speed [m/s]")
    ax.set_title("Mean wind speed vertical profile comparison")
    ax.grid()
    return ax


def plot_wind_speed_quantiles_vertical_profile_comparison(
    measured_wind_speed_da: xr.DataArray,
    aspire_wind_speed_da: xr.DataArray,
    concurrent: bool = True,
    quantiles: list[float] = [0.1, 0.5, 0.9],
    ax: plt.Axes = None,
) -> plt.Axes:
    """Compare vertical profiles of measured and simulated wind speeds.

    Notes
    -----
        - Data arrays should contain time and height dimensions.
        - Data arrays can have different heights.
        - If 'concurrent' is True, time intersection between all heights
          and data arrays will be performed.

    Parameters
    ----------
    measured_wind_speed_da : xr.DataArray
        Measured wind speed data array.
    aspire_wind_speed_da : xr.DataArray
        Simulated wind speed data array.
    concurrent : bool, optional
        If True, compare concurrent wind speeds i.e. an intersection of
        measured and simulated data on the time index will be performed
        before plotting.
    quantiles: list[float], optional
        Quantiles to plot.
    ax : bool, optional
        Matplotlib axes.

    Returns
    -------
    plt.Axes
        Matplotlib axes with the plot.
    """
    if ax is None:
        _, ax = plt.subplots()
    measured_wind_speed_da = measured_wind_speed_da.dropna("height", how="all")
    if concurrent:
        measured_time_idx = measured_wind_speed_da.dropna("time")["time"].to_index()
        aspire_time_idx = aspire_wind_speed_da.dropna("time")["time"].to_index()
        concurrent_time_idx = measured_time_idx.intersection(aspire_time_idx)
        measured_wind_speed_da = measured_wind_speed_da.sel(time=concurrent_time_idx)
        aspire_wind_speed_da = aspire_wind_speed_da.sel(time=concurrent_time_idx)
    data_da = xr.concat(
        [
            measured_wind_speed_da.assign_coords(source="measured"),
            aspire_wind_speed_da.assign_coords(source="whiffle-wind"),
        ],
        dim="source",
    )
    quantiles_df = data_da.quantile(quantiles, dim="time").to_series().reset_index()
    ax = sns.lineplot(
        data=quantiles_df,
        x="horizontal-wind-speed",
        y="height",
        hue="source",
        style="quantile",
        marker=".",
        markeredgecolor=None,
        orient="y",
        ax=ax,
    )
    ax.legend()
    ax.set_xlabel("Wind speed quantiles [m/s]")
    ax.set_ylabel("Height [m]")
    ax.set_title("Wind speed quantiles vertical profile comparison")
    ax.grid()
    return ax


def plot_wind_rose(
    wind_direction_series: pd.Series,
    wind_speed_series: pd.Series,
    wind_speed_bin_edges: np.array = np.arange(0, 30, 5),
    nsector: int = 16,
    varunit: str = "m/s",
    cmap: str = "viridis",
    ax: plt.Axes = None,
) -> plt.Axes:
    """Plot a colored wind rose.

    Parameters
    ----------
    wind_direction_series : pd.Series
        Wind direction.
    wind_speed_series : pd.Series
        Wind speed.
    wind_speed_bin_edges : np.array, optional
        Bin edges for color bins of wind_speed_series.
    nsector : int, optional
        Number of sector for the wind rose.
    varunit : str, optional
        Unit for wind speed.
    cmap : str, optional
        Matplotlib colormap to use.
    ax : plt.Axes, optional
        Axis for the plot.

    Returns
    -------
    plt.Axes
        Matplotlib axes with the plot.
    """
    if ax is None:
        _, ax = plt.subplots(subplot_kw={"projection": "polar"})

    dir_bin_edges, var_bins, table = _rose_histogram(
        wind_direction_series,
        wind_speed_series,
        nsector,
        wind_speed_bin_edges,
        normed=True,
    )

    nbins = len(var_bins) - 1
    colors = plt.get_cmap(cmap)(np.linspace(0.1, 0.9, nbins))

    width = 0.8 * 2 * np.pi / nsector
    angles = np.arange(0, -2 * np.pi, -2 * np.pi / nsector) + np.pi / 2

    offset = np.zeros(nsector)
    for bin in range(nbins):
        zorder = -1000 + nbins - bin
        if bin < 1:
            binlabel = "< {:2.1f} {}".format(var_bins[1], varunit)
        elif bin < nbins - 1:
            binlabel = "{:2.1f}-{:2.1f} {}".format(
                var_bins[bin], var_bins[bin + 1], varunit
            )
        else:
            binlabel = "> {:2.1f} {}".format(
                var_bins[bin], varunit
            )  # adjust final bin label
        ax.bar(
            angles,
            table[bin, :],
            width=width,
            color=colors[bin],
            bottom=offset,
            zorder=zorder,
            linewidth=0,
            label=binlabel,
        )
        offset += table[bin, :]

    theta_angles = np.arange(0, 360, 45)
    theta_labels = ["E", "N-E", "N", "N-W", "W", "S-W", "S", "S-E"]
    ax.set_thetagrids(
        angles=theta_angles, labels=theta_labels
    )  # Fails if you don't pass polar-projected ax

    ax = _wind_rose_set_yticks(ax)

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    ax.legend(loc="upper left", bbox_to_anchor=(1.05, 1.0))

    return ax


def plot_timeseries_comparison(
    measured_series: pd.Series,
    aspire_series: pd.Series,
    ax: plt.Axes = None,
) -> plt.Axes:
    """Plot time series comparison.

    Parameters
    ----------
    measured_series : pd.Series
        Measured time series.
    aspire_series : pd.Series
        Whiffle wind time series.
    ax : plt.Axes, optional
        Axis for the plot.

    Returns
    -------
    plt.Axes
        Matplotlib axes with the plot.
    """
    if ax is None:
        _, ax = plt.subplots()

    if measured_series.name != aspire_series.name:
        raise ValueError("Series names must match.")

    ax = measured_series.plot(ax=ax, label="measured")
    ax = aspire_series.plot(ax=ax, label="whiffle-wind")
    ax.legend()
    ax.set_xlabel("time")
    ax.set_ylabel(measured_series.name)
    ax.set_title("Wind speed comparison")
    ax.grid()
    return ax
