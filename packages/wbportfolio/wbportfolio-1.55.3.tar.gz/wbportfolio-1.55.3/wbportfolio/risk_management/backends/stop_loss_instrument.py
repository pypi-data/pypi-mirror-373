from typing import Generator

from wbcompliance.models.risk_management import backend
from wbcompliance.models.risk_management.dispatch import register

from wbportfolio.pms.typing import Valuation as ValuationDTO

from .mixins import ActiveProductRelationshipMixin, StopLossMixin


@register("Stop Loss Instrument Rule Backend", rule_group_key="portfolio")
class RuleBackend(ActiveProductRelationshipMixin, StopLossMixin, backend.AbstractRuleBackend):
    def is_passive_evaluation_valid(self) -> bool:
        return (
            super().is_passive_evaluation_valid()
            and self.product
            and self.product.valuations.filter(date=self.evaluation_date).exists()
        )

    def _process_dto(
        self, instrument_valuation_dto: ValuationDTO, benchmark_valuation_dto: ValuationDTO = None, *args, **kwargs
    ) -> Generator[backend.IncidentResult, None, None]:
        perf_instrument = self._get_performance(instrument_valuation_dto)
        perf_benchmark = self._get_performance(benchmark_valuation_dto)
        yield from self._generate_incidents(self.product.id, perf_instrument, perf_benchmark)
