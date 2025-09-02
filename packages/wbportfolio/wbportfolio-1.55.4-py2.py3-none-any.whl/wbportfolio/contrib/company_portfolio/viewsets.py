from datetime import date

from django.db.models import F, OuterRef, Subquery, Sum
from django.utils.functional import cached_property
from wbcore import viewsets
from wbcore.contrib.currency.models import CurrencyFXRates
from wbcore.contrib.directory.models import EmployerEmployeeRelationship
from wbcore.contrib.directory.serializers import NewPersonModelSerializer
from wbcore.contrib.directory.serializers import (
    PersonModelSerializer as BasePersonModelSerializer,
)
from wbcore.contrib.directory.viewsets.entries import (
    CompanyModelViewSet as OriginalCompanyModelViewSet,
)
from wbcore.contrib.directory.viewsets.entries import (
    PersonModelViewSet as OriginalPersonModelViewSet,
)
from wbcore.utils.strings import format_number

from .configs import (
    AssetAllocationDisplay,
    AssetAllocationModelEndpointConfig,
    CompanyModelDisplay,
    CompanyPreviewConfig,
    GeographicFocusDisplay,
    GeographicFocusModelEndpointConfig,
    PersonModelDisplay,
)
from .filters import CompanyFilter, PersonFilter
from .models import AssetAllocation, AssetAllocationType, GeographicFocus
from .serializers import (
    AssetAllocationModelSerializer,
    AssetAllocationTypeModelSerializer,
    AssetAllocationTypeRepresentationSerializer,
    CompanyModelListSerializer,
    CompanyModelSerializer,
    GeographicFocusModelSerializer,
    PersonModelListSerializer,
    PersonModelSerializer,
)


class CompanyModelViewSet(OriginalCompanyModelViewSet):
    LIST_DOCUMENTATION = "wbportfolio/markdown/documentation/company.md"
    display_config_class = CompanyModelDisplay
    preview_config_class = CompanyPreviewConfig
    filterset_class = CompanyFilter
    ordering_fields = OriginalCompanyModelViewSet.ordering_fields + (
        "invested_assets_under_management_usd__nulls_last",
        "potential__nulls_last",
        "asset_under_management__nulls_last",
    )

    @cached_property
    def fx_rate_date(self) -> date:
        try:
            return CurrencyFXRates.objects.latest("date").date
        except CurrencyFXRates.DoesNotExist:
            return date.today()

    def get_serializer_class(self):
        if self.get_action() in ["list", "list-metadata"]:
            return CompanyModelListSerializer
        return CompanyModelSerializer

    def get_aggregates(self, queryset, **kwargs):
        sum_potential = queryset.aggregate(sum_potential=Sum("potential")).get("sum_potential", 0.0)
        sum_assets_under_management_usd = queryset.aggregate(
            sum_assets_under_management_usd=Sum("assets_under_management_usd")
        ).get("sum_assets_under_management_usd", 0.0)
        sum_invested_assets_under_management_usd = queryset.aggregate(
            sum_invested_assets_under_management_usd=Sum("invested_assets_under_management_usd")
        ).get("sum_invested_assets_under_management_usd", 0.0)
        return {
            "potential": {"Σ": format_number(sum_potential)},
            "asset_under_management": {"Σ": format_number(sum_assets_under_management_usd)},
            "invested_assets_under_management_usd": {"Σ": format_number(sum_invested_assets_under_management_usd)},
        }

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                asset_under_management=F("portfolio_data__assets_under_management"),
                assets_under_management_currency=F("portfolio_data__assets_under_management_currency"),
                assets_under_management_currency_repr=F("portfolio_data__assets_under_management_currency__symbol"),
                fx=CurrencyFXRates.get_fx_rates_subquery(
                    self.fx_rate_date, currency="assets_under_management_currency", lookup_expr="exact"
                ),
                assets_under_management_usd=F("asset_under_management") * F("fx"),
                invested_assets_under_management_usd=F("portfolio_data__invested_assets_under_management_usd"),
                investment_discretion=F("portfolio_data__investment_discretion"),
                potential=F("portfolio_data__potential"),
                potential_currency=F("portfolio_data__potential_currency"),
            )
        )


class PersonModelViewSet(OriginalPersonModelViewSet):
    LIST_DOCUMENTATION = "wbportfolio/markdown/documentation/person.md"
    display_config_class = PersonModelDisplay
    filterset_class = PersonFilter
    ordering_fields = OriginalPersonModelViewSet.ordering_fields + (
        "invested_assets_under_management_usd__nulls_last",
        "asset_under_management__nulls_last",
        "potential",
    )
    serializer_class = PersonModelSerializer

    def get_serializer_class(self) -> BasePersonModelSerializer:
        if self.get_action() in ["list", "list-metadata"]:
            return PersonModelListSerializer
        elif "pk" not in self.kwargs:
            return NewPersonModelSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(
            asset_under_management=Subquery(
                EmployerEmployeeRelationship.objects.filter(primary=True, employee__id=OuterRef("id")).values(
                    "employer__portfolio_data__assets_under_management"
                )[:1],
            ),
            asset_under_management_currency_repr=Subquery(
                EmployerEmployeeRelationship.objects.filter(primary=True, employee__id=OuterRef("id")).values(
                    "employer__portfolio_data__assets_under_management_currency__key"
                )[:1],
            ),
            invested_assets_under_management_usd=Subquery(
                EmployerEmployeeRelationship.objects.filter(primary=True, employee__id=OuterRef("id")).values(
                    "employer__portfolio_data__invested_assets_under_management_usd"
                )[:1],
            ),
            potential=Subquery(
                EmployerEmployeeRelationship.objects.filter(primary=True, employee__id=OuterRef("id")).values(
                    "employer__portfolio_data__potential"
                )[:1],
            ),
            potential_currency=Subquery(
                EmployerEmployeeRelationship.objects.filter(primary=True, employee__id=OuterRef("id")).values(
                    "employer__portfolio_data__potential_currency"
                )[:1],
            ),
            assets_under_management_currency=Subquery(
                EmployerEmployeeRelationship.objects.filter(primary=True, employee__id=OuterRef("id")).values(
                    "employer__portfolio_data__assets_under_management_currency"
                )[:1],
            ),
            investment_discretion=EmployerEmployeeRelationship.objects.filter(
                primary=True, employee__id=OuterRef("id")
            ).values("employer__portfolio_data__investment_discretion")[:1],
        )
        return qs


class AssetAllocationTypeRepresentationViewSet(viewsets.RepresentationViewSet):
    queryset = AssetAllocationType.objects.all()
    serializer_class = AssetAllocationTypeRepresentationSerializer


class AssetAllocationTypeModelViewSet(viewsets.ModelViewSet):
    queryset = AssetAllocationType.objects.all()
    serializer_class = AssetAllocationTypeModelSerializer


class AssetAllocationModelViewSet(viewsets.ModelViewSet):
    queryset = AssetAllocation.objects.all()
    serializer_class = AssetAllocationModelSerializer

    display_config_class = AssetAllocationDisplay
    endpoint_config_class = AssetAllocationModelEndpointConfig

    def get_queryset(self):
        qs = super().get_queryset()
        if company_id := self.kwargs.get("company_id", None):
            qs = qs.filter(company_id=company_id)
        return qs.select_related(
            "asset_type",
            "company",
        )


class GeographicFocusModelViewSet(viewsets.ModelViewSet):
    queryset = GeographicFocus.objects.all()
    serializer_class = GeographicFocusModelSerializer

    display_config_class = GeographicFocusDisplay
    endpoint_config_class = GeographicFocusModelEndpointConfig

    def get_queryset(self):
        if company_id := self.kwargs.get("company_id", None):
            return super().get_queryset().filter(company_id=company_id)
        return super().get_queryset()
