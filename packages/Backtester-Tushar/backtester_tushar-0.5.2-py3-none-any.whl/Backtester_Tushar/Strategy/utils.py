import numpy as np
import pandas as pd
from numba import njit


@njit
def rolling_zscore(arr, window):
    """
    Compute rolling z-scores with only past information (t-1).
    arr: 1D numpy array
    window: int, rolling window length
    """
    n = len(arr)
    out = np.zeros(n)
    cumsum = 0.0
    cumsum_sq = 0.0

    for i in range(n):
        if i > 0:
            # include value at i-1 into window
            cumsum += arr[i - 1]
            cumsum_sq += arr[i - 1] ** 2

        if i >= window:
            # drop element falling out of window
            cumsum -= arr[i - window]
            cumsum_sq -= arr[i - window] ** 2

        count = min(i, window)
        if count > 1:
            mean = cumsum / count
            var = (cumsum_sq / count) - mean ** 2
            std = np.sqrt(var) if var > 1e-12 else 0.0
            out[i] = (arr[i] - mean) / std if std > 0 else 0.0
        else:
            out[i] = 0.0

    return out
