import pandas as pd
import numpy as np
from numba import njit, prange
from scipy import stats, optimize, linalg
from scipy.stats import norm
from sklearn.decomposition import PCA
from sklearn.covariance import LedoitWolf
import warnings
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Optional
import logging
from scipy.optimize import minimize
from Backtester_Tushar.Risk.risk_limits import RiskLimits
from Backtester_Tushar.Portfolio_Management_and_Tracker.utils import *
warnings.filterwarnings('ignore')


class RiskManager:
    """Comprehensive risk management with VaR, factor exposure, and compliance"""

    def __init__(self, risk_limits: RiskLimits, lookback_days=252):
        self.risk_limits = risk_limits
        self.lookback_days = lookback_days
        self.factor_loadings = {}
        self.correlation_matrix = None
        self.var_models = {}

    def calculate_portfolio_var(self, positions, returns_covariance, confidence=0.05):
        """Calculate portfolio VaR as % of portfolio value (not absolute dollars)."""
        if not positions or returns_covariance is None:
            return 0.0

        tickers = list(positions.keys())
        position_values = np.array([positions[ticker]['market_value'] for ticker in tickers])

        if len(position_values) == 0:
            return 0.0

        portfolio_value = np.sum(np.abs(position_values))
        if portfolio_value == 0:
            return 0.0

        weights = position_values / portfolio_value

        n_assets = len(weights)
        if returns_covariance.shape[0] != n_assets:
            return 0.0

        # Portfolio variance (in return space)
        portfolio_variance = np.dot(weights.T, np.dot(returns_covariance, weights))
        if portfolio_variance < 0:
            portfolio_variance = 0
        portfolio_std = np.sqrt(portfolio_variance)

        # Parametric VaR (as % of portfolio value)
        z_score = norm.ppf(1 - confidence)  # e.g. 1.645 for 95%
        parametric_var_pct = z_score * portfolio_std  # % loss

        # Historical VaR fallback (also in % terms)
        if hasattr(self, 'historical_returns') and len(self.historical_returns) > 100:
            hist_var_pct = -np.percentile(self.historical_returns, confidence * 100)
            return max(parametric_var_pct, hist_var_pct)

        return parametric_var_pct

    def optimize_with_constraints(self, expected_returns, covariance_matrix, sector_groups, betas=None,
                                  risk_aversion=1.0, is_short=False):
        """
        Mean-variance optimization with position, sector, and beta constraints.
        Args:
            expected_returns (np.array): Expected returns for each asset.
            covariance_matrix (np.array): Covariance matrix of returns.
            sector_groups (dict): Mapping of sector names to indices of assets in that sector.
            betas (np.array, optional): Beta values for each asset, default None.
            risk_aversion (float): Risk aversion factor, default 1.0.
            is_short (bool): Whether optimizing for short positions, default False.
        Returns:
            np.array: Optimized weights.
        """
        n_assets = len(expected_returns)
        if n_assets == 0 or covariance_matrix is None or covariance_matrix.shape[0] != n_assets:
            return np.zeros(n_assets)

        # Validate inputs
        if np.any(np.isnan(expected_returns)) or np.any(np.isnan(covariance_matrix)):
            return np.zeros(n_assets)
        expected_returns = np.nan_to_num(expected_returns, nan=0.0)
        covariance_matrix = np.nan_to_num(covariance_matrix, nan=0.0)

        # Regularize covariance matrix to avoid ill-conditioning
        regularization = 1e-6 * np.eye(n_assets)
        cov_reg = covariance_matrix + regularization

        # Objective function: minimize risk - (1/risk_aversion) * return
        def objective(weights):
            if risk_aversion <= 0:
                return np.inf  # Prevent division by zero or negative risk aversion
            port_var = np.dot(weights.T, np.dot(cov_reg, weights))
            port_ret = np.dot(weights, expected_returns)
            return port_var - (1 / risk_aversion) * port_ret

        # Helper function to create position size constraint
        def create_position_constraint(index):
            def constraint(weights):
                return self.risk_limits.max_position_size - abs(weights[index])

            return constraint

        # Helper function to create sector exposure constraint
        def create_sector_constraint(indices):
            def constraint(weights):
                return self.risk_limits.max_sector_exposure - np.sum(np.abs(weights[indices]))

            return constraint

        # Helper function to create beta constraint
        def create_beta_constraint():
            def constraint(weights):
                return self.risk_limits.max_beta_exposure - abs(np.dot(weights, betas))

            return constraint

        # Build constraints list
        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}  # Weights sum to 1
        ]

        # Add position size constraints
        for i in range(n_assets):
            constraints.append({'type': 'ineq', 'fun': create_position_constraint(i)})

        # Add sector exposure constraints
        for sector, indices in sector_groups.items():
            if not all(0 <= idx < n_assets for idx in indices):  # Validate indices
                continue
            constraints.append({'type': 'ineq', 'fun': create_sector_constraint(indices)})

        # Add beta constraint if betas provided
        if betas is not None and len(betas) == n_assets:
            constraints.append({'type': 'ineq', 'fun': create_beta_constraint()})

        # Bounds: 0 to 1 for longs, -1 to 0 for shorts
        bounds = [(0, 1) if not is_short else (-1, 0) for _ in range(n_assets)]

        # Initial guess
        init_weights = np.ones(n_assets) / n_assets
        if is_short:
            init_weights = -init_weights  # Start with short bias

        # Optimization
        result = minimize(objective, init_weights, method='SLSQP', bounds=bounds, constraints=constraints,
                          options={'maxiter': 1000, 'ftol': 1e-8})

        if result.success:
            weights = result.x
        else:
            # Fallback: equal weights with iterative constraint adjustment
            weights = np.ones(n_assets) / n_assets
            if is_short:
                weights = -weights
            max_iterations = 20
            for _ in range(max_iterations):
                violations = False
                # Check position size
                pos_viol = np.max(np.abs(weights) - self.risk_limits.max_position_size)
                if pos_viol > 0:
                    violations = True
                    weights[np.abs(weights) > self.risk_limits.max_position_size] *= (
                                self.risk_limits.max_position_size / np.abs(
                            weights[np.abs(weights) > self.risk_limits.max_position_size]))

                # Check sector exposure
                for sector, indices in sector_groups.items():
                    sector_sum = np.sum(np.abs(weights[indices]))
                    if sector_sum > self.risk_limits.max_sector_exposure:
                        violations = True
                        scale = self.risk_limits.max_sector_exposure / sector_sum
                        weights[indices] *= scale

                # Check beta if applicable
                if betas is not None and len(betas) == n_assets:
                    beta_exp = abs(np.dot(weights, betas))
                    if beta_exp > self.risk_limits.max_beta_exposure:
                        violations = True
                        weights *= (self.risk_limits.max_beta_exposure / beta_exp)

                if not violations:
                    break
            weights = weights / np.sum(np.abs(weights))  # Renormalize

        return weights


    def calculate_marginal_var(self, ticker, positions, returns_covariance, confidence=0.05):
        """Calculate marginal VaR contribution of a position"""
        if ticker not in positions or returns_covariance is None:
            return 0.0

        # Calculate VaR with and without the position
        full_var = self.calculate_portfolio_var(positions, returns_covariance, confidence)

        # Remove position and recalculate
        positions_without = {k: v for k, v in positions.items() if k != ticker}
        var_without = self.calculate_portfolio_var(positions_without, returns_covariance, confidence)

        return full_var - var_without

    def check_risk_limits(self, positions, portfolio_value, beta_exposure=0.0):
        """Check all risk limits and return violations"""
        violations = []

        if not positions:
            return violations

        # Position size limits
        for ticker, pos in positions.items():
            position_pct = abs(pos['market_value']) / portfolio_value
            if position_pct > self.risk_limits.max_position_size:
                violations.append(f"Position size limit violated for {ticker}: {position_pct:.2%}")

        # Beta exposure limit
        if abs(beta_exposure) > self.risk_limits.max_beta_exposure:
            violations.append(f"Beta exposure limit violated: {beta_exposure:.3f}")

        # Leverage limit
        gross_exposure = sum(abs(pos['market_value']) for pos in positions.values())
        leverage = gross_exposure / portfolio_value
        if leverage > self.risk_limits.max_leverage:
            violations.append(f"Leverage limit violated: {leverage:.2f}")

        return violations

    def calculate_risk_adjusted_weights(self, expected_returns, covariance_matrix, risk_aversion=1.0):
        """Calculate optimal portfolio weights using mean-variance optimization"""
        if len(expected_returns) == 0 or covariance_matrix is None:
            return {}

        try:
            # Regularize covariance matrix
            regularization = 1e-8 * np.eye(covariance_matrix.shape[0])
            reg_cov_matrix = covariance_matrix + regularization

            # Solve for optimal weights: w = (1/lambda) * inv(Sigma) * mu
            inv_cov = linalg.inv(reg_cov_matrix)
            optimal_weights = np.dot(inv_cov, expected_returns) / risk_aversion

            # Normalize weights
            total_weight = np.sum(np.abs(optimal_weights))
            if total_weight > 0:
                optimal_weights = optimal_weights / total_weight

            return optimal_weights

        except (linalg.LinAlgError, np.linalg.LinAlgError):
            # Fall back to equal weights if optimization fails
            n_assets = len(expected_returns)
            return np.ones(n_assets) / n_assets
