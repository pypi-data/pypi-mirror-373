from datetime import datetime

import numpy as np
import pandas as pd
from django.db.models import F, OuterRef, Subquery
from rest_framework.exceptions import ParseError
from wbcore.contrib.currency.models import CurrencyFXRates
from wbcore.contrib.io.viewsets import ExportPandasAPIViewSet
from wbcore.pandas import fields as pf
from wbcore.permissions.permissions import InternalUserPermissionMixin
from wbcore.serializers import decorator
from wbcore.utils.strings import format_number
from wbfdm.models import Classification, ClassificationGroup, Instrument

from wbportfolio.filters import (
    AggregatedAssetPositionLiquidityFilter,
    AssetPositionPandasFilter,
)
from wbportfolio.filters.positions import GroupbyChoice
from wbportfolio.models import AssetPosition, Portfolio

from ..constants import EQUITY_TYPE_KEYS
from .configs import (
    AggregatedAssetPositionLiquidityDisplayConfig,
    AggregatedAssetPositionLiquidityEndpointConfig,
    AggregatedAssetPositionLiquidityTitleConfig,
    AssetPositionPandasDisplayConfig,
    AssetPositionPandasEndpointConfig,
    AssetPositionPandasTitleConfig,
)
from .mixins import UserPortfolioRequestPermissionMixin


class AssetPositionPandasView(
    UserPortfolioRequestPermissionMixin, InternalUserPermissionMixin, ExportPandasAPIViewSet
):
    IDENTIFIER = "wbportfolio:equityposition"

    queryset = AssetPosition.objects.all()
    filterset_class = AssetPositionPandasFilter

    pandas_fields = pf.PandasFields(
        fields=(
            pf.PKField(key="id", label="ID"),
            pf.CharField(key="title", label="Title"),
            pf.FloatField(key="performance_total", label="Total Performance", precision=2, percent=True),
            pf.FloatField(key="performance_forex", label="Forex Performance", precision=2, percent=True),
            pf.FloatField(key="contribution_total", label="Total Contribution", precision=2, percent=True),
            pf.FloatField(key="contribution_forex", label="Forex Contribution", precision=2, percent=True),
            pf.FloatField(key="allocation_start", label="Value Start", precision=2, percent=True),
            pf.FloatField(key="allocation_end", label="Value End", precision=2, percent=True),
            # pf.FloatField(key="price_start", label="Price Start", precision=1),
            # pf.FloatField(key="price_end", label="Price End", precision=1),
            pf.FloatField(
                key="total_value_start",
                label="Total Value Start",
                precision=1,
                decorators=(decorator(decorator_type="text", position="left", value="$"),),
            ),
            pf.FloatField(
                key="total_value_end",
                label="Total Value End",
                precision=1,
                decorators=(decorator(decorator_type="text", position="left", value="$"),),
            ),
            pf.FloatField(key="market_share", label="Market Shares", precision=4, percent=True),
        )
    )
    display_config_class = AssetPositionPandasDisplayConfig
    title_config_class = AssetPositionPandasTitleConfig
    endpoint_config_class = AssetPositionPandasEndpointConfig

    search_fields = ["title"]
    ordering_fields = [
        "title",
        "allocation_start",
        "total_value_start",
        "total_value_end",
        "allocation_end",
        "performance_total",
        "contribution_total",
        "performance_forex",
        "contribution_forex",
        "market_share",
    ]

    def get_aggregates(self, request, df):
        if df.empty:
            return {}
        return {
            "allocation_start": {"Σ": format_number(df["allocation_start"].sum())},
            "allocation_end": {"Σ": format_number(df["allocation_end"].sum())},
            "total_value_start": {"Σ": format_number(df["total_value_start"].sum())},
            "total_value_end": {"Σ": format_number(df["total_value_end"].sum())},
            "contribution_total": {"Σ": format_number(df["contribution_total"].sum())},
            "contribution_forex": {"Σ": format_number(df["contribution_forex"].sum())},
        }

    def get_queryset(self):
        if self.is_analyst:
            return (
                super()
                .get_queryset()
                .filter(
                    shares__isnull=False, is_invested=True
                )  # We remove assets position coming from non real portfolio (e.g. index)
                .annotate(
                    currency_fx_rate_usd=CurrencyFXRates.get_fx_rates_subquery(
                        "date", currency="currency", lookup_expr="exact"
                    )
                )
            )
        return AssetPosition.objects.none()

    def get_dataframe(self, request, queryset, **kwargs):
        df = pd.DataFrame()
        if queryset.exists() and (
            primary_classification_group := ClassificationGroup.objects.filter(is_primary=True).first()
        ):
            groupby = GroupbyChoice(request.GET.get("group_by", GroupbyChoice.UNDERLYING_INSTRUMENT))
            groupby_classification_height = int(request.GET.get("groupby_classification_height", "0"))

            groupby_id = GroupbyChoice.get_id(groupby.name)
            if groupby == GroupbyChoice.PRIMARY_CLASSIFICATION:
                queryset = queryset.annotate_classification_for_group(
                    primary_classification_group, classification_height=groupby_classification_height, unique=True
                ).annotate(
                    classification_id=F("classifications"),
                    classification_title=Subquery(
                        Classification.objects.filter(id=OuterRef("classification_id")).values("name")[:1]
                    ),
                )
            elif groupby == GroupbyChoice.PREFERRED_CLASSIFICATION:
                queryset = queryset.annotate_preferred_classification_for_group(
                    primary_classification_group, classification_height=groupby_classification_height
                )
            df = Portfolio.get_contribution_df(
                queryset.values_list("date", "price", "currency_fx_rate_usd", groupby_id, "weighting"),
                need_normalize=True,
            )
            df = df.rename(
                columns={
                    "group_key": "id",
                }
            )
            df["title"] = df["id"].map(groupby.get_repr(df["id"]))
            if groupby == GroupbyChoice.UNDERLYING_INSTRUMENT.value:
                df_market_shares = pd.DataFrame(
                    queryset.values("market_share", "date", "underlying_instrument")
                ).pivot_table(
                    index="underlying_instrument",
                    columns=["date"],
                    values="market_share",
                    fill_value=None,
                    aggfunc="sum",
                )
                df = df.set_index("id")
                df["market_share"] = df_market_shares.iloc[:, -1]
                df = df.reset_index()

        return df

    def manipulate_dataframe(self, df):
        if "titl" in df.columns:
            df["title"] = df["title"].fillna("N/A").astype(str)
        # df[df["title"].isnull()] = "N/A"
        return df.fillna(0)


class AggregatedAssetPositionLiquidityPandasView(InternalUserPermissionMixin, ExportPandasAPIViewSet):
    IDENTIFIER = "wbportfolio:aggregatedassetpositionliquidity"
    LIST_DOCUMENTATION = "wbportfolio/markdown/documentation/aggregate_asset_position_liquidity.md"
    queryset = AssetPosition.objects.all()

    def get_pandas_fields(self, request):
        historic_date = self.request.GET.get("historic_date", None)
        compared_date = self.request.GET.get("compared_date", None)
        fields = [
            pf.PKField(key="id", label="ID"),
            pf.CharField(key="name", label="Name"),
            pf.CharField(
                key="shares_first_date", label=f"Total Shares - {historic_date}" if historic_date else "None"
            ),
            pf.CharField(
                key="volume_50d_first_date", label=f"Mean Volume - {historic_date}" if historic_date else "None"
            ),
            pf.CharField(
                key="liquidity_first_date", label=f"Days To Liquidate - {historic_date}" if historic_date else "None"
            ),
            pf.CharField(
                key="pct_aum_first_date", label=f"Percent AUM - {historic_date}" if historic_date else "None"
            ),
            pf.CharField(
                key="liquidity_second_date", label=f"Days To Liquidate - {compared_date}" if compared_date else "None"
            ),
            pf.CharField(
                key="pct_aum_second_date", label=f"Percent AUM - {compared_date}" if compared_date else "None"
            ),
        ]
        return pf.PandasFields(fields=list(fields))

    title_config_class = AggregatedAssetPositionLiquidityTitleConfig
    endpoint_config_class = AggregatedAssetPositionLiquidityEndpointConfig
    display_config_class = AggregatedAssetPositionLiquidityDisplayConfig

    filterset_class = AggregatedAssetPositionLiquidityFilter

    def get_dataframe(self, request, queryset, **kwargs):
        if "historic_date" not in request.GET or "compared_date" not in request.GET:
            raise ParseError()
        historic_date = datetime.strptime(request.GET["historic_date"], "%Y-%m-%d").date()
        compared_date = datetime.strptime(request.GET["compared_date"], "%Y-%m-%d").date()

        # Take the liquidity query for the two dates.
        qs_assets = queryset.filter(
            underlying_instrument__instrument_type__key__in=EQUITY_TYPE_KEYS,
            date__in=[historic_date, compared_date],
        ).values(
            "date",
            "underlying_instrument",
            "underlying_instrument__name",
            "portfolio",
            "shares",
            "liquidity",
            "volume_50d",
            "total_value_fx_usd",
        )

        if not qs_assets.exists():
            return pd.DataFrame()
        df_assets = pd.DataFrame(qs_assets).set_index(["date", "underlying_instrument", "portfolio"])
        # We aggregate by date and underlying instrument to drop the portfolio level.
        df_assets = df_assets.groupby(["date", "underlying_instrument"]).agg(
            {
                "underlying_instrument__name": "first",
                "shares": "sum",
                "liquidity": "sum",
                "total_value_fx_usd": "sum",
                "volume_50d": "first",
            }
        )
        df_assets = df_assets.reset_index("underlying_instrument").set_index("underlying_instrument", append=True)
        df_assets["pct_aum"] = df_assets.total_value_fx_usd / df_assets.total_value_fx_usd.groupby("date").sum() * 100
        df_assets = df_assets.reindex(columns=["shares", "volume_50d", "liquidity", "pct_aum"]).unstack("date")

        # Make a distinction between first & second date for the columns.
        df_assets.columns = pd.Index(
            [(f"{a}_first_date" if b == historic_date else f"{a}_second_date") for a, b in df_assets.columns]
        )

        # Sort by days to liquidate.
        if "liquidity_first_date" in df_assets.columns:
            df_assets.sort_values(by="liquidity_first_date", ascending=False, inplace=True)
        else:  # if first one does not exist, at least second one exists.
            df_assets.sort_values(by="liquidity_second_date", ascending=False, inplace=True)

        # Cut dataframe for days to liquidate smaller than a specific value.
        if bigger_than_x := request.GET.get("bigger_than_x"):
            if "liquidity_first_date" in df_assets.columns:
                df_assets = df_assets[df_assets["liquidity_first_date"] >= float(bigger_than_x)]
            else:
                df_assets = df_assets[df_assets["liquidity_second_date"] >= float(bigger_than_x)]
        return df_assets

    def manipulate_dataframe(self, df):
        df = df.astype(float).round(2)
        # Make empty columns if they do not exist.
        if df.filter(like="first_date").empty:
            df[["liquidity_first_date", "pct_aum_first_date", "shares_first_date", "volume_50d_first_date"]] = np.nan
        if df.filter(like="second_date").empty:
            df[["liquidity_second_date", "pct_aum_second_date"]] = np.nan

        # Put % for percent columns.
        df.loc[:, df.filter(like="pct_aum").columns] = df.filter(like="pct_aum").applymap(
            lambda x: str(x) + "%" if not np.isnan(x) else None
        )

        # Round big numbers columns and put an apostrophe.
        df.loc[:, ["shares_first_date", "volume_50d_first_date"]] = (
            df.loc[:, ["shares_first_date", "volume_50d_first_date"]]
            .round(0)
            .applymap(lambda x: f"{int(x):,}" if not np.isnan(x) else x)
        )
        df = df.reset_index()
        if not df.empty:
            df["name"] = df["underlying_instrument"].map(
                dict(
                    Instrument.objects.filter(id__in=df["underlying_instrument"].unique()).values_list(
                        "id", "computed_str"
                    )
                )
            )
        return df.rename(columns={"underlying_instrument": "id"})
