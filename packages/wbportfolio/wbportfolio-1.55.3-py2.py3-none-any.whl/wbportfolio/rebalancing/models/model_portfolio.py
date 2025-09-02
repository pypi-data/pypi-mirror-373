from wbportfolio.pms.typing import Portfolio
from wbportfolio.rebalancing.base import AbstractRebalancingModel
from wbportfolio.rebalancing.decorators import register


@register("Model Portfolio Rebalancing")
class ModelPortfolioRebalancing(AbstractRebalancingModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value_date = (
            self.trade_date
            if self.model_portfolio.assets.filter(date=self.trade_date).exists()
            else self.last_effective_date
        )

    @property
    def model_portfolio_rel(self):
        return self.portfolio.dependency_through.filter(type="MODEL").first()

    @property
    def model_portfolio(self):
        return self.model_portfolio_rel.dependency_portfolio if self.model_portfolio_rel else None

    @property
    def assets(self):
        return self.model_portfolio.get_positions(self.value_date) if self.model_portfolio else []

    def is_valid(self) -> bool:
        return len(self.assets) > 0

    def get_target_portfolio(self) -> Portfolio:
        positions = []
        for asset in self.assets:
            asset.date = self.value_date
            asset.asset_valuation_date = self.value_date
            positions.append(asset._build_dto())
        return Portfolio(positions=tuple(positions))
