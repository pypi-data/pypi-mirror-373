from datetime import timedelta
from decimal import Decimal

import pytest
from faker import Faker

from wbportfolio.models import Product, Trade

fake = Faker()


@pytest.mark.django_db
class TestTradeModel:
    def test_init(self, trade):
        assert trade.id is not None

    def test_str(self, product, trade_factory):
        trade = trade_factory.create(underlying_instrument=product)
        assert str(trade) == f"{trade.product.ticker}:{trade.shares} ({trade.bank})"

    def test_save_with_price(self, trade_factory):
        trade = trade_factory(price=150)
        assert trade.price == 150

    def test_subquery_net_money(self, trade_factory, instrument_price_factory, product):
        v = instrument_price_factory.create(instrument=product)
        c2 = trade_factory.create(
            underlying_instrument=product,
            transaction_date=v.date - timedelta(days=1),
            shares=-1,
            transaction_subtype=Trade.Type.REDEMPTION,
        )
        c1 = trade_factory.create(
            underlying_instrument=product,
            transaction_date=v.date - timedelta(days=1),
            shares=1,
            transaction_subtype=Trade.Type.SUBSCRIPTION,
        )
        trade_factory.create(  # noise
            underlying_instrument=product,
            transaction_date=v.date,
            shares=1,
            transaction_subtype=Trade.Type.SUBSCRIPTION,
        )
        products_pos = Product.objects.annotate(value=Trade.subquery_net_money(v.date, v.date))
        assert products_pos.first().value == pytest.approx(c2.shares * c2.price + c1.shares * c1.price)

        products_pos = Product.objects.annotate(value=Trade.subquery_net_money(v.date, v.date, only_positive=True))
        assert products_pos.first().value == pytest.approx(c1.shares * c1.price)

        products_neg = Product.objects.annotate(value=Trade.subquery_net_money(v.date, v.date, only_negative=True))
        assert products_neg.first().value == pytest.approx(c2.shares * c2.price)

    @pytest.mark.parametrize("date", [(fake.date_object())])
    def test_subquery_shares_per_product(self, trade_factory, product, date):
        a1 = trade_factory.create(
            underlying_instrument=product,
            transaction_date=date - timedelta(days=1),
            transaction_subtype=Trade.Type.SUBSCRIPTION,
        )
        trade_factory.create(  # noise
            underlying_instrument=product, transaction_date=date, transaction_subtype=Trade.Type.SUBSCRIPTION
        )
        qs = Product.objects.annotate(total_shares=Trade.subquery_shares_per_underlying_instrument(date))
        assert qs.first().total_shares == a1.shares

    @pytest.mark.parametrize("date", [(fake.date_object())])
    def test_subquery_shares_per_product_per_date(self, trade_factory, product, date):
        a1 = trade_factory.create(
            underlying_instrument=product,
            transaction_date=date - timedelta(days=1),
            transaction_subtype=Trade.Type.SUBSCRIPTION,
        )
        trade_factory.create(  # noise
            underlying_instrument=product, transaction_date=date, transaction_subtype=Trade.Type.SUBSCRIPTION
        )
        qs = Product.objects.annotate(total_shares=Trade.subquery_shares_per_underlying_instrument(date))
        assert qs.first().total_shares == a1.shares

    @pytest.mark.parametrize("date", [(fake.date_object())])
    def test_subquery_net_new_money(self, trade_factory, product, date):
        a1 = trade_factory.create(
            underlying_instrument=product,
            transaction_date=date - timedelta(days=1),
            transaction_subtype=Trade.Type.SUBSCRIPTION,
        )
        trade_factory.create(  # noise
            underlying_instrument=product,
            transaction_date=date,
            transaction_subtype=Trade.Type.SUBSCRIPTION,
        )
        qs = Product.objects.annotate(total_shares=Trade.subquery_shares_per_underlying_instrument(date))
        assert qs.first().total_shares == a1.shares

    def test_claim_update_claimed_shares(self, customer_trade_factory, claim_factory):
        customer_trade = customer_trade_factory.create()
        claim_factory.create(status="PENDING", trade=customer_trade)
        customer_trade.refresh_from_db()
        assert customer_trade.claimed_shares == 0
        c2 = claim_factory.create(status="APPROVED", trade=customer_trade)
        customer_trade.refresh_from_db()
        assert customer_trade.claimed_shares == c2.shares


@pytest.mark.django_db
class TestTradeInstrumentPrice:
    def test_shares(self, portfolio, product_factory, trade_factory, instrument_price_factory):
        product = product_factory.create()
        price = instrument_price_factory.create(instrument=product)
        trade1 = trade_factory.create(
            portfolio=product.primary_portfolio,
            underlying_instrument=product,
            transaction_date=price.date - timedelta(days=1),
            transaction_subtype=Trade.Type.SUBSCRIPTION,
        )
        trade2 = trade_factory.create(
            portfolio=product.primary_portfolio,
            underlying_instrument=product,
            transaction_date=price.date - timedelta(days=1),
            transaction_subtype=Trade.Type.SUBSCRIPTION,
        )
        trade_factory.create(  # noise
            portfolio=product.primary_portfolio,
            underlying_instrument=product,
            transaction_date=price.date,
            transaction_subtype=Trade.Type.SUBSCRIPTION,
        )
        assert price.shares == pytest.approx(trade1.shares + trade2.shares)

    def test_nominal_value(self, portfolio, product_factory, trade_factory, instrument_price_factory):
        product = product_factory.create()
        price = instrument_price_factory.create(instrument=product)
        trade1 = trade_factory.create(
            portfolio=product.primary_portfolio,
            underlying_instrument=product,
            transaction_date=price.date - timedelta(days=1),
            transaction_subtype=Trade.Type.SUBSCRIPTION,
        )
        trade2 = trade_factory.create(
            portfolio=product.primary_portfolio,
            underlying_instrument=product,
            transaction_date=price.date - timedelta(days=1),
            transaction_subtype=Trade.Type.SUBSCRIPTION,
        )
        trade_factory.create(  # noise
            portfolio=product.primary_portfolio,
            underlying_instrument=product,
            transaction_date=price.date,
            transaction_subtype=Trade.Type.SUBSCRIPTION,
        )
        assert price.nominal_value == pytest.approx(Decimal(product.share_price * (trade1.shares + trade2.shares)))

    def test_subscription_link_to_internal_trade(self, weekday, trade_factory, product):
        shares = 100
        trade_factory.create(shares=shares, transaction_subtype=Trade.Type.BUY, transaction_date=weekday)  # noise 1
        trade_factory.create(
            shares=shares,
            transaction_subtype=Trade.Type.BUY,
            transaction_date=weekday + timedelta(days=Trade.TRADE_WINDOW_INTERVAL + 1),
            underlying_instrument=product,
        )  # noise 2
        subscription_trade1 = trade_factory.create(
            shares=shares,
            transaction_subtype=Trade.Type.SUBSCRIPTION,
            transaction_date=weekday,
            underlying_instrument=product,
        )  # noise 3
        internal_trade = trade_factory.create(
            shares=shares, transaction_subtype=Trade.Type.BUY, transaction_date=weekday, underlying_instrument=product
        )
        subscription_trade2 = trade_factory.create(
            shares=shares,
            transaction_subtype=Trade.Type.SUBSCRIPTION,
            transaction_date=weekday,
            underlying_instrument=product,
        )

        subscription_trade1.link_to_internal_trade()
        assert subscription_trade1.internal_trade == internal_trade
        assert subscription_trade1.marked_as_internal is True

        # Reset attribute to test the other side
        subscription_trade1.internal_trade = None
        subscription_trade1.marked_as_internal = False
        subscription_trade1.save()

        # Check that linking from the other site but with two similar subscriptions won't link
        internal_trade.link_to_internal_trade()
        subscription_trade1.refresh_from_db()
        subscription_trade2.refresh_from_db()
        assert subscription_trade1.internal_trade is None
        assert subscription_trade2.internal_trade is None

        # Check that with now only one subscription, the linking is successful
        subscription_trade2.delete()
        internal_trade.link_to_internal_trade()
        subscription_trade1.refresh_from_db()
        assert subscription_trade1.internal_trade == internal_trade
        assert subscription_trade1.marked_as_internal is True
