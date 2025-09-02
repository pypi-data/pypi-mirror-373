from typing import Generator

from wbcompliance.models.risk_management import backend
from wbcompliance.models.risk_management.dispatch import register
from wbcompliance.models.risk_management.rules import RiskIncidentType
from wbcore import serializers as wb_serializers
from wbfdm.enums import ESGControveryFlag
from wbfdm.models import Instrument
from wbfdm.models.esg.controversies import Controversy

from wbportfolio.pms.typing import Portfolio as PortfolioDTO

from .mixins import ActivePortfolioRelationshipMixin


@register("Controversy Portfolio Rule Backend", rule_group_key="portfolio")
class RuleBackend(ActivePortfolioRelationshipMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # if thresholds are attached to this rule, we take the first as severity. Otherwise, we get the risk incident with the highest severity (e.g. Critical)
        if self.thresholds:
            self.severity = self.thresholds[0].severity
        else:
            self.severity = RiskIncidentType.objects.order_by("-severity_order").first()
        self.flags_repr = [ESGControveryFlag[f].label for f in self.flags]

    @classmethod
    def get_serializer_class(cls) -> wb_serializers.Serializer:
        class RuleBackendSerializer(wb_serializers.Serializer):
            flags = wb_serializers.MultipleChoiceField(
                choices=ESGControveryFlag.choices,
                default=[ESGControveryFlag.ORANGE.value, ESGControveryFlag.RED.value],
                label="Flags",
                help_text="Set the flags that will trigger the rule",
            )

            @classmethod
            def get_parameter_fields(cls):
                return [
                    "flags",
                ]

        return RuleBackendSerializer

    def _process_dto(self, portfolio: PortfolioDTO, **kwargs) -> Generator[backend.IncidentResult, None, None]:
        for instrument_id, weight in portfolio.positions_map.items():
            instrument = Instrument.objects.get(id=instrument_id)
            if (
                controversies := Controversy.objects.filter(
                    instrument__in=instrument.get_ancestors(include_self=True), flag__in=self.flags
                )
            ).exists():
                controversies_headlines = "".join([f"<li>{c.headline}</li>" for c in controversies])
                yield backend.IncidentResult(
                    breached_object=instrument,
                    breached_object_repr=str(instrument),
                    breached_value=f"# {controversies.count()}",
                    report_details={
                        "Controversies Flags": ", ".join(self.flags_repr),
                        "Controversies Headlines": controversies_headlines,
                    },
                    severity=self.severity,
                )
