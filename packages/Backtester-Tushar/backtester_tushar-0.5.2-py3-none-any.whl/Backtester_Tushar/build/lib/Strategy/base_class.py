import numpy as np
from abc import ABC, abstractmethod
import pandas as pd
from Backtester_Tushar.Feature_Generator.feature_gen import FeatureGenerator

class Strategy(ABC):
    """Abstract base class for trading strategies."""

    def __init__(self, name, timeframe="daily", atr_period=14, feature_configs=None, base_risk=150000, atr_threshold=5):
        self.name = name
        self.timeframe = timeframe
        self.atr_period = atr_period
        self.atr_cache = {}
        self.feature_generator = FeatureGenerator(feature_configs)
        self.base_risk = base_risk
        self.atr_threshold = atr_threshold

    def base_risk_allocation(self, row):
        if row["Signal"] == 0:
            return np.nan
        atr_percent = row["ATR_percent"] if "ATR_percent" in row else np.inf
        volatility = row["1_Volatility"] if "1_Volatility" in row else np.inf
        if atr_percent <= self.atr_threshold and volatility < 0.02:
            return self.base_risk * 1.33
        return self.base_risk

    @abstractmethod
    def risk_allocation(self, row):
        pass

    @abstractmethod
    def generate_signals(self, df):
        pass

    def atr(self, high, low, close):
        key = (tuple(high), tuple(low), tuple(close), self.atr_period)
        if key not in self.atr_cache:
            tr = np.amax(
                np.vstack(((high - low).to_numpy(), (abs(high - close)).to_numpy(), (abs(low - close)).to_numpy())).T,
                axis=1)
            self.atr_cache[key] = pd.Series(tr).rolling(self.atr_period).mean().to_numpy()
        return self.atr_cache[key]

