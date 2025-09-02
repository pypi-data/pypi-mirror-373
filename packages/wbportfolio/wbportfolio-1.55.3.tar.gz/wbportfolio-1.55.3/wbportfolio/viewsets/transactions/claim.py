import json
from contextlib import suppress
from datetime import date, timedelta
from decimal import Decimal

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from django.apps import apps
from django.contrib.messages import warning
from django.db.models import (
    BooleanField,
    Case,
    CharField,
    DecimalField,
    ExpressionWrapper,
    F,
    FloatField,
    OuterRef,
    Q,
    Subquery,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Coalesce, Concat, Least
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from django.utils.functional import cached_property
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from wbcore import viewsets as wb_viewsets
from wbcore.contrib.currency.models import CurrencyFXRates
from wbcore.contrib.directory.models import Entry
from wbcore.contrib.io.viewsets import ExportPandasAPIViewSet
from wbcore.enums import WidgetType
from wbcore.filters import DjangoFilterBackend
from wbcore.pandas import fields as pf
from wbcore.serializers import decorator
from wbcore.utils.date import get_date_interval_from_request
from wbcore.utils.strings import format_number
from wbcrm.models.accounts import Account
from wbfdm.models import ClassificationGroup, InstrumentPrice
from wbfdm.preferences import get_default_classification_group

from wbportfolio.analysis.claims import ConsolidatedTradeSummary
from wbportfolio.filters import (
    ClaimFilter,
    ConsolidatedTradeSummaryTableFilterSet,
    CumulativeNNMChartFilter,
    CustomerAPIFilter,
    CustomerClaimFilter,
    CustomerClaimGroupByFilter,
    DistributionNNMChartFilter,
    NegativeTermimalAccountPerProductFilterSet,
    ProfitAndLossPandasFilter,
)
from wbportfolio.models import Product, Trade
from wbportfolio.models.transactions.claim import Claim, ClaimGroupbyChoice
from wbportfolio.preferences import get_monthly_nnm_target
from wbportfolio.serializers import (
    ClaimAPIModelSerializer,
    ClaimCustomerModelSerializer,
    ClaimModelSerializer,
    ClaimRepresentationSerializer,
    ClaimTradeModelSerializer,
    NegativeTermimalAccountPerProductModelSerializer,
)

from ..configs.buttons import (
    ClaimTradeButtonConfig,
    ConsolidatedTradeSummaryButtonConfig,
)
from ..configs.buttons.claims import TransferTradeSerializer
from ..configs.display import (
    ClaimDisplayConfig,
    ConsolidatedTradeSummaryDisplayConfig,
    NegativeTermimalAccountPerProductDisplayConfig,
    ProfitAndLossPandasDisplayConfig,
)
from ..configs.endpoints import (
    ClaimAccountEndpointConfig,
    ClaimEndpointConfig,
    ClaimEntryEndpointConfig,
    ClaimProductEndpointConfig,
    ClaimTradeEndpointConfig,
    ConsolidatedTradeSummaryDistributionChartEndpointConfig,
    ConsolidatedTradeSummaryEndpointConfig,
    CumulativeNNMChartEndpointConfig,
    NegativeTermimalAccountPerProductEndpointConfig,
    ProfitAndLossPandasEndpointConfig,
)
from ..configs.titles import (
    ClaimAccountTitleConfig,
    ClaimEntryTitleConfig,
    ClaimProductTitleConfig,
    ClaimTitleConfig,
    ClaimTradeTitleConfig,
    ConsolidatedTradeSummaryDistributionChartTitleConfig,
    ConsolidatedTradeSummaryTitleConfig,
    CumulativeNNMChartTitleConfig,
    NegativeTermimalAccountPerProductTitleConfig,
    ProfitAndLossPandasTitleConfig,
)
from .mixins import ClaimPermissionMixin


class ClaimAPIModelViewSet(ClaimPermissionMixin, viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_class = CustomerAPIFilter
    queryset = Claim.objects.select_related("product", "claimant")
    serializer_class = ClaimAPIModelSerializer


class ClaimRepresentationViewSet(ClaimPermissionMixin, wb_viewsets.RepresentationViewSet):
    IDENTIFIER = "wbportfolio:claim"

    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    serializer_class = ClaimRepresentationSerializer
    queryset = Claim.objects.all()

    ordering_fields = ("title",)
    search_fields = (
        "product__name",
        "product__isin",
        "product__ticker",
        "claimant__computed_str",
    )
    ordering = ["id"]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .exclude(status=Claim.Status.WITHDRAWN)
            .select_related("product", "claimant", "account")
        )


class ClaimModelViewSet(ClaimPermissionMixin, wb_viewsets.ModelViewSet):
    IDENTIFIER = "wbportfolio:claim"

    serializer_class = ClaimModelSerializer
    queryset = Claim.objects.exclude(status=Claim.Status.WITHDRAWN)

    search_fields = [
        "claimant__computed_str",
        "product__name",
        "product__isin",
        "bank",
        "account__title",
        "trade_comment",
    ]
    ordering_fields = (
        "date",
        "product__name",
        "claimant",
        "account__title",
        "trade_comment",
        "shares",
        "last_nav",
        "total_value",
        "total_value_usd",
        "bank",
        "creator",
        "reference",
    )
    ordering = ["id", "-date"]

    display_config_class = ClaimDisplayConfig
    title_config_class = ClaimTitleConfig
    endpoint_config_class = ClaimEndpointConfig

    def get_filterset_class(self, request):
        profile = request.user.profile
        if profile.is_internal or request.user.is_superuser:
            return ClaimFilter
        return CustomerClaimFilter

    def get_messages(self, request, queryset=None, paginated_queryset=None, instance=None, initial=False):
        if instance and instance.product and instance.account:
            sum_shares = Claim.objects.exclude(status=Claim.Status.WITHDRAWN).filter(
                product=instance.product, account=instance.account
            ).aggregate(s=Sum("shares"))["s"] or Decimal(0.0)
            if sum_shares < 0:
                warning(
                    request,
                    f"The total shares balance for this account and for this product is negative of {sum_shares}",
                )

    def get_aggregates(self, queryset, paginated_queryset):
        return {
            "shares": {"Σ": format_number(queryset.aggregate(s=Sum("shares"))["s"] or 0, decimal=4)},
        }

    def get_serializer_class(self):
        profile = self.request.user.profile
        if profile.is_internal or self.request.user.is_superuser:
            return super().get_serializer_class()
        return ClaimCustomerModelSerializer

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                currency=F("product__currency__symbol"),
                last_nav=InstrumentPrice.subquery_closest_value(
                    "net_value", instrument_pk_name="product", date_lookup="exact"
                ),
                fx_rate=CurrencyFXRates.get_fx_rates_subquery("date", lookup_expr="exact"),
                total_value=F("last_nav") * F("shares"),
                total_value_usd=ExpressionWrapper(F("fx_rate") * F("total_value"), output_field=FloatField()),
                trade_claimed_shares=Coalesce(
                    Subquery(
                        Claim.objects.filter(Q(status=Claim.Status.APPROVED) & Q(trade=OuterRef("trade")))
                        .values("trade")
                        .annotate(s=Sum("shares"))
                        .values("s")[:1]
                    ),
                    Decimal(0),
                ),
                quantity=Case(
                    When(as_shares=True, then=F("shares")),
                    When(as_shares=False, then=F("nominal_amount")),
                    default=None,
                    output_field=DecimalField(max_digits=15, decimal_places=2),
                ),
                trade_type=Case(
                    When(shares__gte=0, then=Value(True)),
                    When(shares__lt=0, then=Value(False)),
                    output_field=BooleanField(),
                ),
                trade_comment=F("trade__comment"),
            )
            .select_related(
                "account",
                "trade",
                "product",
                "creator",
                "claimant",
            )
            .defer("account__reference_id")
        )


class ClaimAccountModelViewSet(ClaimModelViewSet):
    title_config_class = ClaimAccountTitleConfig
    endpoint_config_class = ClaimAccountEndpointConfig

    @cached_property
    def account(self):
        return get_object_or_404(Account, id=self.kwargs["account_id"])

    def get_queryset(self):
        return super().get_queryset().filter(account__in=self.account.get_descendants(include_self=True))


class ClaimProductModelViewSet(ClaimModelViewSet):
    title_config_class = ClaimProductTitleConfig
    endpoint_config_class = ClaimProductEndpointConfig

    @cached_property
    def product(self):
        return get_object_or_404(Product, id=self.kwargs["product_id"])

    def get_queryset(self):
        return super().get_queryset().filter(product=self.product)

    def get_identifier(self, request, identifier=None):
        return "commission:product-claim"


class ClaimEntryModelViewSet(ClaimModelViewSet):
    serializer_class = ClaimModelSerializer

    display_config_class = ClaimDisplayConfig
    title_config_class = ClaimEntryTitleConfig
    endpoint_config_class = ClaimEntryEndpointConfig
    ordering = ["id"]

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.kwargs["claimant_id"] = self.kwargs["entry_id"]  # ensure claimant_id is available for the serializer

    @cached_property
    def entry(self):
        return Entry.objects.get(id=self.kwargs["entry_id"])

    def get_queryset(self):
        return super().get_queryset().filter_for_customer(self.entry)


class ClaimTradeModelViewSet(ClaimModelViewSet):
    IDENTIFIER = "commission:trade-claim"

    serializer_class = ClaimTradeModelSerializer

    title_config_class = ClaimTradeTitleConfig
    endpoint_config_class = ClaimTradeEndpointConfig
    button_config_class = ClaimTradeButtonConfig

    @cached_property
    def trade(self) -> Trade:
        return get_object_or_404(Trade, pk=self.kwargs["trade_id"])

    @cached_property
    def product(self) -> Product | None:
        with suppress(Product.DoesNotExist):
            return Product.objects.get(id=self.trade.underlying_instrument.id)

    def get_queryset(self):
        return super().get_queryset().filter(trade__id=self.kwargs["trade_id"])

    @action(methods=["POST"], detail=False)
    def transfer_trade(self, request, trade_id):
        serializer = TransferTradeSerializer(data=request.data)
        if serializer.is_valid():
            trade = Trade.objects.get(id=trade_id)
            transfer_date = (parse_date(serializer.data["transfer_date"]) - pd.tseries.offsets.BDay(0)).date()
            from_account = serializer.data["from_account"]
            to_account = serializer.data["to_account"]

            if not transfer_date or not from_account or not to_account:
                return Response(
                    {"__notification": {"title": "Trade not Transferred."}}, status=status.HTTP_400_BAD_REQUEST
                )

            Claim.objects.create(
                trade=trade,
                shares=trade.shares * -1,
                bank=trade.bank,
                date=transfer_date,
                product=trade.product,
                account_id=from_account,
                claimant_id=request.user.profile.id,
            )

            Claim.objects.create(
                trade=trade,
                shares=trade.shares,
                bank=trade.bank,
                date=transfer_date,
                product=trade.product,
                account_id=to_account,
                claimant_id=request.user.profile.id,
            )

            return Response({"__notification": {"title": "Trade Transferred."}}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False)
    def quick_claim(self, request, trade_id):
        trade = Trade.objects.get(id=trade_id)

        account = request.data.get("account")

        if not account:
            return Response({"__notification": {"title": "Trade not Claimed."}}, status=status.HTTP_400_BAD_REQUEST)

        Claim.objects.create(
            trade=trade,
            shares=trade.shares,
            bank=trade.bank,
            date=trade.transaction_date,
            product=trade.product,
            account_id=account,
            claimant_id=request.user.profile.id,
        )

        return Response({"__notification": {"title": "Trade Claimed."}}, status=status.HTTP_200_OK)


# Abstract AUM Viewset


class ConsolidatedTradeSummaryTableView(ClaimPermissionMixin, ExportPandasAPIViewSet):
    IDENTIFIER = "commission:aum"

    def get_pandas_fields(self, request):
        fields = [
            pf.PKField(key="id", label="ID"),
            pf.CharField(key="title", label="Title"),
            pf.DateField(key="initial_investment_date", label="First Investment"),
            pf.SparklineField(key="aum_sparkline", label="AUM", dimension="double"),
            pf.FloatField(key="sum_shares_start", label="Shares Start", precision=0),
            pf.FloatField(key="sum_shares_end", label="Shares End", precision=0),
            pf.FloatField(key="sum_shares_diff", label="Share difference", precision=0),
            pf.FloatField(key="sum_shares_perf", label="Share Perf", precision=2, percent=True),
            pf.FloatField(
                key="sum_aum_start",
                label="AUM Start",
                precision=0,
                decorators=(decorator(decorator_type="text", position="left", value="$"),),
            ),
            pf.FloatField(
                key="sum_aum_end",
                label="AUM End",
                precision=0,
                decorators=(decorator(decorator_type="text", position="left", value="$"),),
            ),
            pf.FloatField(
                key="sum_aum_diff",
                label="Nominal difference",
                precision=0,
                decorators=(decorator(decorator_type="text", position="left", value="$"),),
            ),
            pf.FloatField(key="sum_aum_perf", label="% difference", precision=2, percent=True),
            pf.FloatField(
                key="sum_nnm_total",
                label="NNM",
                precision=0,
                decorators=(decorator(decorator_type="text", position="left", value="$"),),
            ),
            pf.FloatField(key="sum_nnm_perf", label="NNM (%)", precision=2, percent=True),
            pf.FloatField(key="total_performance", label="Performance", precision=2),
            pf.FloatField(key="total_performance_perf", label="Performance (%)", precision=2, percent=True),
        ]
        for nnm_column in self.nnm_monthly_columns:
            fields.append(
                pf.FloatField(
                    key=nnm_column[0],
                    label=nnm_column[1],
                    precision=0,
                    decorators=(decorator(decorator_type="text", position="left", value="$"),),
                ),
            )
        if self.commission_type_columns:
            fields.append(
                pf.FloatField(
                    key="rebate_total",
                    label="Rebate",
                    precision=0,
                    decorators=(decorator(decorator_type="text", position="left", value="$"),),
                )
            )

            for ct in self.commission_type_columns:
                fields.append(
                    pf.FloatField(
                        key=ct[0],
                        label=ct[1],
                        precision=0,
                        decorators=(decorator(decorator_type="text", position="left", value="$"),),
                    )
                )

        return pf.PandasFields(fields=fields)

    queryset = Claim.objects.filter(status=Claim.Status.APPROVED, account__isnull=False)

    filterset_class = ConsolidatedTradeSummaryTableFilterSet

    search_fields = ["title"]

    def get_ordering_fields(self):
        fields = [
            "title",
            "sum_shares_start",
            "sum_shares_end",
            "sum_shares_diff",
            "sum_shares_perf",
            "sum_aum_start",
            "sum_aum_end",
            "sum_aum_diff",
            "sum_aum_perf",
            "sum_nnm_total",
            "sum_nnm_perf",
            "total_performance",
            "total_performance_perf",
            *map(lambda x: x[0], self.nnm_monthly_columns),
        ]
        if self.commission_type_columns:
            fields.extend(list(map(lambda x: x[0], self.commission_type_columns)))
            fields.append("rebate_total")
        return fields

    ordering = ["-sum_aum_end"]
    display_config_class = ConsolidatedTradeSummaryDisplayConfig
    title_config_class = ConsolidatedTradeSummaryTitleConfig
    endpoint_config_class = ConsolidatedTradeSummaryEndpointConfig
    button_config_class = ConsolidatedTradeSummaryButtonConfig

    @cached_property
    def commission_type_columns(self) -> list[tuple[str, str]]:
        if apps.is_installed("wbcommission"):
            from wbcommission.models.commission import CommissionType

            return list(map(lambda x: ("rebate_" + x[0], x[1]), CommissionType.objects.values_list("key", "name")))

    @cached_property
    def nnm_monthly_columns(self) -> list[tuple[str, str]]:
        res = []
        if self.start_date and self.end_date:
            # + MonthEnd to ensure that we include the current month
            for _d in pd.date_range(
                self.start_date, self.end_date - timedelta(days=1) + pd.offsets.MonthEnd(), freq="ME"
            ):
                res.append(("sum_nnm_" + _d.strftime("%Y-%m"), _d.strftime("%b %Y")))
        return res

    @cached_property
    def start_date(self) -> date:
        return get_date_interval_from_request(self.request, exclude_weekend=True, left_interval_inclusive=True)[0]

    @cached_property
    def end_date(self) -> date:
        return get_date_interval_from_request(self.request, exclude_weekend=True, right_interval_inclusive=True)[1]

    @cached_property
    def groupby_classification_group(self) -> ClassificationGroup:
        try:
            return ClassificationGroup.objects.get(id=self.request.GET["groupby_classification_group"])
        except (ValueError, KeyError):
            return get_default_classification_group()

    @cached_property
    def unique_product(self) -> bool:
        return self.request.GET.get("product") is not None

    def _rebate_df(self, df_aum_end: pd.Series, **kwargs) -> pd.DataFrame:
        df = pd.DataFrame()
        if apps.is_installed("wbcommission"):
            from wbcommission.viewsets.rebate import RebatePandasView

            rebate_view = RebatePandasView()
            rebate_view.request = self.request
            df = rebate_view._get_dataframe(**kwargs).drop(["title", "index"], axis=1, errors="ignore").set_index("id")
            if not df.empty:
                return df.reindex(df_aum_end.index, fill_value=0)
        return df

    def add_messages(self, request, queryset=None, paginated_queryset=None, instance=None, initial=False):
        if self.unique_product:
            return warning(
                request, "Internal trades are excluded from the Net New Money total due to the selected product."
            )

    def get_dataframe(
        self,
        request,
        queryset,
        with_rebate_df: bool = True,
        with_aum_sparkline: bool = True,
        with_neg_pos_nnm: bool = False,
        **kwargs,
    ):
        groupby = self.request.GET.get("group_by", "PRODUCT")
        groupby_map = ClaimGroupbyChoice.get_map(groupby)
        pivot = groupby_map["pk"]
        pivot_label = groupby_map["title_key"]

        cts_generator = ConsolidatedTradeSummary(
            queryset,
            self.start_date,
            self.end_date,
            pivot,
            pivot_label,
            classification_group=self.groupby_classification_group,
        )

        df = cts_generator.df
        if not df.empty:
            df_aum = cts_generator.get_aum_df()
            df_nnm = cts_generator.get_nnm_df(filter_internal_trade=not self.unique_product)
            if with_neg_pos_nnm:
                self.df_nnm_neg = cts_generator.get_nnm_df(
                    only_negative=True, filter_internal_trade=not self.unique_product
                )
                self.df_nnm_pos = cts_generator.get_nnm_df(
                    only_positive=True, filter_internal_trade=not self.unique_product
                )

            df_aum_sparkline = pd.DataFrame()
            if with_aum_sparkline:
                df_aum_sparkline = cts_generator.get_aum_sparkline()
            df_rebate = pd.DataFrame()
            if with_rebate_df:
                df_rebate = self._rebate_df(df_aum["sum_aum_end"], **kwargs)
            df_initial_investment_date = cts_generator.get_initial_investment_date_df()

            df_title = df[["id", "title"]].groupby("id").first()
            df = pd.concat(
                [df_title, df_initial_investment_date, df_aum, df_nnm, df_aum_sparkline, df_rebate], axis=1
            ).reset_index(names="id")
            df["total_performance"] = df["sum_aum_end"] - (df["sum_aum_start"] + df["sum_nnm_total"])
            df["total_performance_perf"] = df["total_performance"] / df["sum_aum_start"]

            df.loc[df["sum_aum_start"] != 0, "sum_nnm_perf"] = (
                df.loc[df["sum_aum_start"] != 0, "sum_nnm_total"] / df.loc[df["sum_aum_start"] != 0, "sum_aum_start"]
            )
            df = df[(df["sum_shares_start"].abs() > 1) | (df["sum_shares_end"].abs() > 1)]
            df = df.replace([np.inf, -np.inf, np.nan], None)
            if hasattr(self, "df_nnm_neg"):
                self.df_nnm_neg = (
                    pd.concat([df_title, self.df_nnm_neg], axis=1)
                    .reset_index()
                    .replace([np.inf, -np.inf, np.nan], None)
                    .sort_values(by="title")
                )
            if hasattr(self, "df_nnm_pos"):
                self.df_nnm_pos = (
                    pd.concat([df_title, self.df_nnm_pos], axis=1)
                    .reset_index()
                    .replace([np.inf, -np.inf, np.nan], None)
                    .sort_values(by="title")
                )
        self._columns = df.columns
        return df

    def get_aggregates(self, request, df):
        if df.empty:
            return {}
        aggregates = {}
        for col in filter(
            lambda x: ("sum" in x and "perf" not in x) or x == "total_performance" or "rebate" in x, df.columns
        ):
            aggregates[col] = {"Σ": format_number(df[col].sum())}
        return aggregates

    def get_filterset_class(self, request):
        profile = request.user.profile
        if profile.is_internal or request.user.is_superuser:
            return ConsolidatedTradeSummaryTableFilterSet
        return CustomerClaimGroupByFilter


def _sanitize_df(df: pd.DataFrame, normalization_factor: pd.Series | None = None) -> pd.DataFrame:
    df = df.replace({0: np.nan})
    scalar_columns = df.columns.difference(["title", "id"])
    if normalization_factor is not None:
        df[scalar_columns] = df[scalar_columns].div(normalization_factor.replace({0: np.nan}), axis=0)
    return df.dropna(axis=0, how="all", subset=scalar_columns)


class ConsolidatedTradeSummaryDistributionChart(ConsolidatedTradeSummaryTableView):
    WIDGET_TYPE = WidgetType.CHART.value
    IDENTIFIER = "wbportfolio:consolidatedtradesummarydistributionchart"

    title_config_class = ConsolidatedTradeSummaryDistributionChartTitleConfig
    endpoint_config_class = ConsolidatedTradeSummaryDistributionChartEndpointConfig
    button_config_class = None

    def get_filterset_class(self, request):
        return DistributionNNMChartFilter

    @cached_property
    def is_percent(self) -> bool:
        return self.request.GET.get("percent", "false") == "true"

    # TODO This is not really optimal. We need to change it at some point
    def list(self, request, *args, **kwargs):
        # we copy pasted this function from the chartviewset. Can be optimize
        figure = go.Figure()
        self.request = request
        df = self._get_dataframe(**kwargs, with_rebate_df=False, with_aum_sparkline=False, with_neg_pos_nnm=True)
        if not df.empty:
            figure = self.get_plotly(df)
        figure_json = figure.to_json()  # we serialize to use the default PlotlyEncoder
        figure_dict = json.loads(
            figure_json
        )  # we reserialize to be able to hijack the figure config. This adds an extra steps of serialization/deserialization but the overhead is negligable.
        figure_dict["config"] = {"responsive": True, "displaylogo": False}
        figure_dict["useResizeHandler"] = True
        figure_dict["style"] = {"width": "100%", "height": "100%"}
        figure_dict["messages"] = list(self._get_messages(request))

        return Response(figure_dict)

    def get_plotly(self, df):
        fig = go.Figure()
        # create the groupby NNM distribution histogram
        df = df.sort_values(by="title").set_index("id")
        normalization_factor = None
        if self.is_percent:
            normalization_factor = df["sum_aum_start"]
        nnm_monthly_columns = dict(self.nnm_monthly_columns)
        df = _sanitize_df(
            df.drop(columns=df.columns.difference(["title", *nnm_monthly_columns.keys(), "sum_nnm_total"])),
            normalization_factor=normalization_factor,
        )
        for key, label in nnm_monthly_columns.items():
            if len(nnm_monthly_columns.keys()) == 1 and hasattr(self, "df_nnm_neg") and hasattr(self, "df_nnm_pos"):
                df_nnm_pos = _sanitize_df(self.df_nnm_pos.set_index("id"), normalization_factor)
                df_nnm_neg = _sanitize_df(self.df_nnm_neg.set_index("id"), normalization_factor)
                if key in df_nnm_neg.columns:
                    fig.add_trace(
                        go.Histogram(
                            histfunc="sum",
                            y=df_nnm_neg[key],
                            x=df_nnm_neg["title"],
                            name=label + " (Negative)",
                            marker_color="#FF6961",
                        )
                    )
                if key in df_nnm_pos.columns:
                    fig.add_trace(
                        go.Histogram(
                            histfunc="sum",
                            y=df_nnm_pos[key],
                            x=df_nnm_pos["title"],
                            name=label + " (Positive)",
                            marker_color="#77DD77",
                        )
                    )
            if key in df.columns:
                figure_kwargs = {"name": label}
                if len(nnm_monthly_columns.keys()) == 1:
                    figure_kwargs["marker_color"] = "#D3D3D3"
                    figure_kwargs["name"] = label + " (Total)"
                fig.add_trace(go.Histogram(histfunc="sum", y=df[key], x=df["title"], **figure_kwargs))
        if len(nnm_monthly_columns.keys()) > 1:
            fig.add_trace(
                go.Histogram(
                    histfunc="sum",
                    y=df["sum_nnm_total"],
                    x=df["title"],
                    name=f'[{self.start_date.strftime("%Y-%m-%d")}, {self.end_date.strftime("%Y-%m-%d")}]',
                )
            )
        fig.update_layout(
            template="plotly_white",
            margin=dict(l=10, r=10, t=0, b=40),
            showlegend=True,
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1,
                "xanchor": "center",
                "x": 0.5,
            },
        )
        if self.is_percent:
            fig.update_yaxes(tickformat=".2%")
        return fig


class CumulativeNNMChartView(ConsolidatedTradeSummaryDistributionChart):
    IDENTIFIER = "wbportfolio:cumulativennmchart"

    title_config_class = CumulativeNNMChartTitleConfig
    endpoint_config_class = CumulativeNNMChartEndpointConfig
    filterset_class = CumulativeNNMChartFilter

    @cached_property
    def projected_monthly_nnm_target(self) -> int:
        try:
            return int(self.request.GET["projected_monthly_nnm_target"])
        except (ValueError, KeyError):
            return get_monthly_nnm_target()

    @cached_property
    def hide_projected_monthly_nnm_target(self) -> bool:
        try:
            return self.request.GET["hide_projected_monthly_nnm_target"] == "true"
        except (ValueError, KeyError):
            return False

    def get_filterset_class(self, request):
        return CumulativeNNMChartFilter

    def get_plotly(self, df):
        fig = go.Figure()

        # create the cumulative NNM histogram
        nnm_monthly_columns_dict = dict(self.nnm_monthly_columns)

        nnm_monthly_columns = df.columns.intersection(nnm_monthly_columns_dict.keys())
        if not nnm_monthly_columns.empty and not df.empty:
            monthly_nnm = df[[*nnm_monthly_columns]].sum().cumsum().rename(index={**nnm_monthly_columns_dict})

            fig.add_trace(
                go.Histogram(
                    histfunc="sum",
                    y=monthly_nnm,
                    x=monthly_nnm.index,
                    autobinx=False,
                    showlegend=False,
                    yaxis="y",
                    marker_color="darkgrey",
                    name="Monthly Cumulative NNM",
                )
            )
            if not self.hide_projected_monthly_nnm_target:
                a = self.projected_monthly_nnm_target
                x = np.linspace(0, monthly_nnm.shape[0], monthly_nnm.shape[0] - 1)
                target_points = a * x + a
                fig.add_trace(
                    go.Scatter(
                        x=monthly_nnm.index[0:],
                        y=target_points,
                        mode="lines",
                        text="Projected NNM target",
                        line=dict(color="red", width=4),
                        showlegend=False,
                    )
                )
        return fig


class ProfitAndLossPandasView(ClaimPermissionMixin, ExportPandasAPIViewSet):
    IDENTIFIER = "commission:pnl"
    # LIST_DOCUMENTATION = "wbportfolio/commission/viewsets/documentation/profitandlosspandasview.md"
    # Averaging method based on https://www.tradingtechnologies.com/xtrader-help/fix-adapter-reference/pl-calculation-algorithm/understanding-pl-calculations/
    pandas_fields = pf.PandasFields(
        fields=(
            pf.PKField(key="id", label="ID"),
            pf.CharField(key="title", label="Product"),
            pf.FloatField(
                key="unrealized_pnl",
                label="Realized P&L",
                precision=2,
                decorators=(decorator(decorator_type="text", position="left", value="$"),),
                help_text="P&L_unrealized (points) = (Theoretical Exit Price - Avg Buy Price) *  total_shares",
            ),
            pf.FloatField(
                key="realized_pnl",
                label="Unrealized P&L",
                precision=2,
                decorators=(decorator(decorator_type="text", position="left", value="$"),),
                help_text="P&L_realized (points) = (Avg Sell Price - Avg Buy Price) * total_shares_sold",
            ),
            pf.FloatField(
                key="total_pnl",
                label="Total P&L",
                precision=2,
                decorators=(decorator(decorator_type="text", position="left", value="$"),),
                help_text="P&L_total (points) = P&L_unrealized + P&L_realized",
            ),
            pf.FloatField(
                key="total_invested",
                label="Total AUM",
                precision=2,
                decorators=(decorator(decorator_type="text", position="left", value="$"),),
                help_text="total_invested = Avg Buy Price * total_shares",
            ),
            pf.BooleanField(
                key="is_invested",
                label="Invested",
            ),
            pf.FloatField(
                key="performance",
                label="Performance",
                precision=2,
                percent=True,
                help_text="performance = P&L_total / total_invested",
            ),
        )
    )

    queryset = Claim.objects.filter(account__owner__isnull=False)

    filterset_class = ProfitAndLossPandasFilter

    search_fields = ("title",)
    ordering_fields = ["title", "unrealized_pnl", "realized_pnl", "total_pnl", "total_invested", "performance"]

    display_config_class = ProfitAndLossPandasDisplayConfig
    title_config_class = ProfitAndLossPandasTitleConfig
    endpoint_config_class = ProfitAndLossPandasEndpointConfig

    def get_aggregates(self, request, df):
        if df.empty:
            return {}
        return {
            "unrealized_pnl": {"Σ": format_number(df.unrealized_pnl.sum())},
            "realized_pnl": {"Σ": format_number(df.realized_pnl.sum())},
            "total_pnl": {"Σ": format_number(df.total_pnl.sum())},
            "total_invested": {"Σ": format_number(df.total_invested.sum())},
        }

    def get_queryset(self):
        start_date, end_date = get_date_interval_from_request(self.request, exclude_weekend=True)
        return (
            super()
            .get_queryset()
            .annotate(
                net_value=InstrumentPrice.subquery_closest_value(
                    "net_value", instrument_pk_name="product__pk", date_lookup="exact"
                ),
                fx_rate=CurrencyFXRates.get_fx_rates_subquery("date", lookup_expr="exact"),
                total_value=ExpressionWrapper(
                    F("net_value") * F("shares") * F("fx_rate"), output_field=DecimalField()
                ),
                date_end=Least(F("product__last_valuation_date"), Value(end_date)),
                net_value_end=InstrumentPrice.subquery_closest_value(
                    "net_value", date_name="date_end", instrument_pk_name="product__pk", date_lookup="exact"
                ),
                fx_rate_end=CurrencyFXRates.get_fx_rates_subquery("date_end", lookup_expr="exact"),
                price_end=ExpressionWrapper(F("net_value_end") * F("fx_rate_end"), output_field=DecimalField()),
            )
        )

    def get_dataframe(self, request, queryset, **kwargs):
        start_date, end_date = get_date_interval_from_request(self.request, exclude_weekend=True)
        if not start_date or not end_date:
            return pd.DataFrame()

        df = pd.DataFrame(queryset.values("shares", "total_value", "price_end", "account__owner__id", "product"))
        if not df.empty:
            df[["shares", "total_value"]] = df[["shares", "total_value"]].astype("float")

            df_price_end = (
                df[["price_end", "account__owner__id", "product"]].groupby(["account__owner__id", "product"]).mean()
            )
            df_buy = df[["shares", "total_value", "account__owner__id", "product"]][df["shares"] > 0]
            df_buy = df_buy.groupby(["account__owner__id", "product"]).agg({"shares": "sum", "total_value": "sum"})
            df_buy["total_value"] = df_buy.total_value / df_buy.shares
            df_buy = df_buy.rename(columns={"total_value": "avg_buy_price", "shares": "total_buy_shares"})

            df_sell = df[["shares", "total_value", "account__owner__id", "product"]][df["shares"] < 0]
            df_sell = df_sell.groupby(["account__owner__id", "product"]).agg({"shares": "sum", "total_value": "sum"})
            df_sell = df_sell.abs()
            df_sell["total_value"] = df_sell.total_value / df_sell.shares
            df_sell = df_sell.rename(columns={"total_value": "avg_sell_price", "shares": "total_sell_shares"})

            df = pd.concat([df_buy, df_sell], axis=1).fillna(0)
            df["realized_pnl"] = (df.avg_sell_price - df.avg_buy_price) * df.total_sell_shares
            df["total_shares"] = df.total_buy_shares - df.total_sell_shares

            df["unrealized_pnl"] = (df_price_end["price_end"] - df.avg_buy_price) * df.total_shares
            df["total_pnl"] = df.unrealized_pnl + df.realized_pnl
            df = df.groupby(level=0).sum().reset_index()

            df["total_invested"] = df.avg_buy_price * df.total_buy_shares

            df["performance"] = df.total_pnl.astype(float).divide(df.total_invested.astype(float))

            df["id"] = df["account__owner__id"]
            df["title"] = df["account__owner__id"].map(
                dict(Entry.objects.filter(id__in=df["id"]).values_list("id", "computed_str"))
            )
        return df.where(pd.notnull(df), None)


class NegativeTermimalAccountPerProductModelViewSet(ClaimPermissionMixin, wb_viewsets.ReadOnlyInfiniteModelViewSet):
    IDENTIFIER = "wbportfolio:negativeaccountproduct"

    serializer_class = NegativeTermimalAccountPerProductModelSerializer
    filterset_class = NegativeTermimalAccountPerProductFilterSet
    queryset = Claim.objects.filter(account__is_active=True)

    search_fields = ("account__title", "product__computed_str")
    ordering_fields = ("account__title", "product__computed_str", "sum_shares")
    ordering = "sum_shares"

    display_config_class = NegativeTermimalAccountPerProductDisplayConfig
    title_config_class = NegativeTermimalAccountPerProductTitleConfig
    endpoint_config_class = NegativeTermimalAccountPerProductEndpointConfig

    def get_aggregates(self, queryset, paginated_queryset):
        return {
            "sum_shares": {"Σ": format_number(queryset.aggregate(s=Sum("sum_shares"))["s"] or 0)},
        }

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("account", "product")
            .values("account", "product")
            .annotate(
                sum_shares=Sum("shares"),
                id=ExpressionWrapper(Concat(F("account__id"), Value("-"), F("product__id")), output_field=CharField()),
                account_repr=F("account__computed_str"),
                product_repr=F("product__computed_str"),
                account_id=F("account__id"),
                product_id=F("product__id"),
            )
            .filter(sum_shares__lt=0, account__isnull=False)
            .exclude(status=Claim.Status.WITHDRAWN)
            .values("account_repr", "product_repr", "account_id", "product_id", "sum_shares", "id")
        )
