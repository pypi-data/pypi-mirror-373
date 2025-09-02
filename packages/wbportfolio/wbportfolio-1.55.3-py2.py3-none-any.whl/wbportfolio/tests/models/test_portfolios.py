import random
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

import pandas as pd
import pytest
from django.db.models import F, Sum
from django.forms.models import model_to_dict
from faker import Faker
from pandas.tseries.offsets import BDay
from psycopg.types.range import DateRange
from wbcore.contrib.currency.factories import CurrencyFactory
from wbcore.contrib.geography.factories import CountryFactory

from wbportfolio.models import (
    AssetPosition,
    Portfolio,
    PortfolioInstrumentPreferredClassificationThroughModel,
    PortfolioPortfolioThroughModel,
    Trade,
)

from ...models.portfolio import update_portfolio_after_investable_universe
from .utils import PortfolioTestMixin

fake = Faker()


@pytest.mark.django_db
class TestPortfolioModel(PortfolioTestMixin):
    def test_init(self, portfolio):
        assert portfolio.id is not None

    def test_str(self, portfolio):
        assert str(portfolio) == f"{portfolio.id:06}: {portfolio.name}"

    def test_get_assets(self, portfolio, product, cash, asset_position_factory):
        asset_position_factory.create_batch(4, portfolio=portfolio, underlying_instrument=product)
        asset_position_factory.create(portfolio=portfolio, underlying_instrument=cash)
        assert portfolio._get_assets().count() == 5
        assert portfolio._get_assets(with_cash=False).count() == 4

    def test_get_earliest_asset_position_date(self, portfolio, asset_position_factory):
        asset_position_factory.create_batch(5, portfolio=portfolio)
        assert portfolio.get_earliest_asset_position_date() == AssetPosition.objects.earliest("date").date

    def test_get_latest_asset_position_date(self, portfolio, asset_position_factory):
        asset_position_factory.create_batch(5, portfolio=portfolio)
        assert portfolio.get_latest_asset_position_date() == AssetPosition.objects.latest("date").date

    def test_get_holding(self, portfolio_factory, asset_position_factory, equity, weekday):
        portfolio = portfolio_factory.create()
        asset_position_factory.create(portfolio=portfolio, date=weekday, initial_price=1, initial_shares=10)
        a2 = asset_position_factory.create(
            portfolio=portfolio,
            date=weekday,
            initial_price=1,
            initial_shares=40,
            underlying_instrument=equity,
            portfolio_created=portfolio_factory.create(),
        )
        asset_position_factory.create(portfolio=portfolio, date=weekday, initial_price=1, initial_shares=50)
        a4 = asset_position_factory.create(
            portfolio=portfolio,
            date=weekday,
            initial_price=1,
            initial_shares=30,
            underlying_instrument=equity,
            portfolio_created=portfolio_factory.create(),
        )
        assert (
            portfolio.get_holding(weekday)
            .filter(underlying_instrument=equity)
            .values_list("total_value_fx_portfolio", flat=True)[0]
            == a2._total_value_fx_portfolio + a4._total_value_fx_portfolio
        )

    def test_get_groupeby(self, portfolio, asset_position_factory, weekday):
        a1 = asset_position_factory.create(
            portfolio=portfolio, date=weekday, initial_price=1, initial_shares=10, weighting=0.1
        )
        asset_position_factory.create(
            portfolio=portfolio, date=weekday, initial_price=1, initial_shares=40, weighting=0.4
        )
        asset_position_factory.create(
            portfolio=portfolio, date=weekday, initial_price=1, initial_shares=50, weighting=0.5
        )

        def groupby(qs, **kwargs):
            return qs.annotate(aggregated_title=F("underlying_instrument__ticker"))

        df = portfolio._get_groupedby_df(groupby, weekday)
        assert df.aggregated_title[2] == a1.underlying_instrument.ticker

    def test_get_geographical_breakdown(self, portfolio, asset_position_factory, equity_factory, weekday):
        c1 = CountryFactory.create()
        c2 = CountryFactory.create()
        asset_position_factory.create(
            portfolio=portfolio, underlying_instrument=equity_factory.create(country=c1), date=weekday
        )
        asset_position_factory.create(
            portfolio=portfolio, underlying_instrument=equity_factory.create(country=c1), date=weekday
        )
        asset_position_factory.create(
            portfolio=portfolio, underlying_instrument=equity_factory.create(country=c2), date=weekday
        )
        assert portfolio.get_geographical_breakdown(weekday).shape[0] == 2

    def test_get_currency_exposure(self, portfolio, asset_position_factory, equity_factory, weekday):
        a1 = asset_position_factory.create(
            portfolio=portfolio,
            underlying_instrument=equity_factory.create(currency=CurrencyFactory.create()),
            date=weekday,
        )
        asset_position_factory.create(
            portfolio=portfolio, underlying_instrument=equity_factory.create(), currency=a1.currency, date=weekday
        )
        asset_position_factory.create(
            portfolio=portfolio,
            underlying_instrument=equity_factory.create(currency=CurrencyFactory.create()),
            date=weekday,
        )
        assert portfolio.get_currency_exposure(weekday).shape[0] == 2

    def test_get_equity_market_cap_distribution(
        self, portfolio, equity, asset_position_factory, instrument_price_factory
    ):
        price = instrument_price_factory.create(instrument=equity)
        asset_position_factory.create_batch(10, portfolio=portfolio, date=price.date, underlying_instrument=equity)

        assert not portfolio.get_equity_market_cap_distribution(price.date).empty

    def test_get_get_equity_liquidity(self, portfolio, asset_position_factory, equity_factory, weekday):
        asset_position_factory.create_batch(
            10, portfolio=portfolio, date=weekday, underlying_instrument=equity_factory.create()
        )
        assert not portfolio.get_equity_liquidity(weekday).empty

    def test_get_industry_exposure(
        self, portfolio, asset_position_factory, weekday, classification_group, classification_factory, equity_factory
    ):
        parent_classification = classification_factory.create(group=classification_group)
        asset_position_factory.create_batch(
            10,
            portfolio=portfolio,
            date=weekday,
            underlying_instrument=equity_factory.create(
                classifications=[
                    classification_factory.create(group=classification_group, parent=parent_classification)
                ]
            ),
        )
        assert not portfolio.get_industry_exposure(weekday).empty

    def test_get_asset_allocation(self, portfolio, equity, cash, index_factory, asset_position_factory, weekday):
        index = index_factory.create(is_cash=True)
        asset_position_factory.create_batch(10, portfolio=portfolio, date=weekday, underlying_instrument=equity)
        asset_position_factory.create(portfolio=portfolio, date=weekday, underlying_instrument=index)
        asset_position_factory.create(portfolio=portfolio, date=weekday, underlying_instrument=cash)
        assert portfolio.get_asset_allocation(weekday).shape[0] == 2

    def test_get_portfolio_contribution_df(self, portfolio, asset_position_factory, instrument_factory, weekday):
        i1 = instrument_factory.create()
        i2 = instrument_factory.create()
        end = (weekday + BDay(1)).date()
        asset_position_factory.create(
            portfolio=portfolio,
            underlying_instrument=i1,
            date=weekday,
            initial_price=100,
            initial_shares=10,
            initial_currency_fx_rate=1,
            weighting=0.25,
        )
        asset_position_factory.create(
            portfolio=portfolio,
            underlying_instrument=i2,
            date=weekday,
            initial_price=100,
            initial_shares=30,
            initial_currency_fx_rate=1,
            weighting=0.75,
        )
        asset_position_factory.create(
            portfolio=portfolio,
            underlying_instrument=i1,
            date=end,
            initial_price=120,
            initial_shares=10,
            initial_currency_fx_rate=1,
            weighting=0.33,
        )
        asset_position_factory.create(
            portfolio=portfolio,
            underlying_instrument=i2,
            date=end,
            initial_price=80,
            initial_shares=30,
            initial_currency_fx_rate=1,
            weighting=0.66,
        )
        res = portfolio.get_portfolio_contribution_df(weekday, end)
        assert 0.05 == pytest.approx(res.contribution_total[0])
        assert -0.15 == pytest.approx(res.contribution_total[1])
        assert 0.2 == pytest.approx(res.performance_total[0])
        assert -0.2 == pytest.approx(res.performance_total[1])

    def test_get_longshort_distribution(
        self, asset_position_factory, portfolio_factory, cash, index_factory, equity_factory, weekday
    ):
        portfolio = portfolio_factory.create()

        ind1 = index_factory.create(is_cash=False)
        short_underlying_portfolio = portfolio_factory.create()
        ind1.portfolios.add(short_underlying_portfolio)

        ind2 = index_factory.create(is_cash=False)
        long_underlying_portfolio = portfolio_factory.create()
        ind2.portfolios.add(long_underlying_portfolio)

        asset_position_factory.create(date=weekday, portfolio=portfolio, weighting=-1.0, underlying_instrument=ind1)
        short_p1 = asset_position_factory.create(
            date=weekday, portfolio=short_underlying_portfolio, underlying_instrument=cash
        )
        short_p2 = asset_position_factory.create(
            date=weekday,
            portfolio=short_underlying_portfolio,
            underlying_instrument=equity_factory.create(is_cash=False),
            weighting=1 - short_p1.weighting,
        )

        asset_position_factory.create(date=weekday, portfolio=portfolio, weighting=1.0, underlying_instrument=ind2)
        long_p1 = asset_position_factory.create(
            date=weekday,
            portfolio=long_underlying_portfolio,
            underlying_instrument=equity_factory.create(is_cash=False),
        )
        long_p2 = asset_position_factory.create(
            date=weekday,
            portfolio=long_underlying_portfolio,
            underlying_instrument=equity_factory.create(is_cash=False),
            weighting=1 - long_p1.weighting,
        )

        res = portfolio.get_longshort_distribution(weekday)
        total_weight = abs(short_p2.weighting) + long_p1.weighting + long_p2.weighting
        assert Decimal(res.weighting[0]) == pytest.approx(
            (long_p1.weighting + long_p2.weighting) / total_weight, rel=Decimal(1e-4)
        )
        assert Decimal(res.weighting[1]) == pytest.approx((abs(short_p2.weighting)) / total_weight, rel=Decimal(1e-4))

    @patch.object(Portfolio, "estimate_net_asset_values", autospec=True)
    def test_change_at_date(self, mock_estimate_net_asset_values, asset_position_factory, portfolio, weekday):
        a1 = asset_position_factory.create(portfolio=portfolio, date=weekday, weighting=Decimal("0.1"))
        a2 = asset_position_factory.create(portfolio=portfolio, date=weekday, weighting=Decimal("0.3"))
        a3 = asset_position_factory.create(portfolio=portfolio, date=weekday, weighting=Decimal("0.5"))

        portfolio.change_at_date(weekday, fix_quantization=True)

        cash_pos = portfolio.assets.get(date=weekday, portfolio=portfolio, underlying_quote=portfolio.cash_component)
        assert cash_pos.weighting == Decimal("1.0") - (a1.weighting + a2.weighting + a3.weighting)

        mock_estimate_net_asset_values.assert_called_once_with(
            portfolio, (weekday + BDay(1)).date(), analytic_portfolio=None
        )

    @patch.object(Portfolio, "compute_lookthrough", autospec=True)
    def test_change_at_date_with_dependent_portfolio(
        self,
        mock_compute_lookthrough,
        portfolio_factory,
        product_factory,
        instrument_price_factory,
        customer_trade_factory,
        weekday,
    ):
        base_portfolio = portfolio_factory.create()

        dependent_portfolio = portfolio_factory.create(is_lookthrough=True)
        dependent_portfolio.depends_on.add(base_portfolio)
        base_portfolio.change_at_date(weekday)

        mock_compute_lookthrough.assert_called_once_with(
            dependent_portfolio,
            weekday,
        )

    def test_is_active_at_date(
        self,
        portfolio,
    ):
        # a portfolio is active at a date if it is active or the deletion time is greater than that date AND if there is instruments attached, at least one instrument is still active as well

        assert portfolio.is_active
        assert portfolio.is_active_at_date(fake.date_object())

        portfolio.delete()  # soft deletion
        assert portfolio.is_active_at_date(fake.past_date())
        assert not portfolio.is_active_at_date(fake.future_date())

    def test_is_active_at_date_with_instruments(
        self,
        portfolio,
        instrument_factory,
    ):
        i1 = instrument_factory.create(inception_date=date.today(), delisted_date=None)
        i2 = instrument_factory.create(inception_date=date.today(), delisted_date=None)
        portfolio.instruments.add(i1)
        portfolio.instruments.add(i2)

        assert i1.is_active_at_date(fake.future_date())
        assert i2.is_active_at_date(fake.future_date())
        assert portfolio.is_active_at_date(fake.future_date())

        i1.delisted_date = date.today()
        i1.save()
        assert portfolio.is_active_at_date(fake.future_date())

        i2.delisted_date = date.today()
        i2.save()
        assert not portfolio.is_active_at_date(
            fake.date_object()
        )  # as no instrument is active, even if the portfolio is active at any date, the portfolio is consiodered inactive

    def test_propagate_or_update_assets(
        self, portfolio, asset_position_factory, instrument_factory, instrument_price_factory, weekday
    ):
        next_day = (weekday + BDay(1)).date()

        i1 = instrument_factory.create(currency=portfolio.currency)
        price1_0 = instrument_price_factory.create(instrument=i1, date=(weekday - BDay(1)).date())  # noqa
        price1_1 = instrument_price_factory.create(instrument=i1, date=weekday)
        price1_2 = instrument_price_factory.create(instrument=i1, date=next_day)
        i2 = instrument_factory.create(currency=portfolio.currency)
        price2_0 = instrument_price_factory.create(instrument=i2, date=(weekday - BDay(1)).date())  # noqa
        price2_1 = instrument_price_factory.create(instrument=i2, date=weekday)
        price2_2 = instrument_price_factory.create(instrument=i2, date=next_day)
        i3 = instrument_factory.create(currency=portfolio.currency)
        price3_0 = instrument_price_factory.create(instrument=i3, date=(weekday - BDay(1)).date())  # noqa
        price3_1 = instrument_price_factory.create(instrument=i3, date=weekday)
        price3_2 = instrument_price_factory.create(instrument=i3, date=next_day)
        i4 = instrument_factory.create(currency=portfolio.currency)

        a1_1 = asset_position_factory.create(
            portfolio=portfolio,
            underlying_instrument=i1,
            underlying_quote_price=price1_1,
            date=weekday,
            weighting=Decimal(0.4),
        )
        a2_1 = asset_position_factory.create(
            portfolio=portfolio,
            underlying_instrument=i2,
            underlying_quote_price=price2_1,
            date=weekday,
            weighting=Decimal(0.3),
        )
        a3_1 = asset_position_factory.create(
            portfolio=portfolio,
            underlying_instrument=i3,
            underlying_quote_price=price3_1,
            date=weekday,
            weighting=Decimal(0.2),
        )
        a4_1 = asset_position_factory.create(  # noqa
            portfolio=portfolio,
            underlying_instrument=i4,
            underlying_quote_price=None,  # the price won't be created automatically by the fixture, we expect this position to be removed from the propagated portfolio
            date=weekday,
            weighting=Decimal(0.1),
        )

        # Test basic output
        portfolio.propagate_or_update_assets(weekday, next_day)
        a1_2 = AssetPosition.objects.get(portfolio=portfolio, date=next_day, underlying_instrument=i1)
        a2_2 = AssetPosition.objects.get(portfolio=portfolio, date=next_day, underlying_instrument=i2)
        a3_2 = AssetPosition.objects.get(portfolio=portfolio, date=next_day, underlying_instrument=i3)
        with pytest.raises(AssetPosition.DoesNotExist):
            AssetPosition.objects.get(portfolio=portfolio, date=next_day, underlying_instrument=i4)

        assert a1_2.initial_price == pytest.approx(price1_2.net_value, rel=Decimal(1e-4))
        assert a2_2.initial_price == pytest.approx(price2_2.net_value, rel=Decimal(1e-4))
        assert a3_2.initial_price == pytest.approx(price3_2.net_value, rel=Decimal(1e-4))

        contrib_1 = a1_1.weighting * price1_2.net_value / price1_1.net_value
        contrib_2 = a2_1.weighting * price2_2.net_value / price2_1.net_value
        contrib_3 = a3_1.weighting * price3_2.net_value / price3_1.net_value
        assert a1_2.weighting == pytest.approx(contrib_1 / (contrib_1 + contrib_2 + contrib_3), rel=Decimal(1e4))
        assert a2_2.weighting == pytest.approx(contrib_2 / (contrib_1 + contrib_2 + contrib_3), rel=Decimal(1e4))
        assert a3_2.weighting == pytest.approx(contrib_3 / (contrib_1 + contrib_2 + contrib_3), rel=Decimal(1e4))

        # # Test if a deleted assets is kept if delete_existing_assets is set to True
        # a1_1.delete()
        # portfolio.propagate_or_update_assets(weekday, next_day, delete_existing_assets=True)
        # with pytest.raises(AssetPosition.DoesNotExist):
        #     a1_2.refresh_from_db()

        # a2_2 = AssetPosition.objects.get(portfolio=portfolio, date=next_day, underlying_instrument=i2)
        # a3_2 = AssetPosition.objects.get(portfolio=portfolio, date=next_day, underlying_instrument=i3)
        # assert a2_2
        # assert a3_2

        # Test that we don't do anything on target portfolio because there is a non estimated position
        a2_2.is_estimated = False
        a2_2.save()
        portfolio.propagate_or_update_assets(weekday, next_day)
        a2_2_weighting = a2_2.weighting
        a3_2_weighting = a3_2.weighting
        a2_2.refresh_from_db()
        a3_2.refresh_from_db()

        assert a2_2.weighting == a2_2_weighting
        assert a3_2.weighting == a3_2_weighting

    def test_propagate_or_update_assets_active_states(
        self, weekday, active_product, asset_position_factory, instrument_price_factory, instrument
    ):
        next_day = (weekday + BDay(1)).date()

        portfolio = active_product.portfolio
        portfolio.currency = instrument.currency
        portfolio.save()

        instrument_price_factory.create(date=(weekday - BDay(1)).date(), instrument=instrument)
        a1 = asset_position_factory.create(
            portfolio=portfolio, date=weekday, underlying_instrument=instrument, currency=instrument.currency
        )
        instrument_price_factory.create(date=next_day, instrument=instrument)

        active_product.delisted_date = weekday
        active_product.save()
        # Test1: test if unactive portfolio keep having the to date assets. (asset found at next day are suppose to be deleted when the portfolio is non active at the from date)
        portfolio.propagate_or_update_assets(weekday, next_day)
        assert portfolio.assets.filter(date=next_day).exists() is False

        # Activate product
        active_product.delisted_date = None
        active_product.save()

        # Expect proper creation
        portfolio.propagate_or_update_assets(weekday, next_day)
        a_future = AssetPosition.objects.get(portfolio=portfolio, date=next_day)

        # Test if only estimated update existing pos,

        portfolio.propagate_or_update_assets(weekday, next_day)
        initial_shares = a1.initial_shares

        # Test that estimated shares keep being updated
        portfolio.only_weighting = False
        portfolio.save()
        a1.initial_shares *= 2
        a1.save()
        portfolio.propagate_or_update_assets(weekday, next_day)
        a_future = AssetPosition.objects.get(portfolio=portfolio, date=next_day)
        assert a_future.initial_shares == initial_shares * 2

        # Test that non-estimated shares are not being updated
        updated_fields = ["initial_currency_fx_rate", "weighting", "initial_price", "initial_shares"]
        for field in updated_fields:
            setattr(a1, field, getattr(a1, field) * 2)
        a1.save()
        a_future_copy = model_to_dict(a_future)
        a_future.is_estimated = False
        a_future.save()
        portfolio.propagate_or_update_assets(weekday, next_day)
        a_future.refresh_from_db()
        for field in updated_fields:
            assert getattr(a_future, field) == a_future_copy[field]

        # Test active (from) portfolio but not active (to) create a zero weight position
        active_product.delisted_date = next_day
        active_product.save()

        a_future.is_estimated = True
        a_future.save()
        portfolio.propagate_or_update_assets(weekday, next_day)
        with pytest.raises(AssetPosition.DoesNotExist):
            AssetPosition.objects.get(portfolio=portfolio, date=next_day)
        # assert a_future.weighting == 0

    def test_update_preferred_classification_per_instrument(
        self, portfolio, asset_position_factory, equity_factory, classification_factory, classification_group_factory
    ):
        primary_group = classification_group_factory.create(is_primary=True)
        other_group = classification_group_factory.create(is_primary=False)
        c1 = classification_factory.create(group=other_group)
        c2_primary = classification_factory.create(group=primary_group)
        c2_secondary = classification_factory.create(group=other_group)
        c3_1 = classification_factory.create(group=other_group)
        c3_2 = classification_factory.create(group=other_group)

        # One classification to this instrument, we expect the relationship to be filled automatically
        i1 = equity_factory.create(classifications=[c1])
        # One classification "Primary" and one "other" to this instrument, we expect the relationship to be filled automatically
        i2 = equity_factory.create(classifications=[c2_secondary, c2_primary])
        # Two non-primary classifications to this instrument, we expect the relationship to not be filled with the classification automatically (created though)
        i3 = equity_factory.create(classifications=[c3_2, c3_1])
        asset_position_factory.create(portfolio=portfolio, underlying_instrument=i1)
        a2 = asset_position_factory.create(portfolio=portfolio, underlying_instrument=i2)
        a3 = asset_position_factory.create(portfolio=portfolio, underlying_instrument=i3)

        assert not portfolio.preferred_instrument_classifications.exists()
        portfolio.update_preferred_classification_per_instrument()
        res1 = PortfolioInstrumentPreferredClassificationThroughModel.objects.get(
            portfolio=portfolio, classification=c1, instrument=i1, classification_group=other_group
        )
        res2 = PortfolioInstrumentPreferredClassificationThroughModel.objects.get(
            portfolio=portfolio, classification=c2_secondary, instrument=i2, classification_group=other_group
        )
        res3 = PortfolioInstrumentPreferredClassificationThroughModel.objects.get(
            portfolio=portfolio, classification=None, instrument=i3, classification_group=None
        )

        assert not PortfolioInstrumentPreferredClassificationThroughModel.objects.exclude(
            id__in=[res1.id, res2.id, res3.id]
        ).exists()

        # We delete portfolio positions and retrigger the function to check that the leftovers relationship are indeed removed
        a3.delete()
        a2.delete()
        portfolio.update_preferred_classification_per_instrument()
        with pytest.raises(PortfolioInstrumentPreferredClassificationThroughModel.DoesNotExist):
            res3.refresh_from_db()
        with pytest.raises(PortfolioInstrumentPreferredClassificationThroughModel.DoesNotExist):
            res2.refresh_from_db()
        res1.refresh_from_db()
        assert res1

    def test_get_total_asset_under_management(
        self, portfolio_factory, customer_trade_factory, instrument_factory, instrument_price_factory, weekday
    ):
        portfolio = portfolio_factory.create()
        i1 = instrument_factory.create()
        i2 = instrument_factory.create()
        previous_day = (weekday - BDay(5)).date()
        price11 = instrument_price_factory.create(instrument=i1, date=weekday, calculated=False)
        price12 = instrument_price_factory.create(instrument=i1, date=previous_day, calculated=False)
        price2 = instrument_price_factory.create(instrument=i2, date=weekday, calculated=False)

        # "noise" trades
        pending_customer_trade_i1 = customer_trade_factory.create(  # noqa
            portfolio=portfolio, transaction_date=weekday, underlying_instrument=i1, pending=True
        )
        marked_for_deletion_customer_trade_i1 = customer_trade_factory.create(  # noqa
            portfolio=portfolio, transaction_date=weekday, underlying_instrument=i1, marked_for_deletion=True
        )

        # valid trade for two different instrument but within the same portfolio
        trade_11 = customer_trade_factory.create(
            portfolio=portfolio, transaction_date=weekday, underlying_instrument=i1
        )
        trade_12 = customer_trade_factory.create(
            portfolio=portfolio, transaction_date=previous_day, underlying_instrument=i1
        )
        trade_2 = customer_trade_factory.create(
            portfolio=portfolio, transaction_date=weekday, underlying_instrument=i2
        )

        assert (
            portfolio.get_total_asset_under_management(weekday)
            == price11.net_value * (trade_11.shares + trade_12.shares) + price2.net_value * trade_2.shares
        )
        assert portfolio.get_total_asset_under_management(previous_day) == price12.net_value * trade_12.shares
        assert portfolio.get_total_asset_under_management(previous_day - BDay(1)) == Decimal(0)

    def test_tracked_object(self, portfolio, asset_position_factory):
        assert not Portfolio.tracked_objects.exists()

        asset_position_factory.create(portfolio=portfolio)
        assert set(Portfolio.tracked_objects.all()) == {
            portfolio,
        }

        portfolio.is_tracked = False
        portfolio.save()
        assert portfolio.is_manageable is True
        assert Portfolio.tracked_objects.exists()

        portfolio.is_manageable = False
        portfolio.save()
        assert not Portfolio.tracked_objects.exists()

    def test_is_invested_at_date(self, portfolio_factory):
        portfolio = portfolio_factory.create(invested_timespan=DateRange(date(2024, 1, 2), date(2024, 1, 3)))
        assert portfolio.is_invested_at_date(date(2024, 1, 1)) is False
        assert portfolio.is_invested_at_date(date(2024, 1, 2)) is True
        assert portfolio.is_invested_at_date(date(2024, 1, 3)) is False

        assert set(Portfolio.objects.filter_invested_at_date(date(2024, 1, 1))) == set()
        assert set(Portfolio.objects.filter_invested_at_date(date(2024, 1, 2))) == {portfolio}
        assert set(Portfolio.objects.filter_invested_at_date(date(2024, 1, 1))) == set()

    @patch.object(Portfolio, "get_total_asset_under_management", autospec=True)
    def test_compute_lookthrough(
        self,
        mock_fct,
        active_product,
        weekday,
        portfolio_factory,
        index_factory,
        equity_factory,
        asset_position_factory,
        trade_factory,
        instrument_price_factory,
        instrument_portfolio_through_model_factory,
    ):
        root_index = index_factory.create()
        root_index_portfolio = portfolio_factory.create()
        root_index.portfolios.add(root_index_portfolio)

        index1 = index_factory.create()
        index1_portfolio = portfolio_factory.create()
        index1.portfolios.add(index1_portfolio)

        a1 = asset_position_factory.create(
            underlying_instrument=index1,
            portfolio=root_index_portfolio,
            weighting=0.6,
            initial_shares=None,
            initial_price=100,
            date=weekday,
        )

        index2 = index_factory.create()
        index2_portfolio = portfolio_factory.create()
        index2.portfolios.add(index2_portfolio)

        a2 = asset_position_factory.create(
            underlying_instrument=index2,
            portfolio=root_index_portfolio,
            weighting=0.4,
            initial_shares=None,
            initial_price=100,
            date=weekday,
        )

        a1_1 = asset_position_factory.create(
            underlying_instrument=equity_factory.create(),
            portfolio=index1_portfolio,
            weighting=0.2,
            initial_shares=None,
            initial_price=100,
            date=weekday,
        )
        a2_1 = asset_position_factory.create(
            underlying_instrument=equity_factory.create(),
            portfolio=index1_portfolio,
            weighting=0.3,
            initial_shares=None,
            initial_price=100,
            date=weekday,
        )
        a3_1 = asset_position_factory.create(
            underlying_instrument=equity_factory.create(),
            portfolio=index1_portfolio,
            weighting=0.5,
            initial_shares=None,
            initial_price=100,
            date=weekday,
        )

        a1_2 = asset_position_factory.create(
            underlying_instrument=equity_factory.create(),
            portfolio=index2_portfolio,
            weighting=0.7,
            initial_shares=None,
            initial_price=100,
            date=weekday,
        )
        a2_2 = asset_position_factory.create(
            underlying_instrument=equity_factory.create(),
            portfolio=index2_portfolio,
            weighting=0.3,
            initial_shares=None,
            initial_price=100,
            date=weekday,
        )

        product_base_portfolio = active_product.primary_portfolio
        product_portfolio = portfolio_factory.create(is_lookthrough=True, only_weighting=True)
        instrument_portfolio_through_model_factory.create(instrument=active_product, portfolio=product_portfolio)
        trade_factory.create(
            underlying_instrument=active_product,
            transaction_date=weekday,
            transaction_subtype=Trade.Type.SUBSCRIPTION,
            shares=100,
        )

        product_portfolio.depends_on.add(root_index_portfolio)

        instrument_portfolio_through_model_factory.create(instrument=active_product, portfolio=product_portfolio)

        instrument_price_factory.create(instrument=active_product, date=weekday)
        trade_factory.create(
            underlying_instrument=active_product,
            portfolio=product_base_portfolio,
            transaction_date=weekday,
            shares=1000,
            transaction_subtype="SUBSCRIPTION",
        )

        product_portfolio.compute_lookthrough(weekday)
        assert product_portfolio.assets.filter(date=weekday).count() == 5
        assert float(a1_1.weighting) * float(a1.weighting) == pytest.approx(
            float(
                product_portfolio.assets.filter(
                    portfolio_created=index1_portfolio,
                    underlying_instrument=a1_1.underlying_instrument,
                    date=weekday,
                )
                .first()
                .weighting
            )
        )
        assert float(a2_1.weighting) * float(a1.weighting) == pytest.approx(
            float(
                product_portfolio.assets.filter(
                    portfolio_created=index1_portfolio,
                    underlying_instrument=a2_1.underlying_instrument,
                    date=weekday,
                )
                .first()
                .weighting
            )
        )
        assert float(a3_1.weighting) * float(a1.weighting) == pytest.approx(
            float(
                product_portfolio.assets.filter(
                    portfolio_created=index1_portfolio,
                    underlying_instrument=a3_1.underlying_instrument,
                    date=weekday,
                )
                .first()
                .weighting
            )
        )
        assert float(a1_2.weighting) * float(a2.weighting) == pytest.approx(
            float(
                product_portfolio.assets.filter(
                    portfolio_created=index2_portfolio,
                    underlying_instrument=a1_2.underlying_instrument,
                    date=weekday,
                )
                .first()
                .weighting
            )
        )
        assert float(a2_2.weighting) * float(a2.weighting) == pytest.approx(
            float(
                product_portfolio.assets.filter(
                    portfolio_created=index2_portfolio,
                    underlying_instrument=a2_2.underlying_instrument,
                    date=weekday,
                )
                .first()
                .weighting
            )
        )
        assert Decimal(1.0) == pytest.approx(product_portfolio.assets.aggregate(s=Sum("weighting"))["s"])

        product_portfolio.only_weighting = False
        product_portfolio.save()
        mock_fct.return_value = Decimal(1_000_000)
        product_portfolio.compute_lookthrough(weekday)
        position = product_portfolio.assets.get(
            portfolio_created=index1_portfolio,
            underlying_instrument=a1_1.underlying_instrument,
            date=weekday,
        )
        assert position.initial_shares == (position.weighting * Decimal(1_000_000)) / (
            position.initial_price * position.initial_currency_fx_rate
        )

    def test_estimate_net_asset_values(
        self,
        weekday,
        equity_factory,
        product_factory,
        asset_position_factory,
        instrument_price_factory,
        trade_factory,
    ):
        while weekday.weekday() in [5, 6]:
            weekday += timedelta(days=1)

        previous_sync_date = weekday - timedelta(days=1)
        while previous_sync_date.weekday() in [5, 6]:
            previous_sync_date -= timedelta(days=1)

        product = product_factory.create(inception_date=weekday - timedelta(days=1), delisted_date=None)
        portfolio = product.portfolio

        trade_factory.create(
            underlying_instrument=product,
            portfolio=portfolio,
            transaction_date=previous_sync_date,
            shares=1000,
            transaction_subtype="SUBSCRIPTION",
        )

        e1 = equity_factory.create()
        pe1_1 = instrument_price_factory.create(instrument=e1, date=previous_sync_date)
        pe1_2 = instrument_price_factory.create(instrument=e1, date=weekday)
        e2 = equity_factory.create()
        pe2_1 = instrument_price_factory.create(instrument=e2, date=previous_sync_date)
        pe2_2 = instrument_price_factory.create(instrument=e2, date=weekday)
        e3 = equity_factory.create()
        pe3_1 = instrument_price_factory.create(instrument=e3, date=previous_sync_date)
        pe3_2 = instrument_price_factory.create(instrument=e3, date=weekday)

        a1_1 = asset_position_factory.create(
            underlying_instrument=e1,
            underlying_quote_price=pe1_1,
            portfolio=portfolio,
            date=previous_sync_date,
            weighting=Decimal(0.3),
            initial_price=Decimal(100),
            initial_shares=300,
        )
        a2_1 = asset_position_factory.create(
            underlying_instrument=e2,
            underlying_quote_price=pe2_1,
            portfolio=portfolio,
            date=previous_sync_date,
            weighting=Decimal(0.5),
            initial_price=Decimal(100),
            initial_shares=500,
        )
        a3_1 = asset_position_factory.create(
            underlying_instrument=e3,
            underlying_quote_price=pe3_1,
            portfolio=portfolio,
            date=previous_sync_date,
            weighting=Decimal(0.2),
            initial_price=Decimal(100),
            initial_shares=200,
        )

        a1_2 = asset_position_factory.create(
            underlying_instrument=e1,
            underlying_quote_price=pe1_2,
            portfolio=portfolio,
            date=weekday,
            weighting=Decimal(0.3719),
            initial_price=Decimal(150),
            initial_shares=300,
        )
        a2_2 = asset_position_factory.create(
            underlying_instrument=e2,
            underlying_quote_price=pe2_2,
            portfolio=portfolio,
            date=weekday,
            weighting=Decimal(0.4959),
            initial_price=Decimal(120),
            initial_shares=500,
        )
        a3_2 = asset_position_factory.create(
            underlying_instrument=e3,
            underlying_quote_price=pe3_2,
            portfolio=portfolio,
            date=weekday,
            weighting=Decimal(0.1322),
            initial_price=Decimal(80),
            initial_shares=200,
        )

        price = instrument_price_factory.create(instrument=product, date=previous_sync_date, net_value=100)
        portfolio.estimate_net_asset_values(weekday)

        total_perf = (
            (a1_2._price / a1_1._price - 1) * a1_1.weighting
            + (a2_2._price / a2_1._price - 1) * a2_1.weighting
            + (a3_2._price / a3_1._price - 1) * a3_1.weighting
        )
        assert product.prices.count() == 2
        assert float(price.net_value * (Decimal(1.0) + total_perf)) == pytest.approx(
            float(product.prices.filter(date=weekday).first().net_value)
        )

    def test_pms_instrument(self, product_group, index, product, portfolio):
        product_group.portfolios.set([portfolio])
        product.portfolios.set([portfolio])
        index.portfolios.set([portfolio])
        assert set(portfolio.pms_instruments) == {product_group, product, index}

    @pytest.mark.parametrize(
        "portfolio__is_manageable, portfolio__is_lookthrough",
        [
            (True, True),
            (False, True),
            (False, False),
        ],
    )
    def test_cannot_be_rebalanced(self, portfolio):
        assert portfolio.can_be_rebalanced is False

    @pytest.mark.parametrize(
        "portfolio__is_manageable, portfolio__is_lookthrough",
        [
            (True, False),
        ],
    )
    def test_can_be_rebalanced(self, portfolio):
        assert portfolio.can_be_rebalanced is True

    def test_get_analytic_portfolio(
        self, weekday, portfolio, asset_position_factory, instrument_factory, instrument_price_factory
    ):
        i1 = instrument_factory.create(currency=portfolio.currency)
        i2 = instrument_factory.create(currency=portfolio.currency)
        p10 = instrument_price_factory.create(instrument=i1, date=weekday)
        p11 = instrument_price_factory.create(instrument=i1, date=(weekday + BDay(1)).date())
        p20 = instrument_price_factory.create(instrument=i2, date=weekday)
        p21 = instrument_price_factory.create(instrument=i2, date=(weekday + BDay(1)).date())

        a1 = asset_position_factory.create(date=weekday, portfolio=portfolio, underlying_instrument=i1)
        a1.refresh_from_db()
        a2 = asset_position_factory.create(
            date=weekday, portfolio=portfolio, underlying_instrument=i2, weighting=Decimal(1.0) - a1.weighting
        )
        a2.refresh_from_db()

        analytic_portfolio = portfolio.get_analytic_portfolio(weekday)
        assert analytic_portfolio.weights.tolist() == [float(a1.weighting), float(a2.weighting)]
        expected_X = pd.DataFrame(
            [[float(p11.net_value / p10.net_value - Decimal(1)), float(p21.net_value / p20.net_value - Decimal(1))]],
            columns=[i1.id, i2.id],
            index=[(weekday + BDay(1)).date()],
        )
        expected_X.index = pd.to_datetime(expected_X.index)
        pd.testing.assert_frame_equal(analytic_portfolio.X, expected_X, check_names=False, check_freq=False)

    def test_get_total_asset_value(self, weekday, portfolio, asset_position_factory):
        a1 = asset_position_factory.create(date=weekday, portfolio=portfolio)
        a2 = asset_position_factory.create(date=weekday, portfolio=portfolio)
        a3 = asset_position_factory.create(date=weekday, portfolio=portfolio)
        assert (
            portfolio.get_total_asset_value(weekday)
            == a1.initial_price * a1.initial_shares * a1.initial_currency_fx_rate
            + a2.initial_price * a2.initial_shares * a2.initial_currency_fx_rate
            + a3.initial_price * a3.initial_shares * a3.initial_currency_fx_rate
        )

    @pytest.mark.parametrize("name", fake.word())
    def test_create_model_portfolio(self, name, currency):
        portfolio = Portfolio.create_model_portfolio(name, currency)
        assert portfolio.name == name
        assert portfolio.currency == currency
        assert portfolio.is_manageable is True
        pms_instruments = list(portfolio.pms_instruments)
        assert len(pms_instruments) == 1
        assert pms_instruments[0].instrument_type.key == "index"
        assert pms_instruments[0].name == name
        assert pms_instruments[0].currency == currency

    @patch.object(Portfolio, "propagate_or_update_assets", autospec=True)
    def test_update_portfolio_after_investable_universe(
        self, mock_fct, weekday, portfolio_factory, asset_position_factory
    ):
        untracked_portfolio = portfolio_factory.create(is_tracked=False, is_manageable=False)  # noqa
        asset_position_factory.create(portfolio=untracked_portfolio)
        tracked_lookthrough_portfolio = portfolio_factory.create(is_tracked=True, is_lookthrough=True)  # noqa
        asset_position_factory.create(portfolio=tracked_lookthrough_portfolio)

        update_portfolio_after_investable_universe(end_date=weekday)
        mock_fct.assert_not_called()

        tracked_portfolio = portfolio_factory.create(is_tracked=True)
        asset_position_factory.create(portfolio=tracked_portfolio)

        update_portfolio_after_investable_universe(end_date=weekday)
        mock_fct.assert_called_once_with(tracked_portfolio, (weekday - BDay(1)).date(), weekday)

    def test_get_weights(
        self, weekday, portfolio_factory, asset_position_factory, instrument_factory, instrument_price_factory
    ):
        portfolio = portfolio_factory.create()
        portfolio_created = portfolio_factory.create()

        a1 = asset_position_factory.create(date=weekday, portfolio=portfolio)
        a2 = asset_position_factory.create(date=weekday, portfolio=portfolio)
        a3 = asset_position_factory.create(
            date=weekday,
            portfolio=portfolio,
            underlying_instrument=a2.underlying_instrument,
            portfolio_created=portfolio_created,
        )
        a1.refresh_from_db()
        a2.refresh_from_db()
        a3.refresh_from_db()
        weights = portfolio.get_weights(weekday)
        assert weights[a1.underlying_quote.id] == float(a1.weighting)
        assert weights[a2.underlying_quote.id] == float(a2.weighting + a3.weighting)

    def test_get_estimated_portfolio_from_weights(
        self, weekday, portfolio, instrument, instrument_price_factory, currency_fx_rates_factory
    ):
        p = instrument_price_factory.create(instrument=instrument, date=weekday)
        fx_portfolio = currency_fx_rates_factory.create(currency=portfolio.currency, date=weekday)
        fx_instrument = currency_fx_rates_factory.create(currency=instrument.currency, date=weekday)
        instrument_id: int = instrument.id
        weights = {instrument_id: Decimal(random.random())}
        portfolio.builder.prices = {weekday: {instrument_id: p.net_value}}
        portfolio.builder.add((weekday, weights), infer_underlying_quote_price=False)

        res = list(portfolio.builder.get_positions())
        a = res[0]
        assert len(res) == 1
        assert a.date == weekday
        assert a.underlying_quote == instrument
        assert a.underlying_quote_price == None
        assert a.initial_price == p.net_value
        assert a.weighting == pytest.approx(weights[instrument.id], abs=Decimal(10e-6))
        assert a.currency_fx_rate_portfolio_to_usd == fx_portfolio
        assert a.currency_fx_rate_instrument_to_usd == fx_instrument

        # ensure saving the unsave assetposition do not lead to exception
        a.save()
        assert a

    def test_drift_weights_with_rebalancer(
        self,
        weekday,
        rebalancer_factory,
        portfolio,
        asset_position_factory,
        instrument_price_factory,
        instrument_factory,
    ):
        middle_date = (weekday + BDay(1)).date()
        rebalancing_date = (middle_date + BDay(1)).date()

        i1 = instrument_factory.create(currency=portfolio.currency)
        i2 = instrument_factory.create(currency=portfolio.currency)

        instrument_price_factory.create(net_value=Decimal("100"), instrument=i1, date=(weekday - BDay(1)).date())
        instrument_price_factory.create(net_value=Decimal("100"), instrument=i1, date=weekday)
        instrument_price_factory.create(net_value=Decimal("100"), instrument=i1, date=middle_date)
        instrument_price_factory.create(net_value=Decimal("100"), instrument=i1, date=rebalancing_date)
        instrument_price_factory.create(net_value=Decimal("100"), instrument=i2, date=(weekday - BDay(1)).date())
        instrument_price_factory.create(net_value=Decimal("100"), instrument=i2, date=weekday)
        instrument_price_factory.create(net_value=Decimal("100"), instrument=i2, date=middle_date)
        instrument_price_factory.create(net_value=Decimal("100"), instrument=i2, date=rebalancing_date)

        asset_position_factory.create(date=weekday, portfolio=portfolio, underlying_instrument=i1, weighting=0.7)
        asset_position_factory.create(date=weekday, portfolio=portfolio, underlying_instrument=i2, weighting=0.3)

        rebalancer_factory.create(portfolio=portfolio, frequency="RRULE:FREQ=DAILY;", activation_date=rebalancing_date)
        portfolio.load_builder_returns(weekday, rebalancing_date)
        gen = portfolio.drift_weights(weekday, (rebalancing_date + BDay(1)).date(), stop_at_rebalancing=True)
        assert next(gen)[0] == middle_date, "Drifting weight with a non automatic rebalancer stops the iteration"
        try:
            next(gen)
            assert False, "the next iteration should stop and return the rebalancing"
        except StopIteration as e:
            rebalancing_order_proposal = e.value
            assert rebalancing_order_proposal.trade_date == rebalancing_date
            assert rebalancing_order_proposal.status == "APPROVED"

            # we expect a equally rebalancing (default) so both orders needs to be created
            orders = rebalancing_order_proposal.get_orders()
            t1 = orders.get(value_date=rebalancing_date, underlying_instrument=i1)
            t2 = orders.get(value_date=rebalancing_date, underlying_instrument=i2)
            assert t1._target_weight == Decimal("0.5")
            assert t2._target_weight == Decimal("0.5")

            # we approve the rebalancing order proposal
            assert rebalancing_order_proposal.status == "APPROVED"
            rebalancing_order_proposal.apply(replay=False)
            rebalancing_order_proposal.save()

        # check that the rebalancing was applied and position reflect that
        assert portfolio.assets.get(date=rebalancing_date, underlying_instrument=i1).weighting == Decimal("0.5")
        assert portfolio.assets.get(date=rebalancing_date, underlying_instrument=i2).weighting == Decimal("0.5")

    def test_bulk_create_positions(self, portfolio, weekday, asset_position_factory, instrument_factory):
        portfolio.is_manageable = False
        portfolio.save()
        i1 = instrument_factory.create()
        i2 = instrument_factory.create()
        i3 = instrument_factory.create()
        a1 = asset_position_factory.build(date=weekday, portfolio=portfolio, underlying_instrument=i1)

        # check initial creation
        portfolio.builder.add([a1]).bulk_create_positions(fix_quantization=False, compute_metrics=True)
        assert AssetPosition.objects.get(portfolio=portfolio, date=weekday).weighting == a1.weighting
        assert AssetPosition.objects.get(portfolio=portfolio, date=weekday).underlying_instrument == i1

        # check that if we change key value, an already existing position will be updated accordingly
        a1.weighting = Decimal(0.5)
        portfolio.builder.add([a1]).bulk_create_positions(fix_quantization=False)
        assert AssetPosition.objects.get(portfolio=portfolio, date=weekday).weighting == Decimal(0.5)

        a2 = asset_position_factory.build(date=weekday, portfolio=portfolio, underlying_instrument=i2)
        portfolio.builder.add([a2]).bulk_create_positions(fix_quantization=False)
        assert (
            AssetPosition.objects.get(portfolio=portfolio, date=weekday, underlying_instrument=i1).weighting
            == a1.weighting
        )
        assert (
            AssetPosition.objects.get(portfolio=portfolio, date=weekday, underlying_instrument=i2).weighting
            == a2.weighting
        )

        a3 = asset_position_factory.build(date=weekday, portfolio=portfolio, underlying_instrument=i3)
        portfolio.builder.add([a3]).bulk_create_positions(delete_leftovers=True, fix_quantization=False)
        assert AssetPosition.objects.get(portfolio=portfolio, date=weekday).weighting == a3.weighting
        assert AssetPosition.objects.get(portfolio=portfolio, date=weekday).underlying_instrument == i3

    def test_to_dependency_iterator(self, portfolio_factory, asset_position_factory, index, weekday):
        Portfolio.objects.all().delete()  # ensure no portfolio remains
        dependant_portfolio = portfolio_factory.create(name="dependant portfolio", id=1)
        dependency_portfolio = portfolio_factory.create(name="dependency portfolio", id=2)
        PortfolioPortfolioThroughModel.objects.create(
            portfolio=dependant_portfolio, dependency_portfolio=dependency_portfolio
        )
        index_portfolio = portfolio_factory.create(name="Index portfolio", id=3)
        index.portfolios.add(index_portfolio)
        asset_position_factory.create(portfolio=dependency_portfolio, underlying_instrument=index, date=weekday)

        undependant_portfolio = portfolio_factory.create(name="undependant portfolio", id=4)
        res = list(Portfolio.objects.all().to_dependency_iterator(weekday))
        assert res == [index_portfolio, dependency_portfolio, dependant_portfolio, undependant_portfolio]

    @patch.object(Portfolio, "compute_lookthrough", autospec=True)
    def test_handle_controlling_portfolio_change_at_date(self, mock_compute_lookthrough, weekday, portfolio_factory):
        primary_portfolio = portfolio_factory.create(only_weighting=True)
        lookthrough_portfolio = portfolio_factory.create(is_lookthrough=True, only_weighting=False)
        PortfolioPortfolioThroughModel.objects.create(
            portfolio=lookthrough_portfolio,
            dependency_portfolio=primary_portfolio,
            type=PortfolioPortfolioThroughModel.Type.PRIMARY,
        )

        primary_portfolio.handle_controlling_portfolio_change_at_date(weekday)
        mock_compute_lookthrough.assert_called_once_with(lookthrough_portfolio, weekday)

    def test_get_model_portfolio_relationships(self, portfolio_factory, asset_position_factory, weekday):
        model_portfolio = portfolio_factory.create()
        model_index = model_portfolio.get_or_create_index()
        dependent_portfolio = portfolio_factory.create()
        re1 = PortfolioPortfolioThroughModel.objects.create(
            portfolio=dependent_portfolio,
            dependency_portfolio=model_portfolio,
            type=PortfolioPortfolioThroughModel.Type.MODEL,
        )

        assert set(model_portfolio.get_model_portfolio_relationships(weekday)) == {
            re1,
        }
        parent_portfolio = portfolio_factory.create()
        child_portfolio = portfolio_factory.create()
        re2 = PortfolioPortfolioThroughModel.objects.create(
            portfolio=child_portfolio,
            dependency_portfolio=parent_portfolio,
            type=PortfolioPortfolioThroughModel.Type.MODEL,
        )
        assert set(model_portfolio.get_model_portfolio_relationships(weekday)) == {
            re1,
        }  # child portfolio is not considered in the tree because there is no position yet

        asset_position_factory.create(portfolio=parent_portfolio, underlying_instrument=model_index, date=weekday)
        assert set(model_portfolio.get_model_portfolio_relationships(weekday)) == {re1, re2}

        dependent_portfolio.is_active = False  # disable this portfolio
        dependent_portfolio.deletion_datetime = weekday - timedelta(days=1)
        dependent_portfolio.save()
        assert set(model_portfolio.get_model_portfolio_relationships(weekday)) == {
            re2,
        }
