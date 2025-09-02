from typing import Generator

from django.db.models import Q
from wbcompliance.models.risk_management import backend
from wbcompliance.models.risk_management.dispatch import register
from wbcore import serializers as wb_serializers
from wbfdm.models import Instrument, InstrumentList, InstrumentListThroughModel
from wbfdm.serializers.instruments.instrument_lists import (
    InstrumentListRepresentationSerializer,
)

from wbportfolio.pms.typing import Portfolio as PortfolioDTO

from .mixins import ActivePortfolioRelationshipMixin


@register("Instrument List Portfolio Rule Backend", rule_group_key="portfolio")
class RuleBackend(ActivePortfolioRelationshipMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instrument_list_type:
            self.instrument_lists = InstrumentList.objects.filter(instrument_list_type=self.instrument_list_type)
        self.instruments_relationship = InstrumentListThroughModel.objects.filter(
            Q(instrument_list__in=self.instrument_lists)
            & (Q(from_date__isnull=True) | Q(from_date__lte=self.evaluation_date))
            & (Q(to_date__isnull=True) | Q(to_date__gt=self.evaluation_date))
        )
        self.instrument_lists_repr = " ,".join(map(lambda x: x.name, self.instrument_lists))
        self.severity = self.thresholds[0].severity

    @classmethod
    def get_serializer_class(cls) -> wb_serializers.Serializer:
        class RuleBackendSerializer(wb_serializers.Serializer):
            exclude = wb_serializers.BooleanField(
                default=True,
                label="Exclude",
                help_text="If true, the rule will check that the portfolio composition DOES NOT intersect the given instrument list",
            )
            instrument_list_type = wb_serializers.ChoiceField(
                choices=InstrumentList.InstrumentListType.choices,
                required=False,
                default=None,
                allow_null=True,
                help_text="If specified, will dynamically load the list of instrument list to check of the same specified type",
                label="Instrument List Type",
            )
            instrument_lists = wb_serializers.PrimaryKeyRelatedField(
                queryset=InstrumentList.objects.all(),
                many=True,
                default=None,
                allow_null=True,
                label="Instrument Lists",
            )
            _instrument_lists = InstrumentListRepresentationSerializer(many=True)

            @classmethod
            def get_parameter_fields(cls):
                return [
                    "exclude",
                    "instrument_list_type",
                    "instrument_lists",
                ]

        return RuleBackendSerializer

    def _process_dto(self, portfolio: PortfolioDTO, **kwargs) -> Generator[backend.IncidentResult, None, None]:
        for instrument_id, weight in portfolio.positions_map.items():
            instrument = Instrument.objects.get(id=instrument_id)
            relationships = self.instruments_relationship.filter(instrument=instrument, validated=True)

            if self.exclude and relationships.exists():
                report_details = {
                    "Instrument Lists": ", ".join(relationships.values_list("instrument_list__name", flat=True)),
                }
                yield backend.IncidentResult(
                    breached_object=instrument,
                    breached_object_repr=str(instrument),
                    breached_value=f"# {relationships.count()}",
                    report_details=report_details,
                    severity=self.severity,
                )
            elif not self.exclude and not relationships.exists():
                report_details = {"Instrument Lists": self.instrument_lists_repr}
                yield backend.IncidentResult(
                    breached_object=instrument,
                    breached_object_repr=str(instrument),
                    breached_value=f"# {relationships.count()}",
                    report_details=report_details,
                    severity=self.severity,
                )
