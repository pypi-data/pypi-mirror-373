import datetime
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest
from faker import Faker
from wbfdm.models import Instrument

from wbportfolio.models import Product, Trade

from ...preferences import get_product_termination_notice_period
from .utils import PortfolioTestMixin

fake = Faker()


@pytest.mark.django_db
class TestProductModel(PortfolioTestMixin):
    def test_init(self, product):
        assert product.id is not None

    def test_white_label(self, white_label_product):
        assert white_label_product.white_label_product

    def test_total_value(self, product_factory, trade_factory, instrument_price_factory):
        product = product_factory.create()
        t1 = trade_factory.create(
            shares=100,
            underlying_instrument=product,
            transaction_date=datetime.date(2010, 1, 1) - datetime.timedelta(days=2),
            transaction_subtype=Trade.Type.SUBSCRIPTION,
        )
        t2 = trade_factory.create(
            shares=50,
            underlying_instrument=product,
            transaction_date=datetime.date(2010, 1, 1) - datetime.timedelta(days=1),
            transaction_subtype=Trade.Type.SUBSCRIPTION,
        )
        t3 = trade_factory.create(  # noise
            shares=10,
            underlying_instrument=product,
            transaction_date=datetime.date(2010, 1, 1),
            transaction_subtype=Trade.Type.SUBSCRIPTION,
        )
        p1 = instrument_price_factory.create(
            instrument=Instrument.objects.get(id=product.id), date=t1.transaction_date
        )
        p2 = instrument_price_factory.create(
            instrument=Instrument.objects.get(id=product.id), date=t2.transaction_date
        )
        p3 = instrument_price_factory.create(
            instrument=Instrument.objects.get(id=product.id), date=t3.transaction_date
        )
        assert product.get_total_aum_usd(p1.date) == pytest.approx(Decimal(0), rel=Decimal("1e-4"))
        assert product.get_total_aum_usd(p2.date) == pytest.approx(
            Decimal(p2.net_value * (t1.shares)), rel=Decimal("1e-4")
        )
        assert product.get_total_aum_usd(p3.date) == pytest.approx(
            Decimal(p3.net_value * (t1.shares + t2.shares)), rel=Decimal("1e-4")
        )

    def test_total_shares_with_date(self, product_factory, trade_factory):
        date1 = datetime.date(2010, 1, 1)
        date2 = datetime.date(2010, 1, 2)
        product = product_factory.create()
        sub1 = trade_factory.create(
            underlying_instrument=product,
            transaction_date=date1 - datetime.timedelta(days=1),
            value_date=date1,
            transaction_subtype=Trade.Type.SUBSCRIPTION,
        )
        sub2 = trade_factory.create(
            underlying_instrument=product,
            transaction_date=date2 - datetime.timedelta(days=1),
            value_date=date2,
            transaction_subtype=Trade.Type.SUBSCRIPTION,
        )
        red1 = trade_factory.create(
            underlying_instrument=product,
            transaction_date=date1 - datetime.timedelta(days=1),
            value_date=date1,
            transaction_subtype=Trade.Type.REDEMPTION,
        )
        red2 = trade_factory.create(
            underlying_instrument=product,
            transaction_date=date2 - datetime.timedelta(days=1),
            value_date=date2,
            transaction_subtype=Trade.Type.REDEMPTION,
        )
        assert product.total_shares(date1 - datetime.timedelta(days=1)) == 0
        assert product.total_shares(date1) == red1.shares + sub1.shares
        assert product.total_shares(date2) == red1.shares + red2.shares + sub1.shares + sub2.shares

    def test_nominal_value_with_date(self, product_factory, trade_factory):
        product = product_factory.create()
        trade_factory.create_batch(
            5,
            shares=100,
            underlying_instrument=product,
            transaction_date=datetime.date(2010, 1, 1) - datetime.timedelta(days=1),
            transaction_subtype=Trade.Type.SUBSCRIPTION,
        )
        trade_factory.create_batch(
            5,
            shares=100,
            underlying_instrument=product,
            transaction_date=datetime.date(2010, 1, 2) - datetime.timedelta(days=1),
            transaction_subtype=Trade.Type.SUBSCRIPTION,
        )
        assert product.nominal_value(datetime.date(2010, 1, 1)) == (500 * product.share_price)
        assert product.nominal_value(datetime.date(2010, 1, 2)) == (1000 * product.share_price)

    def test_get_title(self, product, user):
        assert product.get_title()

    def test_compute_str(self, product, user):
        assert product.compute_str()

        # test if we save the parent instrument, the computed str is the one from the product class
        instrument = product.instrument_ptr
        instrument.save()
        product.refresh_from_db()
        assert product.computed_str == product.compute_str()

    def test_urlify_title(self, product):
        assert product.name.lower() in product.urlify_title

    def test_get_products_internal_user(self, product, white_label_product, internal_user_factory):
        assert set(Product.get_products(internal_user_factory.create().profile)) == {product, white_label_product}

    def test_get_products_normal_user(self, product_factory, user, company):
        public_product = product_factory.create()
        assert set(Product.get_products(user.profile)) == {public_product}

        white_label_product_profile = product_factory.create()
        white_label_product_profile.white_label_customers.add(user.profile)

        white_label_product_employer = product_factory.create()
        user.profile.employers.add(company)
        white_label_product_employer.white_label_customers.add(company)

        assert set(Product.get_products(user.profile)) == {
            white_label_product_employer,
            white_label_product_profile,
            public_product,
        }

    def test_subquery_is_white_label_product(self, product, white_label_product):
        product_queryset = Product.objects.all().annotate(is_white_label=Product.subquery_is_white_label_product())
        assert product_queryset.filter(is_white_label=True).count() == 1

    def test_annotate_aum(
        self, portfolio, product_factory, instrument_price_factory, trade_factory, currency_fx_rates_factory
    ):
        p1 = product_factory.create()
        d = datetime.date(2021, 1, 1)
        c1 = trade_factory.create(
            portfolio=p1.portfolio,
            underlying_instrument=p1,
            transaction_subtype=Trade.Type.SUBSCRIPTION,
            value_date=d,
            transaction_date=d,
        )
        v1 = instrument_price_factory.create(instrument=p1, date=d, outstanding_shares=c1.shares)
        fx_rate = p1.currency.fx_rates.get(date=d)
        qs = Product.annotate_last_aum(Product.objects.all(), val_date=d)
        p1.update_last_valuation_date()
        assert float(qs.first().assets_under_management_usd) == pytest.approx(
            float(v1.net_value) * float(c1.shares) / float(fx_rate.value)
        )

    def test_account_merging(self, account_factory, product):
        base_account = account_factory.create()
        merged_account = account_factory.create()
        product.default_account = merged_account
        product.save()
        base_account.merge(merged_account)
        product.refresh_from_db()
        assert product.default_account == base_account

    def test_high_water_mark(self, product, instrument_price_factory):
        initial_price = instrument_price_factory.create(instrument=product, net_value=100)
        p1 = instrument_price_factory.create(instrument=product, net_value=200)
        p2 = instrument_price_factory.create(instrument=product, net_value=100)
        p3 = instrument_price_factory.create(instrument=product, net_value=300)
        p4 = instrument_price_factory.create(instrument=product, net_value=100)
        assert product.get_high_water_mark(p1.date) == initial_price.net_value
        assert product.get_high_water_mark(p2.date) == p1.net_value
        assert product.get_high_water_mark(p3.date) == p1.net_value
        assert product.get_high_water_mark(p4.date) == p3.net_value
        product.initial_high_water_mark = 400
        product.save()
        assert product.get_high_water_mark(p4.date) == 400

    @patch("wbportfolio.models.products.send_notification")
    def test_check_and_notify_product_termination_on_date(
        self, mock_fct, weekday, product, manager_portfolio_role_factory, internal_user
    ):
        assert not product.check_and_notify_product_termination_on_date(weekday)

        product.delisted_date = weekday + datetime.timedelta(days=get_product_termination_notice_period())
        product.save()
        assert product.check_and_notify_product_termination_on_date(weekday)
        mock_fct.assert_not_called()
        assert not product.check_and_notify_product_termination_on_date(
            weekday + timedelta(days=1)
        )  # one day later is not valid anymore

        manager_portfolio_role_factory.create(person=internal_user.profile)
        product.check_and_notify_product_termination_on_date(weekday)
        mock_fct.assert_called_with(
            code="wbportfolio.product.termination_notice",
            title="Product Termination Notice",
            body=f"The product {product} will be terminated on the {product.delisted_date:%Y-%m-%d}",
            user=internal_user,
        )

    def test_delist_product_disable_report(self, product, report_factory):
        report = report_factory.create(content_object=product, is_active=True)
        assert product.delisted_date is None
        assert report.is_active

        product.delisted_date = datetime.date.today()
        product.save()

        report.refresh_from_db()
        assert report.is_active is False
