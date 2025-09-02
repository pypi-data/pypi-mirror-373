import collections
import warnings

import numpy as np
from sklearn.metrics import r2_score


def get_metric_name(metric_name):
    names = {
        "npoints": "# of data points",
        "mean(a)": "mean(a)",
        "mean(b)": "mean(b)",
        "bias": "bias",
        "r2": r"$R^2$",
        "pearsonr": r"$\rho$",
        "nmae": "nMAE",
        "mae": "MAE",
        "rmse": "RMSE",
        "nrmse": "nRMSE",
        "rmsd": "RMSD",
        "nrmsd": "nRMSD",
    }
    return names[metric_name]


def get_metric(metric_name):
    return globals()[metric_name]


def normalize(x, axis=None, norm=None):
    if norm is None:
        return 1.0
    elif norm == "mean":
        return np.nanmean(x, axis=axis)
    elif isinstance(norm, float):
        return norm
    else:
        raise ValueError("expected 'mean' or float")


def rmsd(x, y, axis=None, norm=None):
    y_bias = bias(x, y, axis=axis)

    y_minus_bias = y - y_bias

    return rmse(x, y_minus_bias, axis=axis) / normalize(x, axis=axis, norm=norm)


def rmse(x, y, axis=None, norm=None):
    return np.sqrt(((x - y) ** 2).mean()) / normalize(x, axis=axis, norm=norm)


def bias(x, y, axis=None, norm=None):
    return (y.mean(axis=axis) - x.mean(axis=axis)) / normalize(x, axis=axis, norm=norm)


def mae(x, y, axis=None, norm=None):
    return np.nanmean(np.abs(x - y), axis=axis) / normalize(x, axis=axis, norm=norm)


def r2(x, y, **kw):
    """R^2 (coefficient of determination) regression score function.

    See
    https://scikit-learn.org/stable/modules/generated/sklearn.metrics.r2_score.html
    and
    https://scikit-learn.org/stable/modules/model_evaluation.html#r2-score
    """
    return r2_score(x, y, **kw)


def pearsonr(x, y, axis=0):
    return x.to_frame().corrwith(y.to_frame()).squeeze()


def skill(a, b, norm=None):
    if norm is None:
        return collections.OrderedDict(
            [
                ("npoints", a.size),
                ("mean(a)", np.nanmean(a)),
                ("mean(b)", np.nanmean(b)),
                ("bias", bias(a, b)),
                ("pearsonr", pearsonr(a, b)),
                ("rmse", rmse(a, b)),
                ("rmsd", rmsd(a, b)),
                ("mae", mae(a, b)),
            ]
        )
    else:
        return collections.OrderedDict(
            [
                ("npoints", a.size),
                ("mean(a)", np.nanmean(a)),
                ("mean(b)", np.nanmean(b)),
                ("bias", bias(a, b)),
                ("pearsonr", pearsonr(a, b)),
                ("rmse", rmse(a, b)),
                ("nrmse", rmse(a, b, norm=norm)),
                ("rmsd", rmsd(a, b)),
                ("nrmsd", rmsd(a, b, norm=norm)),
                ("mae", mae(a, b)),
                ("nmae", mae(a, b, norm=norm)),
            ]
        )


def skill_str(a, b, metrics=None, norm=None, fmt=None):
    """Create a skill-string that is easily parsed by the 'ax.text' method.

    Parameters
    ----------
    a: array-like
        The observation.
    b: array-like
        The model.
    metrics: list or dict-like
        List of metrics or mapping of metric to metric name.
    norm:
        Norm passed to underlying skill functions.
    fmt: string or dict-like
        String format of the metrics in `metrics`, e.g.
        '.4f' or {'mean': '.0f', pearsonr: '.3f'}

    Examples
    --------
    ax.text(0.05, 0.95,
            skill_str(a, b),
            transform=ax.transAxes,
            fontsize=6,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white'),
            )
    """
    if metrics is None:
        if norm is None:
            metrics = [
                "npoints",
                "mean(a)",
                "mean(b)",
                "bias",
                "pearsonr",
                "rmse",
                "rmsd",
                "mae",
            ]
        else:
            metrics = [
                "npoints",
                "mean(a)",
                "mean(b)",
                "bias",
                "pearsonr",
                "nrmse",
                "nrmsd",
                "nmae",
            ]

    if fmt is None:
        fmt = ".5g"

    if isinstance(fmt, str):
        fmt = {metric: fmt for metric in metrics}

    if isinstance(metrics, list):
        metrics = collections.OrderedDict(
            [(metric, get_metric_name(metric)) for metric in metrics]
        )

    skill_dict = skill(a, b, norm)

    msg = ""
    for metric, metric_name in metrics.items():
        value = skill_dict[metric]
        try:
            msg += "{} = {:{sfmt:s}}\n".format(metric_name, value, sfmt=fmt[metric])
        except ValueError as err:
            # if formatting fails format as string
            warnings.warn(
                "failed to format {} as '{}': {}".format(value, fmt[metric], str(err))
            )
            msg += "{} = {:{sfmt:s}}\n".format(metric_name, value, sfmt="s")

    return msg.strip()
