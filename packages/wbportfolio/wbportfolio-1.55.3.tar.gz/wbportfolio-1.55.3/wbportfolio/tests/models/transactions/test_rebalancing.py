from datetime import date
from decimal import Decimal

import pandas as pd
import pytest
from django.core.exceptions import ValidationError
from pandas._libs.tslibs.offsets import BDay

from wbportfolio.models import AssetPosition, OrderProposal


@pytest.mark.django_db
class TestRebalancingModel:
    def test_get_target_portfolio(
        self, rebalancing_model, portfolio, weekday, asset_position_factory, instrument_price_factory
    ):
        trade_date = (weekday + BDay(1)).date()
        with pytest.raises(ValidationError):  # trigger value error because rebalancing not valid (no position yet)
            rebalancing_model.get_target_portfolio(portfolio, trade_date, weekday)
        a1 = asset_position_factory(weighting=0.7, portfolio=portfolio, date=weekday)
        a2 = asset_position_factory(weighting=0.3, portfolio=portfolio, date=weekday)
        instrument_price_factory.create(instrument=a1.underlying_quote, date=trade_date)
        target_portfolio = rebalancing_model.get_target_portfolio(portfolio, (weekday + BDay(1)).date(), weekday)
        target_positions = target_portfolio.positions_map
        assert target_positions[a1.underlying_instrument.id].weighting == 0.5
        assert target_positions[a2.underlying_instrument.id].weighting == 0.5


@pytest.mark.django_db
class TestRebalancer:
    def test_activation_date(self, rebalancer_factory, asset_position):
        r1 = rebalancer_factory.create(portfolio=asset_position.portfolio)
        assert r1.activation_date == asset_position.date

        r2 = rebalancer_factory.create()
        r2.activation_date = date.today()

    def test_is_valid(self, weekday, rebalancer_factory):
        # default frequency is monthly

        first_of_the_month = weekday.replace(day=1)
        rebalancer = rebalancer_factory.create(frequency="RRULE:FREQ=MONTHLY;", activation_date=first_of_the_month)
        assert rebalancer.is_valid(first_of_the_month)
        if weekday.day != 1:
            assert not rebalancer.is_valid(weekday)

    def test_evaluate_rebalancing(
        self, weekday, rebalancer_factory, asset_position_factory, instrument_factory, instrument_price_factory
    ):
        rebalancer = rebalancer_factory.create(apply_order_proposal_automatically=True)
        trade_date = (weekday + BDay(1)).date()

        i1 = instrument_factory.create()
        i2 = instrument_factory.create()
        instrument_price_factory.create(instrument=i1, date=weekday)
        instrument_price_factory.create(instrument=i1, date=trade_date)
        instrument_price_factory.create(instrument=i2, date=weekday)
        instrument_price_factory.create(instrument=i2, date=trade_date)

        a1 = asset_position_factory.create(
            portfolio=rebalancer.portfolio, date=weekday, weighting=0.7, underlying_instrument=i1
        )
        a2 = asset_position_factory.create(
            portfolio=rebalancer.portfolio, date=weekday, weighting=0.3, underlying_instrument=i2
        )
        order_proposal = rebalancer.evaluate_rebalancing(trade_date)
        assert order_proposal.orders.count() == 2
        assert order_proposal.status == OrderProposal.Status.APPLIED
        assert AssetPosition.objects.get(
            portfolio=rebalancer.portfolio, date=trade_date, underlying_quote=a1.underlying_instrument
        ).weighting == Decimal(0.5)
        assert AssetPosition.objects.get(
            portfolio=rebalancer.portfolio, date=trade_date, underlying_quote=a2.underlying_instrument
        ).weighting == Decimal(0.5)

    def test_get_rrule(self, weekday, rebalancer_factory):
        # default frequency is monthly

        first_of_the_month = weekday.replace(day=1)
        until = first_of_the_month.replace(year=first_of_the_month.year + 1)
        rebalancer = rebalancer_factory.create(frequency="RRULE:FREQ=MONTHLY;", activation_date=first_of_the_month)

        valid_dates = set(rebalancer.get_rrule(until))
        assert valid_dates
        assert set(valid_dates) == set(pd.date_range(start=first_of_the_month, end=until, freq="MS"))
