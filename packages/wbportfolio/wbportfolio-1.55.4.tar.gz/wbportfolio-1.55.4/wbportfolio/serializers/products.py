from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from rest_framework.reverse import reverse
from wbcore import serializers as wb_serializers
from wbcore.contrib.currency.serializers import CurrencyRepresentationSerializer
from wbcore.contrib.directory.serializers import (
    CompanyRepresentationSerializer,
    EntryRepresentationSerializer,
)
from wbcore.contrib.geography.serializers import GeographyRepresentationSerializer
from wbfdm.models import Instrument
from wbfdm.serializers.instruments.instruments import InstrumentModelSerializer

from wbportfolio.models import Portfolio, Product
from wbportfolio.serializers.portfolios import PortfolioRepresentationSerializer

from .product_group import ProductGroupRepresentationSerializer


class ProductRepresentationSerializer(wb_serializers.RepresentationSerializer):
    _detail = wb_serializers.HyperlinkField(reverse_name="wbportfolio:product-detail")
    bank_name = wb_serializers.CharField(read_only=True)

    class Meta:
        model = Product
        fields = ("id", "computed_str", "isin", "name", "bank_name", "_detail")


class ProductCustomerRepresentationSerializer(ProductRepresentationSerializer):
    label_key = "{{name}} - {{isin}} ({{bank_name}})"

    class Meta:
        model = Product
        fields = ("id", "isin", "name", "bank_name")


class ProductUnlinkedRepresentationSerializer(ProductRepresentationSerializer):
    class Meta(ProductRepresentationSerializer.Meta):
        model = Product
        fields = ("id", "isin", "name")


class ProductListModelSerializer(
    InstrumentModelSerializer,
):
    _bank = CompanyRepresentationSerializer(source="bank")
    _parent = ProductGroupRepresentationSerializer(source="parent")
    _white_label_customers = EntryRepresentationSerializer(source="white_label_customers", many=True)
    current_total_issuer_fees = wb_serializers.DecimalField(
        default=Decimal(0), read_only=True, max_digits=6, decimal_places=4, label="Issue Fees"
    )
    current_bank_fees = wb_serializers.DecimalField(
        default=Decimal(0), read_only=True, max_digits=6, decimal_places=4, label="Bank Fees"
    )
    current_management_fees = wb_serializers.DecimalField(
        default=Decimal(0), read_only=True, max_digits=6, decimal_places=4, label="Management Fees"
    )
    current_performance_fees = wb_serializers.DecimalField(
        default=Decimal(0), read_only=True, max_digits=6, decimal_places=4, label="Performance Fees"
    )

    # AUM based info
    net_value = wb_serializers.FloatField(label="Net Value", required=False, read_only=True)
    assets_under_management = wb_serializers.FloatField(
        label="Assets under Management", required=False, default=0, read_only=True
    )
    assets_under_management_usd = wb_serializers.FloatField(
        label="Assets under Management in USD", required=False, default=0, read_only=True
    )
    sum_shares = wb_serializers.FloatField(default=0, read_only=True)
    is_white_label = wb_serializers.BooleanField(read_only=True)

    # NNM annotations
    nnm_weekly = wb_serializers.FloatField(label="NNM Weekly", required=False, default=0, read_only=True)
    nnm_monthly = wb_serializers.FloatField(label="NNM Monthly", required=False, default=0, read_only=True)
    nnm_year_to_date = wb_serializers.FloatField(label="NNM YTD", required=False, default=0, read_only=True)
    nnm_yearly = wb_serializers.FloatField(label="NNM YEARLY", required=False, default=0, read_only=True)
    # general info
    is_invested = wb_serializers.BooleanField(default=True, read_only=True)

    @wb_serializers.register_resource()
    def additional_resources(self, instance, request, user):
        additional_resources = dict()
        additional_resources["peers"] = (
            reverse("wbfdm:instrument-relatedinstrument-list", args=[instance.id], request=request)
            + "?related_type=PEER"
        )
        additional_resources["benchmarks"] = (
            reverse("wbfdm:instrument-relatedinstrument-list", args=[instance.id], request=request)
            + "?related_type=BENCHMARK"
        )
        return additional_resources

    class Meta(InstrumentModelSerializer.Meta):
        decorators = {
            "share_price": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{_currency.symbol}}"
            ),
            "net_value": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{_currency.symbol}}"
            ),
            "assets_under_management": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{_currency.symbol}}"
            ),
            "assets_under_management_usd": wb_serializers.decorator(decorator_type="text", position="left", value="$"),
            "nnm_weekly": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{_currency.symbol}}"
            ),
            "nnm_monthly": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{_currency.symbol}}"
            ),
            "nnm_year_to_date": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{_currency.symbol}}"
            ),
            "nnm_yearly": wb_serializers.decorator(
                decorator_type="text", position="left", value="{{_currency.symbol}}"
            ),
        }
        percent_fields = [
            "current_bank_fees",
            "current_management_fees",
            "current_performance_fees",
            "current_total_issuer_fees",
        ]
        model = Product
        read_only_fields = [
            "share_price",
            "initial_high_water_mark",
            "issue_price",
            "last_valuation_date",
            "last_price_date",
            *InstrumentModelSerializer.Meta.read_only_fields,
        ]
        fields = (
            "id",
            "name",
            "name_repr",
            "bank",
            "_bank",
            "parent",
            "_parent",
            "description",
            "share_price",
            "initial_high_water_mark",
            "current_total_issuer_fees",
            "current_management_fees",
            "current_performance_fees",
            "current_bank_fees",
            "currency",
            "_currency",
            "isin",
            "ticker",
            "net_value",
            "sum_shares",
            "assets_under_management",
            "assets_under_management_usd",
            "nnm_weekly",
            "nnm_monthly",
            "nnm_year_to_date",
            "nnm_yearly",
            "is_white_label",
            "last_valuation_date",
            "last_price_date",
            "is_invested",
            "white_label_customers",
            "_white_label_customers",
            "_additional_resources",
            "_classifications",
            "classifications",
        )


class ProductModelSerializer(ProductListModelSerializer):
    id_repr = wb_serializers.CharField(source="id", read_only=True, label="ID")

    _jurisdiction = GeographyRepresentationSerializer(source="jurisdiction", filter_params={"level": 1})

    is_next_factsheet_available = wb_serializers.BooleanField(default=False, read_only=True)

    _portfolios = PortfolioRepresentationSerializer(source="portfolios", many=True)

    @wb_serializers.register_resource()
    def additional_resources(self, instance, request, user):
        additional_resources = dict()

        if user.profile.is_internal or user.is_superuser:
            additional_resources["aum"] = (
                f'{reverse("wbportfolio:aumtable-list", args=[], request=request)}?product={instance.id}&group_by=ACCOUNT'
            )
            additional_resources["claims"] = reverse(
                "wbportfolio:product-claim-list",
                args=[instance.id],
                request=request,
            )

            if portfolio := instance.portfolio:
                additional_resources["preferredclassification"] = reverse(
                    "wbportfolio:portfolio-preferredclassification-list",
                    args=[portfolio.id],
                    request=request,
                )
                product_ct = ContentType.objects.get_for_model(Product)
                instrument_ct = ContentType.objects.get_for_model(Instrument)
                portfolio_cd = ContentType.objects.get_for_model(Portfolio)
                additional_resources["risk_rules"] = (
                    reverse("wbcompliance:riskrule-list", args=[], request=request)
                    + f"?checked_object_relationships=[({product_ct.id},{instance.id}),({instrument_ct.id},{instance.id}),({portfolio_cd.id},{portfolio.id})]"
                )
                additional_resources["risk_incidents"] = (
                    reverse("wbcompliance:riskincident-list", args=[], request=request)
                    + f"?checked_object_relationships=[({product_ct.id},{instance.id}),({instrument_ct.id},{instance.id}),({portfolio_cd.id},{portfolio.id})]"
                )
        return additional_resources

    class Meta(ProductListModelSerializer.Meta):
        fields = (
            "id_repr",
            "bank",
            "_bank",
            "share_price",
            "initial_high_water_mark",
            "current_bank_fees",
            "current_management_fees",
            "current_performance_fees",
            "current_total_issuer_fees",
            "white_label_customers",
            "_white_label_customers",
            "type_of_return",
            "asset_class",
            "legal_structure",
            "investment_index",
            "liquidity",
            "risk_scale",
            "jurisdiction",
            "_jurisdiction",
            "is_next_factsheet_available",
            "external_webpage",
            "issue_price",
            "is_invested",
            "net_value",
            "last_valuation_date",
            "assets_under_management",
            "assets_under_management_usd",
            "nnm_weekly",
            "nnm_monthly",
            "nnm_year_to_date",
            "nnm_yearly",
            "is_white_label",
            "parent",
            "_parent",
            "_portfolios",
            "portfolios",
        ) + InstrumentModelSerializer.Meta.fields


class ProductCustomerModelSerializer(ProductListModelSerializer):
    bank_repr = wb_serializers.CharField(read_only=True)
    currency_symbol = wb_serializers.CharField(read_only=True)

    class Meta:
        model = Product
        decorators = {
            "net_value": wb_serializers.decorator(decorator_type="text", position="left", value="{{currency_symbol}}"),
        }
        fields = (
            "id",
            "name",
            "isin",
            "bank_repr",
            "currency_symbol",
            "ticker",
            "net_value",
        )


class ProductFeesModelSerializer(wb_serializers.ModelSerializer):
    _currency = CurrencyRepresentationSerializer(source="currency")

    sum_management_fees = wb_serializers.FloatField(
        label="Bank Fees",
        required=False,
        read_only=True,
        decorators=[{"position": "left", "value": "{{_currency.symbol}}"}],
    )
    sum_management_fees_usd = wb_serializers.FloatField(
        label="USD",
        required=False,
        read_only=True,
        decorators=[{"position": "left", "value": "$"}],
    )
    sum_performance_fees_net = wb_serializers.FloatField(
        label="Bank Fees",
        required=False,
        read_only=True,
        decorators=[{"position": "left", "value": "{{_currency.symbol}}"}],
    )
    sum_performance_fees_net_usd = wb_serializers.FloatField(
        label="USD",
        required=False,
        read_only=True,
        decorators=[{"position": "left", "value": "$"}],
    )
    sum_total = wb_serializers.FloatField(
        label="USD",
        required=False,
        read_only=True,
        decorators=[{"position": "left", "value": "{{_currency.symbol}}"}],
    )
    sum_total_usd = wb_serializers.FloatField(
        label="USD",
        required=False,
        read_only=True,
        decorators=[{"position": "left", "value": "$"}],
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "computed_str",
            "isin",
            "ticker",
            "currency",
            "_currency",
            "sum_management_fees",
            "sum_management_fees_usd",
            "sum_performance_fees_net",
            "sum_performance_fees_net_usd",
            "sum_total",
            "sum_total_usd",
        )
