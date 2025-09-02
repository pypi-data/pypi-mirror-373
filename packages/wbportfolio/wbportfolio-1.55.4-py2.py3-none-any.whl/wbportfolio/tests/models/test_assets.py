from decimal import Decimal

import pytest
from pandas.tseries.offsets import BDay

from wbportfolio.models import AssetPosition, PortfolioRole


@pytest.mark.django_db
class TestAssetPositionModel:
    def test_init(self, asset_position):
        assert asset_position.id is not None

    def test_currency_group_by(self, asset_position_factory, equity_factory, portfolio, currency):
        asset_position_factory.create(
            portfolio=portfolio, currency=currency, underlying_instrument=equity_factory.create()
        )
        asset_position_factory.create(
            portfolio=portfolio, currency=currency, underlying_instrument=equity_factory.create()
        )
        assert (
            AssetPosition.currency_group_by(AssetPosition.objects.all()).values("groupby_id").distinct().count() == 1
        )

    def test_country_group_by(self, asset_position_factory, portfolio, equity):
        asset_position_factory.create(portfolio=portfolio, underlying_instrument=equity)
        asset_position_factory.create(portfolio=portfolio, underlying_instrument=equity)
        assert AssetPosition.country_group_by(AssetPosition.objects.all()).values("groupby_id").distinct().count() == 1

    def test_exchange_group_by(self, asset_position_factory, portfolio, exchange_factory, instrument):
        asset_position_factory.create(
            portfolio=portfolio, exchange=exchange_factory.create(), underlying_quote=instrument
        )
        asset_position_factory.create(
            portfolio=portfolio, exchange=exchange_factory.create(), underlying_quote=instrument
        )
        assert (
            AssetPosition.exchange_group_by(AssetPosition.objects.all()).values("groupby_id").distinct().count() == 1
        )

    def test_cash_group_by(self, asset_position_factory, portfolio, cash, equity):
        asset_position_factory.create(portfolio=portfolio, underlying_instrument=cash)
        asset_position_factory.create(portfolio=portfolio, underlying_instrument=cash)
        asset_position_factory.create(portfolio=portfolio, underlying_instrument=equity)
        assert AssetPosition.cash_group_by(AssetPosition.objects.all()).values("groupby_id").distinct().count() == 2

    def test_equity_group_by(self, asset_position_factory, portfolio, equity):
        asset_position_factory.create(portfolio=portfolio, underlying_instrument=equity)
        asset_position_factory.create(portfolio=portfolio, underlying_instrument=equity)
        assert AssetPosition.equity_group_by(AssetPosition.objects.all()).values("groupby_id").distinct().count() == 1

    def test_marketcap_group_by(
        self, asset_position_factory, equity_factory, portfolio, instrument_price_factory, currency_fx_rates_factory
    ):
        fx_rate = currency_fx_rates_factory.create(value=1)
        i1 = instrument_price_factory.create(instrument=equity_factory.create(), market_capitalization=1000000000)
        i2 = instrument_price_factory.create(instrument=equity_factory.create(), market_capitalization=30000000000)
        asset_position_factory.create(
            portfolio=portfolio,
            underlying_quote_price=i1,
            currency_fx_rate_instrument_to_usd=fx_rate,
            currency_fx_rate_portfolio_to_usd=fx_rate,
        )  # small
        asset_position_factory.create(
            portfolio=portfolio,
            underlying_quote_price=i2,
            currency_fx_rate_instrument_to_usd=fx_rate,
            currency_fx_rate_portfolio_to_usd=fx_rate,
        )  # larg

        qs = AssetPosition.marketcap_group_by(AssetPosition.objects.all())
        assert qs.values("aggregated_title").distinct().count() == 2
        assert set(qs.distinct().values_list("aggregated_title", flat=True)) == {"10B to 50B", "< 2B"}

    def test_liquidity_group_by(self, asset_position_factory, equity_factory, portfolio, instrument_price_factory):
        a1 = asset_position_factory.create(
            portfolio=portfolio, initial_shares=1, underlying_instrument=equity_factory.create()
        )  # small
        a2 = asset_position_factory.create(
            portfolio=portfolio, initial_shares=1, underlying_instrument=equity_factory.create()
        )  # larg

        instrument_price_factory.create(instrument=a1.underlying_instrument, date=a1.date, volume_50d=1000000)
        instrument_price_factory.create(instrument=a2.underlying_instrument, date=a2.date, volume_50d=3000000)

        qs = AssetPosition.liquidity_group_by(AssetPosition.objects.all())
        assert qs.values("aggregated_title").distinct().count() == 1

    def test_get_shown_positions_superuser(self, portfolio, superuser, asset_position_factory):
        superuser.is_superuser = True
        superuser.save()
        asset_position_factory.create_batch(10, portfolio=portfolio)
        qs = AssetPosition.get_shown_positions(superuser.profile)
        assert qs.count() == 10

    def test_get_shown_positions_analyst(
        self, portfolio_factory, product_factory, person, user, asset_position_factory, product_portfolio_role_factory
    ):
        user.profile = person
        user.save()
        p2 = portfolio_factory.create()
        product = product_factory.create()
        product_portfolio_role_factory.create(
            person=person, instrument=product, role_type=PortfolioRole.RoleType.ANALYST
        )
        asset_position_factory.create_batch(10, portfolio=product.portfolio)
        asset_position_factory.create_batch(10, portfolio=p2)
        qs = AssetPosition.get_shown_positions(person)
        assert qs.count() == 10

    def test_analytical_objects(self, asset_position_factory, portfolio, equity_factory):
        # Data creation
        equity1 = equity_factory.create()
        equity2 = equity_factory.create()
        asset_position_factory.create_batch(5, underlying_instrument=equity1, portfolio=portfolio)
        asset_position_factory.create_batch(5, underlying_instrument=equity2, portfolio=portfolio)

        # We test calculation with equity1. equity2 allows to certify the temporal continuity of the portfolio.
        qs_assets_equity1 = AssetPosition.analytical_objects.order_by("date").filter(underlying_instrument=equity1)
        qs_prices_equity1 = equity1.prices.order_by("date")

        # ap holds for AssetPosition and ep holds for Equity Price.
        ap1, ap2 = qs_assets_equity1[:2]
        ep1, ep2, ep3, ep4 = qs_prices_equity1[:4]

        # Basic Performance
        assert ap2.performance == float(ap2.price_fx_usd / ap1.price_fx_usd - 1)
        assert ap2.performance == pytest.approx(float(ep2._net_value_usd / ep1._net_value_usd - Decimal(1)))

        # We sell the equity (ap3 deleted) and then we buy it again (back in ap4).
        # This is like having a missing data in between.
        qs_assets_equity1.exclude(id__in=[ap1.id, ap2.id]).first().delete()  # ap3
        ap4 = qs_assets_equity1.exclude(id__in=[ap1.id, ap2.id]).first()

        assert ap4.performance is None
        assert ep4._net_value_usd / ep3._net_value_usd is not None

    def test_get_underlying_quote_price(self, asset_position_factory, instrument_price_factory):
        """
        In this test, we confirm that an asset position with no matching real price for the same date and underlying instrument will result in an empty underlying_quote_price
        """
        a1 = asset_position_factory.create(underlying_quote_price=None)
        a1.save()
        assert a1.underlying_quote_price is None
        p2_calculated = instrument_price_factory.create(calculated=True)
        a2 = asset_position_factory.create(
            underlying_quote_price=None, underlying_instrument=p2_calculated.instrument, date=p2_calculated.date
        )
        a2.save()
        assert a2.underlying_quote_price is None
        p2_real = instrument_price_factory.create(
            calculated=False, date=p2_calculated.date, instrument=p2_calculated.instrument
        )
        a2.save()
        assert a2.underlying_quote_price == p2_real

    def test_change_currency_recompute_currency_fx_rate_for_price_and_assets(
        self, weekday, instrument, currency_fx_rates_factory, instrument_price_factory, asset_position_factory
    ):
        fx_rate = currency_fx_rates_factory.create(currency=instrument.currency, date=weekday)
        fx_rate_other = currency_fx_rates_factory.create(date=weekday)

        p = instrument_price_factory.create(instrument=instrument, date=weekday)
        a = asset_position_factory.create(underlying_instrument=instrument, date=weekday)

        assert p.currency_fx_rate_to_usd == fx_rate
        assert a.currency_fx_rate_instrument_to_usd == fx_rate

        instrument.currency = fx_rate_other.currency
        instrument.save()

        p.refresh_from_db()
        a.refresh_from_db()

        assert p.currency_fx_rate_to_usd == fx_rate_other
        assert a.currency_fx_rate_instrument_to_usd == fx_rate_other

    def test_create_price_set_assetposition(self, asset_position_factory, instrument_price_factory):
        p0 = instrument_price_factory.create()
        d1 = (p0.date + BDay(1)).date()
        a1 = asset_position_factory.create(date=d1, underlying_instrument=p0.instrument, underlying_quote_price=None)

        # check it is linked to the only price
        assert a1.underlying_quote_price == p0
        p1 = instrument_price_factory.create(instrument=p0.instrument, date=d1)
        a1.refresh_from_db()
        assert a1.underlying_quote_price == p1

        d_1 = (p0.date - BDay(1)).date()
        a_1 = asset_position_factory.create(date=d_1, underlying_instrument=p1.instrument, underlying_quote_price=None)
        assert a_1.underlying_quote_price is None
        p_1 = instrument_price_factory.create(instrument=p1.instrument, date=d_1)
        a_1.refresh_from_db()
        assert a_1.underlying_quote_price == p_1

    def test_save_asset_without_instrument(self, asset_position_factory, instrument_factory):
        parent = instrument_factory.create()
        instrument_factory.create(parent=parent)  # noise
        primary_quote = instrument_factory.create(parent=parent, is_primary=True)

        a = asset_position_factory.create(underlying_quote=primary_quote, underlying_instrument=None)
        assert a.underlying_instrument == parent

        a = asset_position_factory.create(underlying_quote=None, underlying_instrument=parent)
        assert a.underlying_quote == primary_quote
