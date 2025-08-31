import pandas as pd
import numpy as np
from Backtester_Tushar.Strategy.base_class import Strategy
from Backtester_Tushar.Portfolio_Opt.optimization import PortfolioOptimizer

class MultiAssetStrategy(Strategy):
    """Implements a multi-asset trading strategy."""

    def __init__(self, tickers, timeframe="daily", atr_period=14, feature_configs=None, optimizer=None,
                 base_risk=150000, atr_threshold=5):
        super().__init__("MultiAssetStrategy", timeframe, atr_period, feature_configs, base_risk, atr_threshold)
        self.tickers = tickers
        self.optimizer = optimizer or PortfolioOptimizer()

    def risk_allocation(self, row):
        return self.base_risk_allocation(row)

    def generate_signals(self, dfs):
        signals = {}
        returns = {}
        for ticker, df in dfs.items():
            df = df.copy()
            df = self.feature_generator.compute_features(df)
            df["ATR"] = self.atr(df["High"], df["Low"], df["Close"])
            df["ATR"] = df["ATR"].bfill().ffill()
            df["ATR_percent"] = df["ATR"] * 100 / df["Close"]
            df["Returns"] = np.log(df["Close"] / df["Close"].shift(1)).fillna(0)
            df["Signal"] = np.where(df["Close"] > df["Close"].shift(1), 1, -1)
            signals[ticker] = df
            returns[ticker] = df["Returns"].dropna()

        if len(returns) > 1:
            cov_matrix = pd.DataFrame(returns).cov()
            weights = self.optimizer.optimize(pd.Series({t: r.mean() for t, r in returns.items()}), cov_matrix)
            for i, (ticker, df) in enumerate(signals.items()):
                df["Signal"] *= weights[i]
                signals[ticker] = df
        return signals
