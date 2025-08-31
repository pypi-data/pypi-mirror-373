from abc import ABC, abstractmethod

from build.lib.Backtester_Tushar.example import weights


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

    @abstractmethod
    def get_weights(self):
        pass