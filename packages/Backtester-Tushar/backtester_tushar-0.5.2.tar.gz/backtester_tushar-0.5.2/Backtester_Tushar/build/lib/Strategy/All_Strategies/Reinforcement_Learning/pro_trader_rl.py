from Backtester_Tushar.Data.handler import DataHandler
from Backtester_Tushar.Strategy.All_Strategies.Reinforcement_Learning.ql_strategy_with_ppo_dqn import QLStrategy
from Backtester_Tushar.Portfolio_Management_and_Tracker.portfolio_management import Portfolio
from Backtester_Tushar.Sizing.atr_based_sizing import ATRPositionSizer
from Backtester_Tushar.Execution.execution_model import ExecutionModel
from Backtester_Tushar.Execution.t_cost import TransactionCostModel
from Backtester_Tushar.Portfolio_Management_and_Tracker.tracker import PerformanceTracker

# Configuration for features (aligned with paper's ATR and RSI)
feature_configs = [
    {"name": "RSI", "params": {"period": 14}},
    {"name": "Bollinger_Bands", "params": {"period": 20}},
    {"name": "Momentum", "params": {"period": 10}},
]


def run_backtest(tickers,data_dir=r"C:\D_Drive\Algo\data_files\Zerodha\One_day", initial_capital=1000000):

    # Initialize DataHandler with external connectors
    data_handler = DataHandler(
        data_dir=data_dir,
        start_date='2010-01-01',
        supported_timeframes=['daily'],
        feature_configs=feature_configs
    )

    # Initialize other components
    position_sizer = ATRPositionSizer(risk_per_trade=0.01)
    execution_model = ExecutionModel(execution_type='market', slippage_pct=0.002)
    transaction_cost_model = TransactionCostModel(model_type='percentage', base_cost=0.001)
    performance_tracker = PerformanceTracker(risk_free_rate=0.03)

    # Backtest across tickers and market periods
    all_results = {}
    total_capital = initial_capital
    capital_per_ticker = total_capital / len(tickers) if tickers else total_capital

    for ticker in tickers:
        print(f"\nProcessing ticker: {ticker}")
        strategy = QLStrategy(
            timeframe='daily',
            atr_period=14,
            state_size=10,
            action_space=[0, 1, -1],  # Hold, Buy, Sell
            rl_algorithm='dqn',
            learning_rate=0.001,
            discount_factor=0.95,
            max_steps=100,
            hidden_size=64,
            replay_buffer_size=10000,
            batch_size=64,
            target_update_freq=100,
            feature_configs=feature_configs,
            base_risk=150000,
            atr_threshold=5
        )

        results = {}

        # Load and preprocess data
        df = data_handler.load_stock_data(ticker)
        if df is None:
            print(f"No data for {ticker} in market.")
            continue

        # Ensure required columns are present
        required_cols = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_cols):
            print(f"Missing required columns in {ticker} data.")
            continue

        # Train RL model with all available features
        strategy.train_model(df)

        # Generate signals
        df = strategy.generate_signals(df)

        # Initialize portfolio for this ticker
        portfolio = Portfolio(
            initial_capital=capital_per_ticker,
            transaction_cost_model=transaction_cost_model,
            execution_model=execution_model,
            position_sizer=position_sizer,
            max_stocks=5,
            max_capital_deployed=0.9 * capital_per_ticker
        )

        # Manage positions
        df = portfolio.manage_positions(df, ticker, strategy.name, 'daily', strategy)

        # Update performance metrics
        performance_tracker.capital = capital_per_ticker
        performance_tracker.update_metrics(ticker, strategy.name, 'daily', df)
        performance_tracker.aggregate_metrics()

        # Store results
        results["all"] = {
            'df': df,
            'metrics': performance_tracker.get_metrics(level='portfolio')
        }

        # Print key metrics
        metrics = results["all"]['metrics']
        if not metrics.empty:
            print(f"Results for {ticker} in market:")
            print(f"Annualized Return: {metrics['Annualized_Returns'].iloc[-1]:.2f}%")
            print(f"Max Drawdown: {metrics['Max_Drawdown'].iloc[-1]:.2f}")
            print(f"Sharpe Ratio: {metrics['Sharpe_Ratio'].iloc[-1]:.2f}")

        all_results[ticker] = results
        performance_tracker.aggregate_portfolio()

    # Plot overall portfolio performance
    performance_tracker.plot_performance(level='portfolio')

    # Save results to CSV
    for ticker, ticker_results in all_results.items():
        for market, result in ticker_results.items():
            result['df'].to_csv(f'results_{ticker}_{market}.csv', index=False)
            result['metrics'].to_csv(f'metrics_{ticker}_{market}.csv', index=False)

    # Save overall portfolio metrics
    portfolio_metrics = performance_tracker.get_metrics(level='portfolio')
    if not portfolio_metrics.empty:
        portfolio_metrics.to_csv('portfolio_metrics.csv', index=False)

    return all_results


if __name__ == '__main__':
    tickers = ['HDFCBANK', 'IOC', 'SHREECEM', 'TATAMOTORS', 'ADANIPORTS', 'ULTRACEMCO', 'BHARTIARTL',
               'HEROMOTOCO', 'HINDUNILVR', 'GRASIM', 'TATASTEEL', 'UPL', 'AXISBANK', 'BSE', 'LT', 'POWERGRID',
               'SBIN', 'WIPRO', 'INDUSINDBK', 'INFY', 'ONGC', 'BAJAJFINSV', 'CIPLA', 'KOTAKBANK', 'MARUTI',
               'TCS', 'TITAN', 'BPCL', 'BRITANNIA', 'EICHERMOT', 'ICICIBANK', 'RELIANCE', 'ASIANPAINT',
               'BAJAJ-AUTO', 'NESTLEIND', 'BAJFINANCE', 'COALINDIA', 'HCLTECH', 'HDFCLIFE', 'HINDALCO',
               'DRREDDY', 'GAIL', 'DIVISLAB', 'NTPC', 'TECHM', 'ITC', 'JSWSTEEL', 'M&M', 'SBILIFE', 'SUNPHARMA', 'HDFC'
                                                                                                                 'NIFTY 50',
               'BANK NIFTY']
    results = run_backtest(tickers=tickers, data_dir=r"C:\D_Drive\Algo\data_files\Zerodha\One_day",
                           initial_capital=1000000)