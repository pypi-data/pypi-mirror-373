import pandas as pd
import os

def _aggregate_parquet(parquet_dir, ticker_column_name, datetime_column_name):
    all_dfs = []
    for file in os.listdir(parquet_dir):
        if file.endswith(".parquet"):
            ticker = os.path.splitext(file)[0]
            df = pd.read_parquet(os.path.join(parquet_dir, file))
            df["Ticker"] = ticker
            all_dfs.append(df)

    if not all_dfs:
        raise ValueError("No parquet files found in directory.")

    df_all = pd.concat(all_dfs, ignore_index=True)
    df_all[datetime_column_name] = pd.to_datetime(df_all[datetime_column_name])
    # df_all = df_all.set_index([ticker_column_name, datetime_column_name]).sort_index()
    return df_all