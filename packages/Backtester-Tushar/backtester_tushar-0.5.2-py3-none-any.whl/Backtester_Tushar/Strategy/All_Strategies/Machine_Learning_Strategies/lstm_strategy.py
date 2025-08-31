import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from Backtester_Tushar.Strategy.ml_base_class import MLStrategy

class LSTMStrategy(MLStrategy):
    def train_model(self, df):
        df = self.feature_generator.compute_features(df.copy())

        features = [
            "Close", "Volume", "ATR_percent", "PE_Ratio", "EPS_Growth_4", "Debt_to_Equity",
            "Social_Media_Sentiment", "Macro_Indicator"
        ] + [col for col in df.columns if col.startswith(("RSI_", "BB_", "Momentum_"))]

        df = df.dropna(subset=features)
        if df.empty:
            return

        X = df[features].values
        y = np.where(df["Close"].shift(-1) > df["Close"], 1, 0)[df.index[:-1]]
        X_scaled = self.scaler.fit_transform(X)

        # Prepare sequences
        sequences = [
            X_scaled[i:i + self.sequence_length]
            for i in range(len(X_scaled) - self.sequence_length)
        ]
        targets = y[self.sequence_length - 1:]

        if len(sequences) == 0:
            return

        X_tensor = torch.tensor(sequences, dtype=torch.float32).to(self.device)
        y_tensor = torch.tensor(targets, dtype=torch.long).to(self.device)

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)

        self.model.train()
        for epoch in range(5):  # reduced epochs for performance
            optimizer.zero_grad()
            outputs = self.model(X_tensor)
            loss = criterion(outputs, y_tensor)
            loss.backward()
            optimizer.step()

    def predict(self, df):
        df = self.feature_generator.compute_features(df.copy())

        features = [
            "Close", "Volume", "ATR_percent", "PE_Ratio", "EPS_Growth_4", "Debt_to_Equity",
            "Social_Media_Sentiment", "Macro_Indicator"
        ] + [col for col in df.columns if col.startswith(("RSI_", "BB_", "Momentum_"))]

        df = df.dropna(subset=features)
        if df.empty:
            return pd.Series(0, index=df.index)

        X = self.scaler.transform(df[features].values)
        sequences = [
            X[i:i + self.sequence_length] for i in range(len(X) - self.sequence_length + 1)
        ]

        if not sequences:
            return pd.Series(0, index=df.index)

        X_tensor = torch.tensor(sequences, dtype=torch.float32).to(self.device)
        self.model.eval()
        with torch.no_grad():
            preds = self.model(X_tensor)
            labels = torch.argmax(preds, dim=1).cpu().numpy()

        pad = [0] * (self.sequence_length - 1)
        return pd.Series(pad + list(labels), index=df.index)
