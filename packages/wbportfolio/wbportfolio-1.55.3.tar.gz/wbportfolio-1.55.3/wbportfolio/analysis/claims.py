from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from django.db import connection
from django.db.models import DateField, DecimalField, ExpressionWrapper, F, OuterRef, Subquery
from django.db.models.functions import Greatest
from django.template.loader import get_template
from jinjasql import JinjaSql
from wbcore.contrib.currency.models import CurrencyFXRates
from wbcore.contrib.dataloader.utils import dictfetchall
from wbcrm.models import Account
from wbfdm.models import ClassificationGroup
from wbfdm.models.instruments import Classification, InstrumentPrice

from wbportfolio.models.products import Product

if TYPE_CHECKING:
    from datetime import date
    from typing import Iterable


def get_assets_and_net_new_money_progression(
    from_date: "date", to_date: "date", product_id: int | None = None, account_tree_id: int | None = None
) -> "Iterable[dict]":
    template = get_template("wbportfolio/sql/aum_nnm.sql", using="jinja").template
    query, params = JinjaSql(param_style="format").prepare_query(
        template,
        {
            "from_date": from_date.strftime("%Y-%m-%d"),
            "to_date": to_date.strftime("%Y-%m-%d"),
            "product_id": product_id,
            "account_tree_id": account_tree_id,
        },
    )

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        yield from dictfetchall(cursor)


class ConsolidatedTradeSummary:
    def __init__(
        self,
        queryset,
        start_date: "date",
        end_date: "date",
        pivot: str,
        pivot_label: str,
        classification_group: ClassificationGroup | None = None,
        classification_height: int = 0,
        date_label: str = "date_considered",
    ):
        self.queryset = queryset.filter(trade__isnull=False, status="APPROVED")
        self.start_date = start_date
        self.end_date = end_date
        self.pivot = pivot
        self.pivot_label = pivot_label
        self.queryset = self.queryset.annotate(
            internal_trade=F("trade__marked_as_internal"),
            date_considered=ExpressionWrapper(
                Greatest("trade__transaction_date", "date") + 1, output_field=DateField()
            ),
            net_value=InstrumentPrice.subquery_closest_value(
                "net_value", date_name="date_considered", instrument_pk_name="product__pk", date_lookup="exact"
            ),
            fx_rate=CurrencyFXRates.get_fx_rates_subquery("date_considered", lookup_expr="exact"),
            aum=ExpressionWrapper(F("fx_rate") * F("net_value") * F("shares"), output_field=DecimalField()),
        )
        self.queryset = Account.annotate_root_account_info(self.queryset)

        if classification_group:
            self.queryset = classification_group.annotate_queryset(self.queryset, classification_height, "product")

        self.queryset = self.queryset.select_related(
            "product",
            "account",
            "product__parent",
        )
        self.df = self._prepare_df(date_label)

    def _prepare_df(self, date_label: str) -> pd.DataFrame:
        columns = ["shares", date_label, "product__id", "aum", "internal_trade"]
        if self.pivot == "classification_id":
            columns.append("classifications")
        else:
            columns.append(self.pivot)
            columns.append(self.pivot_label)

        df = pd.DataFrame(self.queryset.values_list(*columns), columns=columns).rename(columns={date_label: "date"})
        if self.pivot == "classification_id":
            df = (
                df.explode("classifications")
                .rename(columns={"classifications": "classification_id"})
                .replace([np.inf, -np.inf, np.nan], None)
            )
            df["classification_title"] = df.classification_id.map(
                dict(Classification.objects.filter(id__in=df.classification_id.unique()).values_list("id", "name")),
                na_action="ignore",
            )
        df_product = pd.DataFrame(
            Product.objects.annotate(
                net_value_date_start=Subquery(
                    InstrumentPrice.objects.filter(
                        instrument=OuterRef("pk"), calculated=False, date__lte=self.start_date
                    )
                    .order_by("-date")
                    .values("date")[:1]
                ),
                net_value_date_end=Subquery(
                    InstrumentPrice.objects.filter(
                        instrument=OuterRef("pk"), calculated=False, date__lte=self.end_date
                    )
                    .order_by("-date")
                    .values("date")[:1]
                ),
                net_value_start=InstrumentPrice.subquery_closest_value(
                    "net_value",
                    date_name="net_value_date_start",
                    instrument_pk_name="pk",
                    date_lookup="exact",
                    # we get all net value (even estimated) to avoir showing None price on holiday
                ),
                fx_rate_start=CurrencyFXRates.get_fx_rates_subquery(
                    "net_value_date_start", currency="currency", lookup_expr="exact"
                ),
                price_start=ExpressionWrapper(F("net_value_start") * F("fx_rate_start"), output_field=DecimalField()),
                net_value_end=InstrumentPrice.subquery_closest_value(
                    "net_value",
                    date_name="net_value_date_end",
                    instrument_pk_name="pk",
                    date_lookup="exact",
                    # we get all net value (even estimated) to avoir showing None price on holiday
                ),
                fx_rate_end=CurrencyFXRates.get_fx_rates_subquery(
                    "net_value_date_end", currency="currency", lookup_expr="exact"
                ),
                price_end=ExpressionWrapper(F("net_value_end") * F("fx_rate_end"), output_field=DecimalField()),
            ).values("price_start", "price_end", "id"),
            columns=["price_start", "price_end", "id"],
        ).rename(columns={"id": "product__id"})

        df = df.merge(df_product, on="product__id")

        df = df.rename(columns={self.pivot: "id", self.pivot_label: "title"})
        df.loc[df["id"].isnull(), "id"] = -1
        df.loc[df["id"] == -1, "title"] = "N/A"
        df = df.dropna(subset=["id"])
        df[df.columns.difference(["title", "id", "date", "product__id", "internal_trade"])] = df[
            df.columns.difference(["title", "id", "date", "product__id", "internal_trade"])
        ].astype("float")
        return df[df["date"] < self.end_date]

    def get_aum_df(self) -> pd.DataFrame:
        df = self.df.copy().drop(columns=["internal_trade"])
        df.loc[df.date <= self.start_date, "sum_shares_start"] = df.shares
        df.loc[df.date < self.end_date, "sum_shares_end"] = df.shares
        df = df.fillna(0)
        # Prepare dataframe
        df["sum_aum_start"] = df.sum_shares_start * df.price_start
        df["sum_aum_end"] = df.sum_shares_end * df.price_end

        # Sanitize dataframe
        df = df.drop(
            columns=df.columns.difference(["id", "sum_shares_start", "sum_shares_end", "sum_aum_start", "sum_aum_end"])
        )
        df = df.groupby("id").agg(
            {
                "sum_shares_start": "sum",
                "sum_shares_end": "sum",
                "sum_aum_start": "sum",
                "sum_aum_end": "sum",
            }
        )
        df = df.round()
        # Compute statistics
        df["sum_shares_diff"] = df.sum_shares_end - df.sum_shares_start
        df["sum_shares_perf"] = df.sum_shares_end / df.sum_shares_start - 1
        df["sum_aum_diff"] = df.sum_aum_end - df.sum_aum_start
        df["sum_aum_perf"] = df.sum_aum_end / df.sum_aum_start - 1
        return df

    def get_nnm_df(
        self, only_positive: bool = False, only_negative: bool = False, filter_internal_trade: bool = True
    ) -> pd.DataFrame:
        df = self.df.copy()
        if filter_internal_trade:
            df = df[~df["internal_trade"]].drop(columns=["internal_trade"])
        if only_positive:
            df.loc[df["aum"] < 0, "aum"] = 0
        elif only_negative:
            df.loc[df["aum"] > 0, "aum"] = 0
        df = df[((df["date"] > self.start_date) & (df["date"] <= self.end_date))]
        df["date"] = pd.to_datetime(df["date"])
        df["period"] = "sum_nnm_" + df.date.dt.year.astype(str) + "-" + df.date.dt.month.map("{:02}".format)
        df = df[["id", "period", "aum"]].groupby(["id", "period"]).sum().reset_index()
        df = pd.pivot_table(df, values="aum", index="id", columns=["period"])
        df["sum_nnm_total"] = df.sum(axis=1)
        df = df.round().fillna(0).reindex(self.df["id"].unique(), fill_value=0)
        return df

    def get_aum_sparkline(self) -> pd.DataFrame:
        df = self.df[self.df["date"] >= self.start_date].copy()
        df["aum_sparkline"] = None
        if not df.empty:
            df["aum_sparkline"] = df["aum"]
            df = df[["product__id", "id", "date", "aum_sparkline"]].groupby(["product__id", "id", "date"]).sum()
            df = df.reindex(
                pd.MultiIndex.from_product(
                    [
                        df.index.levels[0],
                        df.index.levels[1],
                        pd.date_range(df.index.levels[2].min(), df.index.levels[2].max()),
                    ],  # we downsample to make the chart easier on the frontend
                    names=["product__id", "id", "date"],
                ),
                fill_value=0,
            )
            df["aum_sparkline"] = df.groupby(level=["product__id", "id"])["aum_sparkline"].cumsum()
            df = df.groupby(level=[1, 2]).sum()
            df = df.reindex(
                pd.MultiIndex.from_product(
                    [
                        df.index.levels[0],
                        pd.date_range(df.index.levels[1].min(), df.index.levels[1].max(), freq="W-MON"),
                    ],  # we downsample to make the chart easier on the frontend
                    names=["id", "date"],
                ),
                fill_value=0,
            )
            df = df.reset_index(level=1)[["date", "aum_sparkline"]].apply(tuple, axis=1).rename("aum_sparkline")
            return df.groupby("id").apply(list)
        return pd.DataFrame()

    def get_initial_investment_date_df(self) -> pd.DataFrame:
        return (
            self.df[["date", "id"]]
            .sort_values(by="date")
            .groupby("id")
            .first()
            .rename(columns={"date": "initial_investment_date"})
        )
