import pytest
from faker import Faker
from wbfdm.enums import ESGControveryFlag

from wbportfolio.risk_management.backends.controversy_portfolio import (
    RuleBackend as ControversyPortfolio,
)
from wbportfolio.tests.models.utils import PortfolioTestMixin

fake = Faker()


@pytest.mark.django_db
class TestControversyPortfolioRUle(PortfolioTestMixin):
    @pytest.mark.parametrize("flag", ESGControveryFlag.values)
    def test_check_rule_exclude(
        self, weekday, portfolio, asset_position_factory, controversy_factory, rule_threshold, flag
    ):
        rule_backend = ControversyPortfolio(
            weekday, portfolio, thresholds=[rule_threshold], json_parameters={"flags": [flag]}
        )
        a1 = asset_position_factory.create(portfolio=portfolio, date=weekday)
        asset_position_factory.create(portfolio=portfolio, date=weekday)  # noise position

        # No controversy yet, so this shouldn't trigger the rule
        res = list(rule_backend.check_rule())
        assert len(res) == 0

        controversy = controversy_factory.create(flag=flag, instrument=a1.underlying_instrument)  # noqa

        res = list(rule_backend.check_rule())[0]
        assert res.breached_object == a1.underlying_instrument
        assert res.breached_object_repr == str(a1.underlying_instrument)
        assert res.severity == rule_threshold.severity
