from rest_framework.reverse import reverse
from wbcore import serializers
from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig
from wbcore.metadata.configs.display.instance_display.shortcuts import (
    create_simple_display,
)
from wbcore.utils.urls import get_urlencode_endpoint
from wbcrm.models.accounts import Account
from wbcrm.serializers.accounts import TerminalAccountRepresentationSerializer


class TransferTradeSerializer(serializers.Serializer):
    transfer_date = serializers.DateField(label="Transfer Date", required=True)
    from_account = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(), label="From Account", required=True
    )
    _from_account = TerminalAccountRepresentationSerializer(source="from_account")

    to_account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), label="To Account", required=True)
    _to_account = TerminalAccountRepresentationSerializer(source="to_account")


class QuickClaimSerializer(serializers.Serializer):
    account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all(), label="Account", required=True)
    _account = TerminalAccountRepresentationSerializer(source="account")


class ConsolidatedTradeSummaryButtonConfig(ButtonViewConfig):
    def get_custom_buttons(self) -> set:
        return {
            bt.WidgetButton(
                endpoint=get_urlencode_endpoint(
                    reverse(
                        "wbportfolio:consolidatedtradesummarydistributionchart-list", args=[], request=self.request
                    ),
                    self.request.GET,
                ),
                label="Distribution NNM Chart",
            ),
            bt.WidgetButton(
                endpoint=get_urlencode_endpoint(
                    reverse("wbportfolio:cumulativennmchart-list", args=[], request=self.request), self.request.GET
                ),
                label="Cumulative NNM Chart",
            ),
        }


class ClaimTradeButtonConfig(ButtonViewConfig):
    def get_custom_buttons(self):
        return {
            bt.ActionButton(
                method=RequestType.POST,
                action_label="Trade transferred.",
                endpoint=reverse(
                    "wbportfolio:trade-claim-transfer-trade", request=self.request, args=[self.view.kwargs["trade_id"]]
                ),
                description_fields="Do you want to transfer this trade?",
                label="Transfer Trade",
                icon=WBIcon.DEAL.icon,
                confirm_config=bt.ButtonConfig(label="Transfer"),
                cancel_config=bt.ButtonConfig(label="Cancel"),
                serializer=TransferTradeSerializer,
                instance_display=create_simple_display([["transfer_date"], ["from_account"], ["to_account"]]),
            ),
            bt.ActionButton(
                method=RequestType.POST,
                action_label="Trade claimed.",
                endpoint=reverse(
                    "wbportfolio:trade-claim-quick-claim", request=self.request, args=[self.view.kwargs["trade_id"]]
                ),
                description_fields="Do you want to quick claim this trade?",
                label="Quick Claim",
                icon=WBIcon.EURO.icon,
                confirm_config=bt.ButtonConfig(label="Claim"),
                cancel_config=bt.ButtonConfig(label="Cancel"),
                serializer=QuickClaimSerializer,
                instance_display=create_simple_display([["account"]]),
            ),
        }
