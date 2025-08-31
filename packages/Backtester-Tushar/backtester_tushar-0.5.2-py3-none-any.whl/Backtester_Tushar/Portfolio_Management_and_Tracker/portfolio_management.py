from Backtester_Tushar.Execution.execution_model import ExecutionModel
from Backtester_Tushar.Execution.t_cost import TransactionCostModel
from Backtester_Tushar.Sizing.atr_based_sizing import ATRPositionSizer
import pandas as pd
import numpy as np

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
        trail_sl = df["Stoploss_inter"].copy()
        inter_signal = df["Inter_Signal"]
        close = df["Close"]
        atr = df["Entry_ATR"]

        buy_trail = close - atr
        sell_trail = close + atr

        trail_sl[(inter_signal == 1) & trail_sl.isna()] = buy_trail
        trail_sl[(inter_signal == -1) & trail_sl.isna()] = sell_trail

        trail_sl = trail_sl.ffill()

        # df = df.reset_index()
        # trail_sl = np.full(len(df), np.nan)
        # for i in range(1, len(df)):
        #     if pd.isna(df["Stoploss_inter"].iloc[i]):
        #         if df["Duration"].iloc[i] > 0:
        #             prev_close = df["Close"].iloc[i - 1]
        #             prev_atr = df["Entry_ATR"].iloc[i - 1]
        #             inter_signal = df["Inter_Signal"].iloc[i - 1]
        #             potential_sl = prev_close - 1 * prev_atr if inter_signal == 1 else prev_close + 1 * prev_atr if inter_signal == -1 else np.nan
        #             if inter_signal == 1:
        #                 trail_sl[i] = max(trail_sl[i - 1], potential_sl) if not pd.isna(
        #                     trail_sl[i - 1]) else potential_sl
        #             elif inter_signal == -1:
        #                 trail_sl[i] = min(trail_sl[i - 1], potential_sl) if not pd.isna(
        #                     trail_sl[i - 1]) else potential_sl
        #         else:
        #             trail_sl[i] = trail_sl[i - 1]
        #     else:
        #         trail_sl[i] = df["Stoploss_inter"].iloc[i]
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
