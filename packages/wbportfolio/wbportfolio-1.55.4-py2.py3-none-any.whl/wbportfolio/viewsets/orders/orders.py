from decimal import Decimal

from django.contrib.messages import error, info
from django.db.models import (
    Case,
    F,
    Sum,
    Value,
    When,
)
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from wbcore import viewsets
from wbcore.permissions.permissions import InternalUserPermissionMixin
from wbcore.utils.strings import format_number
from wbcore.viewsets.mixins import OrderableMixin

from wbportfolio.import_export.resources.trades import OrderProposalTradeResource
from wbportfolio.models import Order, OrderProposal
from wbportfolio.serializers import (
    OrderOrderProposalListModelSerializer,
    OrderOrderProposalModelSerializer,
    ReadOnlyOrderOrderProposalModelSerializer,
)

from ...filters.orders import OrderFilterSet
from ..mixins import UserPortfolioRequestPermissionMixin
from .configs import (
    OrderOrderProposalButtonConfig,
    OrderOrderProposalDisplayConfig,
    OrderOrderProposalEndpointConfig,
)


class OrderOrderProposalModelViewSet(
    UserPortfolioRequestPermissionMixin, InternalUserPermissionMixin, OrderableMixin, viewsets.ModelViewSet
):
    IMPORT_ALLOWED = True
    ordering = (
        "order_proposal",
        "order",
    )
    ordering_fields = (
        "underlying_instrument__name",
        "underlying_instrument_isin",
        "underlying_instrument_ticker",
        "underlying_instrument_refinitiv_identifier_code",
        "underlying_instrument_instrument_type",
        "target_weight",
        "effective_weight",
        "effective_shares",
        "target_shares",
        "shares",
        "weighting",
    )
    IDENTIFIER = "wbportfolio:orderproposal"
    search_fields = ("underlying_instrument__name",)
    queryset = Order.objects.none()
    filterset_class = OrderFilterSet

    display_config_class = OrderOrderProposalDisplayConfig
    endpoint_config_class = OrderOrderProposalEndpointConfig
    serializer_class = OrderOrderProposalModelSerializer
    button_config_class = OrderOrderProposalButtonConfig

    @cached_property
    def order_proposal(self):
        return get_object_or_404(OrderProposal, pk=self.kwargs["order_proposal_id"])

    @cached_property
    def portfolio_total_asset_value(self):
        return self.order_proposal.portfolio_total_asset_value

    def has_import_permission(self, request) -> bool:  # allow import only on draft order proposal
        return super().has_import_permission(request) and self.order_proposal.status == OrderProposal.Status.DRAFT

    def get_import_resource_kwargs(self):
        resource_kwargs = super().get_import_resource_kwargs()
        resource_kwargs["columns_mapping"] = {"underlying_instrument": "underlying_instrument__isin"}
        return resource_kwargs

    def get_resource_class(self):
        return OrderProposalTradeResource

    def get_aggregates(self, queryset, *args, **kwargs):
        agg = {}
        if queryset.exists():
            noncash_aggregates = queryset.filter(underlying_instrument__is_cash=False).aggregate(
                sum_target_weight=Sum(F("target_weight")),
                sum_effective_weight=Sum(F("effective_weight")),
                sum_target_total_value_fx_portfolio=Sum(F("target_total_value_fx_portfolio")),
                sum_effective_total_value_fx_portfolio=Sum(F("effective_total_value_fx_portfolio")),
            )
            # weights aggregates
            cash_sum_effective_weight = (
                self.order_proposal.total_effective_portfolio_weight - noncash_aggregates["sum_effective_weight"]
            )
            cash_sum_target_cash_weight = Decimal("1.0") - noncash_aggregates["sum_target_weight"]
            noncash_sum_effective_weight = noncash_aggregates["sum_effective_weight"] or Decimal(0)
            noncash_sum_target_weight = noncash_aggregates["sum_target_weight"] or Decimal(0)
            sum_buy_weight = queryset.filter(weighting__gte=0).aggregate(s=Sum(F("weighting")))["s"] or Decimal(0)
            sum_sell_weight = queryset.filter(weighting__lt=0).aggregate(s=Sum(F("weighting")))["s"] or Decimal(0)

            # shares aggregates
            cash_sum_effective_total_value_fx_portfolio = cash_sum_effective_weight * self.portfolio_total_asset_value
            cash_sum_target_total_value_fx_portfolio = cash_sum_target_cash_weight * self.portfolio_total_asset_value
            noncash_sum_effective_total_value_fx_portfolio = noncash_aggregates[
                "sum_effective_total_value_fx_portfolio"
            ] or Decimal(0)
            noncash_sum_target_total_value_fx_portfolio = noncash_aggregates[
                "sum_target_total_value_fx_portfolio"
            ] or Decimal(0)
            sum_buy_total_value_fx_portfolio = queryset.filter(total_value_fx_portfolio__gte=0).aggregate(
                s=Sum(F("total_value_fx_portfolio"))
            )["s"] or Decimal(0)
            sum_sell_total_value_fx_portfolio = queryset.filter(total_value_fx_portfolio__lt=0).aggregate(
                s=Sum(F("total_value_fx_portfolio"))
            )["s"] or Decimal(0)

            agg = {
                "effective_weight": {
                    "Cash": format_number(cash_sum_effective_weight, decimal=Order.ORDER_WEIGHTING_PRECISION),
                    "Non-Cash": format_number(noncash_sum_effective_weight, decimal=Order.ORDER_WEIGHTING_PRECISION),
                    "Total": format_number(
                        noncash_sum_effective_weight + cash_sum_effective_weight,
                        decimal=Order.ORDER_WEIGHTING_PRECISION,
                    ),
                },
                "target_weight": {
                    "Cash": format_number(cash_sum_target_cash_weight, decimal=Order.ORDER_WEIGHTING_PRECISION),
                    "Non-Cash": format_number(noncash_sum_target_weight, decimal=Order.ORDER_WEIGHTING_PRECISION),
                    "Total": format_number(
                        cash_sum_target_cash_weight + noncash_sum_target_weight,
                        decimal=Order.ORDER_WEIGHTING_PRECISION,
                    ),
                },
                "effective_total_value_fx_portfolio": {
                    "Cash": format_number(cash_sum_effective_total_value_fx_portfolio, decimal=6),
                    "Non-Cash": format_number(noncash_sum_effective_total_value_fx_portfolio, decimal=6),
                    "Total": format_number(
                        cash_sum_effective_total_value_fx_portfolio + noncash_sum_effective_total_value_fx_portfolio,
                        decimal=6,
                    ),
                },
                "target_total_value_fx_portfolio": {
                    "Cash": format_number(cash_sum_target_total_value_fx_portfolio, decimal=6),
                    "Non-Cash": format_number(noncash_sum_target_total_value_fx_portfolio, decimal=6),
                    "Total": format_number(
                        cash_sum_target_total_value_fx_portfolio + noncash_sum_target_total_value_fx_portfolio,
                        decimal=6,
                    ),
                },
                "weighting": {
                    "Cash Flow": format_number(
                        sum_sell_weight + sum_buy_weight,
                        decimal=Order.ORDER_WEIGHTING_PRECISION,
                    ),
                    "Buy": format_number(sum_buy_weight, decimal=Order.ORDER_WEIGHTING_PRECISION),
                    "Sell": format_number(sum_sell_weight, decimal=Order.ORDER_WEIGHTING_PRECISION),
                },
                "total_value_fx_portfolio": {
                    "Cash Flow": format_number(
                        cash_sum_target_total_value_fx_portfolio - cash_sum_effective_total_value_fx_portfolio,
                        decimal=6,
                    ),
                    "Buy": format_number(sum_buy_total_value_fx_portfolio, decimal=6),
                    "Sell": format_number(sum_sell_total_value_fx_portfolio, decimal=6),
                },
            }

        return agg

    def get_serializer_class(self):
        if self.order_proposal.status != OrderProposal.Status.DRAFT:
            return ReadOnlyOrderOrderProposalModelSerializer
        elif not self.new_mode and "pk" not in self.kwargs:
            return OrderOrderProposalListModelSerializer
        return OrderOrderProposalModelSerializer

    def add_messages(self, request, queryset=None, paginated_queryset=None, instance=None, initial=False):
        if self.orders.exists() and self.order_proposal.status in [
            OrderProposal.Status.PENDING,
            OrderProposal.Status.DRAFT,
        ]:
            total_target_weight = self.orders.aggregate(c=Sum(F("target_weight")))["c"] or Decimal(0)
            if round(total_target_weight, 8) != 1:
                info(
                    request,
                    "The total target weight does not equal 1. To avoid automatic cash allocation, please adjust the order weights to sum up to 1. Otherwise, a cash component will be added when this order proposal is submitted.",
                )
            if self.orders.filter(has_warnings=True).exists():
                error(
                    request,
                    "Some orders failed preparation. To resolve this, please revert the order proposal to draft, review and correct the orders, and then resubmit.",
                )

    @cached_property
    def orders(self):
        qs = self.order_proposal.get_orders()
        if not self.is_portfolio_manager:
            return qs.none()
        return qs

    def get_queryset(self):
        return self.orders.annotate(  # .exclude(underlying_instrument__is_cash=True)
            underlying_instrument_isin=F("underlying_instrument__isin"),
            underlying_instrument_ticker=F("underlying_instrument__ticker"),
            underlying_instrument_refinitiv_identifier_code=F("underlying_instrument__refinitiv_identifier_code"),
            underlying_instrument_instrument_type=Case(
                When(
                    underlying_instrument__parent__is_security=True,
                    then=F("underlying_instrument__parent__instrument_type__short_name"),
                ),
                default=F("underlying_instrument__instrument_type__short_name"),
            ),
            underlying_instrument_exchange=F("underlying_instrument__exchange__name"),
            effective_total_value_fx_portfolio=F("previous_weight") * Value(self.portfolio_total_asset_value),
            target_total_value_fx_portfolio=F("target_weight") * Value(self.portfolio_total_asset_value),
            portfolio_currency=F("portfolio__currency__symbol"),
            security=F("underlying_instrument__parent"),
            company=F("underlying_instrument__parent__parent"),
        ).select_related(
            "underlying_instrument", "underlying_instrument__parent", "underlying_instrument__parent__parent"
        )
