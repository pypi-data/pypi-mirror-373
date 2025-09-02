from decimal import Decimal

from wbfdm.models import InstrumentPrice

from wbportfolio.pms.typing import Portfolio
from wbportfolio.rebalancing.base import AbstractRebalancingModel
from wbportfolio.rebalancing.decorators import register


@register("Equally Weighted Rebalancing")
class EquallyWeightedRebalancing(AbstractRebalancingModel):
    def __init__(self, *args, **kwargs):
        super(EquallyWeightedRebalancing, self).__init__(*args, **kwargs)
        if not self.effective_portfolio:
            self.effective_portfolio = self.portfolio._build_dto(self.trade_date)

    def is_valid(self) -> bool:
        return (
            len(self.effective_portfolio.positions) > 0
            and InstrumentPrice.objects.filter(
                date=self.trade_date, instrument__in=self.effective_portfolio.positions_map.keys()
            ).exists()
        )

    def get_target_portfolio(self) -> Portfolio:
        positions = []
        assets = list(filter(lambda p: not p.is_cash, self.effective_portfolio.positions))
        for position in assets:
            positions.append(
                position.copy(
                    weighting=Decimal(1 / len(assets)), date=self.trade_date, asset_valuation_date=self.trade_date
                )
            )
        return Portfolio(positions)
