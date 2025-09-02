# Import necessary modules
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import call, patch

import pytest
from django.db.models import Sum
from faker import Faker
from pandas._libs.tslibs.offsets import BDay, BusinessMonthEnd

from wbportfolio.models import Order, OrderProposal, Portfolio, RebalancingModel
from wbportfolio.pms.typing import Portfolio as PortfolioDTO
from wbportfolio.pms.typing import Position

fake = Faker()


# Mark tests to use Django's database
@pytest.mark.django_db
class TestOrderProposal:
    def test_init(self, order_proposal):
        assert order_proposal.id is not None

    # Test that the checked object is correctly set to the portfolio
    def test_checked_object(self, order_proposal):
        """
        Verify that the checked object is the portfolio associated with the order proposal.
        """
        assert order_proposal.checked_object == order_proposal.portfolio

    # Test that the evaluation date matches the trade date
    def test_check_evaluation_date(self, order_proposal):
        """
        Ensure the evaluation date is the same as the trade date.
        """
        assert order_proposal.check_evaluation_date == order_proposal.trade_date

    # Test the validated trading service functionality
    def test_validated_trading_service(self, order_proposal, asset_position_factory, order_factory):
        """
        Validate that the effective and target portfolios are correctly calculated.
        """
        effective_date = (order_proposal.trade_date - BDay(1)).date()

        # Create asset positions for testing
        a1 = asset_position_factory.create(
            portfolio=order_proposal.portfolio, date=effective_date, weighting=Decimal("0.3")
        )
        a2 = asset_position_factory.create(
            portfolio=order_proposal.portfolio, date=effective_date, weighting=Decimal("0.7")
        )

        # Create orders for testing
        o1 = order_factory.create(
            order_proposal=order_proposal,
            weighting=Decimal("0.05"),
            portfolio=order_proposal.portfolio,
            underlying_instrument=a1.underlying_quote,
        )
        o2 = order_factory.create(
            order_proposal=order_proposal,
            weighting=Decimal("-0.05"),
            portfolio=order_proposal.portfolio,
            underlying_instrument=a2.underlying_quote,
        )

        r1 = o1.price / a1.initial_price - Decimal("1")
        r2 = o2.price / a2.initial_price - Decimal("1")
        p_return = a1.weighting * (Decimal("1") + r1) + a2.weighting * (Decimal("1") + r2)
        # Get the validated trading service
        trades = order_proposal.validated_trading_service.trades_batch.trades_map
        t1 = trades[a1.underlying_quote.id]
        t2 = trades[a2.underlying_quote.id]

        # Assert effective and target portfolios are as expected
        assert t1.previous_weight == a1.weighting
        assert t2.previous_weight == a2.weighting
        assert t1.target_weight == pytest.approx(
            a1.weighting * ((r1 + Decimal("1")) / p_return) + o1.weighting, abs=Decimal("1e-8")
        )
        assert t2.target_weight == pytest.approx(
            a2.weighting * ((r2 + Decimal("1")) / p_return) + o2.weighting, abs=Decimal("1e-8")
        )

    # Test the calculation of the last effective date
    def test_last_effective_date(self, order_proposal, asset_position_factory):
        """
        Verify the last effective date is correctly determined based on asset positions.
        """
        # Without any positions, it should be the day before the trade date
        assert (
            order_proposal.last_effective_date == (order_proposal.trade_date - BDay(1)).date()
        ), "Last effective date without position should be t-1"

        # Create an asset position before the trade date
        a1 = asset_position_factory.create(
            portfolio=order_proposal.portfolio, date=(order_proposal.trade_date - BDay(5)).date()
        )
        a_noise = asset_position_factory.create(portfolio=order_proposal.portfolio, date=order_proposal.trade_date)  # noqa

        # The last effective date should still be the day before the trade date due to caching
        assert (
            order_proposal.last_effective_date == (order_proposal.trade_date - BDay(1)).date()
        ), "last effective date is cached, so it won't change as is"

        # Reset the cache property to recalculate
        del order_proposal.last_effective_date

        # Now it should be the date of the latest position before the trade date
        assert (
            order_proposal.last_effective_date == a1.date
        ), "last effective date is the latest position strictly lower than trade date"

    # Test finding the previous order proposal
    def test_previous_order_proposal(self, order_proposal_factory):
        """
        Ensure the previous order proposal is correctly identified as the last approved proposal before the current one.
        """
        tp = order_proposal_factory.create()
        tp_previous_submit = order_proposal_factory.create(  # noqa
            portfolio=tp.portfolio, status=OrderProposal.Status.PENDING, trade_date=(tp.trade_date - BDay(1)).date()
        )
        tp_previous_approve = order_proposal_factory.create(
            portfolio=tp.portfolio, status=OrderProposal.Status.APPLIED, trade_date=(tp.trade_date - BDay(2)).date()
        )
        tp_next_approve = order_proposal_factory.create(  # noqa
            portfolio=tp.portfolio, status=OrderProposal.Status.APPLIED, trade_date=(tp.trade_date + BDay(1)).date()
        )

        # The previous valid order proposal should be the approved one strictly before the current proposal
        assert (
            tp.previous_order_proposal == tp_previous_approve
        ), "the previous valid order proposal is the strictly before and approved order proposal"

    # Test finding the next order proposal
    def test_next_order_proposal(self, order_proposal_factory):
        """
        Verify the next order proposal is correctly identified as the first approved proposal after the current one.
        """
        tp = order_proposal_factory.create()
        tp_previous_approve = order_proposal_factory.create(  # noqa
            portfolio=tp.portfolio, status=OrderProposal.Status.APPLIED, trade_date=(tp.trade_date - BDay(1)).date()
        )
        tp_next_submit = order_proposal_factory.create(  # noqa
            portfolio=tp.portfolio, status=OrderProposal.Status.PENDING, trade_date=(tp.trade_date + BDay(1)).date()
        )
        tp_next_approve = order_proposal_factory.create(
            portfolio=tp.portfolio, status=OrderProposal.Status.APPLIED, trade_date=(tp.trade_date + BDay(2)).date()
        )

        # The next valid order proposal should be the approved one strictly after the current proposal
        assert (
            tp.next_order_proposal == tp_next_approve
        ), "the next valid order proposal is the strictly after and approved order proposal"

    # Test getting the default target portfolio
    def test__get_default_target_portfolio(self, order_proposal, asset_position_factory):
        """
        Ensure the default target portfolio is set to the effective portfolio from the day before the trade date.
        """
        effective_date = (order_proposal.trade_date - BDay(1)).date()

        # Create asset positions for testing
        a1 = asset_position_factory.create(
            portfolio=order_proposal.portfolio, date=effective_date, weighting=Decimal("0.3")
        )
        a2 = asset_position_factory.create(
            portfolio=order_proposal.portfolio, date=effective_date, weighting=Decimal("0.7")
        )
        asset_position_factory.create(portfolio=order_proposal.portfolio, date=order_proposal.trade_date)  # noise

        # The default target portfolio should match the effective portfolio
        assert order_proposal._get_default_target_portfolio().to_dict() == {
            a1.underlying_quote.id: a1.weighting,
            a2.underlying_quote.id: a2.weighting,
        }

    # Test getting the default target portfolio with a rebalancing model
    @patch.object(RebalancingModel, "get_target_portfolio")
    def test__get_default_target_portfolio_with_rebalancer_model(self, mock_fct, order_proposal, rebalancer_factory):
        """
        Verify that the target portfolio is correctly obtained from a rebalancing model.
        """
        # Expected target portfolio from the rebalancing model
        expected_target_portfolio = PortfolioDTO(
            positions=(Position(underlying_instrument=1, weighting=Decimal(1), date=order_proposal.trade_date),)
        )
        mock_fct.return_value = expected_target_portfolio

        # Create a rebalancer for testing
        rebalancer = rebalancer_factory.create(
            portfolio=order_proposal.portfolio, parameters={"rebalancer_parameter": "A"}
        )
        order_proposal.rebalancing_model = rebalancer.rebalancing_model
        order_proposal.save()

        # Additional keyword arguments for the rebalancing model
        extra_kwargs = {"test": "test"}

        # Combine rebalancer parameters with extra keyword arguments
        expected_kwargs = rebalancer.parameters
        expected_kwargs.update(extra_kwargs)

        # Assert the target portfolio matches the expected output from the rebalancing model
        assert (
            order_proposal._get_default_target_portfolio(**extra_kwargs) == expected_target_portfolio
        ), "We expect the target portfolio to be whatever is returned by the rebalancer model"
        mock_fct.assert_called_once_with(
            order_proposal.portfolio, order_proposal.trade_date, order_proposal.last_effective_date, **expected_kwargs
        )

    # Test normalizing orders
    def test_normalize_orders(self, order_proposal, order_factory):
        """
        Ensure orders are normalized to sum up to 1, handling quantization errors.
        """
        # Create orders for testing
        t1 = order_factory.create(
            order_proposal=order_proposal,
            portfolio=order_proposal.portfolio,
            weighting=Decimal(0.2),
        )
        t2 = order_factory.create(
            order_proposal=order_proposal,
            portfolio=order_proposal.portfolio,
            weighting=Decimal(0.26),
        )
        t3 = order_factory.create(
            order_proposal=order_proposal,
            portfolio=order_proposal.portfolio,
            weighting=Decimal(0.14),
        )

        # Normalize orders
        order_proposal.normalize_orders()

        # Refresh orders from the database
        t1.refresh_from_db()
        t2.refresh_from_db()
        t3.refresh_from_db()

        # Expected normalized weights
        normalized_t1_weight = Decimal("0.33333333")
        normalized_t2_weight = Decimal("0.43333333")
        normalized_t3_weight = Decimal("0.23333333")

        # Calculate quantization error
        quantize_error = Decimal(1) - (normalized_t1_weight + normalized_t2_weight + normalized_t3_weight)

        # Assert quantization error exists and weights are normalized correctly
        assert quantize_error
        assert t1.weighting == normalized_t1_weight
        assert t2.weighting == normalized_t2_weight + quantize_error  # Add quantize error to the largest position
        assert t3.weighting == normalized_t3_weight

    # Test resetting orders
    def test_reset_orders(
        self, order_proposal, instrument_factory, cash_factory, instrument_price_factory, asset_position_factory
    ):
        """
        Verify orders are correctly reset based on effective and target portfolios.
        """
        cash = cash_factory.create()
        effective_date = order_proposal.last_effective_date

        # Create instruments for testing
        i1 = instrument_factory.create(currency=order_proposal.portfolio.currency)
        i2 = instrument_factory.create(currency=order_proposal.portfolio.currency)
        i3 = instrument_factory.create(currency=order_proposal.portfolio.currency)
        # Build initial effective portfolio constituting only from two positions of i1 and i2
        asset_position_factory.create(
            portfolio=order_proposal.portfolio, date=effective_date, underlying_instrument=i1, weighting=Decimal("0.7")
        )
        asset_position_factory.create(
            portfolio=order_proposal.portfolio, date=effective_date, underlying_instrument=i2, weighting=Decimal("0.3")
        )
        p1 = instrument_price_factory.create(instrument=i1, date=effective_date)
        p2 = instrument_price_factory.create(instrument=i2, date=effective_date)
        p3 = instrument_price_factory.create(instrument=i3, date=effective_date)

        # build the target portfolio
        target_portfolio = PortfolioDTO(
            [
                Position(
                    underlying_instrument=i2.id,
                    date=order_proposal.trade_date,
                    weighting=Decimal("0.4"),
                    price=float(p2.net_value),
                ),
                Position(
                    underlying_instrument=i3.id,
                    date=order_proposal.trade_date,
                    weighting=Decimal("0.6"),
                    price=float(p3.net_value),
                ),
            ]
        )

        # Reset orders
        order_proposal.reset_orders(target_portfolio=target_portfolio)

        # Get orders for each instrument
        t1 = order_proposal.orders.get(underlying_instrument=i1)
        t2 = order_proposal.orders.get(underlying_instrument=i2)
        t3 = order_proposal.orders.get(underlying_instrument=i3)

        # Assert trade weights are correctly reset
        assert t1.weighting == Decimal("-0.7")
        assert t2.weighting == Decimal("0.1")
        assert t3.weighting == Decimal("0.6")

        # build the target portfolio
        new_target_portfolio = PortfolioDTO(
            [
                Position(
                    underlying_instrument=i1.id,
                    date=order_proposal.trade_date,
                    weighting=Decimal("0.2"),
                    price=float(p1.net_value),
                ),
                Position(
                    underlying_instrument=i2.id,
                    date=order_proposal.trade_date,
                    weighting=Decimal("0.3"),
                    price=float(p2.net_value),
                ),
                Position(
                    underlying_instrument=i3.id,
                    date=order_proposal.trade_date,
                    weighting=Decimal("0.5"),
                    price=float(p3.net_value),
                ),
            ]
        )

        order_proposal.reset_orders(target_portfolio=new_target_portfolio)
        # Refetch the orders for each instrument
        t1.refresh_from_db()
        t2.refresh_from_db()
        t3.refresh_from_db()
        # Assert existing trade weights are correctly updated
        assert t1.weighting == Decimal("-0.5")
        assert t2.weighting == Decimal("0")
        assert t3.weighting == Decimal("0.5")

        # assert cash position creates a proper order
        # build the target portfolio
        target_portfolio_with_cash = PortfolioDTO(
            [
                Position(
                    underlying_instrument=i1.id,
                    date=order_proposal.trade_date,
                    weighting=Decimal("0.5"),
                    price=float(p1.net_value),
                ),
                Position(
                    underlying_instrument=cash.id,
                    date=order_proposal.trade_date,
                    weighting=Decimal("0.5"),
                    price=1.0,
                ),
            ]
        )
        order_proposal.reset_orders(target_portfolio=target_portfolio_with_cash)

        # Assert existing trade weights are correctly updated
        assert order_proposal.orders.get(underlying_instrument=i1).weighting == Decimal("-0.2")
        assert order_proposal.orders.get(underlying_instrument=i2).weighting == Decimal("-0.3")
        assert order_proposal.orders.get(underlying_instrument=cash).weighting == Decimal("0.5")

    def test_reset_orders_remove_invalid_orders(self, order_proposal, order_factory):
        # create a invalid trade and its price
        invalid_trade = order_factory.create(order_proposal=order_proposal, weighting=Decimal(0))

        # create a valid trade and its price
        valid_trade = order_factory.create(order_proposal=order_proposal, weighting=Decimal(1))
        order_proposal.reset_orders()
        assert order_proposal.orders.get(underlying_instrument=valid_trade.underlying_instrument).weighting == Decimal(
            "1"
        )
        with pytest.raises(Order.DoesNotExist):
            order_proposal.orders.get(underlying_instrument=invalid_trade.underlying_instrument)

    # Test replaying order proposals
    @patch.object(Portfolio, "drift_weights")
    def test_replay(self, mock_fct, order_proposal_factory):
        """
        Ensure replaying order proposals correctly calls drift_weights for each period.
        """
        mock_fct.return_value = iter([])

        # Create approved order proposals for testing
        tp0 = order_proposal_factory.create(status=OrderProposal.Status.APPLIED)
        tp1 = order_proposal_factory.create(
            portfolio=tp0.portfolio,
            status=OrderProposal.Status.APPLIED,
            trade_date=(tp0.trade_date + BusinessMonthEnd(1)).date(),
        )
        tp2 = order_proposal_factory.create(
            portfolio=tp0.portfolio,
            status=OrderProposal.Status.APPLIED,
            trade_date=(tp1.trade_date + BusinessMonthEnd(1)).date(),
        )

        # Replay order proposals
        tp0.replay()

        # Expected calls to drift_weights
        expected_calls = [
            call(tp0.trade_date, tp1.trade_date - timedelta(days=1), stop_at_rebalancing=True),
            call(tp1.trade_date, tp2.trade_date - timedelta(days=1), stop_at_rebalancing=True),
            call(tp2.trade_date, date.today(), stop_at_rebalancing=True),
        ]

        # Assert drift_weights was called as expected
        mock_fct.assert_has_calls(expected_calls)

        # Test stopping replay on a non-approved proposal
        tp1.status = OrderProposal.Status.FAILED
        tp1.save()
        expected_calls = [call(tp0.trade_date, tp1.trade_date - timedelta(days=1), stop_at_rebalancing=True)]
        mock_fct.assert_has_calls(expected_calls)

    # Test estimating shares for a trade
    @patch.object(Portfolio, "get_total_asset_value")
    def test_get_estimated_shares(
        self, mock_fct, order_proposal, order_factory, instrument_price_factory, instrument_factory
    ):
        """
        Verify shares estimation based on trade weighting and instrument price.
        """
        portfolio = order_proposal.portfolio
        instrument = instrument_factory.create(currency=portfolio.currency)
        underlying_quote_price = instrument_price_factory.create(instrument=instrument, date=order_proposal.trade_date)
        mock_fct.return_value = Decimal(1_000_000)  # 1 million cash
        trade = order_factory.create(
            order_proposal=order_proposal,
            value_date=order_proposal.trade_date,
            portfolio=portfolio,
            underlying_instrument=instrument,
        )
        trade.refresh_from_db()

        # Assert estimated shares are correctly calculated
        assert (
            order_proposal.get_estimated_shares(
                trade.weighting, trade.underlying_instrument, underlying_quote_price.net_value
            )
            == Decimal(1_000_000) * trade.weighting / underlying_quote_price.net_value
        )

    @patch.object(Portfolio, "get_total_asset_value")
    def test_get_estimated_target_cash(self, mock_fct, order_proposal, order_factory, cash_factory):
        order_proposal.portfolio.only_weighting = False
        order_proposal.portfolio.save()
        mock_fct.return_value = Decimal(1_000_000)  # 1 million cash
        cash = cash_factory.create(currency=order_proposal.portfolio.currency)
        order_factory.create(  # equity trade
            order_proposal=order_proposal,
            value_date=order_proposal.trade_date,
            portfolio=order_proposal.portfolio,
            weighting=Decimal("0.7"),
        )
        order_factory.create(  # cash trade
            order_proposal=order_proposal,
            value_date=order_proposal.trade_date,
            portfolio=order_proposal.portfolio,
            underlying_instrument=cash,
            weighting=Decimal("0.2"),
        )
        target_cash_position = order_proposal.get_estimated_target_cash()
        assert target_cash_position.weighting == Decimal("0.3")
        assert target_cash_position.initial_shares == Decimal(1_000_000) * Decimal("0.3")

    def test_order_proposal_update_inception_date(self, order_proposal_factory, portfolio, instrument_factory):
        # Check that if we create a prior order proposal, the instrument inception date is updated accordingly
        instrument = instrument_factory.create(inception_date=None)
        instrument.portfolios.add(portfolio)
        tp = order_proposal_factory.create(portfolio=portfolio)
        instrument.refresh_from_db()
        assert instrument.inception_date == tp.trade_date

        tp2 = order_proposal_factory.create(portfolio=portfolio, trade_date=(tp.trade_date - BDay(1)).date())
        instrument.refresh_from_db()
        assert instrument.inception_date == tp2.trade_date

    def test_get_round_lot_size(self, order_proposal, instrument):
        # without a round lot size, we expect no normalization of shares
        assert order_proposal.get_round_lot_size(Decimal("66"), instrument) == Decimal("66")
        instrument.round_lot_size = 100
        instrument.save()

        # if instrument has a round lot size different than 1, we expect different behavior based on whether shares is positive or negative
        assert order_proposal.get_round_lot_size(Decimal(66.0), instrument) == Decimal("100")
        assert order_proposal.get_round_lot_size(Decimal(-66.0), instrument) == Decimal(-66.0)
        assert order_proposal.get_round_lot_size(Decimal(-120), instrument) == Decimal(-200)

        # exchange can disable rounding based on the lot size
        instrument.exchange.apply_round_lot_size = False
        instrument.exchange.save()
        assert order_proposal.get_round_lot_size(Decimal("66"), instrument) == Decimal("66")

    def test_submit_round_lot_size(self, order_proposal, order_factory, instrument_factory):
        order_proposal.portfolio.only_weighting = False
        order_proposal.portfolio.save()
        instrument = instrument_factory.create()
        instrument.round_lot_size = 100
        instrument.save()
        trade = order_factory.create(
            underlying_instrument=instrument,
            shares=70,
            order_proposal=order_proposal,
            weighting=Decimal("1.0"),
        )
        warnings = order_proposal.submit()
        order_proposal.save()
        assert (
            len(warnings) == 1
        )  # ensure that submit returns a warning concerning the rounded trade based on the lot size
        trade.refresh_from_db()
        assert trade.shares == 100  # we expect the share to be transformed from 70 to 100 (lot size of 100)

    def test_submit_round_fractional_shares(self, order_proposal, order_factory):
        order_proposal.portfolio.only_weighting = False
        order_proposal.portfolio.save()
        trade = order_factory.create(
            shares=5.6,
            order_proposal=order_proposal,
            weighting=Decimal("1.0"),
        )
        order_proposal.submit()
        order_proposal.save()
        trade.refresh_from_db()
        assert trade.shares == 6  # we expect the fractional share to be rounded

    def test_ex_post(
        self, instrument_factory, asset_position_factory, instrument_price_factory, order_proposal_factory, portfolio
    ):
        """
        Tests the ex-post rebalancing mechanism of a portfolio with two instruments.
        Verifies that weights are correctly recalculated after submitting and approving a order proposal.
        """

        # --- Create instruments ---
        msft = instrument_factory.create(currency=portfolio.currency)
        apple = instrument_factory.create(currency=portfolio.currency)

        # --- Key dates ---
        d1 = date(2025, 6, 24)
        d2 = date(2025, 6, 25)
        d3 = date(2025, 6, 26)
        d4 = date(2025, 6, 27)

        # --- Create MSFT prices ---
        msft_p1 = instrument_price_factory.create(instrument=msft, date=d1, net_value=Decimal("10"))
        msft_p2 = instrument_price_factory.create(instrument=msft, date=d2, net_value=Decimal("8"))
        msft_p3 = instrument_price_factory.create(instrument=msft, date=d3, net_value=Decimal("12"))
        msft_p4 = instrument_price_factory.create(instrument=msft, date=d4, net_value=Decimal("15"))  # noqa

        # Calculate MSFT returns between dates
        msft_r2 = msft_p2.net_value / msft_p1.net_value - Decimal("1")  # noqa
        msft_r3 = msft_p3.net_value / msft_p2.net_value - Decimal("1")

        # --- Create Apple prices (stable) ---
        apple_p1 = instrument_price_factory.create(instrument=apple, date=d1, net_value=Decimal("100"))
        apple_p2 = instrument_price_factory.create(instrument=apple, date=d2, net_value=Decimal("100"))
        apple_p3 = instrument_price_factory.create(instrument=apple, date=d3, net_value=Decimal("100"))
        apple_p4 = instrument_price_factory.create(instrument=apple, date=d4, net_value=Decimal("100"))  # noqa

        # Apple returns (always 0 since price is stable)
        apple_r2 = apple_p2.net_value / apple_p1.net_value - Decimal("1")  # noqa
        apple_r3 = apple_p3.net_value / apple_p2.net_value - Decimal("1")

        # --- Create positions on d2 ---
        msft_a2 = asset_position_factory.create(
            portfolio=portfolio,
            underlying_quote=msft,
            date=d2,
            initial_shares=10,
            weighting=Decimal("0.44"),
        )
        apple_a2 = asset_position_factory.create(
            portfolio=portfolio,
            underlying_quote=apple,
            date=d2,
            initial_shares=1,
            weighting=Decimal("0.56"),
        )

        # Check that initial weights sum to 1
        total_weight_d2 = msft_a2.weighting + apple_a2.weighting
        assert total_weight_d2 == pytest.approx(Decimal("1.0"), abs=Decimal("1e-6"))

        # --- Calculate total portfolio return between d2 and d3 ---
        portfolio_r3 = msft_a2.weighting * (Decimal("1.0") + msft_r3) + apple_a2.weighting * (
            Decimal("1.0") + apple_r3
        )

        # --- Create positions on d3 with weights adjusted for returns ---

        # Check that weights on d2 sum to 1
        total_weight_d2 = msft_a2.weighting + apple_a2.weighting
        assert total_weight_d2 == pytest.approx(Decimal("1.0"), abs=Decimal("1e-6"))

        # --- Create a order proposal on d3 ---
        order_proposal = order_proposal_factory.create(portfolio=portfolio, trade_date=d3)
        order_proposal.reset_orders()
        # Retrieve orders for each instrument
        orders = order_proposal.get_orders()
        trade_msft = orders.get(underlying_instrument=msft)
        trade_apple = orders.get(underlying_instrument=apple)
        # Check that trade weights are initially zero
        assert trade_msft.weighting == Decimal("0")
        assert trade_apple.weighting == Decimal("0")

        msft_drifted = msft_a2.weighting * (Decimal("1.0") + msft_r3) / portfolio_r3
        apple_drifted = apple_a2.weighting * (Decimal("1.0") + apple_r3) / portfolio_r3
        # --- Adjust trade weights to target 50% each ---
        target_weight = Decimal("0.5")
        trade_msft.weighting = target_weight - msft_drifted
        trade_msft.save()

        trade_apple.weighting = target_weight - apple_drifted
        trade_apple.save()
        orders = order_proposal.get_orders()
        trade_msft = orders.get(underlying_instrument=msft)
        trade_apple = orders.get(underlying_instrument=apple)

        # --- Check drift factors and effective weights ---
        assert trade_msft.daily_return == pytest.approx(msft_r3, abs=Decimal("1e-6"))
        assert trade_apple.daily_return == pytest.approx(apple_r3, abs=Decimal("1e-6"))

        assert trade_msft._effective_weight == pytest.approx(msft_drifted, abs=Decimal("1e-6"))
        assert trade_apple._effective_weight == pytest.approx(apple_drifted, abs=Decimal("1e-6"))

        # Check that the target weight is the sum of drifted weight and adjustment
        assert trade_msft._target_weight == pytest.approx(target_weight, abs=Decimal("1e-6"))
        assert trade_apple._target_weight == pytest.approx(target_weight, abs=Decimal("1e-6"))

        # --- Submit and approve the order proposal ---
        order_proposal.submit()
        order_proposal.save()
        order_proposal.approve()
        order_proposal.apply()
        order_proposal.save()

        # Final check that weights have been updated to 50%
        assert order_proposal.portfolio.assets.get(underlying_instrument=msft).weighting == pytest.approx(
            target_weight, abs=Decimal("1e-6")
        )
        assert order_proposal.portfolio.assets.get(underlying_instrument=apple).weighting == pytest.approx(
            target_weight, abs=Decimal("1e-6")
        )

    def test_replay_reset_draft_order_proposal(
        self, instrument_factory, instrument_price_factory, order_factory, order_proposal_factory
    ):
        instrument = instrument_factory.create()
        order_proposal = order_proposal_factory.create(trade_date=date.today() - BDay(2))
        instrument_price_factory.create(instrument=instrument, date=date.today() - BDay(2))
        instrument_price_factory.create(instrument=instrument, date=date.today() - BDay(1))
        instrument_price_factory.create(instrument=instrument, date=date.today())
        trade = order_factory.create(
            underlying_instrument=instrument,
            order_proposal=order_proposal,
            weighting=1,
        )
        order_proposal.submit()
        order_proposal.approve()
        order_proposal.apply(replay=False)
        order_proposal.save()

        draft_tp = order_proposal_factory.create(portfolio=order_proposal.portfolio, trade_date=date.today() - BDay(1))
        assert not Order.objects.filter(order_proposal=draft_tp).exists()

        order_proposal.replay()

        assert Order.objects.filter(order_proposal=draft_tp).count() == 1
        assert Order.objects.get(
            order_proposal=draft_tp, underlying_instrument=trade.underlying_instrument
        ).weighting == Decimal("0")

    def test_order_submit_bellow_minimum_allowed_order_value(self, order_factory):
        order = order_factory.create(price=Decimal(1), weighting=Decimal(1), shares=Decimal(999))
        order.submit()
        order.save()
        assert order.shares == Decimal(999)
        assert order.weighting == Decimal(1)

        order.order_proposal.min_order_value = Decimal(1000)
        order.order_proposal.save()

        order.submit()
        order.save()
        assert order.shares == Decimal(0)
        assert order.weighting == Decimal(0)

    def test_reset_order_use_desired_target_weight(self, order_proposal, order_factory):
        order1 = order_factory.create(
            order_proposal=order_proposal, weighting=Decimal("0.5"), desired_target_weight=Decimal("0.7")
        )
        order2 = order_factory.create(
            order_proposal=order_proposal, weighting=Decimal("0.5"), desired_target_weight=Decimal("0.3")
        )
        order_proposal.submit()
        order_proposal.approve()
        order_proposal.apply()
        order_proposal.save()

        order1.refresh_from_db()
        order2.refresh_from_db()
        assert order1.desired_target_weight == Decimal("0.5")
        assert order2.desired_target_weight == Decimal("0.5")
        assert order1.weighting == Decimal("0.5")
        assert order2.weighting == Decimal("0.5")

        order1.desired_target_weight = Decimal("0.7")
        order2.desired_target_weight = Decimal("0.3")
        order1.save()
        order2.save()

        order_proposal.reset_orders(use_desired_target_weight=True)
        order1.refresh_from_db()
        order2.refresh_from_db()
        assert order1.weighting == Decimal("0.7")
        assert order2.weighting == Decimal("0.3")

    def test_reset_order_proposal_keeps_target_cash_weight(self, order_factory, order_proposal_factory):
        order_proposal = order_proposal_factory.create(
            total_cash_weight=Decimal("0.02")
        )  # create a OP with total cash weight of 2%

        # create orders that total weight account for only 50%
        order_factory.create(order_proposal=order_proposal, weighting=Decimal("0.3"))
        order_factory.create(order_proposal=order_proposal, weighting=Decimal("0.2"))

        order_proposal.reset_orders()
        assert order_proposal.get_orders().aggregate(s=Sum("target_weight"))["s"] == Decimal(
            "0.98"
        ), "The total target weight leftover does not equal the stored total cash weight"

    def test_convert_to_portfolio_always_100percent(self, order_proposal, order_factory):
        o1 = order_factory.create(order_proposal=order_proposal, weighting=Decimal("0.5"))
        o2 = order_factory.create(order_proposal=order_proposal, weighting=Decimal("0.3"))

        portfolio = order_proposal.convert_to_portfolio()
        assert portfolio.positions_map[o1.underlying_instrument.id].weighting == Decimal("0.5")
        assert portfolio.positions_map[o2.underlying_instrument.id].weighting == Decimal("0.3")
        assert portfolio.positions_map[order_proposal.cash_component.id].weighting == Decimal("0.2")
