from Backtester_Tushar.Strategy.base_class import Strategy
import numpy as np
from abc import abstractmethod
import pandas as pd

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

    @abstractmethod
    def train_model_multi_ticker(self, df):
        """
        Train model on master DataFrame containing multiple tickers.
        Default implementation - can be overridden for more sophisticated training.
        """
        pass

    def predict_multi_ticker(self, df):
        """
        Generate predictions for master DataFrame containing multiple tickers.

        Args:
            df: Master DataFrame with 'ticker' column and features

        Returns:
            Series of predictions aligned with input DataFrame
        """
        if 'ticker' not in df.columns:
            raise ValueError("DataFrame must contain 'ticker' column for multi-ticker processing")

        predictions = []

        # Group by ticker and predict for each group
        for ticker, group_df in df.groupby('ticker'):
            try:
                ticker_predictions = self.predict(group_df.copy())
                predictions.append(ticker_predictions)
            except Exception as e:
                print(f"Error predicting for ticker {ticker}: {str(e)}")
                # Return zeros for failed predictions
                predictions.append(pd.Series(np.zeros(len(group_df)), index=group_df.index))
                continue

        # Concatenate all predictions
        final_predictions = pd.concat(predictions)

        # Align with original DataFrame index
        return final_predictions.reindex(df.index).fillna(0)

    def risk_allocation(self, row):
        return self.base_risk_allocation(row)

    def generate_signals(self, df):
        """Generate signals for single ticker DataFrame."""
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
        df["Long_Signal"] = predictions.apply(lambda x: 1 if x == 1 else 0)  # Fixed: was -1
        df["Short_Signal"] = predictions.apply(lambda x: 1 if x == -1 else 0)
        df["Signal"] = df["Long_Signal"] - df["Short_Signal"]  # Long=1, Short=-1
        return df

    def generate_signals_multi_ticker(self, df):
        """
        Generate signals for master DataFrame containing multiple tickers.
        Optimized version that computes features once and predicts in batch.

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
                # Copy and compute features for this ticker
                ticker_df = group_df.copy()
                ticker_df = self.feature_generator.compute_features(ticker_df)
                ticker_df["ATR"] = self.atr(ticker_df["High"], ticker_df["Low"], ticker_df["Close"])
                ticker_df["ATR"] = ticker_df["ATR"].bfill().ffill()
                ticker_df["ATR_percent"] = ticker_df["ATR"] * 100 / ticker_df["Close"]
                ticker_df["Returns"] = np.log(ticker_df["Close"] / ticker_df["Close"].shift(1)).fillna(0)

                for window in [1, 10, 22, 66, 132, 252]:
                    ticker_df[f"{window}_Volatility"] = ticker_df["Returns"].rolling(window=window).std() * np.sqrt(
                        window)
                    ticker_df[f"{window}_Returns"] = ticker_df["Close"].pct_change(periods=window).mul(100)

                # Generate predictions for this ticker
                predictions = self.predict(ticker_df)
                ticker_df["Entry_Signal"] = predictions.apply(lambda x: 1 if x == 1 else 0)
                ticker_df["Long_Signal"] = predictions.apply(lambda x: 1 if x == 1 else 0)
                ticker_df["Short_Signal"] = predictions.apply(lambda x: 1 if x == -1 else 0)
                ticker_df["Signal"] = ticker_df["Long_Signal"] - ticker_df["Short_Signal"]

                # Ensure ticker column is preserved
                ticker_df['ticker'] = ticker

                results.append(ticker_df)

            except Exception as e:
                print(f"Error processing ticker {ticker}: {str(e)}")
                continue

        if not results:
            raise ValueError("No tickers were successfully processed")

        # Concatenate all results
        final_df = pd.concat(results, ignore_index=True)

        # Restore original order if possible
        date_cols = [col for col in df.columns if
                     'date' in col.lower() or df[col].dtype in ['datetime64[ns]', 'object']]
        if date_cols and 'ticker' in final_df.columns:
            try:
                final_df = final_df.sort_values(['ticker', date_cols[0]]).reset_index(drop=True)
            except:
                pass

        return final_df
