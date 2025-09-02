from typing import Generator

from django.db import models
from wbcompliance.models.risk_management import backend
from wbcompliance.models.risk_management.dispatch import register
from wbcompliance.models.risk_management.rules import RiskIncidentType
from wbcore import serializers as wb_serializers
from wbcore.contrib.currency.models import Currency
from wbcore.contrib.currency.serializers import CurrencyRepresentationSerializer
from wbcore.contrib.geography.models import Geography
from wbcore.contrib.geography.serializers import CountryRepresentationSerializer
from wbfdm.models import Classification, Instrument, InstrumentType
from wbfdm.serializers import (
    ClassificationRepresentationSerializer,
    InstrumentTypeRepresentationSerializer,
)

from wbportfolio.pms.typing import Portfolio as PortfolioDTO

from .mixins import ActivePortfolioRelationshipMixin


@register("Exposure Portfolio Rule Backend", rule_group_key="portfolio")
class RuleBackend(
    ActivePortfolioRelationshipMixin,
):
    class GroupbyChoices(models.TextChoices):
        UNDERLYING_INSTRUMENT = "underlying_instrument", "Underlying Instrument"
        ASSET_TYPE = "instrument_type", "Asset Type"
        CASH = "is_cash", "Cash"
        CURRENCY = "currency", "Currency"
        COUNTRY = "country", "Country"
        PRIMARY_CLASSIFICATION = "primary_classification", "Primary Classification"
        FAVORITE_CLASSIFICATION = "favorite_classification", "Favorite Classification"

    class Field(models.TextChoices):
        WEIGHTING = "weighting", "Weighting"
        MARKET_CAPITALIZATION_USD = "market_capitalization_usd", "Market Capitalization (USD)"
        MARKET_SHARE = "market_share", "Market Shares"
        DAILY_LIQUIDITY = "daily_liquidity", "Daily Liquidity"
        VOLUME_USD = "volume_usd", "Dollar Volume"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_by = self.GroupbyChoices(self.group_by)
        self.field = self.Field(self.field)

    @classmethod
    def get_serializer_class(cls) -> wb_serializers.Serializer:
        class RuleBackendSerializer(wb_serializers.Serializer):
            group_by = wb_serializers.ChoiceField(
                choices=cls.GroupbyChoices.choices,
                default=cls.GroupbyChoices.ASSET_TYPE,
                allow_null=True,
                help_text="Choose how the position will be aggregated before evaluating the rule",
                label="Group By",
            )
            field = wb_serializers.ChoiceField(
                choices=cls.Field.choices,
                default=cls.Field.WEIGHTING,
                allow_null=True,
                label="Field",
                help_text="Choose which field will be evaluated after aggregatation",
            )
            is_cash = wb_serializers.BooleanField(
                default=None, allow_null=True, label="Cash", help_text="Exclude cash position"
            )
            asset_classes = wb_serializers.PrimaryKeyRelatedField(
                queryset=InstrumentType.objects.all(),
                many=True,
                default=None,
                allow_null=True,
                label="Only Asset Classes",
            )
            _asset_classes = InstrumentTypeRepresentationSerializer(source="asset_classes", many=True)

            currencies = wb_serializers.PrimaryKeyRelatedField(
                queryset=Currency.objects.all(),
                many=True,
                default=None,
                allow_null=True,
                label="Only Currencies",
            )
            _currencies = CurrencyRepresentationSerializer(many=True, source="parameters__currencies")
            countries = wb_serializers.PrimaryKeyRelatedField(
                queryset=Geography.countries.all(),
                many=True,
                default=None,
                allow_null=True,
                label="Only Countries",
            )
            _countries = CountryRepresentationSerializer(
                many=True, source="parameters__countries", filter_params={"level": 1}
            )
            classifications = wb_serializers.PrimaryKeyRelatedField(
                queryset=Classification.objects.all(),
                many=True,
                default=None,
                allow_null=True,
                label="Classifications",
            )
            _classifications = ClassificationRepresentationSerializer(many=True, source="parameters__classifications")

            extra_filter_field = wb_serializers.ChoiceField(
                choices=cls.Field.choices,
                default=None,
                allow_null=True,
                label="Extra Filter Field",
                help_text="Specify if we need to narrow done the position applying a filter on that field and the corresponding range",
            )
            extra_filter_field_lower_bound = wb_serializers.FloatField(
                default=None,
                allow_null=True,
                label="Extra Filter Field Lower bound",
            )
            extra_filter_field_upper_bound = wb_serializers.FloatField(
                default=None,
                allow_null=True,
                label="Extra Filter Field Lower bound",
            )

            @classmethod
            def get_parameter_fields(cls):
                return [
                    "group_by",
                    "field",
                    "is_cash",
                    "asset_classes",
                    "currencies",
                    "countries",
                    "classifications",
                    "extra_filter_field",
                    "extra_filter_field_lower_bound",
                    "extra_filter_field_upper_bound",
                ]

        return RuleBackendSerializer

    @property
    def report_details(self) -> dict[str, str]:
        repr = {
            "Field": self.field.label,
            "Group By": self.group_by.label,
        }
        if self.is_cash:
            repr["Only Cash"] = "True"
        if self.asset_classes:
            repr["Only Types"] = ", ".join(map(lambda o: o.name, self.asset_classes))
        if self.currencies:
            repr["Only Currencies"] = ", ".join(map(lambda o: o.key, self.currencies))
        if self.countries:
            repr["Only Countries"] = ", ".join(map(lambda o: o.code_2, self.countries))
        if self.classifications:
            repr["Only Classifications"] = ", ".join(map(lambda o: o.name, self.classifications))
        if self.extra_filter_field:
            repr["Extra Filter Field"] = (
                f"{self.extra_filter_field}=[{self.extra_filter_field_lower_bound},{self.extra_filter_field_upper_bound}["
            )
        return repr

    def _process_dto(self, portfolio: PortfolioDTO, **kwargs) -> Generator[backend.IncidentResult, None, None]:
        if not (df := self._filter_df(portfolio.to_df())).empty:
            df = df[[self.group_by.value, self.field.value]].groupby(self.group_by.value).sum().astype(float)
            for threshold in self.thresholds:
                numerical_range = threshold.numerical_range
                incident_df = df[
                    (df[self.field.value] >= numerical_range[0]) & (df[self.field.value] < numerical_range[1])
                ]
                if not incident_df.empty:
                    for id, row in incident_df.to_dict("index").items():
                        obj, obj_repr = self._get_obj_repr(id)
                        severity: RiskIncidentType = threshold.severity
                        if self.field == self.Field.WEIGHTING:
                            breached_value = f"{row[self.field.value]:+,.2%}"
                        else:
                            breached_value = f"{row[self.field.value]:,.3f}"
                        if row[self.field.value] < 0:
                            breached_value = f'<span style="color:red">{breached_value}</span>'
                        else:
                            breached_value = f'<span style="color:green">{breached_value}</span>'
                        yield backend.IncidentResult(
                            breached_object=obj,
                            breached_object_repr=obj_repr,
                            breached_value=breached_value,
                            report_details=self.report_details,
                            severity=severity,
                        )

    def _filter_df(self, df):
        if df.empty:
            return df
        if self.is_cash is True or self.is_cash is False:
            df = df[df["is_cash"] == self.is_cash]
        if self.asset_classes:
            df = df[df["instrument_type"].isin(list(map(lambda o: o.id, self.asset_classes)))]

        if self.countries:
            df = df[(~df["country"].isnull() & df["country"].isin(list(map(lambda o: o.id, self.countries))))]
        if self.currencies:
            df = df[(~df["currency"].isnull() & df["currency"].isin(list(map(lambda o: o.id, self.currencies))))]
        if self.classifications:
            df = df[
                (
                    ~df["primary_classification"].isnull()
                    & df["primary_classification"].isin(list(map(lambda o: o.id, self.classifications)))
                )
            ]
        if self.extra_filter_field:
            if (lower_bound := self.extra_filter_field_lower_bound) is not None:
                df = df[df[self.extra_filter_field] >= lower_bound]
            if (upper_bound := self.extra_filter_field_upper_bound) is not None:
                df = df[df[self.extra_filter_field] < upper_bound]
        return df

    def _get_obj_repr(self, pivot_object_id) -> tuple[models.Model | None, str]:
        match self.group_by:
            case self.GroupbyChoices.UNDERLYING_INSTRUMENT:
                obj = Instrument.objects.get(id=pivot_object_id)
                return obj, str(obj)
            case self.GroupbyChoices.ASSET_TYPE:
                return None, InstrumentType.objects.get(id=pivot_object_id)
            case self.GroupbyChoices.CASH:
                return None, "Cash"
            case self.GroupbyChoices.COUNTRY:
                obj = Geography.countries.get(id=pivot_object_id)
                return obj, str(obj)
            case self.GroupbyChoices.CURRENCY:
                obj = Currency.objects.get(id=pivot_object_id)
                return obj, str(obj)
            case self.GroupbyChoices.PRIMARY_CLASSIFICATION:
                obj = Classification.objects.get(id=pivot_object_id)
                return obj, str(obj)
            case self.GroupbyChoices.FAVORITE_CLASSIFICATION:
                obj = Classification.objects.get(id=pivot_object_id)
                return obj, str(obj)
