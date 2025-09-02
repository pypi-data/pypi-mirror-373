from decimal import Decimal

import pytest
from django.test.client import RequestFactory
from faker import Faker
from pandas.tseries.offsets import BDay, BMonthEnd, BYearEnd
from rest_framework.reverse import reverse
from rest_framework.test import force_authenticate
from wbfdm.factories import InstrumentPriceFactory

from wbportfolio.factories import ProductFactory
from wbportfolio.viewsets.product_performance import PerformanceComparisonPandasView

fake = Faker()


@pytest.mark.django_db
class TestPerformanceComparisonPandasView:
    @classmethod
    def populated_product_and_get_prices(cls):
        product = ProductFactory.create()
        last_date = (fake.date_object() - BDay(0)).date()
        date_t1 = (last_date - BDay(1)).date()  # t-1 date
        date_m1 = (last_date - BMonthEnd(1)).date()  # last month latest date
        date_y1 = (last_date - BYearEnd(1)).date()  # last year latest date
        date_inception = (last_date - BYearEnd(2)).date()  # some random date to represent inception

        last_price = InstrumentPriceFactory.create(instrument=product, date=last_date, calculated=False)
        t1 = InstrumentPriceFactory.create(instrument=product, date=date_t1, calculated=False)
        InstrumentPriceFactory.create(instrument=product, date=date_t1, calculated=True)  # Create noise

        m1 = InstrumentPriceFactory.create(instrument=product, date=date_m1, calculated=False)
        InstrumentPriceFactory.create(instrument=product, date=date_m1, calculated=True)  # Create noise
        InstrumentPriceFactory.create(
            instrument=product, date=(fake.date_between(date_m1, date_t1) - BDay(0)).date(), calculated=False
        )  # Create noise

        y1 = InstrumentPriceFactory.create(instrument=product, date=date_y1, calculated=False)
        InstrumentPriceFactory.create(instrument=product, date=date_y1, calculated=True)  # Create noise
        InstrumentPriceFactory.create(
            instrument=product, date=(fake.date_between(date_y1, date_m1) - BDay(0)).date(), calculated=False
        )  # Create noise

        inception = InstrumentPriceFactory.create(instrument=product, date=date_inception, calculated=False)
        InstrumentPriceFactory.create(instrument=product, date=date_inception, calculated=True)  # Create noise
        InstrumentPriceFactory.create(
            instrument=product, date=(fake.date_between(date_inception, date_y1) - BDay(0)).date(), calculated=False
        )  # Create noise

        product.last_valuation_date = last_date
        product.inception_date = date_inception
        product.save()
        last_price.refresh_from_db()
        m1.refresh_from_db()

        return last_price.net_value, t1.net_value, m1.net_value, y1.net_value, inception.net_value

    def test_simple_performance(self, superuser):
        """
        Basic test to check that the given performance are correct
        """
        last_price, t1, m1, y1, inception = self.populated_product_and_get_prices()

        url = reverse("wbportfolio:productperformancecomparison-list")
        request = RequestFactory().get(url)
        force_authenticate(request, user=superuser)
        view = PerformanceComparisonPandasView.as_view({"get": "list"})
        response = view(request)
        res = response.data["results"][0]
        assert pytest.approx(Decimal(res["instrument_last_valuation_price"]), rel=Decimal(1e-4)) == last_price
        assert pytest.approx(Decimal(res["perf_last_day"]), rel=Decimal(1e-4)) == last_price / t1 - Decimal(1)
        assert pytest.approx(Decimal(res["perf_month_to_date"]), rel=Decimal(1e-4)) == last_price / m1 - Decimal(1)
        assert pytest.approx(Decimal(res["perf_year_to_date"]), rel=Decimal(1e-4)) == last_price / y1 - Decimal(1)
        assert pytest.approx(Decimal(res["perf_inception"]), rel=Decimal(1e-4)) == last_price / inception - Decimal(1)
