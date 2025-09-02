from typing import Generator

from django.contrib.contenttypes.models import ContentType
from wbcompliance.models.risk_management import backend
from wbcompliance.models.risk_management.dispatch import register
from wbcore import serializers as wb_serializers
from wbcore.serializers.fields.number import percent_decorator
from wbfdm.models import Instrument

from wbportfolio.pms.typing import Portfolio as PortfolioDTO

from .mixins import ActiveProductRelationshipMixin


@register("Liquidity Stress Instrument Rule Backend", rule_group_key="portfolio")
class RuleBackend(ActiveProductRelationshipMixin, backend.AbstractRuleBackend):
    @classmethod
    def get_parameter_fields(cls):
        return [
            "group_by",
            "field",
            "is_cash",
            "asset_classes",
            "currencies",
            "countries",
            "classification_height",
            "classifications",
        ]

    @classmethod
    def get_serializer_class(cls) -> wb_serializers.Serializer:
        class RuleBackendSerializer(wb_serializers.Serializer):
            below_x_days = wb_serializers.IntegerField(default=5, label="Below X days")
            liquidity_factor = wb_serializers.FloatField(default=0.33, label="Liquidity factory")
            pct_worst_volume = wb_serializers.FloatField(
                default=100.0, label="Worst volume (%)", percent=True, decorators=[percent_decorator]
            )
            pct_redemption = wb_serializers.FloatField(
                default=100.0, label="Redemption (%)", percent=True, decorators=[percent_decorator]
            )
            last_x_trading_dates = wb_serializers.IntegerField(default=60, label="Number of trading days")
            is_slicing = wb_serializers.BooleanField(default=True, label="Slicing")

            @classmethod
            def get_parameter_fields(cls):
                return [
                    "below_x_days",
                    "liquidity_factor",
                    "pct_worst_volume",
                    "pct_redemption",
                    "last_x_trading_dates",
                    "is_slicing",
                ]

        return RuleBackendSerializer

    def _process_dto(self, portfolio: PortfolioDTO, **kwargs) -> Generator[backend.IncidentResult, None, None]:
        # TODO adapt to DTO framework
        factor = self.instrument.pct_liquidated_below_n_days(
            self.evaluation_date,
            below_n_days=self.below_x_days,
            liq_factor=self.liquidity_factor,
            pct_worst_volume=self.pct_worst_volume,
            pct_redemption=self.pct_redemption,
            last_x_trading_dates=self.last_x_trading_dates,
            is_slicing=self.is_slicing,
        )
        for threshold in self.thresholds:
            if factor is not None and threshold.is_inrange(factor):
                yield backend.IncidentResult(
                    breached_object=self.instrument,
                    breached_object_repr=str(self.instrument),
                    breached_value=str(factor),
                    report_details=dict(),
                    severity=threshold.severity,
                )

    @classmethod
    def get_allowed_content_type(cls) -> "ContentType":
        return ContentType.objects.get_for_model(Instrument)

    def is_passive_evaluation_valid(self) -> bool:
        if not self.instrument.portfolio:
            return False
        return (self.instrument.portfolio.imported_assets.filter(date=self.evaluation_date).exists()) and (
            self.instrument.valuations.filter(date=self.evaluation_date).exists()
        )
