import pandas as pd
from Backtester_Tushar.Feature_Generator.feature_gen import FeatureGenerator
import calendar
import os


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