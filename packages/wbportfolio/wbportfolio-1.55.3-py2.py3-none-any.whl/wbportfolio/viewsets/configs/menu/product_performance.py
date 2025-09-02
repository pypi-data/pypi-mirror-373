from wbcore.menus import ItemPermission, MenuItem
from wbcore.permissions.shortcuts import is_internal_user

PRODUCTPERFORMANCELIST_MENUITEM = MenuItem(
    label="Performances",
    endpoint="wbportfolio:productperformance-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbportfolio.view_product"]
    ),
)

PRODUCTPERFORMANCECOMPARISONLIST_MENUITEM = MenuItem(
    label="Performances Summary",
    endpoint="wbportfolio:productperformancecomparison-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbportfolio.view_product"]
    ),
)
PRODUCTPERFORMANCENNMLIST_MENUITEM = MenuItem(
    label="Net new money",
    endpoint="wbportfolio:productperformancennmlist-list",
    permission=ItemPermission(
        method=lambda request: is_internal_user(request.user), permissions=["wbportfolio.view_product"]
    ),
)
