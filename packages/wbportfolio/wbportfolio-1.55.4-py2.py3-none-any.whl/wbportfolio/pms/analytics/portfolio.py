import numpy as np
import pandas as pd
from skfolio import Portfolio as BasePortfolio

from .utils import fix_quantization_error


class Portfolio(BasePortfolio):
    @property
    def all_weights_per_observation(self) -> pd.DataFrame:
        """DataFrame of the Portfolio weights containing even near zero weight per observation."""
        weights = self.weights
        assets = self.assets
        df = pd.DataFrame(
            np.ones((len(self.observations), len(assets))) * weights,
            index=self.observations,
            columns=assets,
        )
        return df

    def get_contributions(self) -> tuple[pd.Series, float]:
        returns = self.X.iloc[-1, :].T
        weights = self.all_weights_per_observation.iloc[-1, :].T
        portfolio_returns = (weights * (returns + 1.0)).sum()
        return returns, portfolio_returns

    def get_next_weights(self, round_precision: int = 8) -> dict[int, float]:
        """
        Given the next returns, compute the drifted weights of this portfolio
            round_precision: Round the weight to the given round number and ensure the total weight reflects this. Default to 8 decimals
        Returns:
            A dictionary of weights (instrument ids as keys and weights as values)
        """
        returns, portfolio_returns = self.get_contributions()
        weights = self.all_weights_per_observation.iloc[-1, :].T
        next_weights = weights * (returns + 1.0) / portfolio_returns
        next_weights = next_weights.dropna()
        next_weights = next_weights / next_weights.sum()
        if round_precision and not next_weights.empty:
            next_weights = fix_quantization_error(next_weights, round_precision)
        return {i: round(w, round_precision) for i, w in next_weights.items()}  # handle float precision manually

    def get_estimate_net_value(self, previous_net_asset_value: float) -> float:
        expected_returns = self.weights @ self.X.iloc[-1, :].T
        return previous_net_asset_value * (1.0 + expected_returns)
