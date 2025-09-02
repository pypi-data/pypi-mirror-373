from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

VALUATIONDATAAUM_MENUITEM = MenuItem(
    label="AuM Chart",
    endpoint="wbportfolio:aumchart-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbportfolio.view_portfolio"]
    ),
)
