from Backtester_Tushar.Strategy_Weights.base_class import StrategyWeights
from Backtester_Tushar.Strategy_Weights.equal_weights import EqualWeights


class PerformanceBasedWeights(StrategyWeights):
    """Assigns weights based on historical performance (e.g., Sharpe Ratio)."""

    def __init__(self, metric="Sharpe_Ratio"):
        super().__init__()
        self.metric = metric

    def compute_weights(self, strategies, performance_data=None, df=None):
        if performance_data is None or performance_data.empty:
            return EqualWeights().compute_weights(strategies)

        strategy_names = {s.name for s in strategies}
        perf_data = performance_data[performance_data["Strategy"].isin(strategy_names)]

        if perf_data.empty:
            return EqualWeights().compute_weights(strategies)

        metric_values = perf_data.set_index("Strategy")[self.metric]
        metric_values = metric_values.clip(lower=0) + 1e-6
        total = metric_values.sum()
        weights = metric_values / total
        return weights.to_dict()
