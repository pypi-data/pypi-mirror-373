import pytest
from faker import Faker
from wbfdm.models.instruments.instrument_lists import InstrumentListThroughModel

from wbportfolio.risk_management.backends.instrument_list_portfolio import (
    RuleBackend as InstrumentListPortfolio,
)
from wbportfolio.tests.models.utils import PortfolioTestMixin

fake = Faker()


@pytest.mark.django_db
class TestInstrumentListPortfolio(PortfolioTestMixin):
    def test_check_rule_exclude(self, weekday, portfolio, asset_position_factory, instrument_list, rule_threshold):
        rule_backend = InstrumentListPortfolio(
            weekday, portfolio, json_parameters={"instrument_lists": [instrument_list.id]}, thresholds=[rule_threshold]
        )
        a1 = asset_position_factory.create(portfolio=portfolio, date=weekday)
        asset_position_factory.create(portfolio=portfolio, date=weekday)  # noise position

        rel = InstrumentListThroughModel.objects.create(
            instrument=a1.underlying_instrument, instrument_list=instrument_list, validated=False
        )
        # we check that even though the insturment is in the list, it's still not validated, so this shouldn't trigger the rule
        res = list(rule_backend.check_rule())
        assert len(res) == 0

        rel.validated = True
        rel.save()
        res = list(rule_backend.check_rule())[0]
        assert res.breached_object == a1.underlying_instrument
        assert res.breached_object_repr == str(a1.underlying_instrument)
        assert res.severity == rule_threshold.severity

    def test_check_rule_include(self, weekday, portfolio, asset_position_factory, instrument_list, rule_threshold):
        rule_backend = InstrumentListPortfolio(
            weekday,
            portfolio,
            json_parameters={"exclude": False, "instrument_lists": [instrument_list.id]},
            thresholds=[rule_threshold],
        )
        a1 = asset_position_factory.create(portfolio=portfolio, date=weekday)
        a2 = asset_position_factory.create(portfolio=portfolio, date=weekday)

        InstrumentListThroughModel.objects.create(
            instrument=a1.underlying_instrument, instrument_list=instrument_list, validated=True
        )
        InstrumentListThroughModel.objects.create(
            instrument=a2.underlying_instrument, instrument_list=instrument_list, validated=True
        )
        # ground truth
        res = list(rule_backend.check_rule())
        assert len(res) == 0

        a3 = asset_position_factory.create(portfolio=portfolio, date=weekday)

        res = list(rule_backend.check_rule())[0]
        assert res.breached_object == a3.underlying_instrument
        assert res.breached_object_repr == str(a3.underlying_instrument)
        assert res.severity == rule_threshold.severity
