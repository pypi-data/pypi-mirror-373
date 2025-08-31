import pandas as pd
import numpy as np
from numba import njit, prange
from scipy import stats, optimize, linalg
from scipy.stats import norm
from sklearn.decomposition import PCA
from sklearn.covariance import LedoitWolf
import warnings
from collections import defaultdict, deque
import logging
from scipy.optimize import minimize
from Backtester_Tushar.Risk.risk_limits import RiskLimits
from Backtester_Tushar.Portfolio_Management_and_Tracker.utils import *
from Backtester_Tushar.Strategy.signal_processing import SignalProcessor
from Backtester_Tushar.Execution.t_cost import MarketImpactModel
warnings.filterwarnings('ignore')

class PerformanceAnalyzer:
    """Advanced performance analytics with attribution and benchmarking"""

    def __init__(self, benchmark_returns=None):
        self.benchmark_returns = benchmark_returns
        self.performance_history = []
        self.attribution_history = []

    def calculate_performance_metrics(self, returns, benchmark_returns=None):
        """Calculate comprehensive performance metrics"""
        if len(returns) == 0:
            return {}

        returns_array = np.array(returns)
        returns_array = returns_array[~np.isnan(returns_array)]

        if len(returns_array) == 0:
            return {}

        # Basic metrics
        total_return = np.prod(1 + returns_array) - 1
        annualized_return = (np.prod(1 + returns_array)) ** (252 / len(returns_array)) - 1
        annualized_vol = np.std(returns_array) * np.sqrt(252)
        sharpe_ratio = annualized_return / annualized_vol if annualized_vol > 0 else 0

        # Risk metrics
        downside_returns = returns_array[returns_array < 0]
        downside_vol = np.std(downside_returns) * np.sqrt(252) if len(downside_returns) > 0 else 0
        sortino_ratio = annualized_return / downside_vol if downside_vol > 0 else 0

        # Drawdown metrics
        cumulative_returns = np.cumprod(1 + returns_array)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdowns)

        # Skewness and Kurtosis
        skewness = stats.skew(returns_array)
        kurtosis = stats.kurtosis(returns_array)

        metrics = {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'annualized_volatility': annualized_vol,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'var_95': np.percentile(returns_array, 5),
            'cvar_95': np.mean(returns_array[returns_array <= np.percentile(returns_array, 5)])
        }

        # Benchmark-relative metrics
        if benchmark_returns is not None and len(benchmark_returns) == len(returns_array):
            excess_returns = returns_array - np.array(benchmark_returns)
            tracking_error = np.std(excess_returns) * np.sqrt(252)
            information_ratio = np.mean(excess_returns) * 252 / tracking_error if tracking_error > 0 else 0

            # Beta calculation
            covariance = np.cov(returns_array, benchmark_returns)[0, 1]
            benchmark_variance = np.var(benchmark_returns)
            beta = covariance / benchmark_variance if benchmark_variance > 0 else 0

            # Alpha calculation
            risk_free_rate = 0.02 / 252  # Assume 2% annual risk-free rate
            alpha = (annualized_return - risk_free_rate) - beta * (np.mean(benchmark_returns) * 252 - risk_free_rate)

            metrics.update({
                'tracking_error': tracking_error,
                'information_ratio': information_ratio,
                'beta': beta,
                'alpha': alpha
            })

        return metrics

