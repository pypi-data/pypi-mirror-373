import numpy as np
from numba import njit, prange

@njit
def fast_softmax(x):
    """Numerically stable softmax with numba acceleration"""
    x_shifted = x - np.max(x)
    exp_x = np.exp(x_shifted)
    return exp_x / np.sum(exp_x)



@njit
def fast_sharpe_ratio(returns, risk_free_rate=0.0):
    """Fast Sharpe ratio calculation"""
    excess_returns = returns - risk_free_rate
    if np.std(excess_returns) == 0:
        return 0.0
    return np.mean(excess_returns) / np.std(excess_returns)


@njit
def exponential_decay(values, half_life):
    """Apply exponential decay to signal values"""
    decay_factor = np.log(0.5) / half_life
    n = len(values)
    weights = np.exp(decay_factor * np.arange(n - 1, -1, -1))
    return values * weights

