from datetime import timedelta
from decimal import Decimal

import pytest
from wbfdm.models import InstrumentPrice

from wbportfolio.models import FeeCalculation, Fees, Product


def fees_calculation(price_id):
    price = InstrumentPrice.objects.get(id=price_id)
    product = Product.objects.get(id=price.instrument.id)
    yield {
        "product": product,
        "fee_date": price.date,
        "transaction_subtype": Fees.Type.MANAGEMENT,
        "currency": product.currency,
        "calculated": True,
        "total_value": price.net_value,
        "total_value_gross": price.net_value,
    }


@pytest.mark.django_db
class TestFeesModel:
    def test_init(self, fees):
        assert fees.id is not None

    def test_filter_only_valid_fees(self, fees_factory):
        fees_d0 = (
            fees_factory.create()
        )  # no matter if estimated or not, we expect this fee to be on the resulting queryset
        calculated_fees_d1 = fees_factory.create(  # there will be a real fee for that date, type and product, so this will be filtered out
            calculated=True,
            product=fees_d0.product,
            fee_date=(fees_d0.fee_date + timedelta(days=1)),
            transaction_subtype=fees_d0.transaction_subtype,
        )
        real_fees_d1 = fees_factory.create(
            calculated=False,
            product=calculated_fees_d1.product,
            fee_date=calculated_fees_d1.fee_date,
            transaction_subtype=calculated_fees_d1.transaction_subtype,
        )

        assert set(Fees.valid_objects.all()) == {fees_d0, real_fees_d1}
        assert set(Fees.objects.filter_only_valid_fees()) == {fees_d0, real_fees_d1}

    def test_compute_fee_from_price(self, product_factory, instrument_price_factory):
        # we check the mechanism of computing fees on valuation creation
        fee_calculation = FeeCalculation.objects.create(
            name="base computation", import_path="wbportfolio.tests.models.transactions.test_fees"
        )
        product = product_factory.create(fee_calculation=fee_calculation)
        price = instrument_price_factory.create(instrument=product)  # post save must be called to compute fees

        fees = Fees.objects.get(
            product=product, fee_date=price.date, calculated=True, transaction_subtype=Fees.Type.MANAGEMENT
        )
        assert fees.total_value == pytest.approx(price.net_value, rel=Decimal(1e-4))
