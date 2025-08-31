from dataclasses import dataclass


@dataclass
class RiskLimits:
    """Risk limit configuration"""
    max_position_size: float = 0.05  # 5% max per position
    max_sector_exposure: float = 0.20  # 20% max per sector
    max_beta_exposure: float = 0.15  # Net beta limit
    max_daily_var: float = 0.02  # 2% daily VaR
    max_drawdown: float = 0.10  # 10% max drawdown
    max_leverage: float = 1.0  # Net leverage limit