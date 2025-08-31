import numpy as np
import pandas as pd


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

