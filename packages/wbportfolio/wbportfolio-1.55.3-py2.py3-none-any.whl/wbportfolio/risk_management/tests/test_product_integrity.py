import pytest
from faker import Faker
from pandas.tseries.offsets import BDay
from psycopg.types.range import NumericRange
from wbcompliance.factories.risk_management import RuleThresholdFactory

from wbportfolio.risk_management.backends.product_integrity import (
    RuleBackend as ProductRuleBackend,
)

fake = Faker()


@pytest.mark.django_db
class TestProductRuleModel:
    @pytest.fixture
    def product_backend(
        self,
        weekday,
        product,
    ):
        return ProductRuleBackend(
            weekday,
            product,
            thresholds=[
                RuleThresholdFactory.create(range=NumericRange(lower=1, upper=2), severity__name="LOW"),
                RuleThresholdFactory.create(range=NumericRange(lower=2, upper=None), severity__name="HIGH"),
            ],  # detect any -20% perf
        )

    def test_check_rule_product_data_integrity(
        self, weekday, product, instrument_price_factory, asset_position_factory, product_backend
    ):
        asset_position_factory.create(date=weekday - BDay(2), portfolio=product.portfolio, is_estimated=False)
        instrument_price_factory.create(date=weekday - BDay(1), instrument=product, calculated=False)

        res = list(product_backend.check_rule())
        assert len(res) == 1
        incident = res[0]
        assert incident.severity.name == "HIGH"
        assert incident.breached_value == str(2)
        assert incident.report_details["Lag"] == 2
        assert incident.report_details["Last Asset Position Datapoint"] == f"{(weekday - BDay(2)).date():%d.%m.%Y}"
        assert incident.report_details["Last Valuation Datapoint"] == f"{(weekday - BDay(1)).date():%d.%m.%Y}"

        instrument_price_factory.create(date=weekday, instrument=product, calculated=False)
        asset_position_factory.create(date=weekday, portfolio=product.portfolio, is_estimated=False)
        res = list(product_backend.check_rule())
        assert len(res) == 0
