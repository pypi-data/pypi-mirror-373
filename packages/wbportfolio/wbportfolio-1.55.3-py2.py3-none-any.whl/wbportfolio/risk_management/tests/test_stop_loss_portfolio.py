import random
from decimal import Decimal

import pytest
from faker import Faker
from pandas._libs.tslibs.offsets import BDay
from psycopg.types.range import NumericRange
from wbcompliance.factories.risk_management import RuleThresholdFactory

from wbportfolio.risk_management.backends.stop_loss_portfolio import (
    RuleBackend as StopLossPortfolioRuleBackend,
)
from wbportfolio.tests.models.utils import PortfolioTestMixin

fake = Faker()


@pytest.mark.django_db
class TestStopLossPortfolioRuleModel(PortfolioTestMixin):
    @pytest.fixture
    def stop_loss_portfolio_backend(self, weekday, date_interval_option, freq, product):
        parameters = {"freq": freq, "date_interval_option": date_interval_option}
        lower = random.random()
        upper = random.uniform(lower, 1)
        return StopLossPortfolioRuleBackend(
            weekday,
            product,
            parameters,
            [RuleThresholdFactory.create(range=NumericRange(lower=lower, upper=upper))],  # type: ignore
        )

    @pytest.mark.parametrize(
        "date_interval_option, freq",
        [
            ("ROLLING_WINDOWS", StopLossPortfolioRuleBackend.FreqChoices.BUSINESS_DAY),
            *[("FREQUENCY", option) for option in StopLossPortfolioRuleBackend.FreqChoices.values],
        ],
    )
    def test_check_rule_frequency(
        self,
        weekday,
        date_interval_option,
        freq,
        product,
        instrument,
        instrument_price_factory,
        asset_position_factory,
        stop_loss_portfolio_backend,
    ):
        previous_date = (weekday - BDay(1)).date()

        d1 = stop_loss_portfolio_backend._get_start_interval()

        threshold = stop_loss_portfolio_backend.thresholds[0]
        breach_perf = random.uniform(threshold.range.lower, threshold.range.upper)

        instrument_price_factory.create(date=d1, net_value=100, calculated=False, instrument=product)
        instrument_price_factory.create(date=previous_date, net_value=100, calculated=False, instrument=product)
        instrument_price_factory.create(date=weekday, net_value=100, calculated=False, instrument=product)

        i1 = instrument_price_factory.create(date=d1, net_value=100, calculated=False, instrument=instrument)
        instrument_price_factory.create(date=previous_date, calculated=False, instrument=instrument)
        i2 = instrument_price_factory.create(
            date=weekday, net_value=Decimal(breach_perf + 1) * i1.net_value, calculated=False, instrument=instrument
        )

        previous_position = asset_position_factory.create(
            date=previous_date, underlying_instrument=instrument, portfolio=product.portfolio
        )
        asset_position_factory.create(date=weekday, underlying_instrument=instrument, portfolio=product.portfolio)

        expected_performance = i2.net_value / i1.net_value - Decimal(1.0)
        res = list(stop_loss_portfolio_backend.check_rule())
        assert len(res) == 1
        incident = res[0]
        assert incident.breached_object.id == instrument.id
        assert incident.breached_value == f'<span style="color:green">{expected_performance:+,.2%}</span>'
        assert incident.report_details == {
            "Field": "Net Value",
            "Portfolio Impact": f"{previous_position.weighting * expected_performance:+,.2%}",
        }

    @pytest.mark.parametrize(
        "date_interval_option, freq",
        [
            ("ROLLING_WINDOWS", StopLossPortfolioRuleBackend.FreqChoices.BUSINESS_DAY),
            *[("FREQUENCY", option) for option in StopLossPortfolioRuleBackend.FreqChoices.values],
        ],
    )
    def test_check_rule_frequency_2(
        self,
        weekday,
        date_interval_option,
        freq,
        product,
        instrument_price_factory,
        asset_position_factory,
        instrument_factory,
        stop_loss_portfolio_backend,
    ):
        d1 = stop_loss_portfolio_backend._get_start_interval()
        benchmark = instrument_factory.create()
        instrument = instrument_factory.create()

        threshold = stop_loss_portfolio_backend.thresholds[0]
        threshold.range = NumericRange(upper=-0.5, lower=None)  # type: ignore
        threshold.save()

        instrument_price_factory.create(date=weekday, net_value=100, calculated=False, instrument=product)

        instrument_price_factory.create(date=d1, net_value=100, calculated=False, instrument=instrument)
        instrument_price_factory.create(date=weekday, net_value=100, calculated=False, instrument=instrument)

        instrument_price_factory.create(date=d1, net_value=100, calculated=False, instrument=benchmark)
        instrument_price_factory.create(date=weekday, net_value=300, calculated=False, instrument=benchmark)

        asset_position_factory.create(date=weekday, underlying_instrument=instrument, portfolio=product.portfolio)

        res = list(stop_loss_portfolio_backend.check_rule())
        assert len(res) == 0

        setattr(stop_loss_portfolio_backend, "static_benchmark", benchmark)
        res = list(stop_loss_portfolio_backend.check_rule())
        assert len(res) == 1
        assert res[0].breached_object.id == instrument.id
