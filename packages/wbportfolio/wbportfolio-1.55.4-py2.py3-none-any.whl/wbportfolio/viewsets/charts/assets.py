import datetime as dt
from collections import defaultdict
from contextlib import suppress
from decimal import Decimal

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django.db.models import F, Prefetch
from django.utils.functional import cached_property
from plotly.subplots import make_subplots
from rest_framework.request import Request
from wbcore import viewsets
from wbcore.contrib.currency.models import Currency
from wbcore.contrib.geography.models import Geography
from wbcore.contrib.io.viewsets import ExportPandasAPIViewSet
from wbcore.contrib.pandas import fields as pf
from wbcore.filters import DjangoFilterBackend
from wbcore.utils.date import get_date_interval_from_request
from wbcore.utils.figures import (
    get_default_timeserie_figure,
    get_hovertemplate_timeserie,
)
from wbcore.utils.strings import format_number
from wbfdm.models import (
    Classification,
    ClassificationGroup,
    Instrument,
    InstrumentClassificationThroughModel,
    InstrumentType,
)

from wbportfolio.filters.assets import (
    AssetPositionUnderlyingInstrumentChartFilter,
    CompositionContributionChartFilter,
    ContributionChartFilter,
    DistributionFilter,
)
from wbportfolio.models import (
    AssetPosition,
    AssetPositionGroupBy,
    Portfolio,
    PortfolioRole,
)

from ..configs.buttons.assets import (
    DistributionChartButtonConfig,
    DistributionTableButtonConfig,
)
from ..configs.display.assets import DistributionTableDisplayConfig
from ..configs.endpoints.assets import (
    AssetPositionUnderlyingInstrumentChartEndpointConfig,
    ContributorPortfolioChartEndpointConfig,
    DistributionChartEndpointConfig,
    DistributionTableEndpointConfig,
)
from ..configs.titles.assets import (
    AssetPositionUnderlyingInstrumentChartTitleConfig,
    ContributorPortfolioChartTitleConfig,
    DistributionChartTitleConfig,
    DistributionTableTitleConfig,
)
from ..mixins import UserPortfolioRequestPermissionMixin


class AbstractDistributionMixin(UserPortfolioRequestPermissionMixin):
    queryset = AssetPosition.objects.all()
    filterset_class = DistributionFilter
    filter_backends = (DjangoFilterBackend,)
    request: Request

    @cached_property
    def group_by(self) -> AssetPositionGroupBy:
        try:
            return AssetPositionGroupBy(self.request.GET.get("group_by", "classification"))
        except ValueError:
            return AssetPositionGroupBy.INDUSTRY

    @cached_property
    def val_date(self) -> dt.date:
        if validity_date_repr := self.request.GET.get("date"):
            val_date = dt.datetime.strptime(validity_date_repr, "%Y-%m-%d")
        else:
            val_date = dt.date.today()
        return val_date

    @cached_property
    def classification_group(self):
        try:
            return ClassificationGroup.objects.get(id=self.request.GET.get("group_by_classification_group"))
        except ClassificationGroup.DoesNotExist:
            return ClassificationGroup.objects.get(is_primary=True)

    @cached_property
    def classification_height(self) -> int:
        return int(self.request.GET.get("group_by_classification_height", "0"))

    @cached_property
    def columns_map(self) -> dict:
        if self.group_by == AssetPositionGroupBy.INDUSTRY:
            columns = {}
            level_representations = self.classification_group.get_levels_representation()
            for key, label in zip(
                reversed(self.classification_group.get_fields_names(sep="_")), reversed(level_representations[1:])
            ):
                columns[key] = label
            columns["label"] = "Classification"
            columns["equity"] = "Instrument"
        else:
            columns = {"label": "Label"}
        return columns

    def get_queryset(self):
        profile = self.request.user.profile
        if PortfolioRole.is_analyst(profile, portfolio=self.portfolio) or profile.is_internal:
            return AssetPosition.objects.filter(portfolio=self.portfolio)
        return AssetPosition.objects.none()

    def get_dataframe(self, request, queryset, **kwargs) -> pd.DataFrame:
        instruments = defaultdict(Decimal)
        for asset in self.portfolio.get_positions(self.val_date):
            if self.group_by != AssetPositionGroupBy.INDUSTRY:
                group_field = getattr(asset.underlying_instrument, self.group_by.value)
            else:
                group_field = asset.underlying_instrument.get_root()
            group_field = getattr(group_field, "id", group_field)
            instruments[group_field] += asset.weighting
        df = pd.DataFrame.from_dict(instruments, orient="index", columns=["weighting"])
        if self.group_by == AssetPositionGroupBy.INDUSTRY:
            classifications = InstrumentClassificationThroughModel.objects.filter(
                instrument__in=instruments.keys(), classification__group=self.classification_group
            )
            field_names = {
                field_name.replace("__", "_"): F(f"classification__{field_name}__name")
                for field_name in self.classification_group.get_fields_names()
            }
            classifications = (
                classifications.annotate(**field_names)
                .select_related(
                    *[f"classification__{field_name}" for field_name in self.classification_group.get_fields_names()]
                )
                .prefetch_related(
                    "tags",
                    Prefetch("instrument", queryset=Instrument.objects.filter(classifications_through__isnull=False)),
                )
            )
            df_classification = (
                pd.DataFrame(
                    classifications.values_list("instrument", "classification", *field_names.keys()),
                    columns=["id", "classification", *field_names.keys()],
                )
                .groupby("id")
                .first()
            )
            df = pd.concat([df, df_classification], axis=1)
        if df.weighting.sum():  # normalize
            df.weighting /= df.weighting.sum()
        return df.reset_index(names="id")

    def manipulate_dataframe(self, df):
        if self.group_by == AssetPositionGroupBy.INDUSTRY:
            if not PortfolioRole.is_analyst(self.request.user.profile, portfolio=self.portfolio):
                df["equity"] = ""
            else:
                df["equity"] = df["id"].map(
                    dict(Instrument.objects.filter(id__in=df["id"]).values_list("id", "computed_str"))
                )
            df["label"] = df["classification"].map(
                dict(Classification.objects.filter(id__in=df["classification"].dropna()).values_list("id", "name"))
            )
        elif self.group_by == AssetPositionGroupBy.CASH:
            df.loc[df["id"] == True, "label"] = "Cash"
            df.loc[df["id"] == False, "label"] = "Non-Cash"
        elif self.group_by == AssetPositionGroupBy.COUNTRY:
            df["label"] = df["id"].map(dict(Geography.objects.filter(id__in=df["id"]).values_list("id", "name")))
        elif self.group_by == AssetPositionGroupBy.CURRENCY:
            currencies = dict(map(lambda o: (o.id, str(o)), Currency.objects.filter(id__in=df["id"])))
            df["label"] = df["id"].map(currencies)
        elif self.group_by == AssetPositionGroupBy.INSTRUMENT_TYPE:
            df["label"] = df["id"].map(
                dict(InstrumentType.objects.filter(id__in=df["id"]).values_list("id", "short_name"))
            )
        df.sort_values(by="weighting", ascending=False, inplace=True)
        return df


class DistributionChartViewSet(AbstractDistributionMixin, viewsets.ChartViewSet):
    title_config_class = DistributionChartTitleConfig
    endpoint_config_class = DistributionChartEndpointConfig
    button_config_class = DistributionChartButtonConfig

    @staticmethod
    def pie_chart(df: pd.DataFrame) -> go.Figure:
        fig = go.Figure()
        if not df.empty:
            fig.add_pie(
                labels=df.index,
                values=df.weighting.mul(100),
                marker=dict(colors=px.colors.qualitative.Plotly[: df.shape[0]], line=dict(color="#000000", width=2)),
                hovertemplate="<b>%{label}</b><extra></extra>",
            )
        return fig

    def get_plotly(self, queryset):
        fig = go.Figure()
        df = self.manipulate_dataframe(self.get_dataframe(self.request, queryset))
        df = df.dropna(how="any")
        if not df.empty:
            levels = list(self.columns_map.keys())
            fig = px.sunburst(
                df,
                path=levels,
                values="weighting",
                hover_data={"weighting": ":.2%"},
            )
        fig.update_traces(hovertemplate="<b>%{label}</b><br>Weight = %{customdata:.3p}")
        return fig


class DistributionTableViewSet(AbstractDistributionMixin, ExportPandasAPIViewSet):
    endpoint_config_class = DistributionTableEndpointConfig
    display_config_class = DistributionTableDisplayConfig
    title_config_class = DistributionTableTitleConfig
    button_config_class = DistributionTableButtonConfig

    def get_pandas_fields(self, request):
        fields = [
            pf.PKField(key="id", label="id"),
            pf.FloatField(key="weighting", label="Weight", precision=2, percent=True),
        ]
        for key, label in self.columns_map.items():
            fields.append(pf.CharField(key=key, label=label))
        return pf.PandasFields(fields=fields)

    def get_aggregates(self, request, df):
        return {"weighting": {"Σ": format_number(df["weighting"].sum())}}


# ##### CHART VIEWS #####


class ContributorPortfolioChartView(UserPortfolioRequestPermissionMixin, viewsets.ChartViewSet):
    filterset_class = ContributionChartFilter
    filter_backends = (DjangoFilterBackend,)
    IDENTIFIER = "wbportfolio:portfolio-contributor"
    queryset = AssetPosition.objects.all()

    title_config_class = ContributorPortfolioChartTitleConfig
    endpoint_config_class = ContributorPortfolioChartEndpointConfig

    ROW_HEIGHT: int = 20

    @property
    def min_height(self):
        if hasattr(self, "nb_rows"):
            return self.nb_rows * self.ROW_HEIGHT
        return "300px"

    @cached_property
    def hedged_currency(self) -> Currency | None:
        if "hedged_currency" in self.request.GET:
            with suppress(Currency.DoesNotExist):
                return Currency.objects.get(pk=self.request.GET["hedged_currency"])

    @cached_property
    def show_lookthrough(self) -> bool:
        return self.portfolio.is_composition and self.request.GET.get("show_lookthrough", "false").lower() == "true"

    def get_filterset_class(self, request):
        if self.portfolio.is_composition:
            return CompositionContributionChartFilter
        return ContributionChartFilter

    def get_plotly(self, queryset):
        fig = go.Figure()
        data = []
        if self.show_lookthrough:
            d1, d2 = get_date_interval_from_request(self.request)
            for _d in pd.date_range(d1, d2):
                for pos in self.portfolio.get_lookthrough_positions(_d.date()):
                    data.append(
                        [
                            pos.date,
                            pos.initial_price,
                            pos.initial_currency_fx_rate,
                            pos.underlying_instrument_id,
                            pos.weighting,
                        ]
                    )
        else:
            data = queryset.annotate_hedged_currency_fx_rate(self.hedged_currency).values_list(
                "date", "price", "hedged_currency_fx_rate", "underlying_instrument", "weighting"
            )
        df = Portfolio.get_contribution_df(data).rename(columns={"group_key": "underlying_instrument"})
        if not df.empty:
            df = df[["contribution_total", "contribution_forex", "underlying_instrument"]].sort_values(
                by="contribution_total", ascending=True
            )

            df["instrument_id"] = df.underlying_instrument.map(
                dict(Instrument.objects.filter(id__in=df["underlying_instrument"]).values_list("id", "name_repr"))
            )
            df_forex = df[["instrument_id", "contribution_forex"]]
            df_forex = df_forex[df_forex.contribution_forex != 0]

            contribution_equity = df.contribution_total - df.contribution_forex

            text_forex = df_forex.contribution_forex.apply(lambda x: f"{x:,.2%}")
            text_equity = contribution_equity.apply(lambda x: f"{x:,.2%}")
            setattr(self, "nb_rows", df.shape[0])
            fig.add_trace(
                go.Bar(
                    y=df.instrument_id,
                    x=contribution_equity,
                    name="Contribution Equity",
                    orientation="h",
                    marker=dict(
                        color="rgba(247,110,91,0.6)",
                        line=dict(color="rgb(247,110,91,1.0)", width=2),
                    ),
                    text=text_equity.values,
                    textposition="auto",
                )
            )
            fig.add_trace(
                go.Bar(
                    y=df_forex.instrument_id,
                    x=df_forex.contribution_forex,
                    name="Contribution Forex",
                    orientation="h",
                    marker=dict(
                        color="rgba(58, 71, 80, 0.6)",
                        line=dict(color="rgba(58, 71, 80, 1.0)", width=2),
                    ),
                    text=text_forex.values,
                    textposition="outside",
                )
            )
            fig.update_layout(
                barmode="relative",
                xaxis=dict(showgrid=False, showline=False, zeroline=False, tickformat=".2%"),
                yaxis=dict(showgrid=False, showline=False, zeroline=False, tickmode="linear"),
                margin=dict(b=0, r=20, l=20, t=0, pad=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="roboto", size=12, color="black"),
                bargap=0.3,
            )
            # fig = get_horizontal_barplot(df, x_label="contribution_total", y_label="name")
        return fig

    def parse_figure_dict(self, figure_dict: dict[str, any]) -> dict[str, any]:
        figure_dict = super().parse_figure_dict(figure_dict)
        figure_dict["style"]["minHeight"] = self.min_height
        return figure_dict

    def get_queryset(self):
        if self.has_portfolio_access:
            return super().get_queryset().filter(portfolio=self.portfolio)
        return AssetPosition.objects.none()


class AssetPositionUnderlyingInstrumentChartViewSet(UserPortfolioRequestPermissionMixin, viewsets.ChartViewSet):
    IDENTIFIER = "wbportfolio:assetpositionchart"

    queryset = AssetPosition.objects.all()

    title_config_class = AssetPositionUnderlyingInstrumentChartTitleConfig
    endpoint_config_class = AssetPositionUnderlyingInstrumentChartEndpointConfig
    filterset_class = AssetPositionUnderlyingInstrumentChartFilter

    def get_queryset(self):
        return AssetPosition.objects.filter(underlying_quote__in=self.instrument.get_descendants(include_self=True))

    def get_plotly(self, queryset):
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig = get_default_timeserie_figure(fig)
        if queryset.exists():
            df_weight = pd.DataFrame(queryset.values("date", "weighting", "portfolio__name"))
            df_weight = df_weight.where(pd.notnull(df_weight), 0)
            df_weight = df_weight.groupby(["date", "portfolio__name"]).sum().reset_index()
            min_date = df_weight["date"].min()
            max_date = df_weight["date"].max()

            df_price = (
                pd.DataFrame(
                    self.instrument.prices.filter_only_valid_prices()
                    .annotate_base_data()
                    .filter(date__gte=min_date, date__lte=max_date)
                    .values_list("date", "net_value_usd"),
                    columns=["date", "price_fx_usd"],
                )
                .set_index("date")
                .sort_index()
            )

            fig.add_trace(
                go.Scatter(
                    x=df_price.index, y=df_price.price_fx_usd, mode="lines", marker_color="green", name="Price"
                ),
                secondary_y=False,
            )

            df_weight = pd.DataFrame(queryset.values("date", "weighting", "portfolio__name"))
            df_weight = df_weight.where(pd.notnull(df_weight), 0)
            df_weight = df_weight.groupby(["date", "portfolio__name"]).sum().reset_index()
            for portfolio_name, df_tmp in df_weight.groupby("portfolio__name"):
                fig.add_trace(
                    go.Scatter(
                        x=df_tmp.date,
                        y=df_tmp.weighting,
                        hovertemplate=get_hovertemplate_timeserie(is_percent=True),
                        mode="lines",
                        name=f"Allocation: {portfolio_name}",
                    ),
                    secondary_y=True,
                )

            # Set x-axis title
            fig.update_xaxes(title_text="Date")
            # Set y-axes titles
            fig.update_yaxes(
                title_text="<b>Price</b>",
                secondary_y=False,
                titlefont=dict(color="green"),
                tickfont=dict(color="green"),
            )
            fig.update_yaxes(
                title_text="<b>Portfolio Allocation (%)</b>",
                secondary_y=True,
                titlefont=dict(color="blue"),
                tickfont=dict(color="blue"),
            )

        return fig
