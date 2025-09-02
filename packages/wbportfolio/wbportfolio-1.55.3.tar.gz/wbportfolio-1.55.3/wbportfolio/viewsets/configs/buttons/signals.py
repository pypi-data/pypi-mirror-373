from django.dispatch import receiver
from wbcore.contrib.directory.viewsets import (
    CompanyModelViewSet,
    EntryModelViewSet,
    PersonModelViewSet,
)
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.display import create_simple_display
from wbcore.signals.instance_buttons import add_instance_button
from wbcrm.viewsets import AccountModelViewSet
from wbfdm.viewsets.instruments import InstrumentModelViewSet

from wbportfolio.serializers.reconciliations import AccountReconciliationModelSerializer

from .mixins import InstrumentButtonMixin


@receiver(add_instance_button, sender=InstrumentModelViewSet)
def add_instrument_request_button(sender, many, *args, request=None, view=None, pk=None, **kwargs):
    return InstrumentButtonMixin.add_instrument_request_button(request=request, view=view, pk=pk)


@receiver(add_instance_button, sender=InstrumentModelViewSet)
def add_transactions_request_button(sender, many, *args, request=None, view=None, pk=None, **kwargs):
    return InstrumentButtonMixin.add_transactions_request_button(request=request, view=view, pk=pk)


@receiver(add_instance_button, sender=PersonModelViewSet)
@receiver(add_instance_button, sender=EntryModelViewSet)
@receiver(add_instance_button, sender=CompanyModelViewSet)
def crm_claim_buttons(sender, many, *args, **kwargs):
    if many:
        return
    return bt.DropDownButton(
        label="Claims",
        icon=WBIcon.UNFOLD.icon,
        buttons=(
            bt.WidgetButton(key="claims", label="Claims", icon=WBIcon.TRADE.icon),
            bt.WidgetButton(key="aum", label="AUM", icon=WBIcon.DOLLAR.icon),
        ),
    )


@receiver(add_instance_button, sender=AccountModelViewSet)
def add_account_holdings_reconciliation_button(sender, many, *args, **kwargs):
    if many:
        return
    return bt.DropDownButton(
        label="Reconciliations",
        icon=WBIcon.UNFOLD.icon,
        buttons=[
            bt.WidgetButton(
                label="Reconciliations",
                key="wbportfolio-accountreconciliation",
            ),
            bt.ActionButton(
                label="Reconcile",
                icon=WBIcon.APPROVE.icon,
                key="wbportfolio-reconcile-account",
                method=RequestType.POST,
                identifiers=("wbportfolio:accountreconciliation", "wbportfolio:accountreconciliationline"),
                action_label="Reconcile this account. A notification will be send to the customer",
                serializer=AccountReconciliationModelSerializer,
                instance_display=create_simple_display([["reconciliation_date"]]),
            ),
        ],
    )
