from decimal import Decimal

from rest_framework import serializers
from wbcore import serializers as wb_serializers
from wbcore.metadata.configs.display.list_display import BaseTreeGroupLevelOption
from wbfdm.models import Instrument
from wbfdm.serializers import InvestableInstrumentRepresentationSerializer
from wbfdm.serializers.instruments.instruments import (
    CompanyRepresentationSerializer,
    SecurityRepresentationSerializer,
)

from wbportfolio.models import Order


class GetSecurityDefault:
    requires_context = True

    def __call__(self, serializer_instance):
        try:
            instance = serializer_instance.view.get_object()
            return instance.underlying_instrument.parent or instance.underlying_instrument
        except Exception:
            return None


class GetCompanyDefault:
    requires_context = True

    def __call__(self, serializer_instance):
        try:
            instance = serializer_instance.view.get_object()
            security = instance.underlying_instrument.parent or instance.underlying_instrument
            return security.parent or security
        except Exception:
            return None


class OrderOrderProposalListModelSerializer(wb_serializers.ModelSerializer):
    underlying_instrument = wb_serializers.SlugRelatedField(read_only=True, slug_field="name")
    underlying_instrument_isin = wb_serializers.CharField(read_only=True)
    underlying_instrument_ticker = wb_serializers.CharField(read_only=True)
    underlying_instrument_refinitiv_identifier_code = wb_serializers.CharField(read_only=True)
    underlying_instrument_instrument_type = wb_serializers.CharField(read_only=True)
    underlying_instrument_exchange = wb_serializers.CharField(read_only=True)

    target_weight = wb_serializers.DecimalField(
        max_digits=Order.ORDER_WEIGHTING_PRECISION + 1,
        decimal_places=Order.ORDER_WEIGHTING_PRECISION,
        required=False,
        default=0,
    )
    effective_weight = wb_serializers.DecimalField(
        read_only=True,
        max_digits=Order.ORDER_WEIGHTING_PRECISION + 1,
        decimal_places=Order.ORDER_WEIGHTING_PRECISION,
        default=0,
    )

    effective_shares = wb_serializers.DecimalField(read_only=True, max_digits=16, decimal_places=6, default=0)
    target_shares = wb_serializers.DecimalField(read_only=True, max_digits=16, decimal_places=6, default=0)

    total_value_fx_portfolio = wb_serializers.DecimalField(read_only=True, max_digits=16, decimal_places=2, default=0)
    effective_total_value_fx_portfolio = wb_serializers.DecimalField(
        read_only=True, max_digits=16, decimal_places=2, default=0
    )
    target_total_value_fx_portfolio = wb_serializers.DecimalField(
        read_only=True, max_digits=16, decimal_places=2, default=0
    )

    portfolio_currency = wb_serializers.CharField(read_only=True)
    has_warnings = wb_serializers.BooleanField(read_only=True)

    def validate(self, data):
        data.pop("company", None)
        data.pop("security", None)
        if self.instance and "underlying_instrument" in data:
            raise serializers.ValidationError(
                {
                    "underlying_instrument": "You cannot modify the underlying instrument other than creating a new entry"
                }
            )
        effective_weight = self.instance._effective_weight if self.instance else Decimal(0.0)
        weighting = data.get("weighting", self.instance.weighting if self.instance else Decimal(0.0))
        if (target_weight := data.pop("target_weight", None)) is not None:
            weighting = target_weight - effective_weight
            data["desired_target_weight"] = target_weight
        if weighting >= 0:
            data["order_type"] = "BUY"
        else:
            data["order_type"] = "SELL"
        data["weighting"] = weighting
        return super().validate(data)

    class Meta:
        model = Order
        percent_fields = ["effective_weight", "target_weight", "weighting"]
        decorators = {
            "total_value_fx_portfolio": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{portfolio_currency}}"
            ),
            "effective_total_value_fx_portfolio": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{portfolio_currency}}"
            ),
            "target_total_value_fx_portfolio": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{portfolio_currency}}"
            ),
        }
        read_only_fields = (
            "order_type",
            "shares",
            "effective_shares",
            "target_shares",
            "total_value_fx_portfolio",
            "effective_total_value_fx_portfolio",
            "target_total_value_fx_portfolio",
            "has_warnings",
        )
        fields = (
            "id",
            "shares",
            "underlying_instrument",
            "underlying_instrument_isin",
            "underlying_instrument_ticker",
            "underlying_instrument_refinitiv_identifier_code",
            "underlying_instrument_instrument_type",
            "underlying_instrument_exchange",
            "order_type",
            "comment",
            "effective_weight",
            "target_weight",
            "weighting",
            "order_proposal",
            "order",
            "effective_shares",
            "target_shares",
            "total_value_fx_portfolio",
            "effective_total_value_fx_portfolio",
            "target_total_value_fx_portfolio",
            "portfolio_currency",
            "has_warnings",
            "execution_confirmed",
            "execution_comment",
        )


class OrderOrderProposalModelSerializer(OrderOrderProposalListModelSerializer):
    company = wb_serializers.PrimaryKeyRelatedField(
        queryset=Instrument.objects.filter(level=0),
        required=False,
        read_only=lambda view: not view.new_mode,
        default=GetCompanyDefault(),
    )
    _company = CompanyRepresentationSerializer(source="company", required=False)

    security = wb_serializers.PrimaryKeyRelatedField(
        queryset=Instrument.objects.filter(is_security=True),
        required=False,
        read_only=lambda view: not view.new_mode,
        default=GetSecurityDefault(),
    )
    _security = SecurityRepresentationSerializer(
        source="security",
        optional_get_parameters={"company": "parent"},
        depends_on=[{"field": "company", "options": {}}],
        required=False,
    )
    underlying_instrument = wb_serializers.PrimaryKeyRelatedField(
        queryset=Instrument.objects.all(), label="Quote", read_only=lambda view: not view.new_mode
    )
    _underlying_instrument = InvestableInstrumentRepresentationSerializer(
        source="underlying_instrument",
        optional_get_parameters={"security": "parent"},
        depends_on=[{"field": "security", "options": {}}],
        tree_config=BaseTreeGroupLevelOption(clear_filter=True, filter_key="parent"),
    )

    class Meta(OrderOrderProposalListModelSerializer.Meta):
        fields = list(OrderOrderProposalListModelSerializer.Meta.fields) + [
            "company",
            "_company",
            "security",
            "_security",
            "_underlying_instrument",
        ]


class ReadOnlyOrderOrderProposalModelSerializer(OrderOrderProposalListModelSerializer):
    class Meta(OrderOrderProposalListModelSerializer.Meta):
        read_only_fields = OrderOrderProposalListModelSerializer.Meta.fields
