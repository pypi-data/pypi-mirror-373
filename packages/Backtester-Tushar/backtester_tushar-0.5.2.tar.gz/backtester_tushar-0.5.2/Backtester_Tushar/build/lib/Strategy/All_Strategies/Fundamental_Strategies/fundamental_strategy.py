from Backtester_Tushar.Strategy.base_class import Strategy
import numpy as np
import pandas as pd

class FundamentalStrategy(Strategy):
    """Implements a trading strategy based on company fundamentals."""

    def __init__(self, timeframe="daily", atr_period=14, pe_threshold=20, eps_growth_threshold=0.1,
                 debt_equity_threshold=1.0, feature_configs=None, base_risk=150000, atr_threshold=5):
        super().__init__("FundamentalStrategy", timeframe, atr_period, feature_configs, base_risk, atr_threshold)
        self.pe_threshold = pe_threshold
        self.eps_growth_threshold = eps_growth_threshold
        self.debt_equity_threshold = debt_equity_threshold

    def risk_allocation(self, row):
        base_risk = self.base_risk_allocation(row)
        if pd.isna(base_risk):
            return np.nan
        pe_ratio = row["PE_Ratio"] if "PE_Ratio" in row else np.inf
        eps_growth = row["EPS_Growth_4"] if "EPS_Growth_4" in row else 0
        debt_equity = row["Debt_to_Equity"] if "Debt_to_Equity" in row else np.inf
        score = (1 if pe_ratio < self.pe_threshold else 0) + \
                (1 if eps_growth > self.eps_growth_threshold else 0) + \
                (1 if debt_equity < self.debt_equity_threshold else 0)
        return base_risk * (1.0 + 0.2 * score)

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

        # Generate signals based on fundamentals
        df["Fundamental_Score"] = (
                (df["PE_Ratio"] < self.pe_threshold).astype(int) +
                (df["EPS_Growth_4"] > self.eps_growth_threshold).astype(int) +
                (df["Debt_to_Equity"] < self.debt_equity_threshold).astype(int)
        )
        df["Entry_Signal"] = np.where(df["Fundamental_Score"] >= 2, 1, 0)
        df["Long_Signal"] = df["Entry_Signal"].apply(lambda x: -1 if x == 1 else 0)
        df["Short_Signal"] = np.where(df["Fundamental_Score"] <= 0, 1, 0)
        df["Signal"] = df["Long_Signal"] + df["Short_Signal"]
        return df
