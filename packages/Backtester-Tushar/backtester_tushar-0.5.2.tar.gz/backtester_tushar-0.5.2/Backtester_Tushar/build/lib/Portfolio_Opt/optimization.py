import numpy as np
from scipy.optimize import minimize


class PortfolioOptimizer:
    """Optimizes portfolio weights using mean-variance or Black-Litterman models."""

    def __init__(self, method="mean_variance", risk_free_rate=0.03, tau=0.025):
        self.method = method
        self.risk_free_rate = risk_free_rate
        self.tau = tau  # Black-Litterman scaling factor for uncertainty

    def optimize(self, returns, cov_matrix, constraints=None, views=None, view_confidences=None):
        """Optimize portfolio weights based on the specified method."""
        if self.method == "mean_variance":
            return self._mean_variance_optimization(returns, cov_matrix, constraints)
        elif self.method == "black_litterman":
            return self._black_litterman_optimization(returns, cov_matrix, views, view_confidences, constraints)
        else:
            raise ValueError("Method must be 'mean_variance' or 'black_litterman'")

    def _mean_variance_optimization(self, returns, cov_matrix, constraints=None):
        """Mean-variance optimization to maximize Sharpe ratio."""
        n = len(returns)

        def objective(weights):
            port_return = np.sum(returns * weights) * 252
            port_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix * 252, weights)))
            return -port_return / port_vol if port_vol != 0 else np.inf

        constraints = constraints or [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        bounds = [(0, 1)] * n
        initial_weights = np.ones(n) / n
        result = minimize(objective, initial_weights, bounds=bounds, constraints=constraints)
        return result.x

    def _black_litterman_optimization(self, returns, cov_matrix, views, view_confidences, constraints=None):
        """Black-Litterman optimization incorporating investor views."""
        n = len(returns)

        # Market equilibrium returns (assuming equal weights for simplicity)
        pi = returns * 252  # Annualized market-implied returns

        # If no views are provided, return market equilibrium weights
        if views is None or view_confidences is None:
            return np.ones(n) / n

        # Views matrix (Q) and confidences (P, Omega)
        k = len(views)
        P = np.zeros((k, n))
        Q = np.array([view["return"] for view in views])
        Omega = np.diag([1 / view_confidences[i] for i in range(k)])  # Diagonal matrix of view uncertainties

        for i, view in enumerate(views):
            asset_idx = view["asset_idx"]
            P[i, asset_idx] = view["weight"]

        # Black-Litterman calculations
        tau_cov = self.tau * cov_matrix
        try:
            tau_cov_inv = np.linalg.inv(tau_cov)
            omega_inv = np.linalg.inv(Omega)
            P_transpose = P.T

            # Adjusted expected returns
            bl_returns = pi + tau_cov @ P_transpose @ np.linalg.inv(P @ tau_cov @ P_transpose + Omega) @ (Q - P @ pi)

            # Adjusted covariance
            bl_cov = cov_matrix + tau_cov - tau_cov @ P_transpose @ np.linalg.inv(
                P @ tau_cov @ P_transpose + Omega) @ P @ tau_cov
        except np.linalg.LinAlgError:
            print("Matrix inversion failed, falling back to mean-variance optimization")
            return self._mean_variance_optimization(returns, cov_matrix, constraints)

        # Optimize weights using adjusted returns and covariance
        def objective(weights):
            port_return = np.sum(bl_returns * weights) * 252
            port_vol = np.sqrt(np.dot(weights.T, np.dot(bl_cov * 252, weights)))
            return -port_return / port_vol if port_vol != 0 else np.inf

        constraints = constraints or [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        bounds = [(0, 1)] * n
        initial_weights = np.ones(n) / n
        result = minimize(objective, initial_weights, bounds=bounds, constraints=constraints)
        return result.x
