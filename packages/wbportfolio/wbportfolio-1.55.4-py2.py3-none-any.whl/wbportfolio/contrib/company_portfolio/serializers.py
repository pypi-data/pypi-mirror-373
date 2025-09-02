from django.conf import settings
from rest_framework.reverse import reverse
from wbcore import serializers
from wbcore.contrib.currency.models import Currency
from wbcore.contrib.currency.serializers import CurrencyRepresentationSerializer
from wbcore.contrib.directory.models import Company, Entry, Person
from wbcore.contrib.directory.serializers.companies import (
    CompanyModelListSerializer as BaseCompanyModelListSerializer,
)
from wbcore.contrib.directory.serializers.companies import (
    CompanyModelSerializer as BaseCompanyModelSerializer,
)
from wbcore.contrib.directory.serializers.entries import (
    CompanyRepresentationSerializer as BaseCompanyRepresentationSerializer,
)
from wbcore.contrib.directory.serializers.persons import (
    PersonModelListSerializer as BasePersonModelListSerializer,
)
from wbcore.contrib.directory.serializers.persons import (
    PersonModelSerializer as BasePersonModelSerializer,
)
from wbcore.contrib.geography.serializers import GeographyRepresentationSerializer
from wbcore.serializers.fields.types import DisplayMode

from .constants import DEFAULT_PORTFOLIO_DATA_UPDATE_TASK_INTERVAL_MINUTES
from .models import (
    AssetAllocation,
    AssetAllocationType,
    CompanyPortfolioData,
    GeographicFocus,
)

HELP_TEXT = f" (Updated every {DEFAULT_PORTFOLIO_DATA_UPDATE_TASK_INTERVAL_MINUTES} minutes)"


def _get_assets_under_management_kwargs(field_name):
    field = getattr(CompanyPortfolioData, field_name).field
    return {
        "max_digits": field.max_digits,
        "decimal_places": field.decimal_places,
        "label": field.verbose_name,
        "help_text": field.help_text + HELP_TEXT,
        "display_mode": DisplayMode.SHORTENED,
        "required": False,
    }


def _get_investment_discretion_kwargs():
    field = CompanyPortfolioData.investment_discretion.field
    return {
        "choices": field.choices,
        "default": field.default,
        "help_text": field.help_text + HELP_TEXT,
        "label": field.verbose_name,
    }


def _get_potential_kwargs():
    return {
        "decimal_places": CompanyPortfolioData.potential.field.decimal_places,
        "max_digits": CompanyPortfolioData.potential.field.max_digits,
        "help_text": CompanyPortfolioData.potential.field.help_text + HELP_TEXT,
        "display_mode": DisplayMode.SHORTENED,
        "read_only": True,
    }


def get_portfolio_data(validated_data, method="get"):
    method = getattr(validated_data, method)

    assets_under_management = method("asset_under_management", None)
    assets_under_management_currency_id = method("assets_under_management_currency", None)
    investment_discretion = method("investment_discretion", None)

    if isinstance(assets_under_management_currency_id, Currency):
        assets_under_management_currency_id = assets_under_management_currency_id.id

    return validated_data, {
        "assets_under_management": assets_under_management,
        "assets_under_management_currency_id": assets_under_management_currency_id,
        "investment_discretion": investment_discretion,
    }


def update_portfolio_data(company_portfolio_data, portfolio_data):
    if assets_under_management := portfolio_data["assets_under_management"]:
        company_portfolio_data.assets_under_management = assets_under_management

    if assets_under_management_currency_id := portfolio_data["assets_under_management_currency_id"]:
        company_portfolio_data.assets_under_management_currency_id = assets_under_management_currency_id

    if investment_discretion := portfolio_data["investment_discretion"]:
        company_portfolio_data.investment_discretion = investment_discretion

    company_portfolio_data.save()


class CompanyPortfolioDataMixin(serializers.ModelSerializer):
    asset_under_management = serializers.DecimalField(
        **_get_assets_under_management_kwargs(field_name="assets_under_management"),
    )
    invested_assets_under_management_usd = serializers.DecimalField(
        read_only=True,
        **_get_assets_under_management_kwargs(field_name="invested_assets_under_management_usd"),
    )
    investment_discretion = serializers.ChoiceField(**_get_investment_discretion_kwargs())
    assets_under_management_currency = serializers.PrimaryKeyRelatedField(
        required=False,
        queryset=Currency.objects.all(),
        default=None,
        label=CompanyPortfolioData.assets_under_management_currency.field.verbose_name,
    )
    assets_under_management_currency_repr = serializers.CharField(read_only=True, required=False)
    _assets_under_management_currency = CurrencyRepresentationSerializer(source="assets_under_management_currency")
    potential = serializers.DecimalField(**_get_potential_kwargs())
    potential_currency = serializers.PrimaryKeyRelatedField(
        required=False,
        queryset=Currency.objects.all(),
        label=CompanyPortfolioData.potential_currency.field.verbose_name,
    )
    _potential_currency = CurrencyRepresentationSerializer(source="potential_currency")

    # Not sure why read_only_fields does not work...
    tier = serializers.ChoiceField(
        read_only=True, choices=Company.Tiering.choices, help_text=settings.DEFAULT_TIERING_HELP_TEXT
    )

    class Meta:
        model = Entry
        read_only_fields = ("tier",)
        decorators = {
            "asset_under_management": serializers.decorator(
                position="left", value="{{assets_under_management_currency_repr}}"
            ),
            "potential": serializers.decorator(
                decorator_type="text", position="left", value="{{assets_under_management_currency_repr}}"
            ),
            "invested_assets_under_management_usd": serializers.decorator(
                decorator_type="text", position="left", value="$"
            ),
        }

        fields = (
            "asset_under_management",  # TODO: add an s after asset - After removing this field from the base model
            "assets_under_management_currency_repr",
            "invested_assets_under_management_usd",
            "potential_currency",
            "_potential_currency",
            "assets_under_management_currency",
            "_assets_under_management_currency",
            "investment_discretion",
            "potential",
            "tier",
        )


class CompanyModelSerializer(CompanyPortfolioDataMixin, BaseCompanyModelSerializer):
    SERIALIZER_CLASS_FOR_REMOTE_ADDITIONAL_RESOURCES = BasePersonModelSerializer

    def update(self, instance, validated_data):
        validated_data, portfolio_data = get_portfolio_data(validated_data)
        updated_instance = super().update(instance, validated_data)
        update_portfolio_data(updated_instance.portfolio_data, portfolio_data)

        return updated_instance

    def create(self, validated_data):
        validated_data, portfolio_data = get_portfolio_data(validated_data, method="pop")
        created_instance = super().create(validated_data)
        update_portfolio_data(created_instance.portfolio_data, portfolio_data)

        return created_instance

    @serializers.register_resource()
    def extra_additional_resources(self, instance, request, user):
        return {
            "asset_allocation_table": reverse(
                "company_portfolio:companyassetallocation-list", kwargs={"company_id": instance.id}, request=request
            ),
            "geographic_focus_table": reverse(
                "company_portfolio:companygeographicfocus-list", kwargs={"company_id": instance.id}, request=request
            ),
        }

    class Meta(CompanyPortfolioDataMixin.Meta, BaseCompanyModelSerializer.Meta):
        model = Company
        read_only_fields = (
            *BaseCompanyModelSerializer.Meta.read_only_fields,
            *CompanyPortfolioDataMixin.Meta.read_only_fields,
        )
        fields = (
            *BaseCompanyModelSerializer.Meta.fields,
            *CompanyPortfolioDataMixin.Meta.fields,
            "assets_under_management_currency",
            "_assets_under_management_currency",
            "potential_currency",
            "_potential_currency",
        )


class CompanyModelListSerializer(CompanyPortfolioDataMixin, BaseCompanyModelListSerializer):
    SERIALIZER_CLASS_FOR_REMOTE_ADDITIONAL_RESOURCES = BaseCompanyModelListSerializer

    class Meta(CompanyPortfolioDataMixin.Meta, BaseCompanyModelListSerializer.Meta):
        model = Company
        fields = (*BaseCompanyModelListSerializer.Meta.fields, *CompanyPortfolioDataMixin.Meta.fields)


class PersonModelSerializer(CompanyPortfolioDataMixin, BasePersonModelSerializer):
    SERIALIZER_CLASS_FOR_REMOTE_ADDITIONAL_RESOURCES = BasePersonModelSerializer

    asset_under_management = serializers.DecimalField(
        **_get_assets_under_management_kwargs(field_name="assets_under_management"),
        read_only=True,
    )
    investment_discretion = serializers.ChoiceField(**_get_investment_discretion_kwargs(), read_only=True)

    class Meta(CompanyPortfolioDataMixin.Meta, BasePersonModelSerializer.Meta):
        model = Person
        read_only_fields = (
            *BasePersonModelSerializer.Meta.read_only_fields,
            *CompanyPortfolioDataMixin.Meta.fields,
            *CompanyPortfolioDataMixin.Meta.read_only_fields,
        )
        fields = (
            *BasePersonModelSerializer.Meta.fields,
            *CompanyPortfolioDataMixin.Meta.fields,
            "assets_under_management_currency",
            "_assets_under_management_currency",
            "potential_currency",
            "_potential_currency",
        )


class PersonModelListSerializer(CompanyPortfolioDataMixin, BasePersonModelListSerializer):
    investment_discretion = serializers.ChoiceField(**_get_investment_discretion_kwargs(), read_only=True)
    SERIALIZER_CLASS_FOR_REMOTE_ADDITIONAL_RESOURCES = BasePersonModelListSerializer

    class Meta(CompanyPortfolioDataMixin.Meta, BasePersonModelListSerializer.Meta):
        model = Person
        fields = (*BasePersonModelListSerializer.Meta.fields, *CompanyPortfolioDataMixin.Meta.fields)
        read_only_fields = fields


class AssetAllocationTypeRepresentationSerializer(serializers.RepresentationSerializer):
    _detail = serializers.HyperlinkField(reverse_name="company_portfolio:assetallocationtyperepresentation-detail")

    class Meta:
        model = AssetAllocationType
        fields = ("id", "name", "_detail")


class AssetAllocationTypeModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetAllocationType
        fields = ("id", "name", "_additional_resources")


class AssetAllocationModelSerializer(serializers.ModelSerializer):
    _asset_type = AssetAllocationTypeRepresentationSerializer(source="asset_type")
    _company = BaseCompanyRepresentationSerializer(source="company")
    company = serializers.PrimaryKeyRelatedField(
        default=serializers.DefaultFromGET("company"), queryset=Company.objects.all(), label="Company"
    )
    comment = serializers.TextAreaField(default="")

    class Meta:
        percent_fields = ("percent", "max_investment")
        model = AssetAllocation
        fields = (
            "id",
            "company",
            "_company",
            "asset_type",
            "_asset_type",
            "percent",
            "max_investment",
            "comment",
            "_additional_resources",
        )


class GeographicFocusModelSerializer(serializers.ModelSerializer):
    _country = GeographyRepresentationSerializer(source="country")
    company = serializers.PrimaryKeyRelatedField(
        default=serializers.DefaultFromGET("company"), queryset=Company.objects.all(), label="Company"
    )
    _company = BaseCompanyRepresentationSerializer(source="company")
    comment = serializers.TextAreaField(default="")

    class Meta:
        percent_fields = ("percent",)
        model = GeographicFocus
        fields = (
            "id",
            "company",
            "_company",
            "country",
            "_country",
            "percent",
            "comment",
            "_additional_resources",
        )
