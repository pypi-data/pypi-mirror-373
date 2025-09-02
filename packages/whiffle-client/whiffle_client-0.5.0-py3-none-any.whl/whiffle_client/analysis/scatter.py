import numpy as np
import matplotlib as mpl


def plot_one_to_one_line(ax, x, y, method, **kw):
    if method in [None, "max"]:
        start = min(np.nanmin(x), np.nanmin(y))
        end = max(np.nanmax(x), np.nanmax(y))
    elif method == "percentile":
        percmin, percmax = 1, 99
        start = min(np.nanpercentile(x, percmin), np.nanpercentile(y, percmin))
        end = max(np.nanpercentile(x, percmax), np.nanpercentile(y, percmax))
    elif method == "margin":
        margin = 0.1
        start = (1 - margin) * min(np.nanmin(x), np.nanmin(y))
        end = (1 + margin) * max(np.nanmax(x), np.nanmax(y))
    else:
        raise ValueError(method)

    ax.plot([start, end], [start, end], "-", **kw)

    ax.set_xlim(start, end)
    ax.set_ylim(start, end)

    ax.set_aspect(1)


def scatter_density(
    ax,
    x,
    y,
    cmap="viridis",
    one_to_one=None,
    s=1,
    edgecolor="none",
    sort=False,
    colour_kwargs={},
    **kw,
):
    """Efficient scatter density algorithm."""

    x, y = x.to_numpy().reshape(-1, 1), y.to_numpy().reshape(-1, 1)

    inds = np.isfinite(x) & np.isfinite(y)

    x = x[inds]
    y = y[inds]

    if sort or colour_kwargs:
        x, y, cvals = hist_colouring_sort(x, y, **colour_kwargs)
        C = ax.scatter(x, y, c=cvals, cmap=cmap, edgecolor=edgecolor, s=s, **kw)
    else:
        cvals = hist_colouring(x, y, 1000, cmap, 15)
        C = ax.scatter(x, y, c=cvals, edgecolor=edgecolor, s=s, **kw)

    if one_to_one is not False:
        plot_one_to_one_line(ax, x, y, method=one_to_one, color="k")

    return C


def hist_colouring(
    xarray, yarray, nbins=300, cmap="inferno", smoother=3, fnc=None, norm=None
):
    """
    Explanation on `norm`:

    Purpose:
      To have multiple figures showing data of different min/maxes (thus dif-
      ferent bin-edges) and different "maximum bin value"s, show comparable
      color behavior for comparable point-densities.

    Implications:
      Color behavior normalization is by default determined by the maximum bin-
      count. This bin (or smoothed bin) will have the highest value color.
      The point-density is the number of points per area. It is therefore
      necessary to also consider the area of the bins in the normalization.
    """
    cmap = mpl.cm.get_cmap(cmap)

    def bin_indices(data, bins):
        ixs = np.zeros(len(data), int) - 1
        for i, bini in enumerate(bins[:-1]):
            inbin = (bini <= data) * (data < bins[i + 1])
            if i == len(bins) - 1:
                inbin *= data == bins[i + 1]
            ixs += inbin * (i + 1)
        return ixs

    mask = np.isfinite(xarray) & np.isfinite(yarray)
    xarray = xarray[mask]
    yarray = yarray[mask]

    xmin = np.min(xarray)
    xmax = np.max(xarray)
    ymin = np.min(yarray)
    ymax = np.max(yarray)

    xbins = np.linspace(
        xmin - (xmax - xmin) / (nbins * 10),
        xmax + (xmax - xmin) / (nbins * 10),
        nbins + 1,
    )
    ybins = np.linspace(
        ymin - (ymax - ymin) / (nbins * 10),
        ymax + (ymax - ymin) / (nbins * 10),
        nbins + 1,
    )

    hist2d, _, _ = np.histogram2d(xarray, yarray, bins=[xbins, ybins])

    if fnc is not None:
        hist2d = fnc(hist2d)
    x_ix = bin_indices(xarray, xbins)
    y_ix = bin_indices(yarray, ybins)

    if smoother:
        smoothhist = np.zeros(len(x_ix))
        for i, (ix, iy) in enumerate(zip(x_ix, y_ix)):
            smoothhist[i] = np.mean(
                hist2d[
                    max(0, ix - smoother) : ix + smoother + 1,
                    max(0, iy - smoother) : iy + smoother + 1,
                ]
            )

        if norm is None:
            norm = np.max(smoothhist)
        else:
            dA = (xbins[1] - xbins[0]) * (ybins[1] - ybins[0]) * nbins**2
            norm *= dA

        return cmap(smoothhist / norm)

    else:
        if norm is None:
            norm = np.max(hist2d)
        else:
            dA = (xbins[1] - xbins[0]) * (ybins[1] - ybins[0]) * nbins**2
            norm *= dA

        return cmap(hist2d[x_ix, y_ix] / norm)


def hist_colouring_sort(x, y, nbins=300, zmax=None, fnc=None):
    """
    Alternative to hist_colouring that uses sorting instead of smoothing
    and allows for a colorbar to be added easily
    """
    if fnc == "log":
        fnc = lambda z: np.log10(z, where=z > 0)

    hist2d, locx, locy = np.histogram2d(x, y, bins=[nbins, nbins])

    if zmax:
        hist2d = hist2d.clip(0, zmax)

    if fnc:
        hist2d = fnc(hist2d)

    # Sorting the points such that that the largest bins are drawn on top
    hist2d = np.array(
        [
            hist2d[np.argmax(a <= locx[1:]), np.argmax(b <= locy[1:])]
            for a, b in zip(x, y)
        ]
    )
    idx = hist2d.argsort()
    x, y, hist2d = x[idx], y[idx], hist2d[idx]

    return x, y, hist2d
