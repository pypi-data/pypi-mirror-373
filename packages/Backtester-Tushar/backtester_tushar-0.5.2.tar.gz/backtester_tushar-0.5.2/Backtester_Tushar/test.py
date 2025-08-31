import pandas as pd
import numpy as np
import math
import calendar
from abc import ABC, abstractmethod
import os
import uuid
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque
from joblib import Parallel, delayed
import yaml
from scipy.optimize import minimize


class StrategyWeights(ABC):
    """Abstract base class for computing strategy weights."""

    def __init__(self):
        self.weights_cache = {}

    @abstractmethod
    def compute_weights(self, strategies, performance_data=None, df=None):
        """Compute weights for each strategy."""
        pass

    def get_weights(self, strategies, performance_data=None, df=None):
        """Retrieve or compute weights, using cache for efficiency."""
        cache_key = tuple(s.name for s in strategies) + (
        id(performance_data) if performance_data is not None else 0,) + (id(df) if df is not None else 0,)
        if cache_key not in self.weights_cache:
            self.weights_cache[cache_key] = self.compute_weights(strategies, performance_data, df)
        return self.weights_cache[cache_key]


class EqualWeights(StrategyWeights):
    """Assigns equal weights to all strategies."""

    def compute_weights(self, strategies, performance_data=None, df=None):
        n = len(strategies)
        return {s.name: 1.0 / n for s in strategies} if n > 0 else {}


class PerformanceBasedWeights(StrategyWeights):
    """Assigns weights based on historical performance (e.g., Sharpe Ratio)."""

    def __init__(self, metric="Sharpe_Ratio"):
        super().__init__()
        self.metric = metric

    def compute_weights(self, strategies, performance_data=None, df=None):
        if performance_data is None or performance_data.empty:
            return EqualWeights().compute_weights(strategies)

        strategy_names = {s.name for s in strategies}
        perf_data = performance_data[performance_data["Strategy"].isin(strategy_names)]

        if perf_data.empty:
            return EqualWeights().compute_weights(strategies)

        metric_values = perf_data.set_index("Strategy")[self.metric]
        metric_values = metric_values.clip(lower=0) + 1e-6
        total = metric_values.sum()
        weights = metric_values / total
        return weights.to_dict()


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


class FeatureGenerator:
    """Generates custom features for trading strategies, including fundamentals and alternative data."""

    def __init__(self, feature_configs=None):
        self.feature_configs = feature_configs or []
        self.cache = {}

    def compute_features(self, df):
        df = df.copy()
        key = (tuple(df["Close"]), tuple(df["High"]), tuple(df["Low"]), tuple(df["Volume"]), str(self.feature_configs))
        if key in self.cache:
            return self.cache[key]

        for config in self.feature_configs:
            name, params = config.get("name"), config.get("params", {})
            if name == "RSI":
                period = params.get("period", 14)
                df[f"RSI_{period}"] = self._compute_rsi(df["Close"], period)
            elif name == "Bollinger_Bands":
                period = params.get("period", 20)
                df[[f"BB_upper_{period}", f"BB_lower_{period}"]] = self._compute_bollinger(df["Close"], period)
            elif name == "Momentum":
                period = params.get("period", 10)
                df[f"Momentum_{period}"] = df["Close"].diff(period)
            elif name == "PE_Ratio":
                df[f"PE_Ratio"] = df["PE_Ratio"] if "PE_Ratio" in df else np.nan
            elif name == "EPS_Growth":
                period = params.get("period", 4)
                df[f"EPS_Growth_{period}"] = self._compute_eps_growth(df, period)
            elif name == "Debt_to_Equity":
                df[f"Debt_to_Equity"] = df["Debt_to_Equity"] if "Debt_to_Equity" in df else np.nan
            elif name == "Social_Media_Sentiment":
                df[f"Social_Media_Sentiment"] = df["Social_Media_Sentiment"] if "Social_Media_Sentiment" in df else 0
            elif name == "Macro_Indicator":
                df[f"Macro_Indicator_{params.get('name', 'Generic')}"] = df[
                    params.get("name", "Macro_Indicator")] if params.get("name", "Macro_Indicator") in df else 0

        self.cache[key] = df
        return df

    def _compute_rsi(self, series, period):
        delta = series.diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs.replace(np.inf, np.nan)))

    def _compute_bollinger(self, series, period):
        sma = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        return pd.DataFrame({
            f"BB_upper_{period}": sma + 2 * std,
            f"BB_lower_{period}": sma - 2 * std
        })

    def _compute_eps_growth(self, df, period):
        if "EPS" not in df:
            return np.nan
        return df["EPS"].pct_change(periods=period) * 100


class DataConnector:
    """Fetches and aligns external data sources, including fundamentals and alternative data."""

    def __init__(self, source_type="csv", source_path=None, fundamental_path=None, social_media_path=None,
                 macro_path=None):
        self.source_type = source_type
        self.source_path = source_path
        self.fundamental_path = fundamental_path
        self.social_media_path = social_media_path
        self.macro_path = macro_path

    def fetch_data(self, ticker, start_date, end_date, data_type="sentiment"):
        """Fetch data based on type (sentiment, fundamentals, social media, macro)."""
        if self.source_type == "csv":
            try:
                if data_type == "sentiment" and self.source_path:
                    df = pd.read_csv(self.source_path)
                    df["Datetime"] = pd.to_datetime(df["Datetime"])
                    df = df[(df["Datetime"] >= start_date) & (df["Datetime"] <= end_date)]
                    return df[["Datetime", "Sentiment_Score"]].dropna()
                elif data_type == "fundamentals" and self.fundamental_path:
                    df = pd.read_csv(self.fundamental_path)
                    df["Datetime"] = pd.to_datetime(df["Date"])
                    df = df[(df["Datetime"] >= start_date) & (df["Datetime"] <= end_date)]
                    return df[["Datetime", "PE_Ratio", "EPS", "Debt_to_Equity"]].dropna()
                elif data_type == "social_media" and self.social_media_path:
                    df = pd.read_csv(self.social_media_path)
                    df["Datetime"] = pd.to_datetime(df["Datetime"])
                    df = df[(df["Datetime"] >= start_date) & (df["Datetime"] <= end_date)]
                    return df[["Datetime", "Social_Media_Sentiment"]].dropna()
                elif data_type == "macro" and self.macro_path:
                    df = pd.read_csv(self.macro_path)
                    df["Datetime"] = pd.to_datetime(df["Datetime"])
                    df = df[(df["Datetime"] >= start_date) & (df["Datetime"] <= end_date)]
                    return df[["Datetime", "Macro_Indicator"]].dropna()
            except FileNotFoundError:
                print(f"Data file for {data_type} not found for {ticker}.")
                return None
        return None

    def align_data(self, base_df, external_df, column_name):
        """Align external data with base DataFrame."""
        if external_df is None:
            return base_df
        return base_df.merge(external_df[["Datetime", column_name]], on="Datetime", how="left").fillna(0)


class TradingEnvironment:
    """RL environment for trading."""

    def __init__(self, df, features, action_space=[0, 1, -1], max_steps=100):
        self.df = df.reset_index(drop=True)
        self.features = features
        self.action_space = action_space
        self.max_steps = max_steps
        self.current_step = 0
        self.done = False

    def reset(self):
        self.current_step = 0
        self.done = False
        return self._get_state()

    def _get_state(self):
        if self.current_step >= len(self.df):
            self.done = True
            return np.zeros(len(self.features))
        return self.df[self.features].iloc[self.current_step].values

    def step(self, action):
        if self.done or self.current_step >= len(self.df) - 1:
            self.done = True
            return np.zeros(len(self.features)), 0, True

        current_price = self.df["Close"].iloc[self.current_step]
        next_price = self.df["Close"].iloc[self.current_step + 1]
        reward = (next_price - current_price) * action
        self.current_step += 1
        next_state = self._get_state()
        self.done = self.current_step >= self.max_steps or self.current_step >= len(self.df) - 1
        return next_state, reward, self.done


class DataHandler:
    """Handles loading and preprocessing of stock data with multi-timeframe support."""

    def __init__(self, data_dir, start_date="2016-01-01", supported_timeframes=["daily", "hourly", "15min"],
                 external_connectors=None, feature_configs=None):
        self.data_dir = data_dir
        self.start_date = pd.to_datetime(start_date)
        self.supported_timeframes = supported_timeframes
        self.data = {}
        self.feature_generator = FeatureGenerator(feature_configs)
        self.external_connectors = external_connectors or []

    def load_stock_data(self, ticker):
        try:
            file_path = os.path.join(self.data_dir, f"{ticker}.csv")
            df = pd.read_csv(file_path)
            df["Ticker"] = ticker
            df["Datetime"] = pd.to_datetime(df["Datetime"])
            df = df[df["Datetime"] >= self.start_date].copy()

            df["Shifted_Close"] = df["Close"].shift(periods=1)
            df["Shifted_Volume"] = df["Volume"].shift(periods=1)
            df["Avg_Rolling_Volume"] = df["Volume"].ewm(span=10, min_periods=0, adjust=False).mean()
            df["bar_index"] = df.index.values
            df["date"] = df["Datetime"].dt.strftime("%Y-%m-%d")
            df["Month_Year"] = df["Datetime"].apply(lambda x: f"{calendar.month_name[int(x.month)]} {x.year}")
            df["Year"] = df["Datetime"].dt.year
            df["Gap"] = (df["Open"] - df["Shifted_Close"]) * 100 / df["Shifted_Close"]

            df = self.feature_generator.compute_features(df)
            for connector in self.external_connectors:
                for data_type, column_name in [
                    ("sentiment", "Sentiment_Score"),
                    ("fundamentals", "PE_Ratio"),
                    ("fundamentals", "EPS"),
                    ("fundamentals", "Debt_to_Equity"),
                    ("social_media", "Social_Media_Sentiment"),
                    ("macro", "Macro_Indicator")
                ]:
                    external_df = connector.fetch_data(ticker, df["Datetime"].min(), df["Datetime"].max(), data_type)
                    df = connector.align_data(df, external_df, column_name)
            return df
        except FileNotFoundError:
            print(f"Data file for {ticker} not found.")
            return None

    def resample_data(self, df, timeframe):
        if timeframe not in self.supported_timeframes:
            raise ValueError(f"Timeframe {timeframe} not supported. Choose from {self.supported_timeframes}")
        if timeframe == "daily":
            return df
        df = df.set_index("Datetime")
        agg_dict = {
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Volume": "sum",
            "Ticker": "last",
            "Shifted_Close": "last",
            "Shifted_Volume": "last",
            "Avg_Rolling_Volume": "last",
            "bar_index": "last",
            "date": "last",
            "Month_Year": "last",
            "Year": "last",
            "Gap": "last",
            "Sentiment_Score": "last",
            "PE_Ratio": "last",
            "EPS": "last",
            "Debt_to_Equity": "last",
            "Social_Media_Sentiment": "last",
            "Macro_Indicator": "last"
        }
        for col in df.columns:
            if col.startswith("RSI_") or col.startswith("BB_") or col.startswith("Momentum_") or col.startswith(
                    "EPS_Growth_"):
                agg_dict[col] = "last"
        df_resampled = df.resample({"hourly": "1H", "15min": "15min"}.get(timeframe, "1D")).agg(agg_dict).dropna()
        df_resampled = df_resampled.reset_index()
        df_resampled["bar_index"] = df_resampled.index.values
        return df_resampled

    def get_data(self, ticker, timeframe="daily"):
        key = (ticker, timeframe)
        if key not in self.data:
            df = self.load_stock_data(ticker)
            if df is not None:
                self.data[key] = self.resample_data(df, timeframe)
        return self.data.get(key)


class PositionSizer(ABC):
    """Abstract base class for position sizing and risk management."""

    @abstractmethod
    def calculate_shares(self, row, capital, max_exposure):
        pass

    @abstractmethod
    def calculate_stoploss(self, row):
        pass

    @abstractmethod
    def calculate_takeprofit(self, row):
        pass


class ATRPositionSizer(PositionSizer):
    """ATR-based position sizing."""

    def __init__(self, risk_per_trade=0.01):
        self.risk_per_trade = risk_per_trade

    def calculate_shares(self, row, capital, max_exposure):
        if row["Signal"] == 0 or pd.isna(row["Risk"]):
            return np.nan
        risk_amount = capital * self.risk_per_trade
        return math.floor(min(row["Risk"], risk_amount) / (1 * row["ATR"]))

    def calculate_stoploss(self, row):
        if row["Signal"] == 1:
            return row["Close"] - 1 * row["ATR"]
        elif row["Signal"] == -1:
            return row["Close"] + 1 * row["ATR"]
        return np.nan

    def calculate_takeprofit(self, row):
        if row["Signal"] == 1:
            return row["Close"] + 2 * row["ATR"]
        elif row["Signal"] == -1:
            return row["Close"] - 2 * row["ATR"]
        return np.nan


class TransactionCostModel:
    """Models transaction costs."""

    def __init__(self, model_type="percentage", base_cost=0.001, volume_factor=0.0001):
        self.model_type = model_type
        self.base_cost = base_cost
        self.volume_factor = volume_factor

    def calculate_cost(self, shares, price, volume):
        if self.model_type == "percentage":
            return shares * price * self.base_cost
        elif self.model_type == "volume_weighted":
            return shares * price * (self.base_cost + self.volume_factor * (shares / volume if volume > 0 else 0))
        return 0


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


class PortfolioOptimizer:
    """Optimizes portfolio weights."""

    def __init__(self, method="mean_variance", risk_free_rate=0.03):
        self.method = method
        self.risk_free_rate = risk_free_rate

    def optimize(self, returns, cov_matrix, constraints=None):
        if self.method == "mean_variance":
            n = len(returns)

            def objective(weights):
                port_return = np.sum(returns * weights) * 252
                port_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix * 252, weights)))
                return -port_return / port_vol

            constraints = constraints or [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
            bounds = [(0, 1)] * n
            result = minimize(objective, np.ones(n) / n, bounds=bounds, constraints=constraints)
            return result.x
        return np.ones(len(returns)) / len(returns)


class Strategy(ABC):
    """Abstract base class for trading strategies."""

    def __init__(self, name, timeframe="daily", atr_period=14, feature_configs=None, base_risk=150000, atr_threshold=5):
        self.name = name
        self.timeframe = timeframe
        self.atr_period = atr_period
        self.atr_cache = {}
        self.feature_generator = FeatureGenerator(feature_configs)
        self.base_risk = base_risk
        self.atr_threshold = atr_threshold

    def base_risk_allocation(self, row):
        if row["Signal"] == 0:
            return np.nan
        atr_percent = row["ATR_percent"] if "ATR_percent" in row else np.inf
        volatility = row["1_Volatility"] if "1_Volatility" in row else np.inf
        if atr_percent <= self.atr_threshold and volatility < 0.02:
            return self.base_risk * 1.33
        return self.base_risk

    @abstractmethod
    def risk_allocation(self, row):
        pass

    @abstractmethod
    def generate_signals(self, df):
        pass

    def atr(self, high, low, close):
        key = (tuple(high), tuple(low), tuple(close), self.atr_period)
        if key not in self.atr_cache:
            tr = np.amax(
                np.vstack(((high - low).to_numpy(), (abs(high - close)).to_numpy(), (abs(low - close)).to_numpy())).T,
                axis=1)
            self.atr_cache[key] = pd.Series(tr).rolling(self.atr_period).mean().to_numpy()
        return self.atr_cache[key]


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


class RandomForestStrategy(MLStrategy):
    """Implements a Random Forest-based trading strategy."""

    def __init__(self, timeframe="daily", atr_period=14, n_estimators=100, max_depth=10, feature_configs=None,
                 base_risk=150000, atr_threshold=5):
        super().__init__("RandomForestStrategy", timeframe, atr_period, feature_configs, base_risk, atr_threshold)
        self.model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
        self.scaler = StandardScaler()

    def risk_allocation(self, row):
        base_risk = self.base_risk_allocation(row)
        if pd.isna(base_risk):
            return np.nan
        features = ["Close", "Volume", "ATR_percent", "PE_Ratio", "EPS_Growth_4", "Debt_to_Equity",
                    "Social_Media_Sentiment", "Macro_Indicator"] + \
                   [f"{w}_Volatility" for w in [1, 10, 22, 66, 132, 252]] + \
                   [col for col in row.index if col.startswith(("RSI_", "BB_", "Momentum_"))]
        X = pd.DataFrame([row[features]])
        X_scaled = self.scaler.transform(X)
        confidence = self.model.predict_proba(X_scaled).max() if hasattr(self.model, 'predict_proba') else 0.5
        return base_risk * (1.33 if confidence > 0.7 else 1.0)

    def train_model(self, df):
        features = ["Close", "Volume", "ATR_percent", "PE_Ratio", "EPS_Growth_4", "Debt_to_Equity",
                    "Social_Media_Sentiment", "Macro_Indicator"] + \
                   [f"{w}_Volatility" for w in [1, 10, 22, 66, 132, 252]] + \
                   [col for col in df.columns if col.startswith(("RSI_", "BB_", "Momentum_"))]
        X = df[features].dropna()
        y = np.where(df["Close"].shift(-1) > df["Close"], 1, -1)[X.index]
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)

    def predict(self, df):
        features = ["Close", "Volume", "ATR_percent", "PE_Ratio", "EPS_Growth_4", "Debt_to_Equity",
                    "Social_Media_Sentiment", "Macro_Indicator"] + \
                   [f"{w}_Volatility" for w in [1, 10, 22, 66, 132, 252]] + \
                   [col for col in df.columns if col.startswith(("RSI_", "BB_", "Momentum_"))]
        X = df[features].dropna()
        X_scaled = self.scaler.transform(X)
        predictions = pd.Series(self.model.predict(X_scaled), index=X.index)
        return predictions.reindex(df.index, fill_value=0)


class LSTMStrategy(MLStrategy):
    """Implements an LSTM-based trading strategy using PyTorch."""

    def __init__(self, timeframe="daily", atr_period=14, sequence_length=20, hidden_size=50, num_layers=2,
                 feature_configs=None, base_risk=150000, atr_threshold=5):
        super().__init__("LSTMStrategy", timeframe, atr_period, feature_configs, base_risk, atr_threshold)
        self.sequence_length = sequence_length
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.input_size = 8 + len([col for col in feature_configs if col["name"] in ["RSI", "Momentum"]]) + \
                          2 * len([col for col in feature_configs if col["name"] == "Bollinger_Bands"])
        self.model = self._build_model()
        self.scaler = StandardScaler()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def risk_allocation(self, row):
        base_risk = self.base_risk_allocation(row)
        if pd.isna(base_risk):
            return np.nan
        features = ["Close", "Volume", "ATR_percent", "PE_Ratio", "EPS_Growth_4", "Debt_to_Equity",
                    "Social_Media_Sentiment", "Macro_Indicator"] + \
                   [col for col in row.index if col.startswith(("RSI_", "BB_", "Momentum_"))]
        X = pd.DataFrame([row[features]])
        X_scaled = self.scaler.transform(X)
        X_tensor = torch.tensor(X_scaled[-self.sequence_length:], dtype=torch.float32).to(self.device)
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(X_tensor.unsqueeze(0))
            confidence = torch.softmax(outputs, dim=1).max().item()
        return base_risk * (1.2 if confidence > 0.7 else 1.0)

    def _build_model(self):
        class LSTMModel(nn.Module):
            def __init__(self, input_size, hidden_size, num_layers):
                super(LSTMModel, self).__init__()
                self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
                self.fc = nn.Linear(hidden_size, 2)

            def forward(self, x):
                h0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
                c0 = torch.zeros(self.lstm.num_layers, x.size(0), self.lstm.hidden_size).to(x.device)
                out, _ = self.lstm(x, (h0, c0))
                out = self.fc(out[:, -1, :])
                return out

        return LSTMModel(input_size=self.input_size, hidden_size=self.hidden_size, num_layers=self.num_layers)

    def train_model(self, df):
        features = ["Close", "Volume", "ATR_percent", "PE_Ratio", "EPS_Growth_4", "Debt_to_Equity",
                    "Social_Media_Sentiment", "Macro_Indicator"] + \
                   [col for col in df.columns if col.startswith(("RSI_", "BB_", "Momentum_"))]
        X = df[features].dropna().values
        y = np.where(df["Close"].shift(-1) > df["Close"], 1, -1)[df[features].dropna().index]
        X_scaled = self.scaler.fit_transform(X)

        sequences = []
        targets = []
        for i in range(len(X_scaled) - self.sequence_length):
            sequences.append(X_scaled[i:i + self.sequence_length])
            targets.append(y[i + self.sequence_length])

        if len(sequences) == 0:
            return

        X_tensor = torch.tensor(sequences, dtype=torch.float32).to(self.device)
        y_tensor = torch.tensor(targets, dtype=torch.long).to(self.device)

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)

        self.model.train()
        for epoch in range(10):
            optimizer.zero_grad()
            outputs = self.model(X_tensor)
            loss = criterion(outputs, y_tensor)
            loss.backward()
            optimizer.step()

    def predict(self, df):
        features = ["Close", "Volume", "ATR_percent", "PE_Ratio", "EPS_Growth_4", "Debt_to_Equity",
                    "Social_Media_Sentiment", "Macro_Indicator"] + \
                   [col for col in df.columns if col.startswith(("RSI_", "BB_", "Momentum_"))]
        X = df[features].dropna().values
        X_scaled = self.scaler.transform(X)

        sequences = []
        for i in range(len(X_scaled) - self.sequence_length + 1):
            sequences.append(X_scaled[i:i + self.sequence_length])

        if len(sequences) == 0:
            return pd.Series(0, index=df.index)

        X_tensor = torch.tensor(sequences, dtype=torch.float32).to(self.device)
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(X_tensor)
            predictions = torch.argmax(outputs, dim=1).cpu().numpy() - 1
        return pd.Series(np.pad(predictions, (self.sequence_length - 1, 0), mode='constant'), index=df.index)


class QLStrategy(MLStrategy):
    """Implements an RL-based trading strategy with PPO or DQN."""

    def __init__(self, timeframe="daily", atr_period=14, state_size=10, action_space=[0, 1, -1],
                 rl_algorithm="dqn", learning_rate=0.001, discount_factor=0.95, max_steps=100,
                 hidden_size=64, replay_buffer_size=10000, batch_size=64, target_update_freq=100, feature_configs=None,
                 base_risk=150000, atr_threshold=5):
        super().__init__("QLStrategy", timeframe, atr_period, feature_configs, base_risk, atr_threshold)
        self.state_size = state_size
        self.action_space = action_space
        self.rl_algorithm = rl_algorithm.lower()
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.max_steps = max_steps
        self.hidden_size = hidden_size
        self.replay_buffer_size = replay_buffer_size
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq
        self.features = ["Close", "Volume", "ATR_percent", "PE_Ratio", "EPS_Growth_4", "Debt_to_Equity",
                         "Social_Media_Sentiment", "Macro_Indicator"] + \
                        [f"{w}_Volatility" for w in [1, 10, 22]] + \
                        [col for col in feature_configs if col["name"] in ["RSI", "Momentum"]] + \
                        [f"BB_upper_{config['params']['period']}" for config in feature_configs if
                         config["name"] == "Bollinger_Bands"] + \
                        [f"BB_lower_{config['params']['period']}" for config in feature_configs if
                         config["name"] == "Bollinger_Bands"]
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.scaler = StandardScaler()
        self.epsilon = 0.1

        if self.rl_algorithm == "ppo":
            self.policy_net = self._build_ppo_model().to(self.device)
            self.value_net = self._build_value_model().to(self.device)
            self.policy_optimizer = optim.Adam(self.policy_net.parameters(), lr=self.learning_rate)
            self.value_optimizer = optim.Adam(self.value_net.parameters(), lr=self.learning_rate)
        else:
            self.q_net = self._build_dqn_model().to(self.device)
            self.target_net = self._build_dqn_model().to(self.device)
            self.target_net.load_state_dict(self.q_net.state_dict())
            self.optimizer = optim.Adam(self.q_net.parameters(), lr=self.learning_rate)
            self.replay_buffer = deque(maxlen=replay_buffer_size)
            self.step_count = 0

    def risk_allocation(self, row):
        base_risk = self.base_risk_allocation(row)
        if pd.isna(base_risk):
            return np.nan
        state = row[self.features][:self.state_size].values
        state_tensor = torch.tensor([state], dtype=torch.float32).to(self.device)
        if self.rl_algorithm == "ppo":
            with torch.no_grad():
                probs = self.policy_net(state_tensor)
                confidence = probs.max().item()
            return base_risk * (1.33 if confidence > 0.7 else 1.0)
        else:
            with torch.no_grad():
                q_values = self.q_net(state_tensor)
                confidence = q_values.max().item()
            return base_risk * (1.33 if confidence > 0.5 else 1.0)

    def _build_ppo_model(self):
        class PolicyNetwork(nn.Module):
            def __init__(self, state_size, action_size, hidden_size):
                super(PolicyNetwork, self).__init__()
                self.fc1 = nn.Linear(state_size, hidden_size)
                self.fc2 = nn.Linear(hidden_size, hidden_size)
                self.fc3 = nn.Linear(hidden_size, action_size)
                self.softmax = nn.Softmax(dim=-1)

            def forward(self, x):
                x = torch.relu(self.fc1(x))
                x = torch.relu(self.fc2(x))
                x = self.fc3(x)
                return self.softmax(x)

        return PolicyNetwork(self.state_size, len(self.action_space), self.hidden_size)

    def _build_value_model(self):
        class ValueNetwork(nn.Module):
            def __init__(self, state_size, hidden_size):
                super(ValueNetwork, self).__init__()
                self.fc1 = nn.Linear(state_size, hidden_size)
                self.fc2 = nn.Linear(hidden_size, hidden_size)
                self.fc3 = nn.Linear(hidden_size, 1)

            def forward(self, x):
                x = torch.relu(self.fc1(x))
                x = torch.relu(self.fc2(x))
                return self.fc3(x)

        return ValueNetwork(self.state_size, self.hidden_size)

    def _build_dqn_model(self):
        class QNetwork(nn.Module):
            def __init__(self, state_size, action_size, hidden_size):
                super(QNetwork, self).__init__()
                self.fc1 = nn.Linear(state_size, hidden_size)
                self.fc2 = nn.Linear(hidden_size, hidden_size)
                self.fc3 = nn.Linear(hidden_size, action_size)

            def forward(self, x):
                x = torch.relu(self.fc1(x))
                x = torch.relu(self.fc2(x))
                return self.fc3(x)

        return QNetwork(self.state_size, len(self.action_space), self.hidden_size)

    def train_model(self, df):
        if len(df) < 2:
            return

        df = df.copy()
        X = df[self.features].dropna()
        X_scaled = self.scaler.fit_transform(X)
        df[self.features] = pd.DataFrame(X_scaled, index=X.index, columns=self.features)
        env = TradingEnvironment(df, self.features, self.action_space, self.max_steps)

        if self.rl_algorithm == "ppo":
            self._train_ppo(env)
        else:
            self._train_dqn(env)

    def _train_ppo(self, env, episodes=10, clip_epsilon=0.2, gae_lambda=0.95):
        for _ in range(episodes):
            state = env.reset()
            states, actions, rewards, log_probs, values = [], [], [], [], []
            done = False

            while not done:
                state_tensor = torch.tensor([state], dtype=torch.float32).to(self.device)
                with torch.no_grad():
                    probs = self.policy_net(state_tensor)
                    value = self.value_net(state_tensor)
                    dist = torch.distributions.Categorical(probs)
                    action_idx = dist.sample()
                    log_prob = dist.log_prob(action_idx)

                action = self.action_space[action_idx.item()]
                next_state, reward, done = env.step(action)

                states.append(state)
                actions.append(action_idx)
                rewards.append(reward)
                log_probs.append(log_prob)
                values.append(value)

                state = next_state

            returns = []
            advantages = []
            discounted_sum = 0
            for r in rewards[::-1]:
                discounted_sum = r + self.discount_factor * discounted_sum
                returns.insert(0, discounted_sum)

            returns = torch.tensor(returns, dtype=torch.float32).to(self.device)
            values = torch.cat(values).squeeze()
            advantages = returns - values
            advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

            states_tensor = torch.tensor(states, dtype=torch.float32).to(self.device)
            actions_tensor = torch.tensor(actions, dtype=torch.long).to(self.device)
            old_log_probs = torch.cat(log_probs)

            for _ in range(5):
                probs = self.policy_net(states_tensor)
                dist = torch.distributions.Categorical(probs)
                new_log_probs = dist.log_prob(actions_tensor)
                ratios = torch.exp(new_log_probs - old_log_probs)
                surr1 = ratios * advantages
                surr2 = torch.clamp(ratios, 1 - clip_epsilon, 1 + clip_epsilon) * advantages
                policy_loss = -torch.min(surr1, surr2).mean()

                value_pred = self.value_net(states_tensor).squeeze()
                value_loss = ((value_pred - returns) ** 2).mean()

                self.policy_optimizer.zero_grad()
                policy_loss.backward()
                self.policy_optimizer.step()

                self.value_optimizer.zero_grad()
                value_loss.backward()
                self.value_optimizer.step()

    def _train_dqn(self, env, episodes=10):
        for _ in range(episodes):
            state = env.reset()
            done = False
            while not done:
                state_tensor = torch.tensor([state], dtype=torch.float32).to(self.device)
                if random.random() < self.epsilon:
                    action_idx = random.randint(0, len(self.action_space) - 1)
                else:
                    with torch.no_grad():
                        q_values = self.q_net(state_tensor)
                        action_idx = q_values.argmax().item()

                action = self.action_space[action_idx]
                next_state, reward, done = env.step(action)
                self.replay_buffer.append((state, action_idx, reward, next_state, done))

                if len(self.replay_buffer) >= self.batch_size:
                    batch = random.sample(self.replay_buffer, self.batch_size)
                    states, actions, rewards, next_states, dones = zip(*batch)

                    states_tensor = torch.tensor(states, dtype=torch.float32).to(self.device)
                    actions_tensor = torch.tensor(actions, dtype=torch.long).to(self.device)
                    rewards_tensor = torch.tensor(rewards, dtype=torch.float32).to(self.device)
                    next_states_tensor = torch.tensor(next_states, dtype=torch.float32).to(self.device)
                    dones_tensor = torch.tensor(dones, dtype=torch.float32).to(self.device)

                    q_values = self.q_net(states_tensor).gather(1, actions_tensor.unsqueeze(1)).squeeze(1)
                    with torch.no_grad():
                        next_q_values = self.target_net(next_states_tensor).max(1)[0]
                        targets = rewards_tensor + self.discount_factor * next_q_values * (1 - dones_tensor)

                    loss = nn.MSELoss()(q_values, targets)
                    self.optimizer.zero_grad()
                    loss.backward()
                    self.optimizer.step()

                    self.step_count += 1
                    if self.step_count % self.target_update_freq == 0:
                        self.target_net.load_state_dict(self.q_net.state_dict())

                state = next_state

        self.epsilon = max(0.01, self.epsilon * 0.995)

    def predict(self, df):
        df = df.copy()
        X = df[self.features].dropna()
        X_scaled = self.scaler.transform(X)
        df[self.features] = pd.DataFrame(X_scaled, index=X.index, columns=self.features)
        predictions = []

        for i, row in df.iterrows():
            state = row[self.features][:self.state_size].values
            state_tensor = torch.tensor([state], dtype=torch.float32).to(self.device)

            if self.rl_algorithm == "ppo":
                with torch.no_grad():
                    probs = self.policy_net(state_tensor)
                    action_idx = torch.distributions.Categorical(probs).sample().item()
            else:
                with torch.no_grad():
                    q_values = self.q_net(state_tensor)
                    action_idx = q_values.argmax().item()

            action = self.action_space[action_idx]
            predictions.append(action)

        return pd.Series(predictions, index=df.index)


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


class Portfolio:
    """Manages positions, risk, and trade execution."""

    def __init__(self, initial_capital=10000000, transaction_cost_model=None, execution_model=None, position_sizer=None,
                 max_stocks=5, max_capital_deployed=0.9):
        self.capital = initial_capital
        self.positions = []
        self.trades = []
        self.uid = 1
        self.transaction_cost_model = transaction_cost_model or TransactionCostModel()
        self.execution_model = execution_model or ExecutionModel()
        self.position_sizer = position_sizer or ATRPositionSizer()
        self.max_stocks = max_stocks
        self.max_capital_deployed = max_capital_deployed * initial_capital

    def calculate_trailing_sl(self, df):
        df = df.reset_index()
        trail_sl = np.full(len(df), np.nan)
        for i in range(1, len(df)):
            if pd.isna(df["Stoploss_inter"].iloc[i]):
                if df["Duration"].iloc[i] > 0:
                    prev_close = df["Close"].iloc[i - 1]
                    prev_atr = df["Entry_ATR"].iloc[i - 1]
                    inter_signal = df["Inter_Signal"].iloc[i - 1]
                    potential_sl = prev_close - 1 * prev_atr if inter_signal == 1 else prev_close + 1 * prev_atr if inter_signal == -1 else np.nan
                    if inter_signal == 1:
                        trail_sl[i] = max(trail_sl[i - 1], potential_sl) if not pd.isna(
                            trail_sl[i - 1]) else potential_sl
                    elif inter_signal == -1:
                        trail_sl[i] = min(trail_sl[i - 1], potential_sl) if not pd.isna(
                            trail_sl[i - 1]) else potential_sl
                else:
                    trail_sl[i] = trail_sl[i - 1]
            else:
                trail_sl[i] = df["Stoploss_inter"].iloc[i]
        return trail_sl

    def calculate_exit_price(self, row):
        if (row["Inter_Signal"] == 1) and (row["Duration"] > 0) and (row["Low"] <= row["Trail_SL"]):
            exit_price = row["Open"] if row["Open"] <= row["Trail_SL"] else row["Trail_SL"]
            return self.execution_model.execute_order(row, -1)
        elif (row["Inter_Signal"] == -1) and (row["Duration"] > 0) and (row["High"] >= row["Trail_SL"]):
            exit_price = row["Open"] if row["Open"] >= row["Trail_SL"] else row["Trail_SL"]
            return self.execution_model.execute_order(row, 1)
        elif (row["Inter_Signal"] == 1) and (row["Duration"] > 0) and (row["High"] >= row["Takeprofit_inter"]):
            exit_price = row["Open"] if row["Open"] >= row["Takeprofit_inter"] else row["Takeprofit_inter"]
            return self.execution_model.execute_order(row, -1)
        elif (row["Inter_Signal"] == -1) and (row["Duration"] > 0) and (row["Low"] <= row["Takeprofit_inter"]):
            exit_price = row["Open"] if row["Open"] <= row["Takeprofit_inter"] else row["Takeprofit_inter"]
            return self.execution_model.execute_order(row, 1)
        return np.nan

    def calculate_mtm(self, row):
        if pd.isna(row["Inter_Signal"]):
            return np.nan
        entry_cost = self.transaction_cost_model.calculate_cost(row["Num_Shares"], row["Entry_Price"], row["Volume"])
        current_value = row["Num_Shares"] * row["Close"]
        if row["Inter_Signal"] == 1:
            return current_value - (row["Num_Shares"] * row["Entry_Price"]) - entry_cost
        elif row["Inter_Signal"] == -1:
            return (row["Num_Shares"] * row["Entry_Price"]) - current_value - entry_cost
        return np.nan

    def can_open_position(self, ticker, num_shares, close_price, strategy, timeframe):
        current_tickers = {pos[0] for pos in self.positions}
        if ticker not in current_tickers and len(current_tickers) >= self.max_stocks:
            return False
        current_exposure = sum(pos[1] * pos[2] for pos in self.positions)
        new_exposure = num_shares * close_price
        return current_exposure + new_exposure <= self.max_capital_deployed

    def manage_positions(self, df, ticker, strategy, timeframe, strategy_obj):
        df = df.copy()
        df["Risk"] = df.apply(strategy_obj.risk_allocation, axis=1)
        df["Num_Shares"] = df.apply(
            lambda x: self.position_sizer.calculate_shares(x, self.capital, self.max_capital_deployed), axis=1)
        df["Entry_Price"] = df.apply(lambda x: self.execution_model.execute_order(x, x["Signal"]), axis=1)
        df["Entry_Price"] = np.where(
            df.apply(
                lambda x: x["Signal"] != 0 and self.can_open_position(ticker, x["Num_Shares"], x["Close"], strategy,
                                                                      timeframe), axis=1),
            df["Entry_Price"],
            np.nan
        )
        df["Signal"] = np.where(df["Entry_Price"].isna() & (df["Signal"] != 0), 0, df["Signal"])
        df["Long_Signal"] = np.where(df["Signal"] == -1, -1, 0)
        df["Short_Signal"] = np.where(df["Signal"] == 1, 1, 0)
        df["Entry_ATR"] = np.where(df["Signal"] != 0, df["ATR"], np.nan)
        df["Entry_Date"] = np.where(df["Signal"] != 0, df["date"], np.nan)
        df["Count"] = range(len(df))
        df["Entry_Index"] = np.where(df["Signal"] != 0, df["Count"], np.nan)
        df["Inter_Signal"] = df["Signal"].replace(0, np.nan).ffill()
        df["Duration"] = df["Count"] - df["Entry_Index"].ffill()
        df["Stoploss_inter"] = df.apply(self.position_sizer.calculate_stoploss, axis=1)
        df["Takeprofit_inter"] = df.apply(self.position_sizer.calculate_takeprofit, axis=1)
        df["Trail_SL"] = np.nan
        df["Exit_Signal"] = np.where(
            ((df["Inter_Signal"] == 1) & (df["Duration"] > 0) & (df["Low"] <= df["Trail_SL"])) |
            ((df["Inter_Signal"] == -1) & (df["Duration"] > 0) & (df["High"] >= df["Trail_SL"])) |
            ((df["Inter_Signal"] == 1) & (df["Duration"] > 0) & (df["High"] >= df["Takeprofit_inter"])) |
            ((df["Inter_Signal"] == -1) & (df["Duration"] > 0) & (df["Low"] <= df["Takeprofit_inter"])),
            1, np.nan
        )
        df["Exit_Price"] = df.apply(self.calculate_exit_price, axis=1)
        df["MTM"] = df.apply(self.calculate_mtm, axis=1)
        df["Open_Positions"] = np.where(df["Inter_Signal"].notna(), 1, 0)
        df["trade_identifier"] = np.where(df["Signal"] != 0, self.uid, np.nan).ffill()

        filtered_df = df[df["Inter_Signal"].notna()]
        if not filtered_df.empty:
            df["Trail_SL"] = self.calculate_trailing_sl(filtered_df).reindex(df.index, fill_value=np.nan)

        for i, row in df.iterrows():
            if row["Signal"] != 0 and pd.notna(row["Entry_Price"]):
                self.positions.append(
                    (ticker, row["Num_Shares"], row["Entry_Price"], row["date"], row["Signal"], strategy, timeframe))
                self.uid += 1
            if row["Exit_Signal"] == 1:
                self.positions = [pos for pos in self.positions if
                                  pos[0] != ticker or pos[6] != timeframe or pos[5] != strategy]
                self.trades.append((ticker, strategy, timeframe, row["trade_identifier"], row["Exit_Price"],
                                    row["Entry_Price"], row["Num_Shares"], row["Inter_Signal"]))

        return df


class PerformanceTracker:
    """Tracks and computes trade performance metrics."""

    def __init__(self, risk_free_rate=0.03):
        self.risk_free_rate = risk_free_rate
        self.trade_summary = pd.DataFrame(columns=[
            "Ticker", "Strategy", "Timeframe", "Number_of_Trades", "Average_Returns_from_Winners",
            "Average_Returns_from_Losers", "Average_Trade_Returns",
            "Avg_Holding_Period", "Avg_Holding_Period_from_Winners",
            "Avg_Holding_Period_from_Losers", "Reward_Risk", "Strike_Rate",
            "Expectancy", "Max_Drawdown", "Calmar_Ratio", "Sharpe_Ratio",
            "Sortino_Ratio", "Annualized_Returns", "Cumulative_Returns",
            "VaR_95", "CVaR_95", "Omega_Ratio"
        ])
        self.aggregated_metrics = pd.DataFrame(columns=[
            "Strategy", "Total_Trades", "Total_Return", "Average_Return",
            "Strike_Rate", "Expectancy", "Max_Drawdown", "Calmar_Ratio",
            "Sharpe_Ratio", "Sortino_Ratio", "Annualized_Returns",
            "Cumulative_Returns", "VaR_95", "CVaR_95", "Omega_Ratio"
        ])
        self.portfolio_metrics = pd.DataFrame(columns=[
            "Portfolio_Management_and_Tracker", "Total_Trades", "Total_Return", "Average_Return",
            "Strike_Rate", "Expectancy", "Max_Drawdown", "Calmar_Ratio",
            "Sharpe_Ratio", "Sortino_Ratio", "Annualized_Returns",
            "Cumulative_Returns", "VaR_95", "CVaR_95", "Omega_Ratio"
        ])
        self.trade_data = {}
        self.capital = None

    def calculate_calmar_ratio(self, annualized_return, max_drawdown):
        return annualized_return / abs(max_drawdown) if max_drawdown != 0 else np.inf

    def calculate_sharpe_ratio(self, returns):
        mean_return = returns.mean() * 252
        std_dev = returns.std() * np.sqrt(252)
        return (mean_return - self.risk_free_rate) / std_dev if std_dev != 0 else np.inf

    def calculate_sortino_ratio(self, returns):
        mean_return = returns.mean() * 252
        downside_returns = returns[returns < 0]
        downside_dev = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else np.nan
        return (mean_return - self.risk_free_rate) / downside_dev if downside_dev != 0 else np.inf

    def calculate_var(self, returns, confidence_level=0.95):
        return np.percentile(returns, 100 * (1 - confidence_level))

    def calculate_cvar(self, returns, confidence_level=0.95):
        var = self.calculate_var(returns, confidence_level)
        return returns[returns <= var].mean() if len(returns[returns <= var]) > 0 else np.nan

    def calculate_omega_ratio(self, returns, threshold=0):
        excess_returns = returns - threshold
        positive = excess_returns[excess_returns > 0].sum()
        negative = -excess_returns[excess_returns < 0].sum()
        return positive / negative if negative != 0 else np.inf

    def calculate_annualized_returns(self, cumulative_return, days):
        if days <= 0:
            return np.nan
        years = days / 252
        return ((1 + cumulative_return / 100) ** (1 / years) - 1) * 100 if years > 0 else np.nan

    def update_metrics(self, ticker, strategy_name, timeframe, df):
        trades = df[df["Exit_Signal"] == 1].copy()
        if len(trades) == 0:
            return

        num_trades = len(trades)
        returns = trades.apply(
            lambda x: x["Num_Shares"] * (x["Exit_Price"] - x["Entry_Price"]) if x["Inter_Signal"] == 1 else
            x["Num_Shares"] * (-x["Exit_Price"] + x["Entry_Price"]), axis=1
        )
        winners = returns[returns > 0]
        losers = returns[returns <= 0]
        avg_winner = winners.mean() if len(winners) > 0 else 0
        avg_loser = losers.mean() if len(losers) > 0 else 0
        avg_return = returns.mean() if len(returns) > 0 else 0
        holding_period = trades["Duration"].mean()
        holding_winners = trades[returns > 0]["Duration"].mean() if len(winners) > 0 else 0
        holding_losers = trades[returns <= 0]["Duration"].mean() if len(losers) > 0 else 0
        strike_rate = len(winners) / num_trades if num_trades > 0 else 0
        expectancy = (strike_rate * avg_winner) + ((1 - strike_rate) * avg_loser) if num_trades > 0 else 0
        equity_curve = returns.cumsum()
        max_drawdown = (equity_curve - equity_curve.cummax()).min() if len(equity_curve) > 0 else 0
        reward_risk = avg_winner / abs(avg_loser) if avg_loser != 0 else np.inf
        days = (trades["Datetime"].max() - trades["Datetime"].min()).days
        cumulative_return = equity_curve.iloc[-1] / self.capital * 100 if self.capital else 0
        annualized_return = self.calculate_annualized_returns(cumulative_return, days)
        calmar_ratio = self.calculate_calmar_ratio(annualized_return, max_drawdown)
        sharpe_ratio = self.calculate_sharpe_ratio(returns / self.capital if self.capital else returns)
        sortino_ratio = self.calculate_sortino_ratio(returns / self.capital if self.capital else returns)
        var_95 = self.calculate_var(returns / self.capital if self.capital else returns)
        cvar_95 = self.calculate_cvar(returns / self.capital if self.capital else returns)
        omega_ratio = self.calculate_omega_ratio(returns / self.capital if self.capital else returns)

        self.trade_summary.loc[len(self.trade_summary)] = {
            "Ticker": ticker,
            "Strategy": strategy_name,
            "Timeframe": timeframe,
            "Number_of_Trades": num_trades,
            "Average_Returns_from_Winners": avg_winner,
            "Average_Returns_from_Losers": avg_loser,
            "Average_Trade_Returns": avg_return,
            "Avg_Holding_Period": holding_period,
            "Avg_Holding_Period_from_Winners": holding_winners,
            "Avg_Holding_Period_from_Losers": holding_losers,
            "Reward_Risk": reward_risk,
            "Strike_Rate": strike_rate,
            "Expectancy": expectancy,
            "Max_Drawdown": max_drawdown,
            "Calmar_Ratio": calmar_ratio,
            "Sharpe_Ratio": sharpe_ratio,
            "Sortino_Ratio": sortino_ratio,
            "Annualized_Returns": annualized_return,
            "Cumulative_Returns": cumulative_return,
            "VaR_95": var_95,
            "CVaR_95": cvar_95,
            "Omega_Ratio": omega_ratio
        }

        self.trade_data[(ticker, strategy_name, timeframe)] = {
            "trades": trades,
            "returns": returns,
            "equity_curve": equity_curve,
            "drawdowns": equity_curve - equity_curve.cummax(),
            "df": df
        }


    def aggregate_metrics(self):
        """Aggregate metrics across all strategies."""
        strategies = self.trade_summary["Strategy"].unique()
        self.aggregated_metrics = pd.DataFrame(columns=self.aggregated_metrics.columns)

        for strategy in strategies:
            strategy_data = self.trade_summary[self.trade_summary["Strategy"] == strategy]
            if strategy_data.empty:
                continue

            total_trades = strategy_data["Number_of_Trades"].sum()
            total_return = strategy_data["Cumulative_Returns"].sum()
            avg_return = strategy_data["Average_Trade_Returns"].mean()
            strike_rate = strategy_data["Strike_Rate"].mean()
            expectancy = strategy_data["Expectancy"].mean()
            max_drawdown = strategy_data["Max_Drawdown"].min()

            # Combine returns across all tickers and timeframes for this strategy
            all_returns = []
            for (ticker, strat, timeframe), data in self.trade_data.items():
                if strat == strategy:
                    all_returns.append(data["returns"] / self.capital if self.capital else data["returns"])
            combined_returns = pd.concat(all_returns) if all_returns else pd.Series()

            days = (strategy_data["Datetime"].max() - strategy_data[
                "Datetime"].min()).days if not strategy_data.empty else 0
            cumulative_return = strategy_data["Cumulative_Returns"].sum()
            annualized_return = self.calculate_annualized_returns(cumulative_return, days)
            calmar_ratio = self.calculate_calmar_ratio(annualized_return, max_drawdown)
            sharpe_ratio = self.calculate_sharpe_ratio(combined_returns) if not combined_returns.empty else np.nan
            sortino_ratio = self.calculate_sortino_ratio(combined_returns) if not combined_returns.empty else np.nan
            var_95 = self.calculate_var(combined_returns) if not combined_returns.empty else np.nan
            cvar_95 = self.calculate_cvar(combined_returns) if not combined_returns.empty else np.nan
            omega_ratio = self.calculate_omega_ratio(combined_returns) if not combined_returns.empty else np.nan

            self.aggregated_metrics.loc[len(self.aggregated_metrics)] = {
                "Strategy": strategy,
                "Total_Trades": total_trades,
                "Total_Return": total_return,
                "Average_Return": avg_return,
                "Strike_Rate": strike_rate,
                "Expectancy": expectancy,
                "Max_Drawdown": max_drawdown,
                "Calmar_Ratio": calmar_ratio,
                "Sharpe_Ratio": sharpe_ratio,
                "Sortino_Ratio": sortino_ratio,
                "Annualized_Returns": annualized_return,
                "Cumulative_Returns": cumulative_return,
                "VaR_95": var_95,
                "CVaR_95": cvar_95,
                "Omega_Ratio": omega_ratio
            }

    def aggregate_portfolio(self):
        """Compute portfolio-level metrics across all strategies and tickers."""
        if self.trade_summary.empty:
            return

        total_trades = self.trade_summary["Number_of_Trades"].sum()
        total_return = self.trade_summary["Cumulative_Returns"].sum()
        avg_return = self.trade_summary["Average_Trade_Returns"].mean()
        strike_rate = self.trade_summary["Strike_Rate"].mean()
        expectancy = self.trade_summary["Expectancy"].mean()
        max_drawdown = self.trade_summary["Max_Drawdown"].min()

        # Combine all returns
        all_returns = []
        for _, data in self.trade_data.items():
            all_returns.append(data["returns"] / self.capital if self.capital else data["returns"])
        combined_returns = pd.concat(all_returns) if all_returns else pd.Series()

        days = (self.trade_summary["Datetime"].max() - self.trade_summary[
            "Datetime"].min()).days if not self.trade_summary.empty else 0
        cumulative_return = self.trade_summary["Cumulative_Returns"].sum()
        annualized_return = self.calculate_annualized_returns(cumulative_return, days)
        calmar_ratio = self.calculate_calmar_ratio(annualized_return, max_drawdown)
        sharpe_ratio = self.calculate_sharpe_ratio(combined_returns) if not combined_returns.empty else np.nan
        sortino_ratio = self.calculate_sortino_ratio(combined_returns) if not combined_returns.empty else np.nan
        var_95 = self.calculate_var(combined_returns) if not combined_returns.empty else np.nan
        cvar_95 = self.calculate_cvar(combined_returns) if not combined_returns.empty else np.nan
        omega_ratio = self.calculate_omega_ratio(combined_returns) if not combined_returns.empty else np.nan

        self.portfolio_metrics.loc[len(self.portfolio_metrics)] = {
            "Portfolio_Management_and_Tracker": "All Strategies",
            "Total_Trades": total_trades,
            "Total_Return": total_return,
            "Average_Return": avg_return,
            "Strike_Rate": strike_rate,
            "Expectancy": expectancy,
            "Max_Drawdown": max_drawdown,
            "Calmar_Ratio": calmar_ratio,
            "Sharpe_Ratio": sharpe_ratio,
            "Sortino_Ratio": sortino_ratio,
            "Annualized_Returns": annualized_return,
            "Cumulative_Returns": cumulative_return,
            "VaR_95": var_95,
            "CVaR_95": cvar_95,
            "Omega_Ratio": omega_ratio
        }

    def get_metrics(self, level="strategy"):
        """Return metrics at specified level ('trade', 'strategy', 'portfolio')."""
        if level == "trade":
            return self.trade_summary
        elif level == "strategy":
            return self.aggregated_metrics
        elif level == "portfolio":
            return self.portfolio_metrics
        return None

    def plot_performance(self, level="strategy"):
        """Plot performance metrics using Plotly."""
        metrics = self.get_metrics(level)
        if metrics is None or metrics.empty:
            print("No metrics available to plot.")
            return

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Cumulative Returns", "Max Drawdown", "Sharpe Ratio", "Sortino Ratio"),
            specs=[[{"type": "bar"}, {"type": "bar"}], [{"type": "bar"}, {"type": "bar"}]]
        )

        identifier = "Strategy" if level == "strategy" else "Portfolio_Management_and_Tracker" if level == "portfolio" else "Ticker"
        fig.add_trace(
            go.Bar(x=metrics[identifier], y=metrics["Cumulative_Returns"], name="Cumulative Returns"),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(x=metrics[identifier], y=metrics["Max_Drawdown"], name="Max Drawdown"),
            row=1, col=2
        )
        fig.add_trace(
            go.Bar(x=metrics[identifier], y=metrics["Sharpe_Ratio"], name="Sharpe Ratio"),
            row=2, col=1
        )
        fig.add_trace(
            go.Bar(x=metrics[identifier], y=metrics["Sortino_Ratio"], name="Sortino Ratio"),
            row=2, col=2
        )

        fig.update_layout(
            title_text=f"{level.capitalize()} Performance Metrics",
            showlegend=True,
            height=600
        )
        fig.show()

if __name__ == "__main__":
    import pandas as pd
    import numpy as np

    # Create sample trade data
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='B')
    sample_df = pd.DataFrame({
        'Datetime': dates,
        'Close': np.random.normal(100, 10, len(dates)),
        'Signal': np.random.choice([0, 1, -1], len(dates)),
        'Num_Shares': np.random.randint(100, 1000, len(dates)),
        'Entry_Price': np.random.normal(100, 5, len(dates)),
        'Exit_Price': np.random.normal(100, 5, len(dates)),
        'Inter_Signal': np.random.choice([1, -1, np.nan], len(dates)),
        'Duration': np.random.randint(1, 10, len(dates)),
        'ATR': np.random.uniform(1, 3, len(dates)),
        'Volume': np.random.randint(10000, 100000, len(dates))
    })

    # Initialize PerformanceTracker
    tracker = PerformanceTracker(risk_free_rate=0.03)
    tracker.capital = 10000000

    # Update metrics for two strategies
    tracker.update_metrics('AAPL', 'GapStrategy', 'daily', sample_df)
    sample_df['Signal'] = np.random.choice([0, 1, -1], len(dates))  # Different signals for another strategy
    tracker.update_metrics('AAPL', 'MACDStrategy', 'daily', sample_df)

    # Aggregate metrics
    tracker.aggregate_metrics()
    tracker.aggregate_portfolio()

    # Display results
    print("Strategy-Level Metrics:")
    print(tracker.get_metrics('strategy'))
    print("\nPortfolio_Management_and_Tracker-Level Metrics:")
    print(tracker.get_metrics('portfolio'))

    # Plot performance
    tracker.plot_performance('strategy')