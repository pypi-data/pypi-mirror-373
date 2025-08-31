from Backtester_Tushar.Strategy.base_class import Strategy
from Backtester_Tushar.Strategy_Weights.equal_weights import EqualWeights
import numpy as np
import pandas as pd


class EnsembleStrategy(Strategy):
    """Implements an ensemble of multiple strategies."""

    def __init__(self, strategies, weights=None, timeframe="daily", atr_period=14, combine_method="weighted",
                 feature_configs=None, base_risk=150000, atr_threshold=5):
        super().__init__("EnsembleStrategy", timeframe, atr_period, feature_configs, base_risk, atr_threshold)
        self.strategies = strategies
        self.weights = weights or EqualWeights().compute_weights(strategies)
        self.combine_method = combine_method

    def risk_allocation(self, row):
        base_risk = self.base_risk_allocation(row)
        if pd.isna(base_risk):
            return np.nan
        signal_strength = abs(row["Signal"]) if "Signal" in row else 0
        return base_risk * (1.33 if signal_strength > 0.5 else 1.0)

    def generate_signals(self, df):
        df = df.copy()
        df = self.feature_generator.compute_features(df)
        df["ATR"] = self.atr(df["High"], df["Low"], df["Close"])
        df["ATR"] = df["ATR"].bfill().ffill()
        df["ATR_percent"] = df["ATR"] * 100 / df["Close"]
        df["Returns"] = np.log(df["Close"] / df["Close"].shift(1)).fillna(0)
        for window in [1, 10, 22, 66, 132, 252]:
            df[f"{window}_Volatility"] = df["Returns"].rolling(window=window).std() * np.sqrt(window)
            df[f"{window}_Returns"] = df["Close"].pct_change(periods=window).mul(100)

        signals = []
        for strategy in self.strategies:
            strategy_df = strategy.generate_signals(df)
            signals.append(strategy_df["Signal"] * self.weights.get(strategy.name, 1))

        if self.combine_method == "weighted":
            df["Signal"] = pd.concat(signals, axis=1).mean(axis=1).apply(
                lambda x: 1 if x > 0.5 else -1 if x < -0.5 else 0)
        else:
            df["Signal"] = pd.concat(signals, axis=1).mode(axis=1)[0]

        df["Entry_Signal"] = df["Signal"].apply(lambda x: 1 if x == 1 else 0)
        df["Long_Signal"] = df["Signal"].apply(lambda x: -1 if x == 1 else 0)
        df["Short_Signal"] = df["Signal"].apply(lambda x: 1 if x == -1 else 0)
        return df
