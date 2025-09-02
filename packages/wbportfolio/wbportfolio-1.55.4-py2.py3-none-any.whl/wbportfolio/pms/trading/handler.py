import math
from datetime import date
from decimal import Decimal

import cvxpy as cp
import numpy as np
from django.core.exceptions import ValidationError

from wbportfolio.pms.typing import Portfolio, Trade, TradeBatch


class TradeShareOptimizer:
    def __init__(self, batch: TradeBatch, portfolio_total_value: float):
        self.batch = batch
        self.portfolio_total_value = portfolio_total_value

    def optimize(self, target_cash: float = 0.99):
        try:
            return self.optimize_trade_share(target_cash)
        except ValueError:
            return self.floor_trade_share()

    def optimize_trade_share(self, target_cash: float = 0.01):
        prices_fx_portfolio = np.array([trade.price_fx_portfolio for trade in self.batch.trades])
        target_allocs = np.array([trade.target_weight for trade in self.batch.trades])

        # Decision variable: number of shares (integers)
        shares = cp.Variable(len(prices_fx_portfolio), integer=True)

        # Calculate portfolio values
        portfolio_values = cp.multiply(shares, prices_fx_portfolio)

        # Target values based on allocations
        target_values = self.portfolio_total_value * target_allocs

        # Objective: minimize absolute deviation from target values
        objective = cp.Minimize(cp.sum(cp.abs(portfolio_values - target_values)))

        # Constraints
        constraints = [
            shares >= 0,  # No short selling
            cp.sum(portfolio_values) <= self.portfolio_total_value,  # Don't exceed budget
            cp.sum(portfolio_values) >= (1.0 - target_cash) * self.portfolio_total_value,  # Use at least 99% of budget
        ]

        # Solve
        problem = cp.Problem(objective, constraints)
        problem.solve(solver=cp.CBC)

        if problem != "optimal":
            raise ValueError(f"Optimization failed: {problem.status}")

        shares_result = shares.value.astype(int)
        return TradeBatch(
            [
                trade.normalize_target(target_shares=shares_result[index])
                for index, trade in enumerate(self.batch.trades)
            ]
        )

    def floor_trade_share(self):
        return TradeBatch(
            [trade.normalize_target(target_shares=math.floor(trade.target_shares)) for trade in self.batch.trades]
        )


class TradingService:
    """
    This class represents the trading service. It can be instantiated either with the target portfolio and the effective portfolio or given a direct list of trade
    In any case, it will compute all three states
    """

    def __init__(
        self,
        trade_date: date,
        effective_portfolio: Portfolio | None = None,
        target_portfolio: Portfolio | None = None,
        total_target_weight: Decimal = Decimal("1.0"),
    ):
        self.trade_date = trade_date
        if target_portfolio is None:
            target_portfolio = Portfolio(positions=())
        if effective_portfolio is None:
            effective_portfolio = Portfolio(positions=())
        # If effective portfolio and trades batch is provided, we ensure the trade batch contains at least one trade for every position
        self.trades_batch = self.build_trade_batch(effective_portfolio, target_portfolio).normalize(
            total_target_weight
        )
        self._effective_portfolio = effective_portfolio

    @property
    def errors(self) -> list[str]:
        """
        Returned the list of errors stored during the validation process. Can only be called after is_valid
        """
        if not hasattr(self, "_errors"):
            msg = "You must call `.is_valid()` before accessing `.errors`."
            raise AssertionError(msg)
        return self._errors

    @property
    def validated_trades(self) -> list[Trade]:
        """
        Returned the list of validated trade stored during the validation process. Can only be called after is_valid
        """
        if not hasattr(self, "_validated_trades"):
            msg = "You must call `.is_valid()` before accessing `.validated_trades`."
            raise AssertionError(msg)
        return self._validated_trades

    def run_validation(self, validated_trades: list[Trade]):
        """
        Test the given value against all the validators on the field,
        and either raise a `ValidationError` or simply return.
        """
        if self._effective_portfolio:
            for trade in validated_trades:
                if (
                    trade.previous_weight
                    and trade.underlying_instrument not in self._effective_portfolio.positions_map
                ):
                    raise ValidationError("All effective position needs to be matched with a validated trade")

    def build_trade_batch(
        self,
        effective_portfolio: Portfolio,
        target_portfolio: Portfolio,
    ) -> TradeBatch:
        """
        Given combination of effective portfolio and either a trades batch or a target portfolio, ensure all theres variables are set

        Args:
            effective_portfolio: The effective portfolio
            target_portfolio: The optional target portfolio
            trades_batch: The optional trades batch

        Returns: The normalized trades batch
        """

        instruments = effective_portfolio.positions_map.copy()
        instruments.update(target_portfolio.positions_map)

        trades: list[Trade] = []
        for instrument_id, pos in instruments.items():
            previous_weight = target_weight = 0
            effective_shares = target_shares = 0
            daily_return = 0
            is_cash = False
            if effective_pos := effective_portfolio.positions_map.get(instrument_id, None):
                previous_weight = effective_pos.weighting
                effective_shares = effective_pos.shares
                daily_return = effective_pos.daily_return
                is_cash = effective_pos.is_cash
            if target_pos := target_portfolio.positions_map.get(instrument_id, None):
                target_weight = target_pos.weighting
                is_cash = target_pos.is_cash
                if target_pos.shares is not None:
                    target_shares = target_pos.shares
            trade = Trade(
                underlying_instrument=instrument_id,
                previous_weight=previous_weight,
                target_weight=target_weight,
                effective_shares=effective_shares,
                target_shares=target_shares,
                date=self.trade_date,
                instrument_type=pos.instrument_type,
                currency=pos.currency,
                price=Decimal(pos.price) if pos.price is not None else Decimal("0"),
                currency_fx_rate=Decimal(pos.currency_fx_rate),
                daily_return=Decimal(daily_return),
                portfolio_contribution=effective_portfolio.portfolio_contribution,
                is_cash=is_cash,
            )
            trades.append(trade)
        return TradeBatch(trades)

    def is_valid(self, ignore_error: bool = False) -> bool:
        """
        Validate the trade batch against a set of default rules. Populate the validated_trades and errors property.
        Ignore error by default
        Args:
            ignore_error: If true, will raise the error. False by default

        Returns: True if the trades batch is valid
        """
        if not hasattr(self, "_validated_trades"):
            self._validated_trades = []
            self._errors = []
            # Run validation for every trade. If a trade is not valid, we simply exclude it from the validated trades list
            for _, trade in self.trades_batch.trades_map.items():
                try:
                    trade.validate()
                    self._validated_trades.append(trade)
                except ValidationError as exc:
                    self._errors.append(exc.message)
            try:
                # Check the overall validity of the trade batch. If this fail, we consider all trade invalids
                self.run_validation(self._validated_trades)
            except ValidationError as exc:
                self._validated_trades = []
                self._errors.append(exc.message)

            if self._errors and not ignore_error:
                raise ValidationError(self.errors)

        return not bool(self._errors)

    def get_optimized_trade_batch(self, portfolio_total_value: float, target_cash: float):
        return TradeShareOptimizer(
            self.trades_batch, portfolio_total_value
        ).floor_trade_share()  # TODO switch to the other optimization when ready
