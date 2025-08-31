import numpy as np

class MarketImpactModel:
    """Almgren-Chriss execution model with market impact"""

    def __init__(self, permanent_impact=0.1, temporary_impact=0.01, volatility_adjustment=True):
        self.permanent_impact = permanent_impact
        self.temporary_impact = temporary_impact
        self.volatility_adjustment = volatility_adjustment

    def calculate_market_impact(self, shares, avg_volume, volatility, participation_rate=0.1):
        """Calculate market impact cost using Almgren-Chriss model"""
        if avg_volume <= 0 or shares == 0:
            return 0.0

        # Market impact parameters
        volume_ratio = abs(shares) / avg_volume

        # Permanent impact (linear in volume)
        permanent_cost = self.permanent_impact * volume_ratio

        # Temporary impact (square-root law)
        temporary_cost = self.temporary_impact * np.sqrt(volume_ratio)

        # Volatility adjustment
        if self.volatility_adjustment and volatility > 0:
            vol_multiplier = volatility / 0.02  # Normalize to 2% daily vol
            permanent_cost *= vol_multiplier
            temporary_cost *= vol_multiplier

        total_impact = permanent_cost + temporary_cost
        return min(total_impact, 0.05)  # Cap at 5%

    def optimal_execution_schedule(self, total_shares, time_horizon_days, risk_aversion=1e-6):
        """Calculate optimal execution schedule"""
        if time_horizon_days <= 0:
            return [total_shares]

        # Simple arithmetic schedule for now (can be enhanced with more complex optimization)
        shares_per_period = total_shares / time_horizon_days
        return [shares_per_period] * int(time_horizon_days)




