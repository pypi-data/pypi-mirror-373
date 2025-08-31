from Backtester_Tushar.Strategy_Weights.base_class import StrategyWeights
from Backtester_Tushar.Strategy_Weights.equal_weights import EqualWeights
import numpy as np


class MarketRegimeWeights(StrategyWeights):
    """Assigns weights based on detected market regimes."""

    def __init__(self, volatility_window=20, momentum_window=20, atr_threshold=5, momentum_threshold=0.01):
        super().__init__()
        self.volatility_window = volatility_window
        self.momentum_window = momentum_window
        self.atr_threshold = atr_threshold
        self.momentum_threshold = momentum_threshold
        self.strategy_regime_map = {
            "GapStrategy": "mean_reverting",
            "MACDStrategy": "trending",
            "RandomForestStrategy": "volatile",
            "LSTMStrategy": "volatile",
            "QLStrategy": "volatile",
            "MultiAssetStrategy": "trending",
            "EnsembleStrategy": "balanced",
            "FundamentalStrategy": "mean_reverting"
        }

    def _detect_regime(self, df):
        """Detect market regime based on volatility and momentum."""
        if df is None or len(df) < max(self.volatility_window, self.momentum_window):
            return "balanced"

        df = df.copy()
        df["Returns"] = np.log(df["Close"] / df["Close"].shift(1)).fillna(0)
        volatility = df["Returns"].rolling(window=self.volatility_window).std() * np.sqrt(self.volatility_window)
        momentum = df["Close"].pct_change(periods=self.momentum_window)

        latest_volatility = volatility.iloc[-1] if not volatility.empty else 0
        latest_momentum = momentum.iloc[-1] if not momentum.empty else 0
        atr = df["ATR"].iloc[-1] if "ATR" in df else 0

        if atr > self.atr_threshold or latest_volatility > 0.02:
            return "volatile"
        elif abs(latest_momentum) > self.momentum_threshold:
            return "trending"
        else:
            return "mean_reverting"

    def compute_weights(self, strategies, performance_data=None, df=None):
        """Compute weights based on market regime."""
        regime = self._detect_regime(df)
        weights = {}
        total_weight = 0

        for strategy in strategies:
            strategy_regime = self.strategy_regime_map.get(strategy.name, "balanced")
            if regime == "volatile" and strategy_regime == "volatile":
                weights[strategy.name] = 0.4
            elif regime == "trending" and strategy_regime == "trending":
                weights[strategy.name] = 0.4
            elif regime == "mean_reverting" and strategy_regime == "mean_reverting":
                weights[strategy.name] = 0.4
            elif strategy_regime == "balanced":
                weights[strategy.name] = 0.2
            else:
                weights[strategy.name] = 0.1
            total_weight += weights[strategy.name]

        # Normalize weights
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}
        else:
            weights = EqualWeights().compute_weights(strategies)

        return weights
