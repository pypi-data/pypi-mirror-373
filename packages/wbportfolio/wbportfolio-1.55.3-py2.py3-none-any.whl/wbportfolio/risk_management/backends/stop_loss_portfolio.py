from typing import Generator

from wbcompliance.models.risk_management import backend
from wbcompliance.models.risk_management.dispatch import register

from wbportfolio.pms.typing import Portfolio as PortfolioDTO
from wbportfolio.pms.typing import Valuation as ValuationDTO

from .mixins import ActiveProductRelationshipMixin, StopLossMixin


@register("Stop Loss Portfolio Rule Backend", rule_group_key="portfolio")
class RuleBackend(ActiveProductRelationshipMixin, StopLossMixin, backend.AbstractRuleBackend):
    def _build_dto_args(self) -> tuple[PortfolioDTO, ValuationDTO | None]:
        return (
            self.portfolio._build_dto(self.evaluation_date),
            super()._build_dto_args()[1],
        )

    def is_passive_evaluation_valid(self) -> bool:
        return (
            super().is_passive_evaluation_valid()
            and self.portfolio
            and self.portfolio.assets.filter(date=self.evaluation_date).exists()
        )

    def _process_dto(
        self, portfolio: PortfolioDTO, benchmark_valuation_dto: ValuationDTO = None, **kwargs
    ) -> Generator[backend.IncidentResult, None, None]:
        if self.asset_class:
            portfolio = PortfolioDTO(filter(lambda x: x.instrument_type == self.asset_class.id, portfolio.positions))
        perf_benchmark = self._get_performance(benchmark_valuation_dto)
        for instrument_id, pos in portfolio.positions_map.items():
            if pos.price is not None:
                perf_instrument = self._get_performance(ValuationDTO(instrument=instrument_id, net_value=pos.price))

                yield from self._generate_incidents(instrument_id, perf_instrument, perf_benchmark)
