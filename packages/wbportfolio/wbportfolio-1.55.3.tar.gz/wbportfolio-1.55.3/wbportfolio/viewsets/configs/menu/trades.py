from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

TRADE_MENUITEM = MenuItem(
    label="Trades",
    endpoint="wbportfolio:trade-list",
    permission=ItemPermission(
        permissions=["wbportfolio.view_trade"], method=lambda request: is_internal_user(request.user)
    ),
)
SUBSCRIPTION_REDEMPTION_MENUITEM = MenuItem(
    label="Subscription/Redemption",
    endpoint="wbportfolio:subscriptionredemption-list",
    permission=ItemPermission(
        permissions=["wbportfolio.view_trade"], method=lambda request: is_internal_user(request.user)
    ),
)
