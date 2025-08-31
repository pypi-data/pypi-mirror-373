from Backtester_Tushar.Strategy.base_class import Strategy
import numpy as np
import pandas as pd


class MACDStrategy(Strategy):
    """Implements a MACD-based trading strategy."""

    def __init__(self, timeframe="daily", atr_period=14, fast_ema=12, slow_ema=26, signal_ema=9, feature_configs=None,
                 base_risk=150000, atr_threshold=5):
        super().__init__("MACDStrategy", timeframe, atr_period, feature_configs, base_risk, atr_threshold)
        self.fast_ema = fast_ema
        self.slow_ema = slow_ema
        self.signal_ema = signal_ema

    def risk_allocation(self, row):
        base_risk = self.base_risk_allocation(row)
        if pd.isna(base_risk):
            return np.nan
        macd_diff = abs(row["MACD"] - row["Signal_Line"]) if "MACD" in row and "Signal_Line" in row else 0
        return base_risk * (1.67 if macd_diff > 0.5 else 1.0)

    def generate_signals(self, df):
        df = df.copy()
        df = self.feature_generator.compute_features(df)
        exp1 = df["Close"].ewm(span=self.fast_ema, adjust=False).mean()
        exp2 = df["Close"].ewm(span=self.slow_ema, adjust=False).mean()
        df["MACD"] = exp1 - exp2
        df["Signal_Line"] = df["MACD"].ewm(span=self.signal_ema, adjust=False).mean()
        df["ATR"] = self.atr(df["High"], df["Low"], df["Close"])
        df["ATR"] = df["ATR"].bfill().ffill()
        df["ATR_percent"] = df["ATR"] * 100 / df["Close"]
        df["Returns"] = np.log(df["Close"] / df["Close"].shift(1)).fillna(0)
        for window in [1, 10, 22, 66, 132, 252]:
            df[f"{window}_Volatility"] = df["Returns"].rolling(window=window).std() * np.sqrt(window)
            df[f"{window}_Returns"] = df["Close"].pct_change(periods=window).mul(100)
        df["Entry_Signal"] = np.where(
            (df["MACD"] > df["Signal_Line"]) & (df["MACD"].shift(1) <= df["Signal_Line"].shift(1)), 1, 0)
        df["Long_Signal"] = df["Entry_Signal"].apply(lambda x: -1 if x == 1 else 0)
        df["Short_Signal"] = np.where(
            (df["MACD"] < df["Signal_Line"]) & (df["MACD"].shift(1) >= df["Signal_Line"].shift(1)), 1, 0)
        df["Signal"] = df["Long_Signal"] + df["Short_Signal"]
        return df
