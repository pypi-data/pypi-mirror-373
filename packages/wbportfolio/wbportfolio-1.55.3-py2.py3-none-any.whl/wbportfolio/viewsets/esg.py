from contextlib import suppress
from datetime import date, datetime

import pandas as pd
from django.contrib.messages import warning
from django.db.models import Q
from django.utils.functional import cached_property
from wbcore.contrib.io.viewsets import ExportPandasAPIViewSet
from wbcore.pandas import fields as pf
from wbcore.utils.strings import format_number
from wbfdm.analysis.esg.enums import AggregationMethod, ESGAggregation
from wbfdm.analysis.esg.esg_analysis import DataLoader
from wbfdm.models import Instrument

from wbportfolio.filters import ESGMetricAggregationPortfolioPandasFilterSet
from wbportfolio.models import AssetPosition
from wbportfolio.viewsets.configs import (
    ESGMetricAggregationPortfolioPandasDisplayConfig,
    ESGMetricAggregationPortfolioPandasEndpointConfig,
    ESGMetricAggregationPortfolioPandasTitleConfig,
)

from .mixins import UserPortfolioRequestPermissionMixin


class ESGMetricAggregationPortfolioPandasViewSet(UserPortfolioRequestPermissionMixin, ExportPandasAPIViewSet):
    IDENTIFIER = "wbportfolio:esgmetricportfolio"
    filterset_class = ESGMetricAggregationPortfolioPandasFilterSet
    queryset = AssetPosition.objects.all()

    display_config_class = ESGMetricAggregationPortfolioPandasDisplayConfig
    title_config_class = ESGMetricAggregationPortfolioPandasTitleConfig
    endpoint_config_class = ESGMetricAggregationPortfolioPandasEndpointConfig

    search_fields = ["underlying_instrument_repr"]

    @cached_property
    def val_date(self) -> date:
        if validity_date_repr := self.request.GET.get("date"):
            val_date = datetime.strptime(validity_date_repr, "%Y-%m-%d")
        else:
            val_date = date.today()

        qs = AssetPosition.objects.filter(portfolio=self.portfolio, date__lte=val_date)
        if qs.exists():
            return qs.latest("date").date
        else:
            warning(
                self.request,
                f"No position were found before the {val_date:%Y-%m-%d}. Please select another date",
            )
            return val_date

    @cached_property
    def base_df(self) -> pd.DataFrame:
        if self.action != "metadata":
            with suppress(KeyError):
                df = (
                    pd.DataFrame(
                        AssetPosition.objects.filter(portfolio=self.portfolio, date=self.val_date)
                        .exclude(
                            Q(underlying_instrument__is_cash=True) | Q(underlying_instrument__is_cash_equivalent=True)
                        )
                        .values("underlying_instrument", "weighting", "total_value_fx_usd")
                    )
                    .groupby("underlying_instrument")
                    .sum()
                    .astype(float)
                )
                df["weighting"] = df["weighting"] / df["weighting"].sum()
                return df
        return pd.DataFrame(columns=["weighting", "total_value_fx_usd"])

    @cached_property
    def esg_aggregation(self) -> ESGAggregation | None:
        return ESGAggregation[self.request.GET.get("esg_aggregation", ESGAggregation.GHG_EMISSIONS_SCOPE_1.name)]

    @cached_property
    def esg_data(self) -> pd.Series:
        if self.action != "metadata":
            return self.esg_aggregation.get_esg_data(Instrument.objects.filter(id__in=self.base_df.index))
        return pd.Series(dtype="float64")

    @cached_property
    def dataloader(self) -> DataLoader:
        dataloader = DataLoader(
            self.base_df["weighting"],
            self.esg_data,
            self.val_date,
            total_value_fx_usd=self.base_df["total_value_fx_usd"],
        )
        self.metric = dataloader.compute(self.esg_aggregation).rename("metric")
        return dataloader

    @cached_property
    def metric_columns(self) -> list[str]:
        return (
            ["weighting", "total_value_fx_usd", "esg_data", "weights_in_coverage", "metric"]
            + list(map(lambda x: x.series.name, self.dataloader.extra_esg_data_logs))
            + list(map(lambda x: x.series.name, self.dataloader.intermediary_logs))
        )

    def get_pandas_fields(self, request):
        fields = [
            pf.PKField(key="underlying_instrument", label="ID"),
            pf.CharField(key="underlying_instrument_repr", label="Instrument"),
            pf.FloatField(key="weighting", label="Weight", percent=True),
            pf.FloatField(key="total_value_fx_usd", label="Total Asset (USD)"),
            pf.FloatField(key="esg_data", label="ESG Data", precision=4),
            pf.FloatField(key="weights_in_coverage", label="Weights in Coverage", percent=True),
        ]
        for extra_esg_data_log in self.dataloader.extra_esg_data_logs:
            fields.append(
                pf.FloatField(
                    key=extra_esg_data_log.series.name,
                    label=extra_esg_data_log.label,
                    percent=extra_esg_data_log.is_percent,
                    precision=extra_esg_data_log.precision,
                )
            )
        for intermediary_log in self.dataloader.intermediary_logs:
            fields.append(
                pf.FloatField(
                    key=intermediary_log.series.name,
                    label=intermediary_log.label,
                    percent=intermediary_log.is_percent,
                    precision=intermediary_log.precision,
                )
            )
        if self.esg_aggregation.get_aggregation() == AggregationMethod.PERCENTAGE_SUM:
            fields.append(pf.FloatField(key="metric", label="Metric", percent=True))
        else:
            fields.append(pf.FloatField(key="metric", label="Metric", precision=4))
        return pf.PandasFields(fields=fields)

    def get_dataframe(self, request, queryset, **kwargs):
        dataloader = self.dataloader
        df = pd.concat(
            [
                self.base_df["weighting"],
                self.base_df["total_value_fx_usd"],
                self.esg_data.rename("esg_data"),
                *map(lambda x: x.series, dataloader.extra_esg_data_logs),
                dataloader.weights_in_coverage.rename("weights_in_coverage"),
                *map(lambda x: x.series, dataloader.intermediary_logs),
                self.metric,
            ],
            axis=1,
        )
        return df

    def manipulate_dataframe(self, df):
        df["underlying_instrument_repr"] = df.index.map(
            dict(self.dataloader.instruments.values_list("id", "computed_str"))
        )
        return df.reset_index()

    def get_aggregates(self, request, df):
        aggregates = {}
        for column in self.metric_columns:
            with suppress(TypeError, KeyError):  # silent aggregation on str type
                aggregates[column] = {"Σ": format_number(df[column].sum(), decimal=4)}
        return aggregates

    def get_ordering_fields(self) -> list[str]:
        return ["underlying_instrument_repr"] + self.metric_columns
