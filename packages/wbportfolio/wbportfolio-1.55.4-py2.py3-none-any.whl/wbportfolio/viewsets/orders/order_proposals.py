from contextlib import suppress
from datetime import date
from decimal import Decimal

from django.contrib.messages import info, warning
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from pandas._libs.tslibs.offsets import BDay
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from wbcompliance.viewsets.risk_management.mixins import RiskCheckViewSetMixin
from wbcore import serializers as wb_serializers
from wbcore import viewsets
from wbcore.metadata.configs.display.instance_display import (
    Display,
    create_simple_display,
)
from wbcore.permissions.permissions import InternalUserPermissionMixin
from wbcore.utils.views import CloneMixin

from wbportfolio.models import AssetPosition, OrderProposal
from wbportfolio.models.orders.order_proposals import (
    push_model_change_as_task,
    replay_as_task,
)
from wbportfolio.serializers import (
    OrderProposalModelSerializer,
    OrderProposalRepresentationSerializer,
    ReadOnlyOrderProposalModelSerializer,
)

from ...filters.orders import OrderProposalFilterSet
from ...order_routing import ExecutionStatus
from ..mixins import UserPortfolioRequestPermissionMixin
from .configs import (
    OrderProposalButtonConfig,
    OrderProposalDisplayConfig,
    OrderProposalEndpointConfig,
    OrderProposalPortfolioEndpointConfig,
)


class OrderProposalRepresentationViewSet(InternalUserPermissionMixin, viewsets.RepresentationViewSet):
    IDENTIFIER = "wbportfolio:trade"
    queryset = OrderProposal.objects.all()
    serializer_class = OrderProposalRepresentationSerializer


class OrderProposalModelViewSet(CloneMixin, RiskCheckViewSetMixin, InternalUserPermissionMixin, viewsets.ModelViewSet):
    ordering_fields = ("trade_date",)
    ordering = ("-trade_date",)
    search_fields = ("comment",)
    filterset_fields = {"trade_date": ["exact", "gte", "lte"], "status": ["exact"]}

    queryset = OrderProposal.objects.select_related("rebalancing_model", "portfolio")
    serializer_class = OrderProposalModelSerializer
    filterset_class = OrderProposalFilterSet
    display_config_class = OrderProposalDisplayConfig
    button_config_class = OrderProposalButtonConfig
    endpoint_config_class = OrderProposalEndpointConfig

    def get_serializer_class(self):
        if self.new_mode or (
            "pk" in self.kwargs and (obj := self.get_object()) and obj.status == OrderProposal.Status.DRAFT
        ):
            return OrderProposalModelSerializer
        return ReadOnlyOrderProposalModelSerializer

    # 2 methods to parametrize the clone button functionality
    def get_clone_button_serializer_class(self, instance):
        class CloneSerializer(wb_serializers.Serializer):
            clone_date = wb_serializers.DateField(
                default=(instance.trade_date + BDay(1)).date(), label="Trade Date"
            )  # we need to change the field name from the trade proposa fields, otherwise fontend conflicts
            clone_comment = wb_serializers.TextField(label="Comment")

        return CloneSerializer

    def get_clone_button_instance_display(self) -> Display:
        return create_simple_display(
            [
                ["clone_comment"],
                ["clone_date"],
            ]
        )

    def add_messages(self, request, instance: OrderProposal | None = None, **kwargs):
        if instance:
            if instance.status == OrderProposal.Status.APPROVED and not instance.portfolio.is_manageable:
                info(request, "This order proposal cannot be approved the portfolio is considered unmanaged.")
            if instance.status == OrderProposal.Status.PENDING and instance.has_non_successful_checks:
                warning(
                    request,
                    "This order proposal cannot be approved because there is unsuccessful pre-trade checks. Please rectify accordingly and resubmit a valid order proposal",
                )
            if (
                instance.execution_status in [ExecutionStatus.IN_DRAFT, ExecutionStatus.COMPLETED]
                and instance.orders.filter(execution_confirmed=False).exists()
            ):
                warning(request, "Some orders failed confirmation. Check the list for further details.")
            if instance.execution_status in [
                ExecutionStatus.REJECTED,
                ExecutionStatus.FAILED,
                ExecutionStatus.UNKNOWN,
            ]:
                warning(
                    request,
                    f"The execution status is {ExecutionStatus[instance.execution_status].label}. Detail: {instance.execution_comment}",
                )

    @classmethod
    def _get_risk_checks_button_title(cls) -> str:
        return "Pre-Trade Checks"

    @action(detail=True, methods=["PATCH"])
    def reset(self, request, pk=None):
        order_proposal = get_object_or_404(OrderProposal, pk=pk)
        use_desired_target_weight = request.GET.get("use_desired_target_weight") == "true"
        if order_proposal.status == OrderProposal.Status.DRAFT:
            order_proposal.orders.all().update(weighting=0)
            order_proposal.reset_orders(use_desired_target_weight=use_desired_target_weight)
            return Response({"send": True})
        return Response({"status": "Order Proposal is not Draft"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["PATCH"])
    def normalize(self, request, pk=None):
        order_proposal = get_object_or_404(OrderProposal, pk=pk)
        total_cash_weight = Decimal(request.data.get("total_cash_weight", Decimal("0.0")))
        if order_proposal.status == OrderProposal.Status.DRAFT:
            order_proposal.normalize_orders(total_target_weight=Decimal("1.0") - total_cash_weight)
            return Response({"send": True})
        return Response({"status": "Order Proposal is not Draft"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["PATCH"])
    def replay(self, request, pk=None):
        order_proposal = get_object_or_404(OrderProposal, pk=pk)
        if order_proposal.portfolio.is_manageable:
            replay_as_task.delay(order_proposal.id, user_id=self.request.user.id)
            return Response({"send": True})
        return Response({"status": "Order Proposal is not Draft"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["PATCH"])
    def deleteall(self, request, pk=None):
        order_proposal = get_object_or_404(OrderProposal, pk=pk)
        if order_proposal.status == OrderProposal.Status.DRAFT:
            order_proposal.orders.all().delete()
            return Response({"send": True})
        return Response({"status": "Order Proposal is not Draft"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["PATCH"])
    def pushmodelchange(self, request, pk=None):
        order_proposal = get_object_or_404(OrderProposal, pk=pk)
        only_for_portfolio_ids = list(
            map(lambda o: int(o), filter(lambda r: r, request.data.get("only_for_portfolio_ids", "").split(",")))
        )
        approve_automatically = request.data.get("approve_automatically") == "true"
        if order_proposal.status == OrderProposal.Status.APPLIED and order_proposal.portfolio.is_model:
            push_model_change_as_task.delay(
                order_proposal.id,
                request.user.id,
                only_for_portfolio_ids=only_for_portfolio_ids,
                approve_automatically=approve_automatically,
            )
            return Response({"send": True})
        return Response(
            {"status": "Order Proposal needs to be approved and linked to be a model portfolio"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class OrderProposalPortfolioModelViewSet(UserPortfolioRequestPermissionMixin, OrderProposalModelViewSet):
    endpoint_config_class = OrderProposalPortfolioEndpointConfig

    @cached_property
    def default_trade_date(self) -> date | None:
        with suppress(AssetPosition.DoesNotExist):
            return (self.portfolio.assets.latest("date").date + BDay(1)).date()

    def get_queryset(self):
        return OrderProposal.objects.filter(portfolio=self.kwargs["portfolio_id"])
