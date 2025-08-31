from abc import ABC, abstractmethod


class StrategyWeights(ABC):
    """Abstract base class for computing strategy weights."""

    def __init__(self):
        self.weights_cache = {}

    @abstractmethod
    def compute_weights(self, strategies, performance_data=None, df=None):
        """Compute weights for each strategy."""
        pass

    def get_weights(self, strategies, performance_data=None, df=None):
        """Retrieve or compute weights, using cache for efficiency."""
        cache_key = tuple(s.name for s in strategies) + (
        id(performance_data) if performance_data is not None else 0,) + (id(df) if df is not None else 0,)
        if cache_key not in self.weights_cache:
            self.weights_cache[cache_key] = self.compute_weights(strategies, performance_data, df)
        return self.weights_cache[cache_key]
