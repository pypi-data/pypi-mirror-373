from contextlib import suppress
from datetime import date, datetime

import pandas as pd
from django.db.models import OuterRef, Q, Subquery, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from django.utils.functional import cached_property
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.reverse import reverse
from wbcore import viewsets
from wbcore.contrib.currency.models import Currency
from wbcore.contrib.io.viewsets import ExportPandasAPIViewSet
from wbcore.pandas import fields as pf
from wbcore.permissions.permissions import InternalUserPermissionMixin
from wbfdm.models import Instrument

from wbportfolio.filters import PortfolioFilterSet, PortfolioTreeGraphChartFilterSet
from wbportfolio.models import (
    AssetPosition,
    OrderProposal,
    Portfolio,
    PortfolioPortfolioThroughModel,
    Rebalancer,
    RebalancingModel,
)
from wbportfolio.models.portfolio import compute_lookthrough_as_task
from wbportfolio.serializers import (
    PortfolioModelSerializer,
    PortfolioPortfolioThroughModelSerializer,
    PortfolioRepresentationSerializer,
)

from ..models.graphs.portfolio import PortfolioGraph
from .configs import (
    PortfolioButtonConfig,
    PortfolioDisplayConfig,
    PortfolioEndpointConfig,
    PortfolioPortfolioThroughModelDisplayConfig,
    PortfolioPortfolioThroughModelEndpointConfig,
    PortfolioPreviewConfig,
    PortfolioTitleConfig,
    PortfolioTreeGraphChartEndpointConfig,
    PortfolioTreeGraphChartTitleConfig,
    TopDownPortfolioCompositionPandasDisplayConfig,
    TopDownPortfolioCompositionPandasEndpointConfig,
    TopDownPortfolioCompositionPandasTitleConfig,
)
from .mixins import UserPortfolioRequestPermissionMixin


class PortfolioRepresentationViewSet(InternalUserPermissionMixin, viewsets.RepresentationViewSet):
    IDENTIFIER = "wbportfolio:portfolio"

    ordering_fields = ordering = search_fields = ("name",)
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioRepresentationSerializer
    filterset_class = PortfolioFilterSet


class PortfolioModelViewSet(UserPortfolioRequestPermissionMixin, InternalUserPermissionMixin, viewsets.ModelViewSet):
    filterset_class = PortfolioFilterSet
    serializer_class = PortfolioModelSerializer
    queryset = Portfolio.objects.all()

    search_fields = ("currency__key", "name")
    ordering_fields = (
        "name",
        "currency",
        "hedged_currency",
        "updated_at",
        "initial_position_date",
        "last_position_date",
        "last_asset_under_management_usd",
        "last_positions",
        "automatic_rebalancer",
        "last_order_proposal_date",
        "is_manageable",
        "is_tracked",
        "only_weighting",
        "is_lookthrough",
        "is_composition",
    )
    ordering = ["name"]

    display_config_class = PortfolioDisplayConfig
    button_config_class = PortfolioButtonConfig
    title_config_class = PortfolioTitleConfig
    endpoint_config_class = PortfolioEndpointConfig
    preview_config_class = PortfolioPreviewConfig

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("currency", "hedged_currency")
            .prefetch_related("depends_on", "instruments")
            .annotate(
                last_asset_under_management_usd=Subquery(
                    AssetPosition.objects.filter(portfolio=OuterRef("pk"), date=OuterRef("last_position_date"))
                    .values("portfolio")
                    .annotate(s=Sum("total_value_fx_usd"))
                    .values("s")[:1]
                ),
                last_positions=Subquery(
                    AssetPosition.objects.filter(portfolio=OuterRef("pk"), date=OuterRef("last_position_date"))
                    .values("portfolio")
                    .annotate(s=Sum("shares"))
                    .values("s")[:1]
                ),
                last_order_proposal_date=Subquery(
                    OrderProposal.objects.filter(portfolio=OuterRef("pk"))
                    .order_by("-trade_date")
                    .values("trade_date")[:1]
                ),
            )
        )

    @action(detail=True, methods=["POST"])
    def rebalance(self, request, pk=None):
        if date_str := request.POST.get("trade_date", None):
            trade_date = datetime.strptime(date_str, "%Y-%m-%d")
            order_proposal, _ = OrderProposal.objects.get_or_create(portfolio_id=pk, trade_date=trade_date)
            order_proposal.reset_orders()
            return Response(
                {"endpoint": reverse("wbportfolio:orderproposal-detail", args=[order_proposal.id], request=request)}
            )
        raise HttpResponse("Bad Request", status=400)

    @action(detail=False, methods=["POST"])
    def createmodelportfolio(self, request, pk=None):
        if self.is_portfolio_manager:
            name = request.POST["name"]
            currency_id = request.POST["currency"]
            currency = Currency.objects.get(id=currency_id)
            index_parameters = {}
            Portfolio.create_model_portfolio(name, currency, index_parameters=index_parameters)
            return Response({"send": True})
        raise HttpResponse("Unauthorized", status=403)

    @action(detail=True, methods=["POST"])
    def attachrebalancer(self, request, pk=None):
        try:
            activation_date = datetime.strptime(request.POST["activation_date"], "%Y-%m-%d")
            rebalancing_model = get_object_or_404(RebalancingModel, pk=request.POST["rebalancing_model"])
            frequency = request.POST["frequency"]
            apply_order_proposal_automatically = (
                request.POST.get("apply_order_proposal_automatically", "false") == "true"
            )

            rebalancer, _ = Rebalancer.objects.update_or_create(
                portfolio=self.get_object(),
                defaults={
                    "rebalancing_model": rebalancing_model,
                    "frequency": frequency,
                    "activation_date": activation_date,
                    "apply_order_proposal_automatically": apply_order_proposal_automatically,
                },
            )
            return Response(
                {"endpoint": reverse("wbportfolio:rebalancer-detail", args=[rebalancer.id], request=request)}
            )
        except KeyError:
            return HttpResponse("Bad arguments", status=400)

    @action(detail=True, methods=["POST"], permission_classes=[IsAdminUser])
    def recomputelookthrough(self, request, pk=None):
        portfolio = self.get_object()
        if portfolio.is_lookthrough:
            with suppress(KeyError):
                start = datetime.strptime(request.POST["start"], "%Y-%m-%d")
                end = datetime.strptime(request.POST["end"], "%Y-%m-%d")
                compute_lookthrough_as_task.delay(portfolio.id, start, end)
            return HttpResponse("Ok", status=200)

        return HttpResponse("Bad arguments", status=400)


class PortfolioPortfolioThroughModelViewSet(InternalUserPermissionMixin, viewsets.ModelViewSet):
    serializer_class = PortfolioPortfolioThroughModelSerializer
    queryset = PortfolioPortfolioThroughModel.objects.all()

    search_fields = ["dependency_portfolio__name"]

    display_config_class = PortfolioPortfolioThroughModelDisplayConfig
    endpoint_config_class = PortfolioPortfolioThroughModelEndpointConfig

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(Q(portfolio=self.kwargs["portfolio_id"]) | Q(dependency_portfolio=self.kwargs["portfolio_id"]))
        )


class PortfolioTreeGraphChartViewSet(UserPortfolioRequestPermissionMixin, viewsets.HTMLViewSet):
    filterset_class = PortfolioTreeGraphChartFilterSet
    IDENTIFIER = "wbportfolio:portfolio-treegraphchart"
    queryset = Portfolio.objects.all()

    title_config_class = PortfolioTreeGraphChartTitleConfig
    endpoint_config_class = PortfolioTreeGraphChartEndpointConfig

    def get_queryset(self):
        return super().get_queryset().filter(id=self.kwargs["portfolio_id"])

    @cached_property
    def val_date(self) -> date:
        return parse_date(self.request.GET["date"])

    def get_html(self, queryset) -> str:
        portfolio_graph = PortfolioGraph(self.portfolio, self.val_date, rankdir="LR", size="20,11")
        return portfolio_graph.to_svg()


class TopDownPortfolioCompositionPandasAPIView(UserPortfolioRequestPermissionMixin, ExportPandasAPIViewSet):
    IDENTIFIER = "wbportfolio:topdowncomposition"
    queryset = Portfolio.objects.all()

    display_config_class = TopDownPortfolioCompositionPandasDisplayConfig
    title_config_class = TopDownPortfolioCompositionPandasTitleConfig
    endpoint_config_class = TopDownPortfolioCompositionPandasEndpointConfig

    pandas_fields = pf.PandasFields(
        fields=[
            pf.PKField(key="id", label="ID"),
            pf.IntegerField(key="_group_key", label="Group Key"),
            pf.IntegerField(key="parent_row_id", label="Parent Row"),
            pf.CharField(key="instrument", label="Instrument"),
            pf.FloatField(key="effective_weights", label="Effective Weights", precision=2, percent=True),
            pf.FloatField(key="rebalancing_weights", label="Rebalancing Weights", precision=2, percent=True),
        ]
    )

    @cached_property
    def composition_portfolio(self) -> Portfolio | None:
        return self.portfolio.composition_portfolio or self.portfolio

    @cached_property
    def last_rebalancing_date(self) -> date | None:
        if self.composition_portfolio and self.last_effective_date:
            with suppress(OrderProposal.DoesNotExist):
                return (
                    self.composition_portfolio.order_proposals.filter(trade_date__lte=self.last_effective_date)
                    .latest("trade_date")
                    .trade_date
                )

    @cached_property
    def last_effective_date(self) -> date | None:
        if self.composition_portfolio:
            with suppress(AssetPosition.DoesNotExist):
                return self.composition_portfolio.assets.latest("date").date

    def get_dataframe(self, request, queryset, **kwargs):
        df = pd.DataFrame(columns=["id", "parent_row_id", "instrument", "effective_weights", "rebalancing_weights"])

        def _get_parent_instrument_id(portfolio):
            with suppress(AttributeError):
                return str(portfolio.instruments.first().id)

        if (
            self.has_portfolio_access
            and self.composition_portfolio
            and self.last_rebalancing_date
            and self.last_effective_date
        ):
            df = pd.DataFrame(
                map(
                    lambda x: {
                        "instrument": str(x.underlying_instrument.id),
                        "path": "-".join(
                            map(
                                lambda o: _get_parent_instrument_id(o),
                                getattr(x, "path", [self.composition_portfolio]),
                            )
                        ),
                        "effective_weights": x.weighting,
                    },
                    self.composition_portfolio.get_positions(
                        self.last_effective_date, with_intermediary_position=True
                    ),
                ),
                columns=["instrument", "path", "effective_weights"],
            ).set_index(["path", "instrument"])

            if last_rebalancing_date := self.last_rebalancing_date:
                tree_positions_rebalancing_date_df = pd.DataFrame(
                    map(
                        lambda x: {
                            "instrument": str(x.underlying_instrument.id),
                            "path": "-".join(
                                map(
                                    lambda o: _get_parent_instrument_id(o),
                                    getattr(x, "path", [self.composition_portfolio]),
                                )
                            ),
                            "rebalancing_weights": x.weighting,
                        },
                        self.composition_portfolio.get_positions(
                            last_rebalancing_date, with_intermediary_position=True
                        ),
                    ),
                    columns=["instrument", "path", "rebalancing_weights"],
                ).set_index(["path", "instrument"])

                df = pd.concat([df, tree_positions_rebalancing_date_df], axis=1)
            df = df.reset_index()
            df = pd.concat(
                [
                    pd.DataFrame(
                        [
                            {
                                "instrument": str(self.portfolio.instruments.first().id),
                                "path": "",
                                "effective_weights": 1.0,
                                "rebalancing_weights": 1.0,
                            }
                        ]
                    ),
                    df,
                ],
                ignore_index=True,
            )

            df = df.reset_index(names="id")

            def _get_group_key(x):
                return str(int(x)) if not df.loc[df["parent_row_id"] == x, :].empty else None

            def _get_parent_row_id(path):
                s = path.split("-")
                instrument = s[-1]
                parent_path = "-".join(s[:-1]) if len(s) > 1 else ""
                dff = df.loc[(df["instrument"] == instrument) & (df["path"] == parent_path), "id"]
                if not dff.empty:
                    return dff.iloc[0]
                return None

            df["parent_row_id"] = df["path"].apply(lambda x: _get_parent_row_id(x))
            df["_group_key"] = df["id"].apply(lambda x: _get_group_key(x))
            df = df.drop(columns=["path"])
        return df

    def manipulate_dataframe(self, df):
        df["instrument"] = (
            df["instrument"]
            .astype(int)
            .map(dict(Instrument.objects.filter(id__in=df["instrument"]).values_list("id", "name_repr")))
        )
        return df
