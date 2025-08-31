import numpy as np
import pandas as pd


class DataConnector:
    """Fetches and aligns external data sources, including fundamentals and alternative data."""

    def __init__(self, source_type="csv", source_path=None, **kwargs):
        """
        source_type: Type of file where data is stored. It is only csv for now. Parquet can be added later
        source_path: file location where csv is stored. eg "home/desktop". rest will be added as per ticker
        in fetch data method
        **kwargs: includes ["price_action_path", "event_based_path", "sentiment_path",
        "fundamentals_path", "alternative_path", "macro_path"] as keys with the location sent by
        the user as the value
        """
        self.source_type = source_type
        self.source_path = source_path
        for key, value in kwargs.items():
            setattr(self, key, value)

    def fetch_data(self, ticker, start_date, end_date):
        """
        Fetch data based on type (price_action, event_based, sentiment, fundamentals, alternate, macro).
        ticker: Ticker of the security
        start_date: Date from which data is required
        end_date: Date till which data is required
        data_type = ["price_action", "event_based", "sentiment",
        "fundamentals", "alternative", "macro"]: Type of data that has to be provided
        """
        if self.source_type == "csv":
            try:
                key_value_pair_of_instance_variables = vars(self)
                data_type_and_df_dict = {}
                for key, value in key_value_pair_of_instance_variables.items():
                    if "path" not in key:
                        continue
                    else:
                        df = pd.read_csv(self.source_path + f"/{ticker}.csv")
                        df["Datetime"] = pd.to_datetime(df["Datetime"]).dt.tz_localize(None)

                        df = df[(df["Datetime"] >= pd.to_datetime(start_date)) &
                                (df["Datetime"] <= pd.to_datetime(end_date))]
                        data_type_and_df_dict[key.replace("_path", "")] = df
                return data_type_and_df_dict
            except FileNotFoundError:
                print(f"Data file for not found for {ticker}.")
                return None
        return None

    def align_data(self, base_df, external_df, column_name):
        """Align external data with base DataFrame."""
        if external_df is None:
            return base_df
        return base_df.merge(external_df[["Datetime", column_name]], on="Datetime", how="left")