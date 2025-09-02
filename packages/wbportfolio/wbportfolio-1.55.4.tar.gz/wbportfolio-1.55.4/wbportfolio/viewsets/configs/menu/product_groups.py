from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

PRODUCTGROUP_MENUITEM = MenuItem(
    label="Product Groups",
    endpoint="wbportfolio:product_group-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbportfolio.view_productgroup"]
    ),
)
