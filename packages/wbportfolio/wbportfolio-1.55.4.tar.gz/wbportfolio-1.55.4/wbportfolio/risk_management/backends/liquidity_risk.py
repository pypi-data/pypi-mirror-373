from contextlib import suppress
from math import ceil
from typing import Generator

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Exists, OuterRef, Sum
from wbcompliance.models.risk_management import backend
from wbcompliance.models.risk_management.dispatch import register
from wbcore import serializers as wb_serializers
from wbfdm.models import Instrument, InstrumentPrice

from wbportfolio.models import AssetPosition


@register("Liquidity Risk", rule_group_key="portfolio")
class RuleBackend(backend.AbstractRuleBackend):
    OBJECT_FIELD_NAME: str = "instrument"

    instrument: Instrument

    def get_queryset(self):
        return self.instrument.assets.filter(
            date=self.evaluation_date, shares__isnull=False, is_invested=True
        ).exclude(shares=0)

    def is_passive_evaluation_valid(self) -> bool:
        return self.get_queryset().exists()

    @classmethod
    def get_allowed_content_type(cls) -> "ContentType":
        return ContentType.objects.get_for_model(Instrument)

    def _build_dto_args(self):
        with suppress(InstrumentPrice.DoesNotExist):
            last_price = self.instrument.valuations.get(date=self.evaluation_date)
            total_shares = self.get_queryset().aggregate(c=Sum("shares"))["c"]
            if last_price.volume_50d and total_shares:
                return float(total_shares), last_price.volume_50d
        return tuple()

    @classmethod
    def get_all_active_relationships(cls) -> models.QuerySet:
        try:
            base_qs = AssetPosition.objects.filter(shares__isnull=False, is_invested=True).exclude(shares=0)
            last_asset_position = base_qs.latest("date").date

            return Instrument.objects.annotate(
                has_assets=Exists(base_qs.filter(underlying_instrument=OuterRef("pk"), date=last_asset_position))
            ).filter(has_assets=True, children__isnull=True)
        except AssetPosition.DoesNotExist:
            return Instrument.objects.none()

    @classmethod
    def get_serializer_class(cls) -> wb_serializers.Serializer:
        class RuleBackendSerializer(wb_serializers.Serializer):
            liquidation_factor = wb_serializers.FloatField(default=3.0, label="Liquidation Factor")
            redemption_pct = wb_serializers.FloatField(default=0.80, label="Redemption Percentage", percent=True)

            @classmethod
            def get_parameter_fields(cls):
                return [
                    "liquidation_factor",
                    "redemption_pct",
                ]

        return RuleBackendSerializer

    def _process_dto(
        self, total_shares: float, volume_50d: float, **kwargs
    ) -> Generator[backend.IncidentResult, None, None]:
        days_to_liquidate = (total_shares * self.redemption_pct * self.liquidation_factor) / volume_50d
        for threshold in self.thresholds:
            numerical_range = threshold.numerical_range
            if days_to_liquidate >= numerical_range[0] and days_to_liquidate < numerical_range[1]:
                yield backend.IncidentResult(
                    breached_object=self.instrument,
                    breached_object_repr=str(self.instrument),
                    breached_value=f"{ceil(days_to_liquidate)} Days",
                    report_details={
                        "Volume 50D": volume_50d,
                        "Total Shares": total_shares,
                        "Redemption Percentage": f"{self.redemption_pct:.1%}",
                        "Liquidation Factor": self.liquidation_factor,
                    },
                    severity=threshold.severity,
                )
