from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

CustodianMenuItem = MenuItem(
    label="Custodian",
    endpoint="wbportfolio:custodian-list",
    permission=ItemPermission(
        permissions=["wbportfolio.view_custodian"],
        method=lambda request: is_internal_user(request.user),
    ),
)
