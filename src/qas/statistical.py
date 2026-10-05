"""Descriptive statistics with explicitly qualified seed-mean intervals."""

import numpy as np
from scipy.stats import t


def describe(values):
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not len(values) or not np.isfinite(values).all():
        raise ValueError("Statistics require finite observations")
    n = len(values)
    mean = float(values.mean())
    sd = float(values.std(ddof=1)) if n > 1 else None
    interval = None
    if n >= 5:
        margin = float(t.ppf(0.975, n - 1) * sd / np.sqrt(n))
        interval = [mean - margin, mean + margin]
    return dict(
        count=n,
        mean=mean,
        std=sd,
        median=float(np.median(values)),
        minimum=float(values.min()),
        maximum=float(values.max()),
        mean_ci95=interval,
        interval_assumption="Student-t interval for independent seed means; approximate at small n, not uncertainty of exact reference",
    )
