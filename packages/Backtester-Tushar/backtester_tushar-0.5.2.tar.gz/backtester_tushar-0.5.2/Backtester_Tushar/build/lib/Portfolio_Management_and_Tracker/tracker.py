import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class PerformanceTracker:
    """Tracks and computes trade performance metrics."""

    def __init__(self, risk_free_rate=0.03):
        self.risk_free_rate = risk_free_rate
        self.trade_summary = pd.DataFrame(columns=[
            "Ticker", "Strategy", "Timeframe", "Number_of_Trades", "Average_Returns_from_Winners",
            "Average_Returns_from_Losers", "Average_Trade_Returns",
            "Avg_Holding_Period", "Avg_Holding_Period_from_Winners",
            "Avg_Holding_Period_from_Losers", "Reward_Risk", "Strike_Rate",
            "Expectancy", "Max_Drawdown", "Calmar_Ratio", "Sharpe_Ratio",
            "Sortino_Ratio", "Annualized_Returns", "Cumulative_Returns",
            "VaR_95", "CVaR_95", "Omega_Ratio"
        ])
        self.aggregated_metrics = pd.DataFrame(columns=[
            "Strategy", "Total_Trades", "Total_Return", "Average_Return",
            "Strike_Rate", "Expectancy", "Max_Drawdown", "Calmar_Ratio",
            "Sharpe_Ratio", "Sortino_Ratio", "Annualized_Returns",
            "Cumulative_Returns", "VaR_95", "CVaR_95", "Omega_Ratio"
        ])
        self.portfolio_metrics = pd.DataFrame(columns=[
            "Portfolio_Management_and_Tracker", "Total_Trades", "Total_Return", "Average_Return",
            "Strike_Rate", "Expectancy", "Max_Drawdown", "Calmar_Ratio",
            "Sharpe_Ratio", "Sortino_Ratio", "Annualized_Returns",
            "Cumulative_Returns", "VaR_95", "CVaR_95", "Omega_Ratio"
        ])
        self.trade_data = {}
        self.capital = None

    def calculate_calmar_ratio(self, annualized_return, max_drawdown):
        return annualized_return / abs(max_drawdown) if max_drawdown != 0 else np.inf

    def calculate_sharpe_ratio(self, returns):
        mean_return = returns.mean() * 252
        std_dev = returns.std() * np.sqrt(252)
        return (mean_return - self.risk_free_rate) / std_dev if std_dev != 0 else np.inf

    def calculate_sortino_ratio(self, returns):
        mean_return = returns.mean() * 252
        downside_returns = returns[returns < 0]
        downside_dev = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else np.nan
        return (mean_return - self.risk_free_rate) / downside_dev if downside_dev != 0 else np.inf

    def calculate_var(self, returns, confidence_level=0.95):
        return np.percentile(returns, 100 * (1 - confidence_level))

    def calculate_cvar(self, returns, confidence_level=0.95):
        var = self.calculate_var(returns, confidence_level)
        return returns[returns <= var].mean() if len(returns[returns <= var]) > 0 else np.nan

    def calculate_omega_ratio(self, returns, threshold=0):
        excess_returns = returns - threshold
        positive = excess_returns[excess_returns > 0].sum()
        negative = -excess_returns[excess_returns < 0].sum()
        return positive / negative if negative != 0 else np.inf

    def calculate_annualized_returns(self, cumulative_return, days):
        if days <= 0:
            return np.nan
        years = days / 252
        return ((1 + cumulative_return / 100) ** (1 / years) - 1) * 100 if years > 0 else np.nan

    def update_metrics(self, ticker, strategy_name, timeframe, df):
        trades = df[df["Exit_Signal"] == 1].copy()
        if len(trades) == 0:
            return

        num_trades = len(trades)
        # returns = trades.apply(
        #     lambda x: x["Num_Shares"] * (x["Exit_Price"] - x["Entry_Price"]) if x["Inter_Signal"] == 1 else
        #     x["Num_Shares"] * (-x["Exit_Price"] + x["Entry_Price"]), axis=1
        # )
        entry = trades["Entry_Price"]
        exit = trades["Exit_Price"]
        shares = trades["Num_Shares"]
        side = trades["Inter_Signal"]

        returns = shares * (exit - entry) * side

        winners = returns[returns > 0]
        losers = returns[returns <= 0]
        avg_winner = winners.mean() if len(winners) > 0 else 0
        avg_loser = losers.mean() if len(losers) > 0 else 0
        avg_return = returns.mean() if len(returns) > 0 else 0
        holding_period = trades["Duration"].mean()
        holding_winners = trades[returns > 0]["Duration"].mean() if len(winners) > 0 else 0
        holding_losers = trades[returns <= 0]["Duration"].mean() if len(losers) > 0 else 0
        strike_rate = len(winners) / num_trades if num_trades > 0 else 0
        expectancy = (strike_rate * avg_winner) + ((1 - strike_rate) * avg_loser) if num_trades > 0 else 0
        equity_curve = returns.cumsum()
        max_drawdown = (equity_curve - equity_curve.cummax()).min() if len(equity_curve) > 0 else 0
        reward_risk = avg_winner / abs(avg_loser) if avg_loser != 0 else np.inf
        days = (trades["Datetime"].max() - trades["Datetime"].min()).days
        cumulative_return = equity_curve.iloc[-1] / self.capital * 100 if self.capital else 0
        annualized_return = self.calculate_annualized_returns(cumulative_return, days)
        calmar_ratio = self.calculate_calmar_ratio(annualized_return, max_drawdown)
        sharpe_ratio = self.calculate_sharpe_ratio(returns / self.capital if self.capital else returns)
        sortino_ratio = self.calculate_sortino_ratio(returns / self.capital if self.capital else returns)
        var_95 = self.calculate_var(returns / self.capital if self.capital else returns)
        cvar_95 = self.calculate_cvar(returns / self.capital if self.capital else returns)
        omega_ratio = self.calculate_omega_ratio(returns / self.capital if self.capital else returns)

        self.trade_summary.loc[len(self.trade_summary)] = {
            "Ticker": ticker,
            "Strategy": strategy_name,
            "Timeframe": timeframe,
            "Number_of_Trades": num_trades,
            "Average_Returns_from_Winners": avg_winner,
            "Average_Returns_from_Losers": avg_loser,
            "Average_Trade_Returns": avg_return,
            "Avg_Holding_Period": holding_period,
            "Avg_Holding_Period_from_Winners": holding_winners,
            "Avg_Holding_Period_from_Losers": holding_losers,
            "Reward_Risk": reward_risk,
            "Strike_Rate": strike_rate,
            "Expectancy": expectancy,
            "Max_Drawdown": max_drawdown,
            "Calmar_Ratio": calmar_ratio,
            "Sharpe_Ratio": sharpe_ratio,
            "Sortino_Ratio": sortino_ratio,
            "Annualized_Returns": annualized_return,
            "Cumulative_Returns": cumulative_return,
            "VaR_95": var_95,
            "CVaR_95": cvar_95,
            "Omega_Ratio": omega_ratio
        }

        self.trade_data[(ticker, strategy_name, timeframe)] = {
            "trades": trades,
            "returns": returns,
            "equity_curve": equity_curve,
            "drawdowns": equity_curve - equity_curve.cummax(),
            "df": df
        }


    def aggregate_metrics(self):
        """Aggregate metrics across all strategies."""
        strategies = self.trade_summary["Strategy"].unique()
        self.aggregated_metrics = pd.DataFrame(columns=self.aggregated_metrics.columns)

        for strategy in strategies:
            strategy_data = self.trade_summary[self.trade_summary["Strategy"] == strategy]
            if strategy_data.empty:
                continue

            total_trades = strategy_data["Number_of_Trades"].sum()
            total_return = strategy_data["Cumulative_Returns"].sum()
            avg_return = strategy_data["Average_Trade_Returns"].mean()
            strike_rate = strategy_data["Strike_Rate"].mean()
            expectancy = strategy_data["Expectancy"].mean()
            max_drawdown = strategy_data["Max_Drawdown"].min()

            # Combine returns across all tickers and timeframes for this strategy
            all_returns = []
            for (ticker, strat, timeframe), data in self.trade_data.items():
                if strat == strategy:
                    all_returns.append(data["returns"] / self.capital if self.capital else data["returns"])
            combined_returns = pd.concat(all_returns) if all_returns else pd.Series()

            days = (strategy_data["Datetime"].max() - strategy_data[
                "Datetime"].min()).days if not strategy_data.empty else 0
            cumulative_return = strategy_data["Cumulative_Returns"].sum()
            annualized_return = self.calculate_annualized_returns(cumulative_return, days)
            calmar_ratio = self.calculate_calmar_ratio(annualized_return, max_drawdown)
            sharpe_ratio = self.calculate_sharpe_ratio(combined_returns) if not combined_returns.empty else np.nan
            sortino_ratio = self.calculate_sortino_ratio(combined_returns) if not combined_returns.empty else np.nan
            var_95 = self.calculate_var(combined_returns) if not combined_returns.empty else np.nan
            cvar_95 = self.calculate_cvar(combined_returns) if not combined_returns.empty else np.nan
            omega_ratio = self.calculate_omega_ratio(combined_returns) if not combined_returns.empty else np.nan

            self.aggregated_metrics.loc[len(self.aggregated_metrics)] = {
                "Strategy": strategy,
                "Total_Trades": total_trades,
                "Total_Return": total_return,
                "Average_Return": avg_return,
                "Strike_Rate": strike_rate,
                "Expectancy": expectancy,
                "Max_Drawdown": max_drawdown,
                "Calmar_Ratio": calmar_ratio,
                "Sharpe_Ratio": sharpe_ratio,
                "Sortino_Ratio": sortino_ratio,
                "Annualized_Returns": annualized_return,
                "Cumulative_Returns": cumulative_return,
                "VaR_95": var_95,
                "CVaR_95": cvar_95,
                "Omega_Ratio": omega_ratio
            }

    def aggregate_portfolio(self):
        """Compute portfolio-level metrics across all strategies and tickers."""
        if self.trade_summary.empty:
            return

        total_trades = self.trade_summary["Number_of_Trades"].sum()
        total_return = self.trade_summary["Cumulative_Returns"].sum()
        avg_return = self.trade_summary["Average_Trade_Returns"].mean()
        strike_rate = self.trade_summary["Strike_Rate"].mean()
        expectancy = self.trade_summary["Expectancy"].mean()
        max_drawdown = self.trade_summary["Max_Drawdown"].min()

        # Combine all returns
        all_returns = []
        for _, data in self.trade_data.items():
            all_returns.append(data["returns"] / self.capital if self.capital else data["returns"])
        combined_returns = pd.concat(all_returns) if all_returns else pd.Series()

        days = (self.trade_summary["Datetime"].max() - self.trade_summary[
            "Datetime"].min()).days if not self.trade_summary.empty else 0
        cumulative_return = self.trade_summary["Cumulative_Returns"].sum()
        annualized_return = self.calculate_annualized_returns(cumulative_return, days)
        calmar_ratio = self.calculate_calmar_ratio(annualized_return, max_drawdown)
        sharpe_ratio = self.calculate_sharpe_ratio(combined_returns) if not combined_returns.empty else np.nan
        sortino_ratio = self.calculate_sortino_ratio(combined_returns) if not combined_returns.empty else np.nan
        var_95 = self.calculate_var(combined_returns) if not combined_returns.empty else np.nan
        cvar_95 = self.calculate_cvar(combined_returns) if not combined_returns.empty else np.nan
        omega_ratio = self.calculate_omega_ratio(combined_returns) if not combined_returns.empty else np.nan

        self.portfolio_metrics.loc[len(self.portfolio_metrics)] = {
            "Portfolio_Management_and_Tracker": "All Strategies",
            "Total_Trades": total_trades,
            "Total_Return": total_return,
            "Average_Return": avg_return,
            "Strike_Rate": strike_rate,
            "Expectancy": expectancy,
            "Max_Drawdown": max_drawdown,
            "Calmar_Ratio": calmar_ratio,
            "Sharpe_Ratio": sharpe_ratio,
            "Sortino_Ratio": sortino_ratio,
            "Annualized_Returns": annualized_return,
            "Cumulative_Returns": cumulative_return,
            "VaR_95": var_95,
            "CVaR_95": cvar_95,
            "Omega_Ratio": omega_ratio
        }

    def get_metrics(self, level="strategy"):
        """Return metrics at specified level ('trade', 'strategy', 'portfolio')."""
        if level == "trade":
            return self.trade_summary
        elif level == "strategy":
            return self.aggregated_metrics
        elif level == "portfolio":
            return self.portfolio_metrics
        return None

    def plot_performance(self, level="strategy"):
        """Plot performance metrics using Plotly."""
        metrics = self.get_metrics(level)
        if metrics is None or metrics.empty:
            print("No metrics available to plot.")
            return

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Cumulative Returns", "Max Drawdown", "Sharpe Ratio", "Sortino Ratio"),
            specs=[[{"type": "bar"}, {"type": "bar"}], [{"type": "bar"}, {"type": "bar"}]]
        )

        identifier = "Strategy" if level == "strategy" else "Portfolio_Management_and_Tracker" if level == "portfolio" else "Ticker"
        fig.add_trace(
            go.Bar(x=metrics[identifier], y=metrics["Cumulative_Returns"], name="Cumulative Returns"),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(x=metrics[identifier], y=metrics["Max_Drawdown"], name="Max Drawdown"),
            row=1, col=2
        )
        fig.add_trace(
            go.Bar(x=metrics[identifier], y=metrics["Sharpe_Ratio"], name="Sharpe Ratio"),
            row=2, col=1
        )
        fig.add_trace(
            go.Bar(x=metrics[identifier], y=metrics["Sortino_Ratio"], name="Sortino Ratio"),
            row=2, col=2
        )

        fig.update_layout(
            title_text=f"{level.capitalize()} Performance Metrics",
            showlegend=True,
            height=600
        )
        fig.show()
