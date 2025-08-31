import pandas as pd
import numpy as np
from numba import njit, prange
from scipy import stats, optimize, linalg
from scipy.stats import norm
from sklearn.decomposition import PCA
from sklearn.covariance import LedoitWolf
import warnings
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Optional
import logging
from scipy.optimize import minimize
from Backtester_Tushar.Risk.risk_limits import RiskLimits
from Backtester_Tushar.Portfolio_Management_and_Tracker.utils import *
warnings.filterwarnings('ignore')

class SignalProcessor:
    """Advanced signal processing with decay, orthogonalization, and quality metrics"""

    def __init__(self, half_life_days=5, min_ic_threshold=0.02):
        self.half_life_days = half_life_days
        self.min_ic_threshold = min_ic_threshold
        self.signal_history = defaultdict(deque)
        self.ic_history = defaultdict(deque)

    def decay_signals(self, signals_df):
        """Apply exponential decay to signals based on age"""
        decayed_signals = signals_df.copy()

        for ticker in signals_df['ticker'].unique():
            ticker_data = signals_df[signals_df['ticker'] == ticker].sort_values('date')
            if len(ticker_data) > 1:
                signal_values = ticker_data['signal_descriptor'].values
                decayed_values = exponential_decay(signal_values, self.half_life_days)
                decayed_signals.loc[decayed_signals['ticker'] == ticker, 'signal_descriptor'] = decayed_values

        return decayed_signals

    def calculate_information_coefficient(self, signals, forward_returns, periods=20):
        """Calculate rolling information coefficient"""
        if len(signals) != len(forward_returns) or len(signals) < periods:
            return 0.0

        ic_values = []
        for i in range(periods, len(signals)):
            window_signals = signals[i - periods:i]
            window_returns = forward_returns[i - periods:i]

            if len(window_signals) > 5:  # Minimum sample size
                ic, _ = stats.spearmanr(window_signals, window_returns)
                if not np.isnan(ic):
                    ic_values.append(ic)

        return np.mean(ic_values) if ic_values else 0.0

    def orthogonalize_signals(self, signal_matrix):
        """Orthogonalize signals using Gram-Schmidt process"""
        if signal_matrix.shape[1] < 2:
            return signal_matrix

        # Handle NaN values
        signal_matrix = np.nan_to_num(signal_matrix, nan=0.0)

        # Apply Gram-Schmidt orthogonalization
        orthogonal_signals = np.zeros_like(signal_matrix)

        for i in range(signal_matrix.shape[1]):
            vector = signal_matrix[:, i].copy()

            for j in range(i):
                projection = np.dot(vector, orthogonal_signals[:, j]) / np.dot(orthogonal_signals[:, j],
                                                                               orthogonal_signals[:, j])
                if not np.isnan(projection):
                    vector -= projection * orthogonal_signals[:, j]

            norm = np.linalg.norm(vector)
            orthogonal_signals[:, i] = vector / norm if norm > 1e-10 else vector

        return orthogonal_signals
