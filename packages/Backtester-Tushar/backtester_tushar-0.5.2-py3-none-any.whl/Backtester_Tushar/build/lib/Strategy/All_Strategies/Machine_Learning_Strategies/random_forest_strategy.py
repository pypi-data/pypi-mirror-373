import pandas as pd
import numpy as np
from Backtester_Tushar.Strategy.ml_base_class import MLStrategy


class RandomForestStrategy(MLStrategy):
    def train_model(self, df):
        df = self.feature_generator.compute_features(df.copy())
        features = [
            "Close", "Volume", "ATR_percent", "PE_Ratio", "EPS_Growth_4", "Debt_to_Equity",
            "Social_Media_Sentiment", "Macro_Indicator"
        ] + [col for col in df.columns if col.startswith(("RSI_", "BB_", "Momentum_"))]

        X = df[features].dropna()
        if X.empty:
            return

        y = np.where(df["Close"].shift(-1) > df["Close"], 1, -1)[X.index]
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)

    def predict(self, df):
        df = self.feature_generator.compute_features(df.copy())
        features = [
            "Close", "Volume", "ATR_percent", "PE_Ratio", "EPS_Growth_4", "Debt_to_Equity",
            "Social_Media_Sentiment", "Macro_Indicator"
        ] + [col for col in df.columns if col.startswith(("RSI_", "BB_", "Momentum_"))]

        X = df[features].dropna()
        if X.empty:
            return pd.Series(0, index=df.index)

        X_scaled = self.scaler.transform(X)
        preds = self.model.predict(X_scaled)
        return pd.Series(preds, index=X.index).reindex(df.index, fill_value=0)
