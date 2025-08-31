import pandas as pd
from Backtester_Tushar.Feature_Generator.feature_gen import FeatureGenerator
import calendar
import os
import re
import numpy as np

class DataHandler:
    """Handles loading and preprocessing of stock data with multi-timeframe support."""

    def __init__(self, data_dir, start_date="2016-01-01", supported_timeframes=["daily", "hourly", "15min"],
                 external_connectors=None, feature_configs=None, benchmark = None):
        self.data_dir = data_dir
        self.start_date = pd.to_datetime(start_date)
        self.supported_timeframes = supported_timeframes
        self.data = {}
        self.feature_generator = FeatureGenerator(feature_configs, benchmark)
        self.external_connectors = external_connectors or []

    def save_absolute_bbg_stock_data_as_parquet(self,ticker, save_intermediate_files_path,
                            features= [], date_columnn_name = "Datetime"):
        """
        :param columns_required:
        :param ticker:
        :param date_columnn_name:
        :return:
        """
        try:
            # file_path = os.path.join(self.data_dir, f"{ticker}.csv")
            # df = pd.read_csv(file_path)
            # df["Ticker"] = ticker
            columns_required = ['Dates', 'PX_OPEN', 'PX_HIGH', 'PX_LOW', 'PX_CLOSE_1D', 'PX_VOLUME']
            df = pd.read_excel(self.data_dir, sheet_name=ticker)[columns_required]
            df = df.rename(columns={"Dates": "Datetime", "PX_OPEN": "Open", "PX_HIGH": "High",
                                    "PX_LOW": "Low", "PX_CLOSE_1D": "Close", "PX_VOLUME": "Volume"})

            df = self.feature_generator.price_action_transformations(df,
                                                                     start_date = self.start_date,
                                                                     features=features,
                                                                     date_columnn_name=date_columnn_name
                                                                     )
            df = self.feature_generator.compute_features(df)
            df.to_parquet(save_intermediate_files_path + f"/{ticker}.parquet", index=False, compression="gzip")

            return df

        except FileNotFoundError:
            print(f"Data file for {ticker} not found.")
            return None

    def save_relative_bbg_stock_data_as_parquet(self, df_all,
                                                mapping_file,
                                                ticker_column_name = "Ticker",
                                                datetime_column_name = "Datetime",
                                                sector_column_name = "Sector",
                                                returns_column_name = "1D_Close_pct_change"
                                                ):
        """
        :param columns_required:
        :param ticker:
        :param date_columnn_name:
        :return:
        """
        df = self.feature_generator.compute_sector_spreads(df_all,mapping_file,
                                                           ticker_column_name,
                                                           datetime_column_name,
                                                           sector_column_name,
                                                           returns_column_name)
        # df = self.feature_generator.compute_cross_sectional_features(df)
        return df

    def cross_sectional_features(self, df):
        df = self.feature_generator.compute_cross_sectional_features(df)
        return df


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