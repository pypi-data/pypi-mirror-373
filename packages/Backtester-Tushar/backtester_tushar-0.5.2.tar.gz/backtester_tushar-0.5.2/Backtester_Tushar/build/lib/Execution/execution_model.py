import numpy as np

class ExecutionModel:
    """Handles order execution logic."""

    def __init__(self, execution_type="market", slippage_pct=0.002):
        self.execution_type = execution_type
        self.slippage_pct = slippage_pct

    def execute_order(self, row, signal):
        if signal == 0:
            return np.nan
        if self.execution_type == "market":
            return row["Close"] * (1 + self.slippage_pct * signal)
        elif self.execution_type == "limit":
            limit_price = row["Close"] * (1 - 0.01 * signal)
            if signal == 1 and row["Low"] <= limit_price:
                return limit_price
            elif signal == -1 and row["High"] >= limit_price:
                return limit_price
            return np.nan
        return row["Close"]
