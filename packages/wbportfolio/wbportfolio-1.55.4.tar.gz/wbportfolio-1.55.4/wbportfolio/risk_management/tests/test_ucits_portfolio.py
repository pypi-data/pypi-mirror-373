import pytest
from faker import Faker

from wbportfolio.risk_management.backends.ucits_portfolio import (
    RuleBackend as UCITPortfolioRuleBackend,
)
from wbportfolio.tests.models.utils import PortfolioTestMixin

fake = Faker()


@pytest.mark.django_db
class TestUcitsRuleModel(PortfolioTestMixin):
    @pytest.fixture
    def ucits_backend(self, weekday, portfolio):
        return UCITPortfolioRuleBackend(weekday, portfolio, [])

    def testcheck_rule_1(self, weekday, portfolio, asset_position_factory, ucits_backend):
        #  Check No single asset can represent more than 10% of the fund's assets;
        asset_position_factory.create(date=weekday, weighting=0.05, portfolio=portfolio)
        asset_position_factory.create(date=weekday, weighting=0.05, portfolio=portfolio)
        a3 = asset_position_factory.create(date=weekday, weighting=0.15, portfolio=portfolio)

        res = list(ucits_backend.check_rule())
        assert len(res) == 1
        assert res[0].breached_object == a3.underlying_instrument

    def testcheck_rule_2(self, weekday, portfolio, asset_position_factory, ucits_backend):
        # Check that stock below 5% don't trigger rule
        asset_position_factory.create_batch(4, date=weekday, weighting=0.05, portfolio=portfolio)
        asset_position_factory.create_batch(20, date=weekday, weighting=0.04, portfolio=portfolio)

        res = list(ucits_backend.check_rule())
        assert len(res) == 0

    def testcheck_rule_3(self, weekday, portfolio, asset_position_factory, ucits_backend):
        # Check holdings of more than 5% cannot in aggregate exceed 40% of the fund's assets
        asset_position_factory.create_batch(20, date=weekday, weighting=0.05, portfolio=portfolio)
        res = list(ucits_backend.check_rule())
        assert len(res) == 20
