import numpy as np
import pandas as pd
import math
from Backtester_Tushar.Sizing.base_class import PositionSizer


class ATRPositionSizer(PositionSizer):
    """ATR-based position sizing."""

    def __init__(self, risk_per_trade=0.01):
        self.risk_per_trade = risk_per_trade

    def calculate_shares(self, row, capital, max_exposure):
        if row["Signal"] == 0 or pd.isna(row["Risk"]):
            return np.nan
        risk_amount = capital * self.risk_per_trade
        return math.floor(min(row["Risk"], risk_amount) / (1 * row["ATR"]))

    def calculate_stoploss(self, row):
        if row["Signal"] == 1:
            return row["Close"] - 1 * row["ATR"]
        elif row["Signal"] == -1:
            return row["Close"] + 1 * row["ATR"]
        return np.nan

    def calculate_takeprofit(self, row):
        if row["Signal"] == 1:
            return row["Close"] + 2 * row["ATR"]
        elif row["Signal"] == -1:
            return row["Close"] - 2 * row["ATR"]
        return np.nan

from abc import ABC, abstractmethod


class PositionSizer(ABC):
    """Abstract base class for position sizing and risk management."""

    @abstractmethod
    def calculate_shares(self, row, capital, max_exposure):
        pass

    @abstractmethod
    def calculate_stoploss(self, row):
        pass

    @abstractmethod
    def calculate_takeprofit(self, row):
        pass

