from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from wbfdm.models import InstrumentPrice

from wbportfolio.pms.typing import Portfolio, Position
from wbportfolio.rebalancing.base import AbstractRebalancingModel
from wbportfolio.rebalancing.decorators import register


@register("Composite Rebalancing")
class CompositeRebalancing(AbstractRebalancingModel):
    @property
    def base_assets(self) -> dict[int, Decimal]:
        """
        Return a dictionary representation (instrument_id: target weight) of this order proposal
        Returns:
            A dictionary representation

        """
        try:
            latest_order_proposal = self.portfolio.order_proposals.filter(
                status="APPLIED", trade_date__lt=self.trade_date
            ).latest("trade_date")
            return {
                v["underlying_instrument"]: v["target_weight"]
                for v in latest_order_proposal.get_orders().values("underlying_instrument", "target_weight")
            }
        except ObjectDoesNotExist:
            return dict()

    def is_valid(self) -> bool:
        return (
            len(self.base_assets.keys()) > 0
            and InstrumentPrice.objects.filter(date=self.trade_date, instrument__in=self.base_assets.keys()).exists()
        )

    def get_target_portfolio(self) -> Portfolio:
        positions = []
        for underlying_instrument, weighting in self.base_assets.items():
            positions.append(
                Position(underlying_instrument=underlying_instrument, weighting=weighting, date=self.trade_date)
            )
        return Portfolio(positions=tuple(positions))
