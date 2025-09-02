import pandas as pd
from django.db.models import F, Sum
from rest_framework import filters
from wbcore.contrib.currency.models import CurrencyFXRates
from wbcore.contrib.io.viewsets import ExportPandasAPIViewSet
from wbcore.filters import DjangoFilterBackend
from wbcore.pandas import fields as pf
from wbcore.permissions.permissions import InternalUserPermissionMixin
from wbcore.serializers import decorator
from wbcore.utils.strings import format_number
from wbcore.viewsets import ModelViewSet

from wbportfolio.filters import FeesAggregatedFilter, FeesFilter, FeesProductFilterSet
from wbportfolio.models import Fees
from wbportfolio.serializers import FeesModelSerializer

from ..configs import (
    FeeEndpointConfig,
    FeesAggregatedProductPandasDisplayConfig,
    FeesAggregatedProductPandasEndpointConfig,
    FeesAggregatedProductTitleConfig,
    FeesButtonConfig,
    FeesDisplayConfig,
    FeesProductDisplayConfig,
    FeesProductEndpointConfig,
    FeesProductTitleConfig,
    FeesTitleConfig,
)
from ..mixins import UserPortfolioRequestPermissionMixin


class FeesModelViewSet(UserPortfolioRequestPermissionMixin, InternalUserPermissionMixin, ModelViewSet):
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
    )
    queryset = Fees.valid_objects.all()
    serializer_class = FeesModelSerializer
    filterset_class = FeesFilter

    display_config_class = FeesDisplayConfig
    title_config_class = FeesTitleConfig
    button_config_class = FeesButtonConfig
    endpoint_config_class = FeeEndpointConfig
    ordering = ["-fee_date", "id"]  # ordering by id because otherwise there is duplicates in the paginated view

    def get_aggregates(self, queryset, paginated_queryset):
        return {
            "total_value_fx_portfolio": {
                "Σ": format_number(queryset.aggregate(s=Sum("total_value_fx_portfolio"))["s"])
            },
            "total_value_gross_fx_portfolio": {
                "Σ": format_number(queryset.aggregate(s=Sum("total_value_gross_fx_portfolio"))["s"])
            },
        }

    def get_queryset(self):
        if self.is_manager:
            return super().get_queryset().select_related("import_source", "product")
        return Fees.objects.none()


class FeesProductModelViewSet(FeesModelViewSet):
    IDENTIFIER = "wbportfolio:product-fees"

    filterset_class = FeesProductFilterSet

    display_config_class = FeesProductDisplayConfig
    title_config_class = FeesProductTitleConfig
    endpoint_config_class = FeesProductEndpointConfig

    def get_queryset(self):
        if self.is_portfolio_manager:
            return super().get_queryset().filter(product=self.product)

        return Fees.objects.none()


class FeesAggregatedProductPandasView(
    UserPortfolioRequestPermissionMixin, InternalUserPermissionMixin, ExportPandasAPIViewSet
):
    IDENTIFIER = "wbportfolio:aggregetedfees"

    filterset_class = FeesAggregatedFilter

    queryset = Fees.valid_objects.all()

    display_config_class = FeesAggregatedProductPandasDisplayConfig
    title_config_class = FeesAggregatedProductTitleConfig
    endpoint_config_class = FeesAggregatedProductPandasEndpointConfig

    pandas_fields = pf.PandasFields(
        fields=(
            pf.PKField(key="id", label="ID"),
            pf.CharField(key="fee_date", label="Instrument"),
            pf.FloatField(
                key="TRANSACTION",
                label="Transactions",
                decorators=(decorator(decorator_type="text", position="left", value="$"),),
            ),
            pf.FloatField(
                key="PERFORMANCE_CRYSTALIZED",
                label="Performance",
                decorators=(decorator(decorator_type="text", position="left", value="$"),),
            ),
            pf.FloatField(
                key="PERFORMANCE",
                label="Performance Crystalized",
                decorators=(decorator(decorator_type="text", position="left", value="$"),),
            ),
            pf.FloatField(
                key="MANAGEMENT",
                label="Management",
                decorators=(decorator(decorator_type="text", position="left", value="$"),),
            ),
            pf.FloatField(
                key="ISSUER",
                label="Issuer",
                decorators=(decorator(decorator_type="text", position="left", value="$"),),
            ),
            pf.FloatField(
                key="OTHER", label="Other", decorators=(decorator(decorator_type="text", position="left", value="$"),)
            ),
            pf.FloatField(
                key="total", label="Total", decorators=(decorator(decorator_type="text", position="left", value="$"),)
            ),
        )
    )
    ordering = ["-fee_date"]
    ordering_fields = [
        "fee_date",
        "TRANSACTION",
        "PERFORMANCE_CRYSTALIZED",
        "PERFORMANCE",
        "MANAGEMENT",
        "ISSUER",
        "OTHER",
        "total",
    ]

    def get_aggregates(self, request, df):
        if df.empty:
            return {}
        return {
            "TRANSACTION": {"Σ": format_number(df["TRANSACTION"].sum())},
            "PERFORMANCE_CRYSTALIZED": {"Σ": format_number(df["PERFORMANCE_CRYSTALIZED"].sum())},
            "PERFORMANCE": {"Σ": format_number(df["PERFORMANCE"].sum())},
            "MANAGEMENT": {"Σ": format_number(df["MANAGEMENT"].sum())},
            "ISSUER": {"Σ": format_number(df["ISSUER"].sum())},
            "OTHER": {"Σ": format_number(df["OTHER"].sum())},
            "total": {"Σ": format_number(df["total"].sum())},
        }

    def get_queryset(self):
        if self.is_portfolio_manager:
            qs = super().get_queryset().filter(product=self.product)
            return qs.annotate(
                currency_fx_rate_usd=CurrencyFXRates.get_fx_rates_subquery(
                    "fee_date", currency="currency", lookup_expr="exact"
                ),
                total_value_fx_usd=F("total_value") * F("currency_fx_rate_usd"),
            )
        return Fees.objects.none()

    def get_dataframe(self, request, queryset, **kwargs):
        df = pd.DataFrame(queryset.values("fee_date", "transaction_subtype", "total_value_fx_usd"))
        if not df.empty:
            df = (
                df.pivot_table(
                    index="fee_date",
                    columns=["transaction_subtype"],
                    values="total_value_fx_usd",
                    aggfunc="sum",
                )
                .rename_axis(None, axis=1)
                .reset_index()
            )
            for type in Fees.Type.values:
                if type not in df:
                    df[type] = 0
            df["total"] = (
                df["TRANSACTION"]
                + df["PERFORMANCE_CRYSTALIZED"]
                + df["PERFORMANCE"]
                + df["MANAGEMENT"]
                + df["ISSUER"]
                + df["OTHER"]
            )
            df["id"] = df["fee_date"]
            df = df.fillna(0)
        return df
