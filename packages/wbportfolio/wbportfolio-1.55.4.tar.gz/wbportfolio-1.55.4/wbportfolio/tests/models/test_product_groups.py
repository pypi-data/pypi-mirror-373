from datetime import timedelta

import pytest
from faker import Faker
from pandas.tseries.offsets import BDay

from wbportfolio.models import Trade

fake = Faker()


@pytest.mark.django_db
class TestProductGroupModel:
    def test_init(self, product_group):
        assert product_group.id is not None

    def test_get_total_fund_aum(
        self,
        portfolio_factory,
        product_factory,
        instrument_price_factory,
        trade_factory,
        product_group,
        currency_fx_rates_factory,
        weekday,
    ):
        p1 = product_factory.create(parent=product_group, inception_date=weekday)
        p2 = product_factory.create(parent=product_group, inception_date=weekday)
        portfolio1 = p1.portfolio
        portfolio2 = p2.portfolio
        shares1 = 1000
        v1 = instrument_price_factory.create(date=weekday, instrument=p1, outstanding_shares=shares1)
        c11 = trade_factory.create(
            portfolio=portfolio1,
            shares=shares1,
            value_date=weekday,
            underlying_instrument=p1,
            transaction_subtype=Trade.Type.SUBSCRIPTION,
        )
        fx_rate1 = p1.currency.fx_rates.get(date=v1.date)

        c21 = trade_factory.create(
            portfolio=portfolio2,
            value_date=weekday,
            underlying_instrument=p2,
            transaction_subtype=Trade.Type.REDEMPTION,
        )
        v2 = instrument_price_factory.create(instrument=p2, date=weekday, outstanding_shares=c21.shares)
        fx_rate2 = p2.currency.fx_rates.get(date=weekday)
        p1.update_last_valuation_date()
        p2.update_last_valuation_date()
        assert float(product_group.get_total_fund_aum(weekday)) == pytest.approx(
            float(v1.net_value) * float(c11.shares) / float(fx_rate1.value)
            + float(v2.net_value) * float(c21.shares) / float(fx_rate2.value)
        )
        # test: get only trade at value_date
        trade_factory.create(portfolio=portfolio1, transaction_date=weekday, value_date=weekday + timedelta(days=1))
        assert float(product_group.get_total_fund_aum(weekday)) == pytest.approx(
            float(v1.net_value) * float(c11.shares) / float(fx_rate1.value)
            + float(v2.net_value) * float(c21.shares) / float(fx_rate2.value)
        )

    @pytest.mark.parametrize("val_date", [fake.date_object()])
    def test_get_fund_product_table(self, product_group, product_factory, instrument_price_factory, val_date):
        val_date = (val_date + BDay(1)).date()
        p1 = product_factory.create(parent=product_group, inception_date=val_date)
        p2 = product_factory.create(parent=product_group, inception_date=val_date)

        v1 = instrument_price_factory.create(instrument=p1, date=val_date, calculated=False)
        v2 = instrument_price_factory.create(instrument=p2, date=val_date, calculated=False)
        df = product_group.get_fund_product_table(v2.date)
        dfp1 = df[df["share class"] == p1.name]
        assert dfp1["share class"].iloc[0] == p1.name
        assert dfp1["launch date"].iloc[0] == f"{v1.date:%Y-%m-%d}"
        assert dfp1["price"].iloc[0] == f"{v1.net_value:,.2f}"


@pytest.mark.django_db
class TestProductGroupRepresentantModel:
    def test_init(self, product_group_representant):
        assert product_group_representant.id is not None
