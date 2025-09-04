#!/usr/bin/env python3
"""Utilities."""

import numpy as np


def remove_outliers(data, cut=2.0, outliers=False, debug=False):
    """Remove points far away form the rest.

    Args:
    ----
        data : The data
        cut: max allowed distance
        outliers: if True, return the outliers rhater than remove them
        debug: be verbose if True.

    """
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d / (mdev if mdev else 1.)
    if outliers:
        indx = np.where(s > cut)[0]
    else:
        indx = np.where(s < cut)[0]

    return indx