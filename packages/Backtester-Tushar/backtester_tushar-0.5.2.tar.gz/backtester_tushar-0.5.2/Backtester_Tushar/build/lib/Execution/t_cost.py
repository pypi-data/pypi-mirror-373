class TransactionCostModel:
    """Models transaction costs."""

    def __init__(self, model_type="percentage", base_cost=0.001, volume_factor=0.0001):
        self.model_type = model_type
        self.base_cost = base_cost
        self.volume_factor = volume_factor

    def calculate_cost(self, shares, price, volume):
        if self.model_type == "percentage":
            return shares * price * self.base_cost
        elif self.model_type == "volume_weighted":
            return shares * price * (self.base_cost + self.volume_factor * (shares / volume if volume > 0 else 0))
        return 0
