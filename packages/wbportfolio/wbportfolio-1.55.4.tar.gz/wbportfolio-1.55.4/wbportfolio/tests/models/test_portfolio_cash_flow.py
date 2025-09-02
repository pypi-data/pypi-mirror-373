from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest
from django.db.utils import IntegrityError

if TYPE_CHECKING:
    from wbportfolio.factories import DailyPortfolioCashFlowFactory
    from wbportfolio.models.portfolio import Portfolio
    from wbportfolio.models.portfolio_cash_flow import DailyPortfolioCashFlow
    from wbportfolio.models.portfolio_cash_targets import PortfolioCashTarget


@pytest.mark.django_db
class TestDailyPortfolioCashFlowFactory:
    def test_factory(self, daily_portfolio_cash_flow: "DailyPortfolioCashFlow"):
        assert daily_portfolio_cash_flow.pk is not None

    def test_constraint_unique_value_date_portfolio(
        self, portfolio: "Portfolio", daily_portfolio_cash_flow_factory: "DailyPortfolioCashFlowFactory"
    ):
        cf1 = daily_portfolio_cash_flow_factory.create(portfolio=portfolio)
        cf2 = daily_portfolio_cash_flow_factory.create(portfolio=portfolio)

        cf2.value_date = cf1.value_date
        with pytest.raises(IntegrityError):
            cf2.save()

    @pytest.mark.parametrize("daily_portfolio_cash_flow__pending", [False])
    def test_estimated_total_assets(self, daily_portfolio_cash_flow: "DailyPortfolioCashFlow"):
        dpcf = daily_portfolio_cash_flow
        assert dpcf.estimated_total_assets == dpcf.total_assets

    @pytest.mark.parametrize("daily_portfolio_cash_flow__pending", [True])
    def test_estimated_total_assets_while_pending(self, daily_portfolio_cash_flow: "DailyPortfolioCashFlow"):
        dpcf = daily_portfolio_cash_flow
        assert dpcf.estimated_total_assets == dpcf.total_assets + dpcf.cash_flow_forecast

    def test_cash_flow_asset_ratio(self, daily_portfolio_cash_flow: "DailyPortfolioCashFlow"):
        dpcf = daily_portfolio_cash_flow
        assert dpcf.cash_flow_asset_ratio == pytest.approx(
            dpcf.cash_flow_forecast / dpcf.estimated_total_assets, rel=Decimal(1e-4)
        )

    @pytest.mark.parametrize("daily_portfolio_cash_flow__total_assets", [Decimal(0)])
    @pytest.mark.parametrize("daily_portfolio_cash_flow__cash_flow_forecast", [Decimal(0)])
    def test_cash_flow_asset_ratio_zero_assets(self, daily_portfolio_cash_flow: "DailyPortfolioCashFlow"):
        assert daily_portfolio_cash_flow.cash_flow_asset_ratio == Decimal(0)

    def test_cash_pct(self, daily_portfolio_cash_flow: "DailyPortfolioCashFlow"):
        dpct = daily_portfolio_cash_flow
        assert dpct.cash_pct == pytest.approx(dpct.cash / dpct.estimated_total_assets, rel=Decimal(1e-4))

    @pytest.mark.parametrize("daily_portfolio_cash_flow__total_assets", [Decimal(0)])
    @pytest.mark.parametrize("daily_portfolio_cash_flow__cash_flow_forecast", [Decimal(0)])
    def test_cash_pct_zero_assets(self, daily_portfolio_cash_flow: "DailyPortfolioCashFlow"):
        assert daily_portfolio_cash_flow.cash_pct == Decimal(0)

    def test_true_cash(self, daily_portfolio_cash_flow: "DailyPortfolioCashFlow"):
        dpct = daily_portfolio_cash_flow
        assert dpct.true_cash == pytest.approx(dpct.cash + dpct.cash_flow_forecast, rel=Decimal(1e-4))

    def test_true_cash_pct(self, daily_portfolio_cash_flow: "DailyPortfolioCashFlow"):
        dpct = daily_portfolio_cash_flow
        assert dpct.true_cash_pct == pytest.approx(dpct.true_cash / dpct.estimated_total_assets, rel=Decimal(1e-4))

    @pytest.mark.parametrize("daily_portfolio_cash_flow__total_assets", [Decimal(0)])
    @pytest.mark.parametrize("daily_portfolio_cash_flow__cash_flow_forecast", [Decimal(0)])
    def test_true_cash_pct_zero_assets(self, daily_portfolio_cash_flow: "DailyPortfolioCashFlow"):
        assert daily_portfolio_cash_flow.true_cash_pct == Decimal(0)

    def test_target_cash_no_target(self, daily_portfolio_cash_flow: "DailyPortfolioCashFlow"):
        dpct = daily_portfolio_cash_flow
        assert dpct.target_cash == Decimal(0)

    def test_target_cash(
        self, daily_portfolio_cash_flow: "DailyPortfolioCashFlow", portfolio_cash_target: "PortfolioCashTarget"
    ):
        dpct = daily_portfolio_cash_flow
        portfolio_cash_target.portfolio = dpct.portfolio
        portfolio_cash_target.valid_date = dpct.value_date
        portfolio_cash_target.save()
        dpct.save()
        dpct.refresh_from_db()
        assert dpct.target_cash == pytest.approx(portfolio_cash_target.target * dpct.estimated_total_assets)

    def test_excess_cash(
        self, daily_portfolio_cash_flow: "DailyPortfolioCashFlow", portfolio_cash_target: "PortfolioCashTarget"
    ):
        dpct = daily_portfolio_cash_flow
        portfolio_cash_target.portfolio = dpct.portfolio
        portfolio_cash_target.valid_date = dpct.value_date
        portfolio_cash_target.save()
        dpct.save()
        dpct.refresh_from_db()
        assert dpct.excess_cash == pytest.approx(dpct.true_cash - dpct.target_cash, rel=Decimal(1e-4))

    def test_cash_from_yesterday(
        self, portfolio: "Portfolio", daily_portfolio_cash_flow_factory: "DailyPortfolioCashFlowFactory"
    ):
        cf1 = daily_portfolio_cash_flow_factory.create(portfolio=portfolio, value_date=date(2020, 1, 1))
        cf2 = daily_portfolio_cash_flow_factory.create(
            portfolio=portfolio, value_date=date(2020, 1, 2), pending=True, rebalancing=Decimal(0)
        )
        cf1.refresh_from_db()
        cf2.refresh_from_db()
        assert cf2.cash == pytest.approx(cf1.true_cash, rel=Decimal(1e-4))

    @pytest.mark.parametrize("daily_portfolio_cash_flow__cash", [Decimal(1_000_000)])
    @pytest.mark.parametrize("daily_portfolio_cash_flow__pending", [True])
    def test_rebalancing(self, daily_portfolio_cash_flow: "DailyPortfolioCashFlow"):
        dpcf = daily_portfolio_cash_flow
        assert dpcf.cash == Decimal(1_000_000) - dpcf.rebalancing
