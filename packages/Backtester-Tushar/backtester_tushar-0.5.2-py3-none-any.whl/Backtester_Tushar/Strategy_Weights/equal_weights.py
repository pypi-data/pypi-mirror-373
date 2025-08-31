from Backtester_Tushar.Strategy_Weights.base_class import StrategyWeights

class EqualWeights(StrategyWeights):
    """Assigns equal weights to all strategies."""

    def compute_weights(self, strategies, performance_data=None, df=None):
        n = len(strategies)
        return {s.name: 1.0 / n for s in strategies} if n > 0 else {}