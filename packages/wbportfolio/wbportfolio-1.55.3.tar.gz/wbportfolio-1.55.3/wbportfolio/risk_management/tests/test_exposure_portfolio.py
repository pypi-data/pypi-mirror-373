import random

import pytest
from faker import Faker
from psycopg.types.range import NumericRange
from wbcompliance.factories.risk_management import RuleThresholdFactory

from wbportfolio.risk_management.backends.exposure_portfolio import (
    RuleBackend as ExposurePortfolioRuleBackend,
)
from wbportfolio.tests.models.utils import PortfolioTestMixin

fake = Faker()


@pytest.mark.django_db
class TestExposurePortfolioRuleModel(PortfolioTestMixin):
    @pytest.mark.parametrize(
        "group_by",
        [groupby for groupby in ExposurePortfolioRuleBackend.GroupbyChoices.values],
    )
    def test_check_rule_groupby_weighting(
        self,
        weekday,
        group_by,
        instrument_factory,
        cash_factory,
        asset_position_factory,
        instrument_price_factory,
        country_factory,
        currency_factory,
        instrument_type_factory,
        portfolio,
        classification,
    ):
        only_type = instrument_type_factory.create()
        only_country = country_factory.create()
        only_currency = currency_factory.create()
        parameters = {
            "group_by": group_by,
            "field": ExposurePortfolioRuleBackend.Field.WEIGHTING.value,
            "asset_classes": [only_type.id],
            "countries": [only_country.id],
            "currencies": [only_currency.id],
            "classifications": [classification.id],
        }

        lower = random.random()
        upper = random.uniform(lower, 1)
        exposure_portfolio_backend = ExposurePortfolioRuleBackend(
            weekday,
            portfolio,
            parameters,
            [RuleThresholdFactory.create(range=NumericRange(lower=lower, upper=upper))],  # type: ignore
        )

        i1 = instrument_factory.create(
            country=only_country, currency=only_currency, instrument_type=only_type, classifications=[classification]
        )

        threshold = exposure_portfolio_backend.thresholds[0]
        instrument_price_factory.create(instrument=i1, date=weekday)
        asset_position_factory.create(
            date=weekday,
            weighting=random.uniform(threshold.range.lower, threshold.range.upper),
            underlying_instrument=i1,
            portfolio=portfolio,
        )  # Breached position

        asset_position_factory.create(
            date=weekday,
            weighting=random.uniform(threshold.range.lower, threshold.range.upper),
            portfolio=portfolio,
        )  # Breached position but filtered out

        i2 = cash_factory.create()
        instrument_price_factory.create(instrument=i2, date=weekday)
        asset_position_factory.create(
            date=weekday,
            weighting=random.uniform(0, threshold.range.lower),
            underlying_instrument=i2,
            portfolio=portfolio,
        )  # None breached position

        incidents = list(exposure_portfolio_backend.check_rule())
        assert len(incidents) == 1
        if group_by == ExposurePortfolioRuleBackend.GroupbyChoices.CURRENCY:
            assert incidents[0].breached_object == only_currency
        elif group_by == ExposurePortfolioRuleBackend.GroupbyChoices.COUNTRY:
            assert incidents[0].breached_object == only_country
        elif group_by in [
            ExposurePortfolioRuleBackend.GroupbyChoices.PRIMARY_CLASSIFICATION,
            ExposurePortfolioRuleBackend.GroupbyChoices.FAVORITE_CLASSIFICATION,
        ]:
            assert incidents[0].breached_object == classification

    def test_exposure_rule_with_extra_filter_field(
        self, weekday, portfolio, asset_position_factory, instrument_price_factory, instrument_factory
    ):
        parameters = {
            "group_by": "instrument_type",
            "field": ExposurePortfolioRuleBackend.Field.WEIGHTING.value,
            "extra_filter_field": "market_capitalization_usd",
            "extra_filter_field_lower_bound": 1000.0,
            "extra_filter_field_upper_bound": 10000.0,
        }
        exposure_portfolio_backend = ExposurePortfolioRuleBackend(
            weekday,
            portfolio,
            parameters,
            [RuleThresholdFactory.create(range=NumericRange(lower=0.05, upper=None))],  # type: ignore
        )
        i1 = instrument_factory.create()
        i2 = instrument_factory.create(instrument_type=i1.instrument_type)
        i3 = instrument_factory.create(instrument_type=i1.instrument_type)
        instrument_price_factory.create(instrument=i1, date=weekday, market_capitalization=1000)
        instrument_price_factory.create(instrument=i2, date=weekday, market_capitalization=9999)
        instrument_price_factory.create(instrument=i3, date=weekday, market_capitalization=10001)
        asset_position_factory.create(
            date=weekday,
            weighting=0.025,
            underlying_instrument=i1,
            portfolio=portfolio,
        )
        asset_position_factory.create(
            date=weekday,
            weighting=0.025,
            underlying_instrument=i2,
            portfolio=portfolio,
        )

        asset_position_factory.create(
            date=weekday,
            weighting=0.95,
            underlying_instrument=i3,
            portfolio=portfolio,
        )
        incidents = list(exposure_portfolio_backend.check_rule())
        assert len(incidents) == 1
        incident = incidents[0]
        assert incident.breached_object_repr == i1.instrument_type
        assert incident.breached_value == '<span style="color:green">+5.00%</span>'
