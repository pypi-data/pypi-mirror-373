from contextlib import suppress
from datetime import date, datetime

import pandas as pd
from django.db.models import Exists, F, OuterRef, Q, Sum
from django.utils.dateparse import parse_date
from django.utils.functional import cached_property
from wbcore import viewsets
from wbcore.contrib.currency.models import CurrencyFXRates
from wbcore.contrib.io.viewsets import ExportPandasAPIViewSet
from wbcore.pandas import fields as pf
from wbcore.permissions.permissions import InternalUserPermissionMixin
from wbcore.serializers import decorator
from wbcore.utils.strings import format_number
from wbfdm.contrib.metric.viewsets.mixins import InstrumentMetricMixin
from wbfdm.models import Instrument

from wbportfolio.filters import (
    AssetPositionFilter,
    AssetPositionInstrumentFilter,
    AssetPositionPortfolioFilter,
    CashPositionPortfolioFilterSet,
    CompositionModelPortfolioPandasFilter,
)
from wbportfolio.import_export.resources.assets import AssetPositionResource
from wbportfolio.metric.backends.portfolio_base import (
    PORTFOLIO_CAPITAL_EMPLOYED,
    PORTFOLIO_EBIT,
    PORTFOLIO_LIABILITIES,
    PORTFOLIO_ROCE,
    PORTFOLIO_TOTAL_ASSETS,
)
from wbportfolio.metric.backends.portfolio_esg import PORTFOLIO_ESG_KEYS
from wbportfolio.models import (
    AssetPosition,
    InstrumentPortfolioThroughModel,
    Portfolio,
    Product,
)
from wbportfolio.serializers.assets import (
    AssetPositionAggregatedPortfolioModelSerializer,
    AssetPositionInstrumentModelSerializer,
    AssetPositionModelSerializer,
    AssetPositionPortfolioModelSerializer,
    CashPositionPortfolioModelSerializer,
)

from .configs import (
    AssetPositionButtonConfig,
    AssetPositionDisplayConfig,
    AssetPositionEndpointConfig,
    AssetPositionInstrumentButtonConfig,
    AssetPositionInstrumentDisplayConfig,
    AssetPositionInstrumentEndpointConfig,
    AssetPositionInstrumentTitleConfig,
    AssetPositionPortfolioButtonConfig,
    AssetPositionPortfolioDisplayConfig,
    AssetPositionPortfolioEndpointConfig,
    AssetPositionPortfolioTitleConfig,
    AssetPositionTitleConfig,
    CashPositionPortfolioDisplayConfig,
    CashPositionPortfolioEndpointConfig,
    CashPositionPortfolioTitleConfig,
    CompositionModelPortfolioPandasDisplayConfig,
    CompositionModelPortfolioPandasEndpointConfig,
    CompositionModelPortfolioPandasTitleConfig,
)
from .mixins import UserPortfolioRequestPermissionMixin


class AssetPositionModelViewSet(
    UserPortfolioRequestPermissionMixin,
    InternalUserPermissionMixin,
    viewsets.ReadOnlyModelViewSet,
):
    IDENTIFIER = "wbportfolio:assetposition"
    IMPORT_ALLOWED = False

    queryset = AssetPosition.objects.all()
    serializer_class = AssetPositionModelSerializer
    filterset_class = AssetPositionFilter

    ordering_fields = [
        "total_value_fx_portfolio",
        "total_value_fx_usd",
        "total_value",
        "portfolio__name",
        "portfolio_created__name",
        "underlying_quote",
        "underlying_quote_name",
        "underlying_quote_ticker",
        "underlying_quote_isin",
        "price",
        "currency__key",
        "currency_fx_rate",
        "shares",
        "date",
        "asset_valuation_date",
        "weighting",
        "market_share",
        "liquidity",
    ]
    ordering = ["-weighting"]
    search_fields = ["underlying_quote_ticker", "underlying_quote_name", "underlying_quote_isin"]

    display_config_class = AssetPositionDisplayConfig
    button_config_class = AssetPositionButtonConfig
    endpoint_config_class = AssetPositionEndpointConfig
    title_config_class = AssetPositionTitleConfig

    def get_resource_class(self):
        return AssetPositionResource

    def get_aggregates(self, queryset, paginated_queryset):
        aggregates = super().get_aggregates(queryset, paginated_queryset)
        if queryset.exists():
            total_value_fx_usd = queryset.aggregate(s=Sum(F("total_value_fx_usd")))["s"]
            weighting = queryset.aggregate(s=Sum(F("weighting")))["s"]
            aggregates.update(
                {
                    "weighting": {"Σ": format_number(weighting, decimal=8)},
                    "total_value_fx_usd": {"Σ": format_number(total_value_fx_usd)},
                }
            )
        return aggregates

    def get_queryset(self):
        if self.is_analyst:
            return (
                super()
                .get_queryset()
                .annotate(
                    underlying_quote_isin=F("underlying_quote__isin"),
                    underlying_quote_ticker=F("underlying_quote__ticker"),
                    underlying_quote_name=F("underlying_quote__name"),
                )
                .select_related(
                    "underlying_quote",
                    "currency",
                    "portfolio",
                    "exchange",
                    "portfolio_created",
                )
            )
        return AssetPosition.objects.none()


# Portfolio Viewsets


class AssetPositionPortfolioModelViewSet(InstrumentMetricMixin, AssetPositionModelViewSet):
    METRIC_KEYS = (
        PORTFOLIO_EBIT,
        PORTFOLIO_TOTAL_ASSETS,
        PORTFOLIO_LIABILITIES,
        PORTFOLIO_CAPITAL_EMPLOYED,
        PORTFOLIO_ROCE,
        *PORTFOLIO_ESG_KEYS,
    )
    METRIC_BASKET_LABEL = "portfolio"
    METRIC_INSTRUMENT_LABEL = "underlying_quote"
    METRIC_SHOW_BY_DEFAULT = False
    METRIC_SHOW_FILTERS = True

    @property
    def metric_date(self):
        if date_str := self.request.GET.get("date"):
            return parse_date(date_str)

    @property
    def metric_basket(self):
        return self.portfolio

    filterset_class = AssetPositionPortfolioFilter
    display_config_class = AssetPositionPortfolioDisplayConfig
    button_config_class = AssetPositionPortfolioButtonConfig
    title_config_class = AssetPositionPortfolioTitleConfig
    endpoint_config_class = AssetPositionPortfolioEndpointConfig

    def get_serializer_class(self):
        if self.request.GET.get("aggregate", "false") == "true":
            return AssetPositionAggregatedPortfolioModelSerializer
        return AssetPositionPortfolioModelSerializer

    def get_aggregates(self, queryset, paginated_queryset):
        if not queryset.exists():
            return {}
        weighting = queryset.aggregate(s=Sum(F("weighting")))["s"]
        total_value_fx_portfolio = queryset.aggregate(s=Sum(F("total_value_fx_portfolio")))["s"]
        aggregates = super().get_aggregates(queryset, paginated_queryset)
        aggregates["total_value_fx_portfolio"] = {"Σ": format_number(total_value_fx_portfolio)}
        aggregates["weighting"] = {"Σ": format_number(weighting, decimal=8)}
        return aggregates

    def get_queryset(self):
        if self.has_portfolio_access:
            return (
                super()
                .get_queryset()
                .filter(portfolio=self.portfolio)
                .select_related("underlying_quote", "currency", "exchange", "portfolio_created")
            )
        return AssetPosition.objects.none()


# Underlying Assets viewsets
class AssetPositionInstrumentModelViewSet(AssetPositionModelViewSet):
    filterset_class = AssetPositionInstrumentFilter
    serializer_class = AssetPositionInstrumentModelSerializer
    display_config_class = AssetPositionInstrumentDisplayConfig
    title_config_class = AssetPositionInstrumentTitleConfig
    button_config_class = AssetPositionInstrumentButtonConfig
    endpoint_config_class = AssetPositionInstrumentEndpointConfig

    def get_aggregates(self, queryset, paginated_queryset):
        queryset = queryset.filter(is_invested=True)
        if queryset.exists():
            total_value_fx_usd = queryset.aggregate(s=Sum(F("total_value_fx_usd")))["s"]
            total_shares = queryset.aggregate(s=Sum(F("shares")))["s"]
            total_market_share = queryset.aggregate(s=Sum(F("market_share")))["s"]
            return {
                "shares": {"Σ": format_number(total_shares)},
                "total_value_fx_usd": {"Σ": format_number(total_value_fx_usd)},
                "market_share": {"Σ": format_number(total_market_share)},
            }
        return {}

    def get_queryset(self):
        qs = super().get_queryset().filter(underlying_quote__in=self.instrument.get_descendants(include_self=True))
        if self.request.GET.get("filter_last_positions", "false") == "true":
            if self.instrument.assets.exists():
                qs = qs.filter(date=self.instrument.assets.latest("date").date)
        return qs


class CashPositionPortfolioPandasAPIView(
    UserPortfolioRequestPermissionMixin, InternalUserPermissionMixin, ExportPandasAPIViewSet
):
    queryset = AssetPosition.objects.all()
    display_config_class = CashPositionPortfolioDisplayConfig
    title_config_class = CashPositionPortfolioTitleConfig
    endpoint_config_class = CashPositionPortfolioEndpointConfig

    serializer_class = CashPositionPortfolioModelSerializer
    filterset_class = CashPositionPortfolioFilterSet

    search_fields = ["portfolio_name"]
    ordering_fields = ["portfolio_name", "total_value_fx_usd", "portfolio_weight"]

    pandas_fields = pf.PandasFields(
        fields=(
            pf.PKField(key="portfolio", label="ID"),
            pf.CharField(key="portfolio_name", label="Portfolio"),
            pf.FloatField(
                key="total_value_fx_usd",
                label="Total Value",
                precision=2,
                decorators=(decorator(decorator_type="text", position="right", value="$"),),
            ),
            pf.FloatField(key="portfolio_weight", label="Total portfolio value", precision=2, percent=True),
        )
    )

    def get_aggregates(self, request, df):
        if not df.empty:
            sum_total_value_fx_usd = df.total_value_fx_usd.sum()
            return {
                "total_value_fx_usd": {"Σ": format_number(sum_total_value_fx_usd)},
            }
        return {}

    def get_dataframe(self, request, queryset, **kwargs):
        df = pd.DataFrame()
        if queryset.exists():
            df = pd.DataFrame(
                queryset.values(
                    "underlying_instrument__is_cash",
                    "total_value_fx_portfolio",
                    "fx_rate",
                    "portfolio__name",
                    "portfolio",
                )
            )
            df_name = (
                df[["portfolio", "portfolio__name"]]
                .groupby("portfolio")
                .agg("first")
                .rename(columns={"portfolio__name": "portfolio_name"})
            )

            df["total_value_fx_usd"] = df.total_value_fx_portfolio * df.fx_rate
            df_total = (
                df[["portfolio", "total_value_fx_usd"]]
                .groupby("portfolio")
                .sum()
                .rename(columns={"total_value_fx_usd": "total_portfolio_fx_usd"})
            )
            df = df[df["underlying_instrument__is_cash"]]
            df = df[["portfolio", "total_value_fx_usd"]].groupby("portfolio").sum()
            if not df.empty:
                df = df[df["total_value_fx_usd"] != 0]
                df = pd.concat([df, df_total, df_name], axis=1).dropna(how="any")
                df["portfolio_weight"] = df.total_value_fx_usd / df.total_portfolio_fx_usd
                return df.reset_index()
        return df

    def get_queryset(self):
        if self.is_portfolio_manager:
            if date_str := self.request.GET.get("date", None):
                val_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            else:
                val_date = date.today()
            active_products = Product.active_objects.filter_active_at_date(val_date)
            return (
                super()
                .get_queryset()
                .annotate(
                    fx_rate=CurrencyFXRates.get_fx_rates_subquery(
                        "date", currency="portfolio__currency", lookup_expr="exact"
                    ),
                    is_product_portfolio=Exists(
                        InstrumentPortfolioThroughModel.objects.filter(
                            portfolio=OuterRef("portfolio"), instrument__in=active_products
                        )
                    ),
                )
                .filter(is_product_portfolio=True)
            )
        return AssetPosition.objects.none()


class CompositionModelPortfolioPandasView(
    UserPortfolioRequestPermissionMixin, InternalUserPermissionMixin, ExportPandasAPIViewSet
):
    IDENTIFIER = "wbportfolio:topdowncomposition"
    filterset_class = CompositionModelPortfolioPandasFilter
    queryset = AssetPosition.objects.all()

    display_config_class = CompositionModelPortfolioPandasDisplayConfig
    title_config_class = CompositionModelPortfolioPandasTitleConfig
    endpoint_config_class = CompositionModelPortfolioPandasEndpointConfig

    @cached_property
    def val_date(self) -> date:
        return parse_date(self.request.GET["date"])

    @cached_property
    def dependant_portfolios(self):
        return Portfolio.objects.filter(
            Q(depends_on__in=[self.portfolio]) | Q(dependent_portfolios__in=[self.portfolio])
        )

    def get_queryset(self):
        if self.has_portfolio_access:
            return super().get_queryset().filter(portfolio=self.portfolio)
        return AssetPosition.objects.none()

    def get_pandas_fields(self, request):
        fields = [
            pf.PKField(key="underlying_instrument", label="ID"),
            pf.CharField(key="underlying_instrument_repr", label="Instrument"),
        ]
        if not self.portfolio.only_weighting:
            fields.append(pf.FloatField(key=f"shares_{self.portfolio.id}", label=str(self.portfolio)))
        fields.append(pf.FloatField(key=f"weighting_{self.portfolio.id}", label=str(self.portfolio), percent=True))

        for portfolio in self.dependant_portfolios:
            if not portfolio.only_weighting:
                fields.append(pf.FloatField(key=f"shares_{portfolio.id}", label=str(portfolio)))
                fields.append(pf.FloatField(key=f"difference_{portfolio.id}", label=str(portfolio)))
            else:
                fields.append(pf.FloatField(key=f"weighting_{portfolio.id}", label=str(portfolio), percent=True))
                fields.append(pf.FloatField(key=f"difference_{portfolio.id}", label=str(portfolio), percent=True))

        return pf.PandasFields(fields=fields)

    search_fields = ["underlying_instrument_repr"]
    ordering_fields = ["underlying_instrument_repr", "model_portfolio"]

    def get_dataframe(self, request, queryset, **kwargs):
        rows = []
        for portfolio in [*self.dependant_portfolios, self.portfolio]:
            rows.extend(
                list(
                    map(
                        lambda x: {
                            "underlying_instrument": x.underlying_instrument.id,
                            "weighting": x.weighting,
                            "shares": x.shares,
                            "portfolio": portfolio.id,
                        },
                        portfolio.get_positions(self.val_date),
                    )
                )
            )
        df = pd.DataFrame(rows, columns=["underlying_instrument", "weighting", "shares", "portfolio"])
        df = df.pivot_table(
            index="underlying_instrument",
            columns=["portfolio"],
            values=["weighting", "shares"],
            aggfunc="sum",
            fill_value=0,
        )
        for portfolio in self.dependant_portfolios:
            with suppress(KeyError):
                if portfolio.only_weighting:
                    df["difference", portfolio.id] = df["weighting"][self.portfolio.id] - df["weighting"][portfolio.id]
                else:
                    df["difference", portfolio.id] = df["shares"][self.portfolio.id] - df["shares"][portfolio.id]

        df.columns = ["_".join([str(item) for item in col]) for col in df.columns.to_flat_index()]
        df = df.reset_index()

        return df

    def manipulate_dataframe(self, df):
        df["underlying_instrument_repr"] = df["underlying_instrument"].map(
            dict(Instrument.objects.filter(id__in=df["underlying_instrument"]).values_list("id", "computed_str"))
        )
        return df
