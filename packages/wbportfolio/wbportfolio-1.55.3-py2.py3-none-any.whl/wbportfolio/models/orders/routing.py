# TBD: Should this stay a service or should we extend the order proposal model (fat model approach) ?
from contextlib import suppress
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from wbportfolio.order_routing import ExecutionStatus

if TYPE_CHECKING:
    from wbportfolio.models import OrderProposal


def _should_route_as_draft() -> bool:
    """Determine whether orders should be routed as drafts."""
    return getattr(settings, "DEBUG", True) or getattr(settings, "ORDER_ROUTING_AS_DRAFT", True)


def _update_orders_with_confirmations(order_proposal, confirmations, rebalancing_comment):
    """Update all orders in the proposal based on confirmed executions."""


def execute_orders(order_proposal: "OrderProposal") -> tuple[ExecutionStatus, str]:
    """
    Executes the prepared orders of an order proposal via its custodian adapter.
    Updates execution statuses and handles routing errors gracefully.
    """
    orders = order_proposal.prepare_orders_for_execution()
    as_draft = _should_route_as_draft()
    adapter = order_proposal.custodian_adapter
    order_confirmations, rebalancing_comment = adapter.submit_rebalancing(orders, as_draft=as_draft)
    leftover_orders = order_proposal.orders.all()

    for confirmed in order_confirmations:
        with suppress(ObjectDoesNotExist):
            order = leftover_orders.get(id=confirmed.id)
            order.execution_confirmed = True
            order.execution_comment = order.comment
            order.save()
            leftover_orders = leftover_orders.exclude(id=order.id)

    # Orders without confirmation
    leftover_orders.update(execution_confirmed=False, execution_comment="No confirmation received from the custodian")
    return ExecutionStatus.IN_DRAFT if as_draft else ExecutionStatus.PENDING, rebalancing_comment


def get_execution_status(order_proposal: "OrderProposal") -> tuple[ExecutionStatus, str]:
    adapter = order_proposal.custodian_adapter
    return adapter.get_rebalance_status()


def cancel_rebalancing(order_proposal: "OrderProposal") -> bool:
    adapter = order_proposal.custodian_adapter
    return adapter.cancel_current_rebalancing()
