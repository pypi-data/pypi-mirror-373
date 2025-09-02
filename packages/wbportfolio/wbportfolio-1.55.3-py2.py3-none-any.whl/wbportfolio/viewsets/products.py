from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.contrib.messages import info
from django.db.models import (
    ExpressionWrapper,
    F,
    FloatField,
    OuterRef,
    Q,
    Subquery,
    Sum,
)
from django.db.models.functions import Coalesce
from django.dispatch import receiver
from django.utils.functional import cached_property
from wbcore import viewsets
from wbcore.cache.decorators import cache_table
from wbcore.contrib.currency.models import Currency, CurrencyFXRates
from wbcore.permissions.permissions import InternalUserPermissionMixin
from wbcore.signals.instance_buttons import add_instance_button
from wbcore.utils.date import (
    get_date_interval_from_request,
    get_next_day_timedelta,
    get_start_and_end_date_from_date,
)
from wbcore.utils.figures import (
    get_default_timeserie_figure,
    get_hovertemplate_timeserie,
)
from wbcore.utils.strings import format_number
from wbfdm.contrib.metric.backends.performances import PERFORMANCE_METRIC
from wbfdm.contrib.metric.viewsets.mixins import InstrumentMetricMixin
from wbfdm.models import Instrument, InstrumentPrice

from wbportfolio import serializers
from wbportfolio.filters import (
    BaseProductFilterSet,
    ProductCustomerFilter,
    ProductFeeFilter,
    ProductFilter,
)
from wbportfolio.models import Fees, Product, Trade
from wbportfolio.viewsets.configs.buttons.mixins import InstrumentButtonMixin

from .configs import (
    AUMProductEndpointConfig,
    AUMProductTitleConfig,
    InstrumentPriceAUMDataEndpointConfig,
    InstrumentPriceAUMDataTitleConfig,
    NominalProductEndpointConfig,
    NominalProductTitleConfig,
    ProductButtonConfig,
    ProductCustomerButtonConfig,
    ProductCustomerDisplayConfig,
    ProductCustomerEndpointConfig,
    ProductDisplayConfig,
    ProductPerformanceFeesDisplayConfig,
    ProductPerformanceFeesEndpointConfig,
    ProductPerformanceFeesTitleConfig,
)
from .mixins import UserPortfolioRequestPermissionMixin


class ProductRepresentationViewSet(viewsets.RepresentationViewSet):
    IDENTIFIER = "wbportfolio:product"
    serializer_class = serializers.ProductRepresentationSerializer
    filterset_class = BaseProductFilterSet

    queryset = Product.objects.all()
    ordering_fields = ordering = ("computed_str",)
    search_fields = ("computed_str",)

    def get_queryset(self):
        return Product.get_products(self.request.user.profile).annotate(bank_name=F("bank__name"))


class ProductModelViewSet(InstrumentMetricMixin, viewsets.ModelViewSet):
    filterset_class = ProductFilter
    queryset = Product.objects.all()
    METRIC_KEYS = (PERFORMANCE_METRIC,)
    METRIC_WITH_PREFIXED_KEYS = True

    @property
    def metric_basket_class(self):
        return Instrument

    ordering_fields = (
        "is_invested",
        "name_repr",
        "parent__name__nulls_last",
        "bank__name",
        "current_issuer_fees_percent",
        "currency__key",
        "isin",
        "ticker",
        "last_valuation_date",
        "net_value",
        "assets_under_management",
        "assets_under_management_usd",
        "nnm_weekly",
        "nnm_monthly",
        "nnm_year_to_date",
        "nnm_yearly",
        "tags__title__nulls_last",
    )
    search_fields = (
        "name",
        "isin",
        "ticker",
        "white_label_customers__computed_str",
        "parent__name",
        "computed_str",
    )
    ordering = ["name_repr"]

    display_config_class = ProductDisplayConfig
    button_config_class = ProductButtonConfig

    def get_aggregates(self, queryset, paginated_queryset):
        aggregates = {}
        if self.request.user.profile.is_internal or self.request.user.is_superuser:
            df = pd.DataFrame(
                queryset.values(
                    "currency",
                    "nnm_weekly",
                    "nnm_monthly",
                    "nnm_year_to_date",
                    "nnm_yearly",
                    "assets_under_management",
                    "assets_under_management_usd",
                    "is_invested",
                )
            )  # we use pandas to avoid unnecessary db calls
            product_aggregates = defaultdict(dict)
            if not df.empty:
                currency_symbol_map = dict(Currency.objects.filter(id__in=df.currency).values_list("id", "symbol"))
                for currency_id in df.currency.unique():
                    currency_symbol = currency_symbol_map[currency_id]

                    for field in ["nnm_weekly", "nnm_monthly", "nnm_year_to_date", "nnm_yearly"]:
                        product_aggregates[field][currency_symbol] = format_number(
                            df.loc[df["currency"] == currency_id, field].sum()
                        )

                    dff = df.loc[(df["currency"] == currency_id) & (df["is_invested"])]
                    product_aggregates["assets_under_management"][currency_symbol] = format_number(
                        dff["assets_under_management"].sum()
                    )
                product_aggregates["assets_under_management_usd"]["Σ"] = format_number(
                    df[df["is_invested"]]["assets_under_management_usd"].sum()
                )

                # Double Accounting with only is_invested = False
                product_aggregates["assets_under_management_usd"]["Σ (DA)"] = format_number(
                    df[~df["is_invested"]]["assets_under_management_usd"].sum()
                )

            aggregates.update(product_aggregates)

        return aggregates

    def get_serializer_class(self):
        if getattr(self, "action", None) == "list":
            return serializers.ProductListModelSerializer
        return serializers.ProductModelSerializer

    def get_queryset(self):
        today = date.today()
        base_qs = Product.annotate_last_aum(
            Product.get_products(self.request.user.profile, base_qs=super().get_queryset())
        )
        return (
            base_qs.annotate(
                nnm_weekly=Coalesce(
                    Subquery(
                        Trade.valid_external_customer_trade_objects.filter(
                            underlying_instrument=OuterRef("pk"), transaction_date__gte=today - timedelta(days=7)
                        )
                        .values("underlying_instrument")
                        .annotate(sum_aum=Sum("total_value"))
                        .values("sum_aum")[:1]
                    ),
                    Decimal(0),
                ),
                nnm_monthly=Coalesce(
                    Subquery(
                        Trade.valid_external_customer_trade_objects.filter(
                            underlying_instrument=OuterRef("pk"), transaction_date__gte=today - timedelta(days=30)
                        )
                        .values("underlying_instrument")
                        .annotate(sum_aum=Sum("total_value"))
                        .values("sum_aum")[:1]
                    ),
                    Decimal(0),
                ),
                nnm_year_to_date=Coalesce(
                    Subquery(
                        Trade.valid_external_customer_trade_objects.filter(
                            underlying_instrument=OuterRef("pk"), transaction_date__year=today.year
                        )
                        .values("underlying_instrument")
                        .annotate(sum_aum=Sum("total_value"))
                        .values("sum_aum")[:1]
                    ),
                    Decimal(0),
                ),
                nnm_yearly=Coalesce(
                    Subquery(
                        Trade.valid_external_customer_trade_objects.filter(
                            underlying_instrument=OuterRef("pk"), transaction_date__gte=today - timedelta(days=365)
                        )
                        .values("underlying_instrument")
                        .annotate(sum_aum=Sum("total_value"))
                        .values("sum_aum")[:1]
                    ),
                    Decimal(0),
                ),
            )
            .select_related("currency", "bank", "parent")
            .prefetch_related("white_label_customers", "classifications")
        )


class ProductCustomerModelViewSet(viewsets.ModelViewSet):
    IDENTIFIER = "wbportfolio:productcustomer"

    serializer_class = serializers.ProductCustomerModelSerializer
    filterset_class = ProductCustomerFilter
    queryset = Product.active_objects.all()

    search_fields = ("name", "isin", "ticker")
    ordering_fields = ("name", "isin", "ticker")
    ordering = ["name"]

    display_config_class = ProductCustomerDisplayConfig
    button_config_class = ProductCustomerButtonConfig
    endpoint_config_class = ProductCustomerEndpointConfig

    def get_queryset(self):
        qs = (
            Product.get_products(self.request.user.profile)
            .filter(id__in=Product.active_objects.values("id"))
            .annotate(
                net_value=InstrumentPrice.subquery_closest_value(
                    "net_value",
                    val_date=None,
                    date_name="last_valuation_date",
                    instrument_pk_name="pk",
                    date_lookup="exact",
                ),
                bank_repr=F("bank__name"),
                currency_symbol=F("currency__symbol"),
            )
        )
        return qs.filter(net_value__isnull=False)


class ProductPerformanceFeesModelViewSet(
    UserPortfolioRequestPermissionMixin, InternalUserPermissionMixin, viewsets.ModelViewSet
):
    search_fields = ("name", "isin", "ticker", "computed_str")
    ordering_fields = (
        "computed_str",
        "isin",
        "ticker",
        "sum_management_fees",
        "sum_management_fees_usd",
        "sum_performance_fees_net",
        "sum_total",
        "sum_performance_fees_net_usd",
        "sum_total_usd",
    )
    ordering = ["computed_str"]
    queryset = Product.active_objects.all()

    serializer_class = serializers.ProductFeesModelSerializer
    filterset_class = ProductFeeFilter

    display_config_class = ProductPerformanceFeesDisplayConfig
    title_config_class = ProductPerformanceFeesTitleConfig
    endpoint_config_class = ProductPerformanceFeesEndpointConfig

    def get_aggregates(self, queryset, paginated_queryset):
        if not queryset.exists():
            return dict()
        return {
            # NOTE: This does not work at the moment. Somehow grouped by currency is a problem...Weird
            "sum_management_fees_usd": {
                "Σ": format_number(queryset.aggregate(s=Sum(F("sum_management_fees_usd")))["s"])
            },
            "sum_performance_fees_net_usd": {
                "Σ": format_number(queryset.aggregate(s=Sum(F("sum_performance_fees_net_usd")))["s"])
            },
            "sum_total_usd": {"Σ": format_number(queryset.aggregate(s=Sum(F("sum_total_usd")))["s"])},
        }

    @cached_property
    def latest_rate_date(self) -> date:
        try:
            return CurrencyFXRates.objects.latest("date").date
        except CurrencyFXRates.DoesNotExist:
            return date.today()

    def add_messages(self, request, queryset=None, paginated_queryset=None, instance=None, initial=False):
        return info(request, f"The FX Rates from the {self.latest_rate_date:%d.%m.%Y} were used.")

    def get_queryset(self):
        if (latest_rate_date := self.latest_rate_date) and self.is_manager:
            # Check for Filter because they are fake
            date_gte, date_lte = get_date_interval_from_request(self.request, exclude_weekend=True)

            if date_lte is None and date_gte is None:
                date_gte, date_lte = get_start_and_end_date_from_date(date.today())

            fees = Fees.valid_objects.filter(product=OuterRef("pk"))
            if date_gte:
                fees = fees.filter(fee_date__gte=date_gte)
            if date_lte:
                fees = fees.filter(fee_date__lte=date_lte)

            management_fees = Coalesce(
                Subquery(
                    fees.filter(transaction_subtype=Fees.Type.MANAGEMENT)
                    .values("product")
                    .annotate(sum_management_fees=Sum("total_value"))
                    .values("sum_management_fees")[:1],
                    output_field=FloatField(),
                ),
                0.0,
            )

            performance_fees_net = Coalesce(
                Subquery(
                    fees.filter(
                        Q(transaction_subtype=Fees.Type.PERFORMANCE)
                        | Q(transaction_subtype=Fees.Type.PERFORMANCE_CRYSTALIZED)
                    )
                    .values("product")
                    .annotate(sum_performance_fees_net=Sum("total_value"))
                    .values("sum_performance_fees_net")[:1],
                    output_field=FloatField(),
                ),
                0.0,
            )

            qs = (
                Product.get_products(self.request.user.profile)
                .annotate(
                    sum_management_fees=management_fees,
                    sum_performance_fees_net=performance_fees_net,
                    fx_rate=CurrencyFXRates.get_fx_rates_subquery(
                        latest_rate_date, currency="currency", lookup_expr="exact"
                    ),
                    sum_management_fees_usd=ExpressionWrapper(
                        F("sum_management_fees") * F("fx_rate"), output_field=FloatField()
                    ),
                    sum_performance_fees_net_usd=ExpressionWrapper(
                        F("sum_performance_fees_net") * F("fx_rate"),
                        output_field=FloatField(),
                    ),
                    sum_total=F("sum_management_fees") + F("sum_performance_fees_net"),
                    sum_total_usd=F("sum_management_fees_usd") + F("sum_performance_fees_net_usd"),
                )
                .select_related("currency")
                .prefetch_related("fees", "prices")
            )
            return qs

        return Product.objects.none()


# Product based InstrumentPrice Chartview sets


class NominalProductChartView(viewsets.ChartViewSet):
    IDENTIFIER = "wbportfolio:price"
    filterset_fields = {
        "date": ["gte", "exact", "lte"],
    }
    queryset = InstrumentPrice.objects.all()

    title_config_class = NominalProductTitleConfig
    endpoint_config_class = NominalProductEndpointConfig

    def get_plotly(self, queryset):
        fig = get_default_timeserie_figure()
        product = Product.objects.get(id=self.kwargs["product_id"])
        df = pd.DataFrame(queryset.values("date", "outstanding_shares", "calculated"))
        df = df.sort_values(by="calculated").groupby("date").first().dropna()
        df["nominal_value"] = df["outstanding_shares"] * product.share_price
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df.nominal_value,
                mode="lines",
                fill="tozeroy",
                name=f"Nominal Value ({product.currency.key})",
                hovertemplate=get_hovertemplate_timeserie(currency=""),
            )
        )
        return fig

    def get_queryset(self):
        return InstrumentPrice.objects.filter(instrument=self.kwargs["product_id"], outstanding_shares__isnull=False)


class AUMProductChartView(viewsets.ChartViewSet):
    IDENTIFIER = "wbportfolio:price"
    filterset_fields = {
        "date": ["gte", "exact", "lte"],
    }
    queryset = InstrumentPrice.objects.all()

    title_config_class = AUMProductTitleConfig
    endpoint_config_class = AUMProductEndpointConfig

    def get_plotly(self, queryset):
        fig = get_default_timeserie_figure()
        product = Product.objects.get(id=self.kwargs["product_id"])
        df = pd.DataFrame(queryset.values("date", "outstanding_shares", "net_value", "calculated"))
        df = df.sort_values(by="calculated").groupby("date").first().dropna()
        df["assets_under_management"] = df["outstanding_shares"] * df["net_value"]

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df.assets_under_management,
                mode="lines",
                fill="tozeroy",
                name=f"AUM ({product.currency.key})",
                hovertemplate=get_hovertemplate_timeserie(currency=""),
            )
        )

        return fig

    def get_queryset(self):
        return super().get_queryset().filter(instrument=self.kwargs["product_id"], outstanding_shares__isnull=False)


@cache_table(timeout=get_next_day_timedelta(), periodic_caching=True)
class InstrumentPriceAUMDataChartView(viewsets.ChartViewSet):
    IDENTIFIER = "wbportfolio:aum-price"
    LIST_TITLE = "Assets under Management"

    queryset = InstrumentPrice.objects.annotate_base_data()

    title_config_class = InstrumentPriceAUMDataTitleConfig
    endpoint_config_class = InstrumentPriceAUMDataEndpointConfig

    def get_plotly(self, queryset):
        fig = get_default_timeserie_figure(add_rangeslider=False)

        df_net_value = pd.DataFrame(
            queryset.filter(calculated=False, net_value_usd__isnull=False)
            .exclude(net_value_usd=0)
            .values("instrument", "date", "net_value_usd")
        )
        df_outstanding_shares = pd.DataFrame(
            queryset.filter(outstanding_shares__isnull=False)
            .exclude(outstanding_shares=0)
            .values("instrument", "date", "outstanding_shares", "calculated")
        )
        if not df_outstanding_shares.empty and not df_net_value.empty:
            # get the none calculated outstanding share if possible, otherwise get the calculated one
            df_outstanding_shares = (
                (
                    df_outstanding_shares.sort_values(by=["instrument", "date", "calculated"])
                    .groupby(["instrument", "date"])
                    .first()
                )
                .groupby(level=0)
                .ffill()
            )
            df_net_value = df_net_value.set_index(["instrument", "date"])
            df = pd.concat([df_net_value["net_value_usd"], df_outstanding_shares["outstanding_shares"]], axis=1)

            # we reindex to account for missing pos.
            df = df.reindex(
                pd.MultiIndex.from_product(
                    [
                        df.index.levels[0],
                        pd.date_range(df.index.levels[1].min(), df.index.levels[1].max(), freq="W-MON"),
                    ],  # we downsample to make the chart easier on the frontend
                    names=["instrument", "date"],
                )
            )

            # forward fill around the instrument
            df = df.groupby(level=0).ffill().reset_index()

            df["market_capitalization_usd"] = df["outstanding_shares"] * df["net_value_usd"]

            df["instrument_repr"] = df["instrument"].map(dict(Product.objects.values_list("id", "computed_str")))
            df["instrument"] = df["instrument"].map(dict(Product.objects.values_list("id", "isin")))
            df = df.where(pd.notnull(df), None)
            fig = px.area(
                df,
                x="date",
                y="market_capitalization_usd",
                line_group="instrument",
                hover_name="instrument_repr",
                color="instrument",
            )
        return fig

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                instrument__in=Product.objects.values("id"),
            )
            .select_related("instrument")
        )


@receiver(add_instance_button, sender=ProductModelViewSet)
def add_product_instrument_request_button(sender, many, *args, request=None, view=None, pk=None, **kwargs):
    return InstrumentButtonMixin.add_instrument_request_button(request=request, view=view, pk=pk)


@receiver(add_instance_button, sender=ProductModelViewSet)
def add_product_transactions_request_button(sender, many, *args, request=None, view=None, pk=None, **kwargs):
    return InstrumentButtonMixin.add_transactions_request_button(request=request, view=view, pk=pk)
