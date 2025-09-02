from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

REGISTER_MENUITEM = MenuItem(
    label="Registers",
    endpoint="wbportfolio:register-list",
    permission=ItemPermission(
        permissions=["wbportfolio.view_register"], method=lambda request: is_internal_user(request.user)
    ),
)
