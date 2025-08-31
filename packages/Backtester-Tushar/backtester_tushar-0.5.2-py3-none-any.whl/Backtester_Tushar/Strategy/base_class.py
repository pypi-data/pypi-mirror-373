import numpy as np
from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional, Dict, Any, Tuple, Union
import logging
from Backtester_Tushar.Feature_Generator.feature_gen import FeatureGenerator
from Backtester_Tushar.Strategy.utils import rolling_zscore


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
        """Generate signals for single ticker DataFrame."""
        pass

    def generate_signals_multi_ticker(self, df):
        """
        Generate signals for master DataFrame containing multiple tickers.

        Args:
            df: Master DataFrame with 'ticker' column and OHLCV data

        Returns:
            DataFrame with signals generated for each ticker
        """
        if 'ticker' not in df.columns:
            raise ValueError("DataFrame must contain 'ticker' column for multi-ticker processing")

        results = []

        # Group by ticker and process each group
        for ticker, group_df in df.groupby('ticker'):
            try:
                # Generate signals for this ticker
                ticker_signals = self.generate_signals(group_df.copy())

                # Ensure ticker column is preserved
                ticker_signals['ticker'] = ticker

                results.append(ticker_signals)

            except Exception as e:
                print(f"Error processing ticker {ticker}: {str(e)}")
                # Optionally, you can choose to skip errored tickers or raise the error
                continue

        if not results:
            raise ValueError("No tickers were successfully processed")

        # Concatenate all results
        final_df = pd.concat(results, ignore_index=True)

        # Restore original order if possible (assuming df has a date/datetime column)
        date_cols = [col for col in df.columns if
                     'date' in col.lower() or df[col].dtype in ['datetime64[ns]', 'object']]
        if date_cols and 'ticker' in final_df.columns:
            try:
                final_df = final_df.sort_values(['ticker', date_cols[0]]).reset_index(drop=True)
            except:
                # If sorting fails, just return as-is
                pass

        return final_df

    def atr(self, high, low, close):
        key = (tuple(high), tuple(low), tuple(close), self.atr_period)
        if key not in self.atr_cache:
            tr = np.amax(
                np.vstack(((high - low).to_numpy(), (abs(high - close)).to_numpy(), (abs(low - close)).to_numpy())).T,
                axis=1)
            self.atr_cache[key] = pd.Series(tr).rolling(self.atr_period).mean().to_numpy()
        return self.atr_cache[key]

    def normalize_signals_industry_neutral(self, signals_df):
        """
        Two-step normalization (faster version):
        1. Industry-neutral z-score within (date, sector).
        2. Cross-sectional z-score across all tickers in the same date.
        """
        df = signals_df.copy()
        if 'sector' not in df.columns:
            raise ValueError("Sector column is required for industry-neutral normalization")

        # --- Step 1: sector-neutral normalization ---
        sector_stats = (
            df.groupby(['date', 'sector'])['signal_descriptor']
            .agg(['mean', 'std'])
            .rename(columns={'mean': 'sector_mean', 'std': 'sector_std'})
            .reset_index()
        )
        df = df.merge(sector_stats, on=['date', 'sector'], how='left')
        df['signal_descriptor'] = (df['signal_descriptor'] - df['sector_mean']) / df['sector_std']
        # df['signal_descriptor'] = df['signal_descriptor'].replace([np.inf, -np.inf], 0.0).fillna(0.0)
        df = df.drop(columns=['sector_mean', 'sector_std'])

        # --- Step 2: cross-sectional normalization ---
        cross_stats = (
            df.groupby('date')['signal_descriptor']
            .agg(['mean', 'std'])
            .rename(columns={'mean': 'cross_mean', 'std': 'cross_std'})
            .reset_index()
        )
        df = df.merge(cross_stats, on='date', how='left')
        df['signal_descriptor'] = (df['signal_descriptor'] - df['cross_mean']) / df['cross_std']
        # df['signal_descriptor'] = df['signal_descriptor'].replace([np.inf, -np.inf], 0.0).fillna(0.0)
        df = df.drop(columns=['cross_mean', 'cross_std'])

        return df
