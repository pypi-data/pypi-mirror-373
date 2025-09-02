from wbcore.contrib.icons import WBIcon
from wbcore.enums import RequestType
from wbcore.metadata.configs import buttons as bt
from wbcore.metadata.configs.buttons.enums import ButtonDefaultColor
from wbcore.metadata.configs.buttons.view_config import ButtonViewConfig


class AccountReconciliationButtonViewConfig(ButtonViewConfig):
    def get_custom_instance_buttons(self):
        return {
            bt.ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.SUCCESS,
                identifiers=("wbportfolio:accountreconciliation",),
                icon=WBIcon.APPROVE.icon,
                key="agree_customer",
                label="Agree",
                action_label="Agreeing",
                description_fields="<p>After agreening to this holdings, you cannot change this reconcilation anymore!</p>",
            ),
            bt.ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.ERROR,
                identifiers=("wbportfolio:accountreconciliation",),
                icon=WBIcon.DENY.icon,
                key="disagree_customer",
                label="Communicate Differences",
                action_label="Communicating Differences",
                description_fields="<p>After disagreeing with this holdings, someone will reach out to you do discuss the differences.</p>",
            ),
            bt.ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.ERROR,
                identifiers=("wbportfolio:accountreconciliationline", "wbportfolio:accountreconciliation"),
                icon=WBIcon.REFRESH.icon,
                key="recalculate",
                label="Recalculate",
                action_label="Recalculating",
                description_fields="<p>After confirming, the Reconciliation will recompute 'Our Calculations'</p>",
            ),
            bt.ActionButton(
                method=RequestType.PATCH,
                color=ButtonDefaultColor.WARNING,
                identifiers=("wbportfolio:accountreconciliationline",),
                icon=WBIcon.MAIL.icon,
                key="notify",
                label="Notify Reconciliation Managers",
                action_label="Notifying",
                description_fields="<p>After confirming the reconciliation managers of this account reconciliation will be notified.</p>",
            ),
            bt.WidgetButton(key="claims", label="Show Subscriptions/Redemptions", icon=WBIcon.TRADE.icon, weight=200),
            bt.WidgetButton(
                key="add-claim", label="Add Subscription/Redemption", icon=WBIcon.ADD.icon, new_mode=True, weight=300
            ),
        }


class AccountReconciliationLineButtonViewConfig(ButtonViewConfig):
    def get_custom_list_instance_buttons(self):
        return {
            bt.WidgetButton(key="product-claims", label="Show Subscriptions/Redemptions", icon=WBIcon.TRADE.icon),
            bt.WidgetButton(
                key="add-product-claim", label="Add Subscription/Redemption", icon=WBIcon.ADD.icon, new_mode=True
            ),
        }
