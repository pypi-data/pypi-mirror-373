from contextlib import suppress
from datetime import date, timedelta
from decimal import Decimal
from typing import Generator

import pandas as pd
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Sum
from pandas.tseries.offsets import BDay
from wbcompliance.models.risk_management import backend
from wbcore import serializers as wb_serializers
from wbfdm.backends.dto import PriceDTO
from wbfdm.models import Instrument, InstrumentPrice, InstrumentType
from wbfdm.serializers import (
    InstrumentTypeRepresentationSerializer,
    SecurityRepresentationSerializer,
)

from wbportfolio.models import AssetPosition, InstrumentPortfolioThroughModel, Portfolio


class ActivePortfolioRelationshipMixin(backend.AbstractRuleBackend):
    OBJECT_FIELD_NAME: str = "portfolio"

    portfolio: Portfolio

    def is_passive_evaluation_valid(self) -> bool:
        return self.portfolio.imported_assets.filter(date=self.evaluation_date).exists()

    @classmethod
    def get_allowed_content_type(cls) -> "ContentType":
        return ContentType.objects.get_for_model(Portfolio)

    def _build_dto_args(self):
        return (self.portfolio._build_dto(self.evaluation_date, is_estimated=False),)

    @classmethod
    def get_all_active_relationships(cls) -> models.QuerySet:
        valid_relationships = InstrumentPortfolioThroughModel.objects.filter(
            instrument__instrument_type__key="product"
        ).values("portfolio")
        return Portfolio.objects.filter(id__in=valid_relationships, is_tracked=True)


class ActiveProductRelationshipMixin(backend.AbstractRuleBackend):
    OBJECT_FIELD_NAME: str = "product"

    @classmethod
    def get_allowed_content_type(cls) -> "ContentType":
        return ContentType.objects.get_for_model(Instrument)

    @classmethod
    def get_all_active_relationships(cls) -> models.QuerySet:
        return Instrument.active_objects.filter(instrument_type__key="product")


class StopLossMixin(backend.AbstractRuleBackend):
    class FreqChoices(models.TextChoices):
        BUSINESS_DAY = "B", "Business Day"
        WEEKLY_FRIDAY = "W-FRI", "Friday to Friday"
        BUSINESS_MONTHLY = "BME", "Business Monthly"
        BUSINESS_YEARLY = "BYE", "Business Yearly"

    class DateIntervalOption(models.TextChoices):
        ROLLING_WINDOWS = "ROLLING_WINDOWS", "Rolling Window"
        FREQUENCY = "FREQUENCY", "Frequency"

    class DynamicBenchmarkType(models.TextChoices):
        PORTFOLIO = "PORTFOLIO", "Primary Portfolio"
        PRIMARY_BENCHMARK = "PRIMARY_BENCHMARK", "Primary Benchmark"

    class FieldType(models.TextChoices):
        OUTSTANDING_SHARES = "outstanding_shares", "Outstanding shares"
        NET_VALUE = "net_value", "Net Value"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.portfolio = self.product.portfolio

    @classmethod
    def get_serializer_class(cls) -> wb_serializers.Serializer:
        class RuleBackendSerializer(wb_serializers.Serializer):
            freq = wb_serializers.ChoiceField(
                choices=cls.FreqChoices,
                default=cls.FreqChoices.WEEKLY_FRIDAY,
                label="Frequency",
                help_text="Valid only if the interval Option is Frequency. Specify the frequency use for aggregation",
            )
            date_interval_option = wb_serializers.ChoiceField(
                choices=cls.DateIntervalOption,
                default=cls.DateIntervalOption.ROLLING_WINDOWS,
                label="Interval Option",
            )
            dynamic_benchmark_type = wb_serializers.ChoiceField(
                choices=cls.DynamicBenchmarkType,
                default=None,
                allow_null=True,
                label="Benchmark Type",
                help_text="If specified, will compare the stop loss against the instrument related potential benchmark performance",
            )
            rolling_window_interval = wb_serializers.IntegerField(
                default=7,
                label="Rolling Window Interval",
                help_text="Valid only if interval option is Rolling Window. Specify the number of day for sampling",
            )
            static_benchmark = wb_serializers.PrimaryKeyRelatedField(
                queryset=Instrument.objects.all(),
                default=None,
                allow_null=True,
                label="Static Benchmark (If any)",
                help_text="If specified, will compare the stop loss against this benchmark",
            )
            asset_class = wb_serializers.PrimaryKeyRelatedField(
                queryset=InstrumentType.objects.all(),
                default=None,
                allow_null=True,
                label="Only Asset Class",
            )
            _asset_class = InstrumentTypeRepresentationSerializer(source="asset_class")

            _static_benchmark = SecurityRepresentationSerializer(
                source="static_benchmark", default=None, allow_null=True
            )
            field = wb_serializers.ChoiceField(
                choices=cls.FieldType.choices,
                default=cls.FieldType.NET_VALUE,
                label="Field",
            )
            penny_stock_max_abs_net_value = wb_serializers.FloatField(
                default=0.001, label="Penny Stock Max Absolute Net value"
            )

            @classmethod
            def get_parameter_fields(cls):
                return [
                    "freq",
                    "date_interval_option",
                    "dynamic_benchmark_type",
                    "rolling_window_interval",
                    "static_benchmark",
                    "asset_class",
                    "field",
                    "penny_stock_max_abs_net_value",
                ]

        return RuleBackendSerializer

    @property
    def benchmark(self):
        if self.dynamic_benchmark_type == self.DynamicBenchmarkType.PRIMARY_BENCHMARK.name:
            return self.product.primary_benchmark
        elif self.dynamic_benchmark_type == self.DynamicBenchmarkType.PORTFOLIO.name:
            return self.product
        elif self.static_benchmark:
            return self.static_benchmark

    def is_passive_evaluation_valid(self) -> bool:
        try:
            last_price = self.product.get_price(self.evaluation_date)
            base_condition = last_price != 0
            if (benchmark := self.benchmark) and (last_benchmark_price := benchmark.get_price(self.evaluation_date)):
                return (last_benchmark_price != 0) and base_condition
            return base_condition
        except ValueError:
            return False

    def _generate_incidents(
        self,
        tested_instrument_id: int,
        perf_instrument: float,
        perf_benchmark: float,
    ) -> Generator[backend.IncidentResult, None, None]:
        total_perf = perf_instrument if perf_benchmark is None else perf_instrument - perf_benchmark
        field_label = self.FieldType(self.field).label
        for threshold in self.thresholds:
            if threshold.is_inrange(total_perf):
                instrument = Instrument.objects.get(id=tested_instrument_id)
                report_details = {}
                with suppress(AssetPosition.DoesNotExist):
                    previous_portfolio_date = (
                        self.product.portfolio.assets.filter(date__lt=self.evaluation_date).latest("date").date
                    )
                    weighting = self.product.portfolio.assets.filter(
                        underlying_quote=instrument, date=previous_portfolio_date
                    ).aggregate(s=Sum("weighting"))["s"] or Decimal("0.0")
                    report_details["Portfolio Impact"] = f"{float(weighting) * total_perf:+,.2%}"
                report_details["Field"] = field_label
                if self.benchmark:
                    report_details[f"Relative Percentage VS {str(self.benchmark)}"] = f"{total_perf:,.3%}"
                if total_perf < 0:
                    breached_value = f'<span style="color:red">{total_perf:+,.2%}</span>'
                else:
                    breached_value = f'<span style="color:green">{total_perf:+,.2%}</span>'
                yield backend.IncidentResult(
                    breached_object=instrument,
                    breached_object_repr=str(instrument),
                    breached_value=breached_value,
                    report_details=report_details,
                    severity=threshold.severity,
                )

    def _get_start_interval(self) -> date:
        if self.date_interval_option == self.DateIntervalOption.FREQUENCY.name:
            return pd.date_range(end=self.evaluation_date, periods=2, freq=self.FreqChoices(self.freq).value)[0].date()
        else:
            return (self.evaluation_date - timedelta(days=self.rolling_window_interval - 1) - BDay(1)).date()

    def _get_performance(self, valuation_dto: PriceDTO) -> float:
        if not valuation_dto:
            return 0.0
        start_date = self._get_start_interval()
        if (
            qs := InstrumentPrice.objects.filter(
                calculated=False,
                instrument_id=valuation_dto.instrument,
                date__lte=start_date,
                date__gte=start_date - BDay(2),  # we allow 2 business day interval in case of market holiday
            ).exclude(
                net_value__lte=self.penny_stock_max_abs_net_value, net_value__gte=-self.penny_stock_max_abs_net_value
            )
        ).exists():
            last_value = float(getattr(qs.latest("date"), self.field))
            return float(getattr(valuation_dto, self.field)) / last_value - 1
        return 0.0

    def _build_dto_args(self) -> tuple[PriceDTO, PriceDTO | None]:
        if benchmark := self.benchmark:
            return self.product._build_dto(self.evaluation_date), benchmark._build_dto(self.evaluation_date)
        return self.product._build_dto(self.evaluation_date), None
