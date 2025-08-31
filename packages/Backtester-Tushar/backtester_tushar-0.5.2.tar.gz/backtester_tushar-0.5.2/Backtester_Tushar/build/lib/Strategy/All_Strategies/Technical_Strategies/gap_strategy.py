from Backtester_Tushar.Strategy.base_class import Strategy
import numpy as np
import pandas as pd

class GapStrategy(Strategy):
    """Implements a gap-based trading strategy."""

    def __init__(self, timeframe="daily", atr_period=14, trend_window_3=9, trend_window_5=7, trend_threshold=0.9,
                 feature_configs=None, base_risk=150000, atr_threshold=5):
        super().__init__("GapStrategy", timeframe, atr_period, feature_configs, base_risk, atr_threshold)
        self.trend_window_3 = trend_window_3
        self.trend_window_5 = trend_window_5
        self.trend_threshold = trend_threshold

    def risk_allocation(self, row):
        base_risk = self.base_risk_allocation(row)
        if pd.isna(base_risk):
            return np.nan
        gap = abs(row["Gap"]) if "Gap" in row else 0
        return base_risk * (1.5 if gap > 1.0 else 1.0)

    def generate_signals(self, df):
        df = df.copy()
        df = self.feature_generator.compute_features(df)
        df["trend_strength_3"] = df["bar_index"].rolling(self.trend_window_3).corr(df["Close"])
        df["trend_strength_5"] = df["bar_index"].rolling(self.trend_window_5).corr(df["Close"])
        df["ATR"] = self.atr(df["High"], df["Low"], df["Close"])
        df["ATR"] = df["ATR"].bfill().ffill()
        df["ATR_percent"] = df["ATR"] * 100 / df["Close"]
        df["Returns"] = np.log(df["Close"] / df["Close"].shift(1)).fillna(0)
        for window in [1, 10, 22, 66, 132, 252]:
            df[f"{window}_Volatility"] = df["Returns"].rolling(window=window).std() * np.sqrt(window)
            df[f"{window}_Returns"] = df["Close"].pct_change(periods=window).mul(100)
        df["Entry_Signal"] = df["trend_strength_3"].apply(lambda x: 1 if x <= -self.trend_threshold else 0)
        df["Long_Signal"] = df["trend_strength_5"].apply(lambda x: -1 if x <= -self.trend_threshold else 0)
        df["Short_Signal"] = df["trend_strength_5"].apply(lambda x: 1 if x >= self.trend_threshold else 0)
        df["Signal"] = df["Long_Signal"] + df["Short_Signal"]
        return df
