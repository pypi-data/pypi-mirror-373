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

