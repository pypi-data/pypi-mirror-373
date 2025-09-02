from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

PRODUCTCUSTOMER_MENUITEM = MenuItem(
    label="Product Lists",
    endpoint="wbportfolio:productcustomer-list",
    permission=ItemPermission(method=lambda request: not is_internal_user(request.user)),
)
PRODUCT_MENUITEM = MenuItem(
    label="Products",
    endpoint="wbportfolio:product-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbportfolio.view_product"]
    ),
)
