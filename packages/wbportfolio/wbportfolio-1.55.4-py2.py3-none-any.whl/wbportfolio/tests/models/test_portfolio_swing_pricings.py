from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from django.db.utils import IntegrityError

if TYPE_CHECKING:
    from wbportfolio.factories.portfolio_swing_pricings import (
        PortfolioSwingPricingFactory,
    )
    from wbportfolio.models.portfolio import Portfolio
    from wbportfolio.models.portfolio_swing_pricings import PortfolioSwingPricing


@pytest.mark.django_db
class TestPortfolioSwingPricing:
    def test_factory(self, portfolio_swing_pricing: "PortfolioSwingPricing"):
        assert portfolio_swing_pricing.pk is not None

    def test_constraint_negative_polarity(self, portfolio_swing_pricing: "PortfolioSwingPricing"):
        portfolio_swing_pricing.negative_threshold = Decimal(0.1)
        portfolio_swing_pricing.negative_swing_factor = Decimal(0.1)

        with pytest.raises(IntegrityError):
            portfolio_swing_pricing.save()

    def test_constraint_positive_polarity(self, portfolio_swing_pricing: "PortfolioSwingPricing"):
        portfolio_swing_pricing.positive_threshold = Decimal(-0.1)
        portfolio_swing_pricing.positive_swing_factor = Decimal(-0.1)

        with pytest.raises(IntegrityError):
            portfolio_swing_pricing.save()

    def test_constraint_unique_valid_date_portfolio(
        self, portfolio: "Portfolio", portfolio_swing_pricing_factory: "PortfolioSwingPricingFactory"
    ):
        swing1 = portfolio_swing_pricing_factory.create(portfolio=portfolio)
        swing2 = portfolio_swing_pricing_factory.create(portfolio=portfolio)

        swing2.valid_date = swing1.valid_date
        with pytest.raises(IntegrityError):
            swing2.save()
