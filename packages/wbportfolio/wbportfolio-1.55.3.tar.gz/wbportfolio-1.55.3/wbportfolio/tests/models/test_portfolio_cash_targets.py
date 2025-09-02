from typing import TYPE_CHECKING

import pytest
from django.db.utils import IntegrityError

if TYPE_CHECKING:
    from wbportfolio.factories.portfolio_swing_pricings import (
        PortfolioCashTargetFactory,
    )
    from wbportfolio.models.portfolio import Portfolio
    from wbportfolio.models.portfolio_swing_pricings import PortfolioCashTarget


@pytest.mark.django_db
class TestPortfolioCashTarget:
    def test_factory(self, portfolio_cash_target: "PortfolioCashTarget"):
        assert portfolio_cash_target.pk is not None

    def test_constraint_unique_valid_date_portfolio(
        self, portfolio: "Portfolio", portfolio_cash_target_factory: "PortfolioCashTargetFactory"
    ):
        target1 = portfolio_cash_target_factory.create(portfolio=portfolio)
        target2 = portfolio_cash_target_factory.create(portfolio=portfolio)

        target2.valid_date = target1.valid_date
        with pytest.raises(IntegrityError):
            target2.save()
