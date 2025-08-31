import pandas as pd
from backtesting_framework import (DataHandler, GapStrategy, MACDStrategy, EnsembleStrategy,
                                 Portfolio, PerformanceTracker, MarketRegimeWeights,
                                 ATRPositionSizer, TransactionCostModel, ExecutionModel)

# 1. Set up the DataHandler
data_dir = "./stock_data"  # Directory containing CSV files with OHLCV data
feature_configs = [
    {"name": "RSI", "params": {"period": 14}},
    {"name": "Bollinger_Bands", "params": {"period": 20}},
    {"name": "Momentum", "params": {"period": 10}}
]
data_handler = DataHandler(data_dir=data_dir, feature_configs=feature_configs)

# 2. Define strategies
gap_strategy = GapStrategy(timeframe="daily", atr_period=14, feature_configs=feature_configs)
macd_strategy = MACDStrategy(timeframe="daily", atr_period=14, feature_configs=feature_configs)

# 3. Create an ensemble strategy with MarketRegimeWeights
strategies = [gap_strategy, macd_strategy]
weights = MarketRegimeWeights(volatility_window=20, momentum_window=20)
ensemble_strategy = EnsembleStrategy(
    strategies=strategies,
    weights=weights,
    timeframe="daily",
    feature_configs=feature_configs
)

# 4. Set up the Portfolio_Management_and_Tracker
initial_capital = 10000000
portfolio = Portfolio(
    initial_capital=initial_capital,
    position_sizer=ATRPositionSizer(risk_per_trade=0.01),
    transaction_cost_model=TransactionCostModel(model_type="percentage", base_cost=0.001),
    execution_model=ExecutionModel(execution_type="market", slippage_pct=0.002)
)

# 5. Initialize PerformanceTracker
performance_tracker = PerformanceTracker(risk_free_rate=0.07)
performance_tracker.capital = initial_capital

# 6. Run backtest for multiple tickers
tickers = ["AAPL", "MSFT"]
for ticker in tickers:
    # Load and prepare data
    df = data_handler.get_data(ticker, timeframe="daily")
    if df is None:
        print(f"Skipping {ticker} due to missing data")
        continue

    # Generate signals and manage positions for the ensemble strategy
    df_signals = ensemble_strategy.generate_signals(df)
    df_positions = portfolio.manage_positions(
        df_signals, ticker, "EnsembleStrategy", "daily", ensemble_strategy
    )

    # Update performance metrics
    performance_tracker.update_metrics(ticker, "EnsembleStrategy", "daily", df_positions)

# 7. Aggregate metrics across strategies and portfolio
performance_tracker.aggregate_metrics()
performance_tracker.aggregate_portfolio(strategy_weights=weights.get_weights(strategies, performance_tracker.trade_summary, df))

# 8. Display results
print("\nTrade Summary:")
print(performance_tracker.trade_summary[["Ticker", "Strategy", "Timeframe", "Number_of_Trades",
                                        "Sharpe_Ratio", "Max_Drawdown", "Cumulative_Returns"]])

print("\nAggregated Metrics:")
print(performance_tracker.aggregated_metrics[["Strategy", "Total_Trades", "Sharpe_Ratio",
                                             "Max_Drawdown", "Cumulative_Returns"]])

print("\nPortfolio_Management_and_Tracker Metrics:")
print(performance_tracker.portfolio_metrics[["Portfolio_Management_and_Tracker", "Total_Trades", "Sharpe_Ratio",
                                            "Max_Drawdown", "Cumulative_Returns"]])

# 9. Access portfolio-level trade data
portfolio_data = performance_tracker.trade_data[("Combined", "Portfolio_Management_and_Tracker", "All")]
print("\nPortfolio_Management_and_Tracker Equity Curve Tail:")
print(portfolio_data["equity_curve"].tail())

def run_backtest(strategies, tickers, data_handler, portfolio, tracker, timeframe="daily", parallel=False):
    # Preload data for all tickers
    print("Loading data...")
    data_dict = {ticker: data_handler.get_data(ticker, timeframe) for ticker in tickers}

    for strategy in strategies:
        print(f"\nRunning strategy: {strategy.name}")

        if hasattr(strategy, "train_model"):
            # For ML strategies, train once per ticker
            for ticker in tickers:
                df = data_dict[ticker]
                if df is not None:
                    print(f"Training model for {ticker}")
                    strategy.train_model(df)

        for ticker in tickers:
            df = data_dict[ticker]
            if df is None or df.empty:
                continue

            print(f"Generating signals for {ticker} using {strategy.name}")
            df_signals = strategy.generate_signals(df)

            print(f"Managing positions for {ticker}")
            df_trades = portfolio.manage_positions(df_signals, ticker, strategy.name, timeframe, strategy)

            print(f"Updating performance for {ticker}")
            tracker.update_metrics(ticker, strategy.name, timeframe, df_trades)

    tracker.aggregate_metrics()
    print("\n Backtest Complete.")

from joblib import Parallel, delayed

def run_parallel_backtest(strategies, tickers, data_handler, portfolio, tracker, timeframe="daily"):
    def run_one(strategy, ticker):
        df = data_handler.get_data(ticker, timeframe)
        if hasattr(strategy, "train_model"):
            strategy.train_model(df)
        df_signals = strategy.generate_signals(df)
        df_trades = portfolio.manage_positions(df_signals, ticker, strategy.name, timeframe, strategy)
        tracker.update_metrics(ticker, strategy.name, timeframe, df_trades)

    for strategy in strategies:
        Parallel(n_jobs=-1)(delayed(run_one)(strategy, ticker) for ticker in tickers)
    tracker.aggregate_metrics()

