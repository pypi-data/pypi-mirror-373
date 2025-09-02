from typing import Generator

import pandas as pd
from django.contrib.contenttypes.models import ContentType
from django.db import models
from wbcompliance.models.risk_management import backend
from wbcompliance.models.risk_management.dispatch import register
from wbcore import serializers as wb_serializers
from wbfdm.models import InstrumentPrice

from wbportfolio.models import AssetPosition, Product


@register("Product Data Integrity", rule_group_key="portfolio")
class RuleBackend(backend.AbstractRuleBackend):
    OBJECT_FIELD_NAME: str = "product"

    class DataTypeChoices(models.TextChoices):
        INSTRUMENT_PRICE = "INSTRUMENT_PRICE", "Valuation"
        ASSET_POSITION = "ASSET_POSITION", "Asset Position"

    product: Product

    def is_passive_evaluation_valid(self) -> bool:
        return (
            self.product.is_active_at_date(self.evaluation_date)
            and AssetPosition.objects.filter(is_estimated=False, portfolio=self.product.portfolio).exists()
            and InstrumentPrice.objects.filter(calculated=False, instrument=self.product).exists()
        )

    @classmethod
    def get_allowed_content_type(cls) -> "ContentType":
        return ContentType.objects.get_for_model(Product)

    def _build_dto_args(self):
        return (self.product,)

    @classmethod
    def get_all_active_relationships(cls) -> models.QuerySet:
        return Product.active_objects.all()

    @classmethod
    def get_serializer_class(cls) -> wb_serializers.Serializer:
        class RuleBackendSerializer(wb_serializers.Serializer):
            data_type = wb_serializers.MultipleChoiceField(
                choices=cls.DataTypeChoices.choices,
                default=[cls.DataTypeChoices.ASSET_POSITION.value, cls.DataTypeChoices.INSTRUMENT_PRICE.value],
                label="Flags",
                help_text="Set the flags that will trigger the rule",
            )

            @classmethod
            def get_parameter_fields(cls):
                return ["data_type"]

        return RuleBackendSerializer

    def _process_dto(self, product: Product, **kwargs) -> Generator[backend.IncidentResult, None, None]:
        for lag_threshold in reversed(self.thresholds):
            numerical_range = lag_threshold.numerical_range

            last_asset_position_date = (
                AssetPosition.objects.filter(is_estimated=False, portfolio=product.portfolio).latest("date").date
            )
            last_instrument_price_date = (
                InstrumentPrice.objects.filter(calculated=False, instrument=product).latest("date").date
            )

            asset_position_lag = (
                len(
                    pd.date_range(
                        min([self.evaluation_date, last_asset_position_date]), self.evaluation_date, freq="B"
                    )
                )
                - 1
            )
            instrument_price_lag = (
                len(
                    pd.date_range(
                        min([self.evaluation_date, last_instrument_price_date]), self.evaluation_date, freq="B"
                    )
                )
                - 1
            )
            breached_data_type = []
            if (
                self.DataTypeChoices.ASSET_POSITION.value in self.data_type
                and asset_position_lag >= numerical_range[0]
                and asset_position_lag < numerical_range[1]
            ):
                breached_data_type.append("Asset Position")
            if (
                self.DataTypeChoices.INSTRUMENT_PRICE.value in self.data_type
                and instrument_price_lag >= numerical_range[0]
                and instrument_price_lag < numerical_range[1]
            ):
                breached_data_type.append("Valuation")

            if len(breached_data_type) > 0:
                max_lag = max([asset_position_lag, instrument_price_lag])
                yield backend.IncidentResult(
                    breached_object=product,
                    breached_object_repr=str(product),
                    breached_value=str(max_lag),
                    report_details={
                        "Lag": max_lag,
                        "Last Valuation Datapoint": f"{last_instrument_price_date:%d.%m.%Y}",
                        "Last Asset Position Datapoint": f"{last_asset_position_date:%d.%m.%Y}",
                        "Valuation Lag": instrument_price_lag,
                        "Asset Position Lag": asset_position_lag,
                    },
                    severity=lag_threshold.severity,
                )
                break
