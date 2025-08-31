from Backtester_Tushar.Strategy.base_class import Strategy
import numpy as np
from abc import abstractmethod
class MLStrategy(Strategy):
    """Abstract base class for ML/DL/RL strategies."""

    def __init__(self, name, timeframe="daily", atr_period=14, feature_configs=None, base_risk=150000, atr_threshold=5):
        super().__init__(name, timeframe, atr_period, feature_configs, base_risk, atr_threshold)
        self.model = None

    @abstractmethod
    def train_model(self, df):
        pass

    @abstractmethod
    def predict(self, df):
        pass

    def risk_allocation(self, row):
        return self.base_risk_allocation(row)

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

        predictions = self.predict(df)
        df["Entry_Signal"] = predictions.apply(lambda x: 1 if x == 1 else 0)
        df["Long_Signal"] = predictions.apply(lambda x: -1 if x == 1 else 0)
        df["Short_Signal"] = predictions.apply(lambda x: 1 if x == -1 else 0)
        df["Signal"] = df["Long_Signal"] + df["Short_Signal"]
        return df
