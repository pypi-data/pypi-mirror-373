import pandas as pd
import numpy as np
from numba import njit, prange
from numba.cuda.simulator.cudadrv.nvvm import set_cuda_kernel
from scipy import stats, optimize, linalg
from scipy.stats import norm
from sklearn.decomposition import PCA
from sklearn.covariance import LedoitWolf
import warnings
from collections import defaultdict, deque
import logging
from scipy.optimize import minimize

from Backtester_Tushar.Risk.risk_limits import RiskLimits
from Backtester_Tushar.Portfolio_Management_and_Tracker.utils import *
from Backtester_Tushar.Strategy.signal_processing import SignalProcessor
from Backtester_Tushar.Execution.t_cost import MarketImpactModel
from Backtester_Tushar.Risk.risk_manager import RiskManager
from Backtester_Tushar.Portfolio_Management_and_Tracker.analyzer import PerformanceAnalyzer
from Backtester_Tushar.Sizing.portfolio_weights import *


class PortfolioManager:

    def __init__(self,
                 initial_capital=10000000,
                 n_long_positions=20,
                 k_short_positions=20,
                 long_capital_pct=0.6,
                 short_capital_pct=0.4,
                 rebalance_frequency=1,
                 risk_limits=None,
                 deployable_capital_pct=1.0,
                 transaction_cost_bps=5.0,
                 slippage_factor=0.1):

        # Core parameters
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.n_long_positions = n_long_positions
        self.k_short_positions = k_short_positions
        self.long_capital_pct = long_capital_pct
        self.short_capital_pct = short_capital_pct
        self.rebalance_frequency = rebalance_frequency
        self.risk_limits = risk_limits or RiskLimits()

        # Initialize components
        self.risk_manager = RiskManager(self.risk_limits)
        self.signal_processor = SignalProcessor()
        self.market_impact_model = MarketImpactModel()
        self.performance_analyzer = PerformanceAnalyzer()

        self.deployable_capital_pct = deployable_capital_pct

        # Store dynamic allocation parameters
        self.current_long_pct = long_capital_pct
        self.current_short_pct = short_capital_pct
        self.current_deployable_pct = deployable_capital_pct

        # Update risk limits to enforce no leverage
        self.risk_limits.max_leverage = 1.0

        # Initialize tracking variables
        self.positions = {}
        self.trade_log = {}
        self.performance_log = []
        self.risk_log = []
        self.returns_covariance = None
        self.ticker_order = []
        self.betas = {}
        self.historical_returns = []
        self.portfolio_values = []
        self.returns = []
        self.peak_value = initial_capital
        self.current_drawdown = 0.0

        # Fixed transaction costs and slippage
        self.transaction_cost_bps = transaction_cost_bps / 10000
        self.slippage_factor = slippage_factor


        self.trade_date = []
        self.shares_daily = []
        self.mtm_daily =[]
        self.pnl_daily = []
        self.day_start_exposure = []
        self.ticker_daily = []
        self.gross_exposure = []
        self.agg_pnl =[]
        self.net_exposure = []
        self.long_pnl = []
        self.short_pnl = []
        self.problem_rebal = []
        self.trade_date_agg= []

        self.trade_id = 1
        self.last_rebalance_date = None

    def update_allocation_params(self, date):
        pass

    def _should_rebalance(self, current_date):
        """Determine if rebalancing is needed"""
        if self.last_rebalance_date is None:
            return True

        days_since_rebalance = (pd.to_datetime(current_date) - pd.to_datetime(self.last_rebalance_date)).days

        if days_since_rebalance >= self.rebalance_frequency:
            return True

        # Emergency rebalancing
        if self.current_drawdown > self.risk_limits.max_drawdown * 0.8:
            self.logger.warning("Emergency rebalancing triggered")
            return True

        return False

    def execute_smart_rebalancing(self, long_portfolio, short_portfolio,
                                  next_day_data, next_day_date):
        daily_gross_exposure = 0
        daily_net_exposure = 0
        daily_pnl = 0
        long_pnl = 0
        short_pnl = 0
        for key, value in long_portfolio.items():  # portfolio for next day data
            try:
                next_day_ticker_data = next_day_data[next_day_data["ticker"] == key]
                ticker_capital = self.long_capital_today * value
                shares_traded = ticker_capital / next_day_ticker_data["Open"].values[0]
                self.trade_date.append(next_day_ticker_data["date"].values[0])
                self.shares_daily.append(shares_traded)
                self.mtm_daily.append(shares_traded * next_day_ticker_data["Close"].values[0])
                self.pnl_daily.append(shares_traded * (next_day_ticker_data["Close"].values[0] -
                                            next_day_ticker_data["Open"].values[0]))
                self.day_start_exposure.append(shares_traded * (next_day_ticker_data["Open"].values[0]))
                self.ticker_daily.append(key)
                daily_gross_exposure += abs(shares_traded * next_day_ticker_data["Open"].values[0])
                daily_net_exposure += shares_traded * next_day_ticker_data["Open"].values[0]
                daily_pnl += shares_traded * (next_day_ticker_data["Close"].values[0] -
                                              next_day_ticker_data["Open"].values[0])
                long_pnl += shares_traded * (next_day_ticker_data["Close"].values[0] -
                                             next_day_ticker_data["Open"].values[0])
            except Exception as e:
                print(next_day_date, key, e)
                self.problem_rebal.append((next_day_date, key, e))


        for key, value in short_portfolio.items():  # portfolio for next day data
            try:
                next_day_ticker_data = next_day_data[next_day_data["ticker"] == key]
                ticker_capital = self.short_capital_today * value
                shares_traded = -ticker_capital / next_day_ticker_data["Open"].values[0]
                self.trade_date.append(next_day_ticker_data["date"].values[0])
                self.shares_daily.append(shares_traded)
                self.mtm_daily.append(shares_traded * next_day_ticker_data["Close"].values[0])
                self.pnl_daily.append(shares_traded * (next_day_ticker_data["Close"].values[0] -
                                            next_day_ticker_data["Open"].values[0]))
                self.day_start_exposure.append(shares_traded * (next_day_ticker_data["Open"].values[0]))
                self.ticker_daily.append(key)

                daily_gross_exposure += abs(shares_traded * next_day_ticker_data["Open"].values[0])
                daily_net_exposure += shares_traded * next_day_ticker_data["Open"].values[0]
                daily_pnl += shares_traded * (next_day_ticker_data["Close"].values[0] -
                                              next_day_ticker_data["Open"].values[0])
                short_pnl += shares_traded * (next_day_ticker_data["Close"].values[0] -
                                              next_day_ticker_data["Open"].values[0])
            except Exception as e:
                print(next_day_date, key, e)
                self.problem_rebal.append((next_day_date, key, e))

        self.trade_date_agg.append(next_day_date)
        self.gross_exposure.append(daily_gross_exposure)
        self.net_exposure.append(daily_net_exposure)
        self.agg_pnl.append(daily_pnl)
        self.long_pnl.append(long_pnl)
        self.short_pnl.append(short_pnl)

        self.current_capital += daily_pnl

    # def execute_smart_closing_next_day_rebalancing(self, long_portfolio, short_portfolio,
    #                               next_day_data, next_day_date, next_next_day_date):
    #     daily_gross_exposure = 0
    #     daily_net_exposure = 0
    #     daily_pnl = 0
    #     long_pnl = 0
    #     short_pnl = 0
    #     self.trade_date = []
    #     self.shares_daily = []
    #     self.mtm_daily =[]
    #     self.pnl_daily = []
    #     self.day_start_exposure = []
    #     self.ticker_daily = []
    #     for key, value in long_portfolio.items():  # portfolio for next day data
    #         next_day_ticker_data = next_day_data[next_day_data["ticker"] == key]
    #         ticker_capital = self.long_capital_today * value
    #         # shares_traded = ticker_capital / next_day_ticker_data["Open"].values[0]
    #         # # self.positions[str(next_day_date)] = {key:
    #         # #     {
    #         # #     "Trade_date": next_day_ticker_data["date"].values[0],
    #         # #     "Shares_bought": shares_traded,
    #         # #     "MTM": shares_traded * next_next_day_date["Open"].values[0],
    #         # #     "P&L": shares_traded * (next_next_day_date["Open"].values[0] -
    #         # #                             next_day_ticker_data["Open"].values[0]),
    #         # #     "Start_of_day_exposure": shares_traded * (next_day_ticker_data["Open"].values[0]),
    #         # #     }
    #         # # }
    #         self.trade_date.append(next_day_ticker_data["date"].values[0])
    #         self.shares_daily.append(shares_traded)
    #         self.mtm_daily.append(shares_traded * next_next_day_date["Open"].values[0])
    #
    #         daily_gross_exposure += abs(shares_traded * next_day_ticker_data["Open"].values[0])
    #         daily_net_exposure += shares_traded * next_day_ticker_data["Open"].values[0]
    #         daily_pnl += shares_traded * (next_next_day_date["Open"].values[0] -
    #                                       next_day_ticker_data["Open"].values[0])
    #         long_pnl += shares_traded * (next_next_day_date["Open"].values[0] -
    #                                      next_day_ticker_data["Open"].values[0])
    #
    #     for key, value in short_portfolio.items():  # portfolio for next day data
    #         next_day_ticker_data = next_day_data[next_day_data["ticker"] == key]
    #         ticker_capital = self.short_capital_today * value
    #         shares_traded = -ticker_capital / next_day_ticker_data["Open"].values[0]
    #
    #         self.positions[str(next_day_date)] = { key :
    #                                                    {
    #             "Trade_date": next_day_ticker_data["date"].values[0],
    #             "Shares_bought": shares_traded,
    #             "MTM": shares_traded * next_next_day_date["Open"].values[0],
    #             "P&L": shares_traded * (next_next_day_date["Open"].values[0] -
    #                                     next_day_ticker_data["Open"].values[0]),
    #             "Start_of_day_exposure": shares_traded * next_day_ticker_data["Open"].values[0],
    #                                                    }
    #         }
    #         daily_gross_exposure += abs(shares_traded * next_day_ticker_data["Open"].values[0])
    #         daily_net_exposure += shares_traded * next_day_ticker_data["Open"].values[0]
    #         daily_pnl += shares_traded * (next_next_day_date["Open"].values[0] -
    #                                       next_day_ticker_data["Open"].values[0])
    #         short_pnl += shares_traded * (next_next_day_date["Open"].values[0] -
    #                                       next_day_ticker_data["Open"].values[0])
    #     self.trade_log[str(next_day_date)] = {"Gross exposure": daily_gross_exposure,
    #                                      "Net exposure start of day": daily_net_exposure,
    #                                      "P&L": daily_pnl,
    #                                      "Long P&L": long_pnl,
    #                                      "Short P&L": short_pnl}
    #     self.current_capital += self.current_capital + daily_pnl

    def make_results(self):
        all_trades = pd.DataFrame(columns=["Trade_Date", "Ticker", "Shares_Traded", "Exposure_at_Open",
                                           "MTM", "PnL"])
        all_trades["Trade_Date"] = self.trade_date
        all_trades["Ticker"] = self.ticker_daily
        all_trades["Shares_Traded"] = self.shares_daily
        all_trades["Exposure_at_Open"] = self.day_start_exposure
        all_trades["MTM"] = self.mtm_daily
        all_trades["PnL"] = self .pnl_daily

        daily_logs = pd.DataFrame(columns=["Trade_Date", "Gross_Exposure", "Net_Exposure", "PnL",
                                           "Long_PnL", "Short_PnL"])
        daily_logs["Trade_Date"] = self.trade_date_agg
        daily_logs["Gross_Exposure"] = self.gross_exposure
        daily_logs["Net_Exposure"] = self.net_exposure
        daily_logs["PnL"] = self.agg_pnl
        daily_logs["Long_PnL"] = self.long_pnl
        daily_logs["Short_PnL"] = self .short_pnl
        return all_trades, daily_logs



    def run_institutional_backtest(self, master_df, allocation_schedule=None):
        """Run comprehensive institutional-grade backtest
        update allocation can be update daily
        """
        print("=" * 60)
        print("STARTING INSTITUTIONAL PORTFOLIO BACKTEST")
        print("=" * 60)
        print(f"Initial capital: ${self.initial_capital:,.2f}")
        print(f"Initial allocation - Long: {self.current_long_pct:.1%}, Short: {self.current_short_pct:.1%}")

        # Backtest execution
        unique_dates = sorted(master_df['date'].unique())
        results = 0
        allocation_changes = 0

        print(f"Processing {len(unique_dates)} trading days...")

        for i, current_date in enumerate(unique_dates):
                # Check for allocation parameter updates
            if allocation_schedule is not None:
                self.update_allocation_params(current_date)

            self.capital_deployable_today = self.deployable_capital_pct * self.current_capital
            self.long_capital_today = self.long_capital_pct * self.capital_deployable_today
            self.short_capital_today = self.short_capital_pct * self.capital_deployable_today
            # Get current day data (signal day)
            df_day = master_df[master_df['date'] == current_date].copy()

            # Get next day data for execution
            if (i == len(unique_dates) - 2) or (i == len(unique_dates) - 1):
                continue
            next_day_data = master_df[master_df['date'] == unique_dates[i + 1]]

            should_rebalance = self._should_rebalance(current_date)

            # Execute rebalancing
            if should_rebalance and len(df_day) > 0 and next_day_data is not None:
                long_portfolio, short_portfolio = select_optimal_portfolio(df_day, self.n_long_positions,
                                                                           self.k_short_positions,
                                                                           )
                self.execute_smart_rebalancing(
                    long_portfolio, short_portfolio, next_day_data, unique_dates[i + 1]
                )
                print("Current Capital: ", self.current_capital)
                # print(self.positions)
                # self.execute_smart_closing_next_day_rebalancing(
                #     long_portfolio, short_portfolio, next_day_data, unique_dates[i + 1],
                #     master_df[master_df['date'] == unique_dates[i + 2]]
                # )
                # results += self.trade_log[str(unique_dates[i + 1])].get("P&L")
                # print(current_date, self.agg_pnl / self.current_capital )
                self.last_rebalance_date = current_date

        trade_log, daily_logs = self.make_results()
        print(self.problem_rebal)
        trade_log.to_csv("Trade_logs.csv", index=False)
        daily_logs.to_csv("Daily_logs.csv", index = False)





