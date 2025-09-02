import pytest
from faker import Faker
from psycopg.types.range import NumericRange
from wbcompliance.factories.risk_management import RuleThresholdFactory

from wbportfolio.risk_management.backends.liquidity_risk import (
    RuleBackend as LiquidityRiskRuleBackend,
)

fake = Faker()


@pytest.mark.django_db
class TestProductRuleModel:
    @pytest.fixture
    def liquidity_risk_backend(
        self,
        weekday,
        instrument,
    ):
        return LiquidityRiskRuleBackend(
            weekday,
            instrument,
            json_parameters={"liquidation_factor": 3, "redemption_pct": 0.80},
            thresholds=[
                RuleThresholdFactory.create(range=NumericRange(lower=5, upper=None)),
            ],
        )

    def test_check_rule_product_liquidity(
        self, weekday, instrument, instrument_price_factory, asset_position_factory, liquidity_risk_backend
    ):
        res = list(liquidity_risk_backend.check_rule())  # no position, no risk incident
        assert len(res) == 0

        shares = 100

        volume_50d = (shares * liquidity_risk_backend.redemption_pct * liquidity_risk_backend.liquidation_factor) / 6
        instrument_price_factory.create(date=weekday, instrument=instrument, volume_50d=volume_50d, calculated=False)
        asset_position_factory.create(
            date=weekday, underlying_instrument=instrument, is_estimated=False, initial_shares=shares
        )

        res = list(liquidity_risk_backend.check_rule())  # no position, no risk incident
        assert len(res) == 1
        incident = res[0]
        assert incident.report_details["Total Shares"] == shares
        assert incident.report_details["Volume 50D"] == volume_50d
