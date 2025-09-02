from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

from wbportfolio.permissions import is_manager

PORTFOLIOROLE_MENUITEM = MenuItem(
    label="Portfolio Roles",
    endpoint="wbportfolio:portfoliorole-list",
    permission=ItemPermission(permissions=["wbportfolio.view_portfoliorole"], method=is_manager),
    add=MenuItem(
        label="Create Portfolio Role",
        endpoint="wbportfolio:portfoliorole-list",
        permission=ItemPermission(
            method=lambda request: is_internal_user(request.user), permissions=["wbportfolio.add_portfoliorole"]
        ),
    ),
)
