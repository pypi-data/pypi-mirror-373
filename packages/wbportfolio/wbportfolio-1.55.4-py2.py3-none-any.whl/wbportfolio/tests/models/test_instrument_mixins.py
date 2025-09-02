from datetime import timedelta

import pandas as pd
import pytest
from faker import Faker

fake = Faker()


@pytest.mark.django_db
class TestInstrumentMixin:
    def test_get_latest_valid_price(self, product, instrument_price_factory):
        v1 = instrument_price_factory.create(instrument=product)
        v2 = instrument_price_factory.create(instrument=product)
        instrument_price_factory.create(instrument=product, calculated=True)

        assert product.get_latest_valid_price() == v2
        assert product.get_latest_valid_price(v1.date) == v1

    def test_get_earliest_valid_price(self, product, instrument_price_factory):
        instrument_price_factory.create(instrument=product, calculated=True)
        v2 = instrument_price_factory.create(instrument=product)
        v3 = instrument_price_factory.create(instrument=product)

        assert product.get_earliest_valid_price() == v2
        assert product.get_earliest_valid_price(v3.date) == v3

    def test_get_price_range(self, product, instrument_price_factory):
        v_low = instrument_price_factory.create(instrument=product, net_value=1)
        instrument_price_factory.create(instrument=product, net_value=10)
        v_high = instrument_price_factory.create(instrument=product, net_value=100)

        res = product.get_price_range()
        assert res["high"]["price"] == pytest.approx(float(v_high.net_value), rel=1e-4)
        assert res["high"]["date"] == v_high.date
        assert res["low"]["price"] == pytest.approx(float(v_low.net_value), rel=1e-4)
        assert res["low"]["date"] == v_low.date
        assert product.get_price_range(v_low.date - timedelta(days=1)) == dict()

    def test_get_cumulative_shares(self, weekday, product, customer_trade_factory):
        from_date = weekday
        to_date = (weekday + pd.tseries.offsets.BDay(1)).date()
        assert product.get_cumulative_shares(from_date, to_date).to_list() == [0.0, 0.0]

        trade = customer_trade_factory.create(
            transaction_date=weekday, underlying_instrument=product, portfolio=product.primary_portfolio
        )
        assert product.get_cumulative_shares(from_date, to_date).to_list() == [0.0, float(trade.shares)]
