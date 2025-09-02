import random
from decimal import Decimal

import pytest
from faker import Faker
from psycopg.types.range import NumericRange
from wbcompliance.factories.risk_management import RuleThresholdFactory
from wbfdm.models import RelatedInstrumentThroughModel

from wbportfolio.risk_management.backends.stop_loss_instrument import (
    RuleBackend as StopLossInstrumentRuleBackend,
)
from wbportfolio.tests.models.utils import PortfolioTestMixin

fake = Faker()


@pytest.mark.django_db
class TestStopLossInstrumentRuleModel(PortfolioTestMixin):
    @pytest.fixture
    def stop_loss_instrument_backend(self, weekday, date_interval_option, freq, product):
        parameters = {"freq": freq, "date_interval_option": date_interval_option}
        lower = random.random()
        upper = random.uniform(lower, 1)
        return StopLossInstrumentRuleBackend(
            weekday,
            product,
            parameters,
            [RuleThresholdFactory.create(range=NumericRange(lower=lower, upper=upper))],  # type: ignore
        )

    @pytest.mark.parametrize(
        "date_interval_option, freq",
        [
            ("ROLLING_WINDOWS", StopLossInstrumentRuleBackend.FreqChoices.BUSINESS_DAY),
            *[("FREQUENCY", option) for option in StopLossInstrumentRuleBackend.FreqChoices.values],
        ],
    )
    def test_check_rule_frequency(
        self,
        weekday,
        date_interval_option,
        freq,
        product,
        instrument_price_factory,
        stop_loss_instrument_backend,
    ):
        d1 = stop_loss_instrument_backend._get_start_interval()
        threshold = stop_loss_instrument_backend.thresholds[0]

        breach_perf = random.uniform(threshold.range.lower, threshold.range.upper)

        i1 = instrument_price_factory.create(date=d1, net_value=100, calculated=False, instrument=product)
        instrument_price_factory.create(
            date=weekday, net_value=Decimal(breach_perf + 1) * i1.net_value, calculated=False, instrument=product
        )

        res = list(stop_loss_instrument_backend.check_rule())
        assert len(res) == 1
        assert res[0].breached_object.id == product.id

    @pytest.mark.parametrize(
        "date_interval_option, freq",
        [
            ("FREQUENCY", StopLossInstrumentRuleBackend.FreqChoices.WEEKLY_FRIDAY),
            ("ROLLING_WINDOWS", StopLossInstrumentRuleBackend.FreqChoices.WEEKLY_FRIDAY),
        ],
    )
    def test_check_rule_frequency_with_benchmark(
        self,
        weekday,
        date_interval_option,
        freq,
        product,
        instrument_factory,
        instrument_price_factory,
        stop_loss_instrument_backend,
    ):
        benchmark = instrument_factory.create()

        threshold = stop_loss_instrument_backend.thresholds[0]
        threshold.range = NumericRange(upper=-0.5, lower=None)  # type: ignore
        threshold.save()

        d1 = stop_loss_instrument_backend._get_start_interval()

        instrument_price_factory.create(date=d1, net_value=100, calculated=False, instrument=product)
        instrument_price_factory.create(date=weekday, net_value=100, calculated=False, instrument=product)

        instrument_price_factory.create(date=d1, net_value=500, calculated=False, instrument=benchmark)
        benchmark_price_2 = instrument_price_factory.create(
            date=weekday, net_value=500, calculated=False, instrument=benchmark
        )
        RelatedInstrumentThroughModel.objects.create(instrument=product, related_instrument=benchmark, is_primary=True)
        setattr(stop_loss_instrument_backend, "dynamic_benchmark_type", "PRIMARY_BENCHMARK")

        res = list(stop_loss_instrument_backend.check_rule())
        assert len(res) == 0

        # artificially
        benchmark_price_2.net_value = 1000
        benchmark_price_2.save()

        res = list(stop_loss_instrument_backend.check_rule())
        assert len(res) == 1
        assert res[0].breached_object.id == product.id

        setattr(stop_loss_instrument_backend, "static_benchmark", benchmark)
        res = list(stop_loss_instrument_backend.check_rule())
        assert len(res) == 1
        assert res[0].breached_object.id == product.id
